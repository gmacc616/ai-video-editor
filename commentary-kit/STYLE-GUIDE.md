# Commentary Channel — Editing Style Guide

What the commentary / reaction / "drama breakdown" niche does in its edits, and how to do it with this kit.

## 1. The format

| Layer | What it is | Typical treatment |
|---|---|---|
| A-roll | You talking (facecam or voiceover) | Jump-cut every breath and filler word. Gaps under 0.15 s. |
| Evidence | Clips, tweets, Reddit posts, articles, screenshots | Full screen, slow push-in (100→110% over the shot), highlight the line you're reading |
| Reaction | Your face over the evidence | Corner cam (≈25% width) or a cut-out "PiP" with a white outline |
| Punctuation | Memes, SFX, zooms, freeze frames | Used to land a joke or a reveal, **not** constantly |

**Pacing target:** in the first 30 s, change something on screen every 2–4 s. After that, every 4–8 s is fine. The hook (0–15 s) shows the most shocking clip or claim first, then "let's get into it".

## 2. Core techniques (most → least used)

1. **Jump cuts.** Remove silences, "um"s and retakes. This matters more than anything else in the guide. (`tools/pipeline/cuts.js` in this repo already does silence cutting.)
2. **Punch-in zooms.** Alternate the facecam between 100% and 115–120% on every other cut. Hard punch (no ease) to 130–140% on a punchline, plus `zoom_in_blip.wav` or `boom_impact.wav`.
3. **Highlight and read.** Show a screenshot, then zoom to the sentence. Add a yellow highlighter box or the `red_circle_highlight.png` / `red_arrow_right.png`. Blur the rest (Gaussian blur 20–30 on a duplicate layer below).
4. **Freeze frame + record-scratch moment.** Freeze the clip on a ridiculous face, add a slight zoom, desaturate, play `camera_shutter.wav` or a record scratch, and talk over it.
5. **Keyword captions.** Not full subtitles. Pop 1–3 words on screen for the claims that matter: bold sans font (Anton, Bebas Neue or Montserrat ExtraBold), white with a black stroke, one accent colour.
6. **Meme inserts.** 0.5–1.5 s of a reaction image or GIF, full screen or popped in at an angle, with `pop.wav`. Keep it to one or two per minute.
7. **Censor.** Bleep plus a black bar or mosaic over names and handles of private people. Always blur usernames and faces of non-public individuals.
8. **Music bed.** Lo-fi or quirky "investigation" music at −28 to −32 LUFS under the voice. Duck it further while you talk. Cut it to silence for dramatic moments, then hit `boom_deep_sub.wav`.
9. **Segment cards.** A title card between chapters ("PART 2: THE RECEIPTS") with `whoosh_long.wav` + `static_glitch_0.5s.mp4`.
10. **Vignette + grain** on screenshots and old footage so they don't look flat (`vignette.png`, `film_grain_4s_overlay-blend.mp4` on Overlay at 20–40%).

### Music by mood (`music/`)

| Mood | Tracks |
|---|---|
| Investigating / "let's look at the receipts" | Investigations, Sneaky Snitch, Scheming Weasel faster, Sneaky Adventure |
| Goofy / someone being ridiculous | Fluffing a Duck, Monkeys Spinning Monkeys, Pixel Peeker Polka - faster |
| Neutral talking bed | Wallpaper, Carefree, Thinking Music, Local Forecast - Elevator |
| Shady / dramatic | Hitman, Night on the Docks - Sax, Dark Fog |
| Tech / internet drama | Aitech |

For more music, use the YouTube Studio Audio Library (Studio → Audio Library; many tracks need no credit) and Pixabay Music (no credit needed). Always check each track's license line.

## 3. Transitions

Commentary editors mostly use **hard cuts**. Transitions are kept for changes of topic. **User rule (2026-11-07):** pick them from CapCut's 20 ("Main set" in `motion-graphics-library/EFFECTS_INDEX.md`) with their `sound effects/sfxv2/` sounds; the table below is the older kit mapping, used only when none of the 20 fits:

| Use | Transition | Kit asset |
|---|---|---|
| Topic change | Whip/whoosh pan or glitch | `whoosh_short.wav` + `static_glitch_0.5s.mp4` |
| Reveal | White flash | `white_flash_0.4s_screen-blend.mp4` + `boom_impact.wav` |
| Time skip / "later…" | Dip to black + title card | `whoosh_long.wav` |
| Into a flashback or old clip | VHS look | `vhs_scanlines_6s_screen-blend.mp4` (Screen blend) |
| Into a screenshot | Zoom-through (scale 100→200% + motion blur, 6 frames) | `zoom_in_blip.wav` |

ffmpeg's `xfade` filter covers the rest (wipeleft, slideleft, zoomin, pixelize, hblur, circleopen…).

## 4. Sound effects map (kit file → use)

| File | Use it when |
|---|---|
| `boom_impact.wav` | Shocking reveal, "vine boom"-style emphasis |
| `boom_deep_sub.wav` | Dramatic pause / music drop |
| `punch_hit.wav` | Hard punch-in zoom, text slam |
| `whoosh_short.wav` / `whoosh_long.wav` | Text flying in, wipes, pans |
| `riser_2s.wav` | Build-up before a reveal (end it on a boom) |
| `pop.wav` | Meme, emoji or caption pops in |
| `ding.wav` / `correct_chime.wav` | "They were right", checklist items |
| `wrong_buzzer.wav` / `slide_down_fail.wav` | Wrong claims, fails, L moments |
| `censor_bleep.wav` | Swearing, names |
| `camera_shutter.wav` | Screenshot or freeze frame appears |
| `glitch_burst.wav` | Glitch transitions, "error" moments |
| `click.wav` | Cursor clicks, UI or tweet reveals |
| `clock_tick_4s.wav` | "Meanwhile…", waiting, deadlines |
| `suspense_drone_12s.wav` | Under serious or dark segments |

Mix rule: SFX peak around −12 to −8 dBFS under a −14 LUFS master. Voice always wins.

Note: the meme sounds themselves (actual vine boom, "bruh", "oof") are taken from other media and have unclear licensing. The kit has close original substitutes. If you use the real ones, keep them under 1 s and expect them to cause trouble later.

## 5. Copyright and fair use (important in this niche)

- **Transform, don't re-upload.** Talk over or between the clips you show. Keep each clip short (aim for under 10–15 s at a time) and comment on it.
- Never use copyrighted music from the clip as your bed. Mute or duck it.
- Blur private individuals. Stick to public figures and public posts.
- Keep your own receipts (the URL and date for every screenshot). You'll need them for disputes.
- Use only licensed or original SFX, music and fonts (everything in this kit qualifies).

## 6. Video recipe (10–15 min video)

```
0:00  Cold open: the wildest clip (5–10 s) → boom → title slam
0:15  "Here's what happened" — context with screenshots, push-ins, highlights
1:30  Part 1 — evidence + reactions (punch-ins, keyword captions)
...   Part 2/3 — segment cards with whoosh+glitch between chapters
~end  Your take / verdict — slower, fewer effects, music softer
last  10 s end screen — suggest next video
```

## 7. Export settings for YouTube

- 1920×1080 or 2560×1440 (1440p gets the better VP9/AV1 encode), 30 or 60 fps matching your source
- H.264 High, 16–24 Mbps (1080p) / 35–45 Mbps (1440p), AAC 320 kbps 48 kHz
- Loudness −14 LUFS integrated, −1 dBTP peak

## 8. Kit contents

```
commentary-kit/
├── STYLE-GUIDE.md          (this file)
├── sfx/generated/          18 original SFX, 48 kHz WAV, normalised to −1 dBFS — yours, no license
├── sfx/kenney/             418 CC0 sounds (impacts, UI clicks, digital blips, sci-fi) from kenney.nl
├── music/                  15 Kevin MacLeod tracks (CC BY 4.0 — paste lines from music/CREDITS.txt into each description)
├── fonts/                  Anton, Bebas Neue, Montserrat (SIL OFL — free for commercial use)
├── overlays/               grain, VHS scanlines, vignette, red circle, red arrow, letterbox bars
├── transitions/            white flash, static glitch
└── tools/make_kit.sh       regenerate everything: bash tools/make_kit.sh
```
