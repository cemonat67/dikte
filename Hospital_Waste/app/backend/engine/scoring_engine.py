import os
from typing import Dict, Any

import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL bulunamadı")
    return psycopg2.connect(database_url)


def load_thresholds(framework_code: str = "GREEN_HOSPITAL") -> Dict[str, Dict[str, Any]]:
    sql = """
    select
        indicator_code,
        unit,
        good_max,
        monitor_max,
        bad_max,
        weight,
        direction
    from zerocare_sustainability.indicator_thresholds
    where framework_code = %s
      and is_active = true
      and current_date >= effective_from
      and (effective_to is null or current_date <= effective_to)
      and indicator_code is not null
    order by indicator_code;
    """

    thresholds: Dict[str, Dict[str, Any]] = {}

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (framework_code,))
            rows = cur.fetchall()

    for row in rows:
        thresholds[row["indicator_code"]] = {
            "unit": row["unit"],
            "good": {"max": float(row["good_max"])},
            "monitor": {"max": float(row["monitor_max"])},
            "bad": {"max": float(row["bad_max"])},
            "weight": float(row["weight"]),
            "direction": row["direction"],
        }

    if not thresholds:
        raise RuntimeError(f"Threshold bulunamadı: framework_code={framework_code}")

    return thresholds


def get_status(value, threshold):
    if value <= threshold["good"]["max"]:
        return "good"
    elif value <= threshold["monitor"]["max"]:
        return "monitor"
    return "bad"


def normalize_score(value, threshold):
    good_max = threshold["good"]["max"]
    monitor_max = threshold["monitor"]["max"]
    bad_max = threshold["bad"]["max"]

    if value <= good_max:
        if good_max == 0:
            return 100.0
        return 80 + (20 * (good_max - value) / good_max)

    if value <= monitor_max:
        denom = (monitor_max - good_max) or 1
        return 40 + (40 * (monitor_max - value) / denom)

    if value <= bad_max:
        denom = (bad_max - monitor_max) or 1
        return 1 + (39 * (bad_max - value) / denom)

    return 0.0


def calculate_indicator(value, key, thresholds):
    threshold = thresholds[key]
    status = get_status(value, threshold)
    score = round(normalize_score(value, threshold), 2)

    return {
        "value": value,
        "unit": threshold.get("unit"),
        "status": status,
        "score": score
    }


def calculate_total(data, framework_code: str = "GREEN_HOSPITAL"):
    thresholds = load_thresholds(framework_code=framework_code)

    results = {}
    weighted_sum = 0.0
    used_weight = 0.0

    for key, value in data.items():
        if key not in thresholds:
            continue

        res = calculate_indicator(value, key, thresholds)
        results[key] = res

        weight = thresholds[key].get("weight", 0.0)
        weighted_sum += res["score"] * weight
        used_weight += weight

    total_score = round(weighted_sum / used_weight, 2) if used_weight > 0 else 0.0

    if total_score < 40:
        risk = "CRITICAL"
    elif total_score < 60:
        risk = "HIGH"
    elif total_score < 80:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {
        "framework_code": framework_code,
        "indicators": results,
        "total_score": total_score,
        "risk": risk
    }


def generate_summary(scoring_result):
    indicators = scoring_result.get("indicators", {})
    total_score = scoring_result.get("total_score", 0)

    # En kötü indicator
    worst = None
    worst_score = 999

    for k, v in indicators.items():
        if v["score"] < worst_score:
            worst_score = v["score"]
            worst = k

    # Quick action logic
    action_map = {
        "energy_kwh_per_bed": "Reduce energy intensity: optimize HVAC, lighting, equipment usage",
        "water_m3_per_bed": "Reduce water usage: fix leaks, optimize sterilization cycles",
        "waste_kg_per_bed": "Improve waste segregation and reduction practices"
    }

    return {
        "score": total_score,
        "risk": scoring_result.get("risk"),
        "top_issue": worst,
        "quick_action": action_map.get(worst, "Review sustainability indicators"),
    }
