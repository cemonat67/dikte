import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict


BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = BASE_DIR / "archive" / "raw"


def utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def archive_raw_payload(
    source: str,
    payload: Dict[str, Any],
    source_hash: str
) -> Path:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    ts = utc_now_compact()
    filename = f"{source}_{ts}_{source_hash[:12]}.raw.json"
    path = ARCHIVE_DIR / filename

    envelope = {
        "archived_at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "source_hash": source_hash,
        "payload": payload,
    }

    path.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
