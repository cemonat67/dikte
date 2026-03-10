#!/usr/bin/env bash
set -euo pipefail

mkdir -p seed/exports

echo "==> Exporting CSV files from docker container..."

docker exec -i zerodesign-db psql -U postgres -d zero_design_co2 -c "\copy (SELECT * FROM processes ORDER BY process_name) TO STDOUT WITH CSV HEADER" > seed/exports/processes.csv
docker exec -i zerodesign-db psql -U postgres -d zero_design_co2 -c "\copy (SELECT * FROM emissions ORDER BY created_at, id) TO STDOUT WITH CSV HEADER" > seed/exports/emissions.csv
docker exec -i zerodesign-db psql -U postgres -d zero_design_co2 -c "\copy (SELECT * FROM lifecycle_master ORDER BY process_name) TO STDOUT WITH CSV HEADER" > seed/exports/lifecycle_master.csv
docker exec -i zerodesign-db psql -U postgres -d zero_design_co2 -c "\copy (SELECT * FROM fabrics ORDER BY fabric_type) TO STDOUT WITH CSV HEADER" > seed/exports/fabrics.csv
docker exec -i zerodesign-db psql -U postgres -d zero_design_co2 -c "\copy (SELECT * FROM accessories ORDER BY accessory_name) TO STDOUT WITH CSV HEADER" > seed/exports/accessories.csv

echo "==> Export complete."
ls -lah seed/exports
