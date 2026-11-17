# Context-budget tactics — the full playbook

Load this when you need the concrete, copy-pasteable moves behind the summary in `SKILL.md`. Every tactic here is ordered roughly by leverage (biggest, most-frequent savings first). The golden rule still applies: **only apply a tactic when it doesn't drop context the task needs.** Tactics marked ⚠ involve judgement — surface them, don't auto-apply.

---

## A. Persistent context (paid every single turn — highest leverage)

Anything loaded on every message is the most expensive token you own. A 4k-token `CLAUDE.md` across a 50-message session is ~200k tokens of repeated payload. Fix these first.

### A1. Cut filler from `CLAUDE.md`
Delete content that does not change the agent's behavior:
- Restated platitudes ("write clean code", "be careful", "follow best practices") — the model already does this.
- Instructions the model would follow by default ("use the existing style", "don't break tests") unless the repo genuinely deviates.
- Duplicated rules — the same instruction stated three ways. Keep the clearest one.
- Dead links, references to files/scripts that no longer exist, stale "as of <old date>" notes.
- Long prose where a one-line rule would do.

**Keep** every rule that demonstrably changes an action: non-obvious commands, project-specific gotchas, "never do X here" guardrails, the actual house conventions that differ from defaults.

### A2. Move detail to referenced files (progressive disclosure)
Detail that's needed *sometimes* shouldn't load *always*. Pattern:
- Inline in `CLAUDE.md`: the trigger + a one-line pointer.
- In a referenced file (e.g. `docs/RUNBOOK.md`, `references/<topic>.md`): the heavy detail.
The agent loads the reference only when the task hits that topic. This is exactly how well-built skills work — `SKILL.md` stays lean, references carry the weight.

### A3. Collapse nested `CLAUDE.md` duplication
In monorepos, root + per-package `CLAUDE.md` files often repeat the same global rules. Keep global rules in the root only; per-package files carry only what's unique to that package.

### A4. Audit imported memory / always-on context
Memory files, auto-loaded notes, and large system preambles count too. Same test: does each line change behavior? If not, it's rent you're paying every turn.

---

## B. Read amplification (the per-task token sink)

### B1. Locate before you read
Never open a file blind to find one thing. Sequence:
1. `Grep`/`Glob` to find *where* the symbol/string lives (returns paths + line numbers cheaply).
2. `Read` only the relevant **line range** (`offset` + `limit`), not the whole file.
A 2,000-line file read in full to inspect one 30-line function is ~50× the necessary cost.

### B2. Never read these in full
- Lockfiles (`package-lock.json`, `pnpm-lock.yaml`, `poetry.lock`, `Cargo.lock`, `go.sum`) — thousands of lines, almost never needed in full. Grep for the one package if you must.
- Generated / build output (`dist/`, `build/`, `.next/`, `target/`, `__generated__/`).
- Minified assets and source maps (`*.min.js`, `*.map`).
- Vendored dependencies (`node_modules/`, `vendor/`, `.venv/`).
- Large data fixtures, snapshots, CSV/JSON dumps — sample or grep them.

### B3. Don't re-read what's already in context
If a file was read this session and hasn't changed, it's already in the window — re-reading doubles the cost for zero new information. Trust the prior read; only re-read after an edit or if you genuinely need a different part.

### B4. Prefer an index for large codebases
On a big repo, brute-force reading to build a mental model is the most expensive possible approach. Use a code index / knowledge graph / symbol search to answer structural questions from a compact summary instead of raw file contents. (See the `lean-read` skill for the full workflow.)

---

## C. Tool-output discipline (cap the firehose at the source)

The cheapest way to not pay for 5,000 lines of log is to never emit them into context. Add the limit to the *command*, not after the fact.

| Instead of | Run | Why |
|---|---|---|
| `git log` | `git log --oneline -20` | full history is unbounded |
| `npm test` | `npm test 2>&1 \| tail -50` | you need the failures, not every passing line |
| `cat bigfile` | `grep -n PATTERN bigfile` or `Read` with a range | stream only the relevant slice |
| `ls -R` | `ls` per dir, or `git ls-files \| head` | recursion explodes on `node_modules` |
| verbose build | add `--quiet` / `--silent` | most build chatter is noise |
| `curl <api>` (full body) | `curl -s <api> \| jq '<path>'` | extract the field, don't dump the payload |
| `pytest -v` (huge) | `pytest -q` then `--tb=short` on failures | full tracebacks only when needed |

**Capture-then-read pattern:** for output you might need part of, redirect it to a file (`cmd > /tmp/out.log 2>&1`) and then `Read` only the relevant lines. The file holds everything; the context only gets the slice you actually use.

---

## D. Cache-friendly ordering (make prompt caching pay)

Anthropic prompt caching only helps when the **prefix is byte-stable** across calls. Wins:
- Put stable content first: system prompt → tool definitions → `CLAUDE.md` / long references → conversation.
- Don't inject volatile data (timestamps, random ids, per-turn state) *into* the stable prefix — it invalidates the cache for everything after it.
- Keep large reference material that's reused across turns in a stable position so it's read from cache, not re-billed at full rate.
Full treatment: the `prompt-cache-optimizer` skill.

---

## E. Conversation hygiene (⚠ judgement)

Long sessions accumulate dead weight: abandoned approaches, superseded plans, exploratory reads that no longer inform the task. This *is* recoverable budget, but pruning it is a judgement call about what's still needed — so **propose, don't auto-cut**.

- ⚠ Superseded plans / earlier wrong turns: usually safe to consider "done", but confirm.
- ⚠ Early exploration that led nowhere: the *conclusion* matters, the step-by-step usually doesn't.
- For very long sessions, the right move is often a fresh session seeded with a tight summary of decisions + current state, rather than carrying the whole transcript. Suggest this when the window is the bottleneck.

---

## F. Output discipline (output tokens cost too)

- Answer at the altitude asked: a diff, the one function, a 3-line summary — not a re-dump of files already in context.
- Don't echo back large blocks the user can already see. Reference them.
- Prefer "here's the change" over "here's the whole file with the change".

---

## Anti-patterns — do NOT do these to save tokens

- ❌ Truncating a file mid-read and guessing the rest.
- ❌ Skipping a `Read` of a file the task clearly depends on because it's "probably fine".
- ❌ Deleting `CLAUDE.md` rules wholesale without checking whether they change behavior.
- ❌ Summarizing away error messages / stack traces you actually need to debug.
- ❌ Dropping test output that contains the failure you're chasing.
- ❌ Compressing so aggressively that the next turn has to re-read everything you just cut — that's negative savings.

The test for every cut: *"If I remove this, can the current task still be done correctly without re-fetching it?"* If no, keep it.
