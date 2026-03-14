from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple

from agents.intake_core.src.canonical_event import CanonicalEvent
from agents.intake_core.src.fingerprint import build_fingerprint, build_idempotency_key
from agents.intake_core.src.intake_writer import IntakeWriter
from agents.intake_core.src.metric_registry import MetricRegistry
from agents.intake_core.src.facility_registry import FacilityRegistry


ALLOWED_METRICS = {
    "water_m3",
    "energy_kwh",
    "natural_gas_m3",
    "steam_ton",
    "co2_kg",
    "wastewater_m3",
    "production_kg",
    "cod_mg_l",
    "bod_mg_l",
    "tss_mg_l",
    "ph",
}

ZERO_FILL_ALLOWED = {
    "water_m3",
    "energy_kwh",
    "natural_gas_m3",
    "steam_ton",
    "co2_kg",
    "wastewater_m3",
    "production_kg",
    "cod_mg_l",
    "bod_mg_l",
    "tss_mg_l",
}

DEFAULT_SCHEMA_VERSION = "1.0"
DEFAULT_SOURCE_TYPE = "csv"
DEFAULT_CONFIDENCE_SCORE = 1.0
DEFAULT_TRUST_LEVEL = "high"


@dataclass
class CommitResult:
    inserted: int = 0
    duplicate: int = 0
    rejected: int = 0
    zero_filled_fields: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    rejected_rows: List[Dict[str, Any]] = field(default_factory=list)
    total_input_rows: int = 0
    total_expanded_events: int = 0


class RowRejected(Exception):
    def __init__(self, field: str, code: str, message: str) -> None:
        super().__init__(message)
        self.field = field
        self.code = code
        self.message = message


class CommitService:
    def __init__(
        self,
        intake_writer: IntakeWriter,
        metric_registry: MetricRegistry,
        facility_registry: FacilityRegistry,
    ) -> None:
        self.intake_writer = intake_writer
        self.metric_registry = metric_registry
        self.facility_registry = facility_registry

    def commit_csv_bytes(
        self,
        file_bytes: bytes,
        file_name: str,
        zero_fill_missing: bool = False,
    ) -> CommitResult:
        text = file_bytes.decode("utf-8-sig", errors="replace")
        reader = csv.DictReader(io.StringIO(text))

        rows = list(reader)
        result = CommitResult(total_input_rows=len(rows))
        all_events: List[CanonicalEvent] = []

        for row_index, raw_row in enumerate(rows, start=1):
            normalized_row = self._normalize_row_keys(raw_row)

            try:
                row_events, row_zero_fills, row_warnings = self._expand_row_to_events(
                    row=normalized_row,
                    row_index=row_index,
                    file_name=file_name,
                    zero_fill_missing=zero_fill_missing,
                )
                all_events.extend(row_events)
                result.zero_filled_fields.extend(row_zero_fills)
                result.warnings.extend(row_warnings)
            except RowRejected as exc:
                result.rejected += 1
                result.rejected_rows.append(
                    {
                        "row_index": row_index,
                        "field": exc.field,
                        "code": exc.code,
                        "message": exc.message,
                    }
                )

        result.total_expanded_events = len(all_events)

        if all_events:
            write_results = self.intake_writer.write_many(all_events)

            for item in write_results:
                status = item.get("status")
                if status == "inserted":
                    result.inserted += 1
                elif status == "duplicate":
                    result.duplicate += 1
                elif status == "rejected":
                    result.rejected += 1

        return result

    def _expand_row_to_events(
        self,
        row: Dict[str, Any],
        row_index: int,
        file_name: str,
        zero_fill_missing: bool,
    ) -> Tuple[List[CanonicalEvent], List[Dict[str, Any]], List[Dict[str, Any]]]:
        zero_filled_fields: List[Dict[str, Any]] = []
        warnings: List[Dict[str, Any]] = []

        facility_raw = self._clean_str(row.get("facility"))
        if not facility_raw:
            raise RowRejected("facility", "missing_required", "facility is required")

        facility_id = self._resolve_facility_id(facility_raw)

        event_timestamp = self._resolve_event_timestamp(row.get("event_timestamp"))
        if event_timestamp is None:
            event_timestamp = datetime.now(timezone.utc)
            warnings.append(
                {
                    "row_index": row_index,
                    "field": "event_timestamp",
                    "code": "fallback_now",
                    "message": "event_timestamp missing → fallback to server time",
                }
            )

        process_line = self._clean_str(row.get("process_line"))
        batch_id = self._clean_str(row.get("batch_id"))
        order_id = self._clean_str(row.get("order_id"))
        asset_id = self._clean_str(row.get("asset_id"))

        source_event_id = None

        events: List[CanonicalEvent] = []

        for metric_type in sorted(ALLOWED_METRICS):
            source_event_id = self._build_source_event_id(
                file_name=file_name,
                row_index=row_index,
                metric_type=metric_type,
            )
            raw_value = row.get(metric_type)

            if self._is_blank(raw_value):
                if metric_type in ZERO_FILL_ALLOWED and zero_fill_missing:
                    value = Decimal("0")
                    zero_filled_fields.append(
                        {
                            "row_index": row_index,
                            "field": metric_type,
                            "value": "0",
                        }
                    )
                    warnings.append(
                        {
                            "row_index": row_index,
                            "field": metric_type,
                            "code": "zero_filled",
                            "message": f"{metric_type} was missing and filled with 0",
                        }
                    )
                else:
                    continue
            else:
                value = self._to_decimal(raw_value, metric_type)

            if metric_type == "ph" and value == 0:
                raise RowRejected(
                    "ph",
                    "invalid_zero_value",
                    "ph cannot be zero-filled or committed as 0",
                )

            metric_def = self.metric_registry.get_metric_definition(metric_type)
            if not metric_def:
                raise RowRejected(
                    metric_type,
                    "metric_not_registered",
                    f"metric {metric_type} not registered in metric_definitions",
                )

            unit = metric_def["canonical_unit"]

            source_metadata = {
                "file_name": file_name,
                "row_index": row_index,
                "source_format": "wide_row_csv",
                "original_facility": facility_raw,
            }

            event = CanonicalEvent(
                facility_id=facility_id,
                source_type=DEFAULT_SOURCE_TYPE,
                metric_type=metric_type,
                value=value,
                unit=unit,
                event_timestamp=event_timestamp,
                process_line=process_line,
                batch_id=batch_id,
                order_id=order_id,
                asset_id=asset_id,
                confidence_score=DEFAULT_CONFIDENCE_SCORE,
                trust_level=DEFAULT_TRUST_LEVEL,
                source_event_id=source_event_id,
                idempotency_key=None,
                fingerprint=None,
                source_metadata=source_metadata,
                validation_errors=[],
                event_id=None,
                ingested_at=datetime.now(timezone.utc),
                schema_version=DEFAULT_SCHEMA_VERSION,
            )

            fingerprint = build_fingerprint(event)
            event.fingerprint = fingerprint
            event.idempotency_key = build_idempotency_key(event)
            events.append(event)

        if not events:
            raise RowRejected(
                "row",
                "no_metrics_found",
                "row produced zero canonical events",
            )

        return events, zero_filled_fields, warnings

    def _resolve_facility_id(self, facility_raw: str) -> str:
        facility_id = facility_raw.strip().lower()

        facility = self.facility_registry.get_facility(facility_id)
        if facility:
            if isinstance(facility, dict):
                return facility["facility_id"]
            if hasattr(facility, "facility_id"):
                return facility.facility_id

        if hasattr(self.facility_registry, "find_by_name"):
            facility_by_name = self.facility_registry.find_by_name(facility_raw)
            if facility_by_name:
                if isinstance(facility_by_name, dict):
                    return facility_by_name["facility_id"]
                if hasattr(facility_by_name, "facility_id"):
                    return facility_by_name.facility_id

        raise RowRejected(
            "facility",
            "facility_not_found",
            f"facility not found in registry: {facility_raw}",
        )

    def _resolve_event_timestamp(self, raw_value: Any) -> Optional[datetime]:
        if self._is_blank(raw_value):
            return None

        text = str(raw_value).strip()

        try:
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            raise RowRejected(
                "event_timestamp",
                "invalid_timestamp",
                f"invalid event_timestamp: {text}",
            )

    def _build_source_event_id(self, file_name: str, row_index: int, metric_type: str) -> str:
        return f"{file_name}:row:{row_index}:{metric_type}"

    def _normalize_row_keys(self, row: Dict[str, Any]) -> Dict[str, Any]:
        normalized: Dict[str, Any] = {}
        for k, v in row.items():
            key = (k or "").strip()
            normalized[key] = v
        return normalized

    def _to_decimal(self, value: Any, field_name: str) -> Decimal:
        text = str(value).strip().replace(",", ".")
        try:
            return Decimal(text)
        except (InvalidOperation, ValueError):
            raise RowRejected(
                field_name,
                "invalid_numeric",
                f"invalid numeric value for {field_name}: {value}",
            )

    def _clean_str(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _is_blank(self, value: Any) -> bool:
        return value is None or str(value).strip() == ""
