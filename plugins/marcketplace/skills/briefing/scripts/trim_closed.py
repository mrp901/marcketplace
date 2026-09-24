#!/usr/bin/env python3
"""Trim the Closed log to 7 days or 40 lines, whichever bound is hit first.

Implements surface-protocol.md's "The Closed log" retention rule and SKILL.md step 6's
"mechanically, every run this step fires" clause. Deterministic - no model judgement.

Usage:
    trim_closed.py <closed.txt> [--today YYYY-MM-DD] [--max-days N] [--max-lines N]

<closed.txt> holds one Closed line per line, newest first, in the format:
    - <date> (<tag>) <outcome> - <original text, 120 chars> - <by you | by <handler>>
where <date> is YYYY-MM-DD or a "Mon D" / "Mon D, YYYY" form line_budget-style tools in this
repo already use elsewhere. Lines that don't start with "- " are passed through untouched
(so a heading or blank line ahead of the list survives), but are excluded from the day/line
counts.

Reads stdin instead of a file when <closed.txt> is "-". Writes the trimmed list to stdout,
newest first, unchanged order otherwise. Exits 0 always (a parse miss on one line drops that
line rather than failing the whole trim - see "never rewrite a block you cannot parse" in
state-schema.md; a Closed line this script can't date is treated as an item to keep, since
the safe failure mode for a bounded log is to keep too much, not to silently drop an
undateable-but-legitimate line).
"""

import argparse
import re
import sys
from datetime import date, datetime, timedelta

DEFAULT_MAX_DAYS = 7
DEFAULT_MAX_LINES = 40

DATE_RE = re.compile(
    r"^-\s+(\d{4}-\d{2}-\d{2}|[A-Za-z]{3,9}\s+\d{1,2}(?:,\s*\d{4})?)\b"
)
MONTHS = {
    m: i
    for i, m in enumerate(
        [
            "jan", "feb", "mar", "apr", "may", "jun",
            "jul", "aug", "sep", "oct", "nov", "dec",
        ],
        start=1,
    )
}


def parse_date(token, today):
    token = token.strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", token)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.match(r"^([A-Za-z]{3,9})\s+(\d{1,2})(?:,\s*(\d{4}))?$", token)
    if m:
        mon = m.group(1)[:3].lower()
        if mon not in MONTHS:
            return None
        day = int(m.group(2))
        year = int(m.group(3)) if m.group(3) else today.year
        try:
            d = date(year, MONTHS[mon], day)
        except ValueError:
            return None
        # A dateless year that lands in the future is last year's occurrence.
        if not m.group(3) and d > today:
            d = date(year - 1, MONTHS[mon], day)
        return d
    return None


def trim(lines, today, max_days, max_lines):
    cutoff = today - timedelta(days=max_days)
    kept = []
    dated_count = 0
    for line in lines:
        stripped = line.rstrip("\n")
        m = DATE_RE.match(stripped)
        if not m:
            # Not a Closed line (heading, blank line) - pass through, uncounted.
            kept.append(stripped)
            continue
        d = parse_date(m.group(1), today)
        if d is None:
            # Undateable Closed line - keep it (safe failure mode), uncounted toward
            # the day bound, but counted toward the line bound like any other entry.
            dated_count += 1
            if dated_count <= max_lines:
                kept.append(stripped)
            continue
        dated_count += 1
        if dated_count > max_lines or d < cutoff:
            continue
        kept.append(stripped)
    return kept


def main(argv):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("path")
    p.add_argument("--today", default=None, help="Override 'today' as YYYY-MM-DD (default: real today).")
    p.add_argument("--max-days", type=int, default=DEFAULT_MAX_DAYS)
    p.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES)
    args = p.parse_args(argv)

    today = (
        datetime.strptime(args.today, "%Y-%m-%d").date()
        if args.today
        else date.today()
    )

    if args.path == "-":
        text = sys.stdin.read()
    else:
        with open(args.path, "r", encoding="utf-8") as f:
            text = f.read()

    lines = text.splitlines()
    kept = trim(lines, today, args.max_days, args.max_lines)
    for line in kept:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
