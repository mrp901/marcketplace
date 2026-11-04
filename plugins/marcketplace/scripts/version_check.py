#!/usr/bin/env python3
"""SessionStart hook - say so when this machine's marcketplace is behind main.

The plugin runs in three places that update separately: the cloud routines clone `main`,
claude.ai's copy follows it, and the synced copy Claude Code loads locally
(`~/.claude/plugins/synced/*/marcketplace~gN/`) updates only when claude.ai's does. That
local copy lagged two releases once and nobody noticed. This hook compares the version in
this copy's own `.claude-plugin/plugin.json` with `main`'s and, when they differ, prints
one line:

    marcketplace: this machine runs X, main is Y. Update the plugin on claude.ai, then restart Claude Code.

It is deliberately silent otherwise, and on every failure: no network, no `gh`, a private
repo with no login, an unparseable answer. A hook that can fail loudly at session start is
worse than a stale copy, so every path ends in exit 0 within a few seconds.

Where `main`'s version comes from: `gh api` first (it carries the user's login, so it works
on a private repo), else the raw.githubusercontent URL. The answer is cached for 12 hours in
`~/.claude/marcketplace/version-check.json`, beside the plugin's other pointer files, keyed
by repo. A failure stamp is written *before* the lookup and overwritten when it succeeds, so
a lookup that stalls (a hung DNS query) and is killed at the hook's timeout still backs the
next 1 hour off, and an offline laptop does not pay the timeout at every session start. The
comparison itself runs on every start, from the cached `main` version.

A copy that is *ahead* of main (a branch under test, `--plugin-dir`) is not drift and is
left alone.

Environment:
    MARCKETPLACE_VERSION_CHECK=0   turn the check off
    MARCKETPLACE_HEADLESS=1        skip (a scheduled runner's own session; no one to tell)
    MARCKETPLACE_VERSION_CACHE     override the cache file (tests)
    MARCKETPLACE_REPO              override owner/name (default mrp901/marcketplace)

Tests: python3 -m unittest plugins/marcketplace/scripts/test_version_check.py
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request

REPO = os.environ.get("MARCKETPLACE_REPO") or "mrp901/marcketplace"
MANIFEST_PATH = "plugins/marcketplace/.claude-plugin/plugin.json"
RAW_URL = "https://raw.githubusercontent.com/{repo}/main/" + MANIFEST_PATH

CACHE_OK_SECONDS = 12 * 3600
CACHE_FAIL_SECONDS = 1 * 3600
FETCH_TIMEOUT = 3  # seconds per attempt; the hook's own timeout is 10

DEFAULT_CACHE = os.path.join(
    os.path.expanduser("~"), ".claude", "marcketplace", "version-check.json"
)

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


def parse_version(text):
    """'1.12.0' -> (1, 12, 0). None when it is not a plain major.minor.patch version."""
    if not isinstance(text, str) or not VERSION_RE.match(text.strip()):
        return None
    core = re.split(r"[-+]", text.strip(), maxsplit=1)[0]
    return tuple(int(p) for p in core.split("."))


def version_of(manifest_text):
    """The `version` of a plugin.json body, or None."""
    try:
        v = json.loads(manifest_text).get("version")
    except (ValueError, AttributeError):
        return None
    return v.strip() if parse_version(v) else None


def local_version(plugin_root):
    try:
        with open(os.path.join(plugin_root, ".claude-plugin", "plugin.json"), "r", encoding="utf-8") as fh:
            return version_of(fh.read())
    except OSError:
        return None


def fetch_via_gh(repo=REPO, timeout=FETCH_TIMEOUT):
    gh = shutil.which("gh")
    if not gh:
        return None
    try:
        out = subprocess.run(
            [gh, "api", f"repos/{repo}/contents/{MANIFEST_PATH}?ref=main",
             "-H", "Accept: application/vnd.github.raw"],
            capture_output=True, text=True, timeout=timeout, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return version_of(out.stdout) if out.returncode == 0 else None


def fetch_via_raw(repo=REPO, timeout=FETCH_TIMEOUT):
    try:
        req = urllib.request.Request(RAW_URL.format(repo=repo), headers={"User-Agent": "marcketplace-version-check"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - fixed https URL
            return version_of(resp.read().decode("utf-8", "replace"))
    except Exception:  # offline, 404 on a private repo, TLS, anything: silent
        return None


def fetch_main_version(repo=REPO):
    return fetch_via_gh(repo) or fetch_via_raw(repo)


def read_all(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def read_cache(path, repo=REPO):
    entry = read_all(path).get(repo)
    try:
        return float(entry["checked_at"]), entry.get("main")
    except (KeyError, TypeError, ValueError, AttributeError):
        return None


def write_cache(path, now, main, repo=REPO):
    data = read_all(path)  # keep other repos' entries
    data[repo] = {"checked_at": now, "main": main}
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
    except OSError:
        pass  # no cache just means we look again next time


def main_version(cache_path, now, fetch, repo=REPO):
    """`main`'s version from the cache while it is fresh, else from `fetch()`; None if unknown.
    A failure stamp goes in first, so a fetch that never returns still backs the next start off."""
    cached = read_cache(cache_path, repo)
    if cached:
        checked_at, main = cached
        ttl = CACHE_OK_SECONDS if main else CACHE_FAIL_SECONDS
        if 0 <= now - checked_at < ttl:
            return main
    write_cache(cache_path, now, None, repo)
    main = fetch()
    if main:
        write_cache(cache_path, now, main, repo)
    return main


def drift_line(local, main):
    """The one line to print, or None. Silent when the versions match, either is unknown,
    or this copy is ahead of main."""
    lv, mv = parse_version(local), parse_version(main)
    if lv is None or mv is None or lv >= mv:
        return None
    return (f"marcketplace: this machine runs {local}, main is {main}. "
            "Update the plugin on claude.ai, then restart Claude Code.")


def run(plugin_root, cache_path, now=None, fetch=None, env=None, repo=REPO):
    """The whole check; returns the line or None, and never raises."""
    env = os.environ if env is None else env
    fetch = fetch or (lambda: fetch_main_version(repo))
    try:
        if env.get("MARCKETPLACE_VERSION_CHECK") == "0" or env.get("MARCKETPLACE_HEADLESS") == "1":
            return None
        local = local_version(plugin_root)
        if local is None:
            return None
        main = main_version(cache_path, time.time() if now is None else now, fetch, repo)
        return drift_line(local, main)
    except Exception:
        return None


def emit(line):
    json.dump(
        {
            "systemMessage": line,
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": (
                    f"{line} Mention this to the user once, early in the conversation, "
                    "in one sentence; do not act on it."
                ),
            },
        },
        sys.stdout,
    )
    sys.stdout.write("\n")


def main():
    plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_path = os.environ.get("MARCKETPLACE_VERSION_CACHE") or DEFAULT_CACHE
    line = run(plugin_root, cache_path)
    if line:
        emit(line)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
