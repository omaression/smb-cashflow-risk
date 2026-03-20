#!/usr/bin/env bash
# Seed demo data against a remote (hosted) API.
# Usage: ./scripts/seed-remote.sh https://api.cashflow.omaression.com
set -euo pipefail

API_BASE="${1:?Usage: $0 <api-base-url>}"
API="${API_BASE}/api/v1"
DATA_DIR="$(cd "$(dirname "$0")/../data/raw" && pwd)"

echo "Seeding demo data against: ${API}"

for entity in customers invoices payments cash_snapshots; do
  file="${DATA_DIR}/sample_${entity}.csv"
  if [ ! -f "$file" ]; then
    echo "  SKIP ${entity} — file not found: ${file}"
    continue
  fi
  echo "  Loading ${entity}..."
  status=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "${API}/ingest/${entity}" \
    -H "Content-Type: text/csv" \
    --data-binary "@${file}")
  if [ "$status" -ge 200 ] && [ "$status" -lt 300 ]; then
    echo "    OK (${status})"
  else
    echo "    FAILED (${status})"
  fi
done

echo ""
echo "Done. Verify at: ${API}/dashboard/summary"
