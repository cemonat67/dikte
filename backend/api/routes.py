from fastapi import APIRouter, Depends, Query, Header, HTTPException
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.schemas.domain import TrustStateResponse, RiskEvaluateRequest, EvidenceRecordRequest, LoginRequest, TokenResponse, CurrentAdmin, GenericWebhookSignal
from backend.engines import risk, trust, evidence
from backend.core.config import settings
import logging
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter()

security = HTTPBearer(auto_error=False)

last_known_safe_state = {}
last_known_admin_summary = {}

def get_stale_trust_state(environment_id: str):
    cached = last_known_safe_state.get(environment_id)
    if cached:
        cached_copy = dict(cached)
        cached_copy["posture"] = "constrained"
        cached_copy["temporal_state"] = "frozen"
        cached_copy["frontend_phrase"] = "Operational continuity preserved"
        cached_copy["continuity_mode"] = "read_only"
        cached_copy["institutional_memory"] = 0.0
        cached_copy["atmospheric_memory_phrase"] = "Operational continuity preserved"
        return cached_copy
    return {
        "environment_id": environment_id,
        "posture": "constrained",
        "temporal_state": "frozen",
        "silence_locked": False,
        "atmospheric_weight": 0.0,
        "evidence_confidence": 0.0,
        "governance_drag": 0.0,
        "final_trust_pressure": 0.0,
        "weighted_risk_score": 0.0,
        "frontend_phrase": "Operational continuity preserved",
        "continuity_mode": "read_only",
        "institutional_memory": 0.0,
        "atmospheric_memory_phrase": "Operational continuity preserved"
    }

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_admin_key(
    x_admin_key: str = Header(None), 
    auth: HTTPAuthorizationCredentials = Depends(security)
):
    if settings.APP_ENV == "local" and x_admin_key == settings.ADMIN_API_KEY:
        return CurrentAdmin(username="local_admin")
        
    if not auth or not auth.credentials:
        logger.warning("Failed admin authentication attempt: Missing Bearer token.")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
    try:
        payload = jwt.decode(auth.credentials, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return CurrentAdmin(username=username)
    except JWTError:
        logger.warning("Failed JWT decoding attempt.")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def verify_webhook_secret(x_webhook_secret: str = Header(None)):
    if not x_webhook_secret or x_webhook_secret != settings.WEBHOOK_SECRET:
        logger.warning("Failed webhook authentication attempt.")
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
    return x_webhook_secret

def get_db_optional():
    try:
        db = next(get_db())
        yield db
    except Exception:
        yield None

@router.post("/auth/login", response_model=TokenResponse, tags=["Public"])
def login(req: LoginRequest):
    if req.username != settings.ADMIN_USERNAME or req.password != settings.ADMIN_PASSWORD:
        logger.warning(f"Failed login attempt for username: {req.username}")
        raise HTTPException(status_code=401, detail="Incorrect username or password")
        
    logger.info(f"Successful admin login for: {req.username}")
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": req.username}, expires_delta=access_token_expires
    )
    return TokenResponse(access_token=access_token, expires_in=settings.JWT_EXPIRE_MINUTES * 60)

@router.get("/trust/state", tags=["Public"])
def get_trust_state(
    environment_id: str = Query("default"),
    db: Session = Depends(get_db_optional)
):
    try:
        if db is None:
            raise Exception("Database partition dropped")
        state = trust.calculate_trust_state(db, environment_id)
        last_known_safe_state[environment_id] = state
        return state
    except Exception as e:
        logger.warning(f"DB offline for {environment_id}. Serving frozen state.")
        return get_stale_trust_state(environment_id)

@router.post("/risk/evaluate", tags=["Public"])
def evaluate_risk(req: RiskEvaluateRequest, db: Session = Depends(get_db_optional)):
    result = risk.evaluate_risk(db, req.source, req.category, req.severity, req.environment_id)
    return result

@router.post("/evidence/record", tags=["Public"])
def record_evidence(req: EvidenceRecordRequest, db: Session = Depends(get_db_optional)):
    result = evidence.record_evidence(db, req.category, req.weight, req.environment_id)
    return result

@router.post("/webhooks/signal", tags=["Webhook"])
def receive_webhook_signal(req: GenericWebhookSignal, db: Session = Depends(get_db_optional), secret: str = Depends(verify_webhook_secret)):
    try:
        if db is None:
            raise Exception("Database partition dropped")
        result = risk.evaluate_risk(
            db=db, 
            source=req.source, 
            category=req.category, 
            severity=req.severity, 
            environment_id=req.environment_id,
            external_id=req.external_id,
            event_type=req.event_type,
            summary=req.summary,
            metadata_json=req.metadata
        )
        logger.info(f"Accepted webhook signal from source '{req.source}' for env '{req.environment_id}'.")
        return {
            "ok": True,
            "environment_id": req.environment_id,
            "accepted": True,
            "message": "Signal accepted",
            "timestamp": datetime.now(timezone.utc)
        }
    except Exception as e:
        logger.warning("DB partition failed during webhook ingest. Deferring response.")
        return JSONResponse(
            status_code=503,
            content={
                "ok": False,
                "status": "deferred",
                "message": "Operational continuity preserved. Retry deferred."
            }
        )

@router.get("/governance/posture", response_model=TrustStateResponse, tags=["Public"])
def get_governance_posture(
    environment_id: str = Query("default"),
    db: Session = Depends(get_db_optional)
):
    return trust.calculate_trust_state(db, environment_id)

@router.post("/simulate/trust_event/{event_type}", tags=["Simulation"])
def simulate_trust_event(event_type: str, db: Session = Depends(get_db_optional)):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
        
    category_map = {
        "identity_confidence_drop": "identity",
        "midnight_executive_login": "identity",
        "supplier_approval_drift": "supplier",
        "approval_drift": "approval",
        "documentation_expiry": "compliance",
        "document_integrity_degradation": "documentation",
        "payment_verification_mismatch": "payment"
    }
    category = category_map.get(event_type, "operational")
    
    if event_type == "supplier_approval_drift":
        severity = 0.65
    elif event_type == "midnight_executive_login":
        severity = 0.40
    elif event_type in ["document_integrity_degradation", "payment_verification_mismatch"]:
        # Ensure severity is high enough to survive hysteresis decay and remain >= 0.8 (Degraded)
        severity = 0.90
    else:
        severity = 0.6
    
    from backend.models.domain import RiskSignal
    signal = RiskSignal(
        environment_id="default",
        source="simulation",
        category=category,
        severity=severity,
        persistence=0, 
        human_review_required=True
    )
    db.add(signal)
    db.commit()
    return {"status": "injected", "event": event_type, "category": category}

@router.post("/trust/action/resolve", tags=["Public"])
def resolve_dominant_condition(db: Session = Depends(get_db_optional)):
    if not db:
        return {"ok": False}
    from backend.models.domain import RiskSignal
    active_risks = db.query(RiskSignal).filter(
        RiskSignal.environment_id == "default",
        RiskSignal.resolved == False
    ).all()
    from datetime import datetime, timezone
    now_utc = datetime.now(timezone.utc)
    for r in active_risks:
        r.resolved = True
        r.resolved_at = now_utc
    db.commit()
    return {"ok": True, "message": "Human control registered."}

from backend.models.domain import ReviewEvent, GovernanceState, RiskSignal
from backend.schemas.domain import AdminReviewRequest, AdminContinuityRestoreRequest, AdminSummaryResponse, AdminActionResponse
from backend.engines import temporal

@router.get("/admin/environment/{environment_id}/summary", response_model=AdminSummaryResponse, dependencies=[Depends(verify_admin_key)], tags=["Admin"])
def get_admin_summary(environment_id: str, db: Session = Depends(get_db_optional)):
    try:
        if db is None:
            raise Exception("Database partition dropped")
            
        all_risks = db.query(RiskSignal).filter(RiskSignal.environment_id == environment_id).all()
        
        active_risks = [r for r in all_risks if not r.resolved and r.severity > 0.01]
        count = len(active_risks)
        avg_sev = sum(r.severity for r in active_risks) / count if count > 0 else 0.0
        
        suppressed_count = len([r for r in active_risks if r.suppressed])
        resolved_count = len([r for r in all_risks if r.resolved])
        
        ts = trust.calculate_trust_state(db, environment_id)
        gov = db.query(GovernanceState).filter(GovernanceState.environment_id == environment_id).order_by(GovernanceState.id.desc()).first()
        
        temp_mem = temporal.get_temporal_state(db, environment_id)
        
        recent_webhook_count = sum(1 for r in all_risks if r.external_id is not None)
        latest_webhook = next((r.created_at for r in reversed(all_risks) if r.external_id is not None), None)
        
        summary = AdminSummaryResponse(
            environment_id=environment_id,
            active_risk_count=count,
            average_risk_severity=avg_sev,
            suppressed_risk_count=suppressed_count,
            resolved_risk_count=resolved_count,
            recent_webhook_count=recent_webhook_count,
            latest_webhook_timestamp=str(latest_webhook) if latest_webhook else None,
            weighted_risk_score=ts.get("weighted_risk_score", 0.0),
            evidence_confidence=ts.get("evidence_confidence", 0.0),
            governance_drag=ts.get("governance_drag", 0.0),
            final_trust_pressure=ts.get("final_trust_pressure", 0.0),
            latest_posture=ts["posture"],
            temporal_state=ts["temporal_state"],
            silence_locked=ts["silence_locked"],
            continuity_ticks=temp_mem["temporal_ticks"] if isinstance(temp_mem, dict) else (temp_mem.uptime_ticks if temp_mem else 0),
            latest_governance_timestamp=str(gov.created_at) if gov else None
        )
        last_known_admin_summary[environment_id] = summary
        return summary
    except Exception as e:
        logger.warning(f"DB offline for admin summary on {environment_id}. Serving frozen snapshot.")
        cached = last_known_admin_summary.get(environment_id)
        if cached:
            # We explicitly modify the frozen object to signal constraint
            cached_copy = cached.dict()
            cached_copy["latest_posture"] = "constrained"
            cached_copy["temporal_state"] = "frozen"
            return cached_copy
            
        return AdminSummaryResponse(
            environment_id=environment_id,
            active_risk_count=0,
            average_risk_severity=0.0,
            suppressed_risk_count=0,
            resolved_risk_count=0,
            recent_webhook_count=0,
            latest_webhook_timestamp=None,
            weighted_risk_score=0.0,
            evidence_confidence=0.0,
            governance_drag=0.0,
            final_trust_pressure=0.0,
            latest_posture="constrained",
            temporal_state="frozen",
            silence_locked=False,
            continuity_ticks=0,
            latest_governance_timestamp=None
        )

@router.post("/admin/environment/{environment_id}/resolve-risk", response_model=AdminActionResponse, dependencies=[Depends(verify_admin_key)], tags=["Admin"])
def admin_resolve_risk(environment_id: str, req: AdminReviewRequest, db: Session = Depends(get_db_optional)):
    count = risk.resolve_all_risks(db, environment_id, req.reviewer, req.note)
    logger.warning(f"Admin '{req.reviewer}' resolved {count} risks for environment '{environment_id}'.")
    return AdminActionResponse(ok=True, environment_id=environment_id, action="resolve-risk", message=f"Resolved {count} risks", timestamp=datetime.now(timezone.utc), action_count=count)

@router.post("/admin/environment/{environment_id}/suppress-risk", response_model=AdminActionResponse, dependencies=[Depends(verify_admin_key)], tags=["Admin"])
def admin_suppress_risk(environment_id: str, req: AdminReviewRequest, db: Session = Depends(get_db_optional)):
    count = risk.suppress_all_risks(db, environment_id, req.reviewer, req.note)
    logger.warning(f"Admin '{req.reviewer}' suppressed {count} risks for environment '{environment_id}'.")
    return AdminActionResponse(ok=True, environment_id=environment_id, action="suppress-risk", message=f"Suppressed {count} risks", timestamp=datetime.now(timezone.utc), action_count=count)

@router.post("/admin/environment/{environment_id}/restore-continuity", response_model=AdminActionResponse, dependencies=[Depends(verify_admin_key)], tags=["Admin"])
def admin_restore_continuity(environment_id: str, req: AdminContinuityRestoreRequest, db: Session = Depends(get_db_optional)):
    temporal.restore_continuity(db, environment_id, req.reviewer, req.note)
    logger.warning(f"Admin '{req.reviewer}' restored continuity for environment '{environment_id}'.")
    return AdminActionResponse(ok=True, environment_id=environment_id, action="restore-continuity", message="Continuity restored", timestamp=datetime.now(timezone.utc))

@router.post("/admin/environment/{environment_id}/record-review", response_model=AdminActionResponse, dependencies=[Depends(verify_admin_key)], tags=["Admin"])
def admin_record_review(environment_id: str, req: AdminReviewRequest, db: Session = Depends(get_db_optional)):
    event = ReviewEvent(environment_id=environment_id, reviewer=req.reviewer, action="review", note=req.note, event_type="governance")
    db.add(event)
    db.commit()
    logger.warning(f"Admin '{req.reviewer}' recorded a manual review for environment '{environment_id}'.")
    return AdminActionResponse(ok=True, environment_id=environment_id, action="record-review", message="Review recorded", timestamp=datetime.now(timezone.utc), review_id=event.id)
