---
name: cut-silences
description: Utility that removes silences and dead air from a recording (talking-head footage or a long source before clipping). Use when asked to cut silences, trim pauses, remove dead air / gaps, or tighten the pacing of a raw video, given a word-level transcript. Produces an edit list (EDL), a re-timed transcript, and optionally the cut video via ffmpeg. Does NOT cut mistakes, repeats, or false starts (that is cut-mistakes) and never decides style or story — the house-style editing skills (/viral-shorts, /youtube-style-clip, /gab, /boxabl, /puregrit) stay in charge.
---

# Cut Silences

Adapted from Nate Herk's herk-edit-kit (MIT, see LICENSE). Takes a raw recording + its word-level transcript and removes **only silence**: dead air before the first word and after the last word, plus inter-word pauses longer than a threshold (trimmed down to a natural breath, never a hard zero-gap). It leaves the speaker's words untouched — false starts, retakes, and stutters are the **cut-mistakes** skill's job.

This agent is deterministic and transcript-driven, so its output (`*.silence-transcript.json`) feeds cleanly into captions and the house-style build.

## When to use

- "cut the silences", "trim the pauses", "remove dead air", "tighten the pacing"
- Inside a house-style job, when a segment has dead air between words (run **cut-mistakes first**, on the raw transcript: after silences are trimmed, pauses become too short for its retake detection).

## Prerequisites

A word-level transcript JSON: the plain list `[{ text, start, end }]` written by this workspace's local
transcriber, or `{ words: [{ text, start, end }] }`. Generate one locally (no paid service):

```bash
py tools/pipeline/transcribe_lowmem.py path/to/raw.mp4 path/to/t base.en   # -> path/to/t/transcript.json
```

ffmpeg 6 and 7+ both work: the script picks `-filter_complex_script` or `-/filter_complex` automatically.

## Usage

```bash
# 1) Plan only — compute the cut, write EDL + re-timed transcript (no video touched)
node .claude/skills/cut-silences/scripts/cut-silences.mjs <transcript.json> \
  --out-dir jobs/<job>

# 2) With a video — also write the ffmpeg command (still does not render yet)
node .claude/skills/cut-silences/scripts/cut-silences.mjs <transcript.json> \
  --video jobs/<job>/raw.mp4 --out-dir jobs/<job>

# 3) Render the cut video (local ffmpeg, re-encode, A/V kept in sync)
#    add --apply to actually run ffmpeg
node .claude/skills/cut-silences/scripts/cut-silences.mjs <transcript.json> \
  --video jobs/<job>/raw.mp4 --apply \
  --output jobs/<job>/edited-silenced.mp4
```

### Options

| Flag | Default | Meaning |
| --- | --- | --- |
| `--video <path>` | — | Source video; enables the ffmpeg command / render |
| `--out-dir <dir>` | next to transcript | Where outputs are written |
| `--output <path>` | `<video-stem>.silenced.mp4` | Cut-video path |
| `--gap <s>` | `0.55` | Minimum pause treated as trimmable silence |
| `--head-pad <s>` | `0.22` | Silence kept before the first word |
| `--tail-pad <s>` | `0.34` | Silence kept after the last word |
| `--apply` | off | Actually run ffmpeg to render the cut |

## How it decides (the silence rules)

- Pauses below `--gap` (0.55s) are left alone — natural speech rhythm.
- For a trimmed pause, a **natural breath is kept**, scaled by context: `0.24s` for long pauses (≥2s), `0.20s` after a sentence ender (`. ! ?`), `0.14s` otherwise. The kept breath is biased slightly toward the end of the previous phrase.
- Head/tail dead air is trimmed to `--head-pad` / `--tail-pad`.
- Delete ranges are merged; keep ranges are the complement. The cut is rendered with an ffmpeg `trim`/`atrim` + `concat` filtergraph (written to a `*.silence-filter.txt` script and passed via `-/filter_complex` on ffmpeg 7+ or `-filter_complex_script` on ffmpeg 6), so video and audio stay in sync.

## Outputs (written to `--out-dir`)

| File | Purpose |
| --- | --- |
| `<stem>.silence-edl.json` | Keep/delete ranges, durations, params — the edit list |
| `<stem>.silence-transcript.json` | Words re-timed onto the edited timeline (feeds captions) |
| `<stem>.silence-decisions.md` | Human-readable summary + largest pauses trimmed |
| `<stem>.silence-filter.txt` | The ffmpeg filtergraph (only with `--video`) |
| `<video-stem>.silenced.mp4` | The cut video (only with `--apply`) |

The JSON summary printed to stdout includes `removed`, `removedPct`, range counts, and output paths — useful to log in the job's notes.

## Tuning notes

- Talking-head YouTube default (`--gap 0.55`) removes roughly 15-20% of a typical raw take as pure silence. Lower `--gap` for a punchier, faster cut; raise it to preserve more natural breathing room.
- If a cut feels too aggressive at sentence boundaries, raise the sentence-break breath, or raise `--gap`.

## Hand-off

Use `<stem>.silenced.mp4` as the segment's `tight.mp4` (or a source for it) and `<stem>.silence-transcript.json` for captions: its timestamps are already on the edited timeline.
