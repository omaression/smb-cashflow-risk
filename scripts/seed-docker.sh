#!/usr/bin/env bash
set -euo pipefail
# Seed the running API with sample CSV data.
# Usage: ./scripts/seed-docker.sh [API_BASE_URL]
# Default: http://localhost:8000

API="${1:-http://localhost:8000}"
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
DATA_DIR="$ROOT_DIR/data/raw"

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required."
  exit 1
fi

echo "Seeding API at $API ..."
has_failures=false

for entity in customers invoices payments cash_snapshots; do
  file="$DATA_DIR/sample_${entity}.csv"
  if [[ ! -f "$file" ]]; then
    echo "  skip: $file not found"
    continue
  fi

  echo -n "  $entity ... "
  if ! resp=$(curl -sf -X POST "$API/api/v1/import/csv" \
    -F "entity_type=$entity" \
    -F "file=@$file"); then
    echo "FAIL"
    has_failures=true
    continue
  fi

  imported=$(printf '%s' "$resp" | grep -o '"imported":[0-9]*' | head -1 | cut -d: -f2)
  rejected=$(printf '%s' "$resp" | grep -o '"rejected":[0-9]*' | head -1 | cut -d: -f2)
  imported=${imported:-unknown}
  rejected=${rejected:-unknown}

  echo "imported=$imported rejected=$rejected"

  if [[ "$rejected" != "0" ]]; then
    has_failures=true
  fi
done

echo "Done."

if [[ "$has_failures" == true ]]; then
  exit 1
fi
