import json
import urllib.request
import urllib.error
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR.parent / "config" / "feeder_config.json"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)



def _post_json_payload(payload) -> dict:
    config = load_config()
    url = config["api_endpoint"]

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return {
                "ok": True,
                "status_code": resp.status,
                "response_text": body
            }
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {
            "ok": False,
            "status_code": e.code,
            "response_text": body
        }
    except Exception as e:
        return {
            "ok": False,
            "status_code": None,
            "response_text": str(e)
        }


def post_events(events: list[dict]) -> dict:
    if not events:
        return {
            "ok": False,
            "status_code": None,
            "response_text": "No events to post"
        }

    if len(events) == 1:
        return _post_json_payload(events[0])

    payload = {
        "source": "sap_mock_feeder",
        "mode": "burst",
        "event_count": len(events),
        "events": events
    }
    return _post_json_payload(payload)


def post_event(event: dict) -> dict:
    return _post_json_payload(event)


if __name__ == "__main__":
    sample_event = {
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

    result = post_event(sample_event)
    print(json.dumps(result, indent=2))
