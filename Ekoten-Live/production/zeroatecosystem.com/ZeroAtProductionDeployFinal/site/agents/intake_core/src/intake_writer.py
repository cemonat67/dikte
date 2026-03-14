from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from typing import Any, Iterable

import psycopg
from psycopg.rows import dict_row
from agents.intake_core.src.fingerprint import finalize_event


BLOCKING_VALIDATION_ERRORS = {
    "unknown_facility",
    "unknown_metric_type",
    "unknown_process_line",
}


@dataclass
class IntakeWriteResult:
    status: str
    reason: str
    event_id: str | None = None
    fingerprint: str | None = None
    idempotency_key: str | None = None

    def to_dict(self):
        return asdict(self)


class IntakeWriter:

    def __init__(self, db_url: str | None = None):
        self.db_url = db_url or os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL not set")

    def write_event(self, event: Any) -> IntakeWriteResult:
        payload = self._event_to_dict(event)

        event_id = payload.get("event_id")
        facility_id = payload.get("facility_id")
        source_type = payload.get("source_type")
        metric_type = payload.get("metric_type")
        value = payload.get("value")
        unit = payload.get("unit")
        event_timestamp = payload.get("event_timestamp")
        fingerprint = payload.get("fingerprint")
        idempotency_key = payload.get("idempotency_key")
        source_event_id = payload.get("source_event_id")
        validation_errors = payload.get("validation_errors") or []

        reject_reason = self._reject_reason(
            facility_id=facility_id,
            metric_type=metric_type,
            value=value,
            unit=unit,
            event_timestamp=event_timestamp,
            fingerprint=fingerprint,
            idempotency_key=idempotency_key,
            validation_errors=validation_errors,
        )
        if reject_reason:
            return IntakeWriteResult(
                status="rejected",
                reason=reject_reason,
                event_id=event_id,
                fingerprint=fingerprint,
                idempotency_key=idempotency_key,
            )

        with psycopg.connect(self.db_url, row_factory=dict_row) as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    select id
                    from public.ingestion_dedup
                    where idempotency_key = %(idempotency_key)s
                    """,
                    {"idempotency_key": idempotency_key},
                )

                if cur.fetchone():
                    cur.execute(
                        """
                        update public.ingestion_dedup
                           set seen_count = seen_count + 1,
                               last_seen_at = now()
                         where idempotency_key = %(idempotency_key)s
                        """,
                        {"idempotency_key": idempotency_key},
                    )
                    conn.commit()

                    return IntakeWriteResult(
                        status="duplicate",
                        reason="idempotency_key_exists",
                        event_id=event_id,
                        fingerprint=fingerprint,
                        idempotency_key=idempotency_key,
                    )

                cur.execute(
                    """
                    insert into public.canonical_events (
                        event_id,
                        facility_id,
                        source_type,
                        metric_type,
                        value,
                        unit,
                        event_timestamp,
                        fingerprint,
                        idempotency_key
                    )
                    values (
                        %(event_id)s,
                        %(facility_id)s,
                        %(source_type)s,
                        %(metric_type)s,
                        %(value)s,
                        %(unit)s,
                        %(event_timestamp)s,
                        %(fingerprint)s,
                        %(idempotency_key)s
                    )
                    on conflict (fingerprint) do nothing
                    returning event_id
                    """,
                    payload,
                )

                inserted = cur.fetchone()

                if not inserted:
                    return IntakeWriteResult(
                        status="duplicate",
                        reason="fingerprint_exists",
                        event_id=event_id,
                        fingerprint=fingerprint,
                        idempotency_key=idempotency_key,
                    )

                cur.execute(
                    """
                    insert into public.ingestion_dedup (
                        fingerprint,
                        idempotency_key,
                        source_type,
                        facility_id,
                        first_seen_at,
                        last_seen_at,
                        seen_count,
                        last_event_timestamp,
                        source_event_id
                    )
                    values (
                        %(fingerprint)s,
                        %(idempotency_key)s,
                        %(source_type)s,
                        %(facility_id)s,
                        now(),
                        now(),
                        1,
                        %(event_timestamp)s,
                        %(source_event_id)s
                    )
                    """,
                    payload,
                )

            conn.commit()

        return IntakeWriteResult(
            status="inserted",
            reason="inserted",
            event_id=event_id,
            fingerprint=fingerprint,
            idempotency_key=idempotency_key,
        )

    def write_many(self, events: Iterable[Any]):
        results = []
        for e in events:
            e = finalize_event(e)
            results.append(self.write_event(e).to_dict())
        return results

    @staticmethod
    def _event_to_dict(event: Any):
        if hasattr(event, "__dataclass_fields__"):
            return asdict(event)
        if isinstance(event, dict):
            return event
        raise TypeError("Unsupported event type")

    @staticmethod
    def _is_blank(value: Any) -> bool:
        return value is None or (isinstance(value, str) and value.strip() == "")

    def _reject_reason(
        self,
        *,
        facility_id: Any,
        metric_type: Any,
        value: Any,
        unit: Any,
        event_timestamp: Any,
        fingerprint: Any,
        idempotency_key: Any,
        validation_errors: list[str],
    ) -> str | None:
        if self._is_blank(facility_id):
            return "missing_facility_id"
        if self._is_blank(metric_type):
            return "missing_metric_type"
        if value is None:
            return "missing_value"
        if self._is_blank(unit):
            return "missing_unit"
        if self._is_blank(event_timestamp):
            return "missing_event_timestamp"
        if self._is_blank(fingerprint):
            return "missing_fingerprint"
        if self._is_blank(idempotency_key):
            return "missing_idempotency_key"

        blocking = sorted(set(validation_errors) & BLOCKING_VALIDATION_ERRORS)
        if blocking:
            return f"validation_block:{','.join(blocking)}"

        return None
