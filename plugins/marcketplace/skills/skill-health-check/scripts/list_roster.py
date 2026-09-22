#!/usr/bin/env python3
"""List the skill-health-check roster: every skill directory under the plugin's skills/,
excluding this skill's own directory.

Implements SKILL.md step 1's roster rule deterministically, so the roster is never a
hardcoded list drifting out of sync with what's actually installed.

Usage:
    list_roster.py <skills_dir> [--exclude NAME ...]

<skills_dir> is the path to plugins/marcketplace/skills/ (or an equivalent skills root for
a differently-laid-out install). Prints one skill slug per line, sorted, to stdout.
--exclude defaults to this skill's own directory name (skill-health-check); pass it again to
exclude additional slugs (e.g. a skill with genuinely no evidence this skill can ever gather,
per the orchestrator's own decision - never hardcode an exclusion here beyond the default).

A directory is counted as a skill only if it contains a SKILL.md file directly inside it -
this filters out stray non-skill directories without needing a separate manifest.
"""

import argparse
import os
import sys

DEFAULT_EXCLUDE = {"skill-health-check"}


def find_roster(skills_dir, exclude):
    roster = []
    if not os.path.isdir(skills_dir):
        return roster
    for name in os.listdir(skills_dir):
        path = os.path.join(skills_dir, name)
        if not os.path.isdir(path):
            continue
        if name in exclude:
            continue
        if not os.path.isfile(os.path.join(path, "SKILL.md")):
            continue
        roster.append(name)
    return sorted(roster)


def main(argv):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("skills_dir")
    p.add_argument("--exclude", action="append", default=[])
    args = p.parse_args(argv)

    exclude = set(DEFAULT_EXCLUDE) | set(args.exclude)
    for slug in find_roster(args.skills_dir, exclude):
        print(slug)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
