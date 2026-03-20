#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-v0.3.0}"
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT_DIR"

echo "Preparing release ${VERSION}..."

echo "[1/6] Running API tests"
(
  cd apps/api
  . .venv/bin/activate
  pytest -q
)

echo "[2/6] Running baseline evaluation"
(
  cd apps/api
  . .venv/bin/activate
  cd ../..
  python scripts/evaluate-baseline.py
)

echo "[3/6] Running project-native ML readiness"
(
  cd apps/api
  . .venv/bin/activate
  cd ../..
  python scripts/run-project-native-ml-baseline.py
)

echo "[4/6] Running external benchmark baselines"
(
  cd apps/api
  . .venv/bin/activate
  cd ../..
  python scripts/run-external-ml-baselines.py
)

echo "[5/6] Building web app"
(
  cd apps/web
  npm run build
)

echo "[6/6] Validating release docs"
for path in CHANGELOG.md docs/release-notes-v0.3.0.md docs/release-checklist-v0.3.0.md docs/demo-walkthrough.md; do
  test -f "$path"
done

echo
echo "Release prep checks passed for ${VERSION}."
echo "Next manual steps:"
echo "- merge remaining release PRs"
echo "- create git tag ${VERSION}"
echo "- publish GitHub Release using docs/release-notes-v0.3.0.md"
