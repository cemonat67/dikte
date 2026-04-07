#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import psycopg


DEFAULT_SOURCE_SCRIPT = Path("scripts/bootstrap_zero_facilities.py")


@dataclass
class FacilityRow:
    facility_code: str
    facility_name: str | None
    facility_type: str | None
    bed_count: int | None
    gross_area_m2: float | None


@dataclass
class BackfillRunResult:
    facility_code: str
    metric_date: str
    action: str
    returncode: int
    write_status: str | None = None
    inserted_rows: int | None = None
    readiness_ready: bool | None = None
    staging_status: str | None = None
    promote_status: str | None = None
    dashboard_verify_status: str | None = None
    present_metric_count: int | None = None
    stderr: str | None = None
    summary: dict[str, Any] | None = None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Backfill last N calendar days for all active facilities using verified bootstrap layer."
    )
    p.add_argument("--days", type=int, default=30, help="Kaç takvim günü backfill edilsin. Varsayılan: 30")
    p.add_argument("--end-date", default=str(date.today()), help="Pencere bitiş tarihi (YYYY-MM-DD). Varsayılan: today")
    p.add_argument(
        "--facility-code",
        action="append",
        default=[],
        help="Tekil facility code. Birden fazla kez verilebilir. Verilmezse tüm aktif facility'ler seçilir.",
    )
    p.add_argument("--limit", type=int, default=None, help="Facility sayısını sınırla")
    p.add_argument("--dry-run", action="store_true", help="Subprocess çalıştırma, sadece plan göster")
    p.add_argument("--continue-on-error", action="store_true", help="Hata olsa da devam et")
    p.add_argument(
        "--source-script",
        default=str(DEFAULT_SOURCE_SCRIPT),
        help="Tek-facility verified bootstrap script yolu.",
    )
    return p.parse_args()


def parse_iso_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("ERROR: DATABASE_URL env yok.")
    return database_url


def connect_db(database_url: str):
    return psycopg.connect(database_url, prepare_threshold=None)


def discover_facilities(database_url: str, facility_codes: list[str]) -> list[FacilityRow]:
    sql = """
    select
        f.facility_code,
        f.facility_name,
        f.facility_type,
        f.bed_count,
        f.gross_area_m2
    from zerocare_operational.facilities f
    where f.is_active = true
      and (%s::text[] is null or f.facility_code = any(%s))
    order by f.facility_code
    """
    codes_param = facility_codes if facility_codes else None
    with connect_db(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (codes_param, codes_param))
            rows = cur.fetchall()

    found = [
        FacilityRow(
            facility_code=r[0],
            facility_name=r[1],
            facility_type=r[2],
            bed_count=r[3],
            gross_area_m2=float(r[4]) if r[4] is not None else None,
        )
        for r in rows
    ]

    if facility_codes:
        found_codes = {r.facility_code for r in found}
        missing = [c for c in facility_codes if c not in found_codes]
        if missing:
            raise SystemExit(f"ERROR: facility bulunamadı: {', '.join(missing)}")

    if not found:
        raise SystemExit("ERROR: aktif facility bulunamadı.")

    return found


def build_expected_dates(end_date: date, days: int) -> list[date]:
    start_date = end_date - timedelta(days=days - 1)
    return [start_date + timedelta(days=i) for i in range(days)]


def discover_missing_pairs(
    database_url: str,
    facility_codes: list[str],
    start_date: date,
    end_date: date,
) -> set[tuple[str, date]]:
    sql = """
    with facilities_scope as (
        select
            f.facility_code
        from zerocare_operational.facilities f
        where f.is_active = true
          and (%s::text[] is null or f.facility_code = any(%s))
    ),
    dates as (
        select generate_series(%s::date, %s::date, interval '1 day')::date as metric_date
    ),
    expected as (
        select fs.facility_code, d.metric_date
        from facilities_scope fs
        cross join dates d
    ),
    actual as (
        select distinct
            v.facility_code,
            v.metric_date
        from zerocare_operational.vw_dashboard_daily v
        where v.metric_date between %s::date and %s::date
          and (%s::text[] is null or v.facility_code = any(%s))
    )
    select
        e.facility_code,
        e.metric_date
    from expected e
    left join actual a
      on a.facility_code = e.facility_code
     and a.metric_date = e.metric_date
    where a.facility_code is null
    order by e.facility_code, e.metric_date
    """
    codes_param = facility_codes if facility_codes else None
    with connect_db(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    codes_param,
                    codes_param,
                    start_date,
                    end_date,
                    start_date,
                    end_date,
                    codes_param,
                    codes_param,
                ),
            )
            rows = cur.fetchall()

    return {(r[0], r[1]) for r in rows}


def build_single_facility_cmd(source_script: str, row: FacilityRow, metric_date: date) -> list[str]:
    if not row.facility_type:
        raise SystemExit(f"ERROR: facility_type boş: {row.facility_code}")

    cmd = [
        sys.executable,
        source_script,
        "--facility-code",
        row.facility_code,
        "--facility-type",
        row.facility_type,
        "--metric-date",
        metric_date.isoformat(),
    ]

    if row.gross_area_m2 is not None:
        cmd.extend(["--gross-area-m2", str(int(round(row.gross_area_m2)))])

    if row.bed_count is not None:
        cmd.extend(["--bed-count", str(row.bed_count)])

    if row.facility_name:
        cmd.extend(["--facility-name", row.facility_name])

    return cmd


def run_single(source_script: str, row: FacilityRow, metric_date: date, dry_run: bool) -> BackfillRunResult:
    if dry_run:
        return BackfillRunResult(
            facility_code=row.facility_code,
            metric_date=metric_date.isoformat(),
            action="DRY_RUN",
            returncode=0,
        )

    cmd = build_single_facility_cmd(source_script=source_script, row=row, metric_date=metric_date)

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    if proc.returncode != 0:
        return BackfillRunResult(
            facility_code=row.facility_code,
            metric_date=metric_date.isoformat(),
            action="FAILED",
            returncode=proc.returncode,
            stderr=stderr or stdout or "subprocess failed",
        )

    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return BackfillRunResult(
            facility_code=row.facility_code,
            metric_date=metric_date.isoformat(),
            action="FAILED",
            returncode=proc.returncode,
            stderr=f"JSON parse failed. stdout={stdout[:500]} stderr={stderr[:500]}",
        )

    write_result = payload.get("write_result", {}) or {}
    readiness = payload.get("readiness", {}) or {}
    dashboard_verify = payload.get("dashboard_verify", {}) or {}
    promote_result = payload.get("promote_result", {}) or {}

    inserted_rows = write_result.get("inserted_rows")
    write_status = write_result.get("status")
    readiness_ready = readiness.get("ready")
    staging_status = readiness.get("staging_status")
    promote_status = promote_result.get("promote_status")
    dashboard_verify_status = dashboard_verify.get("status")
    present_metric_count = dashboard_verify.get("present_metric_count")

    if inserted_rows == 0 and write_status in {"OK", "NOOP_ALREADY_BOOTSTRAPPED"}:
        action = "NOOP"
    elif (
        write_status == "OK"
        and readiness_ready is True
        and promote_status in {"SUCCESS", "NO_OP"}
        and dashboard_verify_status == "OK"
    ):
        action = "SUCCESS"
    else:
        action = "PARTIAL"

    return BackfillRunResult(
        facility_code=row.facility_code,
        metric_date=metric_date.isoformat(),
        action=action,
        returncode=proc.returncode,
        write_status=write_status,
        inserted_rows=inserted_rows,
        readiness_ready=readiness_ready,
        staging_status=staging_status,
        promote_status=promote_status,
        dashboard_verify_status=dashboard_verify_status,
        present_metric_count=present_metric_count,
        stderr=stderr or None,
        summary=payload,
    )


def aggregate(
    start_date: date,
    end_date: date,
    facilities: list[FacilityRow],
    missing_pairs: set[tuple[str, date]],
    results: list[BackfillRunResult],
    dry_run: bool,
) -> dict[str, Any]:
    counts = {
        "facility_count": len(facilities),
        "missing_pair_count": len(missing_pairs),
        "processed_pair_count": len(results),
        "success_count": sum(1 for r in results if r.action == "SUCCESS"),
        "noop_count": sum(1 for r in results if r.action == "NOOP"),
        "partial_count": sum(1 for r in results if r.action == "PARTIAL"),
        "failed_count": sum(1 for r in results if r.action == "FAILED"),
        "dry_run_count": sum(1 for r in results if r.action == "DRY_RUN"),
    }
    return {
        "status": "OK" if counts["failed_count"] == 0 else "PARTIAL",
        "mode": "BACKFILL_30DAY",
        "window": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
        "dry_run": dry_run,
        "summary": counts,
        "results": [asdict(r) for r in results],
    }


def main() -> None:
    args = parse_args()
    database_url = get_database_url()
    end_date = parse_iso_date(args.end_date)
    start_date = end_date - timedelta(days=args.days - 1)

    source_script = args.source_script
    if not Path(source_script).exists():
        raise SystemExit(f"ERROR: source script yok: {source_script}")

    facilities = discover_facilities(database_url, args.facility_code)
    if args.limit is not None:
        facilities = facilities[: args.limit]

    missing_pairs = discover_missing_pairs(
        database_url=database_url,
        facility_codes=[f.facility_code for f in facilities],
        start_date=start_date,
        end_date=end_date,
    )

    facility_map = {f.facility_code: f for f in facilities}
    ordered_pairs = sorted(missing_pairs, key=lambda x: (x[0], x[1]))

    results: list[BackfillRunResult] = []

    for facility_code, metric_date in ordered_pairs:
        row = facility_map[facility_code]
        result = run_single(
            source_script=source_script,
            row=row,
            metric_date=metric_date,
            dry_run=args.dry_run,
        )
        results.append(result)

        if result.action == "FAILED" and not args.continue_on_error:
            break

    payload = aggregate(
        start_date=start_date,
        end_date=end_date,
        facilities=facilities,
        missing_pairs=missing_pairs,
        results=results,
        dry_run=args.dry_run,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
