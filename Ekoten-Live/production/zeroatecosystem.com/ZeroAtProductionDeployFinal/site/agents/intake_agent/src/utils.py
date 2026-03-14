from __future__ import annotations

import hashlib
import re
from datetime import datetime
from pathlib import Path

NUMERIC_FIELDS = {
    "water_m3",
    "energy_kwh",
    "natural_gas_m3",
    "steam_ton",
    "co2_kg",
    "wastewater_m3",
    "waste_kg",
    "production_kg",
    "cod_mg_l",
    "bod_mg_l",
    "tss_mg_l",
    "ph",
    "conductivity_us_cm",
    "temperature_c",
    "color_ptco",
    "energy_cost_try",
    "water_cost_try",
    "wastewater_cost_try",
    "carbon_cost_try",
    "estimated_total_cost_try",
}

DATE_FIELDS = {"period_start", "period_end"}

def file_sha256(path: str | Path) -> str:
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def coerce_number(value):
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return value

    s = str(value).strip()
    if s == "":
        return None

    s = s.replace(" ", "")
    s = re.sub(r"[^0-9,.\-]", "", s)

    if s in {"", "-", ".", ",", "-.", "-,"}:
        return None

    # Case 1: both dot and comma exist
    # Example:
    # 1.234,56 -> EU -> 1234.56
    # 1,234.56 -> US -> 1234.56
    if "." in s and "," in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "")
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")

    # Case 2: only comma exists
    # Decide whether comma is decimal or thousand separator
    elif "," in s:
        parts = s.split(",")
        if len(parts) == 2 and len(parts[1]) in (1, 2):
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")

    # Case 3: only dot exists
    # Decide whether dot is decimal or thousand separator
    elif "." in s:
        parts = s.split(".")
        if len(parts) == 2 and len(parts[1]) in (1, 2):
            pass
        else:
            s = s.replace(".", "")

    try:
        num = float(s)
        return int(num) if num.is_integer() else num
    except ValueError:
        return None

def coerce_iso_date(value):
    if value is None:
        return ""
    s = str(value).strip()
    if not s:
        return ""

    patterns = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%d.%m.%Y",
    ]
    for fmt in patterns:
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            pass
    return ""

def fingerprint_record(facility: str, period_start: str, period_end: str, source_name: str, row_index: int) -> str:
    raw = f"{facility}|{period_start}|{period_end}|{source_name}|{row_index}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
