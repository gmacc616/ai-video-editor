#!/usr/bin/env python3
"""
filter.py — Run a command and return only the signal, not the flood.

Wraps a build/test/lint command, streams its output through error/warning
detection, and prints only the interesting lines plus a one-line summary.
A 900-line `npm test` log becomes ~5 lines in context. Exit code is
preserved so the caller still knows pass/fail.

Usage:
    python filter.py -- npm test
    python filter.py --tail 5 -- npx tsc --noEmit
    python filter.py --keep "FAIL|Error|✓|✗" -- pytest

By default matches common error/warning/failure markers across ecosystems.
Always shows the last few lines (test summaries usually live there).
"""
import re
import sys
import subprocess
import argparse
from collections import deque

DEFAULT_KEEP = re.compile(
    r"\b(error|errors|failed|failure|fail|exception|traceback|"
    r"warning|warn|panic|fatal|assert|✗|✘|×|✖)\b"
    r"|^\s*at\s+.+:\d+"          # stack frames
    r"|:\d+:\d+:"               # file:line:col diagnostics
    r"|\bFAIL\b|\bERROR\b",
    re.IGNORECASE,
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", default=None, help="regex of lines to keep (overrides default)")
    ap.add_argument("--tail", type=int, default=8, help="always show last N lines (default 8)")
    ap.add_argument("--max", type=int, default=60, help="cap kept lines (default 60)")
    ap.add_argument("cmd", nargs=argparse.REMAINDER, help="-- then the command")
    args = ap.parse_args()

    cmd = args.cmd
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if not cmd:
        print("error: no command. Use:  python filter.py -- <command>", file=sys.stderr)
        sys.exit(2)

    keep = re.compile(args.keep, re.IGNORECASE) if args.keep else DEFAULT_KEEP

    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1, errors="replace",
        )
    except FileNotFoundError:
        print(f"error: command not found: {cmd[0]}", file=sys.stderr)
        sys.exit(127)

    total = 0
    kept = []
    tail = deque(maxlen=max(0, args.tail))
    capped = False

    assert proc.stdout is not None
    for line in proc.stdout:
        line = line.rstrip("\n")
        total += 1
        tail.append(line)
        if keep.search(line):
            if len(kept) < args.max:
                kept.append(line)
            else:
                capped = True
    code = proc.wait()

    # Merge kept lines + tail without duplicating the overlap.
    shown = list(kept)
    for t in tail:
        if t not in shown[-args.tail:]:
            shown.append(t)

    if shown:
        print("\n".join(shown))
    verdict = "PASSED" if code == 0 else f"FAILED (exit {code})"
    print(f"\n--- {verdict} | {total} lines total, {len(kept)} matched"
          + (" (CAPPED)" if capped else ""))
    sys.exit(code)


if __name__ == "__main__":
    main()
