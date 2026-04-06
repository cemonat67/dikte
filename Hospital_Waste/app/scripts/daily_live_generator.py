import os
import math
import uuid
import json
import hashlib
import random
from datetime import date, datetime, timedelta, UTC
from decimal import Decimal

import psycopg

DATABASE_URL = os.getenv("DATABASE_URL")
FACILITY_CODE = os.getenv("FACILITY_CODE")
FACILITY_NAME = os.getenv("FACILITY_NAME")
SOURCE_TYPE = "synthetic"
SOURCE_NAME = "synthetic-hospital-v4-rolling-live"

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

REQUIRED_KEYS = set(METRICS.keys())

if not DATABASE_URL:
    raise SystemExit("DATABASE_URL yok")

if not FACILITY_CODE:
    raise SystemExit("FACILITY_CODE yok")

if not FACILITY_NAME:
    raise SystemExit("FACILITY_NAME yok")

def connect():
    return psycopg.connect(DATABASE_URL)

def D(v: float) -> Decimal:
    return Decimal(str(round(float(v), 4)))

def weekly_factor(day: date) -> float:
    return {0: 1.02, 1: 1.03, 2: 1.01, 3: 1.00, 4: 1.02, 5: 0.96, 6: 0.94}[day.weekday()]

def stable_rng(day: date) -> random.Random:
    seed = int(hashlib.sha256(f"{FACILITY_CODE}:{day.isoformat()}".encode()).hexdigest()[:16], 16)
    return random.Random(seed)

def get_latest_metric_date(cur) -> date | None:
    cur.execute(
        """
        select max(metric_date)
        from public.core_metric_readings
        where facility = %s
        """,
        (FACILITY_NAME,),
    )
    row = cur.fetchone()
    return row[0] if row and row[0] else None

def get_last_complete_day_baseline(cur, baseline_day: date) -> dict[str, float]:
    cur.execute(
        """
        select metric_key, metric_value
        from public.core_metric_readings
        where facility = %s
          and metric_date = %s
        """,
        (FACILITY_NAME, baseline_day),
    )
    rows = cur.fetchall()
    baseline = {k: float(v) for k, v in rows}
    missing = sorted(REQUIRED_KEYS - set(baseline.keys()))
    if missing:
        raise SystemExit(f"Baseline eksik metric set ({baseline_day}): {', '.join(missing)}")
    return baseline

def existing_pairs(cur, start_date: date, end_date: date) -> set[tuple[date, str]]:
    cur.execute(
        """
        select metric_date, metric_key
        from public.core_metric_readings
        where facility = %s
          and metric_date between %s and %s
        """,
        (FACILITY_NAME, start_date, end_date),
    )
    return {(r[0], r[1]) for r in cur.fetchall()}

def generate_daily(day: date, base: dict[str, float]) -> dict[str, Decimal]:
    rng = stable_rng(day)
    wf = weekly_factor(day)
    seasonal = 1.0 + 0.015 * math.sin((day.toordinal()) / 5.0)

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

    co2 = (energy * 0.41) + (natural_gas * 1.90) + (steam * 52.0)

    return {
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

def build_record_fingerprint(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def insert_rows(cur, rows: list[tuple]):
    cur.executemany(
        """
        insert into public.core_metric_readings
        (
            id,
            ingestion_key,
            batch_id,
            source_type,
            source_name,
            facility,
            metric_date,
            metric_key,
            metric_value,
            metric_unit,
            record_fingerprint,
            raw_record,
            inserted_at
        )
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
        """,
        rows,
    )

def main():
    today = datetime.now(UTC).date()
    batch_id = str(uuid.uuid4())
    inserted_at = datetime.now(UTC)

    with connect() as conn:
        with conn.cursor() as cur:
            latest_date = get_latest_metric_date(cur)
            if latest_date is None:
                raise SystemExit("Hiç baseline veri yok. Önce en az bir tam gün veri olmalı.")

            start_date = latest_date + timedelta(days=1)
            end_date = today

            if start_date > end_date:
                print("NOOP: up-to-date")
                return

            baseline = get_last_complete_day_baseline(cur, latest_date)
            existing = existing_pairs(cur, start_date, end_date)

            rows_to_insert = []

            day = start_date
            while day <= end_date:
                values = generate_daily(day, baseline)

                for metric_key, metric_value in values.items():
                    if (day, metric_key) in existing:
                        continue

                    unit = METRICS[metric_key]["unit"]
                    ingestion_key = f"{SOURCE_TYPE}:{batch_id}:{FACILITY_CODE}:{day.isoformat()}:{metric_key}"

                    raw_record = {
                        "facility_code": FACILITY_CODE,
                        "facility_name": FACILITY_NAME,
                        "metric_date": day.isoformat(),
                        "metric_key": metric_key,
                        "metric_value": str(metric_value),
                        "metric_unit": unit,
                        "source_type": SOURCE_TYPE,
                        "source_name": SOURCE_NAME,
                    }

                    fingerprint_payload = {
                        "facility": FACILITY_NAME,
                        "metric_date": day.isoformat(),
                        "metric_key": metric_key,
                        "metric_value": str(metric_value),
                        "metric_unit": unit,
                        "source_type": SOURCE_TYPE,
                        "source_name": SOURCE_NAME,
                    }

                    record_fingerprint = build_record_fingerprint(fingerprint_payload)

                    rows_to_insert.append(
                        (
                            str(uuid.uuid4()),
                            ingestion_key,
                            batch_id,
                            SOURCE_TYPE,
                            SOURCE_NAME,
                            FACILITY_NAME,
                            day,
                            metric_key,
                            metric_value,
                            unit,
                            record_fingerprint,
                            json.dumps(raw_record, ensure_ascii=False),
                            inserted_at,
                        )
                    )

                day += timedelta(days=1)

            if not rows_to_insert:
                print("NOOP: nothing to insert")
                return

            insert_rows(cur, rows_to_insert)
            conn.commit()

            inserted_days = sorted({r[6] for r in rows_to_insert})
            print(f"BATCH_ID={batch_id}")
            print(f"INSERTED_ROWS={len(rows_to_insert)}")
            print(f"INSERTED_DAYS={len(inserted_days)}")
            print(f"DATE_RANGE={inserted_days[0]}..{inserted_days[-1]}")

if __name__ == "__main__":
    main()
