---
description: Edit a source video (speech, podcast, interview, talk) into "motivational" Shorts. Finds the strongest motivational quotes, stories and lessons in the original audio and illustrates each line with motion graphics that match exactly what the speaker says, in the reference's split-screen look (graphic panel on top, speaker below). No narrator. Every graphic makes its own sound.
argument-hint: <source video file | Google Drive link | YouTube url> [reference file/url]
---

# /motivational: motivational quotes and stories, illustrated line by line with motion graphics

Source: $ARGUMENTS

If no source was given above, ask for the link or file and stop. Workspace: `C:\Users\manth\OneDrive\Desktop\AI-Video-Editor`
(cloud: the repo root), tools in `tools/pipeline/`; Google Drive links download with `bash cloud/fetch-drive.sh "<link>"`.
Run `bash tools/pipeline/preflight.sh` first. Read `docs/clipping-playbook.md` and
`motion-graphics-library/EFFECTS_INDEX.md` (the panel section) before planning. /motivational always runs the **7 workflow
steps** (`docs/editing-workflow.md`), written out for this format in § 7; where they differ, this file wins and campaign
rules win over both. Never publish, schedule or upload. Show the plans before editing, unless the prompt says no plan
approval is needed.

**Fixed choices for this command (user's, 2026-10-28):**
- **Original audio only.** No AI voice, no narration, no typed hook, no riser. Build with `"fixedFeatures": false` (no opening
  zoom/woosh, no riser, no loop zoom).
- **Every time a motion graphic or animation is on screen, the screen splits:** graphic panel on top, speaker below. With no
  graphic, the speaker fills the frame. (The builder does this automatically from `"panel"`.)
- **No sound files, except transition sounds.** Don't use sfx-kit, the rest of the `sound effects/` folder or any other file sound. The one exception (user rule 2026-11-07): scene-change transitions are picked from CapCut's 20 and carry their `sound effects/sfxv2/` sound (`build-shorts.js` adds it and drops the split's synthesized hit there). The motion graphics make their
  own sounds: each panel graphic generates a sound shaped to its animation (tick per typed word, shimmer while an icon
  draws, rise while a bar/counter/ring fills, whoosh as a card slides, pop as a quote or screen appears).
- **Music: TBD.** The user will send the motivational track to use on every clip. Until then: no music. Make a silent
  `clipNN/music_duck.wav` (the builder needs the file). **MUSIC TRACK: _(not set yet)_**. When it's set, write its path here,
  build `music_duck.wav` from it at about −8 dB (≈12 dB under the speech) with a 0.4 s fade-out, and credit it if required.

## 0. Motion-graphics direction: prompt-motion.com (applies to ALL graphics in this command)
The user's reference for every motion graphic here is **prompt-motion.com**, a gallery of motion videos made with Claude Opus
5.5. Its direction (the site's improved "showreel" template, read 2026-10-28) is the rulebook; the § 1 video only supplies the
split-screen structure and the timing of graphics to words. Where they differ, this section wins.
- **One concept per clip, and every graphic is made out of the previous one.** Shapes, type and colour transform into the
  next graphic (a title word becomes the icon, a list row becomes the counter, the timeline bar becomes the next title's
  underline) instead of cutting or fading. Plan these hand-offs in the visual script.
- **One typeface** (Montserrat; accents are italic in the accent colour, no serif), **at most three colours plus black and
  white** per clip, set with `"panelAccent"` and each element's `color`. One consistent camera language.
- **Show range across a clip:** kinetic type, shape morphing/drawing, a data moment (counter, timeline, people), and a
  closing title. Give each a fair share.
- **Banned:** particle bursts, glows, lens flares, camera shake, RGB split, crossfades, generic gradients, bouncy easing,
  anything that looks like a template, and **holds longer than half a second**: something must move or build at least every
  0.5 s while a graphic is on screen (new element on the next spoken word, a fill, a draw, the panel's slow drift).
- **Motion:** spring/exponential easing (`expo.out`), and **blur that follows speed** on fast moves; elements leave by moving
  and blurring out, never by a plain fade.
- **Rhythm:** something happens on every beat; here the beat is the speaker's words and phrases (no music grid until the
  music is set). The last graphic should be the strongest moment; where the story allows, end on a frame that matches the
  opening so the clip loops.
- **Sound written in code:** every graphic generates its own sound (§ fixed choices), plus a **hit on each scene change**
  (each time the screen splits). Prompt Motion does this with the Web Audio API; here `panel.js` synthesises the same kinds of
  sounds with ffmpeg at build time.
- **Storyboard first, then build without asking:** show a beat-by-beat storyboard (the visual script) before building, and
  **check one frame per beat before the full render** (`hf.sh snapshot` at every graphic's word); fix anything cluttered, off
  its word, overlapping or hard to read.
- Prompt Motion renders at 60 fps with blended sub-frames for motion blur; this pipeline renders at 30 fps, and the blur on
  fast moves is the CSS blur above. Videos and prompts on the site belong to their creators: copy the principles, never a
  specific video.

## 1. The reference, measured (2026-10-28)
Reference: `downloads/motivref_a.mp4` (Drive file a783…, 85.9 s, 576×1024, 24 fps; a creator explaining the "triple loop"
storytelling method). Study data: `jobs/motiv_ref/a/` (`study.json`, 8 frame sheets, transcript). Copy the editing, never the
content.

| | Measured |
|---|---|
| Layout | Alternates **split** (black motion-graphics panel top ≈ 2/3, speaker band bottom ≈ 1/3) and **full-frame speaker**; switches on the line, median shot 5.2 s (0.55–22.6 s) |
| Graphics | Built **word by word**: each element appears on the word that names it (title words as spoken; "hook, a body, and a payoff" → those three sections fill a script page; "so many people" → a ring of people icons fills; "first five seconds" → a timeline marker at 0:05) |
| Look (superseded by § 0) | Dark radial background, white bold titles with one **italic serif accent word** ("The Ultimate *Storytelling Format.*"), **neon line icons that draw themselves on** with a glow, a consistent colour code per concept (red = hook, yellow = intensifier, green = rehook) |
| Captions | One word at a time, white, small (~60 px at 1080 wide), soft shadow, no outline; on the seam between panel and band in split, mid-frame in full |
| Sound | A soft sound on almost every graphic entrance (≈ 0.7 per second): ticks, pops, small whooshes. Speech always on top |
| Pace | 3.6 words/s speech, little dead air; no flashy transitions (hard switches between layouts) |

## 2. What to clip (motivational moments)
Every clip is a standalone mini-story that leaves the viewer feeling something (playbook § 1). Look for:
- **A quote with its context:** one strong line ("Discipline is choosing what you want most over what you want now") plus the
  setup that makes it land. The quote must be the speaker's own words in the source; never invent or rephrase a quote.
- **A story:** struggle → turning point → lesson (a failure, a decision, a comeback, a number that changed).
- **A principle or framework:** "3 things…", "the reason most people fail…", "the one habit…" with each part named.
- **A reframe:** the moment the speaker flips how you see something ("It's not that you lack time…").
Reject: needs outside context, generic hype with no substance, preachy without a story or reason, medical/financial
promises, anything attacking a person or group. Length **25–60 s** (up to ~90 s only if the story needs it).

## 3. The look (builder settings)
Per clip in `shorts.json`: `"style": "ysc", "barH": 0` (no headline bar), `"fixedFeatures": false`, `"capMax": 62`,
`"capStroke": 0`, `"yscColor": "#FFFFFF"`, `"yscAlt": "#39E75F"` with `"emphasis": [<word indices>]` for 1–2 key words,
`"bandFocus": "50% 32%"` (vertical crop of the speaker in the band; adjust so the face sits in the band), optional
`"splitCapY"` (default 1180), `"panelSfxVol"` (default 0.35), `"panelAccent"` (the clip's accent colour; § 0 palette), and `"panel": [...]` (§ 4). No punch-in spam; at most one
`punch` on the most emotional full-frame line. No transitions between layouts (hard switch, like the reference).

## 4. The visual script (the heart of this command)
Write `clipNN/visual.md` before building: a table with one row per graphic,
`time | exact words spoken | graphic kind | content | colour | why it matches`. Then turn it into `"panel"`.
- **Match the words literally and on time:** each element's `t` (and per-word `times` / per-item `t`) is the start time of
  the word that names it, from `clipNN/t/transcript.json` (land within 0.1 s). If the speaker says "mountain", draw the
  mountain icon on "mountain"; if they list three things, each row appears on its own word; numbers count up on the number.
- **Keep it on screen while the topic continues** (`e`), and clear it when the speaker moves on. Graphics closer than 0.5 s
  merge into one split. Leave the speaker full-frame for emotional lines (eye contact, a pause, the payoff line) — aim for
  roughly half the clip split, like the reference.
- **One idea per panel:** a title plus at most 2–3 elements at once. Keep a colour code for recurring concepts (≤ 3 colours, § 0).
- **Hand-offs (§ 0):** for each change of graphic, write how the next one is made out of the previous (where it appears, which
  shape or colour carries over), and place the next element where the last one was so the eye follows it.
- **No hold over 0.5 s:** check the table: while a graphic is on screen, a new element, draw or fill lands at least every 0.5 s
  or on every phrase.
- **Accuracy:** graphics only show what the speaker says (no invented stats, quotes or claims). Write numbers exactly as said.

Panel kinds (`motion-graphics-library/panel.js`, see EFFECTS_INDEX.md):
| Kind | Use for | Key fields |
|---|---|---|
| `title` | the topic or the quote's headline, typed word by word | `text` (`*accent*` in italic serif), `times` (word starts) |
| `icon` | a concrete thing or idea (mountain, flame, trophy, clock, brain, heart, stairs, target, rocket, lightbulb, money, chart-up/down, check/cross, lock, eye, dumbbell, calendar, star, person, infinity, arrows) | `name`, `color`, `label`, `x`, `y`, `size`, `draw` |
| `list` | steps, reasons, "3 things" | `items: [{text, t, color}]` |
| `quote` | the motivational line itself, revealed as spoken | `text`, `times`, `author` (the speaker) |
| `counter` | a number, money, years, percentages | `from`, `to`, `prefix`, `suffix`, `label`, `dur` |
| `timeline` | progress, time, "day 1 → year 5" | `marks: [{t, at 0..1, label, color}]` |
| `people` | "most people", "everyone", crowds | `n`, `color`, `label`, `fill` |
| `compare` | before/after, wrong/right, them/you | `left`/`right: {title, icon, color, t}` |
| `document` | a plan, a script, a routine with parts | `title`, `sections: [{t, label, color, lines}]` |
| `screen` | show a moment from the same source inside the panel | `ms` (media time), `w`, `h` |
Need something not listed? Add it to `panel.js` with a test (see its self-check), or use a HyperFrames registry block.

## 5. Sound
Only the graphics' own generated sounds (§ fixed choices) under the original speech. Speech first; if a generated sound
masks a word, lower `panelSfxVol` or drop that element's sound with `"sound": false`. Output −14 LUFS (render-shorts).
Music: none until the user sets the track above.

## 6. Rights and safety
Use sources the user may clip (their own, permitted, or a campaign's approved list). Credit the speaker in the caption and
report. No AI-generated visuals of real people. Run `clean-check.py` on the final transcript and every on-screen word.

## 7. The 7 workflow steps (as applied by /motivational)
Paths: source `downloads/motiv_<id>.mp4`, job `jobs/motiv_<id>/`, project `videos/motiv-<id>/clipNN/`, output
`output/motivational/<speaker or topic>/`.
1. **Input:** source (and optional reference; with none, § 1 is the style sheet). Download (Drive: `cloud/fetch-drive.sh`;
   YouTube: `py -m yt_dlp`, ≤1080p). Report a blocked link and continue.
2. **Reference:** with a new reference, `py tools/pipeline/study-reference.py <ref> jobs/motiv_<id>/ref`, read every sheet,
   write `style.md` like § 1; where it differs, follow it. Without one, copy § 1 into `style.md`.
3. **Moments:** transcribe the whole source (`py tools/pipeline/transcribe_lowmem.py <src> jobs/motiv_<id>/t base.en en`),
   read all of `segments.txt`, run `node tools/pipeline/score-moments.js jobs/motiv_<id>/t/transcript.json --min 20 --max 75`,
   pick by § 2 and the playbook's judging rules, and write `candidates.md` (story/quote in one line, timestamps, the 4-part
   score, why it moves people, risks, rejects).
4. **Visual script = storyboard:** per clip, `visual.md` (§ 4, following § 0) and the § 3 settings; no SFX list (the graphics
   make the sounds). Show the storyboards, then build without further questions (unless the prompt says no approval needed).
5. **Edit:** cut the moment into `clipNN/base.mp4` (`cut-silences`/`cut-mistakes` only on dead air and flubs, never inside a
   quote), `reframe.py` to 9:16 full-frame on the speaker, transcribe the clip (word times for § 4), silent
   `music_duck.wav` until the music is set, write `shorts.json`, then `node tools/pipeline/build-shorts.js videos/motiv-<id> clipNN`,
   `bash tools/pipeline/hf.sh check` (0 errors), then **one snapshot per beat** (`hf.sh snapshot` at every graphic's word) and
   look at each before the full render: fix clutter, overlap, unreadable text, anything off its word or breaking § 0.
6. **Clip all that pass:** every candidate that passes; never two clips of the same story; at most ~3 renders at once.
7. **Render, QC, report:** `bash tools/pipeline/render-shorts.sh videos/motiv-<id> "output/motivational/<...>"`. QC per clip:
   `qc-sheet.sh`, `ysc-qc.sh`, re-transcribe and match captions; **every graphic appears on its word (±0.1 s) and shows what is
   said**; the screen is split exactly while a graphic is on screen; the face sits in the band; captions on the seam in split;
   **no sound files used** (only generated `pn*` sounds); speech on top; **§ 0 check:** one typeface, ≤ 3 colours, no glow,
   gradient, bounce, shake, crossfade or particle burst, no graphic holding still > 0.5 s, each graphic grows out of the last. Report in `clips_report.md`: per clip the filename,
   source timestamps, duration, the quote/story in one line, the visual script summary, QC results, and rejects.
   Keep the job files.

## Transitions and transition SFX (user rule, 2026-11-07)
- **Main choices, in every edit:** CapCut's 20 popular transitions: Pull In, Pull Out, Camera Shake, Whirl, Zoom In, Zoom Out, Blur, Glitch, Flash, Spin, Slide, Rotate, Shake, Zoom Blur, Distortion, Cube, Swipe, Wipe, Split, Light Leak. Pick every transition from these first, also when motion graphics are involved (split-screen panels, explainers, montages, slideshows, overlay cards): each scene change between shots or graphics uses one of the 20, not another engine's or the registry's version of the same name. Use another transition only when none of the 20 fits. CapCut name -> preset: the "Main set" table at the top of `motion-graphics-library/EFFECTS_INDEX.md` (`CAPCUT20` in `mgl.js`, ai-video-editor workspace).
- **Transition SFX:** only the user's sfxv2 pack (`sound effects/sfxv2/` in ai-video-editor; master copy `sfxv2/` in the vault repo). The user's files come first; `generated/` holds synthesized fallbacks, currently unused. Each of the 20 has its sound, peak and volume in `CAPCUT20`, and every file is 1.5 s or shorter. `build-shorts.js` adds the sound automatically with the hit on the cut, so never add a second whoosh for the same cut (`"sfx": false` on a transition skips it, `"sfxVol"` sets its volume).
- **Any other engine** (a hand-built HyperFrames composition, Remotion, ffmpeg, OpenMontage): run `node motion-graphics-library/mgl.js --capcut20`, port the transition's motion exactly (same values, durations and eases), and place its sfxv2 sound with the peak on the cut at its volume.
- **Motion graphics keep their own small sounds** (typing ticks, pops, shimmers, rises). The sound on a scene change is the transition's sfxv2 sound; the builder drops a panel split's synthesized hit where a transition sound already lands.
- The skill's or command's own limits still apply: transition sounds count toward its SFX cap, and its cut style (e.g. hard cuts by default) decides how many transitions there are. Not for the cartoon/3D animation skills (cartoon-audio-short, cartoon-3d-short, 3d-short).
