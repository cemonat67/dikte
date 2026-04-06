from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SEEDS_DIR = BASE_DIR / "seeds"

START_DATE = date(2026, 3, 1)
DAYS = 31

FACILITIES = [
    {
        "facility_code": "CIGLI_HOSP",
        "facility_type": "hospital",
        "electricity_base": 42000,
        "water_base": 380,
        "medical_waste_base": 820,
        "pathological_base": 45,
        "general_waste_base": 4700,
    },
    {
        "facility_code": "SADA_HOSP",
        "facility_type": "hospital",
        "electricity_base": 25500,
        "water_base": 240,
        "medical_waste_base": 420,
        "pathological_base": 22,
        "general_waste_base": 2600,
    },
    {
        "facility_code": "EYE_CENTER",
        "facility_type": "eye_center",
        "electricity_base": 1800,
        "water_base": 22,
        "medical_waste_base": 18,
        "pathological_base": 0,
        "general_waste_base": 240,
    },
    {
        "facility_code": "CIGLI_MED",
        "facility_type": "medical_center",
        "electricity_base": 2400,
        "water_base": 28,
        "medical_waste_base": 25,
        "pathological_base": 0,
        "general_waste_base": 320,
    },
    {
        "facility_code": "DENTAL_CENTER",
        "facility_type": "dental_center",
        "electricity_base": 2100,
        "water_base": 18,
        "medical_waste_base": 22,
        "pathological_base": 0,
        "general_waste_base": 180,
    },
    {
        "facility_code": "BALCOVA_MED",
        "facility_type": "medical_center",
        "electricity_base": 2600,
        "water_base": 30,
        "medical_waste_base": 28,
        "pathological_base": 0,
        "general_waste_base": 350,
    },
]

def vary(base: float, pct: float) -> float:
    low = base * (1 - pct)
    high = base * (1 + pct)
    return round(random.uniform(low, high), 2)

def is_weekend(d: date) -> bool:
    return d.weekday() >= 5

def generate_daily_metrics() -> list[dict]:
    rows = []
    random.seed(42)

    for facility in FACILITIES:
        for i in range(DAYS):
            day = START_DATE + timedelta(days=i)
            weekend_factor = 0.88 if is_weekend(day) else 1.00

            electricity = vary(facility["electricity_base"] * weekend_factor, 0.06)
            water = vary(facility["water_base"] * weekend_factor, 0.08)
            medical_waste = vary(facility["medical_waste_base"] * weekend_factor, 0.07)
            pathological = vary(facility["pathological_base"] * weekend_factor, 0.12) if facility["pathological_base"] else 0
            general_waste = vary(facility["general_waste_base"] * weekend_factor, 0.07)

            rows.extend([
                {
                    "facility_code": facility["facility_code"],
                    "metric_date": day.isoformat(),
                    "metric_code": "electricity_kwh",
                    "value": electricity,
                    "unit_code": "kWh",
                    "quality_flag": "estimated",
                    "calculation_method": "mock_generator_v1",
                    "source_system": "mock",
                },
                {
                    "facility_code": facility["facility_code"],
                    "metric_date": day.isoformat(),
                    "metric_code": "water_m3",
                    "value": water,
                    "unit_code": "m3",
                    "quality_flag": "estimated",
                    "calculation_method": "mock_generator_v1",
                    "source_system": "mock",
                },
                {
                    "facility_code": facility["facility_code"],
                    "metric_date": day.isoformat(),
                    "metric_code": "medical_waste_kg",
                    "value": medical_waste,
                    "unit_code": "kg",
                    "quality_flag": "estimated",
                    "calculation_method": "mock_generator_v1",
                    "source_system": "mock",
                },
                {
                    "facility_code": facility["facility_code"],
                    "metric_date": day.isoformat(),
                    "metric_code": "pathological_waste_kg",
                    "value": pathological,
                    "unit_code": "kg",
                    "quality_flag": "estimated",
                    "calculation_method": "mock_generator_v1",
                    "source_system": "mock",
                },
                {
                    "facility_code": facility["facility_code"],
                    "metric_date": day.isoformat(),
                    "metric_code": "general_waste_kg",
                    "value": general_waste,
                    "unit_code": "kg",
                    "quality_flag": "estimated",
                    "calculation_method": "mock_generator_v1",
                    "source_system": "mock",
                },
            ])
    return rows

def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("No rows to write.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

def main() -> None:
    rows = generate_daily_metrics()
    out = SEEDS_DIR / "daily_metrics_mock_mar2026.csv"
    write_csv(out, rows)
    print(f"OK: wrote {len(rows)} rows to {out}")

if __name__ == "__main__":
    main()
