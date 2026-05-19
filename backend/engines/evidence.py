from sqlalchemy.orm import Session
from backend.models.domain import EvidenceRecord

def record_evidence(db: Session, category: str, weight: float, environment_id: str = "default"):
    if db:
        try:
            evidence = EvidenceRecord(environment_id=environment_id, category=category, weight=weight)
            db.add(evidence)
            db.commit()
            db.refresh(evidence)
            return {"status": "recorded", "evidence_id": evidence.id, "environment_id": environment_id}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    return {"status": "error", "message": "no db"}

def get_evidence_confidence(db: Session, environment_id: str = "default"):
    if not db:
        return 0.92
    
    # Calculate simple average of recent evidence confidence for the specific environment
    records = db.query(EvidenceRecord).filter(
        EvidenceRecord.environment_id == environment_id
    ).order_by(EvidenceRecord.id.desc()).limit(100).all()
    
    if not records:
        return 0.92
        
    total_weight = sum(r.weight for r in records)
    return total_weight / len(records)
