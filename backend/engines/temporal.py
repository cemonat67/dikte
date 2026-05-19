from sqlalchemy.orm import Session
from backend.models.domain import ContinuityMemory

def _get_or_create_memory(db: Session, environment_id: str = "default"):
    mem = db.query(ContinuityMemory).filter(ContinuityMemory.environment_id == environment_id).first()
    if not mem:
        mem = ContinuityMemory(environment_id=environment_id, ticks=0.0, state="transient")
        db.add(mem)
        db.flush()
    return mem

from backend.models.domain import ReviewEvent

def tick_temporal(db: Session, is_quiet: bool, environment_id: str = "default"):
    if not db:
        return
    mem = _get_or_create_memory(db, environment_id)
    
    # Compute governance drag: slower recovery if there were recent reviews
    recent_reviews = db.query(ReviewEvent).filter(
        ReviewEvent.environment_id == environment_id,
        ReviewEvent.action.in_(["resolve_risk", "suppress_risk"])
    ).count()
    
    governance_drag = min(0.3, recent_reviews * 0.05)
    
    if is_quiet:
        mem.ticks += max(0.1, 1.0 - governance_drag)
    else:
        # Slow decay
        mem.ticks = max(0, mem.ticks - (0.5 + governance_drag))
        
    if mem.ticks > 120:
        mem.state = "enduring"
    elif mem.ticks > 60:
        mem.state = "persistent"
    elif mem.ticks > 20:
        mem.state = "stable"
    else:
        mem.state = "transient"

def get_temporal_state(db: Session, environment_id: str = "default"):
    if not db:
        return {
            "temporal_ticks": 0.0,
            "temporal_state": "transient",
            "silence_locked": False
        }
    
    mem = _get_or_create_memory(db, environment_id)
    return {
        "temporal_ticks": mem.ticks,
        "temporal_state": mem.state,
        "silence_locked": mem.ticks > 120
    }

from backend.models.domain import ReviewEvent

def restore_continuity(db: Session, environment_id: str, reviewer: str, note: str):
    mem = _get_or_create_memory(db, environment_id)
    mem.ticks = max(mem.ticks, 65.0) # Boost safely to persistent
    mem.state = "persistent"
    
    event = ReviewEvent(environment_id=environment_id, reviewer=reviewer, action="restore_continuity", note=note, event_type="governance")
    db.add(event)
    db.add(mem)
    db.commit()
