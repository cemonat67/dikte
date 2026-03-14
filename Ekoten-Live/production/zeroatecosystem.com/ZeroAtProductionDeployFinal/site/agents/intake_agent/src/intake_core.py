from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib

from agents.intake_agent.src.validate import validate_record, score_confidence


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def fingerprint(record):
    raw = json.dumps(record, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path



def _as_validation_payload(rec: dict, source: str) -> dict:
    return {
        "meta": {
            "source_type": rec.get("source_type") or source or "intake",
            "source_name": rec.get("source_name") or "unified_intake",
            "received_at": rec.get("received_at") or now_iso(),
            "facility": rec.get("facility"),
            "review_status": rec.get("review_status") or "in_review",
            "period_start": rec.get("period_start"),
            "period_end": rec.get("period_end"),
        },
        "metrics": {
            "water_m3": rec.get("water_m3"),
            "wastewater_m3": rec.get("wastewater_m3"),
            "energy_kwh": rec.get("energy_kwh"),
            "natural_gas_m3": rec.get("natural_gas_m3"),
            "steam_ton": rec.get("steam_ton"),
            "production_kg": rec.get("production_kg"),
            "co2_kg": rec.get("co2_kg"),
        },
        "wastewater_quality": {
            "cod_mg_l": rec.get("cod_mg_l"),
            "bod_mg_l": rec.get("bod_mg_l"),
            "tss_mg_l": rec.get("tss_mg_l"),
            "ph": rec.get("ph"),
        },
        "review": {
            "validation_errors": [],
        },
    }


def run_intake_records(records, source, intake_root, facility=None):
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    batch_id = f"{source}_{ts}"

    normalized_dir = Path(intake_root) / "normalized"
    review_dir = Path(intake_root) / "review"
    log_dir = Path(intake_root) / "logs"

    normalized_dir.mkdir(parents=True, exist_ok=True)
    review_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    processed = []
    invalid = []

    for i, rec in enumerate(records, start=1):
        rec = dict(rec)

        if facility and not rec.get("facility"):
            rec["facility"] = facility

        rec_meta = dict(rec.get("_meta", {}))
        rec_meta.update({
            "source": source,
            "batch_id": batch_id,
            "row_number": i,
            "ingested_at": now_iso(),
            "fingerprint": fingerprint(rec),
        })
        rec["_meta"] = rec_meta

        validation_payload = _as_validation_payload(rec, source)
        errors = validate_record(validation_payload)
        valid = len(errors) == 0
        confidence = score_confidence(validation_payload, errors)

        rec["_validation"] = {
            "is_valid": valid,
            "errors": errors,
        }
        rec["_confidence"] = confidence

        processed.append(rec)

        if not valid:
            invalid.append({
                "row_number": i,
                "facility": rec.get("facility"),
                "errors": errors,
                "confidence": confidence,
            })

    avg_conf = round(
        sum(float(r.get("_confidence", 0) or 0) for r in processed) / max(len(processed), 1),
        2
    )

    normalized_payload = {
        "status": "processed",
        "source": source,
        "batch_id": batch_id,
        "record_count": len(processed),
        "valid_count": sum(1 for r in processed if r["_validation"]["is_valid"]),
        "invalid_count": len(invalid),
        "avg_confidence": avg_conf,
        "records": processed,
        "created_at": now_iso(),
    }

    review_manifest = {
        "batch_id": batch_id,
        "source": source,
        "status": "review_required" if invalid else "ready",
        "record_count": len(processed),
        "invalid_count": len(invalid),
        "avg_confidence": avg_conf,
        "invalid_records": invalid,
        "created_at": now_iso(),
    }

    normalized_path = normalized_dir / f"{batch_id}.normalized.json"
    review_path = review_dir / f"{batch_id}.review.json"
    log_file = log_dir / "intake_events.jsonl"

    _write_json(normalized_path, normalized_payload)
    _write_json(review_path, review_manifest)

    event = {
        "ts": now_iso(),
        "event": "intake_processed",
        "source": source,
        "batch_id": batch_id,
        "record_count": len(processed),
        "valid_count": normalized_payload["valid_count"],
        "invalid_count": len(invalid),
        "avg_confidence": avg_conf,
        "normalized_json": str(normalized_path),
        "review_manifest": str(review_path),
    }

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    return {
        "batch_id": batch_id,
        "normalized_json": str(normalized_path),
        "review_manifest": str(review_path),
        "record_count": len(processed),
        "valid_count": normalized_payload["valid_count"],
        "invalid_count": len(invalid),
        "avg_confidence": avg_conf,
    }
