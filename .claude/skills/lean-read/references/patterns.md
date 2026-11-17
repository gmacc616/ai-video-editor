# lean-read patterns — a token-frugal cheat sheet

Load this for the concrete search/read patterns behind the workflow in `SKILL.md`. These are tool-shape patterns, not magic — the principle is always *locate cheaply, read narrowly*.

---

## Locate patterns (cheap — do these first)

| Goal | Pattern | Note |
|---|---|---|
| Find where a symbol is defined/used | `Grep` the name, `-n`, small `-C 2` | returns file:line; jump straight there |
| Find files by name/extension | `Glob "**/*Service.ts"`, `Glob "**/*.config.*"` | never `ls -R` on a big tree |
| Scope a search to the right code | `Grep` with `glob:"src/**"` or `type:"ts"` | don't grep generated/vendored dirs |
| Decide grep-vs-index | `Grep` in **count** mode | 3 hits → read ranges; 300 hits → use an index |
| Find the entry point | `Grep` for `main(`, check manifest `scripts`/`bin` | read the manifest, not the whole tree |
| Find a route/handler | `Grep` the path string or decorator | lands on the exact handler |

## Read patterns (narrow — only after locating)

| Goal | Pattern | Note |
|---|---|---|
| Inspect one function/class | `Read` with `offset`/`limit` around the located line | ~+10 lines context each side is plenty |
| Understand a module's shape | read **exports / signatures / types** first | shape often answers the question without bodies |
| Inspect one config block | grep the key, read that span | not the whole config file |
| Follow an import/caller | one more targeted locate→read | expand on demand, never sweep the dir |

## Never bulk-read (grep inside instead)

`*-lock.json` · `pnpm-lock.yaml` · `*.lock` · `go.sum` · `dist/` · `build/` · `.next/` · `target/` · `__generated__/` · `*.min.js` · `*.map` · `node_modules/` · `vendor/` · `.venv/` · large fixtures / CSV / JSON dumps.

If you need one fact from any of these, `Grep` for it and read only the matching line(s).

## Index-first for structural questions

When the question is "how do these relate / what calls this / where does concept X live" on a large repo:

1. Check for an existing index: a knowledge graph (`graphify-out/`), an LSP/ctags symbol index, an `ARCHITECTURE.md`, a generated API reference. **Query it first.**
2. Use it to get the *specific* file:line spots, then targeted-read only those.
3. Only fall back to repo-wide grep+read when no index exists and the question is a one-off.
4. Read a full architecture dump only for genuine big-picture review — for one question, the scoped query wins.

## The frugality test (apply to every read)

Before a `Read`, ask: **"Do I know roughly where the answer is? If yes, am I reading only that range?"**
- Know where, reading the range → good.
- Know where, reading the whole file anyway → wasteful; add `offset`/`limit`.
- Don't know where → you skipped the locate step; `Grep`/`Glob` first.

And the override: if the file is genuinely small, or the task genuinely requires every branch, just read it. Frugality means not reading what you don't need — never under-reading what you do.
