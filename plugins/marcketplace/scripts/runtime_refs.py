#!/usr/bin/env python3
"""Pre-merge check - does anything outside the repo still use a name this change removes?

The repo checks (validate, plugin test, scrub, line budget, check_refs, unit tests) only look
inside the repo. A local scheduled task, a script under `~/.claude/scripts`, or an env var in
`~/.claude/settings.json` lives outside it and keeps calling what a release deleted. This script
mechanises the "outside the repo" item of RELEASING.md: it works out which names the diff
between `--base` and `--head` removes, then greps the local runtime paths for them.

Names collected (the diff, not the working tree):
    skills        directories under plugins/*/skills/ present at base and absent at head
                  (a rename shows up as a removal). Both `<skill>` and `/<plugin>:<skill>`.
    profile keys  dotted keys in backticks in the first cell of table rows removed from
                  shared/profile-schema.md that appear nowhere else under plugins/ or profiles/
                  at head. Best effort.
    env vars      UPPER_SNAKE names (4+ chars) in plugins/**/scripts/ or plugins/**/hooks/ files
                  at base that appear in no file at head.

A name matches as a whole token: the characters either side must not be [A-Za-z0-9_-], so
`vault-pulse` matches `/marcketplace:vault-pulse` and `vault-pulse profile=` but `pulse` alone
does not match, and `vault-pulse` does not match `vault-pulse-extra`.

Read-only: runs `git ls-tree`, `git show` and `git grep` and reads files; edits nothing. Binary
and unreadable files are skipped; `.git` directories are never entered. Stdlib only.

    python3 plugins/marcketplace/scripts/runtime_refs.py [--base origin/main] [--head HEAD]
        [--paths P ...] [--extra P ...] [--json] [--repo DIR]

--paths replaces the default (~/.claude/scripts, ~/.claude/settings.json, ~/.claude/skills);
--extra appends to whichever list is in force. A path may be a file or a directory, `~` expands.

Exit: 0 no hits, 1 at least one hit, 2 usage or git error.

Tests: python3 -m unittest plugins/marcketplace/scripts/test_runtime_refs.py
"""

import argparse
import json
import os
import re
import subprocess
import sys

DEFAULT_PATHS = ["~/.claude/scripts", "~/.claude/settings.json", "~/.claude/skills"]
SKILL_RE = re.compile(r"^plugins/([^/]+)/skills/([^/]+)/")
SCRIPT_DIR_RE = re.compile(r"^plugins/[^/]+/(?:.+/)?(?:scripts|hooks)/")
ENV_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b")  # UPPER_SNAKE, needs an underscore
ENV_MIN = 4
KEY_RE = re.compile(r"`([a-z][a-z0-9_]*(?:\.[a-z0-9_*<>]+)+)`")
PROFILE_SCHEMA = "plugins/marcketplace/shared/profile-schema.md"
MAX_BYTES = 5 * 1024 * 1024


class GitError(Exception):
    pass


def git(repo, *args, check=True):
    try:
        out = subprocess.run(["git", "-C", repo, *args], capture_output=True, check=False)
    except OSError as exc:
        raise GitError(f"cannot run git: {exc}")
    if check and out.returncode != 0:
        raise GitError(out.stderr.decode("utf-8", "replace").strip() or f"git {' '.join(args)} failed")
    return out


def ls_tree(repo, ref):
    out = git(repo, "ls-tree", "-r", "--name-only", ref)
    return out.stdout.decode("utf-8", "replace").splitlines()


def show(repo, ref, path):
    out = git(repo, "show", f"{ref}:{path}", check=False)
    if out.returncode != 0 or b"\0" in out.stdout[:8192]:
        return ""
    return out.stdout.decode("utf-8", "replace")


def skills_in(files):
    return {m.groups() for m in map(SKILL_RE.match, files) if m}


def removed_skills(repo, base, head):
    return sorted(skills_in(ls_tree(repo, base)) - skills_in(ls_tree(repo, head)))


def head_has(repo, head, text):
    """True when `text` appears literally anywhere under plugins/ or profiles/ at head."""
    out = git(repo, "grep", "-I", "-q", "-F", "-e", text, head, "--", "plugins", "profiles", check=False)
    return out.returncode == 0


def removed_profile_keys(repo, base, head):
    old, new = show(repo, base, PROFILE_SCHEMA), show(repo, head, PROFILE_SCHEMA)
    if not old:
        return []
    new_lines = set(new.splitlines())
    keys = []
    for line in old.splitlines():
        if line in new_lines or not line.lstrip().startswith("|"):
            continue
        cell = line.strip().strip("|").split("|", 1)[0]
        for key in KEY_RE.findall(cell):
            if "<" in key or "*" in key or key in keys:
                continue
            if not head_has(repo, head, key):
                keys.append(key)
    return sorted(keys)


def env_tokens(text):
    return {t for t in ENV_RE.findall(text) if len(t) >= ENV_MIN}


def removed_env_vars(repo, base, head):
    old = set()
    for path in ls_tree(repo, base):
        if SCRIPT_DIR_RE.match(path):
            old |= env_tokens(show(repo, base, path))
    if not old:
        return []
    out = git(repo, "grep", "-I", "-h", "-o", "-w", "-E", r"[A-Z][A-Z0-9_]{3,}", head, check=False)
    present = set(out.stdout.decode("utf-8", "replace").split())
    return sorted(old - present)


def collect(repo, base, head):
    return {
        "skills": [{"plugin": p, "skill": s} for p, s in removed_skills(repo, base, head)],
        "profile_keys": removed_profile_keys(repo, base, head),
        "env_vars": removed_env_vars(repo, base, head),
    }


def token_re(name):
    return re.compile(r"(?<![A-Za-z0-9_-])" + re.escape(name) + r"(?![A-Za-z0-9_-])")


def needles(collected):
    """[(display name, regex, group)]; a skill's qualified form is listed before its bare name."""
    out = []
    for item in collected["skills"]:
        q, b = f"/{item['plugin']}:{item['skill']}", item["skill"]
        out.append((q, token_re(q), b))
        out.append((b, token_re(b), b))
    for name in collected["profile_keys"] + collected["env_vars"]:
        out.append((name, token_re(name), name))
    return out


def iter_files(paths):
    for raw in paths:
        p = os.path.expanduser(raw)
        if os.path.isfile(p):
            yield p
        elif os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d != ".git"]
                for f in files:
                    yield os.path.join(root, f)


def read_text(path):
    try:
        if os.path.getsize(path) > MAX_BYTES:
            return None
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError:
        return None
    if b"\0" in data[:8192]:
        return None
    return data.decode("utf-8", "replace")


def scan(paths, collected):
    pats = needles(collected)
    hits, scanned = [], 0
    for path in iter_files(paths):
        text = read_text(path)
        if text is None:
            continue
        scanned += 1
        for n, line in enumerate(text.splitlines(), 1):
            matched = set()
            for name, rx, group in pats:
                if group in matched or not rx.search(line):
                    continue
                matched.add(group)  # qualified form is listed first, so it wins over the bare one
                hits.append({"file": path, "line": n, "name": name})
    return hits, scanned


def summary(base, head, collected, scanned):
    return (f"runtime_refs: {base}..{head} removes {len(collected['skills'])} skill(s), "
            f"{len(collected['profile_keys'])} profile key(s), {len(collected['env_vars'])} env var(s); "
            f"scanned {scanned} file(s)")


def parse_args(argv):
    ap = argparse.ArgumentParser(description="Find local runtime references to names this diff removes.")
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--paths", nargs="+", default=None, help=f"replace the default {DEFAULT_PATHS}")
    ap.add_argument("--extra", nargs="+", default=[], help="append to the paths searched")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--repo", default=".", help="git repository to diff (default: current directory)")
    return ap.parse_args(argv)


def main(argv=None):
    try:
        args = parse_args(sys.argv[1:] if argv is None else argv)
    except SystemExit as exc:
        return 2 if exc.code else 0
    paths = (args.paths if args.paths is not None else DEFAULT_PATHS) + args.extra
    try:
        collected = collect(args.repo, args.base, args.head)
    except GitError as exc:
        print(f"runtime_refs: git error: {exc}", file=sys.stderr)
        return 2
    hits, scanned = scan(paths, collected)
    line = summary(args.base, args.head, collected, scanned)
    if args.json:
        json.dump({"base": args.base, "head": args.head, "collected": collected,
                   "scanned": scanned, "hits": hits}, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(line)
        for h in hits:
            print(f"{h['file']}:{h['line']}: {h['name']} (removed in this diff)")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
