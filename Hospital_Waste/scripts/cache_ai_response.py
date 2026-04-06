from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "cache"
CACHE_FILE = CACHE_DIR / "ai_cache.json"

def make_key(prompt: str, payload: dict) -> str:
    raw = json.dumps(
        {"prompt": prompt.strip(), "payload": payload},
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def load_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    return json.loads(CACHE_FILE.read_text(encoding="utf-8"))

def save_cache(cache: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

def get_cached(prompt: str, payload: dict) -> str | None:
    cache = load_cache()
    key = make_key(prompt, payload)
    return cache.get(key)

def put_cached(prompt: str, payload: dict, response: str) -> str:
    cache = load_cache()
    key = make_key(prompt, payload)
    cache[key] = response
    save_cache(cache)
    return key

def main() -> None:
    sample_prompt = "Give a 2-line CFO summary."
    sample_payload = {
        "facility_code": "CIGLI_HOSP",
        "scope2_location_tco2e": 19.698,
        "waste_cost_try": 28245.0
    }

    cached = get_cached(sample_prompt, sample_payload)
    if cached:
        print("CACHE HIT")
        print(cached)
        return

    fake_response = (
        "Çiğli Hastanesi için günlük karbon yükü yüksek görünüyor. "
        "Tıbbi atık maliyeti operasyonel bütçede dikkat gerektiriyor."
    )
    key = put_cached(sample_prompt, sample_payload, fake_response)
    print("CACHE MISS -> STORED")
    print("KEY:", key)
    print(fake_response)

if __name__ == "__main__":
    main()
