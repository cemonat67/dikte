from __future__ import annotations
from agents.intake_agent.src.intake_core import run_intake_records


import csv
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
from typing import Any, Dict, List, Tuple


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resolve_symbol(symbol_name: str, module_candidates: List[str]):
    for mod_name in module_candidates:
        try:
            mod = import_module(mod_name)
            if hasattr(mod, symbol_name):
                return getattr(mod, symbol_name)
        except Exception:
            continue
    raise ImportError(f"Could not resolve symbol '{symbol_name}' from candidates: {module_candidates}")


def _safe_float(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if not s:
        return None
    s = s.replace(".", "").replace(",", ".") if s.count(",") == 1 and s.count(".") > 1 else s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None


def _normalize_key(k: str) -> str:
    return str(k).strip().lower().replace(" ", "_").replace("-", "_")


def _read_csv_records(csv_path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean = {}
            for k, v in row.items():
                nk = _normalize_key(k)
                clean[nk] = v.strip() if isinstance(v, str) else v
            records.append(clean)
    return records


def _coerce_metrics(record: Dict[str, Any]) -> Dict[str, Any]:
    metric_keys = [
        "water_m3",
        "energy_kwh",
        "natural_gas_m3",
        "steam_ton",
        "production_kg",
        "production_ton",
        "co2_kg",
        "co2_ton",
    ]
    out = dict(record)
    for key in metric_keys:
        if key in out:
            out[key] = _safe_float(out.get(key))
    return out


def _record_fingerprint(record: Dict[str, Any]) -> str:
    raw = json.dumps(record, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _append_jsonl(path: Path, item: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")


def _fallback_validate_record(record: Dict[str, Any]) -> Dict[str, Any]:
    errors = []
    facility = record.get("facility")
    metric_present = any(record.get(k) not in (None, "", 0, 0.0) for k in [
        "water_m3", "energy_kwh", "natural_gas_m3", "steam_ton", "production_kg", "production_ton"
    ])
    if not facility:
        errors.append("missing_meta:facility")
    if not metric_present:
        errors.append("missing_metrics:any")
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
    }


def _fallback_score_confidence(record: Dict[str, Any], validation: Dict[str, Any]) -> float:
    score = 0.4
    if record.get("facility"):
        score += 0.2
    present = sum(
        1 for k in ["water_m3", "energy_kwh", "natural_gas_m3", "steam_ton", "production_kg", "production_ton"]
        if record.get(k) not in (None, "", 0, 0.0)
    )
    score += min(present * 0.08, 0.32)
    if validation.get("is_valid"):
        score += 0.08
    return round(min(score, 0.99), 2)


def _fallback_write_normalized_json(output_path: Path, payload: Dict[str, Any]) -> str:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(output_path)


def _fallback_write_review_manifest(output_path: Path, payload: Dict[str, Any]) -> str:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(output_path)


def _get_validate_record():
    try:
        return _resolve_symbol("validate_record", [
            "agents.intake_agent.src.validation",
            "agents.intake_agent.src.validators",
            "agents.intake_agent.src.main",
            "agents.intake_agent.src.pipeline",
        ])
    except Exception:
        return _fallback_validate_record


def _get_score_confidence():
    try:
        return _resolve_symbol("score_confidence", [
            "agents.intake_agent.src.validation",
            "agents.intake_agent.src.validators",
            "agents.intake_agent.src.main",
            "agents.intake_agent.src.pipeline",
        ])
    except Exception:
        return _fallback_score_confidence


def _get_write_normalized_json():
    try:
        return _resolve_symbol("write_normalized_json", [
            "agents.intake_agent.src.writers",
            "agents.intake_agent.src.io_utils",
            "agents.intake_agent.src.main",
            "agents.intake_agent.src.pipeline",
        ])
    except Exception:
        return None


def _get_write_review_manifest():
    try:
        return _resolve_symbol("write_review_manifest", [
            "agents.intake_agent.src.writers",
            "agents.intake_agent.src.io_utils",
            "agents.intake_agent.src.main",
            "agents.intake_agent.src.pipeline",
        ])
    except Exception:
        return None


def run_csv_upload_pipeline(
    *,
    csv_path: Path,
    intake_root: Path,
    source: str = "upload_csv",
    facility: str | None = None,
) -> Dict[str, Any]:
    validate_record = _get_validate_record()
    score_confidence = _get_score_confidence()
    write_normalized_json_fn = _get_write_normalized_json()
    write_review_manifest_fn = _get_write_review_manifest()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_id = f"{source}_{ts}"
    normalized_dir = intake_root / "normalized"
    review_dir = intake_root / "review"
    logs_dir = intake_root / "logs"

    raw_records = _read_csv_records(csv_path)
    processed_records: List[Dict[str, Any]] = []
    invalid_records: List[Dict[str, Any]] = []

    for idx, raw in enumerate(raw_records, start=1):
        rec = _coerce_metrics(raw)
        if facility and not rec.get("facility"):
            rec["facility"] = facility

        rec["_meta"] = {
            "source": source,
            "batch_id": batch_id,
            "row_number": idx,
            "ingested_at": _utc_now(),
            "fingerprint": _record_fingerprint(rec),
            "original_filename": csv_path.name,
        }

        validation = validate_record(rec)
        if isinstance(validation, dict):
            is_valid = bool(validation.get("is_valid", validation.get("valid", False)))
            errors = validation.get("errors", []) or validation.get("validation_errors", [])
        else:
            is_valid = bool(validation)
            errors = []

        try:
            confidence = score_confidence(rec, validation)
        except TypeError:
            confidence = score_confidence(rec)

        rec["_validation"] = {
            "is_valid": is_valid,
            "errors": errors,
        }
        rec["_confidence"] = confidence

        processed_records.append(rec)
        if not is_valid:
            invalid_records.append({
                "row_number": idx,
                "facility": rec.get("facility"),
                "errors": errors,
                "confidence": confidence,
            })

    
    summary = run_intake_records(
        records=processed_records,
        source=source,
        intake_root=intake_root,
        facility=facility,
    )

    # keep upload response contract stable
    summary["status"] = "processed"
    summary["source"] = source
    summary["file_name"] = csv_path.name
    summary["stored_at"] = str(csv_path)
    summary["event_log"] = str(Path(intake_root) / "logs" / "intake_events.jsonl")

    return summary

