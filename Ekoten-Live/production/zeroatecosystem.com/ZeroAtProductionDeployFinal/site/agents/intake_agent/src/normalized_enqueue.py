import json
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parents[1]
NORMALIZED_DIR = BASE_DIR / "normalized"
PENDING_DIR = BASE_DIR / "ingestion" / "pending"

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def ensure_dirs():
    PENDING_DIR.mkdir(parents=True, exist_ok=True)

def coerce_to_unified_shape(normalized, file_path):
    if isinstance(normalized, dict):
        return normalized

    if isinstance(normalized, list):
        batch_id = file_path.stem.replace(".normalized", "")
        return {
            "status": "processed",
            "source": "legacy_normalized",
            "batch_id": batch_id,
            "record_count": len(normalized),
            "valid_count": len(normalized),
            "invalid_count": 0,
            "avg_confidence": None,
            "records": normalized,
            "created_at": now_iso(),
        }

    raise TypeError(f"Unsupported normalized payload type: {type(normalized).__name__}")

def build_ingestion_doc(normalized, file_path):
    normalized = coerce_to_unified_shape(normalized, file_path)

    return {
        "ingested_at": now_iso(),
        "source": normalized.get("source"),
        "source_hash": None,
        "status": "completed",
        "raw_archive_path": None,
        "confidence_score": normalized.get("avg_confidence"),
        "validation_errors": [],
        "normalized_record": {
            "batch_id": normalized.get("batch_id"),
            "input_name": file_path.name,
            "source": normalized.get("source"),
            "counts": {
                "total_records": normalized.get("record_count"),
                "accepted_records": normalized.get("valid_count"),
                "rejected_records": normalized.get("invalid_count"),
                "total_validation_errors": 0
            },
            "accepted_records": normalized.get("records"),
            "rejected_records": []
        }
    }

def run():
    ensure_dirs()
    files = sorted(NORMALIZED_DIR.glob("*.normalized.json"))

    if not files:
        print("No normalized files found.")
        return

    ok = 0
    skip = 0

    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fp:
                normalized = json.load(fp)

            ingestion_doc = build_ingestion_doc(normalized, f)
            out_name = f.stem + ".ingestion.json"
            out_path = PENDING_DIR / out_name

            with open(out_path, "w", encoding="utf-8") as out:
                json.dump(ingestion_doc, out, ensure_ascii=False, indent=2)

            print("ENQUEUED:", out_name)
            ok += 1

        except Exception as e:
            print("SKIPPED:", f.name, "->", str(e))
            skip += 1

    print("")
    print(f"TOTAL: {len(files)}")
    print(f"ENQUEUED: {ok}")
    print(f"SKIPPED: {skip}")

if __name__ == "__main__":
    run()
