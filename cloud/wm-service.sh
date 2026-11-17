#!/usr/bin/env bash
# Start the watermarks-remover HTTP service on 127.0.0.1:8765 if it is not already up (the remove-ai-marks skill
# is a thin client over it). Idempotent; used by the cloud SessionStart hook and by the PC's user-level hook.
#   bash cloud/wm-service.sh
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
URL="${WATERMARKS_SERVICE_URL:-http://127.0.0.1:8765}"
curl -sf -m 2 "$URL/health" >/dev/null 2>&1 && exit 0
# Windows ships Store stubs named python/python3, so pick the first candidate that really runs Python 3.
PY=""; for c in python3 "py -3" python; do $c -c 'import sys; sys.exit(sys.version_info<(3,10))' >/dev/null 2>&1 && { PY=$c; break; }; done
[ -n "$PY" ] || { echo "WARN: no Python 3.10+ for the watermarks service"; exit 0; }
LOG="${TMPDIR:-/tmp}/watermarks-service.log"
nohup $PY "$ROOT/cloud/watermarks-remover/service/scripts/server.py" --host 127.0.0.1 --port 8765 >"$LOG" 2>&1 &
for _ in 1 2 3 4 5 6 7 8; do sleep 1; curl -sf -m 2 "$URL/health" >/dev/null 2>&1 && { echo "watermarks service up"; exit 0; }; done
echo "WARN: watermarks service did not start (see $LOG)"
