#!/usr/bin/env python3
"""Measure whether a knowledge base is compounding. Prints one JSON object, writes nothing.

Usage:
    pulse_metrics.py --kb-root <dir> [--days 7] [--dreams <rel>] [--sessions <rel>]
                     [--memory <rel>] [--inbox <rel>] [--ledger <rel>]
                     [--lookup-pattern <regex>] [--matured-from 35] [--matured-to 7]
                     [--stale-memory-days 14] [--stale-ledger-days 7] [--now <iso>]

Every path flag is relative to --kb-root and optional: a signal whose folder is not given
or does not exist comes back as {"measured": false, "why": ...}, never as a zero. Not
measured is not green, and the scorer treats it that way.

Signals, in the order of references/signals.md:
  freshness  newest dated note per folder (the heartbeat's file-side evidence)
  capture    pending/ queue depth and age, and ended transcripts with no archive copy
  reuse      share of matured notes that a later, real note links to
  lookups    share of recent sessions that consulted the knowledge base through a tool
  learning   Memory entries stuck at fold_status none; ledger items with no Promoted marker;
             candidate repeat pairs for the skill to adjudicate
  backlog    Inbox depth and age

stdlib only, read-only. Time is the local clock unless --now is given (ISO 8601).
"""
import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timedelta

DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})")
LINK_RE = re.compile(r"\]\(([^)\s]+?\.md)(?:#[^)\s]*)?\)")
FM_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)
SKIP_DIRS = {".utility", ".obsidian", ".git", "Inbox", "Drafts", "Dreams", "Transcripts"}
NOT_NOTES = re.compile(r"^(index|log|log-archive.*)\.md$", re.I)
IDLE_HOURS = 2
MIN_BYTES = 64 * 1024
STOP = set("the a an of to for and or in on with is are was be by at as it this that from not no".split())


def parse_now(s):
    return datetime.fromisoformat(s) if s else datetime.now()


def naive(dt):
    return dt.replace(tzinfo=None) if dt.tzinfo else dt


def read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def name_date(name):
    m = DATE_RE.match(name)
    if not m:
        return None
    try:
        return datetime(int(m[1]), int(m[2]), int(m[3]))
    except ValueError:
        return None


def note_date(path, text):
    """Creation date: frontmatter generated.at, else a filename date prefix, else None."""
    fm = FM_RE.match(text)
    if fm:
        m = re.search(r"generated:.*?at:\s*(\d{4}-\d{2}-\d{2})", fm.group(1))
        if m:
            return datetime.fromisoformat(m.group(1))
    return name_date(os.path.basename(path))


def days_between(now, then):
    return round((now - then).total_seconds() / 86400, 1)


def md_files(root):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in (".git", ".obsidian")]
        for f in fn:
            if f.endswith(".md"):
                yield os.path.join(dp, f)


# ---------------------------------------------------------------- signals

def freshness(root, now, folders):
    out = {}
    for label, rel in folders.items():
        d = os.path.join(root, rel) if rel else ""
        if not rel or not os.path.isdir(d):
            out[label] = {"measured": False, "why": "folder not configured or absent"}
            continue
        dates = [x for x in (name_date(f) for f in os.listdir(d) if f.endswith(".md")) if x]
        if not dates:
            out[label] = {"measured": False, "why": "no dated notes"}
            continue
        newest = max(dates)
        out[label] = {"measured": True, "newest": newest.date().isoformat(),
                      "days_ago": days_between(now, newest)}
    return out


def session_dir():
    env = os.environ.get("SESSION_LOG_DIR")
    if env:
        return env
    ptr = os.path.join(os.path.expanduser("~"), ".claude", "marcketplace", "session-log-dir.ref")
    try:
        v = read(ptr).strip()
        if v:
            return v
    except OSError:
        pass
    return os.path.join(os.path.expanduser("~"), ".claude", "session-log")


def projects_dir():
    root = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")
    return os.path.join(root, "projects")


def load_pending_sessions():
    """The plugin's own session helpers (what is substantive, what is one session), defined once."""
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.normpath(os.path.join(here, "..", "..", "..", "scripts", "pending_sessions.py"))
    if not os.path.isfile(path):
        return None
    spec = importlib.util.spec_from_file_location("pending_sessions", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def capture(now, days):
    base = session_dir()
    pend = os.path.join(base, "pending")
    arch = os.path.join(base, "archive")
    if not os.path.isdir(base):
        return {"measured": False, "why": f"no session-log directory at {base}"}
    pending = [p for p in glob.glob(os.path.join(pend, "*.jsonl"))]
    ages = [(now - datetime.fromtimestamp(os.path.getmtime(p))).total_seconds() / 86400 for p in pending]
    held = " ".join(os.listdir(pend) if os.path.isdir(pend) else []) + " " + \
           " ".join(os.listdir(arch) if os.path.isdir(arch) else [])
    helpers = load_pending_sessions()
    if helpers is None:
        return {"measured": False, "why": "scripts/pending_sessions.py not found beside the plugin"}
    assess = helpers.assess
    # Age from when each session first entered the queue (1.10.0 `queued_since`), so a long
    # session that keeps ending does not reset the backlog's age.
    ages = [helpers.queued_age_days(pend, os.path.basename(p)) for p in pending]
    cutoff = now - timedelta(days=days)
    orphans = []
    for p in glob.glob(os.path.join(projects_dir(), "*", "*.jsonl")):
        try:
            st = os.stat(p)
        except OSError:
            continue
        mt = datetime.fromtimestamp(st.st_mtime)
        if mt < cutoff or (now - mt) < timedelta(hours=IDLE_HOURS) or st.st_size < MIN_BYTES:
            continue
        stem = os.path.basename(p)[:-6][:8]
        if stem in held:
            continue
        substantive, typed, writes = assess(p, 0.0)[:3]
        if substantive:
            orphans.append({"session": stem, "typed": typed, "writes": writes,
                            "ended": mt.isoformat(timespec="minutes")})
    # One per session, not per file: before 1.10.0 every end of a long-lived session queued another
    # full copy, and 38 files held 10 sessions (26 Oct 2026).
    sessions = helpers.session_stems(os.path.basename(p) for p in pending)
    return {"measured": True, "pending": len(sessions), "pending_files": len(pending),
            "oldest_pending_days": round(max(ages), 1) if ages else 0.0,
            "unarchived_ended_sessions": len(orphans), "unarchived": orphans[:10]}


def reuse(root, now, frm, to):
    notes, text_of = {}, {}
    for p in md_files(root):
        rel = os.path.relpath(p, root).replace("\\", "/")
        parts = rel.split("/")
        if NOT_NOTES.match(parts[-1]):
            continue
        text_of[rel] = read(p)
        if set(parts[:-1]) & SKIP_DIRS:
            continue
        d = note_date(p, text_of[rel])
        if d:
            notes[rel] = d
    inbound = {rel: set() for rel in notes}
    for src, txt in text_of.items():
        sp = src.split("/")
        if set(sp[:-1]) & SKIP_DIRS:
            continue
        for m in LINK_RE.finditer(txt):
            tgt = m.group(1)
            if "://" in tgt:
                continue
            tgt = os.path.normpath(os.path.join(os.path.dirname(src), tgt.replace("%20", " "))).replace("\\", "/")
            if tgt in inbound and tgt != src:
                inbound[tgt].add(src)
    lo, hi = now - timedelta(days=frm), now - timedelta(days=to)
    matured = [r for r, d in notes.items() if lo <= d <= hi]
    if len(matured) < 5:
        return {"measured": False, "why": f"only {len(matured)} notes in the maturing window"}
    linked = [r for r in matured if inbound[r]]
    unlinked = sorted(set(matured) - set(linked))
    return {"measured": True, "matured": len(matured), "linked": len(linked),
            "share": round(len(linked) / len(matured), 2), "unlinked": unlinked[:10]}


def lookups(root, now, days, pattern):
    cutoff = now - timedelta(days=days)
    rx = re.compile(pattern)
    kb = root.replace("\\", "/").lower().rstrip("/")
    sessions = consulted = 0
    for p in glob.glob(os.path.join(projects_dir(), "*", "*.jsonl")):
        try:
            st = os.stat(p)
        except OSError:
            continue
        if datetime.fromtimestamp(st.st_mtime) < cutoff or st.st_size < MIN_BYTES:
            continue
        typed = hit = 0
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if '"tool_use"' not in line and '"user"' not in line:
                    continue
                try:
                    o = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(o, dict) or o.get("isSidechain"):
                    continue
                msg = o.get("message") if isinstance(o.get("message"), dict) else {}
                c = msg.get("content")
                if o.get("type") == "user" and not o.get("isMeta"):
                    t = c if isinstance(c, str) else " ".join(
                        b.get("text", "") for b in (c or []) if isinstance(b, dict) and b.get("type") == "text")
                    if t.strip() and not t.lstrip().startswith(("<", "Caveat:", "[Request interrupted")):
                        typed += 1
                elif o.get("type") == "assistant" and isinstance(c, list) and not hit:
                    for b in c:
                        if not (isinstance(b, dict) and b.get("type") == "tool_use"):
                            continue
                        name = str(b.get("name") or "")
                        blob = json.dumps(b.get("input") or {}).replace("\\\\", "/").lower()
                        if rx.search(name) or (name in ("Read", "Grep", "Glob") and kb in blob):
                            hit = 1
                            break
        if typed >= 6:
            sessions += 1
            consulted += hit
    if sessions < 3:
        return {"measured": False, "why": f"only {sessions} sessions with 6+ typed messages in the window"}
    return {"measured": True, "sessions": sessions, "consulted": consulted,
            "share": round(consulted / sessions, 2)}


def words(s):
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 2}


def learning(root, now, memory, ledger, mem_days, led_days, days):
    out = {}
    md = os.path.join(root, memory) if memory else ""
    if not md or not os.path.isdir(md):
        out["memory"] = {"measured": False, "why": "memory folder not configured or absent"}
    else:
        entries = []
        for p in glob.glob(os.path.join(md, "*.md")):
            if NOT_NOTES.match(os.path.basename(p)):
                continue
            t = read(p)
            fm = FM_RE.match(t)
            head = fm.group(1) if fm else ""
            title = (re.search(r"^title:\s*(.+)$", head, re.M) or [None, ""])[1]
            fold = (re.search(r"^fold_status:\s*(\S+)", head, re.M) or [None, ""])[1]
            entries.append((os.path.basename(p), title, fold, name_date(os.path.basename(p))))
        stuck = [e[0] for e in entries if e[2] == "none" and e[3] and (now - e[3]).days > mem_days]
        recent = [e for e in entries if e[3] and (now - e[3]).days <= days]
        older = [e for e in entries if e[3] and (now - e[3]).days > days]
        pairs = []
        for r in recent:
            wr = words(r[1])
            for o in older:
                wo = words(o[1])
                if wr and wo and len(wr & wo) / len(wr | wo) >= 0.5:
                    pairs.append({"new": r[0], "older": o[0]})
        out["memory"] = {"measured": True, "entries": len(entries), "stuck_at_none": len(stuck),
                         "stuck": stuck[:10], "repeat_candidates": pairs[:5]}
    lp = os.path.join(root, ledger) if ledger else ""
    if not lp or not os.path.isfile(lp):
        out["ledger"] = {"measured": False, "why": "ledger not configured or absent"}
    else:
        sections = re.split(r"(?m)^## ", read(lp))[1:]
        total = unmarked = 0
        for s in sections:
            d = name_date(s)
            for blk in re.split(r"(?m)^(?=\d+\. )", s)[1:]:
                total += 1
                if "Promoted:" not in blk and "Proposed:" not in blk and d and (now - d).days > led_days:
                    unmarked += 1
        out["ledger"] = {"measured": True, "items": total, "unmarked_over_window": unmarked}
    return out


def backlog(root, now, inbox):
    d = os.path.join(root, inbox) if inbox else ""
    if not d or not os.path.isdir(d):
        return {"measured": False, "why": "inbox not configured or absent"}
    files = [p for p in glob.glob(os.path.join(d, "*")) if os.path.isfile(p) and not NOT_NOTES.match(os.path.basename(p))]
    ages = [(now - datetime.fromtimestamp(os.path.getmtime(p))).days for p in files]
    return {"measured": True, "inbox": len(files), "oldest_inbox_days": max(ages) if ages else 0}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kb-root", required=True)
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--dreams", default="")
    ap.add_argument("--sessions", default="")
    ap.add_argument("--memory", default="")
    ap.add_argument("--inbox", default="")
    ap.add_argument("--ledger", default="")
    ap.add_argument("--lookup-pattern", default=r"(?i)vault|bwdocs|codemap|knowledge|(^|__)kb[-_]")
    ap.add_argument("--matured-from", type=int, default=35)
    ap.add_argument("--matured-to", type=int, default=7)
    ap.add_argument("--stale-memory-days", type=int, default=14)
    ap.add_argument("--stale-ledger-days", type=int, default=7)
    ap.add_argument("--now", default="")
    a = ap.parse_args()
    if not os.path.isdir(a.kb_root):
        print(json.dumps({"error": f"kb root not found: {a.kb_root}"}))
        return 2
    now = naive(parse_now(a.now))
    root = a.kb_root
    out = {
        "at": now.isoformat(timespec="minutes"), "window_days": a.days,
        "freshness": freshness(root, now, {"dreams": a.dreams, "sessions": a.sessions}),
        "capture": capture(now, a.days),
        "reuse": reuse(root, now, a.matured_from, a.matured_to),
        "lookups": lookups(root, now, a.days, a.lookup_pattern),
        "learning": learning(root, now, a.memory, a.ledger, a.stale_memory_days, a.stale_ledger_days, a.days),
        "backlog": backlog(root, now, a.inbox),
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
