---
description: Edit a source video into a "mark" Short, a copy of the layout and structure of rKfzqYYoCkg. An AI narrator hooks over reused, reordered teaser shots, narrates the context without revealing the result, a light-leak flash hands over to the original audio for the payoff, and the Short loops back to the opening shot.
argument-hint: <source video file | YouTube url> [reference url] [campaign: boxabl|gab|none]
---

# /mark: narrator-hook Short in the rKfzqYYoCkg layout

Source: $ARGUMENTS

If no source was given above, ask for the link or file and stop. Workspace: `C:\Users\manth\OneDrive\Desktop\AI-Video-Editor`,
tools in `tools/pipeline/`. Run `bash tools/pipeline/preflight.sh` first. Read `docs/clipping-playbook.md` and
`docs/effects-catalog.md`. /mark always runs the **7 workflow steps** (input → reference study → story moments → effects per
cut → edit → clip all that pass → render), written out for this format in § 6; § 1–5 are the style sheet. Never publish,
schedule or upload. Show the plans (moment, narration, shot list) before editing.

**Campaign rules override everything here.** If the source belongs to a campaign (BOXABL → `.claude/commands/boxabl.md`,
DraftKings → `~/.claude/skills/gab/SKILL.md`), read that brief first. For example, BOXABL bans Elon Musk footage, outside
celebrity cutaways, Elon-centred hooks and hashtags in the caption. If the brief bans AI voiceover, stop and tell the user:
this format can't be made without the narrator.

## 1. The reference, measured (2026-10-25)
Reference: https://youtube.com/shorts/rKfzqYYoCkg ("A billionaire lives in this tiny house? @BOXABL", Daily Highlights), cut from
FaZe Rug's "Visiting Elon Musk's $50,000 Tiny Home!" (uu5aORByttg). Shots were matched to the source by frame similarity.

- **Length:** 12.6 s, 1080×1920 at 60 fps.
- **Cuts:** 12 shots, 0.71 cuts/s overall. During the narration the shots run 0.45–1.0 s (median 0.8 s).
- **Loudness:** −9.4 LUFS integrated with LRA 1.6, so the mix is loud and dense with no quiet gaps.

| Time (s) | Shot | Source time | Audio | Words on screen |
|---|---|---|---|---|
| 0.00–0.53 | **FaZe's reaction face** (the payoff reaction, shown first) | 7:26 | narrator: "He did not" | HE / DID / NOT |
| 0.53–1.03 | **Finger tapping the mirror's heat button** (the payoff action, shown early) | ~6:06 | "expect" | EXPECT |
| 1.03–1.50 | Two-story BOXABL, wide | 3:17 | "this." | THIS |
| 1.53–2.10 | FaZe to camera outside, **red dashed circle + red arrow** on his face | 0:03 | "This guy just" | THIS / GUY / JUST |
| 2.13–2.55 | Walking in through the door | — | "went inside" | WENT / INSIDE |
| 2.58–3.10 | BOXABL vest from behind | — | "this tiny" | THIS / TINY |
| 3.12–4.13 | House lifted by crane (**slow push-in**), red arrow | — | "house to find out why" | HOUSE / FIND / OUT / WHY |
| 4.17–5.43 | Elon Musk podcast cutaway, red circle + arrow (outside footage) | not in source | "Elon Musk bought this" | ELON MUSK / BOUGHT / THIS |
| 5.45–6.15 | **Same two-story wide shot again**, red arrow | 3:17 | "BOXABL for" | BOXABL / FOR |
| 6.15–7.00 | Same wide shot + **money-rain overlay** | 3:18 | "$50,000." | $50,000 |
| 7.02–8.45 | Bathroom/kitchen interior, slow push | — | "And he was shocked" | AND / WAS / SHOCKED |
| 8.47–9.04 | **Finger on the heat button again** | ~6:06 | "by this feature." | BY / THIS / FEATURE |
| **9.04–9.20** | **Orange-white light-leak burn flash** + impact, revealing FaZe | — | narrator stops | FEATURE |
| 9.20–10.0 | FaZe side close-up | 6:10 | original: "Is this a heated mirror, bro?" | IS / THIS / HEATED |
| 10.0–10.5 | The mirror, wide | 6:10 | original | MIRROR / BRO |
| 10.5–11.9 | FaZe pressing the button, cameraman in shot | 6:11–6:12 | original: "Like what does that do?" | LIKE / WHAT / THAT / DO |
| 11.93–12.6 | **Opening shot again**, darkened, **manga speed lines**, loud hit | 7:26 | hit SFX | none |

**What makes it work:**
- **The teaser is the payoff, borrowed.** The first two shots come from the end of the story: the reaction and the action.
  They play while the narrator says "He did not expect this", so the viewer sees the result before knowing what it is.
- **Shots repeat on purpose.** The button close-up plays 3 times (hook, "this feature", payoff), the wide house twice, and the
  reaction face twice (open and close, which makes the loop). Each repeat lands on the word that names it.
- **Context shots follow the narration, not the source order.** Each phrase gets the shot that illustrates it, pulled from
  anywhere in the source.
- **The narrator never gives the answer.** It sets up who, where and why, then stops on "shocked by this feature". The payoff
  plays in original audio and in real order. Even then, the answer (FaZe's video says the mirror heats up to stop misting) is
  never given: the Short cuts to the reaction face and loops.
- **Every cut is timed to a sound.** Onsets measured at 1.03, 1.49, 2.26, 2.58, 3.24, 4.14, 5.40, 6.03/6.37 (money rain), 6.93,
  8.39–8.59 (build), 9.04 (flash + impact) and 11.92 (loop hit, the loudest moment at about −5 dB).

## 2. The structure to copy (scale to 12–16 s)
| Part | Share | Build |
|---|---|---|
| **A. Hook** | 0–8% (about 1 s) | Narrator line 1, at most 5 words ("He did not expect this."). Two teaser shots: **A1 = the subject's reaction to the payoff** (it returns as the last shot), **A2 = a close-up of the payoff action or object**. Hard cuts. |
| **B. Context narration** | 8–70% | Lines 2–3, about 25–30 words in story order: who, what they're doing, the hook fact (price, famous owner, record), then "And he was shocked by this [thing]." One shot per phrase, 0.45–1.0 s each (one shot up to about 1.5 s with a slow push). Reuse the wide product shot for the second mention, and end the narration on **A2 again** for "this [thing]". |
| **C. Handover** | at about 70% | The narrator stops. A **light-leak burn flash** (orange to white, about 10 frames / 0.17 s) with **impact-bass** on the exact cut frame reveals the payoff. |
| **D. Payoff** | 70–95% | Original audio, real order, 2–3 shots: the question or reaction, the object, the action. Stop **before** the explanation. |
| **E. Loop tag** | last 0.6 s | Hard cut back to **A1 (the same frames as 0.00 s)**, darkened about 20%, with manga speed lines and a loud impact. End mid-shot so the Short loops cleanly into frame 0. |

**Narration rules:**
- Write the script from the source transcript. It must be accurate and not a quote. Every fact, price or name must be said or
  shown in the source; label dated prices with the year if a brief asks for it.
- Keep it hooky and plain: "He did not expect this.", "This guy just went inside…", "to find out why…", "And he was shocked by this…".
- **Never reveal the result, answer or number the payoff is about.** For example, never say how fast it was built, what the
  button does, or who won. The narrator raises the question; the payoff audio shows the reaction.
- Pace: about 3.5 words/s, with no pauses longer than 0.2 s except a 0.4–0.6 s beat after line 1.

## 3. The look
- **Layout:**
  - black 1080×1920 canvas;
  - the footage band is a square-ish crop of the 16:9 source, 1080×1130 from y≈370 to y≈1500, centred on the subject (use
    `reframe.py`, cropping on frames of the cut clip);
  - black above and below the band.
- **Headline:** small bold white text with a dark outline, centred just above the band (y≈340), always on. It's a question plus
  one emoji, at most 5 words ("A Billionaire owns this? 💀"). Follow the brief's headline rules (BOXABL: the word BOXABL, no Elon).
- **Captions:**
  - one word at a time, synced to the narrator and then to the original speech;
  - small (about 44 px) bold uppercase, centred in the band at about 60% height;
  - white with a black outline. **Keywords** (the hook word, names, the price, SHOCKED, the payoff object) get a **green box**
    behind them.
- **Callouts:**
  - a **red dashed circle** around a face the narrator names ("this guy", a person's name) and a **red arrow** pointing at it;
  - a red arrow on product shots, pointing at the product;
  - both pop in (scale 0 → 1.1 → 1 in 0.15 s) on the shot's first frame.
- **Price moment:** a money-rain overlay (falling bills, transforms and opacity only) for the length of the price word.
- **Motion:** a slow push-in (100 → 108% over the shot) on any shot longer than 1 s. No shake.

## 4. Sound (transition/cut sounds from the user's `sound effects/sfxv2/` pack; the rest from the bundled SFX in `.agents/skills/media-use/audio/assets/sfx/`)
- **Each narration cut:** the transition's sfxv2 sound (`CAPCUT20`; `build-shorts.js` adds it). On a plain hard cut use `sound effects/sfxv2/fast-whoosh.mp3` (peak 0.56 s) alternating with `sound effects/sfxv2/fast-swish.mp3` (peak 0.21 s), started so the peak lands on the cut. (Before 2026-11-07 this was the bundled `whoosh-short` / `whoosh`.)
- **Price word:** sfx-kit `money/money-register.wav` (or `money-notes.wav` under the money rain), full path `commentary-kit/sfx/sfx-kit/sounds/money/…`.
- **Before the handover:** `commentary-kit/sfx/generated/riser_metallic_1.7s.wav` (the user's chosen riser). It peaks and stops dead 1.63 s in, so start it 1.63 s before the flash.
- **Handover flash:** `impact-bass-1` exactly on the flash frame. Duck the original audio in over 0.1 s.
- **Loop tag:** `impact-bass-2`, the loudest hit in the Short.
- **Music:** optional. If used, keep a low bed (narrator at least 12 dB above it) that cuts out at the handover and returns under
  the payoff if the speech allows. Kevin MacLeod tracks need the CC BY credit.
- **Mix:** dense with no silent gaps. `render-shorts.sh` normalises to −14 LUFS, which is fine (YouTube normalises playback anyway).

## 5. The narrator's voice
This PC uses local Kokoro voices (`bash tools/pipeline/hf.sh tts "<text>" -v <voice> -s <speed> -o vo.wav`).
- Kokoro can't clone a voice. Matching a real person's voice would also need their consent.
- The reference narrator is an expressive American male voice, fast (about 3.5 words/s) with a wide pitch range.
- Measured against it, the closest voices are **`am_liam`** (default) or **`am_eric`**, at **speed 1.15**. Samples are in
  `output/mark/voice-audition/`. If the user picked a voice there, use it. That folder is gitignored, so on a cloud session
  or a fresh checkout it's missing: regenerate it when the user wants to compare voices, with
  `mkdir -p output/mark/voice-audition && for v in am_liam am_eric am_fenrir am_adam; do bash tools/pipeline/hf.sh tts "He did not expect this. This guy just went inside this tiny house to find out why it costs fifty thousand dollars. And he was shocked by this feature." -v $v -s 1.15 -o output/mark/voice-audition/$v.wav; done`.
- Generate one file per line and place each line on its shots; `add-vo.py` mixes it.

## 6. The 7 workflow steps (as applied by /mark)
These are the steps from `docs/editing-workflow.md`, run in order with /mark's style filled in. Where this file and the workflow
doc differ, this file wins (its paths, plan approval, narration, SFX timing); campaign rules win over both.
Paths: `downloads/mark_<id>.mp4` (a reference: `downloads/markref_<id>.mp4`), job folder `jobs/mark_<id>/`, HyperFrames
project `videos/mark-<id>/clipNN/`, output `output/mark/<Creator or topic>/` (BOXABL: `output/mark/BOXABL - <Creator>/`).

### Step 1: Read the input
- Sort the message into **source link(s)** (required; ask and stop if missing), an optional **reference video**, and the
  **prompt**. Prompt instructions outrank everything except campaign rules.
- **Rule set:**
  - BOXABL source or campaign → every rule in `.claude/commands/boxabl.md`, plus the overrides in the campaign note at the top
    of this file;
  - DraftKings / ClipFarm creators → the `/gab` rules;
  - anything else → no campaign rules, but the playbook's safety rules still apply.
- **AI voice:** if the brief bans AI voiceover, stop and tell the user (this format needs the narrator).
- **Download** with `py -m yt_dlp` (≤1080p). If a link is private or blocked, report the exact error and continue with the rest.

### Step 2: Study the reference
- **No reference given:** the style sheet is § 1–5 of this file (rKfzqYYoCkg, already measured). Copy it into
  `jobs/mark_<id>/style.md` and go on.
- **A reference given** (another Short in this format): run `py tools/pipeline/study-reference.py downloads/markref_<id>.mp4 jobs/mark_<id>/ref`,
  read every sheet and write `style.md` with measured values, as § 1 does: the shot table (time, shot, audio, words on screen),
  which shots are reused and where, the narration timing, the flash handover, the loop, the SFX onsets and the layout. Where it
  measures differently from § 1, follow the new reference.
- **Copy the editing, never the content.** Footage, wording, frames, logos and music from the reference are never reused.

### Step 3: Find the moments
- **Transcribe the whole source:** `py tools/pipeline/transcribe_lowmem.py <src> jobs/mark_<id>/t base.en en`, in the
  background for long videos.
- **Read all of `segments.txt`,** then run `node tools/pipeline/score-moments.js jobs/mark_<id>/t/transcript.json --min 8 --max 25`.
- **Make contact sheets across the full runtime** for reactions, reveals and close-ups the transcript misses.
- **A /mark moment needs, on top of the playbook's standalone test:**
  - a **payoff** with original audio: a question, a reaction line or a reveal;
  - a visible **reaction** (shot A1, which also closes the loop);
  - a **close-up** of the payoff object or action (shot A2);
  - enough footage elsewhere in the source to illustrate every narration phrase;
  - for BOXABL, a wide shot of the whole home.
- Write `candidates.md`. For each pick: payoff timestamps, A1/A2 timestamps, "this clip is about…", the test result and risks.
  List rejects and why.

### Step 4: Decide the effects for every cut
For each clip, write `jobs/mark_<id>/clipNN/plan.md`:
- the 3 narration lines (the hook, the context and the cliffhanger) and the headline;
- one row per shot, in the § 1 table format: `time | shot | source time | audio | caption words | overlay | transition | SFX`.
  Mark every reused shot.

Choose effects in this order:
1. the user's prompt;
2. the campaign rules;
3. the style sheet (§ 3–4, or the new reference's `style.md`);
4. `docs/effects-catalog.md` for anything the style sheet doesn't cover.

**Effects are judged by timing, not count.** Every cut gets its SFX, peaking on the cut frame. There's one flash (the handover)
and one loop hit. Never add an effect the style sheet doesn't use. The house caps of ≤2 flashes and ≤6 SFX don't apply to /mark,
because the format puts a sound on every cut.
**Show all the plans to the user and wait for approval** before step 5.

### Step 5: Edit
Per clip:
1. **Cut** each planned shot from the source into `clipNN/shots/`. Crop on frames of the cut shot with `track-faces.py --write`
   and `reframe.py`, into the § 3 band. Don't run silence or mistake removal on narration shots (their length comes from the
   narration). On the payoff segment, use `cut-silences` / `cut-mistakes` only to remove dead air, keeping the reaction beats.
2. **Narration:**
   - one Kokoro file per line (§ 5 voice);
   - write "boxable" in the TTS text so the voice says it right, and "BOXABL" in captions;
   - lay the words against the shot list and retime the shots, never the voice;
   - transcribe the payoff audio and fix Whisper mishearings.
3. **Build** the HyperFrames project:
   - start from the `ysc` preset in `build-shorts.js` for the headline and captions, then hand-edit per
     `~/.claude/skills/viral-shorts/SKILL.md` § "HyperFrames editing" for the band layout, reused shots, red circles and arrows,
     money rain, the light-leak handover, speed lines and the loop;
   - search `/hyperframes-registry` before hand-building an effect;
   - animate transforms and opacity only.
4. **Check:**
   - `bash tools/pipeline/hf.sh check <dir>` must show 0 errors;
   - snapshot the hook, the whole-home shot, the handover and the loop frames, and compare them with the reference sheets side by side.

### Step 6: Clip as many as pass
Build every candidate that passed step 3 and the rule set. There's no fixed count. Stop when the next-best moment fails. Never
reuse the same payoff in two clips or mix sources in one clip. This PC has 3.6 GB RAM, so run at most about 3 renders at once.

### Step 7: Render, QC, report
- **Render:** `bash tools/pipeline/render-shorts.sh videos/mark-<id> "output/mark/<...>"`. It never overwrites, so recycle old
  files first. Name files by the brief's caption rule (BOXABL: the caption is the filename, with `@boxabl` and no hashtags).
- **QC per clip:**
  - `qc-sheet.sh` and `ysc-qc.sh` (length, −14 LUFS, LRA, no silence), plus `blackdetect` / `freezedetect`;
  - re-transcribe the render and run `clean-check.py`. Check that the narration **never states the result**, that every claim
    is in the source, and that every caption word matches the audio;
  - check that each SFX lands within 2 frames of its cut and that the last frame flows into frame 0;
  - read the frames: whole home shown and labelled (BOXABL), captions off faces, no forbidden content;
  - **reference match:** length 12–16 s, the narration ends at 60–75% of the clip, shots run 0.45–1.0 s during the narration,
    and the hook pattern, reuse, handover and loop are all present;
  - fix and re-render anything that fails.
- **Report** in `output/mark/<...>/clips_report.md`. Per clip:
  - the filename/caption, source timestamps, duration and the story in one line;
  - the narration, the voice and the reused shots;
  - the effect log (time, effect, why);
  - QC pass/fail and the reference-match numbers.
  Also list rejected moments, blockers, and anything the brief made you change.
- **Keep the job files.** The user runs `/cleanup-project` when ready.

## Transitions and transition SFX (user rule, 2026-11-07)
- **Main choices, in every edit:** CapCut's 20 popular transitions: Pull In, Pull Out, Camera Shake, Whirl, Zoom In, Zoom Out, Blur, Glitch, Flash, Spin, Slide, Rotate, Shake, Zoom Blur, Distortion, Cube, Swipe, Wipe, Split, Light Leak. Pick every transition from these first, also when motion graphics are involved (split-screen panels, explainers, montages, slideshows, overlay cards): each scene change between shots or graphics uses one of the 20, not another engine's or the registry's version of the same name. Use another transition only when none of the 20 fits. CapCut name -> preset: the "Main set" table at the top of `motion-graphics-library/EFFECTS_INDEX.md` (`CAPCUT20` in `mgl.js`, ai-video-editor workspace).
- **Transition SFX:** only the user's sfxv2 pack (`sound effects/sfxv2/` in ai-video-editor; master copy `sfxv2/` in the vault repo). The user's files come first; `generated/` holds synthesized fallbacks, currently unused. Each of the 20 has its sound, peak and volume in `CAPCUT20`, and every file is 1.5 s or shorter. `build-shorts.js` adds the sound automatically with the hit on the cut, so never add a second whoosh for the same cut (`"sfx": false` on a transition skips it, `"sfxVol"` sets its volume).
- **Any other engine** (a hand-built HyperFrames composition, Remotion, ffmpeg, OpenMontage): run `node motion-graphics-library/mgl.js --capcut20`, port the transition's motion exactly (same values, durations and eases), and place its sfxv2 sound with the peak on the cut at its volume.
- **Motion graphics keep their own small sounds** (typing ticks, pops, shimmers, rises). The sound on a scene change is the transition's sfxv2 sound; the builder drops a panel split's synthesized hit where a transition sound already lands.
- The skill's or command's own limits still apply: transition sounds count toward its SFX cap, and its cut style (e.g. hard cuts by default) decides how many transitions there are. Not for the cartoon/3D animation skills (cartoon-audio-short, cartoon-3d-short, 3d-short).
