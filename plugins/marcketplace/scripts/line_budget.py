#!/usr/bin/env python3
"""Line budget check for SKILL.md files.

  line_budget.py <SKILL.md>   line count, PASS/FAIL against a 150-line cap,
                               movable blocks with suggested destinations,
                               remaining-line estimate if all were relocated,
                               and WARN checks on description/## Needs.
  line_budget.py --all        walk plugins/marcketplace/skills/*/SKILL.md,
                               one PASS/FAIL line per skill, exit 1 if any FAIL.
                               "no skills yet" and exit 0 if none exist.

stdlib only, no third-party dependencies.
"""

import glob
import os
import re
import sys

LINE_CAP = 150
FENCE_MIN_LINES = 6
TABLE_MIN_ROWS = 8
LIST_MIN_ITEMS = 10

SECTION_HEADING_RE = re.compile(
    r"^#+\s*(Acceptance criteria|Worked example|Examples?|Format)\s*$", re.IGNORECASE
)
HEADING_RE = re.compile(r"^#+\s")
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
TABLE_SEP_RE = re.compile(r"^\s*\|?[\s:|-]+\|?\s*$")
BULLET_RE = re.compile(r"^\s*([-*+]|\d+[.)])\s+")
FENCE_RE = re.compile(r"^\s*```")


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "block"


def find_movable_blocks(lines):
    """Return list of (start, end, kind, first_line) using 1-based inclusive line numbers."""
    blocks = []
    n = len(lines)
    i = 0
    while i < n:
        line = lines[i]

        # Fenced code block
        if FENCE_RE.match(line):
            start = i + 1
            j = i + 1
            while j < n and not FENCE_RE.match(lines[j]):
                j += 1
            end = j + 1 if j < n else n
            block_len = end - start + 1
            if block_len > FENCE_MIN_LINES:
                blocks.append((start, end, "fenced code block", lines[start - 1].strip()))
            i = j + 1
            continue

        # Markdown table
        if TABLE_ROW_RE.match(line) and i + 1 < n and TABLE_SEP_RE.match(lines[i + 1]) and "|" in lines[i + 1]:
            start = i + 1
            j = i
            while j < n and TABLE_ROW_RE.match(lines[j]):
                j += 1
            end = j
            rows = end - start + 1 - 1  # exclude header separator row from "rows over 8"
            if rows > TABLE_MIN_ROWS:
                blocks.append((start, end, "markdown table", lines[start - 1].strip()))
            i = j
            continue

        # Bullet / numbered list, including wrapped continuation lines that
        # belong to the same item (only a heading, a fence, or a double
        # blank line ends the run).
        if BULLET_RE.match(line):
            start = i + 1
            j = i
            blank_run = 0
            while j < n:
                if lines[j].strip() == "":
                    blank_run += 1
                    if blank_run >= 2:
                        break
                elif HEADING_RE.match(lines[j]) or FENCE_RE.match(lines[j]):
                    break
                else:
                    blank_run = 0
                j += 1
            end_idx = j - 1
            while end_idx >= i and lines[end_idx].strip() == "":
                end_idx -= 1
            end = end_idx + 1
            count = sum(1 for k in range(i, end_idx + 1) if BULLET_RE.match(lines[k]))
            if count > LIST_MIN_ITEMS:
                blocks.append((start, end, "list", lines[start - 1].strip()))
            i = end_idx + 1
            continue

        # Heading matching flagged section names
        if SECTION_HEADING_RE.match(line.strip()):
            start = i + 1
            j = i + 1
            while j < n and not HEADING_RE.match(lines[j]):
                j += 1
            end = j
            blocks.append((start, end, "flagged section", lines[start - 1].strip()))
            i = j
            continue

        i += 1

    return blocks


def check_description(text):
    m = re.search(r"^description:\s*(.*)$", text, re.MULTILINE)
    if not m:
        return "WARN: no frontmatter description found"
    desc = m.group(1).strip().strip('"')
    if not desc.startswith("Use when"):
        return f"WARN: description does not start with 'Use when': {desc[:60]}"
    return None


def check_needs_heading(text):
    if not re.search(r"^##\s+Needs\s*$", text, re.MULTILINE):
        return "WARN: no '## Needs' heading found"
    return None


def report_one(path, verbose=True):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    lines = text.splitlines()
    total = len(lines)
    status = "PASS" if total <= LINE_CAP else "FAIL"

    blocks = find_movable_blocks(lines)
    movable_lines = sum((end - start + 1) for start, end, _, _ in blocks)
    remaining = total - movable_lines

    if verbose:
        print(f"{path}: {total} lines - {status} (cap {LINE_CAP})")
        if blocks:
            print("Movable blocks:")
            for start, end, kind, first in blocks:
                n = end - start + 1
                dest = f"references/{slugify(first)}.md"
                print(f"  {start}-{end} ({n} lines): {kind}: {first[:60]} -> {dest}")
            print(f"Remaining if all relocated: {remaining} lines")
        else:
            print("No movable blocks found.")

        warnings = []
        d = check_description(text)
        if d:
            warnings.append(d)
        nd = check_needs_heading(text)
        if nd:
            warnings.append(nd)
        for w in warnings:
            print(w)

    return status, total


def mode_single(path):
    status, _ = report_one(path, verbose=True)
    return 0 if status == "PASS" else 1


def mode_all():
    skill_files = sorted(glob.glob("plugins/marcketplace/skills/*/SKILL.md"))
    if not skill_files:
        print("no skills yet")
        return 0
    any_fail = False
    for path in skill_files:
        skill_name = os.path.basename(os.path.dirname(path))
        status, total = report_one(path, verbose=False)
        print(f"{status} {total:>4}  {skill_name}")
        if status == "FAIL":
            any_fail = True
    return 1 if any_fail else 0


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    if argv[0] == "--all":
        return mode_all()
    return mode_single(argv[0])


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except BrokenPipeError:
        # output was piped into something that closed early (head, less); not an error
        try:
            sys.stdout.close()
        except Exception:
            pass
        sys.exit(0)
