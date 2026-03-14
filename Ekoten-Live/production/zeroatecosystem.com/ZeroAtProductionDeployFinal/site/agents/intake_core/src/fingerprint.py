from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Dict

SCHEMA_VERSION = "1.0"
FINGERPRINT_VERSION = "fp_v1"
IDEMPOTENCY_VERSION = "idem_v1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _to_iso_utc(value: Any) -> str | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        text = text.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            return None
    else:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    return dt.replace(microsecond=0).isoformat()


def _normalize_number(value: Any) -> str | None:
    if value is None:
        return None
    try:
        dec = Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError):
        return None

    normalized = format(dec.normalize(), "f")
    if "." in normalized:
        normalized = normalized.rstrip("0").rstrip(".")
    return normalized or "0"


def _normalize_text(value: Any, *, lower: bool = False) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text.lower() if lower else text


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _set(obj: Any, key: str, value: Any) -> None:
    if isinstance(obj, dict):
        obj[key] = value
    else:
        setattr(obj, key, value)


def _payload_hash(payload: Dict[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _fingerprint_basis(event: Any) -> Dict[str, Any]:
    return {
        "v": FINGERPRINT_VERSION,
        "facility_id": _normalize_text(_get(event, "facility_id"), lower=True),
        "source_type": _normalize_text(_get(event, "source_type"), lower=True),
        "metric_type": _normalize_text(_get(event, "metric_type"), lower=True),
        "value": _normalize_number(_get(event, "value")),
        "unit": _normalize_text(_get(event, "unit"), lower=True),
        "event_timestamp": _to_iso_utc(_get(event, "event_timestamp")),
        "process_line": _normalize_text(_get(event, "process_line")),
        "batch_id": _normalize_text(_get(event, "batch_id")),
        "order_id": _normalize_text(_get(event, "order_id")),
        "asset_id": _normalize_text(_get(event, "asset_id")),
    }


def _idempotency_basis(event: Any) -> Dict[str, Any]:
    source_event_id = _normalize_text(_get(event, "source_event_id"))

    if source_event_id:
        return {
            "v": IDEMPOTENCY_VERSION,
            "mode": "source_event_id",
            "facility_id": _normalize_text(_get(event, "facility_id"), lower=True),
            "source_type": _normalize_text(_get(event, "source_type"), lower=True),
            "source_event_id": source_event_id,
        }

    fp_basis = _fingerprint_basis(event).copy()
    fp_basis["v"] = IDEMPOTENCY_VERSION
    fp_basis["mode"] = "fingerprint_fallback"
    return fp_basis


def build_fingerprint(event: Any) -> str:
    return _payload_hash(_fingerprint_basis(event))


def build_idempotency_key(event: Any) -> str:
    return _payload_hash(_idempotency_basis(event))


def finalize_event(event: Any) -> Any:
    if _get(event, "schema_version") in (None, ""):
        _set(event, "schema_version", SCHEMA_VERSION)

    ingested_at = _to_iso_utc(_get(event, "ingested_at"))
    if not ingested_at:
        ingested_at = _utc_now_iso()
        _set(event, "ingested_at", ingested_at)
    else:
        _set(event, "ingested_at", ingested_at)

    event_timestamp = _to_iso_utc(_get(event, "event_timestamp"))
    if not event_timestamp:
        event_timestamp = ingested_at
        _set(event, "event_timestamp", event_timestamp)
    else:
        _set(event, "event_timestamp", event_timestamp)

    if not _get(event, "event_id"):
        _set(event, "event_id", str(uuid.uuid4()))

    # normalize core identity fields in-place
    for key in ("facility_id", "source_type", "metric_type", "unit"):
        value = _normalize_text(_get(event, key), lower=True)
        if value is not None:
            _set(event, key, value)

    value_norm = _normalize_number(_get(event, "value"))
    if value_norm is not None:
        try:
            _set(event, "value", float(value_norm))
        except ValueError:
            pass

    if not _get(event, "fingerprint"):
        _set(event, "fingerprint", build_fingerprint(event))

    if not _get(event, "idempotency_key"):
        _set(event, "idempotency_key", build_idempotency_key(event))

    if _get(event, "validation_errors") is None:
        _set(event, "validation_errors", [])

    return event
