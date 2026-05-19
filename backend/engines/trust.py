from sqlalchemy.orm import Session
from backend.models.domain import GovernanceState
from backend.engines import evidence, risk, temporal

def tick_engines(db: Session, environment_id: str = "default"):
    # 1. Tick Risk Engine per environment
    risk.tick_risk(db, environment_id)
    risk_state = risk.get_risk_state(environment_id)
    
    # 2. Tick Temporal Engine per environment
    is_quiet = (risk_state["risk_presence_state"] == "quiet")
    temporal.tick_temporal(db, is_quiet, environment_id)
    
    # 3. Calculate final unified trust state per environment
    state = calculate_trust_state(db, environment_id)
    
    # 4. Optional: Persist the computed governance state log
    if db:
        gov_state = GovernanceState(
            environment_id=environment_id,
            posture=state["posture"],
            temporal_state=state["temporal_state"],
            silence_locked=state["silence_locked"],
            atmospheric_weight=state["atmospheric_weight"]
        )
        db.add(gov_state)

from backend.models.domain import ReviewEvent, RiskSignal

def get_dominant_condition(db: Session, environment_id: str):
    if not db:
        return None
    
    active_risks = db.query(RiskSignal).filter(
        RiskSignal.environment_id == environment_id,
        RiskSignal.resolved == False,
        RiskSignal.suppressed == False
    ).all()
    
    processed_risks = []
    for r in active_risks:
        eff_severity = r.severity
        if r.category == "identity":
            # Escalate identity uncertainty over time (maturing risk)
            eff_severity = r.severity + (r.persistence * 0.05)
            
        # Tier 1 Floor: Documentation and Payment anomalies must remain degraded
        if r.category in ["documentation", "payment"]:
            eff_severity = max(eff_severity, 0.85)
            
        # Hysteresis: only surface risks that persisted across multiple cycles
        if r.persistence >= 2:
            processed_risks.append((eff_severity, r))
            
    if not processed_risks:
        return None
        
    processed_risks.sort(key=lambda x: x[0], reverse=True)
    dominant_eff_severity, dominant = processed_risks[0]
    
    state = "observation"
    if dominant_eff_severity >= 0.8:
        state = "degraded"
    elif dominant_eff_severity >= 0.5:
        state = "constrained"
        
    category = dominant.category or "operational"
    
    mapping = {
        "identity": {
            "title": "Identity Uncertainty",
            "statement": "Access rhythm shifted." if state == "observation" else "Confidence parameter unmet.",
            "recommendation": "Observation active." if state == "observation" else "Verification recommended.",
            "action": "Maintain Observation" if state == "observation" else "Request Verification"
        },
        "supplier": {
            "title": "Supplier Approval Drift",
            "statement": "Approval rhythm changed.",
            "recommendation": "Review advised.",
            "action": "Maintain Constraint"
        },
        "approval": {
            "title": "Approval Drift",
            "statement": "Deviation from established baseline.",
            "recommendation": "Human oversight required.",
            "action": "Maintain Constraint"
        },
        "compliance": {
            "title": "Document Mismatch",
            "statement": "Compliance artifact expired or absent.",
            "recommendation": "Update recommended.",
            "action": "Restore Continuity"
        },
        "documentation": {
            "title": "Document Integrity Degradation",
            "statement": "Evidence continuity interrupted.",
            "recommendation": "Human review required before continuation.",
            "action": "Hold Continuity"
        },
        "payment": {
            "title": "Routing Inconsistency",
            "statement": "Financial payload parameters conflict.",
            "recommendation": "Verification required.",
            "action": "Suspend Routing"
        }
    }
    
    base = mapping.get(category, {
        "title": "Operational Inconsistency",
        "statement": "Continuity rhythm altered.",
        "recommendation": "Review advised.",
        "action": "Restore Continuity"
    })
    
    return {
        "state": state,
        "title": base["title"],
        "statement": base["statement"],
        "recommendation": base["recommendation"],
        "action": base["action"]
    }

from datetime import datetime, timedelta, timezone

def calculate_institutional_memory(db: Session, environment_id: str):
    if not db:
        return 0.0
        
    cutoff = datetime.now(timezone.utc) - timedelta(hours=72)
    
    from sqlalchemy import or_
    resolved_risks = db.query(RiskSignal).filter(
        RiskSignal.environment_id == environment_id,
        RiskSignal.resolved == True,
        or_(RiskSignal.resolved_at >= cutoff, RiskSignal.created_at >= cutoff)
    ).all()
    
    burden = 0.0
    cat_weights = {
        "documentation": 1.0,
        "payment": 1.0,
        "identity": 0.6,
        "supplier": 0.4,
        "operational": 0.3
    }
    
    now = datetime.now(timezone.utc)
    for r in resolved_risks:
        r_resolved_at = r.resolved_at or r.created_at
        if not r_resolved_at:
            continue
            
        if r_resolved_at.tzinfo is None:
            r_resolved_at = r_resolved_at.replace(tzinfo=timezone.utc)
            
        age_hours = (now - r_resolved_at).total_seconds() / 3600.0
        time_decay = max(0.0, 1.0 - (age_hours / 72.0))
        c_weight = cat_weights.get(r.category, 0.3)
        
        burden += (r.severity * time_decay * c_weight)
        
    return min(1.0, burden)

def calculate_trust_state(db: Session = None, environment_id: str = "default"):
    risk_state = risk.get_risk_state(environment_id)
    temporal_state = temporal.get_temporal_state(db, environment_id)
    confidence = evidence.get_evidence_confidence(db, environment_id)
    
    is_locked = temporal_state["silence_locked"]
    
    # Atmospheric weight formula
    weighted_risk_score = risk_state["global_risk_presence"]
    
    recent_reviews = db.query(ReviewEvent).filter(
        ReviewEvent.environment_id == environment_id,
        ReviewEvent.action.in_(["resolve_risk", "suppress_risk"])
    ).count() if db else 0
    governance_drag = min(0.3, recent_reviews * 0.05)
    
    if weighted_risk_score > 0.7:
        softening = (confidence * 0.1) # severe risk cannot be erased easily
    else:
        softening = (confidence * 0.3)
        
    final_trust_pressure = max(0.0, weighted_risk_score - softening + governance_drag)
    
    if final_trust_pressure > 0.75:
        posture = "withheld"
    elif final_trust_pressure > 0.50:
        posture = "burdened"
    elif final_trust_pressure > 0.25:
        posture = "watching"
    else:
        posture = "quiet"
    
    base_weight = min(1.0, final_trust_pressure)
    if temporal_state["temporal_state"] == "enduring":
        base_weight = min(1.0, base_weight + 0.2)
        
    # Phrase selection (max 2 words)
    frontend_phrase = "Continuity."
    if posture == "withheld":
        frontend_phrase = "Trust Withheld."
    elif posture == "burdened":
        frontend_phrase = "Review Held."
    elif posture == "watching":
        frontend_phrase = "Posture Held."
    elif is_locked:
        frontend_phrase = "Continuity Guarded." if weighted_risk_score > 0.1 else "Continuity."

    dominant_condition = get_dominant_condition(db, environment_id)
    
    inst_memory = calculate_institutional_memory(db, environment_id)
    
    atmospheric_memory_phrase = "Continuity."
    
    if not dominant_condition and inst_memory > 0.01:
        # Blend memory into weight
        base_weight = min(1.0, base_weight + (inst_memory * 0.5))
        
        if inst_memory > 0.4:
            atmospheric_memory_phrase = "Institutional caution retained."
            if posture == "quiet":
                posture = "watching"
        elif inst_memory > 0.15:
            atmospheric_memory_phrase = "Atmospheric recovery in progress."
            if posture == "quiet":
                posture = "watching"
        else:
            atmospheric_memory_phrase = "Review Held."
            
        # Gently override frontend phrase so Executive Curiosity hover explains the heaviness
        frontend_phrase = atmospheric_memory_phrase

    return {
        "posture": posture,
        "temporal_state": temporal_state["temporal_state"],
        "silence_locked": is_locked,
        "atmospheric_weight": base_weight,
        "frontend_phrase": frontend_phrase,
        "weighted_risk_score": weighted_risk_score,
        "evidence_confidence": confidence,
        "governance_drag": governance_drag,
        "final_trust_pressure": final_trust_pressure,
        "dominant_condition": dominant_condition,
        "institutional_memory": round(inst_memory, 3),
        "atmospheric_memory_phrase": atmospheric_memory_phrase
    }
