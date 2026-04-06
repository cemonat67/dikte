import os
from fastapi import FastAPI
import psycopg2
from fastapi.middleware.cors import CORSMiddleware

DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI(title="Zero@Hospital API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_conn():
    return psycopg2.connect(DATABASE_URL)


@app.get("/api/dashboard/clinic-highlights")
def clinic_highlights(facility_code: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                select
                    klinik_adi,
                    risk_score,
                    risk_seviyesi,
                    highlight_sirasi
                from zerocare_operational.vw_dashboard_clinic_highlights
                where facility_code = %s
                order by highlight_sirasi
            """, (facility_code,))
            rows = cur.fetchall()

    return [
        {
            "clinic": r[0],
            "risk_score": float(r[1]),
            "risk_level": r[2],
            "rank": r[3],
        }
        for r in rows
    ]


@app.get("/api/dashboard/clinic-daily")
def clinic_daily(facility_code: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                select
                    klinik_adi,
                    temiz_su_m3,
                    tibbi_atik_kg,
                    patolojik_atik_kg,
                    toplam_atik_kg
                from zerocare_operational.vw_dashboard_clinic_daily
                where facility_code = %s
                order by klinik_adi
            """, (facility_code,))
            rows = cur.fetchall()

    return [
        {
            "clinic": r[0],
            "water_m3": float(r[1] or 0),
            "medical_waste_kg": float(r[2] or 0),
            "pathological_waste_kg": float(r[3] or 0),
            "total_waste_kg": float(r[4] or 0),
        }
        for r in rows
    ]
