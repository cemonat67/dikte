#!/usr/bin/env bash
set -euo pipefail

CSV_PATH="${1:-data/synthetic/synthetic_garment_dataset.csv}"

if [ ! -f "$CSV_PATH" ]; then
  echo "ERROR: CSV file not found: $CSV_PATH" >&2
  exit 1
fi

echo "==> Resetting synthetic_garments..."
docker exec -i zerodesign-db psql -U postgres -d zero_design_co2 <<'SQL'
TRUNCATE TABLE synthetic_garments;
SQL

echo "==> Importing CSV: $CSV_PATH"
docker exec -i zerodesign-db psql -U postgres -d zero_design_co2 -c "\copy synthetic_garments(
sku_code,
gender,
category,
product,
fabric_type,
composition,
gsm_range,
garment_weight_kg,
accessory_profile,
process_profile,
fabric_co2_factor_kg_per_kg,
accessory_co2_kg,
process_co2_kg,
estimated_total_co2_kg,
data_source
) FROM STDIN WITH CSV HEADER" < "$CSV_PATH"

echo "==> Verifying import..."
docker exec -it zerodesign-db psql -U postgres -d zero_design_co2 -c "SELECT COUNT(*) FROM synthetic_garments;"
