from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import uuid

import psycopg
from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Any


CANONICAL_METRICS = (
    "electricity_kwh",
    "water_m3",
    "medical_waste_kg",
    "pathological_waste_kg",
    "general_waste_kg",
    "scope2_location_tco2e",
    "waste_cost_try",
)

EMISSION_FACTOR_SCOPE2 = Decimal("0.000460")
WASTE_COST_FACTOR_TRY = Decimal("43.3255")


def q(value: Decimal | float | int | str, digits: str = "0.001") -> Decimal:
    return Decimal(str(value)).quantize(Decimal(digits), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class FacilityBootstrapInput:
    facility_code: str
    facility_name: str | None
    facility_type: str
    gross_area_m2: int | None
    bed_count: int | None
    dashboard_rows: int = 0


@dataclass(frozen=True)
class BootstrapProfile:
    facility_code: str
    facility_type: str
    profile_type: str
    size_band: str
    driver_kind: str
    driver_value: Decimal
    intensity_electricity_kwh_per_driver: Decimal
    intensity_water_m3_per_driver: Decimal
    intensity_medical_waste_kg_per_driver: Decimal
    pathological_share_of_medical: Decimal
    general_waste_ratio_to_medical: Decimal
    source_note: str


@dataclass(frozen=True)
class BootstrapMetricBundle:
    facility_code: str
    metric_date: str
    electricity_kwh: Decimal
    water_m3: Decimal
    medical_waste_kg: Decimal
    pathological_waste_kg: Decimal
    general_waste_kg: Decimal
    scope2_location_tco2e: Decimal
    waste_cost_try: Decimal
    total_waste_kg: Decimal
    driver_kind: str
    driver_value: Decimal
    profile_type: str
    size_band: str


@dataclass(frozen=True)
class BootstrapContract:
    facility: FacilityBootstrapInput
    profile: BootstrapProfile
    metrics: BootstrapMetricBundle

@dataclass(frozen=True)
class StagingMetricRow:
    facility_code: str
    metric_date: str
    metric_code: str
    raw_value: Decimal
    normalized_value: Decimal
    unit: str
    source_system: str
    validation_status: str
    is_promotable: bool
    is_active: bool
    record_version: int
    notes: str


METRIC_UNITS = {
    "electricity_kwh": "kwh",
    "water_m3": "m3",
    "medical_waste_kg": "kg",
    "pathological_waste_kg": "kg",
    "general_waste_kg": "kg",
    "scope2_location_tco2e": "tco2e",
    "waste_cost_try": "try",
}


PROFILE_RULES: dict[str, dict[str, Any]] = {
    "hospital": {
        "driver_kind": "bed_count",
        "default_driver": Decimal("100"),
        "profile_type": "inpatient_hospital",
        "bands": (
            ("small", Decimal("0"), Decimal("99")),
            ("medium", Decimal("100"), Decimal("199")),
            ("large", Decimal("200"), Decimal("999999")),
        ),
        "intensities": {
            "small": {
                "electricity": Decimal("24.0"),
                "water": Decimal("0.80"),
                "medical_waste": Decimal("3.20"),
                "pathological_share": Decimal("0.12"),
                "general_ratio": Decimal("1.80"),
            },
            "medium": {
                "electricity": Decimal("26.0"),
                "water": Decimal("0.90"),
                "medical_waste": Decimal("3.50"),
                "pathological_share": Decimal("0.13"),
                "general_ratio": Decimal("1.90"),
            },
            "large": {
                "electricity": Decimal("28.0"),
                "water": Decimal("1.00"),
                "medical_waste": Decimal("3.80"),
                "pathological_share": Decimal("0.14"),
                "general_ratio": Decimal("2.00"),
            },
        },
    },
    "medical_center": {
        "driver_kind": "gross_area_m2",
        "default_driver": Decimal("3000"),
        "profile_type": "ambulatory_medical_center",
        "bands": (
            ("small", Decimal("0"), Decimal("3999")),
            ("medium", Decimal("4000"), Decimal("7999")),
            ("large", Decimal("8000"), Decimal("999999")),
        ),
        "intensities": {
            "small": {
                "electricity": Decimal("0.95"),
                "water": Decimal("0.020"),
                "medical_waste": Decimal("0.028"),
                "pathological_share": Decimal("0.06"),
                "general_ratio": Decimal("1.25"),
            },
            "medium": {
                "electricity": Decimal("1.05"),
                "water": Decimal("0.022"),
                "medical_waste": Decimal("0.032"),
                "pathological_share": Decimal("0.07"),
                "general_ratio": Decimal("1.35"),
            },
            "large": {
                "electricity": Decimal("1.15"),
                "water": Decimal("0.024"),
                "medical_waste": Decimal("0.036"),
                "pathological_share": Decimal("0.08"),
                "general_ratio": Decimal("1.45"),
            },
        },
    },
    "dental_center": {
        "driver_kind": "gross_area_m2",
        "default_driver": Decimal("2500"),
        "profile_type": "outpatient_dental_center",
        "bands": (
            ("small", Decimal("0"), Decimal("2499")),
            ("medium", Decimal("2500"), Decimal("4999")),
            ("large", Decimal("5000"), Decimal("999999")),
        ),
        "intensities": {
            "small": {
                "electricity": Decimal("0.85"),
                "water": Decimal("0.018"),
                "medical_waste": Decimal("0.024"),
                "pathological_share": Decimal("0.05"),
                "general_ratio": Decimal("1.10"),
            },
            "medium": {
                "electricity": Decimal("0.95"),
                "water": Decimal("0.020"),
                "medical_waste": Decimal("0.028"),
                "pathological_share": Decimal("0.06"),
                "general_ratio": Decimal("1.20"),
            },
            "large": {
                "electricity": Decimal("1.05"),
                "water": Decimal("0.022"),
                "medical_waste": Decimal("0.032"),
                "pathological_share": Decimal("0.07"),
                "general_ratio": Decimal("1.30"),
            },
        },
    },
    "eye_center": {
        "driver_kind": "gross_area_m2",
        "default_driver": Decimal("3500"),
        "profile_type": "specialty_eye_center",
        "bands": (
            ("small", Decimal("0"), Decimal("3499")),
            ("medium", Decimal("3500"), Decimal("5999")),
            ("large", Decimal("6000"), Decimal("999999")),
        ),
        "intensities": {
            "small": {
                "electricity": Decimal("1.05"),
                "water": Decimal("0.019"),
                "medical_waste": Decimal("0.022"),
                "pathological_share": Decimal("0.05"),
                "general_ratio": Decimal("1.15"),
            },
            "medium": {
                "electricity": Decimal("1.15"),
                "water": Decimal("0.021"),
                "medical_waste": Decimal("0.026"),
                "pathological_share": Decimal("0.06"),
                "general_ratio": Decimal("1.25"),
            },
            "large": {
                "electricity": Decimal("1.25"),
                "water": Decimal("0.023"),
                "medical_waste": Decimal("0.030"),
                "pathological_share": Decimal("0.07"),
                "general_ratio": Decimal("1.35"),
            },
        },
    },
}


def normalize_facility_type(value: str | None) -> str:
    raw = (value or "").strip().lower()

    aliases = {
        "private_hospital": "hospital",
        "public_hospital": "hospital",
        "state_hospital": "hospital",
        "training_research_hospital": "hospital",
        "education_research_hospital": "hospital",
        "medical_center": "medical_center",
        "medical_centre": "medical_center",
    }

    normalized = aliases.get(raw, raw)

    if normalized in PROFILE_RULES:
        return normalized

    raise ValueError(f"unsupported facility_type: {value!r}")


def decimal_or_none(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    return Decimal(str(value))


def pick_size_band(driver_value: Decimal, bands: tuple[tuple[str, Decimal, Decimal], ...]) -> str:
    for band_name, low, high in bands:
        if low <= driver_value <= high:
            return band_name
    return bands[-1][0]


def resolve_bootstrap_profile(facility: FacilityBootstrapInput) -> BootstrapProfile:
    facility_type = normalize_facility_type(facility.facility_type)
    rule = PROFILE_RULES[facility_type]

    driver_kind = rule["driver_kind"]
    if driver_kind == "bed_count":
        raw_driver = decimal_or_none(facility.bed_count)
    elif driver_kind == "gross_area_m2":
        raw_driver = decimal_or_none(facility.gross_area_m2)
    else:
        raise ValueError(f"unsupported driver_kind: {driver_kind}")

    driver_value = raw_driver if raw_driver and raw_driver > 0 else rule["default_driver"]
    size_band = pick_size_band(driver_value, rule["bands"])
    intensity = rule["intensities"][size_band]

    source_field = driver_kind if raw_driver and raw_driver > 0 else f"default_{driver_kind}"

    return BootstrapProfile(
        facility_code=facility.facility_code,
        facility_type=facility_type,
        profile_type=rule["profile_type"],
        size_band=size_band,
        driver_kind=driver_kind,
        driver_value=q(driver_value, "0.001"),
        intensity_electricity_kwh_per_driver=q(intensity["electricity"], "0.0001"),
        intensity_water_m3_per_driver=q(intensity["water"], "0.0001"),
        intensity_medical_waste_kg_per_driver=q(intensity["medical_waste"], "0.0001"),
        pathological_share_of_medical=q(intensity["pathological_share"], "0.0001"),
        general_waste_ratio_to_medical=q(intensity["general_ratio"], "0.0001"),
        source_note=f"profile={rule['profile_type']};driver={source_field};band={size_band}",
    )


def generate_bootstrap_metrics(
    facility: FacilityBootstrapInput,
    profile: BootstrapProfile,
    metric_date: date,
) -> BootstrapMetricBundle:
    electricity_kwh = q(profile.driver_value * profile.intensity_electricity_kwh_per_driver)
    water_m3 = q(profile.driver_value * profile.intensity_water_m3_per_driver)
    medical_waste_kg = q(profile.driver_value * profile.intensity_medical_waste_kg_per_driver)
    pathological_waste_kg = q(medical_waste_kg * profile.pathological_share_of_medical)
    general_waste_kg = q(medical_waste_kg * profile.general_waste_ratio_to_medical)

    total_waste_kg = q(medical_waste_kg + pathological_waste_kg + general_waste_kg)
    scope2_location_tco2e = q(electricity_kwh * EMISSION_FACTOR_SCOPE2)
    waste_cost_try = q(total_waste_kg * WASTE_COST_FACTOR_TRY)

    return BootstrapMetricBundle(
        facility_code=facility.facility_code,
        metric_date=metric_date.isoformat(),
        electricity_kwh=electricity_kwh,
        water_m3=water_m3,
        medical_waste_kg=medical_waste_kg,
        pathological_waste_kg=pathological_waste_kg,
        general_waste_kg=general_waste_kg,
        scope2_location_tco2e=scope2_location_tco2e,
        waste_cost_try=waste_cost_try,
        total_waste_kg=total_waste_kg,
        driver_kind=profile.driver_kind,
        driver_value=profile.driver_value,
        profile_type=profile.profile_type,
        size_band=profile.size_band,
    )


def build_bootstrap_contract(
    facility: FacilityBootstrapInput,
    metric_date: date,
) -> BootstrapContract:
    profile = resolve_bootstrap_profile(facility)
    metrics = generate_bootstrap_metrics(facility, profile, metric_date)
    return BootstrapContract(facility=facility, profile=profile, metrics=metrics)


def build_staging_payload(contract: BootstrapContract) -> list[StagingMetricRow]:
    metric_map = {
        "electricity_kwh": contract.metrics.electricity_kwh,
        "water_m3": contract.metrics.water_m3,
        "medical_waste_kg": contract.metrics.medical_waste_kg,
        "pathological_waste_kg": contract.metrics.pathological_waste_kg,
        "general_waste_kg": contract.metrics.general_waste_kg,
        "scope2_location_tco2e": contract.metrics.scope2_location_tco2e,
        "waste_cost_try": contract.metrics.waste_cost_try,
    }

    notes = (
        f"bootstrap_seed;"
        f"profile_type={contract.profile.profile_type};"
        f"size_band={contract.profile.size_band};"
        f"driver_kind={contract.profile.driver_kind};"
        f"driver_value={contract.profile.driver_value}"
    )

    rows: list[StagingMetricRow] = []
    for metric_code in CANONICAL_METRICS:
        value = metric_map[metric_code]
        rows.append(
            StagingMetricRow(
                facility_code=contract.facility.facility_code,
                metric_date=contract.metrics.metric_date,
                metric_code=metric_code,
                raw_value=value,
                normalized_value=value,
                unit=METRIC_UNITS[metric_code],
                source_system="bootstrap_seed",
                validation_status="VALID",
                is_promotable=True,
                is_active=True,
                record_version=1,
                notes=notes,
            )
        )

    return rows



def write_staging_rows(rows: list[StagingMetricRow]) -> dict[str, Any]:
    if not rows:
        return {
            "status": "NOOP_EMPTY_PAYLOAD",
            "inserted_rows": 0,
            "existing_rows": 0,
        }

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    facility_code = rows[0].facility_code
    metric_date = rows[0].metric_date
    batch_id = f"bootstrap_{facility_code}_{metric_date}_{uuid.uuid4().hex[:8]}"

    check_sql = """
    select count(*) as row_count
    from zerocare_operational.staging_daily_metrics
    where facility_code = %s
      and metric_date = %s
      and source_system = 'bootstrap_seed'
      and is_active = true
    """

    insert_sql = """
    insert into zerocare_operational.staging_daily_metrics (
        batch_id,
        source,
        source_system,
        source_ref,
        facility_code,
        metric_date,
        metric_code,
        raw_value,
        raw_unit,
        raw_payload,
        metric_value,
        metric_unit,
        normalized_value,
        normalized_unit,
        conversion_rule,
        metric_profile_version,
        facility_profile_version,
        validation_status,
        validation_errors,
        validation_warnings,
        is_required_metric,
        is_promotable,
        validated_by,
        payload_hash,
        fingerprint,
        record_version,
        is_active
    )
    values (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, %s, %s, %s, %s, %s
    )
    """

    with psycopg.connect(database_url, prepare_threshold=None) as conn:
        with conn.cursor() as cur:
            cur.execute(check_sql, (facility_code, metric_date))
            existing_rows = cur.fetchone()[0]

            if existing_rows > 0:
                return {
                    "status": "NOOP_ALREADY_BOOTSTRAPPED",
                    "inserted_rows": 0,
                    "existing_rows": existing_rows,
                    "facility_code": facility_code,
                    "metric_date": metric_date,
                }

            payload = []
            for row in rows:
                raw_payload_obj = {
                    "facility_code": row.facility_code,
                    "metric_date": row.metric_date,
                    "metric_code": row.metric_code,
                    "raw_value": str(row.raw_value),
                    "normalized_value": str(row.normalized_value),
                    "unit": row.unit,
                    "source_system": row.source_system,
                    "notes": row.notes,
                }
                raw_payload_json = json.dumps(raw_payload_obj, ensure_ascii=False, sort_keys=True)
                payload_hash = hashlib.sha256(raw_payload_json.encode("utf-8")).hexdigest()
                fingerprint_seed = "|".join([
                    row.facility_code,
                    row.metric_date,
                    row.metric_code,
                    row.source_system,
                    str(row.normalized_value),
                    str(row.record_version),
                ])
                fingerprint = hashlib.sha256(fingerprint_seed.encode("utf-8")).hexdigest()

                payload.append(
                    (
                        batch_id,
                        "synthetic",
                        row.source_system,
                        f"{row.facility_code}:{row.metric_date}:{row.metric_code}",
                        row.facility_code,
                        row.metric_date,
                        row.metric_code,
                        str(row.raw_value),
                        row.unit,
                        raw_payload_json,
                        row.normalized_value,
                        row.unit,
                        row.normalized_value,
                        row.unit,
                        "identity",
                        "bootstrap_v1",
                        "bootstrap_v1",
                        row.validation_status,
                        "[]",
                        "[]",
                        True,
                        row.is_promotable,
                        "bootstrap_zero_facilities.py",
                        payload_hash,
                        fingerprint,
                        row.record_version,
                        row.is_active,
                    )
                )

            cur.executemany(insert_sql, payload)
        conn.commit()

    return {
        "status": "OK",
        "inserted_rows": len(rows),
        "existing_rows": 0,
        "facility_code": facility_code,
        "metric_date": metric_date,
        "batch_id": batch_id,
    }

def check_staging_readiness(facility_code: str, metric_date: str) -> dict[str, Any]:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    sql = '''
    select
        facility_code,
        metric_date,
        total_metrics,
        valid_metrics,
        electricity_kwh,
        water_m3,
        medical_waste_kg,
        pathological_waste_kg,
        general_waste_kg,
        scope2_location_tco2e,
        waste_cost_try,
        status
    from zerocare_operational.v_staging_daily_metrics_status
    where facility_code = %s
      and metric_date = %s
    '''

    with psycopg.connect(database_url, prepare_threshold=None) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (facility_code, metric_date))
            row = cur.fetchone()

    if not row:
        return {
            "status": "NOT_FOUND",
            "facility_code": facility_code,
            "metric_date": metric_date,
            "ready": False,
        }

    result = {
        "facility_code": row[0],
        "metric_date": str(row[1]),
        "total_metrics": row[2],
        "valid_metrics": row[3],
        "electricity_kwh": row[4],
        "water_m3": row[5],
        "medical_waste_kg": row[6],
        "pathological_waste_kg": row[7],
        "general_waste_kg": row[8],
        "scope2_location_tco2e": row[9],
        "waste_cost_try": row[10],
        "staging_status": row[11],
    }

    result["ready"] = (
        result["total_metrics"] == 7
        and result["valid_metrics"] == 7
        and result["staging_status"] == "READY"
    )
    result["status"] = "OK" if result["ready"] else "PARTIAL"

    return result


def run_promote(facility_code: str, metric_date: str) -> dict[str, Any]:
    readiness = check_staging_readiness(facility_code, metric_date)
    if not readiness.get("ready"):
        return {
            "status": "SKIP_NOT_READY",
            "facility_code": facility_code,
            "metric_date": metric_date,
            "readiness": readiness,
        }

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    sql = '''
    select *
    from zerocare_operational.run_promote_with_audit(%s, %s, null, false)
    '''

    with psycopg.connect(database_url, prepare_threshold=None) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (facility_code, metric_date))
            row = cur.fetchone()
        conn.commit()

    return {
        "status": "OK",
        "facility_code": facility_code,
        "metric_date": metric_date,
        "promote_run_id": row[0],
        "selected_days": row[1],
        "selected_rows": row[2],
        "written_rows": row[3],
        "promote_status": row[4],
    }


def verify_dashboard_daily(facility_code: str, metric_date: str) -> dict[str, Any]:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    sql = '''
    select
        facility_code,
        metric_date,
        electricity_kwh,
        water_m3,
        medical_waste_kg,
        pathological_waste_kg,
        general_waste_kg,
        scope2_location_tco2e,
        waste_cost_try
    from zerocare_operational.vw_dashboard_daily
    where facility_code = %s
      and metric_date = %s
    '''

    with psycopg.connect(database_url, prepare_threshold=None) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (facility_code, metric_date))
            row = cur.fetchone()

    if not row:
        return {
            "status": "NOT_FOUND",
            "facility_code": facility_code,
            "metric_date": metric_date,
            "exists": False,
        }

    result = {
        "facility_code": row[0],
        "metric_date": str(row[1]),
        "electricity_kwh": row[2],
        "water_m3": row[3],
        "medical_waste_kg": row[4],
        "pathological_waste_kg": row[5],
        "general_waste_kg": row[6],
        "scope2_location_tco2e": row[7],
        "waste_cost_try": row[8],
    }

    result["exists"] = True
    result["present_metric_count"] = sum(
        1 for key in (
            "electricity_kwh",
            "water_m3",
            "medical_waste_kg",
            "pathological_waste_kg",
            "general_waste_kg",
            "scope2_location_tco2e",
            "waste_cost_try",
        )
        if result[key] is not None
    )
    result["status"] = "OK" if result["present_metric_count"] == 7 else "PARTIAL"

    return result


def _json_default(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError(f"unsupported type: {type(value)!r}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--facility-code", required=True)
    parser.add_argument("--facility-type", required=True)
    parser.add_argument("--gross-area-m2", type=int, default=None)
    parser.add_argument("--bed-count", type=int, default=None)
    parser.add_argument("--facility-name", default=None)
    parser.add_argument("--metric-date", default=date.today().isoformat())
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    facility = FacilityBootstrapInput(
        facility_code=args.facility_code,
        facility_name=args.facility_name,
        facility_type=args.facility_type,
        gross_area_m2=args.gross_area_m2,
        bed_count=args.bed_count,
        dashboard_rows=0,
    )

    metric_dt = date.fromisoformat(args.metric_date)
    contract = build_bootstrap_contract(
        facility=facility,
        metric_date=metric_dt,
    )
    staging_rows = build_staging_payload(contract)
    write_result = write_staging_rows(staging_rows)
    readiness = check_staging_readiness(facility.facility_code, metric_dt.isoformat())
    promote_result = run_promote(facility.facility_code, metric_dt.isoformat())
    dashboard_verify = verify_dashboard_daily(facility.facility_code, metric_dt.isoformat())

    payload = {
        "status": "OK" if dashboard_verify.get("status") == "OK" else "PARTIAL",
        "phase": "bootstrap_full_flow",
        "canonical_metrics": list(CANONICAL_METRICS),
        "contract": asdict(contract),
        "staging_row_count": len(staging_rows),
        "write_result": write_result,
        "readiness": readiness,
        "promote_result": promote_result,
        "dashboard_verify": dashboard_verify,
    }

    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None, default=_json_default))


if __name__ == "__main__":
    main()
