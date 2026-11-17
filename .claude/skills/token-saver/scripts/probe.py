#!/usr/bin/env python3
"""
probe.py — Token-frugal search. Like grep, but built to NOT flood context.

Returns each match with a tiny window of surrounding lines, collapses
adjacent/overlapping hits into one block, and caps total output so a broad
search can never dump thousands of lines into the conversation.

Usage:
    python probe.py <regex> [path]
    python probe.py <regex> [path] --context 2 --max 30 --glob "*.py"

Defaults are deliberately tight: 2 lines of context, 30 blocks max.
Skips node_modules/.git/dist/build/__pycache__ and binary-looking files.
"""
import re
import sys
import argparse
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "dist", "build", "__pycache__",
             ".venv", "venv", ".next", "target", "vendor", ".idea", ".cache"}
BINARY_EXT = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".gz", ".tar",
              ".exe", ".dll", ".so", ".dylib", ".woff", ".woff2", ".ttf",
              ".mp4", ".mp3", ".ico", ".webp", ".lock"}


def iter_files(root: Path, glob: str | None):
    if root.is_file():
        yield root
        return
    for p in root.rglob(glob or "*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix.lower() in BINARY_EXT:
            continue
        yield p


def probe(pattern, root, ctx, cap, glob, ignore_case):
    flags = re.IGNORECASE if ignore_case else 0
    try:
        rx = re.compile(pattern, flags)
    except re.error as e:
        print(f"error: bad regex: {e}", file=sys.stderr)
        return 2

    blocks = []          # (path, start_line, [lines])
    total_matches = 0
    truncated = False

    for path in iter_files(root, glob):
        try:
            lines = path.read_text(encoding="utf-8", errors="strict").splitlines()
        except (OSError, UnicodeDecodeError):
            continue  # skip unreadable / binary

        hit_idxs = [i for i, ln in enumerate(lines) if rx.search(ln)]
        if not hit_idxs:
            continue
        total_matches += len(hit_idxs)

        # merge into windows
        windows = []  # [start, end] inclusive, 0-based
        for i in hit_idxs:
            lo, hi = max(0, i - ctx), min(len(lines) - 1, i + ctx)
            if windows and lo <= windows[-1][1] + 1:
                windows[-1][1] = max(windows[-1][1], hi)
            else:
                windows.append([lo, hi])

        for lo, hi in windows:
            if len(blocks) >= cap:
                truncated = True
                break
            blocks.append((path, lo, lines[lo:hi + 1]))
        if truncated:
            break

    for path, lo, chunk in blocks:
        print(f"\n{path}:{lo + 1}")
        for off, ln in enumerate(chunk):
            print(f"  {lo + 1 + off:>5}  {ln}")

    print(f"\n--- {total_matches} match(es), {len(blocks)} block(s) shown"
          + (f", CAPPED at {cap} — narrow the regex or raise --max" if truncated else ""))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pattern")
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("-C", "--context", type=int, default=2, help="lines around each match (default 2)")
    ap.add_argument("-m", "--max", type=int, default=30, help="max blocks to show (default 30)")
    ap.add_argument("-g", "--glob", default=None, help='filter files, e.g. "*.py"')
    ap.add_argument("-i", "--ignore-case", action="store_true")
    args = ap.parse_args()
    root = Path(args.path)
    if not root.exists():
        print(f"error: no such path: {root}", file=sys.stderr)
        sys.exit(2)
    sys.exit(probe(args.pattern, root, args.context, args.max, args.glob, args.ignore_case))


if __name__ == "__main__":
    main()
