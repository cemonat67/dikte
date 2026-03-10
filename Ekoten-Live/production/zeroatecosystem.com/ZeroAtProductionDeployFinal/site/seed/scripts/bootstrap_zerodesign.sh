#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-docker}"

run_sql_file() {
  local file="$1"

  if [ ! -f "$file" ]; then
    echo "ERROR: SQL file not found: $file" >&2
    exit 1
  fi

  if [ "$MODE" = "docker" ]; then
    docker exec -i zerodesign-db psql -U postgres -d zero_design_co2 < "$file"
  else
    DB_URL="${DATABASE_URL:-postgresql://postgres@localhost:5432/zero_design_co2}"
    psql "$DB_URL" < "$file"
  fi
}

run_sql_cmd() {
  local sql="$1"

  if [ "$MODE" = "docker" ]; then
    docker exec -i zerodesign-db psql -U postgres -d zero_design_co2 -c "$sql"
  else
    DB_URL="${DATABASE_URL:-postgresql://postgres@localhost:5432/zero_design_co2}"
    psql "$DB_URL" -c "$sql"
  fi
}

echo "==> Loading master seeds..."
run_sql_file "seed/sql/001_processes.sql"
run_sql_file "seed/sql/002_emissions.sql"
run_sql_file "seed/sql/003_lifecycle_master.sql"

echo "==> Loading domain seeds..."
run_sql_file "seed/sql/004_fabrics.sql"
run_sql_file "seed/sql/005_accessories.sql"

echo "==> Verifying row counts..."
run_sql_cmd "
SELECT 'processes' AS table_name, COUNT(*) AS rows FROM processes
UNION ALL
SELECT 'emissions', COUNT(*) FROM emissions
UNION ALL
SELECT 'lifecycle_master', COUNT(*) FROM lifecycle_master
UNION ALL
SELECT 'fabrics', COUNT(*) FROM fabrics
UNION ALL
SELECT 'accessories', COUNT(*) FROM accessories;
"

echo "==> Done."
