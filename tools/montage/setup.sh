#!/usr/bin/env bash
# Install OpenMontage (AGPL-3.0) for /montage into vendor/openmontage at a pinned commit; idempotent.
# Used on the PC and by cloud-setup.sh. Skips Piper TTS on purpose: Kokoro (tools/voice/kvoice.py) covers it.
#   bash tools/montage/setup.sh
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OM="$ROOT/vendor/openmontage"
PIN="e01dbf433f46eeb91d39bf905e194162921019a3"   # 2026-10-23; bump deliberately, then re-run the /montage checks
PY="$(command -v py || command -v python3)"

if [ ! -d "$OM/.git" ]; then
  mkdir -p "$ROOT/vendor"
  git -c core.longpaths=true clone -q https://github.com/calesthio/OpenMontage.git "$OM"
fi
if [ "$(git -C "$OM" rev-parse HEAD)" != "$PIN" ]; then
  git -C "$OM" fetch -q --depth 1 origin "$PIN" && git -C "$OM" -c advice.detachedHead=false checkout -q "$PIN"
fi

PIP_FLAGS="-q"; [ "$(uname -s)" = Linux ] && PIP_FLAGS="-q --break-system-packages"
"$PY" -m pip install $PIP_FLAGS -r "$OM/requirements.txt"
# Extras its local tools check for: code_snippet (Pygments), transcript_fetcher, math_animate (Manim; Linux needs libcairo2-dev + libpango1.0-dev).
"$PY" -m pip install $PIP_FLAGS Pygments youtube-transcript-api manim || echo "WARN  Manim/extras not installed: math_animate stays unavailable"
[ -d "$OM/remotion-composer/node_modules" ] || (cd "$OM/remotion-composer" && npm install --no-audit --no-fund --loglevel=error)
[ -f "$OM/.env" ] || cp "$OM/.env.example" "$OM/.env"   # the user adds their own API keys here; never commit it
# OpenMontage's music_library tool reads this folder; /montage copies the chosen workspace track into it per job.
[ -e "$OM/music_library" ] || mkdir -p "$OM/music_library"

# Cloud-only extras (the user runs /montage in the cloud; the PC stays light):
#  - corpus_builder / clip_search: CPU torch + transformers (the CLIP model downloads on first use)
#  - bgm_montage_lite: BMTS-Lite (AGPL-3.0) at a pinned commit in its own Python 3.11 venv, made with uv
if [ "$(uname -s)" = Linux ]; then
  { "$PY" -m pip install $PIP_FLAGS torch --index-url https://download.pytorch.org/whl/cpu &&
    "$PY" -m pip install $PIP_FLAGS transformers opencv-python-headless; } ||
    echo "WARN  torch/transformers not installed: corpus_builder and clip_search stay unavailable"

  BM="$ROOT/vendor/bmts-lite"
  BM_PIN="d0b7c1fd5b96fb72d1378950fde8a5673a0813d1"   # 2026-10-09
  if { [ -d "$BM/.git" ] || git clone -q https://github.com/sharbvane/BMTS-Lite.git "$BM"; } &&
     git -C "$BM" -c advice.detachedHead=false checkout -q "$BM_PIN" &&
     "$PY" -m pip install $PIP_FLAGS uv &&
     { [ -x "$BM/.venv/bin/python" ] || "$PY" -m uv venv -q --python 3.11 "$BM/.venv"; } &&
     "$PY" -m uv pip install -q --python "$BM/.venv/bin/python" -r "$BM/requirements-runtime.txt"; then
    # The tool reads these two non-secret settings; OpenMontage loads .env on start.
    grep -q '^BGM_MONTAGE_LITE_ROOT=' "$OM/.env" ||
      printf '\nBGM_MONTAGE_LITE_ROOT=%s\nBGM_MONTAGE_LITE_PYTHON=%s\n' "$BM" "$BM/.venv/bin/python" >> "$OM/.env"
  else
    echo "WARN  BMTS-Lite not installed: bgm_montage_lite stays unavailable"
  fi
fi
echo "OpenMontage ready at $OM ($(git -C "$OM" rev-parse --short HEAD))"
