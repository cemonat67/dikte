from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass(slots=True)
class MetricDefinition:
    metric_type: str
    canonical_unit: str
    min_value: float | None = None
    max_value: float | None = None


@dataclass(slots=True)
class ProcessLine:
    line_id: str
    process_type: str
    description: str = ""


@dataclass(slots=True)
class FacilityDefinition:
    facility_id: str
    facility_name: str
    timezone: str = "Europe/Istanbul"
    aliases: List[str] = field(default_factory=list)
    process_lines: Dict[str, ProcessLine] = field(default_factory=dict)
    metrics: Dict[str, MetricDefinition] = field(default_factory=dict)


class FacilityRegistry:
    """
    In-memory facility registry used by intake architecture.

    Later this can be backed by PostgreSQL / Supabase tables,
    but this class defines the contract now.
    """

    def __init__(self) -> None:
        self._facilities: Dict[str, FacilityDefinition] = {}
        self._alias_to_facility: Dict[str, str] = {}

    def register_facility(self, facility: FacilityDefinition) -> None:
        fid = facility.facility_id.strip().lower()
        self._facilities[fid] = facility
        self._alias_to_facility[fid] = fid

        for alias in facility.aliases:
            self._alias_to_facility[alias.strip().lower()] = fid

    def resolve_facility_id(self, raw_name: str) -> Optional[str]:
        if not raw_name:
            return None
        return self._alias_to_facility.get(raw_name.strip().lower())

    def get_facility(self, facility_id_or_alias: str) -> Optional[FacilityDefinition]:
        resolved = self.resolve_facility_id(facility_id_or_alias)
        if not resolved:
            return None
        return self._facilities.get(resolved)

    def get_metric_definition(
        self,
        facility_id_or_alias: str,
        metric_type: str
    ) -> Optional[MetricDefinition]:
        facility = self.get_facility(facility_id_or_alias)
        if not facility:
            return None
        return facility.metrics.get(metric_type.strip().lower())

    def get_process_line(
        self,
        facility_id_or_alias: str,
        line_id: str
    ) -> Optional[ProcessLine]:
        facility = self.get_facility(facility_id_or_alias)
        if not facility:
            return None
        return facility.process_lines.get(line_id.strip().lower())

    def validate_metric_value(
        self,
        facility_id_or_alias: str,
        metric_type: str,
        value: float
    ) -> Tuple[bool, Optional[str]]:
        metric = self.get_metric_definition(facility_id_or_alias, metric_type)
        if not metric:
            return False, "unknown_metric"

        if metric.min_value is not None and value < metric.min_value:
            return False, f"value_below_min:{metric.min_value}"

        if metric.max_value is not None and value > metric.max_value:
            return False, f"value_above_max:{metric.max_value}"

        return True, None


def build_default_ekoten_registry() -> FacilityRegistry:
    registry = FacilityRegistry()

    ekoten = FacilityDefinition(
        facility_id="ekoten",
        facility_name="Ekoten Tekstil",
        aliases=["ekoten", "ekoten tekstil", "eko", "ektn"],
        process_lines={
            "dye_line_3": ProcessLine(
                line_id="dye_line_3",
                process_type="dyeing",
                description="Primary dyeing line 3",
            ),
            "finishing_line_1": ProcessLine(
                line_id="finishing_line_1",
                process_type="finishing",
                description="Primary finishing line 1",
            ),
            "boiler_room": ProcessLine(
                line_id="boiler_room",
                process_type="utilities",
                description="Steam and heat generation zone",
            ),
        },
        metrics={
            "water_m3": MetricDefinition(
                metric_type="water_m3",
                canonical_unit="m3",
                min_value=0,
                max_value=5000,
            ),
            "energy_kwh": MetricDefinition(
                metric_type="energy_kwh",
                canonical_unit="kwh",
                min_value=0,
                max_value=100000,
            ),
            "natural_gas_m3": MetricDefinition(
                metric_type="natural_gas_m3",
                canonical_unit="m3",
                min_value=0,
                max_value=30000,
            ),
            "production_kg": MetricDefinition(
                metric_type="production_kg",
                canonical_unit="kg",
                min_value=0,
                max_value=500000,
            ),
        },
    )

    registry.register_facility(ekoten)
    return registry

    def find_by_name(self, facility_name: str):
        sql = """
        select facility_id, facility_name, timezone, status
        from public.facility_registry
        where lower(facility_name) = lower(%s)
        limit 1
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (facility_name,))
                row = cur.fetchone()
                if not row:
                    return None
                cols = [d[0] for d in cur.description]
                return dict(zip(cols, row))

