---
name: editor
description: /editor — the one combined editing skill. Merges the general editing skills (/youtube-style-clip, /viral-shorts, /puregrit, /commentary-short, the cutting tools cut-mistakes / cut-silences / auto-editor / beat-sync-editing, and the HyperFrames toolset) into one conflict-free workflow that always runs the user's 7 steps (input → reference study → story moments → effects per cut → edit → clip all that pass → render). Picks a style mode from the prompt, the source or the reference, resolves every rule clash with one precedence order, and hands deep technical detail to the original skill files. Holds no campaign briefs: BOXABL and DraftKings jobs go to /boxabl and /gab. Use when the user types /editor, or asks for a non-campaign clip / Short / edit job without naming a different skill.
argument-hint: <source link | file> [reference link | file] [instructions]
---

# /editor: every editing skill in one, following the 7-step workflow

Workspace `C:\Users\manth\OneDrive\Desktop\AI-Video-Editor` (cloud: the repo root). Tools are in `tools/pipeline/`.

**Read first, every job:**
1. `docs/editing-workflow.md`: the 7 steps and their commands. This skill runs them exactly, with the mode values below.
2. `docs/clipping-playbook.md`: story-first rules, safety, and workflow traps.
3. `docs/effects-catalog.md`: the effects menu.

Then read the chosen mode's source file (see §1) for its full detail. That file holds the detail; this skill settles every conflict between files.

The separate skills still exist. When this skill runs, it wins any clash between them.
Never publish, schedule or boost anything. Never ask for a clip count, timestamps or rules. Ask only for a missing source link, or for a choice only the user can make.

## 0. One precedence order (resolves every conflict)
1. **Safety and law:** no detection-evasion tricks (mirroring, pitch/speed shifts, noise); no fabricated facts, quotes or visuals; no meaning-changing re-cuts; never bypass DRM, private videos or region locks; ask before installs, paid services, and downloads the user didn't send.
2. **Any brief or platform rules the user gives for this job** (none are built in).
3. **The user's prompt** for this job.
4. **The reference video's measured style** (`study.json` + sheets → `style.md`), when one is sent.
5. **The mode's defaults** (§1–§2).
6. **`docs/clipping-playbook.md`**, then **`docs/effects-catalog.md`** best fit.

Older notes (the retention playbook's 2–3 s cadence and "SFX on frame 1") are superseded by the measured looks below.

## 1. Pick the mode (Step 1 of the workflow)
Take the first match:

| # | Trigger | Mode | Full detail in |
|---|---|---|---|
| 1 | Prompt says "PureGrit" | **puregrit** (never chosen automatically) | `~/.claude/skills/puregrit/SKILL.md` + `reference.md` |
| 2 | Prompt asks for a commentary Short / topic for What The Tape Shows | **commentary** | `~/.claude/skills/commentary-short/SKILL.md` |
| 3 | Prompt asks for narration / "viral narrated" / teaser hook | **viral** | `~/.claude/skills/viral-shorts/SKILL.md` + its 3 guides |
| 4 | Anything else | **ysc** (the measured hit-clip look) | `~/.claude/skills/youtube-style-clip/SKILL.md` + `reference.md` |

**Combining modes:**
- **A reference video** changes the look inside the chosen mode (caption style, pacing, effects, hook pattern, narration) but never overrides safety or a brief the user gave.
- **Campaign jobs are out of scope.** BOXABL sources or campaigns use `/boxabl`; DraftKings / ClipFarm creators (Cheddy, Nick Nayersina, FlightReacts) use `/gab`. If one arrives here, say so and switch to that skill.

## 2. Mode values (where the skills used to disagree)

| | ysc | viral | puregrit | commentary |
|---|---|---|---|---|
| **Length** | 10–17 s stunt, 15–35 s story (≤45) | 13–35 s | 40–60 s | 60–120 s (aim 75–90) |
| **Opening** | frame 1 mid-action, strongest image/line | narrator hook over a teaser that shows the build-up, never the result | cold open on the tensest line/reaction | hook fact over the strongest footage |
| **Cut rate** | 0.8–1.6 cuts/s | 0.5–1 s shots at high energy, 1.5–3 s holds on proof | a cut every 1.7–2.5 s | a shot change every 2–5 s |
| **Narration** | none | original Kokoro script, ~3 words/s | one setup sentence (Kokoro) at ~4–8 s | full narration, plus a MY TAKE section |
| **Captions** | one word, mid-frame (55–60%), yellow, green emphasis | one word, synced after the VO mix | 2–3 uppercase words, one glowing coloured keyword | word-by-word animated (build_short.py) |
| **Headline/title** | fixed black bar, ≤6 words, 1 red/yellow keyword + emoji | bar | no bar unless `hook` is set; reaction labels | persistent title [white, yellow] |
| **SFX** | ≤6, impacts/reveals only | ≤6 | ≤6 | about one per beat |
| **Flashes** | ≤2 | ≤2 | ≤2 | wipes/freeze per script |
| **Music** | ducked bed required, no silence | ducked about −10 dB under VO | continuous bed | −24 dB, −34 under soundbites |
| **Grade** | `ysc` | `ysc` | `puregrit` | built-in |
| **Framing** | fill 9:16, no letterbox | fill; pan with the subject | tight face crops | 4:3 band over a blurred fill |
| **Celebrities** | borrowed fame only if the brief allows | if the brief allows | flag TV/league footage | primary sources; credit is not permission |
| **Brand** | — | logo only if a brief requires it | channel initials logo | description ends with the AI-voice line + `#shorts #commentary` |
| **Builder** | `build-shorts.js` style `ysc` | `ysc` + VO + music | style `puregrit` | `scripts/build_short.py` (ffmpeg, not HyperFrames) |
| **Output** | `output/<source>/` | `output/viral-shorts/<slug>/` | `output/<source>/` | `output-commentary/<slug>/` |

**One-off rules don't carry over:** a past job's exceptions (e.g. the Graham Stephan job's "no music, only narration") applied only to that job.

## 3. The 7 steps with this skill

**1. Input.**
- Find the source link(s), the reference and the prompt, then pick the mode (§1).
- Downloads: links the user sends are fetched without asking. Sources Claude finds itself (commentary) need a yes first.
- In the cloud, if YouTube blocks yt-dlp, stop and ask the user to download the video on the PC.
- Run `bash tools/pipeline/preflight.sh`.

**2. Study the reference** (skip if there is none).
- Run `py tools/pipeline/study-reference.py <ref> <job>/ref`, read every sheet and write `style.md`.
- Precedence slot 4: the reference's measured values replace the mode defaults in §2, but never the brief.
- **Narration:**
  - Follow the reference: narrated reference → original Kokoro narration; un-narrated → original audio.
  - If the mode (ysc) or a brief the user gave bans AI voice, use the original audio plus a text hook and tell the user.
- Copy the editing, never the footage, wording, frames, logos or music.

**3. Story moments.**
- Every pick is a standalone mini-story (playbook §1, the 8-question test), sized to the length row in §2 or the reference length.
- Mode-specific picks:
  - **puregrit:** one surprising moment with a visible reaction.
  - **viral:** pick the payoff shot and a teaser excerpt.
  - **commentary:** follow its topic/research/sources/script steps (1–5) here instead.
- Write `candidates.md`, rejects included.

**4. Effects per cut.**
- Write `plan.md`, one row per cut: time | shot | transition | motion | text | SFX | music | narration line.
- Choose in the §0 order, inside the §2 caps. Never exceed the reference's own effect density.
- `beat-sync-editing` applies only when there is music and a beat grid.

**5. Edit.**
- **Cut:** `cut-mistakes` → `cut-silences` (or `auto-editor`, cuts only: no speeding up of speech or footage people watch), then `check-bounds.js`.
- **Frame:** set crops on frames of `tight.mp4`, then run `track-faces.py`, then `reframe.py --grade <§2 grade>`.
- **Voice** (if the mode allows):
  - `bash tools/pipeline/hf.sh tts` + `add-vo.py`;
  - if `hf.sh tts` reports Kokoro missing, use `~/.claude/skills/commentary-short/scripts/synth_lines.py`;
  - trim words, never speed up the voice.
- **Build:**
  - Build with the §2 builder.
  - Anything beyond the preset is a HyperFrames hand edit:
    - `hyperframes-core` for structure;
    - `hyperframes-keyframes` for zooms and camera moves;
    - `hyperframes-registry` first for any named transition or effect;
    - `hyperframes-animation` and `hyperframes-creative` for text and motion;
    - `hyperframes-audio` for mixing;
    - `media-use` for grades and media.
  - Animate transforms and opacity only.
  - `hf.sh check` must show 0 errors; look at the `hf.sh snapshot` frames.

**6. Clip all that pass.** Every candidate that passes the story test and the brief, no padding, never mixing sources. At most ~3 renders at once on this PC.

**7. Render, QC, report.**
- **Render** with `render-shorts.sh` (it never overwrites: recycle old files first), or `build_short.py` for commentary.
- **QC on every file:**
  - `ysc-qc.sh`, judged against the mode's §2 length and cut rate, not the script's 17 s default;
  - `qc-sheet.sh`, `blackdetect`, `freezedetect`;
  - re-transcribe the final, plus `clean-check.py` when cursing is banned;
  - the standalone test on the final file;
  - the mode's own checklist (ysc §9, viral `EDITING_CHECKLIST.md`, puregrit §8, commentary §9);
  - the reference match (cuts/s within ±25%, same hook and caption style, SFX ≤ the reference's).
- **Report:** per clip, the story in one line, timestamps, length, the effect log, QC pass/fail and the music credit. Also list rejects, blockers, and whether narration was used and why.
- **Keep the job files:** `/cleanup-project` runs only when the user asks.

## Transitions and transition SFX (user rule, 2026-11-07)
- **Main choices, in every edit:** CapCut's 20 popular transitions: Pull In, Pull Out, Camera Shake, Whirl, Zoom In, Zoom Out, Blur, Glitch, Flash, Spin, Slide, Rotate, Shake, Zoom Blur, Distortion, Cube, Swipe, Wipe, Split, Light Leak. Pick every transition from these first, also when motion graphics are involved (split-screen panels, explainers, montages, slideshows, overlay cards): each scene change between shots or graphics uses one of the 20, not another engine's or the registry's version of the same name. Use another transition only when none of the 20 fits. CapCut name -> preset: the "Main set" table at the top of `motion-graphics-library/EFFECTS_INDEX.md` (`CAPCUT20` in `mgl.js`, ai-video-editor workspace).
- **Transition SFX:** only the user's sfxv2 pack (`sound effects/sfxv2/` in ai-video-editor; master copy `sfxv2/` in the vault repo). The user's files come first; `generated/` holds synthesized fallbacks, currently unused. Each of the 20 has its sound, peak and volume in `CAPCUT20`, and every file is 1.5 s or shorter. `build-shorts.js` adds the sound automatically with the hit on the cut, so never add a second whoosh for the same cut (`"sfx": false` on a transition skips it, `"sfxVol"` sets its volume).
- **Any other engine** (a hand-built HyperFrames composition, Remotion, ffmpeg, OpenMontage): run `node motion-graphics-library/mgl.js --capcut20`, port the transition's motion exactly (same values, durations and eases), and place its sfxv2 sound with the peak on the cut at its volume.
- **Motion graphics keep their own small sounds** (typing ticks, pops, shimmers, rises). The sound on a scene change is the transition's sfxv2 sound; the builder drops a panel split's synthesized hit where a transition sound already lands.
- The skill's or command's own limits still apply: transition sounds count toward its SFX cap, and its cut style (e.g. hard cuts by default) decides how many transitions there are. Not for the cartoon/3D animation skills (cartoon-audio-short, cartoon-3d-short, 3d-short).

## 4. Always
- Read analytics only when the user asks.
- YouTube uploads: paid promotion No; made for kids No; altered content No; confirm before Schedule/Save.
- Music is licensed or CC BY (credit from `commentary-kit/music/CREDITS.txt`); never rip songs.
- Check every frame for third-party logos, other big creators, minors, alcohol/drugs and banned content.
