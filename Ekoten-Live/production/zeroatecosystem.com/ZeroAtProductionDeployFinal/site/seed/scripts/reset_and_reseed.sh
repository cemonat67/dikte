#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-docker}"

if [ "$MODE" = "docker" ]; then
  PSQL_BASE='docker exec -i zerodesign-db psql -U postgres -d zero_design_co2'
else
  DB_URL="${DATABASE_URL:-postgresql://postgres@localhost:5432/zero_design_co2}"
  PSQL_BASE="psql \"$DB_URL\""
fi

echo "==> Truncating tables..."
eval $PSQL_BASE <<'SQL'
TRUNCATE TABLE emissions, accessories, fabrics, lifecycle_master, processes CASCADE;
SQL

echo "==> Re-seeding..."
./seed/scripts/bootstrap_zerodesign.sh "$MODE"

echo "==> Final verification..."
eval $PSQL_BASE -c "
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
