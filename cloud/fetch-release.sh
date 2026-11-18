#!/usr/bin/env bash
# Download a source video the user attached to a GitHub release of this repo (cloud sessions).
# The repo is private and the Claude GitHub App can't be linked, so this uses $GH_TOKEN (never printed).
#   bash cloud/fetch-release.sh "<file name>" [tag=sources] [out dir=downloads]
#   bash cloud/fetch-release.sh --list [tag=sources]
# REPO=owner/name overrides the repo (used by the self-check against a public repo).
set -euo pipefail
REPO="${REPO:-gmacc616/ai-video-editor-private}"  # the release moved here when ai-video-editor went public (2026-11-17)
if [ "${1:-}" = "--list" ]; then NAME=""; TAG="${2:-sources}"; else NAME="${1:?usage: fetch-release.sh <file name> [tag] [out dir]}"; TAG="${2:-sources}"; fi
OUT="${3:-downloads}"
AUTH=(); [ -n "${GH_TOKEN:-}" ] && AUTH=(-H "Authorization: Bearer $GH_TOKEN")

json=$(curl -fsSL "${AUTH[@]}" -H "Accept: application/vnd.github+json" "https://api.github.com/repos/$REPO/releases/tags/$TAG") \
  || { echo "Can't read release '$TAG' of $REPO (is GH_TOKEN set and allowed to read Contents?)" >&2; exit 1; }
if [ -z "$NAME" ]; then printf '%s' "$json" | python3 -c 'import json,sys;[print(a["name"],a["size"]) for a in json.load(sys.stdin)["assets"]]'; exit 0; fi

# GitHub turns spaces/brackets into dots on upload ("videoplayback (1).mp4" -> "videoplayback.1.mp4"), so match loosely.
hit=$(printf '%s' "$json" | NAME="$NAME" python3 -c '
import json,os,re,sys
key=lambda s: re.sub(r"[^a-z0-9]","",s.lower())
want=key(os.environ["NAME"])
hits=[a for a in json.load(sys.stdin)["assets"] if key(a["name"])==want]
if hits: print(hits[0]["id"], hits[0]["name"], sep="/", end="")')
[ -n "$hit" ] || { echo "No file like '$NAME' in release '$TAG'. Files there:" >&2; bash "$0" --list "$TAG" >&2; exit 1; }
ID="${hit%%/*}"; ANAME="${hit#*/}"

mkdir -p "$OUT"
curl -fL --retry 3 "${AUTH[@]}" -H "Accept: application/octet-stream" -o "$OUT/$ANAME" \
  "https://api.github.com/repos/$REPO/releases/assets/$ID"
echo "saved $OUT/$ANAME ($(du -h "$OUT/$ANAME" | cut -f1))"
