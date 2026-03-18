#!/usr/bin/env bash
set -euo pipefail
# Seed the running API with sample CSV data.
# Usage: ./scripts/seed-docker.sh [API_BASE_URL]
# Default: http://localhost:8000

API="${1:-http://localhost:8000}"
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
DATA_DIR="$ROOT_DIR/data/raw"

echo "Seeding API at $API ..."

for entity in customers invoices payments cash_snapshots; do
  file="$DATA_DIR/sample_${entity}.csv"
  if [[ ! -f "$file" ]]; then
    echo "  skip: $file not found"
    continue
  fi
  echo -n "  $entity ... "
  resp=$(curl -sf -X POST "$API/api/v1/import/csv" \
    -F "entity_type=$entity" \
    -F "file=@$file" 2>&1) || { echo "FAIL"; echo "    $resp"; continue; }
  echo "$resp" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'imported={d[\"imported\"]} rejected={d[\"rejected\"]}')" 2>/dev/null || echo "$resp"
done

echo "Done."
