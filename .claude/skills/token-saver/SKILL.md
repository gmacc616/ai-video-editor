---
name: token-saver
description: Use when working in a large or unfamiliar codebase, or when context is filling up, to slash token usage. Provides scripts to outline files instead of reading them whole, search with tight context windows, filter noisy build/test output down to errors, and map a repo in one shot. Invoke before Reading big files, running verbose commands, or broad greps.
---

# Token Saver

The context killer in Claude Code is **tool output**, not your prose. One full
`Read` of a big file, one verbose `npm test`, one wide `grep` can each dump
thousands of lines into context. These scripts do the heavy lifting in the
shell and return only the distilled result.

`SCRIPTS=` the `scripts/` dir next to this file. Run with `python`.

## Decision tree

- **Need to understand a file >~200 lines?**
  `python SCRIPTS/outline.py <file>` → skeleton with line numbers.
  Then `Read` only the exact ranges you need. Do NOT read the whole file.

- **Searching for something?**
  `python SCRIPTS/probe.py "<regex>" [path] --glob "*.ts"`
  Returns matches with ±2 lines, merged and capped. Prefer over dumping grep.

- **Running a build / test / lint / typecheck?**
  `python SCRIPTS/filter.py -- <command>`
  Returns only error/warning lines + a pass/fail summary. Exit code preserved.

- **Getting oriented in an unfamiliar repo?**
  `python SCRIPTS/treemap.py [path]` → compact tree with line counts.

- **Broad, open-ended exploration** (trace a feature across many files, audit,
  survey)? Delegate to a subagent and ask for a short summary back — keep the
  raw file contents out of the main thread entirely.

## Rules

- Never Read a file whole when an outline + targeted range read will do.
- Never let a command dump its full log; wrap it in `filter.py`.
- When reporting back, summarize — don't paste code or logs verbatim.
- All scripts print a `--- ...` summary line and cap their output; if you see
  `CAPPED`, narrow the query rather than raising the cap blindly.

See `reference/protocol.md` for flags and edge cases (load only if needed).
