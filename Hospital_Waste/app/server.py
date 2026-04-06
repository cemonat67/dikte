import os
from pathlib import Path
from typing import Optional, Any
from datetime import timedelta

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import psycopg
from backend.engine.scoring_engine import calculate_total, generate_summary
from backend.orchestration.facility_registry import resolve_facility_code, get_facility_context
from backend.orchestration.routing_engine import decide_route
from backend.orchestration.kpi_evaluator import evaluate_kpi_state

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8050"))

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Create app/.env from app/.env.example")

app = FastAPI(title="Zero@Hospital Local App", version="0.1.0")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def fetch_all(sql: str, params: Optional[tuple[Any, ...]] = None):
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params or ())
                cols = [desc.name for desc in cur.description]
                rows = cur.fetchall()
                return [dict(zip(cols, row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")


def fetch_one(sql: str, params: Optional[tuple[Any, ...]] = None):
    rows = fetch_all(sql, params)
    return rows[0] if rows else None


def execute_returning_one(sql: str, params: Optional[tuple[Any, ...]] = None):
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params or ())
                cols = [desc.name for desc in cur.description]
                row = cur.fetchone()
                conn.commit()
                return dict(zip(cols, row)) if row else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database write failed: {e}")


class HospitalIntakePayload(BaseModel):
    facility_code: str = "demo_hospital"
    hospital_name: str
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    facility_type: Optional[str] = None
    bed_count: Optional[int] = None
    employee_count: Optional[int] = None
    daily_patient_count: Optional[int] = None
    requested_modules: list[str] = []
    current_systems: Optional[str] = None
    priority_level: str = "normal"
    notes: Optional[str] = None
    source_channel: str = "dashboard"


def fill_gaps(rows: list[dict[str, Any]], days: int) -> list[dict[str, Any]]:
    if not rows:
        return []

    normalized = []
    for row in rows:
        x = dict(row)
        x["data_quality"] = "actual"
        normalized.append(x)

    data = {r["reading_date"]: r for r in normalized}
    all_dates = sorted(data.keys())
    max_date = max(all_dates)
    min_date = max_date - timedelta(days=days - 1)

    result = []
    last_known = None
    current = min_date

    while current <= max_date:
        if current in data:
            row = dict(data[current])
            last_known = dict(row)
        else:
            if last_known is None:
                current += timedelta(days=1)
                continue
            row = dict(last_known)
            row["reading_date"] = current
            row["last_seen_at"] = last_known.get("last_seen_at")
            row["data_quality"] = "estimated"

        result.append(row)
        current += timedelta(days=1)

    return sorted(result, key=lambda x: x["reading_date"], reverse=True)


@app.get("/")
def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():
    row = fetch_one("select now() as server_time")
    return {"status": "ok", "db": "connected", "server_time": row["server_time"] if row else None}


@app.get("/api/facilities")
def facilities():
    sql = """
    select
        facility_code as facility_id,
        facility_name
    from zerocare_operational.facilities
    order by facility_name
    """
    return fetch_all(sql)



@app.get("/api/dashboard/clinic-highlights")
def dashboard_clinic_highlights(
    facility_code: str = Query(..., description="Facility code"),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("rank"),
    sort_dir: str = Query("asc"),
):
    allowed_sort = {
        "rank": "rank",
        "risk_score": "risk_score",
        "clinic": "clinic",
        "risk_level": "risk_level",
    }
    order_col = allowed_sort.get(sort_by, "rank")
    order_dir = "DESC" if str(sort_dir).lower() == "desc" else "ASC"

    sql = f"""
        WITH ranked AS (
            SELECT
                h.klinik_adi AS clinic,
                COALESCE(h.risk_score, 0) AS risk_score,
                LOWER(COALESCE(h.risk_seviyesi, 'yesil')) AS risk_level,
                COALESCE(h.highlight_sirasi, 999999) AS rank,
                ROW_NUMBER() OVER (
                    PARTITION BY h.klinik_adi
                    ORDER BY COALESCE(h.highlight_sirasi, 999999) ASC,
                             COALESCE(h.risk_score, 0) DESC
                ) AS rn
            FROM zerocare_operational.vw_dashboard_clinic_highlights h
            WHERE LOWER(h.facility_name) = LOWER((
                SELECT d.facility_name
                FROM zerocare_operational.vw_dashboard_daily d
                WHERE LOWER(d.facility_code) = LOWER(%s)
                ORDER BY d.metric_date DESC
                LIMIT 1
            ))
        )
        SELECT clinic, risk_score, risk_level, rank
        FROM ranked
        WHERE rn = 1
        ORDER BY {order_col} {order_dir}, clinic ASC
        LIMIT %s
    """
    rows = fetch_all(sql, (facility_code, limit))
    return rows


@app.get("/api/dashboard/clinic-daily")
def dashboard_clinic_daily(
    facility_code: str = Query(..., description="Facility code"),
    days: int = Query(14, ge=1, le=365),
    clinic: str | None = Query(None),
    sort_by: str = Query("clinic"),
    sort_dir: str = Query("asc"),
):
    allowed_sort = {
        "clinic": "klinik_adi",
        "water_m3": "temiz_su_m3",
        "co2_kg": "co2_kg",
        "medical_waste_kg": "tibbi_atik_kg",
        "pathological_waste_kg": "patolojik_atik_kg",
        "total_waste_kg": "toplam_atik_kg",
    }
    order_col = allowed_sort.get(sort_by, "klinik_adi")
    order_dir = "DESC" if str(sort_dir).lower() == "desc" else "ASC"

    sql = f"""
        SELECT
            d.klinik_adi AS clinic,
            COALESCE(d.temiz_su_m3, 0) AS water_m3,
            COALESCE(d.co2_kg, 0) AS co2_kg,
            COALESCE(d.tibbi_atik_kg, 0) AS medical_waste_kg,
            COALESCE(d.patolojik_atik_kg, 0) AS pathological_waste_kg,
            COALESCE(d.toplam_atik_kg, 0) AS total_waste_kg
        FROM zerocare_operational.vw_dashboard_clinic_daily d
        WHERE LOWER(d.facility_code) = LOWER(%s)
          AND ((%s)::text IS NULL OR d.klinik_adi = (%s)::text)
          AND (
                d.metric_date >= CURRENT_DATE - ((%s::int) - 1)
                OR d.metric_date IS NULL
          )
        ORDER BY {order_col} {order_dir}, clinic ASC
    """
    rows = fetch_all(sql, (facility_code, clinic, clinic, days))
    return rows


@app.post("/api/intake")
def create_hospital_intake(payload: HospitalIntakePayload):
    sql = """
    INSERT INTO zerocare_operational.hospital_intake_requests (
        facility_code,
        hospital_name,
        contact_name,
        contact_title,
        contact_email,
        contact_phone,
        facility_type,
        bed_count,
        employee_count,
        daily_patient_count,
        requested_modules,
        current_systems,
        priority_level,
        notes,
        source_channel
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    RETURNING
        intake_id,
        facility_code,
        hospital_name,
        contact_name,
        contact_title,
        contact_email,
        contact_phone,
        facility_type,
        bed_count,
        employee_count,
        daily_patient_count,
        requested_modules,
        current_systems,
        priority_level,
        notes,
        intake_status,
        source_channel,
        created_at,
        updated_at
    """
    row = execute_returning_one(
        sql,
        (
            payload.facility_code,
            payload.hospital_name,
            payload.contact_name,
            payload.contact_title,
            payload.contact_email,
            payload.contact_phone,
            payload.facility_type,
            payload.bed_count,
            payload.employee_count,
            payload.daily_patient_count,
            payload.requested_modules,
            payload.current_systems,
            payload.priority_level,
            payload.notes,
            payload.source_channel,
        ),
    )
    return {"status": "ok", "intake": row}



@app.get("/api/dashboard/latest")
def dashboard_latest(
    facility_id: Optional[str] = Query(default=None),
    facility_code: Optional[str] = Query(default=None),
):
    facility_key = resolve_facility_code(facility_id, facility_code)

    def attach_sustainability_scoring(rows):
        enriched = []

        for r in rows:
            r["facility_context"] = get_facility_context(facility_code=r.get("facility_code"))
            bed_count = r.get("bed_count")
            try:
                bed_count_value = float(bed_count) if bed_count is not None else None
            except (TypeError, ValueError):
                bed_count_value = None

            total_waste_kg = float(r.get("medical_waste_kg") or 0) + float(r.get("pathological_waste_kg") or 0) + float(r.get("general_waste_kg") or 0)

            if not bed_count_value or bed_count_value <= 0:
                r["sustainability_scoring"] = {
                    "framework_code": "GREEN_HOSPITAL",
                    "status": "score_pending_bed_count_missing",
                    "bed_count": bed_count,
                }
                enriched.append(r)
                continue

            scoring_input = {
                "energy_kwh_per_bed": round(float(r.get("energy_kwh") or 0) / bed_count_value, 4),
                "water_m3_per_bed": round(float(r.get("water_m3") or 0) / bed_count_value, 4),
                "waste_kg_per_bed": round(total_waste_kg / bed_count_value, 4),
            }

            scoring = calculate_total(scoring_input, framework_code="GREEN_HOSPITAL")
            scoring["bed_count"] = bed_count_value
            scoring["derived_inputs"] = scoring_input
            scoring["summary"] = generate_summary(scoring)
            r["sustainability_scoring"] = scoring
            enriched.append(r)

        return enriched

    if facility_key:
        sql = """
        select
            d.facility_code,
            d.facility_name as facility,
            d.metric_date as reading_date,
            d.electricity_kwh as energy_kwh,
            d.water_m3,
            d.medical_waste_kg,
            d.pathological_waste_kg,
            d.general_waste_kg,
            d.scope2_location_tco2e,
            d.waste_cost_try,
            f.bed_count,
            'actual' as data_quality
        from zerocare_operational.vw_dashboard_daily d
        left join zerocare_operational.facilities f
          on f.facility_code = d.facility_code
        where d.facility_code = %s
          and d.metric_date = (
              select max(metric_date)
              from zerocare_operational.vw_dashboard_daily
              where facility_code = %s
          )
        order by reading_date desc, facility
        """
        rows = fetch_all(sql, (facility_key, facility_key))
        return attach_sustainability_scoring(rows)

    sql = """
    select
        d.facility_code,
        d.facility_name as facility,
        d.metric_date as reading_date,
        d.electricity_kwh as energy_kwh,
        d.water_m3,
        d.medical_waste_kg,
        d.pathological_waste_kg,
        d.general_waste_kg,
        d.scope2_location_tco2e,
        d.waste_cost_try,
        f.bed_count,
        'actual' as data_quality
    from zerocare_operational.vw_dashboard_daily d
    left join zerocare_operational.facilities f
      on f.facility_code = d.facility_code
    where d.metric_date = (
        select max(metric_date)
        from zerocare_operational.vw_dashboard_daily
    )
    order by facility, reading_date desc
    """
    rows = fetch_all(sql)
    return attach_sustainability_scoring(rows)


@app.get("/api/dashboard/daily")
def dashboard_daily(
    facility_id: Optional[str] = Query(default=None),
    facility_code: Optional[str] = Query(default=None),
    days: int = Query(default=14, ge=1, le=90)
):
    facility_key = resolve_facility_code(facility_id, facility_code)

    if facility_key:
        sql = """
        select
            facility_code,
            facility_name as facility,
            metric_date as reading_date,
            electricity_kwh as energy_kwh,
            water_m3,
            medical_waste_kg,
            pathological_waste_kg,
            general_waste_kg,
            scope2_location_tco2e,
            waste_cost_try,
            'actual' as data_quality
        from zerocare_operational.vw_dashboard_daily
        where facility_code = %s
          and metric_date >= (
              select max(metric_date) - (%s::int - 1)
              from zerocare_operational.vw_dashboard_daily
              where facility_code = %s
          )
        order by reading_date desc, facility
        """
        rows = fetch_all(sql, (facility_key, days, facility_key))
        return fill_gaps(rows, days)

    sql = """
    select
        facility_code,
        facility_name as facility,
        metric_date as reading_date,
        electricity_kwh as energy_kwh,
        water_m3,
        medical_waste_kg,
        pathological_waste_kg,
        general_waste_kg,
        scope2_location_tco2e,
        waste_cost_try,
        'actual' as data_quality
    from zerocare_operational.vw_dashboard_daily
    where metric_date >= (
        select max(metric_date) - (%s::int - 1)
        from zerocare_operational.vw_dashboard_daily
    )
    order by reading_date desc, facility
    """
    rows = fetch_all(sql, (days,))
    return fill_gaps(rows, days)


@app.get("/api/facility-summary")
def facility_summary(
    facility_id: Optional[str] = Query(default=None),
    facility_code: Optional[str] = Query(default=None),
):
    facility_key = resolve_facility_code(facility_id, facility_code)

    if facility_key:
        sql = """
        select *
        from zerocare_operational.vw_facility_summary
        where facility_code = %s
        order by facility_name
        """
        return fetch_all(sql, (facility_key,))
    sql = """
    select *
    from zerocare_operational.vw_facility_summary
    order by facility_name
    """
    return fetch_all(sql)


@app.get("/api/executive/context")
def executive_context(
    facility_id: Optional[str] = Query(default=None),
    facility_code: Optional[str] = Query(default=None),
):
    facility_key = resolve_facility_code(facility_id, facility_code)

    summary_rows = fetch_all(
        """
        select *
        from zerocare_operational.vw_facility_summary
        where (%s is null or facility_code = %s)
        order by facility_name
        """,
        (facility_key, facility_key),
    )

    latest_rows = fetch_all(
        """
        select *
        from zerocare_operational.vw_dashboard_latest
        where (%s is null or facility_code = %s)
        order by facility_name, metric_code
        """,
        (facility_key, facility_key),
    )

    return {
        "scope": facility_key or "all",
        "facility_summary": summary_rows,
        "latest_metrics": latest_rows[:50],
        "ai_policy": {
            "use_for": [
                "executive summaries",
                "anomaly explanations",
                "short decision support",
                "report phrasing"
            ],
            "never_use_for": [
                "kpi calculations",
                "co2 calculations",
                "raw joins",
                "deterministic business logic"
            ]
        }
    }



@app.get("/api/clinics")
def clinics(facility_code: str):
    rows = fetch_all(
        '''
        select clinic_name,
               sum(production_kg) as production_kg,
               sum(energy_kwh) as energy_kwh,
               sum(co2_kg) as co2_kg
        from zerocare_operational.vw_dashboard_daily
        where facility_code = %s
        group by clinic_name
        order by co2_kg desc
        ''',
        (facility_code,)
    )
    return rows


@app.get("/api/orchestration/summary")
def orchestration_summary(
    facility_id: Optional[str] = Query(default=None),
    facility_code: Optional[str] = Query(default=None),
    days: int = Query(default=14, ge=1, le=90),
):
    facility_key = resolve_facility_code(facility_id, facility_code)
    facility_context = get_facility_context(facility_code=facility_key)

    latest_rows = dashboard_latest(facility_id=None, facility_code=facility_key)
    latest = latest_rows[0] if latest_rows else None

    daily_rows = dashboard_daily(facility_id=None, facility_code=facility_key, days=days)

    estimated_days = sum(1 for r in daily_rows if r.get("data_quality") == "estimated")
    quality_ratio = estimated_days / len(daily_rows) if daily_rows else 0

    energy_values = [float(r.get("energy_kwh")) for r in daily_rows if r.get("energy_kwh") is not None]
    energy_trend = "stable"
    if len(energy_values) >= 2:
        if energy_values[0] > energy_values[-1] * 1.1:
            energy_trend = "increasing"
        elif energy_values[0] < energy_values[-1] * 0.9:
            energy_trend = "decreasing"

    kpi_evaluation = evaluate_kpi_state(
        latest_row=latest,
        quality_ratio=quality_ratio,
        energy_trend=energy_trend,
    )

    routing_decision = decide_route(
        facility_context=facility_context,
        latest_row=latest,
        quality_ratio=quality_ratio,
        energy_trend=energy_trend,
    )

    ai = ai_summary(facility_code=facility_key, days=days)

    return {
        "facility": facility_context,
        "latest": latest,
        "kpi_evaluation": kpi_evaluation,
        "routing_decision": routing_decision,
        "ai_summary": {
            "overall_status": ai.get("overall_status"),
            "comment": ai.get("comment"),
            "recommended_action": ai.get("recommended_action"),
        },
        "meta": {
            "days": days,
            "quality_ratio": round(quality_ratio, 2),
            "version": "orchestration_v1",
        },
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host=APP_HOST, port=APP_PORT, reload=True)

@app.get("/api/ai/summary")
def ai_summary(
    facility_code: Optional[str] = Query(default=None),
    days: int = Query(default=14)
):
    facility_key = resolve_facility_code(None, facility_code)
    facility_context = get_facility_context(facility_code=facility_key)

    # latest snapshot
    latest_rows = dashboard_latest(facility_id=None, facility_code=facility_key)
    if not latest_rows:
        return {
            "facility": facility_key,
            "facility_context": facility_context,
            "overall_status": "NO_DATA",
            "comment": "No data available for analysis",
            "recommended_action": "Check data pipeline",
            "routing_decision": {
                "route": "no_data_pipeline_check",
                "priority": "high",
                "persona": "operations",
                "reason": "no_latest_data",
            },
            "kpi_evaluation": {
                "severity": "no_data",
                "quality_ratio": None,
                "energy_trend": "unknown",
                "scoring_risk": None,
                "scoring_status": "no_data",
                "top_issue": None,
                "quick_action": "Check data pipeline",
            },
        }

    latest = latest_rows[0]

    # daily trend
    daily_rows = dashboard_daily(facility_id=None, facility_code=facility_key, days=days)

    # --- RULES ---

    # data quality check
    estimated_days = sum(1 for r in daily_rows if r.get("data_quality") == "estimated")
    quality_ratio = estimated_days / len(daily_rows) if daily_rows else 0

    # energy trend check
    energy_values = [float(r.get("energy_kwh")) for r in daily_rows if r.get("energy_kwh") is not None]
    energy_trend = "stable"
    if len(energy_values) >= 2:
        if energy_values[0] > energy_values[-1] * 1.1:
            energy_trend = "increasing"
        elif energy_values[0] < energy_values[-1] * 0.9:
            energy_trend = "decreasing"

    kpi_evaluation = evaluate_kpi_state(
        latest_row=latest,
        quality_ratio=quality_ratio,
        energy_trend=energy_trend,
    )

    severity = kpi_evaluation.get("severity")

    if severity == "low_confidence":
        overall_status = "LOW_CONFIDENCE"
        comment = "Data reliability is low due to high estimated data ratio."
        action = "Investigate missing data sources."
    elif severity in {"critical", "high", "monitor"}:
        overall_status = "RISK"
        comment = "KPI pattern indicates elevated sustainability attention is required."
        action = kpi_evaluation.get("quick_action") or "Review operational efficiency and recent changes."
    elif severity == "context_missing":
        overall_status = "CONTEXT_MISSING"
        comment = "Scoring context is incomplete due to missing facility capacity data."
        action = "Complete facility bed count and baseline context."
    else:
        overall_status = "STABLE"
        comment = "System is operating within expected parameters."
        action = "Continue monitoring."

    routing_decision = decide_route(
        facility_context=facility_context,
        latest_row=latest,
        quality_ratio=quality_ratio,
        energy_trend=energy_trend,
    )

    return {
        "facility": facility_key,
        "facility_context": facility_context,
        "overall_status": overall_status,
        "data_quality_ratio": round(quality_ratio, 2),
        "energy_trend": energy_trend,
        "kpi_evaluation": kpi_evaluation,
        "routing_decision": routing_decision,
        "comment": comment,
        "recommended_action": action
    }

