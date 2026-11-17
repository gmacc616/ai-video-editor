#!/usr/bin/env bash
# Workspace wiring for a cloud session (fast, no installs): links the skills, copies Claude's memory and writes a
# pointer to the repo. Run by the environment's SessionStart hook after the repo is cloned/pulled, and by cloud-setup.sh.
#   bash cloud/session-start.sh
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Private companions (gmacc616/<repo>-private, 2026-11-17): licensed SFX, campaign briefs, the voice reference, notes and
# memory that must not be public. Cloned next to the public repo and linked into place (gitignored there). Commit
# changes to these paths in the -private clone; the session needs GitHub access to the -private repos.
link_private() {  # <public root> <private repo> <path>...
  local pub="$1" priv; priv="$(dirname "$1")/$2"
  if [ -d "$priv/.git" ]; then git -C "$priv" pull -q --ff-only || echo "WARN: $2 pull failed"
  else git clone -q --depth 1 "https://github.com/gmacc616/$2.git" "$priv" || { echo "WARN: $2 clone failed: its private files are missing this session"; return; }; fi
  shift 2
  for p in "$@"; do
    [ -e "$priv/$p" ] || continue
    [ -e "$pub/$p" ] && [ ! -L "$pub/$p" ] && continue   # never replace a real file or folder
    mkdir -p "$(dirname "$pub/$p")" && ln -sfn "$priv/$p" "$pub/$p"
  done
}
link_private "$ROOT" ai-video-editor-private "sound effects" assets/gab cloud/memory cloud/skills/gab \
  cloud/skills/default-voice/voice .claude/commands/boxabl.md data/youtube docs/brezscales-account-setup.md prompts

# Skills: HyperFrames skills (.agents/skills), custom workflow skills (cloud/skills) and project skills, linked into
# the repo's .claude/skills and the user-level ~/.claude/skills so they load from any folder (sessions start in /home/user).
mkdir -p "$ROOT/.claude/skills" "$HOME/.claude/skills"
for d in "$ROOT"/.agents/skills/* "$ROOT"/cloud/skills/* "$ROOT"/cloud/watermarks-remover/skills/* "$ROOT"/.claude/skills/*; do
  n=$(basename "$d")
  [ -e "$ROOT/.claude/skills/$n" ] || ln -s "$d" "$ROOT/.claude/skills/$n"
  [ -e "$HOME/.claude/skills/$n" ] || ln -s "$(readlink -f "$d")" "$HOME/.claude/skills/$n"
done

# Watermark remover (remove-ai-marks, clean-user-facing-text): skills are linked above; the first is a thin client over a
# local HTTP service, so install its optional system tools (best effort) and start it every session.
command -v exiftool >/dev/null 2>&1 && command -v qpdf >/dev/null 2>&1 || { SUDO=""; [ "$(id -u)" = 0 ] || SUDO="sudo"; $SUDO apt-get install -y -qq libimage-exiftool-perl qpdf >/dev/null 2>&1 || echo "WARN: exiftool/qpdf not installed; PDF/image metadata strip is partial"; }
bash "$ROOT/cloud/wm-service.sh"

# Project slash commands (e.g. /boxabl) as user-level commands, so they work outside the repo folder too.
mkdir -p "$HOME/.claude/commands"
for f in "$ROOT"/.claude/commands/*.md; do
  [ -e "$f" ] && { [ -e "$HOME/.claude/commands/$(basename "$f")" ] || ln -s "$f" "$HOME/.claude/commands/$(basename "$f")"; }
done

# Claude's memory (preferences, campaign rules) for the repo path and the folders sessions start in.
for P in "$ROOT" "$HOME" /home/user; do
  KEY=$(printf '%s' "$P" | sed 's/[^A-Za-z0-9]/-/g')
  mkdir -p "$HOME/.claude/projects/$KEY/memory"
  cp -n "$ROOT"/cloud/memory/*.md "$HOME/.claude/projects/$KEY/memory/" 2>/dev/null || true
done

# Media too big to push from the PC's slow uplink: the Kevin MacLeod tracks (CC BY, same files as the PC copies,
# verified by checksum) come from incompetech.com, and the glitch transition is regenerated like make_kit.sh does.
M="$ROOT/commentary-kit/music"
while read -r sum name; do
  [ -f "$M/$name" ] && continue
  u="https://incompetech.com/music/royalty-free/mp3-royaltyfree/$(printf '%s' "$name" | sed 's/ /%20/g')"
  if curl -fsSL "$u" -o "$M/$name.part" && echo "$sum  $M/$name.part" | sha256sum -c --status; then
    mv "$M/$name.part" "$M/$name"
  else rm -f "$M/$name.part"; echo "WARN: could not fetch music '$name' (network blocked?)"; fi
done < "$ROOT/cloud/music.sha256"
G="$ROOT/commentary-kit/transitions/static_glitch_0.5s.mp4"
[ -f "$G" ] || ffmpeg -v error -f lavfi -i "color=c=black:s=1920x1080:r=30:d=0.5" -f lavfi -i "anoisesrc=d=0.5:c=white:a=0.6"   -filter_complex "[0]noise=alls=100:allf=t,rgbashift=rh=-30:bh=30,format=yuv420p[v]" -map "[v]" -map 1   -c:v libx264 -crf 28 -c:a aac -shortest "$G" || echo "WARN: could not build $G"

# sfx-kit (Wyzowl, CC0, 67 MB): too big to push from the PC, so fetched here at a pinned commit, checksummed.
K="$ROOT/commentary-kit/sfx/sfx-kit"
if [ ! -f "$K/sounds.json" ]; then
  T=$(mktemp -d)
  if curl -fsSL https://codeload.github.com/wyzowl/sfx-kit/tar.gz/92780e7ab0cdfb557497a988089c47f46e8c7412 -o "$T/k.tgz"      && echo "b8e5d7c65b72fc25d84b38a1f9df53f87eb59fb66f2583fbd4af6fa200776054  $T/k.tgz" | sha256sum -c --status; then
    mkdir -p "$K" && tar -xzf "$T/k.tgz" -C "$K" --strip-components=1
  else echo "WARN: could not fetch sfx-kit (network or checksum); its sounds are unavailable this session"; fi
  rm -rf "$T"
fi

# RTK (same version as the PC): compresses shell-command output via the hook in .claude/settings.json. Pinned + checksummed.
if ! command -v rtk >/dev/null 2>&1; then
  SUDO=""; [ "$(id -u)" = 0 ] || SUDO="sudo"
  R=https://github.com/rtk-ai/rtk/releases/download/v1.0.1; F=rtk-x86_64-unknown-linux-musl.tar.gz; T=$(mktemp -d)
  if curl -fsSL "$R/$F" -o "$T/$F" && curl -fsSL "$R/checksums.txt" -o "$T/sums" \
     && (cd "$T" && grep " $F\$" sums | sha256sum -c --status) && tar -xzf "$T/$F" -C "$T"; then
    $SUDO install -m 755 "$(find "$T" -type f -name rtk | head -1)" /usr/local/bin/rtk && echo "rtk installed: $(rtk --version)"
  else echo "WARN: rtk not installed (download or checksum failed); commands run unfiltered"; fi
  rm -rf "$T"
fi

# Perplexity MCP removed (user decision 2026-11-17): drop it from older sessions' config too.
python3 - <<'PY' || true
import json, os
p = os.path.expanduser("~/.claude.json")
if os.path.exists(p):
    d = json.load(open(p))
    if d.get("mcpServers", {}).pop("perplexity", None) is not None:
        json.dump(d, open(p, "w"), indent=2)
PY

# Token tools in the user settings too: the project .claude/settings.json only loads when a session starts inside the
# repo, and cloud sessions start in /home/user (RTK hook + Token Saver style were silently off).
python3 - "$ROOT" <<'PY' || echo "WARN: could not write ~/.claude/settings.json"
import json, os, shutil, sys
root = sys.argv[1]
p = os.path.expanduser("~/.claude/settings.json")
s = json.load(open(p)) if os.path.exists(p) else {}
s.setdefault("env", {}).update({"RTK_SUPPRESS_HOOK_WARNING": "1", "RTK_TELEMETRY_DISABLED": "1"})
pre = s.setdefault("hooks", {}).setdefault("PreToolUse", [])
cmd = "command -v rtk >/dev/null 2>&1 && exec rtk hook claude || exit 0"
if not any(h.get("command") == cmd for e in pre for h in e.get("hooks", [])):
    pre.append({"matcher": "Bash", "hooks": [{"type": "command", "command": cmd}]})
s["outputStyle"] = "Token Saver"
json.dump(s, open(p, "w"), indent=1)
os.makedirs(os.path.expanduser("~/.claude/output-styles"), exist_ok=True)
src = os.path.join(root, ".claude/output-styles/token-saver.md")
if os.path.exists(src): shutil.copy(src, os.path.expanduser("~/.claude/output-styles/token-saver.md"))
PY

# The vault (gmacc616/yt-automation-vault: main workspace, 3D shorts kit) next to this repo, plus its 3D bootstrap in the
# background (npm ci, voice engine, ~10-15 min the first time; /root/.3d-ready when done, log /root/3d-bootstrap.log).
VAULT=/home/user/yt-automation-vault
if [ -d "$VAULT/.git" ]; then git -C "$VAULT" pull -q --ff-only || echo "vault git pull failed"
else git clone -q --depth 1 https://github.com/gmacc616/yt-automation-vault.git "$VAULT" || echo "WARN: vault clone failed"; fi
link_private "$VAULT" yt-automation-vault-private sfxv2 Claude/Sessions Claude/Prompts Claude/graphify-out Graphs \
  graphify-out .claude/skills/gab .claude/skills/default-voice/voice
# The vault's skills are the master copy: they win over this repo's older copies (cloud/skills/3d-short etc. still had
# the Kokoro voice and none of the cloud render fixes when the 2026-11-16 session loaded them).
for d in "$VAULT"/.claude/skills/*/; do
  n=$(basename "$d"); [ -f "$d/SKILL.md" ] || continue
  ln -sfn "$(readlink -f "$d")" "$HOME/.claude/skills/$n"
done
[ -f "$VAULT/cloud/3d-bootstrap.sh" ] && { setsid nohup bash "$VAULT/cloud/3d-bootstrap.sh" > /root/3d-bootstrap.log 2>&1 < /dev/null & }

# Pointer for sessions that start outside the repo.
cat > "$HOME/.claude/CLAUDE.md" <<EOF
# AI-Video-Editor cloud workspace
The video workflow lives in $ROOT (GitHub gmacc616/ai-video-editor). Before any task: cd $ROOT
and follow $ROOT/CLAUDE.md (its "Cloud sessions" section). Work and outputs go inside that folder.
Save work back with git commit + git push only when the user asks.

EOF
# The user's global working rules from the PC (synced by cloud/sync.sh).
[ -f "$ROOT/cloud/global-claude.md" ] && cat "$ROOT/cloud/global-claude.md" >> "$HOME/.claude/CLAUDE.md"
echo "workspace ready: $(ls "$HOME/.claude/skills" | wc -l) skills linked, repo at $ROOT"
