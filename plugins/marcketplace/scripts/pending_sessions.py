#!/usr/bin/env python3
"""SessionStart hook - tell Claude if session write-ups are waiting.

SessionEnd can archive but cannot summarize. SessionStart is the other half:
unlike SessionEnd it *does* support additionalContext, so it can put a note in
front of Claude at the top of the next session saying there is a backlog. That
turns "summarize at the end" into "offer to write up what's outstanding at the
beginning", which is the version that actually works.

Deliberately quiet: emits nothing when the queue is empty, so a normal session
starts with no added noise. Exits 0 unconditionally.

Resolves the archive directory the same way archive_session.py does: the
SESSION_LOG_DIR environment variable, then the pointer file at
~/.claude/marcketplace/session-log-dir.ref, then a local default.
"""

import json
import os
import sys
from datetime import datetime, timezone

MAX_LISTED = 5

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


def emit(context):
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context,
            }
        },
        sys.stdout,
    )
    sys.stdout.write("\n")


def describe_age(path):
    try:
        delta = datetime.now(timezone.utc) - datetime.fromtimestamp(
            os.path.getmtime(path), timezone.utc
        )
    except OSError:
        return "?"
    days = delta.days
    if days >= 1:
        return f"{days}d ago"
    hours = delta.seconds // 3600
    return f"{hours}h ago" if hours else "just now"


def main():
    pending = os.path.join(base_dir(), "pending")
    if not os.path.isdir(pending):
        return 0

    try:
        files = sorted(
            (f for f in os.listdir(pending) if f.endswith(".jsonl")),
            key=lambda f: os.path.getmtime(os.path.join(pending, f)),
        )
    except OSError:
        return 0

    if not files:
        return 0

    lines = [
        f"{len(files)} Claude session transcript(s) are archived and not yet written "
        f"up in the knowledge base, in `{pending}`:",
        "",
    ]
    for f in files[:MAX_LISTED]:
        lines.append(f"  - {f}  ({describe_age(os.path.join(pending, f))})")
    if len(files) > MAX_LISTED:
        lines.append(f"  - ...and {len(files) - MAX_LISTED} more")
    lines += [
        "",
        "If the user asks about past sessions, or asks to catch up the knowledge base, "
        "use the session-log skill to write these up (oldest first) and move each "
        "processed file from pending/ to archive/. Do not raise this unprompted unless "
        "the backlog is large or old - it is a standing queue, not an alert.",
    ]

    emit("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
