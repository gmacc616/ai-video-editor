#!/usr/bin/env bash
# Install Cutline (MIT, github.com/Aepzie/cutline) into vendor/cutline at a pinned commit and build it; idempotent.
# Cutline = browser timeline editor + MCP server; the agent lays out the edit, the user reviews it, ffmpeg renders on the server.
#   bash tools/cutline/setup.sh
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CL="$ROOT/vendor/cutline"
PIN="ab71520285881d8dfa78f5ebca00f8a166e84962"   # 2026-10-16 (reviewed: no install hooks beyond husky); bump deliberately
command -v ffmpeg >/dev/null || { echo "ffmpeg missing"; exit 1; }
[ "$(node -p 'process.versions.node.split(".")[0]')" -ge 22 ] || { echo "Cutline needs Node 22+"; exit 1; }

if [ ! -d "$CL/.git" ]; then mkdir -p "$ROOT/vendor"; git clone -q https://github.com/Aepzie/cutline.git "$CL"; fi
if [ "$(git -C "$CL" rev-parse HEAD)" != "$PIN" ]; then
  git -C "$CL" fetch -q --depth 1 origin "$PIN" && git -C "$CL" -c advice.detachedHead=false checkout -q "$PIN"
fi
cd "$CL"; export TURBO_TELEMETRY_DISABLED=1 DO_NOT_TRACK=1
command -v pnpm >/dev/null || npm i -g pnpm@10 --silent
HUSKY=0 pnpm install --frozen-lockfile --silent
[ -f apps/web/dist/index.html ] && [ -f packages/mcp-server/dist/cli.js ] || pnpm build >/dev/null
echo "cutline ready: bash tools/cutline/start.sh"
