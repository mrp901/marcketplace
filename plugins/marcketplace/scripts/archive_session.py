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

import glob
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


def older_copies(pending, session_stem):
    """Earlier pending copies of this session, and the newest `tail_after` they carry.

    A long-lived session ends (or is swept) many times, and every copy is a full
    transcript, so a newer copy holds everything an older one does. Without this the
    queue held one full copy per end: 38 files for 10 sessions on 26 Oct 2026.
    """
    stems, tail = [], None
    for p in glob.glob(os.path.join(pending, f"*-{session_stem}.jsonl")):
        stem = p[: -len(".jsonl")]
        stems.append(stem)
        try:
            with open(stem + ".meta.json", "r", encoding="utf-8") as fh:
                t = json.load(fh).get("tail_after")
            if t and (tail is None or t > tail):
                tail = t
        except (OSError, ValueError, AttributeError):
            pass
    return stems, tail


def remove_copies(stems, keep):
    """Delete superseded pending copies, never the one just written."""
    for stem in stems:
        if stem == keep:
            continue
        for ext in (".jsonl", ".meta.json"):
            try:
                os.remove(stem + ext)
            except OSError:
                pass


def user_turns(path):
    n = 0
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            if '"type":"user"' in line or '"type": "user"' in line:
                n += 1
    return n


def nothing_new(transcript, session_stem, dirs):
    """True when an existing copy already holds every typed user message in the transcript.

    Re-opening an old session and closing it fires SessionEnd again with a few bytes of
    bookkeeping appended; before 1.10.0 each one queued a fresh full copy (one 28 Sep session
    was archived six times by 26 Oct, never with a new message). Unsure means queue it.
    """
    try:
        copies = [p for d in dirs for p in glob.glob(os.path.join(d, f"*-{session_stem}.jsonl"))]
        if not copies:
            return False
        newest = max(copies, key=os.path.getmtime)
        if os.path.getmtime(transcript) <= os.path.getmtime(newest) + 1:  # copy2 keeps the mtime
            return True
        # Count user turns rather than compare timestamps, so a transcript-format change can only
        # ever cause an extra copy, never a missed one. Reopen bookkeeping adds no user turn.
        return user_turns(transcript) == user_turns(newest)
    except Exception:
        return False


def main():
    raw = sys.stdin.read()
    if os.environ.get("VAULT_PULSE_RUN") == "1" or os.environ.get("MARCKETPLACE_HEADLESS") == "1":
        # A scheduled unattended run (run_pulse.py, run_session_log.py) is not a working session;
        # archiving it would queue a non-session for write-up every run.
        return 0
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
    if nothing_new(transcript, session_id, (pending, os.path.join(base_dir(), "archive"))):
        return 0
    try:
        os.makedirs(pending, exist_ok=True)
    except OSError as e:
        print(f"session-log: cannot create {pending}: {e}", file=sys.stderr)
        return 0

    stamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    stem = os.path.join(pending, f"{stamp}-{session_id}")
    superseded, tail_after = older_copies(pending, session_id)

    try:
        shutil.copy2(transcript, stem + ".jsonl")
        meta = {
            "session_id": payload.get("session_id"),
            "cwd": cwd,
            "reason": reason,
            "ended_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "source_transcript": transcript,
        }
        if tail_after:
            meta["tail_after"] = tail_after
        with open(stem + ".meta.json", "w", encoding="utf-8") as fh:
            json.dump(meta, fh, indent=2)
    except OSError as e:
        print(f"session-log: archive failed: {e}", file=sys.stderr)
        return 0

    # Only once the new copy is safely written: no moment with zero copies queued.
    remove_copies(superseded, keep=stem)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:                      # never break the user's exit
        print(f"session-log: {e}", file=sys.stderr)
        sys.exit(0)
