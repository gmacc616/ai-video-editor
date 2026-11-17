# Token Saver — full protocol

Load this only when you need flag details or hit an edge case. All scripts are
zero-dependency Python 3 (stdlib only) and print a `--- summary` final line.

## outline.py

```
python outline.py <file> [--grep <regex>]
```

Extracts classes/functions/exports with line numbers. `--grep` filters symbol
names by regex. Languages: py, js/ts/jsx/tsx/mjs, go, rs, java, rb, php, c/cpp.
Unknown extensions fall back to a generic class/def/fn/func scan.

**Workflow:** outline → pick ranges → `Read(file, offset, limit)` on just those
ranges. A 2000-line file becomes a 30-line map plus two 40-line reads instead
of one 2000-line read.

## probe.py

```
python probe.py <regex> [path] [-C ctx] [-m max] [-g glob] [-i]
```

- `-C/--context` lines around each hit (default 2)
- `-m/--max` max blocks before capping (default 30)
- `-g/--glob` file filter, e.g. `"*.py"`
- `-i/--ignore-case`

Adjacent/overlapping hits merge into one block. Skips
`node_modules/.git/dist/build/__pycache__/.venv/target/vendor` and binary
extensions. Silently skips files that fail UTF-8 decode. If output shows
`CAPPED`, tighten the regex — don't just raise `--max`.

## filter.py

```
python filter.py [--keep <regex>] [--tail N] [--max N] -- <command>
```

Runs `<command>` (stdout+stderr merged), keeps only lines matching `--keep`
(default: error/warn/fail/exception/stack-frame/`file:line:col` markers across
ecosystems), always appends the last `--tail` lines (default 8, where test
summaries live), caps kept lines at `--max` (default 60). **Exit code is
preserved**, so pass/fail is still authoritative.

The `--` separator is required before the command. Example:
`python filter.py --tail 3 -- npx tsc --noEmit`

If a command's important output doesn't match the default keep-regex, pass an
explicit `--keep`, e.g. `--keep "PASS|FAIL|✓|✗"` for a test runner.

## treemap.py

```
python treemap.py [path] [-d depth] [-m max]
```

- `-d/--depth` max nesting (default 3)
- `-m/--max` max entries (default 200)

Code files show `(NNN L)` line counts. Dirs first then files, alphabetical.
Same skip-list as probe, plus coverage/cache dirs and dotfiles/dotdirs.

## When NOT to use these

- File is already small (<~150 lines): just Read it.
- You need exact byte-level content (config with subtle whitespace): Read it.
- Single known symbol in a known file: Read the range directly.

The goal is fewer tokens for the same understanding — not ceremony.
