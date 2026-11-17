#!/usr/bin/env python3
"""
treemap.py — Compact repo map in one shot.

A directory tree with per-file line counts, dependency/build dirs excluded,
depth-limited, and capped. Gets you the shape of an unfamiliar repo in ~40
lines instead of a dozen `ls` round-trips.

Usage:
    python treemap.py [path]
    python treemap.py [path] --depth 3 --max 200

Excludes node_modules/.git/dist/build/etc. Sorts dirs first, then by size.
"""
import sys
import argparse
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "dist", "build", "__pycache__",
             ".venv", "venv", ".next", "target", "vendor", ".idea",
             ".cache", "coverage", ".pytest_cache", ".mypy_cache"}
CODE_EXT = {".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".go", ".rs",
            ".java", ".rb", ".php", ".c", ".cc", ".cpp", ".h", ".hpp",
            ".css", ".scss", ".html", ".vue", ".svelte", ".md", ".json",
            ".yaml", ".yml", ".toml", ".sh"}


def count_lines(p: Path) -> int:
    try:
        with p.open("rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


class Counter:
    def __init__(self, cap):
        self.n = 0
        self.cap = cap
        self.capped = False


def walk(d: Path, prefix: str, depth: int, max_depth: int, out: list, c: Counter):
    if c.n >= c.cap:
        c.capped = True
        return
    try:
        entries = [e for e in d.iterdir() if e.name not in SKIP_DIRS
                   and not e.name.startswith(".")]
    except OSError:
        return
    dirs = sorted([e for e in entries if e.is_dir()], key=lambda x: x.name)
    files = sorted([e for e in entries if e.is_file()], key=lambda x: x.name)

    for e in dirs:
        if c.n >= c.cap:
            c.capped = True
            return
        out.append(f"{prefix}{e.name}/")
        c.n += 1
        if depth < max_depth:
            walk(e, prefix + "  ", depth + 1, max_depth, out, c)
    for e in files:
        if c.n >= c.cap:
            c.capped = True
            return
        if e.suffix.lower() in CODE_EXT:
            out.append(f"{prefix}{e.name}  ({count_lines(e)}L)")
        else:
            out.append(f"{prefix}{e.name}")
        c.n += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("-d", "--depth", type=int, default=3, help="max depth (default 3)")
    ap.add_argument("-m", "--max", type=int, default=200, help="max entries (default 200)")
    args = ap.parse_args()

    root = Path(args.path)
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        sys.exit(2)

    out = []
    c = Counter(args.max)
    print(f"{root.resolve().name}/")
    walk(root, "  ", 1, args.depth, out, c)
    print("\n".join(out))
    print(f"\n--- {c.n} entries"
          + (f", CAPPED at {c.cap} — raise --max or lower --depth" if c.capped else ""))


if __name__ == "__main__":
    main()
