import csv
import json
from pathlib import Path
from .config import NORMALIZED_DIR, REVIEW_DIR

def ensure_dirs():
    NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)

def write_normalized_json(records: list[dict], base_name: str) -> Path:
    ensure_dirs()
    out_path = NORMALIZED_DIR / f"{base_name}.normalized.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    return out_path

def flatten_record(record: dict) -> dict:
    return {
        "source_id": record["meta"]["source_id"],
        "source_type": record["meta"]["source_type"],
        "source_name": record["meta"]["source_name"],
        "source_hash": record["meta"].get("source_hash", ""),
        "record_fingerprint": record["meta"].get("record_fingerprint", ""),
        "facility": record["meta"]["facility"],
        "period_start": record["meta"].get("period_start", ""),
        "period_end": record["meta"].get("period_end", ""),
        "review_status": record["meta"]["review_status"],
        "confidence_score": record["meta"]["confidence_score"],
        "water_m3": record["metrics"]["water_m3"],
        "energy_kwh": record["metrics"]["energy_kwh"],
        "natural_gas_m3": record["metrics"]["natural_gas_m3"],
        "steam_ton": record["metrics"]["steam_ton"],
        "co2_kg": record["metrics"]["co2_kg"],
        "wastewater_m3": record["metrics"]["wastewater_m3"],
        "waste_kg": record["metrics"]["waste_kg"],
        "production_kg": record["metrics"]["production_kg"],
        "cod_mg_l": record["wastewater_quality"]["cod_mg_l"],
        "bod_mg_l": record["wastewater_quality"]["bod_mg_l"],
        "tss_mg_l": record["wastewater_quality"]["tss_mg_l"],
        "ph": record["wastewater_quality"]["ph"],
        "energy_cost_try": record["financial_overlay"]["energy_cost_try"],
        "water_cost_try": record["financial_overlay"]["water_cost_try"],
        "wastewater_cost_try": record["financial_overlay"]["wastewater_cost_try"],
        "carbon_cost_try": record["financial_overlay"]["carbon_cost_try"],
        "estimated_total_cost_try": record["financial_overlay"]["estimated_total_cost_try"],
    }

def write_flat_csv(records: list[dict], base_name: str) -> Path:
    ensure_dirs()
    out_path = NORMALIZED_DIR / f"{base_name}.flat.csv"
    flat_rows = [flatten_record(r) for r in records]

    if not flat_rows:
        raise ValueError("No rows to write")

    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(flat_rows[0].keys()))
        writer.writeheader()
        writer.writerows(flat_rows)

    return out_path

def write_review_manifest(records: list[dict], base_name: str) -> Path:
    ensure_dirs()
    out_path = REVIEW_DIR / f"{base_name}.review.json"
    payload = {
        "review_id": f"{base_name}-review",
        "normalized_file": f"{base_name}.normalized.json",
        "flat_csv_file": f"{base_name}.flat.csv",
        "record_count": len(records),
        "review_status": "in_review",
        "review_checks": {
            "source_identity_confirmed": False,
            "facility_confirmed": False,
            "period_confirmed": False,
            "units_checked": False,
            "duplicates_checked": False
        },
        "reviewer": "",
        "notes": ""
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return out_path
