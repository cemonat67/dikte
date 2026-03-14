import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
EVENT_LOG_FILE = LOG_DIR / "intake_events.jsonl"


def append_event(
    *,
    event_type: str,
    source: str,
    source_hash: str,
    status: str,
    archive_path: Optional[str] = None,
    normalized_path: Optional[str] = None,
    review_path: Optional[str] = None,
    rejected_path: Optional[str] = None,
    ingestion_path: Optional[str] = None,
    confidence_score: Optional[float] = None,
    validation_errors: Optional[list] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "source": source,
        "source_hash": source_hash,
        "status": status,
        "archive_path": archive_path,
        "normalized_path": normalized_path,
        "review_path": review_path,
        "rejected_path": rejected_path,
        "ingestion_path": ingestion_path,
        "confidence_score": confidence_score,
        "validation_errors": validation_errors or [],
        "extra": extra or {},
    }

    with EVENT_LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
