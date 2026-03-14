from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class CanonicalEvent:
    """
    Unified industrial sustainability event model.

    This object is the single canonical contract used by all adapters
    before data enters the ingestion queue.
    """

    facility_id: str
    source_type: str
    metric_type: str
    value: float
    unit: str
    event_timestamp: str

    process_line: Optional[str] = None
    batch_id: Optional[str] = None
    order_id: Optional[str] = None
    asset_id: Optional[str] = None

    confidence_score: float = 1.0
    trust_level: str = "medium"

    source_event_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    fingerprint: Optional[str] = None

    source_metadata: Dict[str, Any] = field(default_factory=dict)
    validation_errors: list[str] = field(default_factory=list)

    event_id: str = field(default_factory=lambda: str(uuid4()))
    ingested_at: str = field(default_factory=utc_now_iso)
    schema_version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def is_valid(self) -> bool:
        required_string_fields = [
            self.facility_id,
            self.source_type,
            self.metric_type,
            self.unit,
            self.event_timestamp,
        ]
        if any(not str(v).strip() for v in required_string_fields):
            return False

        if not isinstance(self.value, (int, float)):
            return False

        if not (0.0 <= float(self.confidence_score) <= 1.0):
            return False

        return True

    def add_error(self, message: str) -> None:
        self.validation_errors.append(message)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "CanonicalEvent":
        return cls(
            facility_id=str(payload.get("facility_id", "")).strip(),
            source_type=str(payload.get("source_type", "")).strip(),
            metric_type=str(payload.get("metric_type", "")).strip(),
            value=float(payload.get("value", 0)),
            unit=str(payload.get("unit", "")).strip(),
            event_timestamp=str(payload.get("event_timestamp", "")).strip(),
            process_line=payload.get("process_line"),
            batch_id=payload.get("batch_id"),
            order_id=payload.get("order_id"),
            asset_id=payload.get("asset_id"),
            confidence_score=float(payload.get("confidence_score", 1.0)),
            trust_level=str(payload.get("trust_level", "medium")).strip(),
            source_event_id=payload.get("source_event_id"),
            idempotency_key=payload.get("idempotency_key"),
            fingerprint=payload.get("fingerprint"),
            source_metadata=payload.get("source_metadata", {}) or {},
            validation_errors=payload.get("validation_errors", []) or [],
            event_id=payload.get("event_id", str(uuid4())),
            ingested_at=payload.get("ingested_at", utc_now_iso()),
            schema_version=str(payload.get("schema_version", "1.0")),
        )
