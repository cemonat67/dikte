from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from backend.models.domain import RiskSignal, ReviewEvent
import datetime
import json

# Dictionary to hold hysteresis state per environment
global_risk_presence = {}

def get_global_presence(environment_id: str) -> float:
    return global_risk_presence.get(environment_id, 0.0)

def set_global_presence(environment_id: str, val: float):
    global_risk_presence[environment_id] = val

def evaluate_risk(db: Session, source: str, category: str, severity: float, environment_id: str = "default", 
                  external_id: str = None, event_type: str = None, summary: str = None, metadata_json: dict = None):
    if db:
        try:
            if external_id:
                existing = db.query(RiskSignal).filter(
                    RiskSignal.external_id == external_id, 
                    RiskSignal.environment_id == environment_id,
                    RiskSignal.resolved == False
                ).first()
                if existing:
                    return {"status": "ignored", "reason": "duplicate active external_id"}

            signal = RiskSignal(
                environment_id=environment_id, 
                source=source, 
                category=category, 
                severity=severity, 
                persistence=0,
                external_id=external_id,
                event_type=event_type,
                summary=summary,
                metadata_json=json.dumps(metadata_json) if metadata_json else None
            )
            db.add(signal)
            db.commit()
            db.refresh(signal)
            
            # Ensure memory dictionary tracks this environment
            if environment_id not in global_risk_presence:
                global_risk_presence[environment_id] = 0.0

            return {"status": "recorded", "signal_id": signal.id, "environment_id": environment_id}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    return {"status": "error", "message": "no db"}

CATEGORY_WEIGHTS = {
    "payment": 1.25,
    "identity": 1.20,
    "approval": 1.15,
    "vendor": 1.10,
    "access": 1.05,
    "network": 0.90,
    "anomaly": 1.00,
    "unknown": 0.80
}

def tick_risk(db: Session, environment_id: str = "default"):
    if not db:
        return
    
    # Load active risks for this specific environment (ignore resolved)
    active_risks = db.query(RiskSignal).filter(
        RiskSignal.environment_id == environment_id,
        RiskSignal.severity > 0.01,
        RiskSignal.resolved == False
    ).all()
    
    weighted_cycle_risk = 0.0
    
    if active_risks:
        for r in active_risks:
            if r.suppressed:
                r.severity *= 0.25 # Heavy decay if suppressed (requested 0.25 multiplier)
            else:
                r.severity *= 0.95 # Normal slow decay
                
            if r.severity > 0.3:
                r.persistence += 1
            else:
                r.persistence = max(0, r.persistence - 0.5)

        for r in active_risks:
            cat_weight = CATEGORY_WEIGHTS.get(r.category, 0.80)
            # Persistence multiplies weight by up to 1.5x (0.05 per tick)
            persistence_multiplier = min(1.5, 1.0 + (r.persistence * 0.05))
            
            weighted_score = r.severity * cat_weight * persistence_multiplier
            weighted_cycle_risk += weighted_score

        weighted_cycle_risk /= len(active_risks)

    # Hysteresis calculation (slow drag per environment)
    current_presence = get_global_presence(environment_id)
    new_presence = (current_presence * 0.9) + (min(1.0, weighted_cycle_risk) * 0.1)
    set_global_presence(environment_id, new_presence)

def resolve_all_risks(db: Session, environment_id: str, reviewer: str, note: str):
    risks = db.query(RiskSignal).filter(
        RiskSignal.environment_id == environment_id, 
        RiskSignal.resolved == False
    ).all()
    
    count = 0
    for r in risks:
        r.resolved = True
        # Do not zero severity, keep it for institutional memory
        r.resolved_at = func.now()
        count += 1
    
    event = ReviewEvent(environment_id=environment_id, reviewer=reviewer, action="resolve_risk", note=note, event_type="governance")
    db.add(event)
    db.commit()
    return count

def suppress_all_risks(db: Session, environment_id: str, reviewer: str, note: str):
    risks = db.query(RiskSignal).filter(
        RiskSignal.environment_id == environment_id, 
        RiskSignal.resolved == False
    ).all()
    
    count = 0
    for r in risks:
        r.suppressed = True
        count += 1
        
    event = ReviewEvent(environment_id=environment_id, reviewer=reviewer, action="suppress_risk", note=note, event_type="governance")
    db.add(event)
    db.commit()
    return count

def get_risk_state(environment_id: str = "default"):
    presence = get_global_presence(environment_id)
    risk_presence_state = "quiet"
    if presence > 0.75:
        risk_presence_state = "withheld"
    elif presence > 0.50:
        risk_presence_state = "burdened"
    elif presence > 0.25:
        risk_presence_state = "watching"

    return {
        "global_risk_presence": presence,
        "risk_presence_state": risk_presence_state
    }
