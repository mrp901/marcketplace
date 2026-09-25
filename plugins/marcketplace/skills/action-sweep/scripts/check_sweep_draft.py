#!/usr/bin/env python3
"""Mechanical check for one action-sweep draft's frontmatter and section shape.

  check_sweep_draft.py <path/to/Drafts/sweep-YYMMDD-N.md>

Exits 0 and prints PASS if the draft carries every required frontmatter key, a
recognised tier, and section headings drawn from the documented set. Exits 1 and prints
one FAIL line per problem otherwise. This checks shape only, never content - whether a
draft is any good is still a human/model judgement call.

stdlib only, no third-party dependencies.
"""

import re
import sys

REQUIRED_FRONTMATTER_KEYS = [
    "type",
    "title",
    "description",
    "tags",
    "status",
    "generated",
    "supersedes_on",
    "source",
    "tier",
]

KNOWN_TIERS = {"small", "larger", "larger+defined", "modification"}

KNOWN_SECTIONS = [
    "Ticket",
    "Open questions",
]


def check(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()

    problems = []

    fm_match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not fm_match:
        problems.append("no frontmatter block found (expected --- ... --- at file start)")
        fm_text = ""
    else:
        fm_text = fm_match.group(1)

    for key in REQUIRED_FRONTMATTER_KEYS:
        if not re.search(rf"^{re.escape(key)}\s*:", fm_text, re.MULTILINE):
            problems.append(f"missing frontmatter key: {key}")

    if not re.search(r"^type:\s*Draft\s*$", fm_text, re.MULTILINE):
        problems.append("frontmatter 'type' is not 'Draft'")

    if not re.search(r"^status:\s*draft\s*$", fm_text, re.MULTILINE):
        problems.append("frontmatter 'status' is not 'draft'")

    tier = re.search(r"^tier:\s*(.+?)\s*$", fm_text, re.MULTILINE)
    if tier and tier.group(1) not in KNOWN_TIERS:
        problems.append(f"unrecognised tier: {tier.group(1)!r} (expected one of {sorted(KNOWN_TIERS)})")

    headings = re.findall(r"^##\s+(.+?)\s*$", text, re.MULTILINE)
    for h in headings:
        if h not in KNOWN_SECTIONS:
            problems.append(f"unrecognised section heading: {h!r} (not in the documented set)")
    if "Ticket" not in headings:
        problems.append("missing '## Ticket' section")

    if not re.search(r"^#\s+Draft - ", text, re.MULTILINE):
        problems.append("missing top-level '# Draft - <short title> (<tag>)' title line")

    for field in ("Line", "Source", "Route"):
        if not re.search(rf"^\*\*{field}:\*\*", text, re.MULTILINE):
            problems.append(f"missing '**{field}:**' line")

    return problems


def main():
    if len(sys.argv) != 2:
        print("usage: check_sweep_draft.py <path/to/Drafts/sweep-YYMMDD-N.md>")
        return 2

    problems = check(sys.argv[1])
    if problems:
        for p in problems:
            print(f"FAIL: {p}")
        return 1

    print(f"PASS: {sys.argv[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
