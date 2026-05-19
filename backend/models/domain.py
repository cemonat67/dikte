from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from backend.db.session import Base

class EvidenceRecord(Base):
    __tablename__ = "evidence_records"
    id = Column(Integer, primary_key=True, index=True)
    environment_id = Column(String, default="default", index=True)
    category = Column(String, index=True)
    weight = Column(Float, default=1.0)
    maturity = Column(String, default="fresh")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RiskSignal(Base):
    __tablename__ = "risk_signals"
    id = Column(Integer, primary_key=True, index=True)
    environment_id = Column(String, default="default", index=True)
    source = Column(String, index=True)
    category = Column(String)
    severity = Column(Float, default=0.0)
    confidence = Column(Float, default=1.0)
    persistence = Column(Integer, default=0)
    human_review_required = Column(Boolean, default=False)
    
    external_id = Column(String(80), nullable=True)
    event_type = Column(String(80), nullable=True)
    summary = Column(String(500), nullable=True)
    metadata_json = Column(String, nullable=True)

    resolved = Column(Boolean, default=False)
    suppressed = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class GovernanceState(Base):
    __tablename__ = "governance_states"
    id = Column(Integer, primary_key=True, index=True)
    environment_id = Column(String, default="default", index=True)
    posture = Column(String, default="quiet")
    temporal_state = Column(String, default="transient")
    silence_locked = Column(Boolean, default=False)
    atmospheric_weight = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ContinuityMemory(Base):
    __tablename__ = "continuity_memory"
    id = Column(Integer, primary_key=True, index=True)
    environment_id = Column(String, default="default", index=True, unique=True)
    ticks = Column(Float, default=0.0)
    state = Column(String, default="transient")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ReviewEvent(Base):
    __tablename__ = "review_events"
    id = Column(Integer, primary_key=True, index=True)
    environment_id = Column(String, default="default", index=True)
    reviewer = Column(String, default="system")
    action = Column(String)
    note = Column(String, nullable=True)
    event_type = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
