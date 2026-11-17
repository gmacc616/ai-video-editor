#!/usr/bin/env bash
# Setup script for a Claude Code cloud environment (Linux). Set it as the environment's setup command:
#   bash cloud-setup.sh
# Installs the toolchain, adds Windows-compat shims (py, cygpath), wires skills and memory (cloud/session-start.sh), then runs preflight.
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
SUDO=""; [ "$(id -u)" = 0 ] || SUDO="sudo"

# 1. System packages: ffmpeg, fonts for drawtext/captions, Chrome deps for the HyperFrames render browser.
$SUDO apt-get update -qq
$SUDO apt-get install -y -qq ffmpeg fonts-dejavu-core python3-pip >/dev/null
# Node 22+ (HyperFrames needs a modern Node)
if ! node -v 2>/dev/null | grep -qE '^v(2[2-9]|[3-9][0-9])'; then
  curl -fsSL https://deb.nodesource.com/setup_22.x | $SUDO bash - >/dev/null
  $SUDO apt-get install -y -qq nodejs >/dev/null
fi

# 2. Python tools used by tools/pipeline (same as the Windows PC).
PIP="python3 -m pip install -q --break-system-packages -U"
$PIP yt-dlp faster-whisper numpy auto-editor
# Optional extras: narration (Kokoro), face tracking, YouTube API. A failure here only disables that feature.
$PIP kokoro-onnx soundfile || echo "WARN  Kokoro TTS not installed"
# kvoice cloning add-on (tools/voice/kvoice.py clone): CPU-only torch keeps it ~1 GB; Kokoro model files download on first use.
{ $PIP torch --index-url https://download.pytorch.org/whl/cpu && $PIP webrtcvad-wheels librosa scipy typing && $PIP --no-deps resemblyzer; } || echo "WARN  kvoice cloning add-on not installed"
$PIP mediapipe opencv-python-headless || echo "WARN  face tracking not installed"
$PIP google-api-python-client google-auth-oauthlib || echo "WARN  YouTube API client not installed"

# /montage: OpenMontage at a pinned commit (vendor/openmontage, gitignored). Manim needs cairo/pango headers.
$SUDO apt-get install -y -qq libcairo2-dev libpango1.0-dev pkg-config >/dev/null || true
bash "$ROOT/tools/montage/setup.sh" || echo "WARN  OpenMontage (/montage) not installed"

# 3. Windows-compat shims so every existing "py ..." and "cygpath ..." line works unchanged.
printf '#!/bin/sh\nexec python3 "$@"\n' | $SUDO tee /usr/local/bin/py >/dev/null
printf '#!/bin/sh\n# cygpath shim: on Linux paths need no conversion; print the last argument.\nfor a; do :; done; printf "%%s\\n" "$a"\n' | $SUDO tee /usr/local/bin/cygpath >/dev/null
$SUDO chmod +x /usr/local/bin/py /usr/local/bin/cygpath

# 4. HyperFrames CLI (pinned like hf.sh) and its render browser.
npx --yes hyperframes@0.8.157 --version
npx --yes hyperframes@0.8.157 browser ensure >/dev/null 2>&1 || true

# 5. Skills, memory and the workspace pointer (also run at each session start by the environment's hook).
bash "$ROOT/cloud/session-start.sh"

# 7. Verify.
bash "$ROOT/tools/pipeline/preflight.sh" || true
