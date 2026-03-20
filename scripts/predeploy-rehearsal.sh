#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT_DIR"

log() {
  echo "[$(date +"%F %T")] $*"
}

log "Pre-deploy rehearsal start"

log "Bringing Docker stack up (build+start)"
docker compose up -d --build

log "Waiting for API health endpoint"
for _ in $(seq 1 45); do
  if curl -fsS http://localhost:8000/healthz >/dev/null 2>&1; then
    break
  fi
  sleep 2
done
curl -fsS http://localhost:8000/healthz >/dev/null

log "Seeding demo data"
./scripts/seed-docker.sh

log "Checking dashboard summary payload"
python3 - <<'PY'
import json
import urllib.request

url = 'http://localhost:8000/api/v1/dashboard/summary'
with urllib.request.urlopen(url, timeout=10) as resp:
    data = json.load(resp)

required = {'open_invoice_count', 'risky_invoice_count', 'total_ar'}
missing = required - set(data)
if missing:
    raise SystemExit(f"Summary payload missing fields: {sorted(missing)}")

print(json.dumps({k: data[k] for k in sorted(required)}))
PY

log "Running frontend smoke requests"
for url in \
  "http://localhost:3000" \
  "http://localhost:8000/docs"; do
  curl -fsS "$url" >/dev/null
  echo "OK: $url"
done

log "Running regression suite"
cd apps/api
. .venv/bin/activate
pytest -q
cd "$ROOT_DIR"

log "Running frontend build"
cd apps/web
npm run build
cd "$ROOT_DIR"

log "Preparing release artifacts"
./scripts/prepare-release.sh v0.3.0

log "Pre-deploy rehearsal completed"
