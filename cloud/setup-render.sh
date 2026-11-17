#!/usr/bin/env bash
# Render-only setup for CI (GitHub Actions): ffmpeg, fonts, Node 22, py/cygpath shims, HyperFrames + its browser.
# Skips the heavy extras in cloud-setup.sh (torch, Kokoro, mediapipe, OpenMontage).
set -e
SUDO=""; [ "$(id -u)" = 0 ] || SUDO="sudo"
$SUDO apt-get update -qq
$SUDO apt-get install -y -qq ffmpeg fonts-dejavu-core python3 >/dev/null
node -v | grep -qE '^v(2[2-9]|[3-9][0-9])' || { echo "Node 22+ required (use actions/setup-node)"; exit 1; }
# render-shorts.sh and the skills call these Windows-era names
printf '#!/bin/sh\nexec python3 "$@"\n' | $SUDO tee /usr/local/bin/py >/dev/null
printf '#!/bin/sh\nfor a; do :; done; printf "%%s\\n" "$a"\n' | $SUDO tee /usr/local/bin/cygpath >/dev/null
$SUDO chmod +x /usr/local/bin/py /usr/local/bin/cygpath
npx --yes hyperframes@0.8.157 --version
npx --yes hyperframes@0.8.157 browser ensure
