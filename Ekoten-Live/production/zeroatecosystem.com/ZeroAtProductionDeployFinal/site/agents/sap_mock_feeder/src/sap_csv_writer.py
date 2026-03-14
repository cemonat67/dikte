import csv
import json
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR.parent / "config" / "feeder_config.json"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _resolve_output_path() -> Path:
    config = load_config()
    export_dir = config.get("csv_export_dir", str(BASE_DIR.parent / "exports"))
    export_name = config.get("csv_file_name", f"sap_export_{datetime.now().strftime('%Y%m%d')}.csv")
    out_dir = Path(export_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / export_name


def write_events_to_csv(events: list[dict]) -> dict:
    if not events:
        return {
            "ok": False,
            "path": None,
            "rows_written": 0,
            "message": "No events to write"
        }

    output_path = _resolve_output_path()
    file_exists = output_path.exists()

    fieldnames = list(events[0].keys())

    with open(output_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists or output_path.stat().st_size == 0:
            writer.writeheader()

        writer.writerows(events)

    return {
        "ok": True,
        "path": str(output_path),
        "rows_written": len(events),
        "message": "CSV export completed"
    }


if __name__ == "__main__":
    sample = [
        {
            "facility": "ekoten",
            "order_id": "ORD-TEST-0001",
            "batch_id": "BAT-TEST-0001",
            "process_line": "dyeing",
            "asset_id": "JET01",
            "event_timestamp": "2026-03-13T20:00:00+00:00",
            "production_kg": 500,
            "energy_kwh": 220.5,
            "water_m3": 7.8,
            "natural_gas_m3": 12.4,
            "wastewater_m3": 6.2,
            "cod_mg_l": 800.0,
            "bod_mg_l": 350.0,
            "tss_mg_l": 240.0,
            "ph": 7.2,
            "co2_kg": 145.0
        }
    ]
    result = write_events_to_csv(sample)
    print(json.dumps(result, indent=2))
