from __future__ import annotations

import csv
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Any, Set


REQUIRED_FIELDS = [
    "facility",
]

OPTIONAL_FIELDS = [
    "event_timestamp",
    "process_line",
    "batch_id",
    "order_id",
    "asset_id",
]

METRIC_FIELDS = [
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
]

ZERO_FILL_ALLOWED = [
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
]

ZERO_FILL_BLOCKED = [
    "facility",
    "event_timestamp",
    "ph",
]

HEADER_ALIASES = {
    "facility_id": "facility",
    "plant": "facility",
    "site": "facility",

    "water": "water_m3",
    "water_consumption": "water_m3",
    "electricity_kwh": "energy_kwh",
    "electricity": "energy_kwh",
    "gas_m3": "natural_gas_m3",
    "natural_gas": "natural_gas_m3",
    "steam": "steam_ton",
    "co2": "co2_kg",
    "waste_water_m3": "wastewater_m3",
    "wastewater": "wastewater_m3",
    "production": "production_kg",
    "cod": "cod_mg_l",
    "bod": "bod_mg_l",
    "tss": "tss_mg_l",
    "p_h": "ph",
}


@dataclass
class PreflightResult:
    ok: bool
    status: str
    file_name: str
    row_count: int
    source_fields: List[str]
    normalized_field_map: Dict[str, str]
    matched_fields: List[str]
    alias_matched_fields: Dict[str, str]
    missing_required_fields: List[str]
    missing_optional_fields: List[str]
    missing_metric_fields: List[str]
    unknown_source_fields: List[str]
    blank_value_counts: Dict[str, int]
    zero_fill_candidates: List[str]
    zero_fill_blocked: List[str]
    blocking_reasons: List[str]
    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _normalize_header(name: str) -> str:
    return str(name or "").strip()


def _canonical_field(name: str) -> str:
    name = _normalize_header(name)
    return HEADER_ALIASES.get(name, name)


def _is_blank(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def _read_rows(csv_path: str) -> tuple[list[dict], list[str]]:
    p = Path(csv_path)
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample)
        except Exception:
            dialect = csv.excel
        reader = csv.DictReader(f, dialect=dialect)
        rows = list(reader)
        return rows, list(reader.fieldnames or [])


def validate_csv_preflight(csv_path: str, registered_metrics: Set[str] | None = None) -> PreflightResult:
    path = str(Path(csv_path).expanduser().resolve())
    rows, source_fields = _read_rows(path)

    normalized_map: Dict[str, str] = {}
    alias_matched: Dict[str, str] = {}

    for src in source_fields:
        canon = _canonical_field(src)
        normalized_map[src] = canon
        if canon != src:
            alias_matched[src] = canon

    normalized_fields = set(normalized_map.values())
    expected_fields = set(REQUIRED_FIELDS + OPTIONAL_FIELDS + METRIC_FIELDS)

    matched_fields = sorted(f for f in normalized_fields if f in expected_fields)
    missing_required = sorted(f for f in REQUIRED_FIELDS if f not in normalized_fields)
    missing_optional = sorted(f for f in OPTIONAL_FIELDS if f not in normalized_fields)
    missing_metric = sorted(f for f in METRIC_FIELDS if f not in normalized_fields)
    unknown_source_fields = sorted(
        src for src, canon in normalized_map.items()
        if canon not in expected_fields
    )

    blank_value_counts: Dict[str, int] = {}
    for field in REQUIRED_FIELDS + OPTIONAL_FIELDS + METRIC_FIELDS:
        source_names = [src for src, canon in normalized_map.items() if canon == field]
        if not source_names:
            continue

        count = 0
        for row in rows:
            hit_blank = True
            for src in source_names:
                if not _is_blank(row.get(src)):
                    hit_blank = False
                    break
            if hit_blank:
                count += 1
        blank_value_counts[field] = count

    zero_fill_candidates = sorted(
        f for f in missing_metric
        if f in ZERO_FILL_ALLOWED
    )

    zero_fill_blocked = sorted(
        [f for f in missing_required if f in ZERO_FILL_BLOCKED] +
        [f for f in missing_optional if f in ZERO_FILL_BLOCKED] +
        [f for f in missing_metric if f in ZERO_FILL_BLOCKED]
    )

    blocking_reasons: List[str] = []
    warnings: List[str] = []

    if missing_required:
        for field in missing_required:
            blocking_reasons.append(f"missing_required:{field}")

    if "event_timestamp" in missing_optional:
        warnings.append("missing_optional:event_timestamp:fallback_policy_required")

    if registered_metrics is not None:
        for metric in METRIC_FIELDS:
            if metric in normalized_fields and metric not in registered_metrics:
                blocking_reasons.append(f"metric_not_registered:{metric}")

    for field, blank_count in blank_value_counts.items():
        if blank_count > 0:
            if field in ZERO_FILL_ALLOWED:
                warnings.append(f"blank_values:{field}:{blank_count}")
            elif field in ZERO_FILL_BLOCKED:
                blocking_reasons.append(f"blank_values_blocked:{field}:{blank_count}")
            else:
                warnings.append(f"blank_values:{field}:{blank_count}")

    ok = len(blocking_reasons) == 0

    if blocking_reasons:
        status = "blocked"
    elif warnings or zero_fill_candidates:
        status = "warning"
    else:
        status = "ready"

    return PreflightResult(
        ok=ok,
        status=status,
        file_name=Path(path).name,
        row_count=len(rows),
        source_fields=source_fields,
        normalized_field_map=normalized_map,
        matched_fields=matched_fields,
        alias_matched_fields=alias_matched,
        missing_required_fields=missing_required,
        missing_optional_fields=missing_optional,
        missing_metric_fields=missing_metric,
        unknown_source_fields=unknown_source_fields,
        blank_value_counts=blank_value_counts,
        zero_fill_candidates=zero_fill_candidates,
        zero_fill_blocked=zero_fill_blocked,
        blocking_reasons=blocking_reasons,
        warnings=warnings,
    )
