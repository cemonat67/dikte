from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Iterable, List, Optional, Tuple

import psycopg
from psycopg.rows import dict_row


CANONICAL_METRICS = {
    "water_m3": "m3",
    "energy_kwh": "kwh",
    "natural_gas_m3": "m3",
    "steam_ton": "ton",
    "production_kg": "kg",
    "wastewater_m3": "m3",
    "co2_kg": "kg",
    "ph": "ph",
    "cod_mg_l": "mg/L",
    "bod_mg_l": "mg/L",
    "tss_mg_l": "mg/L",
    "chemical_kg": "kg",
}

METRIC_ALIASES = {
    "water_m3": ["water_m3", "water", "water_consumption", "fresh_water_m3"],
    "energy_kwh": ["energy_kwh", "electricity_kwh", "power_kwh", "energy"],
    "natural_gas_m3": ["natural_gas_m3", "gas_m3", "natural_gas", "ng_m3"],
    "steam_ton": ["steam_ton", "steam", "steam_mt", "steam_t"],
    "production_kg": ["production_kg", "production", "output_kg", "qty_kg"],
    "wastewater_m3": ["wastewater_m3", "wastewater", "effluent_m3"],
    "co2_kg": ["co2_kg", "co2", "carbon_kg"],
    "ph": ["ph", "p_h"],
    "cod_mg_l": ["cod_mg_l", "cod"],
    "bod_mg_l": ["bod_mg_l", "bod"],
    "tss_mg_l": ["tss_mg_l", "tss"],
    "chemical_kg": ["chemical_kg", "chemicals_kg", "chemical", "chemicals"],
}


@dataclass
class ProcessorStats:
    claimed: int = 0
    processed: int = 0
    failed: int = 0
    inserted_metrics: int = 0


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")
    return database_url


def log(msg: str) -> None:
    print(msg, flush=True)


def json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def safe_decimal(value: Any) -> Optional[Decimal]:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float, Decimal)):
        try:
            return Decimal(str(value))
        except InvalidOperation:
            return None
    if isinstance(value, str):
        v = value.strip()
        if not v:
            return None
        v = v.replace(" ", "")
        if "," in v and "." in v:
            if v.rfind(",") > v.rfind("."):
                v = v.replace(".", "").replace(",", ".")
            else:
                v = v.replace(",", "")
        else:
            v = v.replace(",", ".")
        try:
            return Decimal(v)
        except InvalidOperation:
            return None
    return None


def parse_metric_date(record: Dict[str, Any]) -> Optional[str]:
    meta = record.get("meta") if isinstance(record.get("meta"), dict) else {}
    candidates = [
        record.get("metric_date"),
        record.get("reading_date"),
        record.get("date"),
        record.get("record_date"),
        record.get("period_date"),
        meta.get("received_at"),
        meta.get("processed_at"),
        meta.get("period_start"),
        meta.get("period_end"),
    ]
    for value in candidates:
        if not value:
            continue
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                continue
            for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%Y/%m/%d"):
                try:
                    return datetime.strptime(raw, fmt).date().isoformat()
                except ValueError:
                    pass
            try:
                return datetime.fromisoformat(raw.replace("Z", "+00:00")).date().isoformat()
            except ValueError:
                pass
    return None


def normalize_facility(record: Dict[str, Any], payload: Dict[str, Any]) -> Optional[str]:
    meta = record.get("meta") if isinstance(record.get("meta"), dict) else {}
    value = (
        record.get("facility")
        or meta.get("facility")
        or record.get("facility_name")
        or record.get("site")
        or record.get("plant")
        or payload.get("facility")
    )
    if value is None:
        return None
    return str(value).strip()


def build_record_fingerprint(record: Dict[str, Any], metric_date: Optional[str], facility: Optional[str]) -> str:
    stable = {
        "facility": facility or "",
        "metric_date": metric_date or "",
        "record": record,
    }
    raw = json.dumps(stable, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_nested_value(record: Dict[str, Any], alias: str) -> Any:
    if alias in record:
        return record.get(alias)

    metrics = record.get("metrics")
    if isinstance(metrics, dict) and alias in metrics:
        return metrics.get(alias)

    wastewater_quality = record.get("wastewater_quality")
    if isinstance(wastewater_quality, dict) and alias in wastewater_quality:
        return wastewater_quality.get(alias)

    meta = record.get("meta")
    if isinstance(meta, dict) and alias in meta:
        return meta.get(alias)

    production_context = record.get("production_context")
    if isinstance(production_context, dict) and alias in production_context:
        return production_context.get(alias)

    return None


def extract_accepted_records(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    candidates = []

    if isinstance(payload.get("accepted_records"), list):
        candidates = payload["accepted_records"]

    normalized_record = payload.get("normalized_record")
    if not candidates and isinstance(normalized_record, dict):
        if isinstance(normalized_record.get("accepted_records"), list):
            candidates = normalized_record["accepted_records"]

    if not candidates and isinstance(payload.get("records"), list):
        candidates = payload["records"]

    return [r for r in candidates if isinstance(r, dict)]


def flatten_metrics(
    record: Dict[str, Any],
    payload: Dict[str, Any],
    ingestion_key: str,
    batch_id: Optional[str],
    staging_id: str,
    source_type: Optional[str],
    source_name: Optional[str],
) -> List[Dict[str, Any]]:
    metric_date = parse_metric_date(record)
    facility = normalize_facility(record, payload)
    record_fingerprint = build_record_fingerprint(record, metric_date, facility)

    rows: List[Dict[str, Any]] = []
    for metric_key, metric_unit in CANONICAL_METRICS.items():
        value = None
        for alias in METRIC_ALIASES.get(metric_key, [metric_key]):
            value = safe_decimal(get_nested_value(record, alias))
            if value is not None:
                break

        if value is None:
            continue

        rows.append(
            {
                "ingestion_key": ingestion_key,
                "batch_id": batch_id,
                "staging_id": staging_id,
                "source_type": source_type,
                "source_name": source_name,
                "facility": facility,
                "metric_date": metric_date,
                "metric_key": metric_key,
                "metric_value": value,
                "metric_unit": metric_unit,
                "record_fingerprint": record_fingerprint,
                "raw_record": json.dumps(record, ensure_ascii=False),
            }
        )
    return rows


def write_event(
    conn: psycopg.Connection,
    staging_id: Optional[str],
    ingestion_key: Optional[str],
    event_type: str,
    event_status: str,
    event_message: str,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into public.intake_processing_events
            (
              staging_id,
              ingestion_key,
              event_type,
              event_status,
              event_message,
              payload
            )
            values (%s, %s, %s, %s, %s, %s::jsonb)
            """,
            (
                staging_id,
                ingestion_key,
                event_type,
                event_status,
                event_message,
                json_dumps(payload or {}),
            ),
        )


def claim_staging_rows(conn: psycopg.Connection, limit: int) -> List[Dict[str, Any]]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            with candidates as (
              select id
              from public.intake_staging
              where processed = false
                and coalesce(processor_status, 'pending') in ('pending', 'failed')
              order by created_at asc
              limit %s
              for update skip locked
            )
            update public.intake_staging s
               set processor_status = 'processing',
                   processing_started_at = now(),
                   processor_error = null
            from candidates c
            where s.id = c.id
            returning
              s.id,
              s.ingestion_key,
              s.batch_id,
              s.source_type,
              s.source_name,
              s.payload
            """,
            (limit,),
        )
        rows = cur.fetchall()
    conn.commit()
    return rows


def insert_metric_rows(conn: psycopg.Connection, metric_rows: List[Dict[str, Any]]) -> int:
    if not metric_rows:
        return 0

    inserted = 0
    with conn.cursor() as cur:
        for row in metric_rows:
            cur.execute(
                """
                insert into public.core_metric_readings
                (
                  ingestion_key,
                  batch_id,
                  staging_id,
                  source_type,
                  source_name,
                  facility,
                  metric_date,
                  metric_key,
                  metric_value,
                  metric_unit,
                  record_fingerprint,
                  raw_record
                )
                values
                (
                  %(ingestion_key)s,
                  %(batch_id)s,
                  %(staging_id)s,
                  %(source_type)s,
                  %(source_name)s,
                  %(facility)s,
                  %(metric_date)s,
                  %(metric_key)s,
                  %(metric_value)s,
                  %(metric_unit)s,
                  %(record_fingerprint)s,
                  %(raw_record)s::jsonb
                )
                on conflict (ingestion_key, record_fingerprint, metric_key, metric_date)
                do nothing
                """,
                row,
            )
            inserted += cur.rowcount
    return inserted


def mark_processed(conn: psycopg.Connection, staging_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            update public.intake_staging
               set processed = true,
                   processed_at = now(),
                   processor_status = 'processed',
                   processor_error = null
             where id = %s
            """,
            (staging_id,),
        )


def mark_failed(conn: psycopg.Connection, staging_id: str, error_text: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            update public.intake_staging
               set processor_status = 'failed',
                   processor_error = left(%s, 2000)
             where id = %s
            """,
            (error_text, staging_id),
        )


def process_one_row(conn: psycopg.Connection, staging_row: Dict[str, Any]) -> Tuple[int, int]:
    staging_id = str(staging_row["id"])
    ingestion_key = staging_row.get("ingestion_key")
    batch_id = staging_row.get("batch_id")
    source_type = staging_row.get("source_type")
    source_name = staging_row.get("source_name")
    payload = staging_row.get("payload") or {}

    if isinstance(payload, str):
        payload = json.loads(payload)

    accepted_records = extract_accepted_records(payload)

    write_event(
        conn,
        staging_id=staging_id,
        ingestion_key=ingestion_key,
        event_type="processor_claimed",
        event_status="ok",
        event_message="Staging row claimed by processor",
        payload={"accepted_record_count": len(accepted_records)},
    )

    if not accepted_records:
        mark_processed(conn, staging_id)
        write_event(
            conn,
            staging_id=staging_id,
            ingestion_key=ingestion_key,
            event_type="processor_processed",
            event_status="ok",
            event_message="No accepted records found; marked processed",
            payload={"inserted_metrics": 0},
        )
        conn.commit()
        return (0, 0)

    metric_rows: List[Dict[str, Any]] = []
    for record in accepted_records:
        metric_rows.extend(
            flatten_metrics(
                record=record,
                payload=payload,
                ingestion_key=ingestion_key,
                batch_id=batch_id,
                staging_id=staging_id,
                source_type=source_type,
                source_name=source_name,
            )
        )

    inserted = insert_metric_rows(conn, metric_rows)
    mark_processed(conn, staging_id)

    write_event(
        conn,
        staging_id=staging_id,
        ingestion_key=ingestion_key,
        event_type="processor_processed",
        event_status="ok",
        event_message="Staging row processed successfully",
        payload={
            "accepted_records": len(accepted_records),
            "flattened_metric_rows": len(metric_rows),
            "inserted_metrics": inserted,
        },
    )
    conn.commit()
    return (len(accepted_records), inserted)


def run_once(limit: int) -> int:
    stats = ProcessorStats()
    database_url = get_database_url()

    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        claimed_rows = claim_staging_rows(conn, limit=limit)
        stats.claimed = len(claimed_rows)

        if not claimed_rows:
            log("TOTAL CLAIMED: 0")
            log("PROCESSED    : 0")
            log("FAILED       : 0")
            log("INSERTED     : 0")
            return 0

        for row in claimed_rows:
            staging_id = str(row["id"])
            ingestion_key = row.get("ingestion_key")
            try:
                _, inserted = process_one_row(conn, row)
                stats.processed += 1
                stats.inserted_metrics += inserted
            except Exception as exc:
                conn.rollback()
                error_text = f"{type(exc).__name__}: {exc}"
                with psycopg.connect(database_url, row_factory=dict_row) as fail_conn:
                    mark_failed(fail_conn, staging_id, error_text)
                    write_event(
                        fail_conn,
                        staging_id=staging_id,
                        ingestion_key=ingestion_key,
                        event_type="processor_failed",
                        event_status="error",
                        event_message="Staging row processing failed",
                        payload={"error": error_text},
                    )
                    fail_conn.commit()
                stats.failed += 1
                log(f"[FAILED] staging_id={staging_id} error={error_text}")

    log(f"TOTAL CLAIMED: {stats.claimed}")
    log(f"PROCESSED    : {stats.processed}")
    log(f"FAILED       : {stats.failed}")
    log(f"INSERTED     : {stats.inserted_metrics}")
    return 0 if stats.failed == 0 else 1


def run_loop(limit: int, interval_seconds: int) -> int:
    while True:
        code = run_once(limit=limit)
        time.sleep(interval_seconds)
        if code not in (0, 1):
            return code


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Zero@Production Staging Processor Worker")
    parser.add_argument("--limit", type=int, default=25, help="Max staging rows to claim per run")
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit")
    parser.add_argument("--interval", type=int, default=20, help="Loop interval seconds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.once:
        return run_once(limit=args.limit)
    return run_loop(limit=args.limit, interval_seconds=args.interval)


if __name__ == "__main__":
    sys.exit(main())
