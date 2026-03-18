#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
API_DIR="$ROOT_DIR/apps/api"
WEB_DIR="$ROOT_DIR/apps/web"

cat <<'EOF'
SMB Cash Flow Risk demo flow
1. Start the API
2. Start the web dashboard
3. Open the dashboard and API docs
EOF

echo
echo "API:"
echo "  cd $API_DIR"
echo "  python3 -m venv .venv && source .venv/bin/activate"
echo "  pip install -r requirements.txt"
echo "  uvicorn app.main:app --reload"
echo
echo "Web:"
echo "  cd $WEB_DIR"
echo "  npm install"
echo "  NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1 npm run dev"
echo
echo "Open:"
echo "  Dashboard  -> http://127.0.0.1:3000"
echo "  API docs   -> http://127.0.0.1:8000/docs"
