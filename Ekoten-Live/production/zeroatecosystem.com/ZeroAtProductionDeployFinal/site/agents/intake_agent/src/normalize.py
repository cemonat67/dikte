from datetime import datetime
from .schema_utils import new_record
from .config import DEFAULT_CONFIDENCE, DEFAULT_FACILITY, DEFAULT_SOURCE_LANGUAGE, PARSER_VERSION
from .utils import coerce_number, coerce_iso_date, fingerprint_record

FIELD_CANDIDATES = {
    "facility": ["facility", "plant", "site", "factory"],
    "period_start": ["period_start", "start_date", "date_start", "from_date"],
    "period_end": ["period_end", "end_date", "date_end", "to_date"],

    "water_m3": ["water_m3", "water", "water consumption", "water consumption m3", "su", "su_m3"],
    "energy_kwh": ["energy_kwh", "energy", "electricity_kwh", "electricity", "enerji", "kwh"],
    "natural_gas_m3": ["natural_gas_m3", "natural gas", "dogalgaz", "gas_m3"],
    "steam_ton": ["steam_ton", "steam", "buhar", "steam ton"],
    "co2_kg": ["co2_kg", "co2", "carbon", "emission", "emissions_kg"],
    "wastewater_m3": ["wastewater_m3", "wastewater", "atiksu", "effluent_m3"],
    "waste_kg": ["waste_kg", "waste", "atik_kg"],
    "production_kg": ["production_kg", "production", "uretim", "kg production"],

    "cod_mg_l": ["cod_mg_l", "cod"],
    "bod_mg_l": ["bod_mg_l", "bod"],
    "tss_mg_l": ["tss_mg_l", "tss"],
    "ph": ["ph", "p_h"],
    "conductivity_us_cm": ["conductivity_us_cm", "conductivity"],
    "temperature_c": ["temperature_c", "temperature", "temp_c"],
    "color_ptco": ["color_ptco", "color"],

    "energy_cost_try": ["energy_cost_try", "energy_cost", "electricity_cost_try"],
    "water_cost_try": ["water_cost_try", "water_cost"],
    "wastewater_cost_try": ["wastewater_cost_try", "wastewater_cost"],
    "carbon_cost_try": ["carbon_cost_try", "carbon_cost"],
    "estimated_total_cost_try": ["estimated_total_cost_try", "total_cost_try", "estimated_total_cost"],
}

NUMERIC_TARGETS = {
    "water_m3", "energy_kwh", "natural_gas_m3", "steam_ton", "co2_kg", "wastewater_m3",
    "waste_kg", "production_kg", "cod_mg_l", "bod_mg_l", "tss_mg_l", "ph",
    "conductivity_us_cm", "temperature_c", "color_ptco",
    "energy_cost_try", "water_cost_try", "wastewater_cost_try", "carbon_cost_try", "estimated_total_cost_try"
}

DATE_TARGETS = {"period_start", "period_end"}

def _norm_key(value: str) -> str:
    return str(value).strip().lower().replace("-", "_").replace(" ", "_")

def _pick_value(row: dict, candidates: list[str]):
    normalized = {_norm_key(k): v for k, v in row.items()}
    for candidate in candidates:
        key = _norm_key(candidate)
        if key in normalized and normalized[key] not in ("", None):
            return normalized[key], key
    return None, None

def build_record_from_row(row: dict, source_name: str, source_type: str, row_index: int) -> dict:
    record = new_record()
    now = datetime.utcnow().isoformat() + "Z"

    facility_value, _ = _pick_value(row, FIELD_CANDIDATES["facility"])
    period_start_value, _ = _pick_value(row, FIELD_CANDIDATES["period_start"])
    period_end_value, _ = _pick_value(row, FIELD_CANDIDATES["period_end"])

    facility = "" if facility_value in (None, "") else str(facility_value).strip()
    period_start = coerce_iso_date(period_start_value)
    period_end = coerce_iso_date(period_end_value)

    record["meta"]["source_id"] = f"{source_name}::row::{row_index}"
    record["meta"]["source_type"] = source_type
    record["meta"]["source_name"] = source_name
    record["meta"]["source_language"] = DEFAULT_SOURCE_LANGUAGE
    record["meta"]["received_at"] = now
    record["meta"]["processed_at"] = now
    record["meta"]["facility"] = facility
    record["meta"]["period_start"] = period_start
    record["meta"]["period_end"] = period_end
    record["meta"]["uploader"] = "local_mvp"
    record["meta"]["review_status"] = "draft"
    record["meta"]["confidence_score"] = DEFAULT_CONFIDENCE
    record["meta"]["parser_version"] = PARSER_VERSION
    record["meta"]["source_hash"] = ""
    record["meta"]["record_fingerprint"] = fingerprint_record(facility, period_start, period_end, source_name, row_index)

    field_map = {}
    transform_notes = []

    for target_field, candidates in FIELD_CANDIDATES.items():
        if target_field in {"facility", "period_start", "period_end"}:
            continue

        value, source_field = _pick_value(row, candidates)
        if value is None:
            continue

        if target_field in NUMERIC_TARGETS:
            coerced = coerce_number(value)
            if coerced is None and str(value).strip() != "":
                transform_notes.append(f"numeric_parse_failed:{target_field}={value}")
            value = coerced

        elif target_field in DATE_TARGETS:
            value = coerce_iso_date(value)

        if target_field in record["metrics"]:
            record["metrics"][target_field] = value
        elif target_field in record["wastewater_quality"]:
            record["wastewater_quality"][target_field] = value
        elif target_field in record["financial_overlay"]:
            record["financial_overlay"][target_field] = value

        if source_field:
            field_map[target_field] = source_field

    record["normalization"]["field_map"] = field_map
    record["normalization"]["transform_notes"] = transform_notes
    record["evidence"]["raw_text_excerpt"] = str(row)[:500]

    return record
