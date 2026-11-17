---
name: cut-mistakes
description: "Utility that finds and removes spoken mistakes — stutters, repeated words, false starts, and retakes (re-recorded lines) — from a recording. Use when asked to cut mistakes, remove stutters / repeats / filler restarts, clean up flubs, or keep the best take. Works review-gated: it proposes every cut with context and a reason for approval, then renders only the approved cuts via ffmpeg. Requires a word-level transcript. Never decides style or story: the house-style editing skills stay in charge."
---

# Cut Mistakes & Repeats

Adapted from Nate Herk's herk-edit-kit (MIT, see LICENSE). Run it **before cut-silences**, on the raw transcript. It removes the things a human editor cuts on a second pass: stutters ("the the", "I- I-"), immediately repeated words, false starts (an abandoned phrase that restarts), and retakes (a line re-recorded — keep the clean take, drop the botched one).

Deciding what counts as a mistake is **judgment, not a formula** — emphatic repetition ("never, never") and rhetorical doubling ("the first piece is, is this…") look identical to a stutter mechanically. So this skill is **review-gated by default**: it surfaces candidates with full context; the agent (and the user) decide; only approved cuts are rendered.

## When to use

- "cut the mistakes", "remove stutters / repeats", "clean up the flubs", "keep the best take", "cut false starts"
- Inside a house-style job (/viral-shorts, /gab, /boxabl, …) when a picked segment has a flub or a retake.

## The three-part flow

### 1. Find candidates (mechanical)

```bash
node .claude/skills/cut-mistakes/scripts/find-cut-candidates.mjs \
  <transcript.json> --out-dir jobs/<job>/mistakes
```

Input is the **raw** word-level transcript: the plain list `[{ text, start, end }]` from `py tools/pipeline/transcribe_lowmem.py`, or `{ words: [...] }`. Use the raw one, not cut-silences' output: retakes are found by splitting sentences at pauses longer than 0.85 s, and trimmed pauses are too short for that (tested 2026-10-24: a false start was found on the raw timeline and missed on the silenced one). Writes:

- `<stem>.cut-candidates.json` — structured candidates (type, confidence, proposed `cut` range, `removes`/`keeps` text, context, recommendation)
- `<stem>.cut-candidates.md` — readable proposal

Candidate types: `stutter` (immediate word repeat), `retake` (duplicate/near-duplicate segment via Jaccard similarity), `false_start` (short abandoned phrase that restarts).

### 2. Review (the gate — REQUIRED)

Read each candidate **in context** and decide keep-or-cut. The mechanical detector cannot tell intentional emphasis/rhetoric from a real flub, so do not trust `recommend` blindly — read `removes` + `context`. Common false positives: emphatic repetition ("it's never, never hands-off"), copula-then-question ("the piece is, is this…"), listing.

Standalone use: present the candidates to the user with a recommendation per item and collect approvals. Inside a house-style job that runs automatically (the user asked not to be stopped for editing choices), review each candidate yourself, apply only clear flubs, and list every cut with its reason in the job report. Write the approved cuts to a file:

```json
{ "cuts": [ { "start": 100.93, "end": 101.06, "reason": "I- false start" }, ... ] }
```

(`start`/`end` in seconds on the input transcript/video timeline. You can widen a candidate's range — e.g. for a retake, cut from the botched take's start to the clean restart.)

### 3. Apply approved cuts

```bash
node .claude/skills/cut-mistakes/scripts/apply-cuts.mjs \
  <transcript.json> --cuts approved-cuts.json \
  --video jobs/<job>/source.mp4 \
  --output jobs/<job>/mistakes/clean.mp4 --apply
```

Writes the EDL, a re-timed `<stem>.mistakes-transcript.json` (use it as cut-silences' input next), a decisions log, and — with `--apply` — the cut video (ffmpeg trim+concat, A/V in sync). Drop `--apply` for a dry run.

## Reviewing the result

Spot-check each cut boundary: extract a frame sheet or listen to 1 s either side of every cut in the rendered file (ffmpeg), and re-transcribe the result to confirm no words were clipped.

ffmpeg 6 and 7+ both work: the script picks `-filter_complex_script` or `-/filter_complex` automatically.

## Notes

- A very clean delivery may yield few or zero real cuts — that's a valid outcome; don't cut natural speech to hit a quota.
- Cuts between two spoken words are hard joins. They're usually clean for stutters/false starts; for tighter audio a 20-30ms fade can be added later.
- Next: run **cut-silences** on `<stem>.mistakes-transcript.json` + the clean video, then continue the house-style build.
