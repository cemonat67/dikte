from __future__ import annotations

import json
import os
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from dotenv import load_dotenv
from supabase import create_client, Client


BASE_DIR = Path(__file__).resolve().parents[1]
INGESTION_DIR = BASE_DIR / "ingestion"
PENDING_DIR = INGESTION_DIR / "pending"
SENT_DIR = INGESTION_DIR / "sent"
FAILED_DIR = INGESTION_DIR / "failed"
LOGS_DIR = BASE_DIR / "logs"
EVENT_LOG = LOGS_DIR / "intake_events.jsonl"

TABLE_NAME = "intake_staging"


@dataclass
class WorkerResult:
    file_path: Path
    success: bool
    message: str
    target_path: Path | None = None


class DuplicateIngestionError(Exception):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> None:
    for p in [PENDING_DIR, SENT_DIR, FAILED_DIR, LOGS_DIR]:
        p.mkdir(parents=True, exist_ok=True)


def append_event(event_type: str, payload: Dict[str, Any]) -> None:
    EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": now_iso(),
        "event_type": event_type,
        **payload,
    }
    with EVENT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_env() -> Tuple[str, str]:
    load_dotenv(BASE_DIR / ".env")
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "").strip()

    if not url or not key:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY in agents/intake_agent/.env")

    if "YOUR_PROJECT" in url or "YOUR_SUPABASE" in key:
        raise RuntimeError("Placeholder Supabase credentials detected in .env")

    return url, key


def get_supabase() -> Client:
    url, key = load_env()
    return create_client(url, key)


def list_pending_files() -> List[Path]:
    return sorted(PENDING_DIR.glob("*.ingestion.json"))


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except Exception:
            return raw

    return raw


def move_file(src: Path, dst_dir: Path) -> Path:
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    return Path(shutil.move(str(src), str(dst)))


def as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def build_row(doc: Any, file_path: Path) -> Dict[str, Any]:
    if not isinstance(doc, dict):
        raise ValueError(f"Unsupported ingestion doc type: {type(doc).__name__}")

    normalized = as_dict(doc.get("normalized_record"))

    if normalized:
        counts = as_dict(normalized.get("counts"))
        accepted_records = normalized.get("accepted_records")
        if not isinstance(accepted_records, list):
            accepted_records = []

        batch_id = safe_str(normalized.get("batch_id"))
        source_type = safe_str(normalized.get("source"))
        source_name = safe_str(normalized.get("input_name")) or file_path.name
        source_hash = safe_str(normalized.get("source_hash"))
        record_count = counts.get("accepted_records", len(accepted_records))
        ingestion_key = file_path.stem

        payload = {
            "ingestion_meta": {
                "ingested_at": doc.get("ingested_at"),
                "status": doc.get("status"),
                "raw_archive_path": doc.get("raw_archive_path"),
                "confidence_score": doc.get("confidence_score"),
                "validation_errors": doc.get("validation_errors", []),
            },
            "normalized_record": normalized,
        }

        return {
            "ingestion_key": ingestion_key,
            "batch_id": batch_id,
            "source_type": source_type,
            "source_name": source_name,
            "source_hash": source_hash,
            "record_count": int(record_count),
            "status": "pending",
            "payload": payload,
        }

    source_value = doc.get("source")
    source_type = source_value if isinstance(source_value, str) else ""

    payload = doc

    return {
        "ingestion_key": file_path.stem,
        "batch_id": "",
        "source_type": safe_str(source_type),
        "source_name": file_path.name,
        "source_hash": safe_str(doc.get("source_hash")),
        "record_count": 1,
        "status": "pending",
        "payload": payload,
    }


def insert_row(client: Client, row: Dict[str, Any]) -> None:
    try:
        client.table(TABLE_NAME).insert(row).execute()
    except Exception as e:
        msg = str(e).lower()
        duplicate_markers = [
            "duplicate key",
            "unique constraint",
            "violates unique constraint",
        ]
        if any(m in msg for m in duplicate_markers):
            raise DuplicateIngestionError(str(e))
        raise


def process_file(client: Client, file_path: Path) -> WorkerResult:
    try:
        doc = read_json(file_path)
        row = build_row(doc, file_path)

        append_event("sender_worker_started", {
            "file": file_path.name,
            "ingestion_key": row["ingestion_key"],
            "batch_id": row["batch_id"],
            "source_type": row["source_type"],
        })

        try:
            insert_row(client, row)

            sent_path = move_file(file_path, SENT_DIR)

            append_event("sender_worker_sent", {
                "file": file_path.name,
                "moved_to": str(sent_path),
                "ingestion_key": row["ingestion_key"],
                "batch_id": row["batch_id"],
                "record_count": row["record_count"],
                "table": TABLE_NAME,
            })

            return WorkerResult(
                file_path=file_path,
                success=True,
                message="inserted",
                target_path=sent_path,
            )

        except DuplicateIngestionError as e:
            sent_path = move_file(file_path, SENT_DIR)

            append_event("sender_worker_duplicate_already_sent", {
                "file": file_path.name,
                "moved_to": str(sent_path),
                "ingestion_key": row["ingestion_key"],
                "batch_id": row["batch_id"],
                "reason": str(e),
                "table": TABLE_NAME,
            })

            return WorkerResult(
                file_path=file_path,
                success=True,
                message="duplicate_already_sent",
                target_path=sent_path,
            )

    except Exception as e:
        failed_path = move_file(file_path, FAILED_DIR)

        append_event("sender_worker_failed", {
            "file": file_path.name,
            "moved_to": str(failed_path),
            "error": str(e),
        })

        return WorkerResult(
            file_path=file_path,
            success=False,
            message=str(e),
            target_path=failed_path,
        )


def run_once() -> int:
    ensure_dirs()
    client = get_supabase()
    files = list_pending_files()

    if not files:
        print("No pending ingestion files found.")
        append_event("sender_worker_noop", {"message": "no pending files"})
        return 0

    ok = 0
    fail = 0

    print(f"Found {len(files)} pending ingestion file(s).")

    for file_path in files:
        result = process_file(client, file_path)
        status = "OK" if result.success else "FAIL"
        print(f"{status}: {file_path.name} -> {result.message}")
        if result.success:
            ok += 1
        else:
            fail += 1

    print("")
    print(f"TOTAL: {len(files)}")
    print(f"SENT: {ok}")
    print(f"FAILED: {fail}")

    append_event("sender_worker_completed", {
        "total": len(files),
        "sent": ok,
        "failed": fail,
    })

    return 1 if fail > 0 else 0


if __name__ == "__main__":
    sys.exit(run_once())
