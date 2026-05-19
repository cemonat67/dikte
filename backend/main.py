import asyncio
import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router
from backend.db.session import engine, Base, SessionLocal
from backend.models.domain import ContinuityMemory
from backend.engines.trust import tick_engines
from backend.core.config import settings
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SYSTEM_BOOT_TIME = datetime.now(timezone.utc)

app = FastAPI(
    title="Zero@Trust API", 
    version="0.9.0",
    description="Headless operational trust posture API"
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled operational exception caught at boundary.")
    return JSONResponse(
        status_code=500,
        content={
            "posture": "constrained",
            "temporal_state": "unavailable",
            "message": "Service posture maintained"
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.info("Malformed payload discarded silently at boundary.")
    return JSONResponse(
        status_code=400,
        content={
            "posture": "constrained",
            "temporal_state": "unavailable",
            "message": "Service posture maintained",
            "status": "discarded"
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Log the detail securely but never leak it back to the client natively
    if exc.status_code >= 500:
        logger.error(f"Internal HTTP Exception: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "posture": "constrained",
            "temporal_state": "unavailable",
            "message": "Service posture maintained"
        }
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=settings.API_PREFIX)

async def background_engine_tick():
    while True:
        db = SessionLocal()
        try:
            # Dynamically fetch all active environments to tick them independently
            envs = db.query(ContinuityMemory.environment_id).distinct().all()
            active_envs = [e[0] for e in envs]
            if "default" not in active_envs:
                active_envs.append("default")
                
            for env_id in active_envs:
                tick_engines(db, env_id)
                logger.info(f"Trust tick complete: {env_id}")
                
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Tick error: {e}")
        finally:
            db.close()
        await asyncio.sleep(settings.TRUST_TICK_SECONDS)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Zero@Trust Core...")
    logger.info(f"APP_ENV: {settings.APP_ENV}")
    logger.info(f"Database Driver: {engine.url.drivername}")
    logger.info(f"Tick Rate: {settings.TRUST_TICK_SECONDS}s")
    
    # SQLite local migration safety hack
    if settings.APP_ENV == "local" and engine.url.drivername == "sqlite" and os.path.exists("./zerotrust.db"):
        try:
            db = SessionLocal()
            db.execute("SELECT environment_id FROM continuity_memory LIMIT 1")
            db.execute("SELECT resolved FROM risk_signals LIMIT 1")
            db.close()
        except Exception:
            db.close()
            os.remove("./zerotrust.db")

    Base.metadata.create_all(bind=engine)
    
    asyncio.create_task(background_engine_tick())

@app.get("/health", tags=["Public"])
def health_check():
    # v16.2 Recovery Posture
    now = datetime.now(timezone.utc)
    seconds_since_boot = (now - SYSTEM_BOOT_TIME).total_seconds()
    
    # If the system just came online, it self-reports as recovering for 60 seconds
    if seconds_since_boot < 60:
        status = "recovering"
    else:
        status = "ok"
        
    return {
        "status": status,
        "app_env": settings.APP_ENV,
        "db_driver": engine.url.drivername,
        "api_prefix": settings.API_PREFIX,
        "version": "0.9.0",
        "uptime_seconds": int(seconds_since_boot)
    }

from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
