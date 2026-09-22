#!/usr/bin/env python3
"""SessionEnd hook - archive the transcript for later write-up.

A SessionEnd hook gets roughly a second and a half and has no way to invoke a
model, so it cannot summarize anything. What it *can* do is make sure the raw
material still exists and is easy to find. That is all this does: copy the
transcript somewhere durable and drop a small metadata sidecar next to it.

The write-up happens later, by the session-log skill, either when the user asks
or when the SessionStart hook notices a backlog.

Reads the hook payload as JSON on stdin. Always exits 0 - a journaling hook that
breaks the user's session has failed at its job, so every error is swallowed and
reported to stderr where Claude Code will show it without blocking.

Install: see plugins/marcketplace/skills/session-log/references/hooks-setup.md

Resolves the archive directory in this order - it has no MCP or kb-discovery
access of its own, so it cannot resolve a profile's kb.local_root directly:
  1. SESSION_LOG_DIR environment variable, if set.
  2. The pointer file at ~/.claude/marcketplace/session-log-dir.ref (one line,
     the resolved local path), written by the session-log skill the first
     time it resolves the knowledge base's local root.
  3. ~/.claude/session-log as a last-resort local default.
"""

import json
import os
import shutil
import sys
from datetime import datetime

MIN_LINES = 5           # below this a session is noise (a /clear, an accidental launch)

POINTER_FILE = os.path.join(
    os.path.expanduser("~"), ".claude", "marcketplace", "session-log-dir.ref"
)
DEFAULT_DIR = os.path.join(os.path.expanduser("~"), ".claude", "session-log")


def base_dir():
    env = os.environ.get("SESSION_LOG_DIR")
    if env:
        return env
    try:
        with open(POINTER_FILE, "r", encoding="utf-8") as fh:
            pointer = fh.read().strip()
        if pointer:
            return pointer
    except OSError:
        pass
    return DEFAULT_DIR


def count_lines(path, cap=200):
    """Cheap liveness check - stop counting once we know it is big enough."""
    n = 0
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            for _ in fh:
                n += 1
                if n >= cap:
                    break
    except OSError:
        return 0
    return n


def main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        print("session-log: could not parse hook payload", file=sys.stderr)
        return 0

    transcript = payload.get("transcript_path")
    if not transcript or not os.path.isfile(transcript):
        # Normal for some end reasons; not worth shouting about.
        return 0

    if count_lines(transcript) < MIN_LINES:
        return 0

    session_id = str(payload.get("session_id") or "unknown")[:12]
    reason = payload.get("session_end_reason") or payload.get("reason") or "other"
    cwd = payload.get("cwd") or ""

    pending = os.path.join(base_dir(), "pending")
    try:
        os.makedirs(pending, exist_ok=True)
    except OSError as e:
        print(f"session-log: cannot create {pending}: {e}", file=sys.stderr)
        return 0

    stamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    stem = os.path.join(pending, f"{stamp}-{session_id}")

    try:
        shutil.copy2(transcript, stem + ".jsonl")
        with open(stem + ".meta.json", "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "session_id": payload.get("session_id"),
                    "cwd": cwd,
                    "reason": reason,
                    "ended_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                    "source_transcript": transcript,
                },
                fh,
                indent=2,
            )
    except OSError as e:
        print(f"session-log: archive failed: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:                      # never break the user's exit
        print(f"session-log: {e}", file=sys.stderr)
        sys.exit(0)
