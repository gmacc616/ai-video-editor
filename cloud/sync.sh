#!/usr/bin/env bash
# Run on the Windows PC before pushing: copies the user-level custom skills and Claude's project memory
# into cloud/ so cloud sessions get the same workflow. Locally nothing changes (Claude still reads ~/.claude/skills).
#   bash cloud/sync.sh
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS="cleanup-project commentary-short gab puregrit viral-shorts youtube-style-clip cartoon-audio-short cartoon-3d-short 3d-short"
mkdir -p "$ROOT/cloud/skills" "$ROOT/cloud/memory"
for s in $SKILLS; do
  [ -d "$HOME/.claude/skills/$s" ] || { echo "missing ~/.claude/skills/$s"; exit 1; }
  mkdir -p "$ROOT/cloud/skills/$s"
  cp -r "$HOME/.claude/skills/$s/." "$ROOT/cloud/skills/$s/"
done
# Watermarks-remover plugin (user-scoped on the PC): refresh the vendored skills + service the cloud uses.
WM=$(ls -d "$HOME"/.claude/plugins/cache/watermarks-remover/watermarks-remover/*/ 2>/dev/null | tail -1)
if [ -n "$WM" ]; then
  W="$ROOT/cloud/watermarks-remover"; rm -rf "$W/skills" "$W/service/scripts"; mkdir -p "$W/service"
  cp -r "$WM/skills" "$W/skills"; cp -r "$WM/service/scripts" "$W/service/scripts"
  rm -f "$W"/service/scripts/bench_* "$W"/service/scripts/*.ps1 "$W"/service/scripts/setup_* "$W"/service/scripts/requirements-* "$W"/service/scripts/synthid_* "$W"/service/scripts/markdiffusion_harness.py "$W"/service/scripts/clean_ctrlregen.py
  find "$W" -name __pycache__ -prune -exec rm -rf {} +
fi
MEM="$HOME/.claude/projects/C--Users-manth-OneDrive-Desktop-AI-Video-Editor/memory"
cp "$MEM"/*.md "$ROOT/cloud/memory/"
# Global working rules (~/.claude/CLAUDE.md, the Karpathy guidelines); RTK is local-only, so its include is dropped.
grep -v '^@RTK.md' "$HOME/.claude/CLAUDE.md" > "$ROOT/cloud/global-claude.md"
echo "synced: $(ls "$ROOT/cloud/skills" | wc -l) skills, $(ls "$ROOT/cloud/memory" | wc -l) memory files"
