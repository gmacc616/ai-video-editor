# AI-Video-Editor (commentary + HyperFrames workflows)

What this project is for and how it got here: `PROJECT-OVERVIEW.md`.

**This repo (`gmacc616/ai-video-editor`) is PUBLIC (2026-11-17).** Private files live in `gmacc616/ai-video-editor-private`: `sound effects/`, `assets/gab`, `cloud/memory`, `cloud/skills/gab`, `cloud/skills/default-voice/voice`, `.claude/commands/boxabl.md`, `data/youtube`, `docs/brezscales-account-setup.md`, `prompts/`. They are gitignored here and linked in by `cloud/session-start.sh`; commit and push changes to them in the `-private` clone. Never commit secrets, licensed media, campaign briefs or personal notes here.

## Token-efficient tooling (project-local)
- RTK rewrites supported Bash commands (git, grep, find, ls, tests…) to filtered `rtk …` output via `.claude/settings.json`. It does not touch the Read/Grep/Glob tools or the PowerShell tool. If filtered output hides something you need, rerun with `rtk proxy <cmd>` for raw output. `rtk gain` shows savings.
- `token-saver` skill scripts: run with `py`, not `python` (`python` here is the Store stub). Use `filter.py` for noisy commands RTK does not cover (hyperframes render/check, ffmpeg, npm).
- Never filter away errors, warnings, failing lines, QC results, or render diagnostics. If a task needs a whole file or full log, read it.

## Token rules (always on, here and in the cloud; correctness first)
These make the token skills default behaviour; the skills themselves hold the detail. Never drop context or output the task needs to save tokens.
- **Commands:** RTK compresses shell output automatically (installed in the cloud by `cloud/session-start.sh`). Run noisy commands RTK doesn't cover (ffmpeg, `hf.sh render/check`, npm, long scripts) through `py .claude/skills/token-saver/scripts/filter.py -- <cmd>`, or `| tail`; batch related commands in one call; add limits (`git log --oneline -20`, `--quiet`).
- **Reading (token-saver + lean-read):** locate with Grep/Glob first, then Read only the line range. For files over ~200 lines, run `py .claude/skills/token-saver/scripts/outline.py <file>` before reading. Never re-read a file already in context or just edited. Never bulk-read lockfiles, `node_modules`, generated renders/compositions, or big JSON transcripts when `segments.txt` will do.
- **Images:** frame sheets are the costliest input. Use one low-res overview sheet for the whole source, then denser sheets only around chosen moments; don't re-view a sheet already seen.
- **Delegation:** broad sweeps across many files go to a subagent that returns a short summary.
- **Long sessions (context-budget):** after an auto-compaction, rely on the summary instead of re-reading files, and suggest a fresh session for the next job. When the user asks why tokens went up, run the context-budget audit.
- **Claude API code (prompt-cache-optimizer):** stable content first, `cache_control` on the stable prefix, volatile content last.

## Writing code (adapted from lazy-coder / Ponytail 5, MIT)
Before writing code, stop at the first rung that holds: is it needed at all → already in this repo (`tools/pipeline/`, `commentary-kit/`, existing skills) → standard library → native platform/ffmpeg/HyperFrames feature → an installed dependency → one line → only then the minimum code that works.
- Understand the task and trace the code it touches before climbing the ladder. List every place the change must reach (callers, tests, fixtures, config, skills/docs that name it) and what it could break (data destroyed or exposed, callers that stop working). Fix bugs at the root cause; grep every caller of a shared function.
- Be lazy about the solution, never about the change: finish every part the task needs, including callers and docs your change breaks.
- No unrequested abstractions, avoidable dependencies, or boilerplate. Keep values in the form the platform gives you and the structure the codebase already has. Prefer deletion over addition, boring over clever, fewest files, shortest working diff — but choose the edge-case-correct option when sizes are equal. A one-liner that needs decoding is not short.
- Comment only the why the code can't show, in one line. Code you move or merge keeps its error handling and validation.
- A deliberate shortcut with a known limit gets a comment `shortcut: <the limit>, <when to upgrade>` (`/ponytail-debt` lists them).
- Never cut: understanding the problem, input validation at trust boundaries, error handling that prevents data loss, security, accessibility, anything explicitly requested. Non-trivial logic leaves one runnable check (an assert self-check or one small test).
- After a code change, end the reply with one line: what was skipped or not checked, and any risk the user must know.
- Reviews: `/ponytail-review` (a change) and `/ponytail-audit` (whole repo) report findings in plain English and change nothing.
- These rules govern code size, not output quality: scripts, research, captions and renders still get full care.

## Editing knowledge
- Before any edit, clip or Shorts job, read `docs/clipping-playbook.md`: story-first moment rules, the measured look, safety and workflow lessons. Every editing skill points to it.
- Every editing job (any editing skill, or a bare link with or without a reference video) follows the default process in `docs/editing-workflow.md`; the active skill sets the look and rules.
- **Motion graphics:** before creating any transition, caption animation or overlay, read `motion-graphics-library/EFFECTS_INDEX.md` and use what exists (`shorts.json` fields `transitions`, `overlays`, `capAnim`/`capAnims`; `motion-graphics-library/SELECTION_GUIDE.md` says which fits which moment). New effects go into `motion-graphics-library/mgl.js` with a test; see its README. Split-screen panel graphics (graphic on top, speaker below, sounds generated by the graphics) are in `motion-graphics-library/panel.js` (`shorts.json` `"panel"`), used by `/motivational`.
- **Transitions (user rule, 2026-11-07):** in every editing or clipping job, skill or command (`/boxabl`, `/mark`, `/meme`, `/motivational`, `/editor`, `/montage`, the house styles and the HyperFrames workflows), including motion-graphics edits, choose transitions from CapCut's 20 popular ones first (the "Main set" table at the top of `motion-graphics-library/EFFECTS_INDEX.md`). Their sounds come only from the user's sfxv2 pack (`sound effects/sfxv2/`, every file 1.5 s or shorter), and `build-shorts.js` adds them on the cut automatically. With any other engine (hand-built HyperFrames, Remotion, ffmpeg), port them from `node motion-graphics-library/mgl.js --capcut20`. Motion graphics keep their own small sounds; a scene change's sound is the transition's. The vendored `.agents/skills` carry this as a local addendum; re-add it if a HyperFrames skills update overwrites them. This does not apply to the cartoon/3D animation skills (`cartoon-audio-short`, `cartoon-3d-short`, `3d-short`).
- **Voiceover:** `py tools/voice/kvoice.py` is the Kokoro voice tool (default voice am_adam): tags, multi-voice scripts, effects/presets, voice design, versions + JSON provenance, consent-gated cloning. `--help` and the file header list everything; no watermark is added.
- **3D shorts render with coldframe** (user rule, 2026-11-17): the final render of every `3d-short` / `cartoon-3d-short` video goes to coldframe (20 GitHub machines in parallel, from the vault's `tools/remotion-3d`; step 10 of the skill has the command). `render.sh` or a local `remotion render` is only a fallback when coldframe fails. Coldframe renders Remotion compositions only, so HyperFrames and ffmpeg edits keep their own renderers.
- **/montage** (`.claude/skills/montage/SKILL.md`) = the /hyperframes entry skill plus OpenMontage (`vendor/openmontage`, installed by `bash tools/montage/setup.sh`): AI video/image/music/voice generators, avatars, stock corpus, 3D, character animation, Remotion, Manim, dubbing. Remotion is its core animation engine; HyperFrames only fills gaps (§ M7). Only when the user asks for it; workspace tools win where both do the same job; paid calls need the user's keys and a yes per call.
- `/editor` (`.claude/skills/editor/SKILL.md`) combines the general editing skills (not /boxabl or /gab, which keep the campaign rules) into one conflict-free skill with a single precedence order and per-style mode table; use it when the user names it or asks for an edit without naming a skill.

## Watermark remover (all sessions, PC and cloud)
- Skills `remove-ai-marks` (thin client over a local HTTP service on 127.0.0.1:8765) and `clean-user-facing-text` (self-contained). On the PC they come from the user-scoped `watermarks-remover` plugin; in the cloud they are vendored in `cloud/watermarks-remover/` and linked by `cloud/session-start.sh`, which also installs exiftool/qpdf and starts the service via `cloud/wm-service.sh` (idempotent; run it by hand if `/health` fails: `bash cloud/wm-service.sh`).
- `bash cloud/sync.sh` refreshes the vendored copy from the plugin before pushing.

## Cloud sessions (Linux checkout of this repo)
- Setup: the environment runs `bash cloud-setup.sh` (toolchain, `py`/`cygpath` shims, skill links, memory). If tools are missing, run it again.
- Paths: any `C:\Users\manth\OneDrive\Desktop\AI-Video-Editor` in skills or docs means the repo root. `py` = `python3`. For ffmpeg drawtext use `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`, not `C:/Windows/Fonts`.
- Not available in the cloud: the built-in browser (YouTube Studio, signed-in analytics), Intel QSV (renders use CPU encoding), OneDrive, the Recycle Bin (`/cleanup-project` there only removes the job's own folders).
- Source videos the user uploads to the GitHub release `sources` of `gmacc616/ai-video-editor-private`: fetch them with `bash cloud/fetch-release.sh "<file name>"` (uses `$GH_TOKEN`; `--list` shows the files). Needs that repo attached to the session (it is when the session starts with it selected). Google Drive links also work (below).
- Source videos the user shares on Google Drive ("Anyone with the link"): `bash cloud/fetch-drive.sh <drive link>` downloads into `downloads/`, skipping Drive's virus-scan page, and checks size and playability (`--check` shows name and size only).
- YouTube may block yt-dlp from cloud servers ("confirm you're not a bot"). If so, stop and ask the user to download the source on their PC and commit it, rather than trying workarounds.
- Finished videos stay on the cloud machine: tell the user where they are so they can download them, or commit them only if asked (`output/` is gitignored).
- Custom skills come from `cloud/skills/` and memory from `cloud/memory/`; on the PC, refresh them with `bash cloud/sync.sh` before pushing.
