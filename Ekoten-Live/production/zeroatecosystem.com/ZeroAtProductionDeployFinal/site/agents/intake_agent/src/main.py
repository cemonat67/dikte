import sys
import json
import shutil
import argparse
from datetime import datetime, timezone
from pathlib import Path

from .config import ARCHIVE_DIR, REJECTED_DIR
from .tabular_parser import parse_tabular_file
from .text_parser import parse_key_value_text
from .writers import write_normalized_json, write_flat_csv, write_review_manifest
from .utils import file_sha256
from .validate import validate_record, score_confidence
from .event_log import append_event
from .ingestion import build_ingestion_envelope, write_ingestion_pending


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_runtime_dirs():
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    REJECTED_DIR.mkdir(parents=True, exist_ok=True)


def archive_input_file(input_path: Path, batch_id: str) -> Path:
    ensure_runtime_dirs()
    archived_name = f"{batch_id}__{input_path.name}"
    archived_path = ARCHIVE_DIR / archived_name
    shutil.copy2(input_path, archived_path)
    return archived_path


def parse_records(path: Path, source: str):
    if source == "csv":
        return parse_tabular_file(str(path))
    if source == "text":
        return parse_key_value_text(str(path))
    raise ValueError(f"Unsupported source: {source}")


def classify_records(records: list[dict], source_hash: str):
    accepted = []
    rejected = []
    total_errors = 0

    for record in records:
        record["meta"]["source_hash"] = source_hash

        errors = validate_record(record)
        record["review"]["validation_errors"] = errors
        record["meta"]["confidence_score"] = score_confidence(record, errors)

        total_errors += len(errors)

        if errors:
            record["meta"]["review_status"] = "rejected"
            rejected.append(record)
        else:
            record["meta"]["review_status"] = "in_review"
            accepted.append(record)

    return accepted, rejected, total_errors


def write_rejected_json(records: list[dict], base_name: str, batch_id: str) -> Path:
    REJECTED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REJECTED_DIR / f"{base_name}.{batch_id}.rejected.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    return out_path


def write_batch_summary(
    *,
    batch_id: str,
    input_file: Path,
    source: str,
    source_hash: str,
    archive_path: Path,
    normalized_path: Path,
    flat_csv_path: Path,
    review_path: Path,
    rejected_path: Path | None,
    total_records: int,
    accepted_count: int,
    rejected_count: int,
    total_errors: int,
) -> Path:
    summary = {
        "batch_id": batch_id,
        "created_at": utc_now(),
        "input_file": str(input_file),
        "input_name": input_file.name,
        "source": source,
        "source_hash": source_hash,
        "archive_file": str(archive_path),
        "outputs": {
            "normalized_json": str(normalized_path),
            "flat_csv": str(flat_csv_path),
            "review_manifest": str(review_path),
            "rejected_json": str(rejected_path) if rejected_path else ""
        },
        "counts": {
            "total_records": total_records,
            "accepted_records": accepted_count,
            "rejected_records": rejected_count,
            "total_validation_errors": total_errors
        },
        "status": "completed" if accepted_count > 0 else "review_required"
    }

    out_path = ARCHIVE_DIR / f"{input_file.stem}.{batch_id}.summary.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    return out_path


def run(path_str: str, source: str):
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Input not found: {path}")

    batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = path.stem

    source_hash = file_sha256(path)
    archive_path = archive_input_file(path, batch_id)

    records = parse_records(path, source)
    accepted, rejected, total_errors = classify_records(records, source_hash)

    normalized_path = write_normalized_json(accepted, base_name)
    flat_csv_path = write_flat_csv(accepted, base_name) if accepted else None
    review_path = write_review_manifest(accepted, base_name)

    rejected_path = None
    if rejected:
        rejected_path = write_rejected_json(rejected, base_name, batch_id)

    summary_path = write_batch_summary(
        batch_id=batch_id,
        input_file=path,
        source=source,
        source_hash=source_hash,
        archive_path=archive_path,
        normalized_path=normalized_path,
        flat_csv_path=flat_csv_path if flat_csv_path else Path(""),
        review_path=review_path,
        rejected_path=rejected_path,
        total_records=len(records),
        accepted_count=len(accepted),
        rejected_count=len(rejected),
        total_errors=total_errors,
    )

    ingestion_payload = {
        "batch_id": batch_id,
        "input_file": str(path),
        "input_name": path.name,
        "source": source,
        "source_hash": source_hash,
        "archive_file": str(archive_path),
        "summary_file": str(summary_path),
        "counts": {
            "total_records": len(records),
            "accepted_records": len(accepted),
            "rejected_records": len(rejected),
            "total_validation_errors": total_errors
        },
        "accepted_records": accepted,
        "rejected_records": rejected
    }

    ingestion_envelope = build_ingestion_envelope(
        source=source,
        source_hash=source_hash,
        status="completed" if accepted else "review_required",
        raw_archive_path=str(archive_path),
        normalized_record=ingestion_payload,
        confidence_score=None,
        validation_errors=[],
    )

    ingestion_path = write_ingestion_pending(
        source=source,
        source_hash=source_hash,
        envelope=ingestion_envelope,
    )

    append_event(
        event_type="intake_batch_completed",
        source=source,
        source_hash=source_hash,
        status="completed" if accepted else "review_required",
        archive_path=str(archive_path),
        normalized_path=str(normalized_path),
        review_path=str(review_path),
        rejected_path=str(rejected_path) if rejected_path else None,
        ingestion_path=str(ingestion_path),
        confidence_score=None,
        validation_errors=[],
        extra={
            "batch_id": batch_id,
            "input_name": path.name,
            "total_records": len(records),
            "accepted_records": len(accepted),
            "rejected_records": len(rejected),
            "total_validation_errors": total_errors,
            "summary_file": str(summary_path)
        },
    )

    print("OK: intake completed")
    print(f"BATCH   : {batch_id}")
    print(f"ARCHIVE : {archive_path}")
    print(f"JSON    : {normalized_path}")
    print(f"CSV     : {flat_csv_path if flat_csv_path else 'NO_ACCEPTED_ROWS'}")
    print(f"REVIEW  : {review_path}")
    print(f"REJECTED: {rejected_path if rejected_path else 'NONE'}")
    print(f"SUMMARY : {summary_path}")
    print(f"INGEST  : {ingestion_path}")
    print(f"TOTAL   : {len(records)}")
    print(f"ACCEPTED: {len(accepted)}")
    print(f"REJECTED: {len(rejected)}")
    print(f"ERRORS  : {total_errors}")


def build_arg_parser():
    ap = argparse.ArgumentParser(description="Zero@Production Intake Runner")
    ap.add_argument("--input", required=True, help="Input file path")
    ap.add_argument("--source", required=True, choices=["csv", "text"], help="Input source type")
    return ap


if __name__ == "__main__":
    parser = build_arg_parser()
    args = parser.parse_args()
    run(args.input, args.source)
