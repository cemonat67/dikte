import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agents.intake_agent.src.normalize import build_record_from_row


def parse_whatsapp_to_record(payload: dict) -> dict:
    row = {
        "facility": payload.get("facility", ""),
        "water_m3": payload.get("water_m3"),
        "energy_kwh": payload.get("energy_kwh"),
        "natural_gas_m3": payload.get("natural_gas_m3"),
        "production_kg": payload.get("production_kg"),
    }

    record = build_record_from_row(
        row=row,
        source_name="whatsapp_form",
        source_type="whatsapp",
        row_index=1,
    )

    record["evidence"]["raw_text_excerpt"] = json.dumps(payload, ensure_ascii=False)
    record["meta"]["uploader"] = "whatsapp_operator"

    return record
