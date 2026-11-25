#!/usr/bin/env python3
"""Fail a change to the plugin that does not bump its version.

    python3 plugins/marcketplace/scripts/version_bump_check.py [--base origin/main] [--head HEAD]

The SessionStart version check (`version_check.py`) and the claude.ai sync both compare only
the `version` in `plugin.json`. A change merged without a bump is invisible to both: on
26 Nov 2026 a router fix (#41) merged at 1.14.0, the drift check stayed quiet and the synced
copy never picked it up. So any diff that touches the plugin must:

1. raise `plugins/marcketplace/.claude-plugin/plugin.json`'s version above the base's, and
2. have a `## [<new version>]` heading in `CHANGELOG.md`.

Files that cannot change what the plugin does are exempt (`EXEMPT` below): its unit and hook
tests, evals, and per-skill `HISTORY.md`. A diff that touches only those, or nothing under
`plugins/marcketplace/`, passes with no bump.

Exit 0 pass, 1 fail, 2 usage or git error. Stdlib only. CI runs it on pull requests against
the PR's base branch; run it locally before opening one.
"""

import argparse
import fnmatch
import json
import re
import subprocess
import sys

PLUGIN_DIR = "plugins/marcketplace/"
MANIFEST = PLUGIN_DIR + ".claude-plugin/plugin.json"
CHANGELOG = "CHANGELOG.md"
EXEMPT = (
    PLUGIN_DIR + "**/test_*.py",
    PLUGIN_DIR + "**/*.test.ts",
    PLUGIN_DIR + "hooks/test-fixtures.ts",
    PLUGIN_DIR + "evals/*",
    PLUGIN_DIR + "skills/*/evals/*",
    PLUGIN_DIR + "**/HISTORY.md",
)
VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def parse_version(text):
    m = VERSION_RE.match((text or "").strip())
    return tuple(int(x) for x in m.groups()) if m else None


def version_of(manifest_text):
    try:
        return json.loads(manifest_text).get("version")
    except (ValueError, AttributeError):
        return None


def is_exempt(path):
    return any(fnmatch.fnmatch(path, pat) for pat in EXEMPT)


def behaviour_files(changed):
    """Changed paths under the plugin that can change what it does."""
    return [p for p in changed if p.startswith(PLUGIN_DIR) and not is_exempt(p)]


def changelog_has(changelog_text, version):
    return re.search(r"^## \[" + re.escape(version) + r"\]", changelog_text or "", re.M) is not None


def evaluate(changed, base_manifest, head_manifest, head_changelog):
    """Return (ok, message). Pure: the git reads happen in main()."""
    touched = behaviour_files(changed)
    if not touched:
        return True, "version_bump_check: no plugin behaviour files changed; no bump needed"
    base_v, head_v = version_of(base_manifest), version_of(head_manifest)
    shown = ", ".join(touched[:5]) + (f" (+{len(touched) - 5} more)" if len(touched) > 5 else "")
    if parse_version(head_v) is None:
        return False, f"version_bump_check: FAIL, {MANIFEST} has no plain x.y.z version ({head_v!r})"
    if parse_version(base_v) is not None and parse_version(head_v) <= parse_version(base_v):
        return False, (f"version_bump_check: FAIL, plugin files changed ({shown}) but the version "
                       f"is still {head_v} (base {base_v}). Bump {MANIFEST} and add a "
                       f"'## [x.y.z]' section to {CHANGELOG}, or the drift check and the "
                       f"claude.ai sync will never see this change.")
    if not changelog_has(head_changelog, head_v):
        return False, f"version_bump_check: FAIL, {CHANGELOG} has no '## [{head_v}]' heading"
    return True, f"version_bump_check: {base_v} -> {head_v}, {len(touched)} plugin file(s) changed"


def git(*args):
    out = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8")
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or f"git {' '.join(args)} failed")
    return out.stdout


def show(ref, path):
    try:
        return git("show", f"{ref}:{path}")
    except RuntimeError:
        return ""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--head", default="HEAD")
    a = ap.parse_args(argv)
    try:
        changed = [p for p in git("diff", "--name-only", f"{a.base}...{a.head}").splitlines() if p]
    except RuntimeError as e:
        print(f"version_bump_check: {e}", file=sys.stderr)
        return 2
    ok, msg = evaluate(changed, show(a.base, MANIFEST), show(a.head, MANIFEST), show(a.head, CHANGELOG))
    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
