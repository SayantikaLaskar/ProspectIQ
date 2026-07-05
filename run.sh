#!/usr/bin/env bash
# Prospect IQ — one-command launcher (backend + frontend).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "▶ Prospect IQ — starting…"

# ---------- backend ----------
cd "$ROOT/backend"
if [ ! -d .venv ]; then
  echo "  · creating Python venv + installing backend deps (first run)"
  python3 -m venv .venv
  ./.venv/bin/pip install -q --upgrade pip
  ./.venv/bin/pip install -q -r requirements.txt
fi
./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level warning &
BACK=$!

# ---------- frontend ----------
cd "$ROOT/frontend"
if [ ! -d node_modules ]; then
  echo "  · installing frontend deps (first run)"
  npm install --no-audit --no-fund
fi
npm run dev -- --host 127.0.0.1 --port 5173 &
FRONT=$!

trap 'echo; echo "stopping…"; kill "$BACK" "$FRONT" 2>/dev/null || true' EXIT INT TERM

echo ""
echo "  ✓ backend  → http://localhost:8000/docs"
echo "  ✓ frontend → http://localhost:5173   (opens after model builds, ~15s)"
echo "  (Ctrl-C to stop both)"
wait
