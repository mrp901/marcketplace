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
    profile keys  dotted keys in the first cell of the key-table rows of
                  shared/profile-schema.md at base that no live row lists at head. A key moved
                  into a "Retired" row (whose first cell is not a key) counts as removed, and
                  mentioning a removal elsewhere (CHANGELOG, HISTORY) does not hide it.
    env vars      names read through env access (os.environ.get("X"), os.environ["X"],
                  os.getenv("X"), process.env.X, $env:X, env.get("X")) in
                  plugins/**/scripts/ or plugins/**/hooks/ files at base and no longer read in
                  that same file set at head. Constants and documentation do not count.
    files         basenames of files removed from those scripts/ and hooks/ directories.

A name matches as a whole token: the characters either side must not be [A-Za-z0-9_-], so
`vault-pulse` matches `/marcketplace:vault-pulse` and `vault-pulse profile=` but `pulse` alone
does not match, and `vault-pulse` does not match `vault-pulse-extra`.

Read-only: runs `git ls-tree` and `git show` and reads files; edits nothing. Binary and
unreadable files are skipped; `.git` directories are never entered. Stdlib only.

    python3 plugins/marcketplace/scripts/runtime_refs.py [--base origin/main] [--head HEAD]
        [--paths P ...] [--extra P ...] [--json] [--repo DIR]

--paths replaces the default (~/.claude/scripts, ~/.claude/settings.json, ~/.claude/skills);
--extra appends to whichever list is in force. A path may be a file or a directory, `~` expands.

A path that does not exist is reported on stderr. A missing default path is a warning; a
missing path given with --paths or --extra is an error (exit 2), and so is a run that scanned
no file at all, because "found nothing" and "looked at nothing" must not read the same.

Exit: 0 no hits, 1 at least one hit, 2 usage or git error or nothing scanned.

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
_NAME = r"([A-Z][A-Z0-9_]{3,})"
_Q = r"""['"]"""
ENV_READ_RES = [
    re.compile(r"(?:environ|env)\s*\.\s*get\s*\(\s*" + _Q + _NAME + _Q),
    re.compile(r"(?:environ|env)\s*\[\s*" + _Q + _NAME + _Q + r"\s*\]"),
    re.compile(r"getenv\s*\(\s*" + _Q + _NAME + _Q),
    re.compile(r"process\.env\." + _NAME + r"\b"),
    re.compile(r"\$env:" + _NAME + r"\b", re.I),
]
KEY_RE = re.compile(r"`([a-z][a-z0-9_-]*(?:\.[a-z0-9_*<>-]+)+)`")
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


def live_profile_keys(text):
    """Keys listed in the first cell of a table row. A "Retired" row has no key there."""
    keys = set()
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cell = line.strip().strip("|").split("|", 1)[0]
        keys.update(k for k in KEY_RE.findall(cell) if "<" not in k and "*" not in k)
    return keys


def removed_profile_keys(repo, base, head):
    old = show(repo, base, PROFILE_SCHEMA)
    if not old:
        return []
    return sorted(live_profile_keys(old) - live_profile_keys(show(repo, head, PROFILE_SCHEMA)))


def env_reads(text):
    return {m.group(1) for rx in ENV_READ_RES for m in rx.finditer(text)}


def script_files(repo, ref):
    return [p for p in ls_tree(repo, ref) if SCRIPT_DIR_RE.match(p)]


def removed_env_vars(repo, base, head):
    old = set()
    for path in script_files(repo, base):
        old |= env_reads(show(repo, base, path))
    if not old:
        return []
    new = set()
    for path in script_files(repo, head):
        new |= env_reads(show(repo, head, path))
    return sorted(old - new)


def removed_files(repo, base, head):
    at_head = script_files(repo, head)
    now = {os.path.basename(p) for p in at_head}
    gone = {os.path.basename(p) for p in script_files(repo, base) if p not in set(at_head)}
    return sorted(gone - now)


def collect(repo, base, head):
    return {
        "skills": [{"plugin": p, "skill": s} for p, s in removed_skills(repo, base, head)],
        "profile_keys": removed_profile_keys(repo, base, head),
        "env_vars": removed_env_vars(repo, base, head),
        "files": removed_files(repo, base, head),
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
    for name in collected["profile_keys"] + collected["env_vars"] + collected["files"]:
        out.append((name, token_re(name), name))
    return out


def iter_files(paths, missing=None):
    """Yield every file under `paths`; append each entry that does not exist to `missing`."""
    for raw in paths:
        p = os.path.expanduser(raw)
        if os.path.isfile(p):
            yield p
        elif os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d != ".git"]
                for f in files:
                    yield os.path.join(root, f)
        elif missing is not None:
            missing.append(raw)


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


def scan(paths, collected, missing=None):
    pats = needles(collected)
    hits, scanned = [], 0
    for path in iter_files(paths, missing):
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
                hits.append({"file": os.path.normpath(path), "line": n, "name": name})
    return hits, scanned


def summary(base, head, collected, scanned):
    return (f"runtime_refs: {base}..{head} removes {len(collected['skills'])} skill(s), "
            f"{len(collected['profile_keys'])} profile key(s), {len(collected['env_vars'])} env var(s), "
            f"{len(collected['files'])} file(s); scanned {scanned} file(s)")


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
    explicit = (args.paths or []) + args.extra
    paths = (args.paths if args.paths is not None else DEFAULT_PATHS) + args.extra
    try:
        collected = collect(args.repo, args.base, args.head)
    except GitError as exc:
        print(f"runtime_refs: git error: {exc}", file=sys.stderr)
        return 2
    missing = []
    hits, scanned = scan(paths, collected, missing)
    bad = [m for m in missing if m in explicit]
    for m in missing:
        kind = "error" if m in explicit else "warning"
        print(f"runtime_refs: {kind}: path not found: {os.path.normpath(os.path.expanduser(m))}",
              file=sys.stderr)
    if scanned == 0:
        print("runtime_refs: error: no file was scanned, so this run proves nothing", file=sys.stderr)
    line = summary(args.base, args.head, collected, scanned)
    if args.json:
        json.dump({"base": args.base, "head": args.head, "collected": collected,
                   "scanned": scanned, "hits": hits}, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(line)
        for h in hits:
            print(f"{h['file']}:{h['line']}: {h['name']} (removed in this diff)")
    if bad or scanned == 0:
        return 2
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
