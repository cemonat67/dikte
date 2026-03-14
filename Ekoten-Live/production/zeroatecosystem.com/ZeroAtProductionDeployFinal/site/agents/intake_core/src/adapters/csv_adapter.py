from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from agents.intake_core.src.adapter_base import AdapterBase
from agents.intake_core.src.canonical_event import CanonicalEvent


class CSVAdapter(AdapterBase):
    source_type = "csv"
    trust_level = "medium"
    default_confidence_score = 0.85

    # metric_type -> canonical unit
    METRIC_UNIT_MAP = {
        "water_m3": "m3",
        "energy_kwh": "kwh",
        "natural_gas_m3": "m3",
        "steam_ton": "ton",
        "co2_kg": "kg",
        "wastewater_m3": "m3",
        "production_kg": "kg",
        "cod_mg_l": "mg/l",
        "bod_mg_l": "mg/l",
        "tss_mg_l": "mg/l",
        "ph": "ph",
    }

    def parse(self, payload: Any) -> List[CanonicalEvent]:
        """
        Expected payload:
        {
          "rows": [ {...}, {...} ],
          "file_name": "example.csv"
        }

        Wide CSV support:
        facility, water_m3, energy_kwh, natural_gas_m3, ...
        =>
        one CanonicalEvent per metric cell
        """
        rows = payload.get("rows", [])
        file_name = payload.get("file_name", "unknown.csv")

        events: List[CanonicalEvent] = []

        for idx, row in enumerate(rows, start=1):
            facility_raw = str(row.get("facility", "")).strip()
            facility_id = self.resolve_facility_id(facility_raw)

            event_timestamp = self._resolve_event_timestamp(row, idx)

            for metric_type, unit in self.METRIC_UNIT_MAP.items():
                raw_value = row.get(metric_type)

                if self._is_blank(raw_value):
                    continue

                try:
                    value = float(str(raw_value).strip().replace(",", "."))
                except ValueError:
                    continue

                event = CanonicalEvent(
                    facility_id=facility_id,
                    source_type=self.source_type,
                    metric_type=metric_type,
                    value=value,
                    unit=unit,
                    event_timestamp=event_timestamp,
                    process_line=row.get("process_line"),
                    batch_id=row.get("batch_id"),
                    order_id=row.get("order_id"),
                    asset_id=row.get("asset_id"),
                    confidence_score=float(row.get("confidence_score", self.default_confidence_score)),
                    trust_level=self.trust_level,
                    source_event_id=f"{file_name}:{idx}:{metric_type}",
                    source_metadata=self.build_source_metadata(
                        payload,
                        {
                            "file_name": file_name,
                            "row_number": idx,
                            "source_facility": facility_raw,
                            "wide_row_metric": metric_type,
                        },
                    ),
                )
                events.append(event)

        return events

    def _resolve_event_timestamp(self, row: Dict[str, Any], idx: int) -> str:
        for key in ("event_timestamp", "timestamp", "date", "datetime", "event_time"):
            v = row.get(key)
            if not self._is_blank(v):
                return str(v).strip()

        # deterministic enough for smoke / ingestion fallback
        # same ingest moment format, UTC ISO
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _is_blank(value: Any) -> bool:
        return value is None or str(value).strip() == ""
