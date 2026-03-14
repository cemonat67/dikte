import json
import time
from pathlib import Path

from sap_event_generator import load_config, SapEventGenerator
from sap_api_sender import post_event, post_events
from sap_csv_writer import write_events_to_csv

BASE_DIR = Path(__file__).resolve().parent
STATUS_PATH = BASE_DIR.parent / "runtime" / "latest_status.json"
STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)


def _deliver_api(events: list[dict]) -> dict:
    if len(events) == 1:
        return post_event(events[0])
    return post_events(events)


def run():
    config = load_config()
    interval_seconds = int(config.get("interval_seconds", 10))
    mode = str(config.get("mode", "api")).strip().lower()
    burst_size = int(config.get("burst_size", 1))

    generator = SapEventGenerator(config)

    print(f"START: SAP mock feeder running every {interval_seconds} seconds")
    print(f"MODE : {mode}")
    print(f"BURST: {burst_size}")
    print(f"API  : {config.get('api_endpoint')}")
    print("Press CTRL+C to stop.\n")

    counter = 0

    try:
        while True:
            counter += 1
            events = generator.generate_events(burst_size)

            api_result = None
            csv_result = None

            if mode in ("api", "both"):
                api_result = _deliver_api(events)

            if mode in ("csv", "both"):
                csv_result = write_events_to_csv(events)

            first = events[0]
            summary = {
                "seq": counter,
                "mode": mode,
                "burst_size": burst_size,
                "event_count": len(events),
                "order_id": first.get("order_id"),
                "batch_id": first.get("batch_id"),
                "process_line": first.get("process_line"),
                "asset_id": first.get("asset_id"),
                "api_ok": api_result["ok"] if api_result else None,
                "api_status_code": api_result["status_code"] if api_result else None,
                "csv_ok": csv_result["ok"] if csv_result else None,
                "csv_rows_written": csv_result["rows_written"] if csv_result else None,
            }

            STATUS_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(summary, ensure_ascii=False))
            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\nSTOP: SAP mock feeder stopped by user.")


if __name__ == "__main__":
    run()
