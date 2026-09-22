#!/usr/bin/env python3
"""Condense a Claude Code session transcript into a readable digest.

Claude Code's transcript JSONL is an internal format that changes between
versions, so everything here is deliberately tolerant: unknown line shapes are
counted and skipped rather than raised. A digest that is missing a few lines is
useful; a traceback is not.

Usage:
    read_transcript.py <transcript.jsonl>     # digest one transcript
    read_transcript.py --list [pending_dir]   # what is waiting to be processed
    read_transcript.py <file> --full          # do not truncate message text

--list resolves the pending directory the same way archive_session.py resolves
its base directory - SESSION_LOG_PENDING (an explicit override), then
SESSION_LOG_DIR + "/pending", then the pointer file at
~/.claude/marcketplace/session-log-dir.ref, then a local default - unless a
directory argument is given explicitly, which always wins.
"""

import json
import os
import sys
from collections import Counter

TRUNCATE = 700          # chars of message text kept per turn unless --full
FILE_KEYS = ("file_path", "path", "notebook_path", "filePath")

POINTER_FILE = os.path.join(
    os.path.expanduser("~"), ".claude", "marcketplace", "session-log-dir.ref"
)
DEFAULT_DIR = os.path.join(os.path.expanduser("~"), ".claude", "session-log")

# Tools that change a file, as opposed to merely looking at one. The digest has to
# keep these separable: "referenced" and "changed" are different claims, and a
# session note that reports a file as changed when it was only read is wrong in a
# way nobody catches later.
MUTATING = {
    "Edit", "Write", "NotebookEdit", "MultiEdit",
    "device_commit_files", "mcp__remote-devices__device_commit_files",
}


def default_pending_dir():
    env = os.environ.get("SESSION_LOG_PENDING")
    if env:
        return env
    base = os.environ.get("SESSION_LOG_DIR")
    if base:
        return os.path.join(base, "pending")
    try:
        with open(POINTER_FILE, "r", encoding="utf-8") as fh:
            pointer = fh.read().strip()
        if pointer:
            return os.path.join(pointer, "pending")
    except OSError:
        pass
    return os.path.join(DEFAULT_DIR, "pending")


def _iter_lines(path):
    """Yield parsed JSON objects, counting anything unparseable."""
    bad = 0
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                bad += 1
                continue
            if isinstance(obj, dict):
                yield obj
            else:
                bad += 1
    if bad:
        print(f"  [note] skipped {bad} unparseable line(s)\n", file=sys.stderr)


def _blocks(content):
    """Normalise a message's content into a list of blocks."""
    if content is None:
        return []
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if isinstance(content, list):
        return [b for b in content if isinstance(b, dict)]
    return []


def _text_of(blocks):
    out = []
    for b in blocks:
        if b.get("type") == "text" and b.get("text"):
            out.append(str(b["text"]))
        elif b.get("type") == "thinking":
            continue
    return "\n".join(out).strip()


def _files_from(inp):
    """Pull plausible file paths out of a tool_use input."""
    found = []
    if not isinstance(inp, dict):
        return found
    for k in FILE_KEYS:
        v = inp.get(k)
        if isinstance(v, str) and v:
            found.append(v)
    # device_commit_files / device_stage_files style payloads
    for k in ("files", "paths"):
        v = inp.get(k)
        if isinstance(v, list):
            for item in v:
                if isinstance(item, str):
                    found.append(item)
                elif isinstance(item, dict):
                    for kk in ("devicePath", "path", "file_path"):
                        if isinstance(item.get(kk), str):
                            found.append(item[kk])
    return found


def digest(path, full=False):
    limit = None if full else TRUNCATE
    turns = []
    tools = Counter()
    touched = {}          # path -> set of tool names, insertion-ordered
    first_ts = last_ts = None
    session_id = None

    for obj in _iter_lines(path):
        ts = obj.get("timestamp")
        if isinstance(ts, str):
            first_ts = first_ts or ts
            last_ts = ts
        session_id = session_id or obj.get("sessionId") or obj.get("session_id")

        kind = obj.get("type")
        msg = obj.get("message") if isinstance(obj.get("message"), dict) else None

        if kind == "summary" and obj.get("summary"):
            turns.append(("summary", str(obj["summary"])))
            continue

        if not msg:
            continue

        role = msg.get("role") or kind
        blocks = _blocks(msg.get("content"))

        for b in blocks:
            if b.get("type") == "tool_use":
                name = b.get("name") or "?"
                tools[name] += 1
                for f in _files_from(b.get("input")):
                    touched.setdefault(f, set()).add(name)

        text = _text_of(blocks)
        if text:
            if limit and len(text) > limit:
                text = text[:limit].rstrip() + f"  ...[+{len(text) - limit} chars]"
            turns.append((role, text))

    # ---- report ----
    print(f"# Transcript digest - {os.path.basename(path)}")
    if session_id:
        print(f"session: {session_id}")
    if first_ts:
        print(f"span:    {first_ts}  ->  {last_ts}")
    print(f"turns:   {len(turns)}")

    if tools:
        print("\n## Tool calls")
        for name, n in tools.most_common():
            print(f"  {n:>4}x  {name}")

    if touched:
        changed = {f: v for f, v in touched.items() if v & MUTATING}
        read_only = {f: v for f, v in touched.items() if not (v & MUTATING)}

        if changed:
            print(f"\n## Files CHANGED ({len(changed)})")
            for f, via in changed.items():
                print(f"  {f}   [{', '.join(sorted(via))}]")
        if read_only:
            print(f"\n## Files read only, not changed ({len(read_only)})")
            for f, via in read_only.items():
                print(f"  {f}   [{', '.join(sorted(via))}]")
        print("\n  Only the CHANGED list belongs in a session note's 'Changes to the")
        print("  knowledge base' table. Reading a file is not a change to it.")

    print("\n## Conversation")
    for role, text in turns:
        print(f"\n--- {role} ---")
        print(text)


def list_pending(d):
    if not os.path.isdir(d):
        print(f"No pending directory at: {d}")
        print("Nothing to process (or the SessionEnd hook is not installed yet).")
        return
    entries = sorted(
        (e for e in os.listdir(d) if e.endswith(".jsonl")),
        key=lambda e: os.path.getmtime(os.path.join(d, e)),
    )
    if not entries:
        print(f"{d} is empty - no sessions waiting.")
        return
    print(f"{len(entries)} session(s) waiting in {d}, oldest first:\n")
    for e in entries:
        p = os.path.join(d, e)
        size = os.path.getsize(p)
        meta = p[: -len(".jsonl")] + ".meta.json"
        extra = ""
        if os.path.exists(meta):
            try:
                with open(meta, encoding="utf-8") as fh:
                    m = json.load(fh)
                extra = f"  cwd={m.get('cwd', '?')}  reason={m.get('reason', '?')}"
            except Exception:
                pass
        print(f"  {e}  ({size:,} bytes){extra}")


def main():
    args = [a for a in sys.argv[1:]]
    full = "--full" in args
    args = [a for a in args if a != "--full"]

    if not args:
        print(__doc__)
        return 1

    if args[0] == "--list":
        list_pending(args[1] if len(args) > 1 else default_pending_dir())
        return 0

    path = args[0]
    if not os.path.isfile(path):
        print(f"Not a file: {path}", file=sys.stderr)
        return 1
    digest(path, full=full)
    return 0


if __name__ == "__main__":
    sys.exit(main())
