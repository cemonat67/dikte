from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class RiskCategory(str, Enum):
    identity = "identity"
    network = "network"
    vendor = "vendor"
    payment = "payment"
    approval = "approval"
    access = "access"
    anomaly = "anomaly"
    unknown = "unknown"

class TrustStateResponse(BaseModel):
    posture: str
    temporal_state: str
    silence_locked: bool
    atmospheric_weight: float
    frontend_phrase: str
    institutional_memory: float = 0.0
    atmospheric_memory_phrase: str = "Continuity."

class RiskEvaluateRequest(BaseModel):
    environment_id: str = Field(default="default", min_length=1, max_length=80)
    source: str = Field(..., min_length=1, max_length=80)
    category: RiskCategory = Field(default=RiskCategory.unknown)
    severity: float = Field(..., ge=0.0, le=1.0)

class EvidenceRecordRequest(BaseModel):
    environment_id: str = Field(default="default", min_length=1, max_length=80)
    category: str = Field(..., min_length=1, max_length=80)
    weight: float = Field(..., ge=0.0, le=1.0)

class AdminReviewRequest(BaseModel):
    reviewer: str = Field(default="admin", min_length=1, max_length=80)
    note: Optional[str] = Field(None, max_length=500)

class AdminContinuityRestoreRequest(BaseModel):
    reviewer: str = Field(default="admin", min_length=1, max_length=80)
    note: Optional[str] = Field(None, max_length=500)

class AdminActionResponse(BaseModel):
    ok: bool = True
    environment_id: str
    action: str
    message: str
    timestamp: datetime
    action_count: Optional[int] = None
    review_id: Optional[int] = None

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=80)
    password: str = Field(..., min_length=1)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class CurrentAdmin(BaseModel):
    username: str

class GenericWebhookSignal(BaseModel):
    environment_id: str = Field(default="default", min_length=1, max_length=80)
    source: str = Field(..., min_length=1, max_length=80)
    event_type: Optional[str] = Field(None, max_length=80)
    severity: float = Field(..., ge=0.0, le=1.0)
    category: RiskCategory = Field(default=RiskCategory.unknown)
    summary: Optional[str] = Field(None, max_length=500)
    external_id: Optional[str] = Field(None, max_length=80)
    metadata: Optional[Dict[str, Any]] = None

class AdminEnvironmentSummaryResponse(BaseModel):
    environment_id: str
    active_risk_count: int
    average_risk_severity: float
    suppressed_risk_count: int
    resolved_risk_count: int
    recent_webhook_count: int
    latest_webhook_timestamp: Optional[str]
    latest_posture: str
    temporal_state: str
    silence_locked: bool
    continuity_ticks: float
    latest_governance_timestamp: Optional[str]

# Compatibility alias for routes.py
AdminSummaryResponse = AdminEnvironmentSummaryResponse
