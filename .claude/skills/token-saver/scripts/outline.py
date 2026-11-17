#!/usr/bin/env python3
"""
outline.py — Extract the structural skeleton of a source file.

Instead of Reading a 2000-line file into context, get a ~30-line map of its
classes / functions / exports with line numbers, then Read only the exact
ranges you care about.

Usage:
    python outline.py <file>
    python outline.py <file> --grep <regex>   # only symbols matching regex

Supports (by regex, no parser deps): Python, JS/TS, Go, Rust, Java, C/C++,
Ruby, PHP. Falls back to a generic "def/class/function" scan otherwise.
"""
import re
import sys
import argparse
from pathlib import Path

# (label, compiled regex). First capture group is the symbol name.
PATTERNS = {
    ".py": [
        ("class", re.compile(r"^\s*class\s+(\w+)")),
        ("def",   re.compile(r"^\s*(?:async\s+)?def\s+(\w+)")),
    ],
    ".js": [
        ("class", re.compile(r"^\s*(?:export\s+)?(?:default\s+)?class\s+(\w+)")),
        ("func",  re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*(\w+)")),
        ("const", re.compile(r"^\s*(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|\w+)\s*=>")),
    ],
    ".go": [
        ("func", re.compile(r"^func\s+(?:\([^)]*\)\s*)?(\w+)")),
        ("type", re.compile(r"^type\s+(\w+)")),
    ],
    ".rs": [
        ("fn",     re.compile(r"^\s*(?:pub\s+)?(?:async\s+)?fn\s+(\w+)")),
        ("struct", re.compile(r"^\s*(?:pub\s+)?struct\s+(\w+)")),
        ("enum",   re.compile(r"^\s*(?:pub\s+)?enum\s+(\w+)")),
        ("impl",   re.compile(r"^\s*impl\s+(?:.*\s+for\s+)?(\w+)")),
        ("trait",  re.compile(r"^\s*(?:pub\s+)?trait\s+(\w+)")),
    ],
    ".java": [
        ("class",     re.compile(r"^\s*(?:public|private|protected|\s)*class\s+(\w+)")),
        ("interface", re.compile(r"^\s*(?:public|private|protected|\s)*interface\s+(\w+)")),
        ("method",    re.compile(r"^\s*(?:public|private|protected|static|final|\s)+[\w<>\[\],.]+\s+(\w+)\s*\(")),
    ],
    ".rb": [
        ("class",  re.compile(r"^\s*class\s+(\w+)")),
        ("module", re.compile(r"^\s*module\s+(\w+)")),
        ("def",    re.compile(r"^\s*def\s+(\w+)")),
    ],
    ".php": [
        ("class",    re.compile(r"^\s*(?:abstract\s+|final\s+)?class\s+(\w+)")),
        ("function", re.compile(r"^\s*(?:public|private|protected|static|\s)*function\s+(\w+)")),
    ],
}
# Shared aliases
PATTERNS[".ts"] = PATTERNS[".tsx"] = PATTERNS[".jsx"] = PATTERNS[".mjs"] = PATTERNS[".js"]
PATTERNS[".cc"] = PATTERNS[".cpp"] = PATTERNS[".c"] = PATTERNS[".h"] = PATTERNS[".hpp"] = [
    ("func", re.compile(r"^[\w:<>~*&\s]+?\b(\w+)\s*\([^;]*\)\s*(?:const\s*)?\{?\s*$")),
    ("struct", re.compile(r"^\s*(?:typedef\s+)?struct\s+(\w+)")),
    ("class", re.compile(r"^\s*class\s+(\w+)")),
]

GENERIC = [
    ("class", re.compile(r"^\s*class\s+(\w+)")),
    ("func",  re.compile(r"^\s*(?:function|def|fn|func)\s+(\w+)")),
]


def outline(path: Path, grep: str | None):
    ext = path.suffix.lower()
    rules = PATTERNS.get(ext, GENERIC)
    grep_re = re.compile(grep) if grep else None

    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as e:
        print(f"error: cannot read {path}: {e}", file=sys.stderr)
        return 1

    hits = []
    for i, line in enumerate(lines, 1):
        for label, pat in rules:
            m = pat.match(line)
            if m:
                name = m.group(1)
                if grep_re and not grep_re.search(name):
                    continue
                indent = len(line) - len(line.lstrip())
                hits.append((i, indent, label, name))
                break

    print(f"{path}  ({len(lines)} lines, {len(hits)} symbols)")
    if not hits:
        print("  (no symbols matched — Read the file directly if small)")
        return 0
    for lineno, indent, label, name in hits:
        pad = "  " * (indent // 4)
        print(f"  {lineno:>5}  {pad}{label} {name}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--grep", default=None, help="only show symbols whose name matches this regex")
    args = ap.parse_args()
    p = Path(args.file)
    if not p.is_file():
        print(f"error: not a file: {p}", file=sys.stderr)
        sys.exit(2)
    sys.exit(outline(p, args.grep))


if __name__ == "__main__":
    main()
