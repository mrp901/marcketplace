#!/usr/bin/env python3
"""Validate one skill-health log entry against references/log-format.md's shape.

Deterministic check for SKILL.md step 4, before an entry is prepended to
kb.paths.utility/skill-health/<skill-slug>.md. Checks structure only, never content quality
- it cannot judge whether a bullet's evidence is real, only that the entry has the shape
this skill promises to write.

Usage:
    check_log_entry.py <entry.txt>

<entry.txt> holds exactly one entry (the heading through its trailing blank line), as it
will be prepended. Reads stdin instead of a file when <entry.txt> is "-".

Checks:
  - First non-blank line matches "## YYYY-MM-DD - green|amber|red".
  - An "Evidence window: ... to ..." line is present.
  - 2 to 4 bullet lines (lines starting with "- ") excluding the evidence-sources line.
  - Exactly one "- Evidence sources available:" line, present.

Exits 0 and prints "OK" if every check passes; exits 1 and prints one line per failed check
otherwise. Never modifies the input.
"""

import re
import sys

HEADING_RE = re.compile(r"^##\s+\d{4}-\d{2}-\d{2}\s+-\s+(green|amber|red)\s*$")
WINDOW_RE = re.compile(r"^Evidence window:\s+\d{4}-\d{2}-\d{2}\s+to\s+\d{4}-\d{2}-\d{2}")
SOURCES_RE = re.compile(r"^-\s+Evidence sources available:")
BULLET_RE = re.compile(r"^-\s+")


def check(text):
    lines = [l for l in text.splitlines()]
    failures = []

    non_blank = [l for l in lines if l.strip()]
    if not non_blank or not HEADING_RE.match(non_blank[0].strip()):
        failures.append("first non-blank line is not '## YYYY-MM-DD - green|amber|red'")

    if not any(WINDOW_RE.match(l.strip()) for l in lines):
        failures.append("missing 'Evidence window: <date> to <date>' line")

    sources_lines = [l for l in lines if SOURCES_RE.match(l.strip())]
    if len(sources_lines) != 1:
        failures.append(
            f"expected exactly one 'Evidence sources available:' line, found {len(sources_lines)}"
        )

    bullets = [
        l for l in lines
        if BULLET_RE.match(l.strip()) and not SOURCES_RE.match(l.strip())
    ]
    if not (2 <= len(bullets) <= 4):
        failures.append(f"expected 2 to 4 evidence bullets, found {len(bullets)}")

    return failures


def main(argv):
    if len(argv) != 1:
        print("usage: check_log_entry.py <entry.txt>", file=sys.stderr)
        return 2

    path = argv[0]
    if path == "-":
        text = sys.stdin.read()
    else:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

    failures = check(text)
    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
