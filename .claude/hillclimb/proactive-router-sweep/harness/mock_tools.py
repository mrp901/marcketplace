#!/usr/bin/env python3
"""Deterministic local stand-in for the chat (Slack) and wiki (Confluence) tools the
proactive-router skill calls, serving one fictional workspace from the sweep-real eval.

    python mock_tools.py --run <run_dir> --world w1 <tool> [args]

Tools (mirroring the MCP tools the skill's profile resolves to):
    search_public_and_private --filters "<slack filters>" [--keywords ...]
    read_thread --channel <id> --ts <ts>
    read_context --channel <id> --ts <ts>        (messages around a non-threaded message)
    read_canvas --id <canvas id>
    update_canvas --id <canvas id> --file <path to the full new canvas markdown>
    get_page --id <page id>
    update_page --id <page id> --file <path to the new page body>

Every call is appended to <run_dir>/mock_calls.jsonl as {n, tool, input, output}.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_worlds as bw  # noqa: E402

CANVAS_ID = "FEXAMPLECANVAS1"
CANVAS = """# Priya's board
_Updated daily by briefing. Tick a line to say yes, do it._
_Sections: Today, To-do, For you, Ideas, Closed._

## Today
### Calendar - Tue 22 Sep
- 10:00 Freight Ops standup
- 14:00 Dock-capacity review prep
### Tracker - Tue 22 Sep
- FLT-21030 moved to In Review

## To-do
- [ ] Book dock-capacity review (todo:220901-1)
- [ ] Send Q3 lane numbers to Graham (todo:220901-2)

## For you

## Ideas

## Closed
"""
SECTION_IDS = {"Today": "sec-today", "To-do": "sec-todo", "For you": "sec-foryou",
               "Ideas": "sec-ideas", "Closed": "sec-closed"}


def world(name):
    items = bw.load()
    rows = []
    for k, iid in enumerate(bw.WORLDS[name]):
        target_ts, msgs = bw.place(items[iid], k)
        rows.append((items[iid], target_ts, msgs))
    return rows


def msg_view(item, m):
    ch = item["channel"]
    return {"channel": ch["name"], "channel_id": ch["id"], "channel_type": ch["type"],
            "ts": m["ts"], "posted_at": m["when"] + " AEST", "author": m["author"],
            "author_id": m["author_id"], "is_bot": m["is_bot"], "text": m["text"],
            "permalink": bw.permalink(ch["id"], m["ts"])}


def search(rows, filters, keywords):
    f = filters or ""
    emoji = re.findall(r"hasmy::([a-z0-9_+-]+):", f)
    saved = "is:saved" in f
    out = []
    for item, target_ts, msgs in rows:
        tgt = next(m for m in msgs if m["role"] == "target")
        hit = (saved and item["source"] == "saved") or \
              (item["source"] == "reacted" and item["reaction"].strip(":") in emoji)
        if hit and not keywords:
            v = msg_view(item, tgt)
            v["reply_count"] = sum(1 for m in msgs if m["role"] == "thread")
            v["thread_ts"] = target_ts if v["reply_count"] else None
            out.append(v)
    return {"messages": out, "total": len(out)}


def find(rows, channel, ts):
    for item, target_ts, msgs in rows:
        if item["channel"]["id"] == channel and any(m["ts"] == ts for m in msgs):
            return item, target_ts, msgs
    return None


def read_thread(rows, channel, ts):
    hit = find(rows, channel, ts)
    if not hit:
        return {"error": "thread_not_found"}
    item, target_ts, msgs = hit
    thread = [m for m in msgs if m["role"] in ("thread", "target")]
    if len(thread) == 1:
        return {"messages": [msg_view(item, thread[0])], "note": "no replies"}
    return {"messages": [msg_view(item, m) for m in thread]}


def read_context(rows, channel, ts):
    hit = find(rows, channel, ts)
    if not hit:
        return {"error": "message_not_found"}
    item, target_ts, msgs = hit
    ctx = [m for m in msgs if m["role"] in ("context", "target")]
    return {"messages": [msg_view(item, m) for m in ctx]}


STATE = """```yaml
state_version: 1
installed_version: 1.1.0
profile_ref: confluence:8f2e4a91-example-cloud-id/889000111
runs: {}
cursors:
  briefing: {last_run_ts: 2026-09-22T06:45:00+10:00}
items: {}
registry: {}
tally: {}
outcomes: []
suppressions: []
patterns_blocked: []
proposals: []
glossary: []
ideas: {}
machines:
  eval-machine: {tools: {chat: "mock_tools.py", wiki: "mock_tools.py"}, resolved_at: 2026-09-21T23:30:00+10:00}
```"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--world", required=True)
    ap.add_argument("tool")
    ap.add_argument("--filters", default="")
    ap.add_argument("--keywords", nargs="*", default=[])
    ap.add_argument("--channel")
    ap.add_argument("--ts")
    ap.add_argument("--id")
    ap.add_argument("--file")
    a, extra = ap.parse_known_args()
    rows = world(a.world)
    inp = {k: v for k, v in vars(a).items() if k not in ("run", "world", "tool") and v not in (None, "", [])}
    if extra:
        inp["unparsed"] = extra
    t = a.tool
    if t == "search_public_and_private":
        out = search(rows, a.filters, a.keywords)
    elif t == "read_thread":
        out = read_thread(rows, a.channel, a.ts)
    elif t == "read_context":
        out = read_context(rows, a.channel, a.ts)
    elif t == "read_canvas":
        out = {"canvas_id": CANVAS_ID, "content": CANVAS, "section_id_mapping": SECTION_IDS} \
            if a.id == CANVAS_ID else {"error": "canvas_not_found"}
    elif t in ("update_canvas", "update_page"):
        body = open(a.file, encoding="utf-8").read() if a.file else sys.stdin.read()
        inp["content"] = body
        inp.pop("file", None)
        out = {"ok": True}
    elif t == "get_page":
        if a.id == "889000111":
            out = {"id": a.id, "title": "marcketplace profile", "body": "```yaml\n" + bw.PROFILE_YAML + "\n```"}
        elif a.id == "990111222":
            out = {"id": a.id, "title": "marcketplace state", "body": STATE}
        else:
            out = {"error": "page_not_found"}
    else:
        out = {"error": f"no such tool: {t}. Tools: search_public_and_private, read_thread, read_context, "
                        "read_canvas, update_canvas, get_page, update_page"}
    os.makedirs(a.run, exist_ok=True)
    log = os.path.join(a.run, "mock_calls.jsonl")
    n = sum(1 for _ in open(log, encoding="utf-8")) + 1 if os.path.exists(log) else 1
    with open(log, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"n": n, "tool": t, "input": inp, "output": out}, ensure_ascii=False) + "\n")
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
