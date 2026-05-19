#!/usr/bin/env bash
set -euo pipefail

echo "=== Zero@Trust Repository Validation ==="

echo
echo "1) Git root:"
git rev-parse --show-toplevel

echo
echo "2) Git status:"
git status --short

echo
echo "3) Required files:"
required_files=(
  "README.md"
  "SESSION_STATE.md"
  "frontend/index.html"
  "frontend/script.js"
  "frontend/style.css"
  "backend/main.py"
  "docker-compose.yml"
  "docker-compose.prod.yml"
)

for file in "${required_files[@]}"; do
  if [ -f "$file" ]; then
    echo "OK  $file"
  else
    echo "MISSING  $file"
    exit 1
  fi
done

echo
echo "4) Python syntax check:"
python3 -m py_compile backend/main.py

echo
echo "5) Frontend sanity check:"
grep -q "<html" frontend/index.html && echo "OK  frontend/index.html contains HTML root"
grep -q "Zero@Trust" README.md && echo "OK  README contains product name"

echo
echo "Validation complete."
