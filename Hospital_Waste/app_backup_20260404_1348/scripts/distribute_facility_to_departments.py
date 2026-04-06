import os

try:
    import psycopg
except Exception:
    import psycopg2 as psycopg

DATABASE_URL = os.getenv("DATABASE_URL")
FACILITY_NAME = "Bazekol Çiğli Hastanesi"

DISTRIBUTION = {
    "Genel Cerrahi": 0.30,
    "Kalp Damar": 0.25,
    "Onkoloji": 0.20,
    "Ortopedi": 0.25,
}

if not DATABASE_URL:
    raise SystemExit("DATABASE_URL yok")


def connect():
    return psycopg.connect(DATABASE_URL)


def main():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select facility_id
                from zerocare_operational.facilities
                where facility_name = %s
                """,
                (FACILITY_NAME,),
            )
            row = cur.fetchone()
            if not row:
                raise SystemExit(f"Facility bulunamadı: {FACILITY_NAME}")
            facility_id = row[0]

            cur.execute(
                """
                select department_id, department_name_tr
                from zerocare_operational.departments
                where facility_id = %s
                order by department_name_tr
                """,
                (facility_id,),
            )
            dept_rows = cur.fetchall()
            dept_map = {name: dept_id for dept_id, name in dept_rows}

            missing_departments = [name for name in DISTRIBUTION if name not in dept_map]
            if missing_departments:
                raise SystemExit("Departman eksik: " + ", ".join(missing_departments))

            cur.execute(
                """
                select
                    facility_id,
                    metric_date,
                    metric_code,
                    sum(value) as value,
                    unit_code,
                    coalesce(max(quality_flag), 'derived') as quality_flag,
                    coalesce(max(calculation_method), 'department_distribution_v1') as calculation_method,
                    coalesce(max(source_system), 'derived') as source_system
                from zerocare_operational.daily_metrics
                where facility_id = %s
                  and department_id is null
                group by facility_id, metric_date, metric_code, unit_code
                order by metric_date, metric_code
                """,
                (facility_id,),
            )
            base_rows = cur.fetchall()

            if not base_rows:
                raise SystemExit("Dağıtılacak facility-level satır bulunamadı")

            metric_dates = sorted({r[1] for r in base_rows})

            cur.execute(
                """
                delete from zerocare_operational.daily_metrics
                where facility_id = %s
                  and department_id is not null
                  and metric_date = any(%s)
                """,
                (facility_id, metric_dates),
            )

            inserts = []
            for (
                facility_id,
                metric_date,
                metric_code,
                value,
                unit_code,
                quality_flag,
                calculation_method,
                source_system,
            ) in base_rows:
                for dept_name, ratio in DISTRIBUTION.items():
                    department_id = dept_map[dept_name]
                    new_value = round(float(value) * ratio, 4)

                    inserts.append(
                        (
                            facility_id,
                            department_id,
                            metric_date,
                            metric_code,
                            new_value,
                            unit_code,
                            "derived",
                            f"{calculation_method}+department_distribution_v1",
                            source_system,
                        )
                    )

            cur.executemany(
                """
                insert into zerocare_operational.daily_metrics
                (
                    facility_id,
                    department_id,
                    metric_date,
                    metric_code,
                    value,
                    unit_code,
                    quality_flag,
                    calculation_method,
                    source_system
                )
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                inserts,
            )

            print(f"{len(inserts)} satır yazıldı")

if __name__ == "__main__":
    main()
