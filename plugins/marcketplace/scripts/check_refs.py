#!/usr/bin/env python3
"""Check that every file cross-reference inside the plugin resolves.

A skill points at its own references and scripts, and at the shared contracts, using
backticked relative paths. Those paths are written by hand and are easy to get wrong by
one directory level, which nothing else catches: the file still reads fine, and the
model following it simply fails to find what it was sent to.

Usage:
    check_refs.py [plugin_root]        # default: the directory two levels up from here

Exits 1 if any reference fails to resolve.

Some references are prose about another skill's file rather than a link to follow
("the router's own references/categories.md"). Those are listed in PROSE_OK below,
keyed by the file that contains them, so a real breakage cannot hide among them.
"""
import re
import sys
import pathlib

PAT = re.compile(r"`((?:\.\./|references/|scripts/)[\w./-]+\.(?:md|py))`")

# file (relative to plugin root) -> references in it that are prose, not links
PROSE_OK = {
    "shared/onboarding.md": {"../../shared/onboarding.md"},
    "shared/handler-contract.md": {"references/categories.md"},
    "skills/session-log/HISTORY.md": {"references/vault-conventions.md"},
    "skills/skill-eval/HISTORY.md": {"references/registry-review.md"},
    "skills/proactive-router/evals/04-saved-minor-followup/graders/allowlist-principle.md": {
        "references/categories.md"
    },
}


def main(argv):
    root = pathlib.Path(argv[0]) if argv else pathlib.Path(__file__).resolve().parents[1]
    broken = []
    checked = 0
    for f in sorted(root.rglob("*.md")):
        rel = str(f.relative_to(root))
        allowed = PROSE_OK.get(rel, set())
        for ref in sorted(set(PAT.findall(f.read_text()))):
            if ref in allowed:
                continue
            checked += 1
            if not (f.parent / ref).resolve().exists():
                broken.append((rel, ref))
    for rel, ref in broken:
        print(f"BROKEN {rel}: {ref}")
    print(f"--- {checked} references checked, {len(broken)} broken ---")
    return 1 if broken else 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except BrokenPipeError:
        sys.exit(0)
