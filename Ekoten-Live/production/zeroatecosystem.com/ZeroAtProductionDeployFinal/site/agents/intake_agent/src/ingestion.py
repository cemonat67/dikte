import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional


BASE_DIR = Path(__file__).resolve().parent.parent
INGESTION_PENDING_DIR = BASE_DIR / "ingestion" / "pending"


def build_ingestion_envelope(
    *,
    source: str,
    source_hash: str,
    status: str,
    raw_archive_path: str,
    normalized_record: Optional[Dict[str, Any]],
    confidence_score: Optional[float],
    validation_errors: Optional[list],
) -> Dict[str, Any]:
    return {
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "source_hash": source_hash,
        "status": status,
        "raw_archive_path": raw_archive_path,
        "confidence_score": confidence_score,
        "validation_errors": validation_errors or [],
        "normalized_record": normalized_record,
    }


def write_ingestion_pending(
    *,
    source: str,
    source_hash: str,
    envelope: Dict[str, Any],
) -> Path:
    INGESTION_PENDING_DIR.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = INGESTION_PENDING_DIR / f"{source}_{ts}_{source_hash[:12]}.ingestion.json"
    path.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
