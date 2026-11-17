---
description: Edit a source video into a "meme" Short. No AI narrator. Finds the funniest and most meme-able moments in the original audio and cuts them in the streamer-reaction style of the two reference clips, with bold one-or-two-word captions, meme sound effects on the beats, punch-ins and colour flashes.
argument-hint: <source video file | YouTube url> [reference file/url] [campaign: boxabl|gab|none]
---

# /meme: funny-moment Short with meme SFX (no narrator)

Source: $ARGUMENTS

If no source was given above, ask for the link or file and stop. Workspace: `C:\Users\manth\OneDrive\Desktop\AI-Video-Editor`,
tools in `tools/pipeline/`. Run `bash tools/pipeline/preflight.sh` first. Read `docs/clipping-playbook.md` and
`docs/effects-catalog.md`, and `motion-graphics-library/EFFECTS_INDEX.md` before making any effect. /meme always runs the
**7 workflow steps** (input → reference study → story moments → effects per cut → edit → clip all that pass → render),
written out for this format in § 6. § 1–5 are the style sheet. Never publish, schedule or upload. Show the plans (moment,
caption script, shot list, SFX list) before editing, unless the prompt says no plan approval is needed.

**No fixed features, on purpose (user's choice):** /meme does NOT use the workflow's fixed features (opening zoom-out +
woosh, hook riser, closing zoom-in + woosh loop). Build with `"fixedFeatures": false`. Don't add them back.

**Fixed /meme rules on every clip (user's standing choice, 2026-10-27; applied by `tools/pipeline/meme-fixed.py`):**
- **Frame 1:** fully white (fades out over 0.14 s), with `sound effects/awkward-moment.mp3` at 0.0 s, played from the
  file's start; level-matched to the speech, then 20 % louder (+1.6 dB).
- **Frame 2:** the CapCut-style `cross-shake` transition. It runs 4 frames of criss-crossing diagonal whip blur, then the shot
  lands at ~115 % and settles with a damped jitter (~0.3 s). It's in the motion-graphics library, modelled on CapCut's "Cross
  shakes" template.
- **Music:** `Ts Pmo.mp3` at −8 dB from 0:00 to the last frame, 0.4 s fade-out, also on campaign jobs. Speech is normalised to
  −16 LUFS first, so the bed sits ~10–12 dB under it.
- **Meme sounds:**
  - **Length:** play in full; only a sound longer than 2 s stops at 1.5 s, with a 0.2 s fade-out.
  - **Level:** each is level-matched to the clip's speech ("same volume as the source").
  - **Placement:** in speech gaps where possible; otherwise the speech dips 6 dB for at most 1 s.
  - **How many:** lots of them (~4–10 per clip), current trending sounds, each matched to the word or beat it lands on. Never
    stack two on one beat.
- **Cuts:** never cut while someone is still speaking. Every segment starts on a word and ends after the sentence or pause.
  Check every edge against two transcripts (small/medium.en; base.en drops and stretches words).
- **No `speed-lines` overlay.**

**Typed hook on every clip (user's choice, 2026-10-27):** each clip opens with a short on-screen hook that types out letter
by letter with the typing sound, copied from the Brezscales reference's first animation: `"typedHook": "LINE ONE / *KEYWORD LINE*"`
(≤6 words, two lines, `*keyword*` glows green) and `"hookEnd"` (when the card leaves, usually 1.5–2.5 s). The builder plays
`sound effects/fast-and-dynamic-typing-keyboard.mp3` exactly while each line types and skips speech captions under the card.
No narration: the hook is text only, accurate, and answered by the clip.

**Differences from /mark:** there is **no AI voice and no narration**. All speech is the original audio. The comedy comes from
picking the funny moment, timing the cuts, one-or-two-word captions and meme sounds. No teaser-reorder, no light-leak handover. Every clip gets the same low music bed (§ 4), and beat-sync editing does not apply.

**Campaign rules override everything here.** BOXABL → `.claude/commands/boxabl.md`; DraftKings → `~/.claude/skills/gab/SKILL.md`.
For campaign clips use sfx-kit / Kenney / generated sounds instead of recognisable meme sounds (§ 4 licence note).

## 1. The references, measured (2026-10-27)
Two reference Shorts supplied by the user, both a streamer (IShowSpeed) reacting. Studied with `study-reference.py`
(`jobs/meme_ref/a`, `jobs/meme_ref/b`; source copies `downloads/memeref_a.mp4`, `memeref_b.mp4`).
**Limit:** the SFX below were located by loudness onsets and the transcript, not identified by ear. Which meme sound plays at
each hit is inferred from the moment, and the user's pack is mapped in § 4.

| | Ref A "number leak" | Ref B "getting fat" |
|---|---|---|
| Length / size | 36.4 s, 360×640, 30 fps | 13.8 s, 360×640, 30 fps |
| Cuts | 12 (0.33/s), shots 0.77–6.5 s, median 1.9 s | 5 (0.36/s), shots 1.1–4.3 s, median 2.0 s |
| Loudness | −13.5 LUFS, LRA 10.9, peaks 0 dBFS | −12.8 LUFS, LRA 7.9, peaks 0 dBFS |
| Sound hits (s) | 1.0, 2.7, 3.4, 6.45, 6.95, 7.35, 7.85, 8.55, 9.5, 10.3, 10.6, 10.95, 12.05, 12.3, 12.7, 13.2 … (38 in 36 s) | 0.9, 1.4, 2.35, 3.95, 6.15, 7.7, 9.5, 10.65, 12.75 (9 in 13.8 s) |
| Speech rate | 2.6 words/s | 2.4 words/s |

**Findings (what to copy):**
- **Full-frame vertical.** The footage fills the whole 9:16 frame, with no black bars, no headline bar and no footage band.
  Ref A stacks two sources: the clip being reacted to on top, the streamer's face-cam in the bottom ~35% (shown full-width, cropped
  at the chest). Ref B is one shot of the streamer filling the frame.
- **Captions carry the joke.** One or two words at a time, **centred at about 45–50% height** (over the body or chin, never
  over the eyes), bold condensed sans, **yellow fill + thick black outline** by default. The caption follows the speech word for
  word. Second colour **cyan** on negation/emphasis words ("NOT", "OUT!", "YUP", "ARE!"); **pink/white with asterisks** for
  an action or sound that isn't a spoken word (`*GETS FAT*`, `*SKINNY*`, `*FAT*`). Exclamation marks on shouted words.
- **Cuts happen on a change of subject or a punchline, not on a clock.** A shot lasts as long as the bit does (about 2 s median).
  Cut types seen in Ref A: a hard cut to the next screen; a **red-tinted frame** (the incoming call screen); a **blurred green
  full-screen** transition frame; a **manga/anime speed-line panel with orange radial lines** dropped in for one beat; a face-cam
  push-in on a reaction.
- **Colour flashes and tints on beats (Ref B).** A strong **green tint** on one word (frame ~5.1 s, "IT") and
  **overexposed white/pink flashes** on the first frames of a new beat. They last 2–4 frames and coincide with a sound hit.
- **Motion is in the footage plus small punch-ins.** Little added camera motion: a hard punch-in (100 → 115–125 %) on the
  reaction word and a snap back. No shake.
- **Sound marks the joke.** The references have many hits (about 1/s in A, 0.65/s in B, counting speech onsets), but the amount is
  not the rule to copy: copy the use, a meme sound on the funny word or moment and a reaction sound after it. Speech stays on top (the speech is never covered).
  Loudness ≈ −13 LUFS with peaks at 0 dBFS. Both references also carry a **quiet background music bed** under everything (§ 4).
- **Opens on the line, not on a title.** First frame is already speech. /meme adds the typed hook card over that opening
  (see above); speech captions take over when the card leaves.

## 2. The structure (scale to 10–35 s)
| Part | Build |
|---|---|
| **A. Cold open + typed hook** (0–2.5 s) | Start on the **setup line already in motion**, or on the funniest face/frame for 0.5 s if the source allows (a 1-shot teaser of the punchline with its original sound, then a hard cut to the setup). The typed hook card types over it from 0.3 s with the typing sound; speech captions start when it leaves. |
| **B. Build** | Original speech in real order. Cut on subject changes and punchlines. Cut out dead air with `cut-silences`; keep a laugh or a pause only when it's the joke. |
| **C. Punchline** | Land the funniest line or reaction **once**. 1 caption in cyan or yellow with a punch-in 100 → 120 %, and 1 meme SFX on the word, then a reaction sound (laugh, boom, crowd) on the next beat. |
| **D. Tag** | Optional: a 0.5–1 s reaction beat (face, record scratch, bonk). End on the reaction, not on a fade. Loop the last frame into frame 0 when the last line works as a lead-in. |

## 3. The look
- **Canvas:** 1080×1920, footage full-frame (blurred-fill only if the source is 16:9, with the subject in a 1080×1350 centre
  crop via `reframe.py`). If there is a second source (a call screen, a clip being reacted to), stack it top ~62 % /
  face-cam bottom ~38 % like Ref A.
- **Captions:** word by word from the transcript (fix Whisper mistakes). About 90 px (at 1080 wide) bold condensed uppercase,
  yellow `#FFE600` with a 6 px black outline; cyan `#00E5FF` for negation/emphasis; white `*ACTION*` text for non-spoken
  beats. At most 2 words on screen. No emoji, no boxes.
- **Overlays (only from `motion-graphics-library/`):** no `speed-lines` (the user's call, 2026-10-27); `tint`
  (`color` red `#ff2020` / green `#20ff40` / pink, `d` 0.07–0.13 s = 2–4 frames) on a hit; `white-flash` for a reveal; no more
  than 1 overlay every ~3 s.
- **Grade:** none, or a small +10 % contrast/+10 % saturation on the whole Short. Don't grade shots individually.

## 4. Sound
**Sources:** `sound effects/45_Viral_Meme_Sound_Effects_Pack/` (the user's pack, 45 meme sounds), the 50 editing and 35
transition packs beside it, `sound effects/trending_myinstants_2026-10/` (current trending meme sounds, unbranded; prefer
these), `sound effects/woosh-sound-effect.mp3`, `commentary-kit/sfx/` (sfx-kit, generated) and the bundled
`.agents/skills/media-use/audio/assets/sfx/`. The user calls ba-dum-tss, ka-ching, crickets and cartoon laughs outdated.

**Licence:** the user's packs are *not cleared* (`sound effects/README.md`): many are owned sounds (Vine boom, Taco Bell,
Windows, Among Us, Roblox oof, Snoop, "Emotional Damage", Mario…). On a personal-channel meme edit use them as the user
asked. Mention the Content ID risk once in the plan. **Campaign jobs (BOXABL, DraftKings) use sfx-kit instead.**

**Pick by moment (default map):**
| Moment | Sound |
|---|---|
| Shock / "WHAT" / jump-scare | trending `shocked-sound-effect`, `vine-boom`; `40_WHAT_Loud_Shock`, `41_Dramatic_Shocked_Hit` |
| Awkward / dumb statement | `03_Bruh_Sound_Effect`, `20_Confused_Cat_HUH`, wrong-answer buzzer (editing pack 29) |
| Punchline / laughing with him | trending `cat-laugh-meme-1`, `vine-boom`, `45_Victory_Tadaaaaa` |
| Fail / panic / oh no | trending `faaah` / `fahhh`, `chicken-on-tree-screaming`, slide-whistle fall (editing pack 44) |
| Suspense / reveal | trending `dun-dun-dun` brass |
| Cute / excited | trending `anime-ahh`, `11_Anime_Kawaii_Wow`, kids cheer / party horn (editing pack 24 / 27) |
| Money / flex | trending `rizz-sound-effect`, `04_Rizz_Bass_Drop` |
| Cut / transition | only `sound effects/sfxv2/` (each CapCut-20 transition's sound from `CAPCUT20`, added by `build-shorts.js`; plain cuts: `fast-whoosh.mp3` / `fast-swish.mp3`) |
| Censor | `26_Censored_Audio_Bleep` (only over a word that must go) |
| Hype | `17_MLG_Air_Horn_Blasts`, `45_Victory_Tadaaaaa` |

**When to use a sound (the only rule):** put a meme sound **only where something is funny**: a word or line that is funny, or
a moment whose implication is funny (a dumb or confident-wrong statement, a fail, an awkward silence, a shock, a face
change that sells the joke). If nothing funny happens, there is no sound. **The number of sounds is irrelevant:** no minimum,
no rate, no maximum, no filler for silent gaps, no sound just because there was a cut or a highlighted caption. A short clip
can have 3, a long one 30; each is judged only by whether it belongs there.

**Use each sound for what it means** (§ map above): choose the sound whose meaning matches the joke, not the one that is
handy. Read the line and the shot, say in the plan why this sound fits, and drop it if you can't.
- **Timing:** the onset of the sound lands on the funny word's first caption frame, or, when the funny part is the implication
  (a fail, a stare, a silence), on the first frame it becomes clear. A reaction sound (laugh, trombone, crowd) may follow the
  line by 0.2–0.4 s. Land within 2 frames of that anchor; snap the sound's onset, not its file start, to it.
- **Length and level (fixed rule):** a sound plays in full unless it's longer than 2 s (then 1.5 s, 0.2 s fade-out), at the same
  loudness as the speech. Put it in a speech gap where you can; otherwise the speech dips 6 dB for at most 1 s
  (`meme-fixed.py` does the trimming, matching and dips).
- **Don't stack** two meme sounds on one beat, and don't repeat the same sound so often that it stops being funny (twice per
  Short at most unless the repetition is the joke).
- **Cuts:** a plain cut gets no sound. A whoosh or transition sound is used only when the cut itself is part of a funny beat
  (a whip to a shock face, a sudden cut-away that delivers the joke).

**Music (mandatory on every clip, any length):** `commentary-kit/music/Ts Pmo.mp3` (170 s, −18.5 LUFS, peak −4.3 dBFS; the
user's pick, matching the quiet bed in both references; its licence is unknown, but the user wants it on campaign jobs too —
mention the Content ID risk once in the report).
- Start it at 0:00 of the clip, run it to the last frame with a 0.4 s fade-out, and trim it to the clip. Pick a start offset in
  the track only if the first seconds are quiet or clash with the opening line.
- **Level:** a constant, very low bed: gain about **−8 dB** on the file (≈ −26 LUFS, roughly 12 dB under the speech). Audible in
  every gap and on a good speaker, but never masking the source speech or a meme sound. No sidechain pumping.
- **Check by measuring, not by feel:** with speech and SFX muted, the bed alone sits 10–14 dB below the speech's integrated
  loudness; in the final mix, speech and every SFX stay clearly on top. If a loud SFX or shout makes the bed vanish or the bed
  covers a quiet word, change the gain by 1–2 dB and re-check; never remove it.
- **No beat sync.** Do not use `beat-sync-editing` or a beat grid on this command. Cuts follow speech and the punchline, SFX
  follow words, and the music is only a bed whose beat is ignored.

**Mix:** speech normalised to −16 LUFS, meme sounds at the speech's level (the frame-1 opener +20 %), music bed ~10–12 dB under,
−14 LUFS output.

## 5. Choosing the funny moments
The playbook's story-first test still applies: the clip must be funny on its own, with no setup outside it.
- **Works:** a reaction that goes too far, a confident wrong statement, an escalating bit, someone being caught, a chain of
  "no way" beats, a clean one-liner, a prank landing, an unexpected cut-away (a face-cam shot). Meme formats: the "wait
  what", the awkward pause, the fail, the yell.
- **Doesn't work:** needs outside context, the joke is the voice quality only, slurs or targeting a person, sexual or graphic
  content, tragedy. Reject those. The whole clip is the setup + ONE strong punchline (plus a callback at the end if it exists).
- **Length:** 10–35 s. Cut anything between the setup and the punchline that isn't needed.

## 6. The 7 workflow steps (as applied by /meme)
Run in order (`docs/editing-workflow.md`). Where this file and the workflow doc differ, this file wins; campaign rules win
over both. Paths: `downloads/meme_<id>.mp4` (reference: `downloads/memeref_<id>.mp4`), job folder `jobs/meme_<id>/`,
HyperFrames project `videos/meme-<id>/clipNN/`, output `output/meme/<Creator or topic>/`.

### Step 1: Read the input
- Source link(s) (required; ask and stop if missing), an optional reference, and the prompt. Prompt instructions outrank
  everything except campaign rules.
- Campaign sources follow their brief (and use the sfx-kit set); anything else has no campaign rules, but the playbook's safety rules apply.
- Download with `py -m yt_dlp` (≤1080p). If a link is private or blocked, report the exact error and continue with the rest.

### Step 2: Study the reference
- No reference: the style sheet is § 1–5 (`jobs/meme_ref/` holds the measured data). Copy it into `jobs/meme_<id>/style.md`.
- With a reference: `py tools/pipeline/study-reference.py downloads/memeref_<id>.mp4 jobs/meme_<id>/ref`, read every sheet,
  and write `style.md` with the same measurements as § 1 (cuts, shot lengths, caption style and colours, overlays, SFX onsets).
  Where it differs from § 1, follow the new reference. **Copy the editing, never the content.**

### Step 3: Find the moments
- Transcribe the full source: `py tools/pipeline/transcribe_lowmem.py <src> jobs/meme_<id>/t base.en en` (background for long
  videos). Read all of `segments.txt`, then `node tools/pipeline/score-moments.js jobs/meme_<id>/t/transcript.json --min 8 --max 35`.
- Find funny beats the transcript misses: laughter, shouting, loudness spikes (`ebur128` momentary peaks), sudden silence
  and reaction faces. Make contact sheets across the full runtime (one low-res overview, then denser sheets only around picks).
- Apply § 5. Write `candidates.md`: per pick, timestamps, "this clip is funny because…", the test result and risks, and the
  rejects with reasons.

### Step 4: Decide the effects for every cut
For each clip write `jobs/meme_<id>/clipNN/plan.md`:
- the one-line premise;
- one row per shot: `time | source time | speech | caption (colour) | overlay/tint | punch-in | SFX (file)`;
- the SFX list: per sound, the file path, its time, **what is funny** there (the word or the implication) and why this sound
  fits it; plus the licence note. No count target.

Order of choice: the user's prompt, the campaign rules, § 3–4 (or the new reference's `style.md`), then `docs/effects-catalog.md`.
**Effects are judged by timing and fit, not count** (every sound lands on something funny). **Show all plans and wait for
approval** before step 5.

### Step 5: Edit
Per clip:
1. **Cut** each shot from the source into `clipNN/shots/`; reframe with `track-faces.py --write` and `reframe.py` to the § 3
   canvas. Remove dead air with `cut-silences`; use `cut-mistakes` only if it's a stutter that isn't the joke. Never cut while
   someone is still speaking: each segment starts on a word and ends after the sentence or a pause (fixed rule).
2. **Captions:** the transcript's word timings, checked against the audio, in the § 3 colours.
3. **Build** with `build-shorts.js`. Per clip in `shorts.json`, the § 3 look is:
   `"style": "ysc", "barH": 0` (no headline, no bar: full-frame), `"fixedFeatures": false`, `"typedHook"` + `"hookEnd"`, `"capWords": 2`, `"capMax": 90`,
   `"capStroke": 6`, `"capY": 900` (≈47 % height; move with `capShift` off eyes), `"yscColor": "#FFE600"`, `"yscAlt": "#00E5FF"`
   with `"emphasis": [<word indices>]` (positions in `t/transcript.json`, not the words) for negation/emphasis words,
   `"actions": [{"t", "d", "text"}]` for white `*ACTION*` cards, `"punch": [[t, 1.2]]` on the punchline, `"sfx"`, `"overlays"`.
   For anything beyond the preset, hand-edit per
   `~/.claude/skills/viral-shorts/SKILL.md` § "HyperFrames editing". Use `shorts.json` `overlays`/`transitions`/`capAnims` from the
   motion-graphics library. Search `/hyperframes-registry` before hand-building an effect. Animate transforms and opacity only.
4. **Sound + fixed rules:** put each planned meme sound in the clip's `shorts.json` as `"sfxSrc": [{"t", "file", "ms", "why"}]`.
   Here `t` is the sound's start time in the clip and `ms` is where the sound starts inside its file. Add curse-word windows as
   `"bleep": [[a, b]]`. Then run `py tools/pipeline/meme-fixed.py jobs/meme_<id> clipNN ...` before building. It writes:
   - the speech, normalised to −16 LUFS with bleeps and dips;
   - the Ts Pmo `music_duck.wav`;
   - the frame-1 white flash, the awkward-moment sound and the frame-2 `cross-shake`;
   - every sound played in full (or 1.5 s if it's over 2 s) and level-matched to the speech, as `"sfx"`.
5. **Check:** `bash tools/pipeline/hf.sh check <dir>` with 0 errors; snapshot the cold open, each punchline and the last frame.

### Step 6: Clip as many as pass
Build every candidate that passed step 3. No fixed count; stop when the next-best moment fails. Never reuse the same punchline
in two clips or mix sources in one clip. This PC has 3.6 GB RAM, so run at most about 3 renders at once.

### Step 7: Render, QC, report
- **Render:** `bash tools/pipeline/render-shorts.sh videos/meme-<id> "output/meme/<...>"` (it never overwrites; recycle old files
  first). Campaign jobs follow the brief's filename rule.
- **QC per clip:** `qc-sheet.sh` and `ysc-qc.sh` (length, −14 LUFS, no silence), `blackdetect`/`freezedetect`; re-transcribe the
  render and check every caption word matches the audio; the typed hook types with the typing sound and is answered by the clip; check that every SFX lands within 2 frames of its funny word or moment
  and never covers speech; **the music bed is present from first to last frame, 10–14 dB under the speech, and speech/SFX stay audible over it**; read the frames (captions off the eyes, no forbidden content). **SFX check:** every sound sits on something funny (a funny word or a funny implication) and
  its meaning fits the joke, none is filler, none is off its moment by more than 2 frames, none is stacked on another; the
  number of sounds is not checked. **Reference match:** 1–2 word captions in the yellow/cyan scheme, cut length median ≈ 2 s, one punchline with a punch-in. Fix and re-render
  anything that fails.
- **Report** in `output/meme/<...>/clips_report.md`: per clip the filename, source timestamps, duration, the joke in one line,
  the SFX list (file, time, why), the effect log and QC pass/fail; plus the rejected moments, blockers and any licence flags.
- **Keep the job files.** The user runs `/cleanup-project` when ready.

## Transitions and transition SFX (user rule, 2026-11-07)
- **Main choices, in every edit:** CapCut's 20 popular transitions: Pull In, Pull Out, Camera Shake, Whirl, Zoom In, Zoom Out, Blur, Glitch, Flash, Spin, Slide, Rotate, Shake, Zoom Blur, Distortion, Cube, Swipe, Wipe, Split, Light Leak. Pick every transition from these first, also when motion graphics are involved (split-screen panels, explainers, montages, slideshows, overlay cards): each scene change between shots or graphics uses one of the 20, not another engine's or the registry's version of the same name. Use another transition only when none of the 20 fits. CapCut name -> preset: the "Main set" table at the top of `motion-graphics-library/EFFECTS_INDEX.md` (`CAPCUT20` in `mgl.js`, ai-video-editor workspace).
- **Transition SFX:** only the user's sfxv2 pack (`sound effects/sfxv2/` in ai-video-editor; master copy `sfxv2/` in the vault repo). The user's files come first; `generated/` holds synthesized fallbacks, currently unused. Each of the 20 has its sound, peak and volume in `CAPCUT20`, and every file is 1.5 s or shorter. `build-shorts.js` adds the sound automatically with the hit on the cut, so never add a second whoosh for the same cut (`"sfx": false` on a transition skips it, `"sfxVol"` sets its volume).
- **Any other engine** (a hand-built HyperFrames composition, Remotion, ffmpeg, OpenMontage): run `node motion-graphics-library/mgl.js --capcut20`, port the transition's motion exactly (same values, durations and eases), and place its sfxv2 sound with the peak on the cut at its volume.
- **Motion graphics keep their own small sounds** (typing ticks, pops, shimmers, rises). The sound on a scene change is the transition's sfxv2 sound; the builder drops a panel split's synthesized hit where a transition sound already lands.
- The skill's or command's own limits still apply: transition sounds count toward its SFX cap, and its cut style (e.g. hard cuts by default) decides how many transitions there are. Not for the cartoon/3D animation skills (cartoon-audio-short, cartoon-3d-short, 3d-short).
