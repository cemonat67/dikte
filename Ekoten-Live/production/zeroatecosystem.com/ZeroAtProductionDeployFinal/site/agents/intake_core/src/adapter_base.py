from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List

from agents.intake_core.src.facility_registry import FacilityRegistry
from agents.intake_core.src.fingerprint import finalize_event


class AdapterBase(ABC):
    source_type = "unknown"

    def __init__(self, registry: FacilityRegistry | None = None) -> None:
        self.registry = registry or FacilityRegistry()

    @abstractmethod
    def parse(self, payload: Any) -> List[Any]:
        raise NotImplementedError

    def resolve_facility_id(self, raw_value: Any) -> str:
        text = "" if raw_value is None else str(raw_value).strip()
        if not text:
            return ""

        reg = self.registry

        # Common API patterns — try them safely in order
        for method_name in (
            "resolve_facility_id",
            "resolve",
            "get_facility_id",
            "normalize_facility_id",
            "lookup",
        ):
            method = getattr(reg, method_name, None)
            if callable(method):
                try:
                    result = method(text)
                    if result:
                        return str(result).strip().lower()
                except TypeError:
                    pass

        # Alias-map fallback if registry is just data
        aliases = getattr(reg, "ALIASES", None) or getattr(reg, "aliases", None)
        if isinstance(aliases, dict):
            candidate = aliases.get(text) or aliases.get(text.lower())
            if candidate:
                return str(candidate).strip().lower()

        # Conservative fallback
        return text.strip().lower()

    def build_source_metadata(self, payload: Any, extra: Dict[str, Any] | None = None) -> Dict[str, Any]:
        meta: Dict[str, Any] = {}

        if isinstance(payload, dict):
            payload_meta = payload.get("source_metadata")
            if isinstance(payload_meta, dict):
                meta.update(payload_meta)

            for key in ("file_name", "source_type", "batch_id", "source_system"):
                value = payload.get(key)
                if value not in (None, ""):
                    meta[key] = value

        if extra:
            for k, v in extra.items():
                if v is not None:
                    meta[k] = v

        return meta

    def finalize_events(self, events: Iterable[Any]) -> List[Any]:
        finalized = []
        for event in events:
            if isinstance(event, dict):
                event.setdefault("source_type", self.source_type)
            else:
                if not getattr(event, "source_type", None):
                    setattr(event, "source_type", self.source_type)

            finalized.append(finalize_event(event))

        return finalized

    def parse_and_finalize(self, payload: Any) -> List[Any]:
        return self.finalize_events(self.parse(payload))
