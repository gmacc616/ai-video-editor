---
name: lean-read
description: Read and understand large codebases token-efficiently — locate with search/index first, then read only the ranges that matter, instead of pulling whole files into context. Use when the user asks to "explore this codebase without burning tokens", "find where X is", "understand this large repo", "stop re-reading whole files", "read efficiently", "the codebase is huge", "trace this function", or when an agent is about to brute-force read big files. Turns "open everything" into a cheap locate → targeted-read → (index for the big stuff) workflow.
---

# lean-read

Understand a codebase without paying to load it. The expensive habit is reading whole files (or whole directories) to find or understand one thing. The lean habit is: **locate cheaply, read narrowly, and use an index for anything structural.** Same understanding, a fraction of the tokens.

## The core loop: locate → read range → confirm

For almost every "where/what/how" question about code, follow this order. Each step is much cheaper than the brute-force alternative.

1. **Locate** with search, not reading. Use `Grep` (content) and `Glob` (filenames) to find *which file* and *which lines*. These return paths and line numbers for pennies — a `Grep` for a symbol is orders of magnitude cheaper than reading the files that contain it.
2. **Read the range, not the file.** Once you know the line numbers, `Read` with `offset` + `limit` to pull just the relevant span (plus a little surrounding context). A 30-line function does not require a 2,000-line file in your window.
3. **Confirm before you build on it.** Read enough to verify the thing actually does what its name suggests — but stop there. Don't keep reading "to be safe"; that's how the window fills.

Expand outward only when the task needs it: follow a specific import, a caller, a callee — each as another targeted locate→read, never a directory-wide sweep.

## When this runs

The user is working in a large or unfamiliar repo and wants to find something, understand a flow, or answer a structural question — and either explicitly wants to conserve tokens/context, or is watching the agent read far more than it needs.

## Tactics

### Search beats reading for locating
- **Find a symbol's definition/uses:** `Grep` the name across the repo; jump straight to the file:line it reports.
- **Find files by name/type:** `Glob` (`**/*.config.*`, `src/**/*Service.ts`) instead of `ls -R`.
- **Narrow with filters:** scope `Grep` by `glob`/`type` so you search the right files only. Use `-n` for line numbers and small `-C` context, not the whole file.
- **Count before you commit:** a `Grep` in count mode tells you whether a symbol appears 3 times or 300 — so you know whether to read targeted ranges or step back and use an index.

### Read narrowly
- Always pass a line range when you know it. Read the function, the class, the config block — not the file.
- Read the **interface/signature first** (exports, type defs, function signatures, the public surface) to understand *shape* before diving into implementation bodies. Often the signature answers the question.
- Don't re-read a file already in context this session — it's already loaded; re-reading doubles the cost for nothing. Re-read only after an edit or for a genuinely different section.

### Never bulk-read these
Reading these in full is almost always waste — locate inside them instead:
- Lockfiles (`*-lock.json`, `pnpm-lock.yaml`, `*.lock`, `go.sum`).
- Generated / build output (`dist/`, `build/`, `.next/`, `target/`, `__generated__/`).
- Minified bundles + source maps (`*.min.js`, `*.map`).
- Vendored deps (`node_modules/`, `vendor/`, `.venv/`).
- Large fixtures / data dumps — sample or grep them, don't ingest them.

### Use an index for structural questions (the big win on large repos)
On a large codebase, repeatedly grepping and reading to assemble a mental model gets expensive fast. A **code index / knowledge graph** answers "what calls this", "how are these modules related", "where does this concept live" from a compact precomputed summary instead of raw source.
- If the repo already has an index (e.g. a `graphify-out/` knowledge graph, a ctags/LSP symbol index, an architecture doc, or a generated API reference), **query that first** and only open source files for the specific spots it points you to.
- If it doesn't and you'll be answering many questions about this repo, building a lightweight index up front is cheaper than re-reading across the whole session. Prefer it over brute force.
- Read a full `GRAPH_REPORT.md`-style architecture dump only for genuine big-picture review — for a targeted question, the scoped query is far cheaper.

### Right-size the answer
When you report back, give the located file:line and the relevant snippet — not a re-dump of everything you opened. The user can see the snippet; reference the rest by path.

## Worked example

> "Where is the auth token refreshed, and is there a race condition?"

Brute force (expensive): read `src/auth/` end to end.

Lean:
1. `Grep` for `refresh` / `token` scoped to `src/auth/**` with `-n` → reports `src/auth/session.ts:142`.
2. `Read` `src/auth/session.ts` with `offset≈120, limit≈60` → the refresh function and its lock (or lack of one).
3. If it calls a `mutex`/`lock` helper, `Grep` that symbol → one more targeted read of just that helper.
4. Answer from those ~120 lines total, citing `session.ts:142`, instead of the whole module.

## Rules

- **Locate before you read. Always.** Searching for the spot is far cheaper than reading to find it.
- **Read ranges, not files** — pass `offset`/`limit` whenever you know roughly where the code is. Whole-file reads are a last resort for genuinely small or genuinely must-read-all files.
- **Don't bulk-read lockfiles, generated code, minified bundles, or vendored deps** — ever. Grep inside them if you need one thing.
- **Prefer an index/graph for structural questions** on large repos; fall back to grep+read for spot lookups.
- **Never sacrifice correctness for frugality.** If the task genuinely needs the whole file (a small file, or you must understand every branch), read it — being cheap and wrong is the worst outcome. Lean reading is about not reading what you *don't* need, not about under-reading what you do.
- Don't re-read what's already in context.
