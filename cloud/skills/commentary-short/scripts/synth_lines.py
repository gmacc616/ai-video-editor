"""Batch Kokoro TTS: load the model once, render every narration item to its own WAV.

Usage: py synth_lines.py <job>/edit/short.json [--force]
Reads "voice"/"speed" and every item that has "text" (sentences split on "|").
Writes <job>/vo/<id>.wav (24 kHz mono) and <job>/vo/durations.json. Skips lines already rendered unless --force.

Calls kokoro_onnx directly: `hyperframes tts` falsely reports Kokoro as missing on this slow PC (its import probe times out).
"""
import json, sys
from pathlib import Path
import kokoro_onnx, soundfile as sf

cfg_path = Path(sys.argv[1]).resolve()
force = "--force" in sys.argv
cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
job = cfg_path.parents[1]
outdir = job / "vo"; outdir.mkdir(exist_ok=True)
voice, speed = cfg.get("voice", "am_fenrir"), float(cfg.get("speed", 1.08))
cache = Path.home() / ".cache/hyperframes/tts"
model = kokoro_onnx.Kokoro(str(cache / "models/kokoro-v1.0.onnx"), str(cache / "voices/voices-v1.0.bin"))
durs_path = outdir / "durations.json"
durs = json.loads(durs_path.read_text()) if durs_path.exists() else {}

for item in cfg["items"]:
    if not item.get("text"):
        continue
    out = outdir / f"{item['id']}.wav"
    if out.exists() and item["id"] in durs and not force:
        continue
    # One call per sentence keeps each call under Kokoro's 510-token limit and RAM low.
    samples, rate = [], 24000
    for part in [p.strip() for p in item["text"].replace("\n", " ").split("|") if p.strip()]:
        s, rate = model.create(part, voice=voice, speed=speed, lang="en-us")
        samples.extend(s)
    sf.write(out, samples, rate)
    durs[item["id"]] = round(len(samples) / rate, 3)
    durs_path.write_text(json.dumps(durs, indent=1))
    print(item["id"], durs[item["id"]], flush=True)
