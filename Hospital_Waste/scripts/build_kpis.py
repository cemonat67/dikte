from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SEEDS_DIR = BASE_DIR / "seeds"

INPUT_FILE = SEEDS_DIR / "daily_metrics_mock_mar2026.csv"
OUTPUT_FILE = SEEDS_DIR / "daily_kpis_mock_mar2026.csv"

GRID_EF_TCO2E_PER_MWH = 0.469
MEDICAL_WASTE_TRY_PER_KG = 30.0
PATHOLOGICAL_TRY_PER_KG = 81.0

def read_rows(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def main() -> None:
    rows = read_rows(INPUT_FILE)
    grouped: dict[tuple[str, str], dict[str, float]] = defaultdict(dict)

    for row in rows:
        key = (row["facility_code"], row["metric_date"])
        grouped[key][row["metric_code"]] = float(row["value"])

    out_rows = []
    for (facility_code, metric_date), metrics in sorted(grouped.items()):
        electricity_kwh = metrics.get("electricity_kwh", 0.0)
        medical_waste_kg = metrics.get("medical_waste_kg", 0.0)
        pathological_waste_kg = metrics.get("pathological_waste_kg", 0.0)

        scope2_tco2e = round((electricity_kwh / 1000.0) * GRID_EF_TCO2E_PER_MWH, 4)
        waste_cost_try = round(
            (medical_waste_kg * MEDICAL_WASTE_TRY_PER_KG) +
            (pathological_waste_kg * PATHOLOGICAL_TRY_PER_KG),
            2
        )

        out_rows.append({
            "facility_code": facility_code,
            "metric_date": metric_date,
            "scope2_location_tco2e": scope2_tco2e,
            "waste_cost_try": waste_cost_try,
            "electricity_kwh": round(electricity_kwh, 2),
            "medical_waste_kg": round(medical_waste_kg, 2),
            "pathological_waste_kg": round(pathological_waste_kg, 2),
        })

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"OK: wrote {len(out_rows)} KPI rows to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
