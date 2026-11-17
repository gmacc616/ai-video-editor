"""kvoice: Voicebox-style features on top of local Kokoro (free, offline, CPU). Default voice: am_adam.

  py tools/voice/kvoice.py speak  --text "Hello there. [pause 0.4] [dramatic] It begins." [--voice V] [--speed 1.0]
                                  [--delivery "slow, calm"] [--fx "pitch=-2,reverb=0.3"] [--preset radio] [--out x.wav]
  py tools/voice/kvoice.py speak  --script story.txt [--out x.wav]      multi-voice script, see SCRIPT FORMAT
  py tools/voice/kvoice.py voices                                        presets + saved custom voices
  py tools/voice/kvoice.py design --name warm_narrator --desc "deep warm older male narrator"   (or --blend "am_adam:0.6,bm_george:0.4")
  py tools/voice/kvoice.py clone  --name me --ref my_voice.wav --i-have-consent [--steps 80]   needs the cloning add-on (see cmd_clone)
  py tools/voice/kvoice.py --selftest

VOICE (V): a preset (am_adam), a blend ("am_adam:0.6,bm_george:0.4"), or a saved custom voice (tools/voice/voices/<name>).
SCRIPT FORMAT:  "@cast NARRATOR=am_adam KING=bm_george:0.7,am_michael:0.3" then lines "NARRATOR: text"; lines without a
  speaker use --voice. Inline tags apply to the rest of the line: [pause 0.5] [slow] [fast] [whisper] [shout] [loud] [soft]
  [dramatic] [excited] [happy] [calm] [sad] [angry] [deep] [high] [narration]. Non-speech tags ([laugh] [chuckle] [sigh]
  [gasp] [groan] [shush] [clear throat]) become spoken approximations ("Ha ha!"), because Kokoro can't make those sounds;
  [cough] and [sniff] are skipped. Every approximation is listed in the take's JSON.
FX: pitch=semitones, speed=x, gain=dB, reverb=0..1, delay=ms, chorus=0..1, flanger=0..1, compress=1, highpass=Hz,
  lowpass=Hz, crush=bits. PRESETS: robotic, radio, echo-chamber, deep-voice.
Every take is kept (never overwritten: x.wav, x_v2.wav, ...) with a JSON sidecar (text, voice blend, settings, model,
duration): versions + provenance. Long text is split into sentences and crossfaded (no length limit).
"""
import argparse, datetime, json, os, re, subprocess, sys, tempfile
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
VOICES_DIR = HERE / "voices"
CACHE = Path.home() / ".cache/hyperframes/tts"
MODEL, VOICES_BIN = CACHE / "models/kokoro-v1.0.onnx", CACHE / "voices/voices-v1.0.bin"
RELEASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
DEFAULT_VOICE, SR = "am_adam", 24000
LANG_BY_PREFIX = {"a": "en-us", "b": "en-gb", "e": "es", "f": "fr-fr", "h": "hi", "i": "it", "j": "ja", "p": "pt-br", "z": "cmn"}

DELIVERY = {  # Kokoro has no acting control: delivery = speed x, pitch semitones, gain dB, extra fx, pause after (s)
    "slow": dict(speed=0.85), "fast": dict(speed=1.15), "whisper": dict(speed=0.95, gain=-7, fx="highpass=350,lowpass=6500"),
    "shout": dict(speed=1.06, pitch=1.0, gain=4, fx="compress=1"), "loud": dict(gain=4), "soft": dict(gain=-5),
    "dramatic": dict(speed=0.9, pitch=-1.0, fx="reverb=0.15", pause=0.25), "excited": dict(speed=1.12, pitch=1.5),
    "happy": dict(speed=1.06, pitch=1.0), "calm": dict(speed=0.92, pitch=-0.5), "sad": dict(speed=0.88, pitch=-1.5, gain=-2),
    "angry": dict(speed=1.08, pitch=0.5, gain=3, fx="compress=1"), "deep": dict(pitch=-3), "high": dict(pitch=3),
    "narration": dict(speed=0.97, fx="compress=1"),
}
NONVERBAL = {"laugh": "Ha ha ha!", "chuckle": "Heh heh.", "sigh": "Haah...", "gasp": "Oh!", "groan": "Ugh.",
             "shush": "Shhh.", "clear throat": "Ahem.", "cough": None, "sniff": None}
PRESETS = {"robotic": "flanger=0.7,crush=8,pitch=-1", "radio": "highpass=300,lowpass=3400,compress=1,gain=3",
           "echo-chamber": "reverb=0.6,delay=180", "deep-voice": "pitch=-4,lowpass=7000"}


def ensure_model():
    for path, name in ((VOICES_BIN, "voices-v1.0.bin"), (MODEL, "kokoro-v1.0.onnx")):
        if not path.exists():  # same official files the HyperFrames TTS uses
            path.parent.mkdir(parents=True, exist_ok=True)
            print(f"downloading {name} (one time) ...", file=sys.stderr)
            subprocess.run(["curl", "-fsSL", "--retry", "3", "-o", str(path), f"{RELEASE}/{name}"], check=True)
    import kokoro_onnx
    return kokoro_onnx.Kokoro(str(MODEL), str(VOICES_BIN))


# ---------- voices: preset | blend | saved custom (design json or cloned npy) ----------
def parse_blend(spec):
    parts = [p.split(":") for p in spec.split(",") if p.strip()]
    pairs = [(p[0].strip(), float(p[1]) if len(p) > 1 else 1.0) for p in parts]
    tot = sum(w for _, w in pairs)
    if tot <= 0: raise SystemExit(f"bad blend weights: {spec}")
    return [(n, w / tot) for n, w in pairs]


def resolve_voice(k, spec):
    """-> (style ndarray, info dict with the exact recipe, extra fx string, lang)"""
    spec = spec or DEFAULT_VOICE
    custom = VOICES_DIR / f"{spec}.json"
    if custom.exists():
        meta = json.loads(custom.read_text(encoding="utf-8"))
        if meta.get("style_file"):
            style = np.load(VOICES_DIR / meta["style_file"])
        else:
            style, _, _, _ = resolve_voice(k, ",".join(f"{n}:{w}" for n, w in meta["blend"]))
        return style.astype(np.float32), {"custom": spec, **meta}, meta.get("fx", ""), meta.get("lang") or "en-us"
    pairs = parse_blend(spec)
    for n, _ in pairs:
        if n not in k.get_voices(): raise SystemExit(f"unknown voice '{n}' (run: kvoice.py voices)")
    style = sum(w * k.get_voice_style(n) for n, w in pairs)
    lang = LANG_BY_PREFIX.get(pairs[0][0][0], "en-us")
    return style.astype(np.float32), {"blend": [[n, round(w, 4)] for n, w in pairs]}, "", lang


# ---------- effects (ffmpeg) ----------
def fx_chain(fx):
    d = {}
    for part in filter(None, (p.strip() for p in (fx or "").split(","))):
        key, _, val = part.partition("="); d[key.strip()] = float(val or 1)
    f = []
    if d.get("pitch"): f.append(f"rubberband=pitch={2 ** (d['pitch'] / 12):.5f}")
    if d.get("speed") and d["speed"] != 1: f.append(f"atempo={d['speed']}")
    if d.get("highpass"): f.append(f"highpass=f={d['highpass']}")
    if d.get("lowpass"): f.append(f"lowpass=f={d['lowpass']}")
    if d.get("chorus"): w = d["chorus"]; f.append(f"chorus=0.6:0.9:50|60:{0.4*w:.2f}|{0.32*w:.2f}:0.25|0.4:2|2.3")
    if d.get("flanger"): f.append(f"flanger=depth={3*d['flanger']:.1f}:regen={-8*d['flanger']:.1f}")
    if d.get("crush"): f.append(f"acrusher=bits={int(d['crush'])}:mode=log:mix=0.6")
    if d.get("delay"): f.append(f"aecho=0.9:0.7:{int(d['delay'])}:0.4")
    if d.get("reverb"): r = d["reverb"]; f.append(f"aecho=0.85:0.85:43|71|113|163|239:{0.45*r:.3f}|{0.36*r:.3f}|{0.28*r:.3f}|{0.2*r:.3f}|{0.12*r:.3f}")
    if d.get("compress"): f.append("acompressor=threshold=0.08:ratio=4:attack=5:release=80:makeup=2")
    if d.get("gain"): f.append(f"volume={d['gain']}dB")
    unknown = set(d) - {"pitch", "speed", "highpass", "lowpass", "chorus", "flanger", "crush", "delay", "reverb", "compress", "gain"}
    if unknown: raise SystemExit(f"unknown fx: {', '.join(sorted(unknown))}")
    return ",".join(f)


def apply_fx(audio, fx):
    chain = fx_chain(fx)
    if not chain: return audio
    with tempfile.TemporaryDirectory() as td:
        a, b = Path(td) / "a.wav", Path(td) / "b.wav"
        import soundfile as sf
        sf.write(a, audio, SR)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(a), "-af", chain, "-ar", str(SR), "-ac", "1", str(b)], check=True)
        out, _ = sf.read(b, dtype="float32")
    return out


# ---------- script parsing: speakers, tags, sentences ----------
def parse_script(text, default_voice):
    cast, segs, notes = {}, [], []
    for raw in text.splitlines():
        line = raw.strip()
        if not line: continue
        if line.startswith("@cast"):
            for m in re.finditer(r"(\w+)=(\S+)", line): cast[m.group(1).upper()] = m.group(2)
            continue
        m = re.match(r"^([A-Za-z][\w ]{0,30}):\s+(.*)$", line)
        who, body = (m.group(1).upper(), m.group(2)) if m and m.group(1).upper() in cast else (None, line)
        voice = cast.get(who, default_voice) if who else default_voice
        mods = []
        for tok in re.split(r"(\[[^\]]+\])", body):
            if not tok.strip(): continue
            t = re.fullmatch(r"\[([^\]]+)\]", tok.strip())
            if t:
                tag = t.group(1).strip().lower()
                if tag.startswith("pause"):
                    segs.append({"pause": float((tag.split() + ["0.5"])[1])})
                elif tag in DELIVERY:
                    mods.append(tag)
                elif tag in NONVERBAL:
                    say = NONVERBAL[tag]; notes.append(f"[{tag}] -> {'skipped' if say is None else repr(say)} (Kokoro can't make that sound)")
                    if say: segs.append({"text": say, "voice": voice, "mods": mods + ["soft"] if tag in ("sigh", "shush") else list(mods), "who": who})
                else:
                    notes.append(f"[{tag}] unknown tag, ignored")
                continue
            for sent in re.findall(r"[^.!?…]+[.!?…]*", tok):
                if sent.strip(): segs.append({"text": sent.strip(), "voice": voice, "mods": list(mods), "who": who})
    return segs, notes


def delivery_from_words(words):
    """'speak slowly, dramatic, a bit louder' -> list of DELIVERY tags (natural-language delivery control, approximated)"""
    words = (words or "").lower(); found = []
    syn = {"slow": "slow", "fast": "fast", "quick": "fast", "whisper": "whisper", "shout": "shout", "loud": "loud", "soft": "soft",
           "quiet": "soft", "dramatic": "dramatic", "excit": "excited", "energetic": "excited", "happy": "happy", "cheer": "happy",
           "calm": "calm", "relax": "calm", "sad": "sad", "angry": "angry", "deep": "deep", "high": "high", "narrat": "narration"}
    for k, v in syn.items():
        if k in words and v not in found: found.append(v)
    return found


def render(k, segs, base_speed, extra_mods, crossfade=0.03):
    out, cf, used = [], int(crossfade * SR), []
    cache = {}
    for s in segs:
        if "pause" in s: out.append(np.zeros(int(s["pause"] * SR), np.float32)); continue
        if s["voice"] not in cache: cache[s["voice"]] = resolve_voice(k, s["voice"])
        style, info, vfx, lang = cache[s["voice"]]
        p = dict(speed=1.0, pitch=0.0, gain=0.0, fx=[], pause=0.0)
        for m in s["mods"] + extra_mods:
            d = DELIVERY[m]; p["speed"] *= d.get("speed", 1); p["pitch"] += d.get("pitch", 0); p["gain"] += d.get("gain", 0)
            p["pause"] = max(p["pause"], d.get("pause", 0)); p["fx"] += [d["fx"]] if "fx" in d else []
        speed = float(np.clip(base_speed * p["speed"], 0.5, 2.0))
        a, sr = k.create(s["text"], voice=style, speed=speed, lang=lang)
        fx = ",".join(filter(None, [vfx, f"pitch={p['pitch']}" if p["pitch"] else "", f"gain={p['gain']}" if p["gain"] else "", *p["fx"]]))
        a = apply_fx(a.astype(np.float32), fx)
        if out and cf and len(out[-1]) > cf and len(a) > cf and not np.allclose(out[-1][-cf:], 0):
            ramp = np.linspace(0, 1, cf, dtype=np.float32)
            out[-1][-cf:] = out[-1][-cf:] * (1 - ramp) + a[:cf] * ramp; a = a[cf:]
        out.append(a)
        if p["pause"]: out.append(np.zeros(int(p["pause"] * SR), np.float32))
        used.append({"text": s["text"], "who": s["who"], "voice": s["voice"], "speed": round(speed, 3), "fx": fx, "mods": s["mods"] + extra_mods})
    return (np.concatenate(out) if out else np.zeros(1, np.float32)), used, {v: c[1] for v, c in cache.items()}


def next_version(path):
    path = Path(path); stem, n = path.stem, 1
    while path.exists(): n += 1; path = path.with_name(f"{stem}_v{n}{path.suffix}")
    return path


def cmd_speak(a):
    import soundfile as sf
    k = ensure_model()
    text = Path(a.script).read_text(encoding="utf-8") if a.script else a.text
    if not text: raise SystemExit("give --text or --script")
    segs, notes = parse_script(text, a.voice or DEFAULT_VOICE)
    audio, used, voices = render(k, segs, a.speed, delivery_from_words(a.delivery), a.crossfade)
    fx = ",".join(filter(None, [PRESETS.get(a.preset, "") if a.preset else "", a.fx or ""]))
    if a.preset and a.preset not in PRESETS: raise SystemExit(f"unknown preset (choose: {', '.join(PRESETS)})")
    audio = apply_fx(audio, fx)
    peak = float(np.max(np.abs(audio)) or 1); audio = audio * min(1.0, 0.95 / peak)
    out = next_version(a.out or "voiceover.wav"); out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(out, audio, SR)
    meta = {"tool": "kvoice", "created": datetime.datetime.now().isoformat(timespec="seconds"), "engine": "Kokoro v1.0 (kokoro-onnx, local)",
            "model": MODEL.name, "default_voice": a.voice or DEFAULT_VOICE, "voices": voices, "base_speed": a.speed,
            "delivery": a.delivery, "global_fx": fx, "segments": used, "approximations": notes, "duration_s": round(len(audio) / SR, 3),
            "ai_generated": True}
    out.with_suffix(".json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"saved {out} ({meta['duration_s']} s, {len(used)} segments){' | ' + '; '.join(notes) if notes else ''}")


def cmd_voices(a):
    k = ensure_model(); v = k.get_voices()
    print("presets:", " ".join(v)); print("presets by language:", {LANG_BY_PREFIX.get(p, p): sum(x[0] == p for x in v) for p in sorted({x[0] for x in v})})
    saved = sorted(p.stem for p in VOICES_DIR.glob("*.json")) if VOICES_DIR.exists() else []
    print("custom:", " ".join(saved) or "(none)"); print("fx presets:", " ".join(PRESETS))


DESC_VOICES = {  # description words -> preset voices to blend (heuristic voice design)
    "female": ["af_heart", "af_bella", "bf_emma"], "male": ["am_adam", "am_michael", "bm_george"],
    "british": ["bm_george", "bm_lewis", "bf_emma"], "american": ["am_adam", "am_michael", "af_heart"],
    "deep": ["am_onyx", "bm_george", "am_fenrir"], "warm": ["am_michael", "af_heart", "bm_lewis"],
    "young": ["am_puck", "am_liam", "af_nova"], "energetic": ["am_liam", "am_puck", "af_nicole"],
    "calm": ["bm_daniel", "af_sky", "am_michael"], "narrator": ["am_michael", "bm_lewis", "am_adam"],
}


def cmd_design(a):
    k = ensure_model(); have = set(k.get_voices()); VOICES_DIR.mkdir(exist_ok=True)
    if a.blend:
        pairs = parse_blend(a.blend); fx = a.fx or ""
    else:
        words = a.desc.lower(); score = {}
        for key, names in DESC_VOICES.items():
            if key in words:
                for i, n in enumerate(names):
                    if n in have: score[n] = score.get(n, 0) + (3 - i)
        if "female" in words or "woman" in words: score = {n: s for n, s in score.items() if n[1] == "f"} or score
        elif "male" in words or " man" in words: score = {n: s for n, s in score.items() if n[1] == "m"} or score
        top = sorted(score.items(), key=lambda x: -x[1])[:3] or [(DEFAULT_VOICE, 1)]
        tot = sum(s for _, s in top); pairs = [(n, s / tot) for n, s in top]
        tweaks = []
        if re.search(r"\b(deep|low|older|old|mature)\b", words): tweaks.append("pitch=-1.5")
        if re.search(r"\b(high|young|child|bright)\b", words): tweaks.append("pitch=1.5")
        if "radio" in words: tweaks.append(PRESETS["radio"])
        fx = ",".join(tweaks + ([a.fx] if a.fx else []))
    meta = {"name": a.name, "description": a.desc, "blend": [[n, round(w, 4)] for n, w in pairs], "fx": fx,
            "lang": LANG_BY_PREFIX.get(pairs[0][0][0], "en-us"), "created": datetime.date.today().isoformat(), "kind": "designed"}
    resolve_voice(k, ",".join(f"{n}:{w}" for n, w in pairs))  # validates names
    (VOICES_DIR / f"{a.name}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(f"saved voice '{a.name}': " + " + ".join(f"{n} {w:.0%}" for n, w in pairs) + (f" | fx {fx}" if fx else ""))


def cmd_clone(a):
    """Search-based cloning: find a Kokoro style vector whose speech sounds like the reference speaker
    (speaker-embedding similarity, Resemblyzer). Only for your own voice or one you have permission to clone."""
    if not a.i_have_consent:
        raise SystemExit("refused: cloning needs --i-have-consent (your own voice, or written permission from the speaker)")
    try:
        from resemblyzer import VoiceEncoder, preprocess_wav
    except ImportError:
        raise SystemExit("cloning needs Resemblyzer: py -m pip install webrtcvad-wheels torch librosa scipy typing && py -m pip install --no-deps resemblyzer  (~1-2 GB)")
    k = ensure_model(); enc = VoiceEncoder("cpu"); VOICES_DIR.mkdir(exist_ok=True)
    ref = enc.embed_utterance(preprocess_wav(Path(a.ref)))
    test = "The quick brown fox jumps over the lazy dog, and then it runs far away into the forest."
    def score(style):
        audio, sr = k.create(test, voice=style.astype(np.float32), speed=1.0)
        return float(np.dot(enc.embed_utterance(preprocess_wav(audio, source_sr=sr)), ref))
    presets = [v for v in k.get_voices() if v[0] in "ab"]
    ranked = sorted(((score(k.get_voice_style(v)), v) for v in presets), reverse=True)[:3]
    print("closest presets:", ", ".join(f"{v} {s:.3f}" for s, v in ranked))
    w = np.array([s for s, _ in ranked]); w = w / w.sum()
    blend = sum(wi * k.get_voice_style(v) for wi, (_, v) in zip(w, ranked)); blend_s = score(blend)
    best, best_s = (blend, blend_s) if blend_s > ranked[0][0] else (k.get_voice_style(ranked[0][1]), ranked[0][0])  # start from whichever is closer
    spread = np.std([k.get_voice_style(v) for v in presets], axis=0); rng = np.random.default_rng(7); step = 0.35
    for i in range(a.steps):
        cand = best + rng.normal(0, 1, best.shape) * spread * step
        s = score(cand)
        if s > best_s: best, best_s = cand, s
        step = max(0.05, step * 0.985)
        if (i + 1) % 10 == 0: print(f"step {i + 1}/{a.steps}: similarity {best_s:.3f}", flush=True)
    np.save(VOICES_DIR / f"{a.name}.npy", best.astype(np.float32))
    meta = {"name": a.name, "kind": "cloned", "style_file": f"{a.name}.npy", "reference": Path(a.ref).name, "similarity": round(best_s, 4),
            "start_presets": [[v, round(s, 4)] for s, v in ranked], "steps": a.steps, "consent": "declared by user (--i-have-consent)",
            "lang": "en-us", "created": datetime.date.today().isoformat()}
    (VOICES_DIR / f"{a.name}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(f"saved cloned voice '{a.name}' (similarity {best_s:.3f}; 0.75+ usually sounds like the same speaker)")


def selftest():
    segs, notes = parse_script("@cast KING=bm_george\nNARRATOR line. [pause 0.3] Two!\nKING: [dramatic] Which one? [laugh]", "am_adam")
    assert [s.get("pause") for s in segs if "pause" in s] == [0.3], segs
    assert any(s.get("who") == "KING" and "dramatic" in s["mods"] for s in segs), segs
    assert any("Ha ha" in s.get("text", "") for s in segs) and notes, notes
    assert delivery_from_words("speak slowly but energetic") == ["slow", "excited"]
    assert "rubberband" in fx_chain("pitch=-2") and "aecho" in fx_chain(PRESETS["echo-chamber"])
    assert [round(w, 2) for _, w in parse_blend("am_adam:3,bm_george:1")] == [0.75, 0.25]
    p = Path(tempfile.gettempdir()) / "kv_selftest.wav"; p.write_bytes(b"x"); assert next_version(p).name == "kv_selftest_v2.wav"; p.unlink()
    print("selftest ok (parsing, tags, delivery, fx chains, blends, versions)")


def main():
    if sys.argv[1:2] == ["--selftest"]: return selftest()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("speak"); s.add_argument("--text"); s.add_argument("--script"); s.add_argument("--voice")
    s.add_argument("--speed", type=float, default=1.0); s.add_argument("--delivery"); s.add_argument("--fx"); s.add_argument("--preset")
    s.add_argument("--crossfade", type=float, default=0.03); s.add_argument("--out")
    sub.add_parser("voices")
    d = sub.add_parser("design"); d.add_argument("--name", required=True); d.add_argument("--desc", default=""); d.add_argument("--blend"); d.add_argument("--fx")
    c = sub.add_parser("clone"); c.add_argument("--name", required=True); c.add_argument("--ref", required=True)
    c.add_argument("--steps", type=int, default=80); c.add_argument("--i-have-consent", action="store_true")
    a = ap.parse_args()
    {"speak": cmd_speak, "voices": cmd_voices, "design": cmd_design, "clone": cmd_clone}[a.cmd](a)


if __name__ == "__main__":
    main()
