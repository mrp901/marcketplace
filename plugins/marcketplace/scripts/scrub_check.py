#!/usr/bin/env python3
"""Scrub check: find Bluewater-specific literals that should not live under plugins/.

Two modes:
  scrub_check.py <path...>       walk paths, print FAIL/WARN hits, exit 1 on any FAIL
  scrub_check.py --report <file> print every hit in one file grouped by pattern, exit 0 always
  scrub_check.py --list-patterns print the pattern table and exit 0

stdlib only, no third-party dependencies.
"""

import os
import re
import sys

EM_DASH = chr(0x2014)

# Directories skipped while walking a path.
SKIP_DIRS = {".git", "source", "profiles", "__pycache__"}

# This script itself is skipped when walking, since the pattern table below
# necessarily contains the literals it is looking for.
SELF_BASENAME = "scrub_check.py"

DEFAULT_ALLOWLIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scrub_allowlist.txt")

# (name, pattern, severity, ignorecase)
PATTERNS = [
    ("company-name", r"[Bb]luewater|bluewatercontrol", "FAIL", True),
    ("user-name", r"\bMarc\b|Pizzinato", "FAIL", True),
    (
        "colleague-surnames",
        r"\b(Burkett|Wong|Giang|Angelov|Beninski|Lim|Stoykov|Hoo|Ho|Jade)\b",
        "FAIL",
        True,
    ),
    ("vendor-names", r"Fournines|Dicker Data|Decadata|ConnectWise|Bw\.Connect", "FAIL", True),
    ("product-codenames", r"\bCEM\b|Cloud Expense|Idea Garden", "FAIL", True),
    ("bw-cloud-id", r"d9adde8c-ac08-42d5-a730-c39fbd5f3799", "FAIL", False),
    ("bw-state-page-key", r"712020:46176f39", "FAIL", False),
    ("bw-confluence-page-ids", r"3404890113|3370024963|3404857345", "FAIL", False),
    (
        "bw-slack-ids",
        r"U0BNWMX90JF|F0BUY7W6WBH|T040N6GAV4K|C0BVBTUBTHU|D0BP4T1PGV7"
        r"|U054D2JQH1A|U04KE1302GL|U04KBDAEFUK|U04K8JFB269|U064BLS4JUB",
        "FAIL",
        False,
    ),
    ("slack-webhook-trigger", r"hooks\.slack\.com/triggers/", "FAIL", False),
    ("bw-onedrive-path", r"OneDrive - BLUEWATER|MarcPizzinato", "FAIL", True),
    ("bw-ticket-keys", r"ENG-\d+|IG-\d+", "FAIL", False),
    ("bw-custom-fields", r"cf\[110(54|67)\]|\b(10372|11067|11054)\b", "FAIL", False),
    ("em-dash", re.escape(EM_DASH), "FAIL", False),
    (
        "uuid",
        r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b",
        "WARN",
        False,
    ),
    ("slack-id-shape", r"\b[UCDTFG]0[0-9A-Z]{7,10}\b", "WARN", False),
    ("confluence-key-shape", r"\d{6}:[0-9a-f-]{36}", "WARN", False),
    ("service-url", r"https?://[a-z0-9-]+\.(slack|atlassian)\.com", "WARN", True),
]

# Special-cased WARN: two capitalised words on a line that also mentions
# "nicknames" or "people" (a likely real-name pair sitting in a mapping line).
NAME_PAIR_RE = re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b")
CONTEXT_RE = re.compile(r"nicknames|people", re.IGNORECASE)


def compiled_patterns():
    out = []
    for name, pattern, severity, ignorecase in PATTERNS:
        flags = re.IGNORECASE if ignorecase else 0
        out.append((name, re.compile(pattern, flags), severity))
    return out


def load_allowlist(path):
    allowed = set()
    if not os.path.isfile(path):
        return allowed
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            allowed.add(line)
    return allowed


def iter_files(paths):
    for p in paths:
        if os.path.isfile(p):
            if os.path.basename(p) == SELF_BASENAME:
                continue
            yield p
        elif os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for fname in files:
                    if fname == SELF_BASENAME:
                        continue
                    yield os.path.join(root, fname)


def scan_file(path, patterns, allowlist):
    """Yield (line_no, name, severity, matched_text) for each hit in a file."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return
    for i, line in enumerate(lines, start=1):
        for name, regex, severity in patterns:
            for m in regex.finditer(line):
                text = m.group(0)
                if text in allowlist:
                    continue
                yield (i, name, severity, text)
        if CONTEXT_RE.search(line):
            for m in NAME_PAIR_RE.finditer(line):
                text = m.group(0)
                if text in allowlist:
                    continue
                yield (i, "name-pair-on-people-line", "WARN", text)


def mode_scan(paths):
    patterns = compiled_patterns()
    allowlist = load_allowlist(DEFAULT_ALLOWLIST)
    fail_count = 0
    warn_count = 0
    for path in sorted(iter_files(paths)):
        for line_no, name, severity, text in scan_file(path, patterns, allowlist):
            print(f"{severity} {path}:{line_no}: {name}: {text}")
            if severity == "FAIL":
                fail_count += 1
            else:
                warn_count += 1
    print(f"--- {fail_count} FAIL, {warn_count} WARN ---")
    return 1 if fail_count else 0


def mode_report(path):
    patterns = compiled_patterns()
    allowlist = load_allowlist(DEFAULT_ALLOWLIST)
    by_pattern = {}
    for line_no, name, severity, text in scan_file(path, patterns, allowlist):
        by_pattern.setdefault(name, []).append((line_no, severity, text))
    if not by_pattern:
        print(f"no hits in {path}")
        return 0
    for name in sorted(by_pattern):
        hits = by_pattern[name]
        print(f"== {name} ({len(hits)} hit{'s' if len(hits) != 1 else ''}) ==")
        for line_no, severity, text in hits:
            print(f"  {severity} line {line_no}: {text}")
    return 0


def mode_list_patterns():
    print(f"{'name':<28} {'severity':<6} {'case':<6} pattern")
    for name, pattern, severity, ignorecase in PATTERNS:
        print(f"{name:<28} {severity:<6} {'ci' if ignorecase else 'cs':<6} {pattern}")
    print(f"{'name-pair-on-people-line':<28} {'WARN':<6} {'special':<6} two capitalised words on a nicknames/people line")
    return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    if argv[0] == "--list-patterns":
        return mode_list_patterns()
    if argv[0] == "--report":
        if len(argv) < 2:
            print("usage: scrub_check.py --report <file>")
            return 1
        return mode_report(argv[1])
    return mode_scan(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
