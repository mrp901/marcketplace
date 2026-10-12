#!/usr/bin/env python3
"""SessionStart hook - tell Claude if session write-ups are waiting.

SessionEnd can archive but cannot summarize. SessionStart is the other half:
unlike SessionEnd it *does* support additionalContext, so it can put a note in
front of Claude at the top of the next session saying there is a backlog. That
turns "summarize at the end" into "offer to write up what's outstanding at the
beginning", which is the version that actually works.

Before counting, it sweeps recent Claude Code transcripts for substantive
sessions the SessionEnd hook never archived (a killed window, a broken hook)
and queues them in pending/ the same way the hook would. See sweep() below and
skills/session-log/references/pending-sessions.md, "The transcript sweep".

Deliberately quiet: emits nothing when the queue is empty, so a normal session
starts with no added noise. Exits 0 unconditionally.

Resolves the archive directory the same way archive_session.py does: the
SESSION_LOG_DIR environment variable, then the pointer file at
~/.claude/marcketplace/session-log-dir.ref, then a local default.

Usage outside the hook:
    pending_sessions.py --dry-run   # print what the sweep would queue; writes nothing
"""

import glob
import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone

MAX_LISTED = 5

POINTER_FILE = os.path.join(
    os.path.expanduser("~"), ".claude", "marcketplace", "session-log-dir.ref"
)
DEFAULT_DIR = os.path.join(os.path.expanduser("~"), ".claude", "session-log")

# ---- sweep tuning: conservative and cheap ----
SWEEP_LOOKBACK_DAYS = 7     # first run (no cursor) looks back this far
SWEEP_IDLE_MINUTES = 120    # a transcript touched more recently may still be open
SWEEP_MAX_CHECKED = 20      # transcripts read per run; the cursor carries the rest over
SWEEP_MIN_BYTES = 64 * 1024 # smaller is an empty or aborted launch: skipped unread
SWEEP_MAX_QUEUED = 8        # copies made per run
MIN_TYPED = 6               # substantive: at least this many typed user messages
MIN_TYPED_NO_WRITES = 15    # ...or this many even if nothing was written
CURSOR_FILE = "sweep-cursor.json"

# A tool call that changes something, as opposed to reading it. Local file
# tools by name; connector tools by a write verb in their name.
MUTATING = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
WRITE_VERBS = ("create", "update", "edit", "send", "commit", "publish", "add", "transition")
NOT_TYPED = ("<", "Caveat:", "[Request interrupted")


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


def projects_dir():
    root = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(
        os.path.expanduser("~"), ".claude"
    )
    return os.path.join(root, "projects")


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


# ---------------------------------------------------------------- sweep


def _epoch(ts):
    """ISO 8601 timestamp from a transcript line -> epoch seconds, or None."""
    if not isinstance(ts, str):
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _is_write(name):
    if name in MUTATING:
        return True
    low = name.lower()
    return low.startswith("mcp__") and any(v in low.rsplit("__", 1)[-1] for v in WRITE_VERBS)


def _covered_until(session_id, dirs):
    """Newest point this session is already queued or archived through (epoch)."""
    best = 0.0
    stem = session_id[:12]
    for d in dirs:
        for p in glob.glob(os.path.join(d, f"*-{stem}.jsonl")):
            try:
                best = max(best, os.path.getmtime(p))  # copy2 keeps the source mtime
            except OSError:
                pass
    return best


def assess(path, after):
    """Count typed user messages and writes made after `after` (epoch).

    A session-log Skill call inside the transcript moves `after` forward: what
    came before it was written up live. Only lines that can matter are parsed.
    """
    typed = writes = 0
    first_text = ""
    cwd = ""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if '"user"' not in line and '"tool_use"' not in line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict) or obj.get("isSidechain"):
                continue
            cwd = cwd or obj.get("cwd") or ""
            ts = _epoch(obj.get("timestamp"))
            msg = obj.get("message") if isinstance(obj.get("message"), dict) else {}
            content = msg.get("content")
            if obj.get("type") == "assistant" and isinstance(content, list):
                for b in content:
                    if not (isinstance(b, dict) and b.get("type") == "tool_use"):
                        continue
                    name = str(b.get("name") or "")
                    inp = b.get("input") if isinstance(b.get("input"), dict) else {}
                    if name == "Skill" and str(inp.get("skill", "")).endswith("session-log"):
                        if ts:
                            after = max(after, ts)
                            typed = writes = 0
                            first_text = ""
                        continue
                    if (ts or 0) > after and _is_write(name):
                        writes += 1
                continue
            if obj.get("type") != "user" or obj.get("isMeta") or (ts or 0) <= after:
                continue
            if isinstance(content, list):
                if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
                    continue
                text = " ".join(
                    str(b.get("text", "")) for b in content
                    if isinstance(b, dict) and b.get("type") == "text"
                )
            else:
                text = content if isinstance(content, str) else ""
            text = text.strip()
            if not text or text.startswith(NOT_TYPED):
                continue
            typed += 1
            first_text = first_text or " ".join(text.split())[:70]
    substantive = (typed >= MIN_TYPED and writes >= 1) or typed >= MIN_TYPED_NO_WRITES
    return substantive, typed, writes, first_text, cwd, after


def sweep(base, dry_run=False, current_session=""):
    """Queue substantive, unarchived recent transcripts into pending/.

    Returns (queued, report_lines). main() wraps the call, so a sweep fault can
    never cost the backlog nudge that follows it.
    """
    pending = os.path.join(base, "pending")
    archive = os.path.join(base, "archive")
    cursor_path = os.path.join(base, CURSOR_FILE)
    now = time.time()
    try:
        with open(cursor_path, "r", encoding="utf-8") as fh:
            since = float(json.load(fh).get("swept_through", 0))
    except (OSError, ValueError, AttributeError):
        since = 0.0
    since = since or now - SWEEP_LOOKBACK_DAYS * 86400
    idle_edge = now - SWEEP_IDLE_MINUTES * 60

    candidates = []
    for p in glob.glob(os.path.join(projects_dir(), "*", "*.jsonl")):
        try:
            m = os.path.getmtime(p)
        except OSError:
            continue
        sid = os.path.basename(p)[: -len(".jsonl")]
        if since < m <= idle_edge and sid != current_session:
            try:
                small = os.path.getsize(p) < SWEEP_MIN_BYTES
            except OSError:
                continue
            candidates.append((m, p, sid, small))
    candidates.sort()

    queued, report = 0, []
    swept_through = since
    checked = 0
    for m, p, sid, small in candidates:
        if not dry_run and (queued >= SWEEP_MAX_QUEUED or checked >= SWEEP_MAX_CHECKED):
            break
        covered = _covered_until(sid, (pending, archive))
        if small or covered >= m - 1:
            swept_through = m
            continue
        checked += 1
        try:
            ok, typed, writes, first, cwd, tail_after = assess(p, covered)
        except OSError:
            continue
        stamp = datetime.fromtimestamp(m).strftime("%Y-%m-%d-%H%M%S")
        where = os.path.basename(os.path.dirname(p))
        verdict = "QUEUE" if ok else "skip "
        report.append(
            f"{verdict} {stamp} {sid[:8]} typed={typed} writes={writes}"
            f"{' tail' if tail_after else ''}  [{where[-32:]}]  {first}"
        )
        if ok and not dry_run:
            stem = os.path.join(pending, f"{stamp}-{sid[:12]}")
            os.makedirs(pending, exist_ok=True)
            shutil.copy2(p, stem + ".jsonl")
            meta = {
                "session_id": sid,
                "cwd": cwd,
                "reason": "swept",
                "ended_at": datetime.fromtimestamp(m).astimezone().isoformat(timespec="seconds"),
                "source_transcript": p,
            }
            if tail_after:
                meta["tail_after"] = datetime.fromtimestamp(tail_after).astimezone().isoformat(
                    timespec="seconds"
                )
            with open(stem + ".meta.json", "w", encoding="utf-8") as fh:
                json.dump(meta, fh, indent=2)
        queued += 1 if ok else 0
        swept_through = m

    if not dry_run and swept_through > since:
        try:
            os.makedirs(base, exist_ok=True)
            with open(cursor_path, "w", encoding="utf-8") as fh:
                json.dump({"swept_through": swept_through}, fh)
        except OSError:
            pass
    return queued, report


# ---------------------------------------------------------------- main


def read_payload():
    try:
        if sys.stdin is None or sys.stdin.isatty():
            return {}
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def main():
    base = base_dir()

    if "--dry-run" in sys.argv[1:]:
        queued, report = sweep(base, dry_run=True)
        print(f"sweep (dry run, nothing written) over {projects_dir()}")
        print("\n".join(report) or "no candidate transcripts in the window")
        print(f"would queue {queued} (a live run caps at {SWEEP_MAX_QUEUED} per session start)")
        return 0

    swept = 0
    if os.environ.get("SESSION_LOG_SWEEP", "1") != "0":
        try:
            swept, _ = sweep(base, current_session=str(read_payload().get("session_id") or ""))
        except Exception as e:                  # the nudge below must still run
            print(f"session-log sweep: {e}", file=sys.stderr)

    pending = os.path.join(base, "pending")
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
    if swept:
        lines += [
            "",
            f"{swept} of these were just queued by the transcript sweep: substantive "
            "sessions the SessionEnd hook never archived.",
        ]
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
