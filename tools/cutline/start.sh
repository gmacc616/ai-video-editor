#!/usr/bin/env bash
# Start the Cutline editor + MCP server (one port serves the editor UI, the HTTP API and /mcp); idempotent.
#   bash tools/cutline/start.sh     -> editor at http://localhost:4100 ; log in output/cutline/server.log
# Bound to loopback with no token: the built UI's own JS/CSS requests carry no token, so token mode breaks --serve-web.
# Cutline's Host/Origin allowlist still blocks other sites. A preview proxy with its own hostname: set CUTLINE_ALLOWED_HOSTS.
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CL="$ROOT/vendor/cutline"; D="$ROOT/output/cutline"; PORT="${CUTLINE_PORT:-4100}"
[ -f "$CL/packages/mcp-server/dist/cli.js" ] || bash "$ROOT/tools/cutline/setup.sh"
mkdir -p "$D"
SETSID=$(command -v setsid || true)   # Git Bash on the PC has no setsid
if ! curl -fs "http://127.0.0.1:$PORT/api/health" >/dev/null 2>&1; then
  ( cd "$CL" && CUTLINE_DATA_DIR="$D/data" CUTLINE_MEDIA_ROOTS="$ROOT" DO_NOT_TRACK=1 \
    ${SETSID:-} nohup node packages/mcp-server/dist/cli.js --serve-web --host 127.0.0.1 --port "$PORT" > "$D/server.log" 2>&1 < /dev/null & )
  for _ in $(seq 30); do curl -fs "http://127.0.0.1:$PORT/api/health" >/dev/null 2>&1 && break; sleep 1; done
fi
curl -fs "http://127.0.0.1:$PORT/api/health" || { echo "Cutline failed to start; see $D/server.log"; tail -20 "$D/server.log"; exit 1; }
echo; echo "cutline editor: http://localhost:$PORT  (MCP: http://localhost:$PORT/mcp)"
