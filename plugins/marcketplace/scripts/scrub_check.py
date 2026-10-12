#!/usr/bin/env python3
"""Scrub check: find organisation-specific literals that should not live under plugins/.

Two kinds of pattern are checked:

  built-in shapes   committed in this file: things that look like a service id, a cloud
                    id, a webhook trigger URL, a service hostname, or an em dash. These
                    are organisation-neutral and catch most leaks by shape alone.
  the denylist      the real names, ids, keys and codenames of the organisation this
                    install runs for. They are themselves private data, so they never
                    live in the repository: they load from
                    `scrub_denylist.local.txt` next to this script (gitignored), or from
                    the file named by the SCRUB_DENYLIST environment variable. See
                    `scrub_denylist.example.txt` for the format.

Without a denylist the check still runs on the built-in shapes and says so in its
output. CI can supply the denylist from a secret (see ci/validate.yml).

Modes:
  scrub_check.py <path...>       walk paths, print FAIL/WARN hits, exit 1 on any FAIL
  scrub_check.py --report <file> print every hit in one file grouped by pattern, exit 0 always
  scrub_check.py --list-patterns print the pattern table (built-in plus denylist) and exit 0

stdlib only, no third-party dependencies.
"""

import os
import re
import sys

EM_DASH = chr(0x2014)

# Directories skipped while walking a path.
SKIP_DIRS = {".git", "source", "profiles", "__pycache__"}

# The TypeScript declarations Claude Code writes beside a plugin it loads with
# --plugin-dir (.claude-plugin/types/). They are the engine's, not this repo's,
# gitignored, and full of em dashes. Matched as a parent/child pair, so the
# plugin's own types/ folder is still scanned.
SKIP_DIR_PAIRS = {(".claude-plugin", "types")}

# Skipped when walking: this script (the pattern table below necessarily contains the
# shapes it looks for) and the denylist files (which hold the literals themselves).
SKIP_BASENAMES = {"scrub_check.py", "scrub_denylist.local.txt", "scrub_denylist.example.txt"}

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ALLOWLIST = os.path.join(HERE, "scrub_allowlist.txt")
DEFAULT_DENYLIST = os.path.join(HERE, "scrub_denylist.local.txt")
DENYLIST_ENV = "SCRUB_DENYLIST"

# Built-in, organisation-neutral patterns: (name, pattern, severity, ignorecase).
# Anything that names a specific organisation, person, vendor, product, id or key
# belongs in the denylist file, never here.
PATTERNS = [
    ("slack-webhook-trigger", r"hooks\.slack\.com/triggers/", "FAIL", False),
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
    ("onedrive-path", r"OneDrive - [A-Za-z][A-Za-z0-9 ]*", "WARN", False),
    ("tracker-custom-field", r"cf\[\d+\]|customfield_\d+", "WARN", False),
]

# Special-cased WARN: two capitalised words on a line that also mentions
# "nicknames" or "people" (a likely real-name pair sitting in a mapping line).
NAME_PAIR_RE = re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b")
CONTEXT_RE = re.compile(r"nicknames|people", re.IGNORECASE)

SEVERITIES = {"FAIL", "WARN"}
CASE_FLAGS = {"ci": True, "cs": False}


def denylist_path():
    """The denylist file to load: $SCRUB_DENYLIST if set, else the default next to this script."""
    return os.environ.get(DENYLIST_ENV) or DEFAULT_DENYLIST


def load_denylist(path):
    """Parse a denylist file into (name, pattern, severity, ignorecase) tuples.

    One pattern per line: `<severity> <ci|cs> <name> <regex>`, whitespace separated,
    the regex being everything after the name. Blank lines and `#` comments are
    ignored. A malformed line is a hard error: a silently dropped pattern is exactly
    the failure this check exists to prevent.
    """
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 3)
            if len(parts) != 4:
                raise ValueError(f"{path}:{line_no}: expected '<FAIL|WARN> <ci|cs> <name> <regex>'")
            severity, case, name, pattern = parts
            if severity not in SEVERITIES:
                raise ValueError(f"{path}:{line_no}: severity must be FAIL or WARN, got {severity!r}")
            if case not in CASE_FLAGS:
                raise ValueError(f"{path}:{line_no}: case must be ci or cs, got {case!r}")
            try:
                re.compile(pattern)
            except re.error as e:
                raise ValueError(f"{path}:{line_no}: bad regex {pattern!r}: {e}") from None
            out.append((name, pattern, severity, CASE_FLAGS[case]))
    return out


def resolve_denylist():
    """Return (entries, status_line). Exits 2 if a denylist was named but is unusable."""
    path = denylist_path()
    explicit = bool(os.environ.get(DENYLIST_ENV))
    if not os.path.isfile(path):
        if explicit:
            print(f"error: {DENYLIST_ENV}={path} does not exist", file=sys.stderr)
            sys.exit(2)
        return [], "denylist: none loaded (built-in shape patterns only)"
    try:
        entries = load_denylist(path)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)
    return entries, f"denylist: {path} ({len(entries)} pattern{'s' if len(entries) != 1 else ''})"


def compiled_patterns(extra=()):
    out = []
    for name, pattern, severity, ignorecase in list(PATTERNS) + list(extra):
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
            if os.path.basename(p) in SKIP_BASENAMES:
                continue
            yield p
        elif os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                parent = os.path.basename(os.path.normpath(root))
                dirs[:] = [
                    d for d in dirs
                    if d not in SKIP_DIRS and (parent, d) not in SKIP_DIR_PAIRS
                ]
                for fname in files:
                    if fname in SKIP_BASENAMES:
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
    extra, status = resolve_denylist()
    patterns = compiled_patterns(extra)
    allowlist = load_allowlist(DEFAULT_ALLOWLIST)
    print(status)
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
    extra, status = resolve_denylist()
    patterns = compiled_patterns(extra)
    allowlist = load_allowlist(DEFAULT_ALLOWLIST)
    print(status)
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
    extra, status = resolve_denylist()
    print(status)
    print(f"{'name':<28} {'severity':<6} {'case':<6} {'from':<9} pattern")
    for name, pattern, severity, ignorecase in PATTERNS:
        print(f"{name:<28} {severity:<6} {'ci' if ignorecase else 'cs':<6} {'built-in':<9} {pattern}")
    for name, pattern, severity, ignorecase in extra:
        print(f"{name:<28} {severity:<6} {'ci' if ignorecase else 'cs':<6} {'denylist':<9} {pattern}")
    print(
        f"{'name-pair-on-people-line':<28} {'WARN':<6} {'special':<6} {'built-in':<9} "
        "two capitalised words on a nicknames/people line"
    )
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
