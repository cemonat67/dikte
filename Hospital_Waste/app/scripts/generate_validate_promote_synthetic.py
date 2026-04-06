import os
import math
import uuid
import json
import hashlib
import random
from datetime import date, datetime, timedelta
from decimal import Decimal

try:
    import psycopg
except Exception:
    import psycopg2 as psycopg


DATABASE_URL = os.getenv("DATABASE_URL")
FACILITY_CODE = os.getenv("FACILITY_CODE")
FACILITY_NAME = os.getenv("FACILITY_NAME")
GENERATOR_VERSION = "synthetic-hospital-v3-baseline-aware"

if not DATABASE_URL:
    raise SystemExit("DATABASE_URL yok")

if not FACILITY_CODE:
    raise SystemExit("FACILITY_CODE yok")

if not FACILITY_NAME:
    raise SystemExit("FACILITY_NAME yok")

BASELINE_DATE = date(2026, 3, 1)
START_DATE = date(2026, 3, 2)
DAYS = 30
END_DATE = START_DATE + timedelta(days=DAYS - 1)
BATCH_ID = str(uuid.uuid4())

METRICS = {
    "water_m3": {"unit": "m3"},
    "wastewater_m3": {"unit": "m3"},
    "energy_kwh": {"unit": "kwh"},
    "natural_gas_m3": {"unit": "m3"},
    "steam_ton": {"unit": "ton"},
    "production_kg": {"unit": "kg"},
    "co2_kg": {"unit": "kg"},
    "cod_mg_l": {"unit": "mg/l"},
    "bod_mg_l": {"unit": "mg/l"},
    "tss_mg_l": {"unit": "mg/l"},
    "ph": {"unit": "ph"},
}

ANOMALY_DAYS = {
    date(2026, 3, 12): "effluent_spike",
    date(2026, 3, 21): "energy_spike",
}


def connect():
    return psycopg.connect(DATABASE_URL)


def D(v):
    return Decimal(str(round(float(v), 4)))


def weekly_factor(day):
    return {0: 1.02, 1: 1.03, 2: 1.01, 3: 1.00, 4: 1.02, 5: 0.96, 6: 0.94}[day.weekday()]


def get_baseline(cur):
    cur.execute(
        """
        select metric_key, metric_value
        from public.core_metric_readings
        where facility = %s
          and metric_date = %s
        """,
        (FACILITY_NAME, BASELINE_DATE),
    )
    rows = cur.fetchall()
    baseline = {k: float(v) for k, v in rows}

    required = {
        "water_m3", "wastewater_m3", "energy_kwh", "natural_gas_m3", "steam_ton",
        "production_kg", "co2_kg", "cod_mg_l", "bod_mg_l", "tss_mg_l", "ph"
    }
    missing = sorted(required - set(baseline.keys()))
    if missing:
        raise SystemExit(f"Baseline eksik metric set: {', '.join(missing)}")

    return baseline


def build_ranges(base):
    def band(v, hard_low=0.75, hard_high=1.25, soft_low=0.88, soft_high=1.12, floor=None):
        hv1 = v * hard_low
        hv2 = v * hard_high
        sv1 = v * soft_low
        sv2 = v * soft_high
        if floor is not None:
            hv1 = max(hv1, floor)
            sv1 = max(sv1, floor)
        return (hv1, hv2), (sv1, sv2)

    hard = {}
    soft = {}

    for metric in ["water_m3", "wastewater_m3", "energy_kwh", "natural_gas_m3", "steam_ton", "production_kg", "co2_kg"]:
        hard[metric], soft[metric] = band(base[metric])

    hard["cod_mg_l"], soft["cod_mg_l"] = band(base["cod_mg_l"], 0.70, 2.40, 0.85, 1.35, floor=1)
    hard["bod_mg_l"], soft["bod_mg_l"] = band(base["bod_mg_l"], 0.70, 2.40, 0.85, 1.35, floor=1)
    hard["tss_mg_l"], soft["tss_mg_l"] = band(base["tss_mg_l"], 0.70, 2.20, 0.85, 1.30, floor=1)

    hard["ph"] = (6.0, 9.0)
    soft["ph"] = (6.5, 8.2)

    return hard, soft


def build_ratio_limits(base):
    wastewater_water = base["wastewater_m3"] / base["water_m3"]
    energy_production = base["energy_kwh"] / base["production_kg"]
    co2_energy = base["co2_kg"] / base["energy_kwh"]

    return {
        "wastewater_water": (wastewater_water * 0.90, wastewater_water * 1.10),
        "energy_production": (energy_production * 0.90, energy_production * 1.10),
        "co2_energy": (co2_energy * 0.88, co2_energy * 1.12),
    }


def generate_daily(day, rng, base):
    wf = weekly_factor(day)
    seasonal = 1.0 + 0.015 * math.sin((day - START_DATE).days / 5.0)

    base_prod = base["production_kg"]
    production = base_prod * wf * seasonal * (1 + rng.uniform(-0.06, 0.06))

    energy_ratio = base["energy_kwh"] / base["production_kg"]
    water_ratio = base["water_m3"] / base["production_kg"]
    gas_ratio = base["natural_gas_m3"] / base["production_kg"]
    steam_ratio = base["steam_ton"] / base["production_kg"]
    ww_ratio = base["wastewater_m3"] / base["water_m3"]

    energy = production * energy_ratio * (1 + rng.uniform(-0.04, 0.04))
    water = production * water_ratio * (1 + rng.uniform(-0.04, 0.04))
    wastewater = water * ww_ratio * (1 + rng.uniform(-0.03, 0.03))
    natural_gas = production * gas_ratio * (1 + rng.uniform(-0.05, 0.05))
    steam = production * steam_ratio * (1 + rng.uniform(-0.05, 0.05))

    cod = base["cod_mg_l"] * (1 + rng.uniform(-0.08, 0.08))
    bod = base["bod_mg_l"] * (1 + rng.uniform(-0.08, 0.08))
    tss = base["tss_mg_l"] * (1 + rng.uniform(-0.08, 0.08))
    ph = base["ph"] + rng.uniform(-0.18, 0.18)

    anomaly_type = ANOMALY_DAYS.get(day)
    anomaly_flag = anomaly_type is not None

    if anomaly_type == "effluent_spike":
        cod *= 1.85
        bod *= 1.70
        tss *= 1.28
        wastewater *= 1.03
        ph = base["ph"] + rng.uniform(-0.12, 0.12)

    if anomaly_type == "energy_spike":
        energy *= 1.18
        natural_gas *= 1.10
        steam *= 1.08

    co2 = (energy * 0.41) + (natural_gas * 1.90) + (steam * 52.0)

    values = {
        "water_m3": D(water),
        "wastewater_m3": D(wastewater),
        "energy_kwh": D(energy),
        "natural_gas_m3": D(natural_gas),
        "steam_ton": D(steam),
        "production_kg": D(production),
        "co2_kg": D(co2),
        "cod_mg_l": D(cod),
        "bod_mg_l": D(bod),
        "tss_mg_l": D(tss),
        "ph": D(ph),
    }

    return {
        "date": day,
        "values": values,
        "anomaly_flag": anomaly_flag,
        "anomaly_type": anomaly_type,
    }


def existing_real_pairs(cur):
    cur.execute(
        """
        select metric_date, metric_key
        from public.core_metric_readings
        where facility = %s
          and metric_date between %s and %s
          and coalesce(source_type, 'real') <> 'synthetic'
        """,
        (FACILITY_NAME, START_DATE, END_DATE),
    )
    return {(r[0], r[1]) for r in cur.fetchall()}


def delete_existing_synthetic_for_window(cur):
    cur.execute(
        """
        delete from public.core_metric_readings
        where facility = %s
          and metric_date between %s and %s
          and source_type = 'synthetic'
        """,
        (FACILITY_NAME, START_DATE, END_DATE),
    )


def insert_staging(cur, rows):
    cur.execute("delete from public.synthetic_metric_readings_staging where batch_id = %s", (BATCH_ID,))
    cur.executemany(
        """
        insert into public.synthetic_metric_readings_staging
        (batch_id, facility_code, facility_name, metric_date, metric_code, metric_value, unit, anomaly_flag, anomaly_type, generator_version)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        rows,
    )


def insert_validation(cur, rows):
    cur.execute("delete from public.synthetic_validation_results where batch_id = %s", (BATCH_ID,))
    if rows:
        cur.executemany(
            """
            insert into public.synthetic_validation_results
            (batch_id, facility_code, metric_date, metric_code, status, check_name, severity, message, observed_value, reference_value)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            rows,
        )


def validate_days(days, hard_ranges, soft_ranges, ratio_limits):
    results = []
    accepted_pairs = set()
    prev = None

    for day in days:
        d = day["date"]
        v = day["values"]
        day_status = "accepted"

        for metric, value in v.items():
            lo, hi = hard_ranges[metric]
            slo, shi = soft_ranges[metric]

            if not (lo <= float(value) <= hi):
                results.append((BATCH_ID, FACILITY_CODE, d, metric, "rejected", "range_validation", "critical", f"{metric} hard range dışında", value, None))
                day_status = "rejected"
            elif not (slo <= float(value) <= shi):
                results.append((BATCH_ID, FACILITY_CODE, d, metric, "warning", "range_validation", "warning", f"{metric} soft range dışında", value, None))
                if day_status != "rejected":
                    day_status = "warning"

        ww_ratio = float(v["wastewater_m3"] / v["water_m3"])
        ep_ratio = float(v["energy_kwh"] / v["production_kg"])
        ce_ratio = float(v["co2_kg"] / v["energy_kwh"])

        ratio_map = {
            "wastewater_m3": ("ratio_validation", "wastewater/water", ww_ratio, ratio_limits["wastewater_water"]),
            "energy_kwh": ("ratio_validation", "energy/production", ep_ratio, ratio_limits["energy_production"]),
            "co2_kg": ("ratio_validation", "co2/energy", ce_ratio, ratio_limits["co2_energy"]),
        }

        for metric, (check_name, label, observed, limits) in ratio_map.items():
            lo, hi = limits
            if not (lo <= observed <= hi):
                severity = "critical" if (observed < lo * 0.9 or observed > hi * 1.1) else "warning"
                status = "rejected" if severity == "critical" else "warning"
                results.append((BATCH_ID, FACILITY_CODE, d, metric, status, check_name, severity, f"{label} beklenen band dışında", D(observed), None))
                if status == "rejected":
                    day_status = "rejected"
                elif day_status != "rejected":
                    day_status = "warning"

        if prev is not None:
            for metric in ["water_m3", "wastewater_m3", "energy_kwh", "natural_gas_m3", "steam_ton", "production_kg", "co2_kg"]:
                curr = float(v[metric])
                prv = float(prev["values"][metric])
                change = abs(curr - prv) / prv if prv else 0
                if change > 0.18:
                    results.append((BATCH_ID, FACILITY_CODE, d, metric, "warning", "trend_consistency", "warning", f"{metric} günlük değişim yüksek", D(change), D(0.18)))
                    if day_status == "accepted":
                        day_status = "warning"

        if day["anomaly_flag"]:
            at = day["anomaly_type"]
            if at == "effluent_spike":
                plausible = float(v["cod_mg_l"]) > (soft_ranges["cod_mg_l"][1] * 1.15) and float(v["bod_mg_l"]) > (soft_ranges["bod_mg_l"][1] * 1.10)
            elif at == "energy_spike":
                plausible = float(v["energy_kwh"] / v["production_kg"]) > ratio_limits["energy_production"][1]
            else:
                plausible = False

            if plausible:
                results.append((BATCH_ID, FACILITY_CODE, d, "ph", "accepted", "anomaly_plausibility", "info", f"{at} makul bulundu", None, None))
            else:
                results.append((BATCH_ID, FACILITY_CODE, d, "ph", "rejected", "anomaly_plausibility", "critical", f"{at} makul bulunmadı", None, None))
                day_status = "rejected"

        if day_status == "accepted":
            for metric in v.keys():
                accepted_pairs.add((d, metric))

        prev = day

    return results, accepted_pairs


def build_raw_record(metric_date, metric_code, metric_value, unit):
    return json.dumps(
        {
            "batch_id": BATCH_ID,
            "facility_code": FACILITY_CODE,
            "facility_name": FACILITY_NAME,
            "metric_date": str(metric_date),
            "metric_key": metric_code,
            "metric_value": float(metric_value),
            "metric_unit": unit,
            "source_type": "synthetic",
            "source_name": GENERATOR_VERSION,
        },
        ensure_ascii=False,
    )


def build_fingerprint(metric_date, metric_code, metric_value, unit):
    base = f"{FACILITY_NAME}|{metric_date}|{metric_code}|{metric_value}|{unit}|synthetic|{GENERATOR_VERSION}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def promote(cur, accepted_pairs):
    real_existing = existing_real_pairs(cur)

    cur.execute(
        """
        select metric_date, metric_code, metric_value, unit
        from public.synthetic_metric_readings_staging
        where batch_id = %s
          and facility_code = %s
        """,
        (BATCH_ID, FACILITY_CODE),
    )
    rows = cur.fetchall()

    insert_rows = []
    now_ts = datetime.utcnow()

    for metric_date, metric_code, metric_value, unit in rows:
        if (metric_date, metric_code) not in accepted_pairs:
            continue
        if (metric_date, metric_code) in real_existing:
            continue

        raw_record = build_raw_record(metric_date, metric_code, metric_value, unit)
        fingerprint = build_fingerprint(metric_date, metric_code, metric_value, unit)

        insert_rows.append(
            (
                str(uuid.uuid4()),
                f"synthetic:{BATCH_ID}:{FACILITY_CODE}:{metric_date}:{metric_code}",
                BATCH_ID,
                None,
                "synthetic",
                GENERATOR_VERSION,
                FACILITY_NAME,
                metric_date,
                metric_code,
                metric_value,
                unit,
                fingerprint,
                raw_record,
                now_ts,
            )
        )

    if insert_rows:
        cur.executemany(
            """
            insert into public.core_metric_readings
            (id, ingestion_key, batch_id, staging_id, source_type, source_name, facility, metric_date, metric_key, metric_value, metric_unit, record_fingerprint, raw_record, inserted_at)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            insert_rows,
        )

    return len(insert_rows)


def main():
    rng = random.Random(42)

    with connect() as conn:
        with conn.cursor() as cur:
            baseline = get_baseline(cur)
            hard_ranges, soft_ranges = build_ranges(baseline)
            ratio_limits = build_ratio_limits(baseline)

            days = []
            staging_rows = []

            for i in range(DAYS):
                day = START_DATE + timedelta(days=i)
                generated = generate_daily(day, rng, baseline)
                days.append(generated)

                for metric_code, value in generated["values"].items():
                    staging_rows.append(
                        (
                            BATCH_ID,
                            FACILITY_CODE,
                            FACILITY_NAME,
                            generated["date"],
                            metric_code,
                            value,
                            METRICS[metric_code]["unit"],
                            generated["anomaly_flag"],
                            generated["anomaly_type"],
                            GENERATOR_VERSION,
                        )
                    )

            delete_existing_synthetic_for_window(cur)
            insert_staging(cur, staging_rows)
            validation_rows, accepted_pairs = validate_days(days, hard_ranges, soft_ranges, ratio_limits)
            insert_validation(cur, validation_rows)
            promoted = promote(cur, accepted_pairs)
        conn.commit()

    print(f"BATCH_ID={BATCH_ID}")
    print(f"STAGING_ROWS={len(staging_rows)}")
    print(f"VALIDATION_ROWS={len(validation_rows)}")
    print(f"ACCEPTED_METRIC_PAIRS={len(accepted_pairs)}")
    print(f"PROMOTED_ROWS={promoted}")


if __name__ == "__main__":
    main()
