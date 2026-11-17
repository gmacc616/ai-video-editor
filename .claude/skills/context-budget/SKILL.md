---
name: context-budget
description: Audit a Claude Code session, CLAUDE.md, or repo for token/context waste and enforce a budget without dropping anything the work actually needs. Use when the user asks to "reduce tokens", "cut my context", "why is this so expensive", "audit my CLAUDE.md", "my context window is full", "trim the context", "save tokens", "lower my Claude Code bill", "optimize context usage", or notices the agent re-reading files and burning the window. Produces a prioritized, safe-by-default set of fixes — never blind truncation.
---

# context-budget

Find where a Claude Code workflow is wasting tokens and fix it **without losing information the task depends on**. The goal is a leaner context, not a lobotomized one: every cut must be justified, and anything load-bearing stays.

## The one rule that overrides everything

**Never remove context the task actually needs to save tokens.** A wrong answer produced cheaply is the most expensive outcome there is — it costs a re-run, plus the human's trust. When you're unsure whether something is needed, keep it and flag it as "review", do not delete it. Optimize the *structure and retrieval* of context first; prune only what is provably stale, duplicated, or irrelevant.

## When this runs

The user is paying too many tokens, hitting the context window, watching the agent re-read the same files, or wants their `CLAUDE.md` / project setup audited for bloat. Your job: measure where the tokens go, then propose ranked fixes that keep correctness intact.

## Procedure

Work in three passes — **measure**, then **diagnose**, then **fix** — and always show the user the diagnosis before changing files.

### 1. Measure (find where the budget goes)

You can't optimize what you haven't located. Identify the biggest line items:

- **Persistent context** — files loaded *every* turn: `CLAUDE.md` (root + nested), `.claude/CLAUDE.md`, imported memory files, large system preambles. These cost their full size on every single message, so a bloated `CLAUDE.md` is the highest-leverage target. Measure each with a rough token estimate (see "Estimating tokens" below).
- **Read amplification** — whole-file `Read` calls where a targeted range, `Grep`, or an index would have sufficed. Re-reads of the same file across turns are pure waste. Look for large files (config dumps, lockfiles, generated code, vendored deps, `.min.js`, `.map`) being read in full.
- **Tool-output bloat** — commands whose output floods the window: `npm test` with full logs, `git log` with no limit, `cat`/`Read` of huge files, `ls -R` on `node_modules`, verbose build output, full HTTP response bodies.
- **Conversation drift** — long sessions accumulating stale exploration, abandoned approaches, and superseded plans that no longer inform the current task.

### 2. Diagnose (rank by leverage)

Score each finding by **cost × frequency**: a 2,000-token block re-paid every turn dwarfs a one-time 10,000-token read. Order your fixes so the user gets the biggest win first. For each finding, name: *what* is costing tokens, *how much* (estimate), *how often* it's paid, and the *fix* — and whether the fix is **safe** (no information loss) or **needs review** (judgement call about what's needed).

### 3. Fix (apply safe wins, propose the rest)

Apply the unambiguous, lossless wins directly; propose anything that involves judgement about what context is needed. The concrete tactics live in **[references/tactics.md](references/tactics.md)** — load it for the full playbook. The high-value categories:

- **Trim persistent context.** Cut filler from `CLAUDE.md` (restated platitudes, obvious instructions, dead links, duplicated rules). Move rarely-needed detail into referenced files that load on demand (progressive disclosure) instead of inline. Keep every rule that changes behavior. (Pairs with the `claude-md-doctor` skill if available.)
- **Prefer targeted reads over whole-file reads.** Locate first (`Grep`/`Glob`/a code index), then `Read` only the relevant line range. Never read lockfiles, generated output, minified bundles, or vendored deps in full. For large codebases, prefer a knowledge-graph/index over brute-force reading — see the `lean-read` skill.
- **Discipline tool output.** Add limits and filters at the source: `git log --oneline -20`, `npm test 2>&1 | tail -50`, `grep` instead of `cat`, `--quiet` flags, head/tail on anything unbounded. Capture verbose output to a file and read the relevant slice rather than streaming it all into context.
- **Order for cache hits.** Put the stable, reusable content (system prompt, tool defs, `CLAUDE.md`, long references) *first and unchanging*; put the volatile per-turn content last. A stable prefix is what makes prompt caching pay off — see the `prompt-cache-optimizer` skill for the deep version.
- **Right-size the output.** Ask for the answer at the altitude needed: a summary, a diff, the specific function — not a re-dump of files already in context. Output tokens cost too.

## Estimating tokens

You usually won't have a tokenizer handy. Use these rules of thumb (English/code, Claude tokenizer ballpark):

- **~4 characters ≈ 1 token**, or **~0.75 tokens per word**. Code and JSON trend a bit denser (more punctuation) — estimate ~3.5 chars/token for those.
- Quick file estimate: `bytes ÷ 4`. For a file you can see the size of, that's a good first cut.
- Report estimates as ranges ("~1.5–2k tokens"), never as false-precision exact counts. The point is relative magnitude to rank fixes, not an accounting figure.

## Output template

```markdown
# Context Budget Audit

**Scope:** <session | CLAUDE.md | repo path>
**Biggest cost:** <the single highest-leverage finding>

## Where the tokens go
| Item | Est. tokens | Paid | Fix | Safe? |
|---|---|---|---|---|
| `CLAUDE.md` filler (§X) | ~1.2k | every turn | cut/condense | ✅ safe |
| whole-file read of `schema.ts` | ~3k | per read | targeted range | ✅ safe |
| `npm test` full log | ~5k | per run | `\| tail -50` | ✅ safe |
| stale plan from early session | ~2k | every turn | drop superseded steps | ⚠ review |

## Recommended fixes (highest leverage first)
1. **<fix>** — <what it saves and why it's safe / what to confirm>
2. ...

## Applied now (lossless)
- <changes you made directly>

## Needs your call (judgement about needed context)
- <changes that risk dropping something — ask before doing>
```

## Rules

- **Correctness is the budget's hard constraint.** Never trade a needed fact for a cheaper turn. If a cut might drop something the task uses, it goes under "needs your call", not "applied".
- **Measure before cutting.** Don't guess what's expensive — locate the actual big line items and rank by cost × frequency.
- **Persistent context is the highest-leverage target** because it's re-paid every turn. Audit `CLAUDE.md` and always-loaded files before chasing one-off reads.
- **Progressive disclosure, not deletion.** The fix for "too much detail" is usually "move it to a referenced file that loads on demand", not "throw it away".
- **Show the audit before you touch files.** The user decides what context is needed for their work; you surface the waste and the tradeoffs.
- Estimates are for *ranking*, not billing. Don't present `bytes ÷ 4` as an exact token count.
