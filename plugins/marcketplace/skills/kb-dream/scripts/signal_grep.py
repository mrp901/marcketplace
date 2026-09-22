#!/usr/bin/env python3
"""Deterministic first pass over session notes for kb-dream's signal extraction.

Usage:
    signal_grep.py <session-note> [<session-note> ...]

Greps each session note for the four signal shapes (see references/signal-extraction.md):
corrections, preferences, decisions, recurring friction. Prints match context (the line
plus one line either side), never the whole note, so the caller can decide what merits a
close read without re-reading everything from scratch.

Degrades gracefully: a path that doesn't exist locally (the knowledge base is a remote
connector and these files were fetched, not downloaded to disk) is reported and skipped,
not a hard failure - the caller falls back to reading the fetched text directly.

stdlib only, no third-party dependencies.
"""

import re
import sys

PATTERNS = {
    "correction": re.compile(
        r"\b(actually|corrected|no,|wrong|that's not|I said|I meant|stop doing|don't do)\b",
        re.IGNORECASE,
    ),
    "preference": re.compile(
        r"\b(I prefer|always use|never use|from now on|going forward|remember that|default to)\b",
        re.IGNORECASE,
    ),
    "decision": re.compile(
        r"\b(let's go with|I decided|we're using|the plan is|we agreed|switch to)\b",
        re.IGNORECASE,
    ),
    "friction": re.compile(
        r"\b(again|every time|keep forgetting|same as before|carried forward)\b",
        re.IGNORECASE,
    ),
}


def scan(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as exc:
        print(f"SKIP: {path} not readable locally ({exc}); fall back to the fetched text")
        return
    for i, line in enumerate(lines):
        for kind, pattern in PATTERNS.items():
            if pattern.search(line):
                start = max(0, i - 1)
                end = min(len(lines), i + 2)
                context = "".join(lines[start:end]).strip()
                print(f"{kind}\t{path}:{i + 1}\t{context}")


def main(argv):
    if not argv:
        print("usage: signal_grep.py <session-note> [...]", file=sys.stderr)
        return 2
    for path in argv:
        scan(path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
