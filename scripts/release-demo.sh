#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT_DIR"

echo "[1/3] Starting Docker stack..."
docker compose up --build -d

echo "[2/3] Waiting for API health..."
for _ in $(seq 1 30); do
  if curl -fsS http://localhost:8000/healthz >/dev/null 2>&1; then
    break
  fi
  sleep 2
done
curl -fsS http://localhost:8000/healthz >/dev/null

echo "[3/3] Seeding demo data..."
./scripts/seed-docker.sh

echo
echo "Demo ready:"
echo "- Web:      http://localhost:3000"
echo "- API docs: http://localhost:8000/docs"
echo "- Summary:  http://localhost:8000/api/v1/dashboard/summary"
