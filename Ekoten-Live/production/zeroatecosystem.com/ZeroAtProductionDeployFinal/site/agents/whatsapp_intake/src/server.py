from datetime import datetime
from pathlib import Path
from .unified_intake import run_csv_upload_pipeline
import json
import os
import shutil

from fastapi import FastAPI, Request, Query, UploadFile, File, Form, HTTPException
from dotenv import load_dotenv
from agents.intake_core.src.commit_service import CommitService

load_dotenv('agents/intake_agent/.env')
from agents.intake_core.src.intake_writer import IntakeWriter
from agents.intake_core.src.metric_registry import MetricRegistry
from agents.intake_core.src.facility_registry import FacilityRegistry, build_default_ekoten_registry
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .adapter import parse_whatsapp_to_record
from agents.intake_agent.src.intake_core import run_intake_records
from agents.brain.brain_rules import evaluate_factory_state
from agents.intake_agent.src.writers import write_normalized_json, write_review_manifest
from agents.intake_agent.src.validate import validate_record, score_confidence
from agents.intake_agent.src.config import REJECTED_DIR

app = FastAPI()

intake_writer = IntakeWriter()
metric_registry = MetricRegistry()
facility_registry = build_default_ekoten_registry()
commit_service = CommitService(
    intake_writer=intake_writer,
    metric_registry=metric_registry,
    facility_registry=facility_registry,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8080",
        "http://localhost:8080",
        "http://127.0.0.1:8010",
        "http://localhost:8010",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SITE_ROOT = Path(__file__).resolve().parents[3]
INTAKE_ROOT = SITE_ROOT / "agents" / "intake_agent"
ARCHIVE_DIR = INTAKE_ROOT / "archive"
LOG_FILE = INTAKE_ROOT / "logs" / "intake_events.jsonl"
NORMALIZED_FILE = INTAKE_ROOT / "normalized" / "sample_metrics.normalized.json"


def write_rejected_json(record: dict, base_name: str) -> str:
    REJECTED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REJECTED_DIR / f"{base_name}.rejected.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump([record], f, indent=2, ensure_ascii=False)
    return str(out_path)


def read_json(path: Path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def read_jsonl(path: Path, limit: int = 5):
    rows = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    except Exception:
        return []
    return rows[-limit:]


def latest_summary_file():
    files = sorted(ARCHIVE_DIR.glob("*.summary.json"), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def latest_rejected_file():
    files = sorted((INTAKE_ROOT / "rejected").glob("*.rejected.json"), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def build_snapshot_for_facility(facility: str):
    rows = read_json(NORMALIZED_FILE, [])
    chosen = None

    for row in rows:
        meta = row.get("meta", {})
        if str(meta.get("facility", "")).lower() == facility.lower():
            chosen = row

    if chosen is None and rows:
        chosen = rows[-1]

    if not chosen:
        return {
            "snapshot_date": datetime.now().strftime("%Y-%m-%d"),
            "water_m3": None,
            "wastewater_m3": None,
            "energy_kwh": None,
            "natural_gas_m3": None,
            "steam_ton": None,
            "production_kg": None,
            "co2_kg": None,
            "cod_mg_l": None,
            "bod_mg_l": None,
            "tss_mg_l": None,
            "ph": None
        }

    metrics = chosen.get("metrics", {})
    ww = chosen.get("wastewater_quality", {})
    meta = chosen.get("meta", {})

    return {
        "snapshot_date": meta.get("period_end") or datetime.now().strftime("%Y-%m-%d"),
        "water_m3": metrics.get("water_m3"),
        "wastewater_m3": metrics.get("wastewater_m3"),
        "energy_kwh": metrics.get("energy_kwh"),
        "natural_gas_m3": metrics.get("natural_gas_m3"),
        "steam_ton": metrics.get("steam_ton"),
        "production_kg": metrics.get("production_kg"),
        "co2_kg": metrics.get("co2_kg"),
        "cod_mg_l": ww.get("cod_mg_l"),
        "bod_mg_l": ww.get("bod_mg_l"),
        "tss_mg_l": ww.get("tss_mg_l"),
        "ph": ww.get("ph")
    }


@app.post("/api/intake/upload")
async def intake_upload(
    file: UploadFile = File(...),
    facility: str = Form("Ekoten")
):
    upload_dir = INTAKE_ROOT / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_name = file.filename or f"upload_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    stored_at = upload_dir / safe_name

    with open(stored_at, "wb") as f:
        shutil.copyfileobj(file.file, f)

    summary = run_csv_upload_pipeline(
        csv_path=stored_at,
        intake_root=INTAKE_ROOT,
        source="csv_upload_ui",
        facility=(facility or "").strip() or None,
    )

    ops_payload = load_ops_snapshot() if "load_ops_snapshot" in globals() else {}

    return JSONResponse({
        "status": summary["status"],
        "message": "Upload received and intake pipeline processed",
        "file_name": summary["file_name"],
        "stored_at": summary["stored_at"],
        "batch_id": summary["batch_id"],
        "record_count": summary["record_count"],
        "valid_count": summary["valid_count"],
        "invalid_count": summary["invalid_count"],
        "avg_confidence": summary["avg_confidence"],
        "normalized_json": summary["normalized_json"],
        "review_manifest": summary["review_manifest"],
        "event_log": summary["event_log"],
        "ops": ops_payload,
        "source": "api"
    })


@app.get("/api/intake/ops")
async def intake_ops(facility: str = Query(default="Ekoten")):
    summary_path = latest_summary_file()
    rejected_path = latest_rejected_file()

    summary = read_json(summary_path, {}) if summary_path else {}
    rejected_rows = read_json(rejected_path, []) if rejected_path else []
    event_rows = read_jsonl(LOG_FILE, 5)

    events = []
    for row in event_rows:
        events.append({
            "ts": row.get("ts", ""),
            "stage": row.get("event_type", "event"),
            "status": row.get("status", ""),
            "detail": row.get("extra", {}).get("input_name")
                      or row.get("archive_path")
                      or row.get("normalized_path")
                      or row.get("review_path")
                      or ""
        })

    return JSONResponse({
        "facility": facility,
        "latest_batch": {
            "batch_id": summary.get("batch_id", "—"),
            "source": summary.get("source", "—"),
            "facility": facility,
            "status": summary.get("status", "—")
        },
        "counts": {
            "accepted": summary.get("counts", {}).get("accepted_records", 0),
            "rejected": summary.get("counts", {}).get("rejected_records", len(rejected_rows) if isinstance(rejected_rows, list) else 0)
        },
        "processor": {
            "status": "Processed" if summary else "No Data",
            "note": summary.get("input_name", "No summary found")
        },
        "events": events,
        "snapshot": build_snapshot_for_facility(facility)
    })


@app.post("/api/intake/whatsapp")
async def whatsapp_intake(request: Request):
    payload = await request.json()
    record = parse_whatsapp_to_record(payload)

    flat_record = {
        "facility": record.get("meta", {}).get("facility"),
        "source_type": record.get("meta", {}).get("source_type") or "whatsapp",
        "source_name": record.get("meta", {}).get("source_name") or "whatsapp_form",
        "received_at": record.get("meta", {}).get("received_at"),
        "review_status": record.get("meta", {}).get("review_status") or "in_review",
        "period_start": record.get("meta", {}).get("period_start"),
        "period_end": record.get("meta", {}).get("period_end"),
        "water_m3": record.get("metrics", {}).get("water_m3"),
        "wastewater_m3": record.get("metrics", {}).get("wastewater_m3"),
        "energy_kwh": record.get("metrics", {}).get("energy_kwh"),
        "natural_gas_m3": record.get("metrics", {}).get("natural_gas_m3"),
        "steam_ton": record.get("metrics", {}).get("steam_ton"),
        "production_kg": record.get("metrics", {}).get("production_kg"),
        "co2_kg": record.get("metrics", {}).get("co2_kg"),
        "cod_mg_l": record.get("wastewater_quality", {}).get("cod_mg_l"),
        "bod_mg_l": record.get("wastewater_quality", {}).get("bod_mg_l"),
        "tss_mg_l": record.get("wastewater_quality", {}).get("tss_mg_l"),
        "ph": record.get("wastewater_quality", {}).get("ph"),
    }

    summary = run_intake_records(
        records=[flat_record],
        source="whatsapp",
        intake_root=INTAKE_ROOT,
        facility=flat_record.get("facility"),
    )

    status = "accepted" if summary["invalid_count"] == 0 else "rejected"

    return {
        "status": status,
        "batch_id": summary["batch_id"],
        "stored_at": summary["normalized_json"],
        "review_manifest": summary["review_manifest"],
        "validation_errors": [],
        "confidence_score": summary["avg_confidence"],
        "record_preview": {
            "facility": flat_record.get("facility"),
            "water_m3": flat_record.get("water_m3"),
            "energy_kwh": flat_record.get("energy_kwh"),
            "production_kg": flat_record.get("production_kg"),
        }
    }


@app.post("/api/intake/raw")
async def raw_intake(request: Request):
    payload = await request.json()

    flat_record = {
        "facility": payload.get("facility"),
        "source_type": payload.get("source_type") or "api",
        "source_name": payload.get("source_name") or "raw_api",
        "received_at": payload.get("received_at"),
        "review_status": payload.get("review_status") or "in_review",
        "period_start": payload.get("period_start"),
        "period_end": payload.get("period_end"),
        "water_m3": payload.get("water_m3"),
        "wastewater_m3": payload.get("wastewater_m3"),
        "energy_kwh": payload.get("energy_kwh"),
        "natural_gas_m3": payload.get("natural_gas_m3"),
        "steam_ton": payload.get("steam_ton"),
        "production_kg": payload.get("production_kg"),
        "co2_kg": payload.get("co2_kg"),
        "cod_mg_l": payload.get("cod_mg_l"),
        "bod_mg_l": payload.get("bod_mg_l"),
        "tss_mg_l": payload.get("tss_mg_l"),
        "ph": payload.get("ph"),
    }

    summary = run_intake_records(
        records=[flat_record],
        source="api_raw",
        intake_root=INTAKE_ROOT,
        facility=flat_record.get("facility"),
    )

    status = "accepted" if summary["invalid_count"] == 0 else "rejected"

    return {
        "status": status,
        "batch_id": summary["batch_id"],
        "stored_at": summary["normalized_json"],
        "review_manifest": summary["review_manifest"],
        "validation_errors": [],
        "confidence_score": summary["avg_confidence"],
        "record_preview": {
            "facility": flat_record.get("facility"),
            "water_m3": flat_record.get("water_m3"),
            "energy_kwh": flat_record.get("energy_kwh"),
            "production_kg": flat_record.get("production_kg"),
        }
    }

from agents.intake_core.src.preflight_service import run_csv_preflight


@app.post("/api/intake/preflight")
async def intake_preflight(file: UploadFile = File(...)):
    filename = file.filename or "upload.csv"

    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported for preflight")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    result = run_csv_preflight(
        file_bytes=raw,
        file_name=filename,
        db_url=os.getenv("DATABASE_URL"),
    )
    return result


@app.post("/api/intake/commit")
async def intake_commit(
    file: UploadFile = File(...),
    zero_fill_missing: bool = Form(False),
):
    file_bytes = await file.read()

    result = commit_service.commit_csv_bytes(
        file_bytes=file_bytes,
        file_name=file.filename or "upload.csv",
        zero_fill_missing=zero_fill_missing,
    )

    return {
        "ok": True,
        "file_name": file.filename,
        "inserted": result.inserted,
        "duplicate": result.duplicate,
        "rejected": result.rejected,
        "total_input_rows": result.total_input_rows,
        "total_expanded_events": result.total_expanded_events,
        "zero_filled_fields": result.zero_filled_fields,
        "warnings": result.warnings,
        "rejected_rows": result.rejected_rows,
    }


@app.get("/api/brain/status")
async def brain_status(facility: str = "ekoten"):
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise HTTPException(status_code=500, detail="DATABASE_URL is not set")

    try:
        result = evaluate_factory_state(db_url=db_url, facility=facility)
        return {
            "ok": True,
            "brain": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brain evaluation failed: {e}")


