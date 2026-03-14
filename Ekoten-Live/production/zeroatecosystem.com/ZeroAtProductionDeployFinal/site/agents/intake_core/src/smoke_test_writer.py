from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

from agents.intake_core.src.adapters.csv_adapter import CSVAdapter
from agents.intake_core.src.intake_writer import IntakeWriter


def load_csv_as_dict_rows(csv_path: str) -> list[dict]:
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def event_to_dict(event):
    if hasattr(event, "__dataclass_fields__"):
        from dataclasses import asdict
        return asdict(event)
    if hasattr(event, "model_dump"):
        return event.model_dump()
    if hasattr(event, "dict"):
        return event.dict()
    if isinstance(event, dict):
        return event
    return {"repr": repr(event)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to input CSV")
    parser.add_argument("--db-url", default=os.getenv("DATABASE_URL"))
    parser.add_argument("--print-events", action="store_true")
    args = parser.parse_args()

    if not args.db_url:
        raise SystemExit("DATABASE_URL is not set")

    csv_path = str(Path(args.csv).expanduser().resolve())
    rows = load_csv_as_dict_rows(csv_path)

    adapter = CSVAdapter()
    events = adapter.parse_and_finalize({"rows": rows, "file_name": Path(csv_path).name, "source_type": "csv"})

    print(f"CSV: {csv_path}")
    print(f"ROW_COUNT  : {len(rows)}")
    print(f"EVENT_COUNT: {len(events)}")

    if args.print_events:
        for i, event in enumerate(events, start=1):
            print(f"\n--- EVENT {i} ---")
            print(json.dumps(event_to_dict(event), indent=2, ensure_ascii=False, default=str))

    writer = IntakeWriter(db_url=args.db_url)
    results = writer.write_many(events)

    inserted = sum(1 for r in results if r["status"] == "inserted")
    duplicate = sum(1 for r in results if r["status"] == "duplicate")
    rejected = sum(1 for r in results if r["status"] == "rejected")

    print("\nWRITE SUMMARY")
    print(f"INSERTED : {inserted}")
    print(f"DUPLICATE: {duplicate}")
    print(f"REJECTED : {rejected}")

    print("\nDETAIL")
    print(json.dumps(results, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
