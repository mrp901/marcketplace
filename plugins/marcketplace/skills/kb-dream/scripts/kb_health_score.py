#!/usr/bin/env python3
"""Score kb-dream's health signals. Reads one JSON object on stdin, prints one JSON object.

Ported from the retired vault-pulse skill (1.11.0), minus its heartbeat and open-follow-ups
signals (the briefing's expected_runs and skill-health-check watch the heartbeats).

Input:
  {"metrics": <kb_health_metrics.py output>,
   "confirmed_repeats": n,                            # the skill's adjudication of the candidates; omit if not adjudicated
   "thresholds": {"<signal key>": [green_edge, amber_edge]},   # profile overrides, optional
   "prior": {"<signal key>": value},                  # last verdict's values, for the trend
   "prior_at": {"<signal key>": "<iso>"},             # when each prior value was last measured
   "now": "<iso>"}

Exits 2 with {"error": ...} when the input is unreadable or carries the metrics script's own error.

Output: {"signals": {key: {tag, value, prev?, why}}, "overall": {tag, headline},
         "values": {key: value}, "values_at": {key: iso}, "carried": [key]}
`values` is what the skill stores as the next verdict's prior. A key the prior holds that this run
did not measure (e.g. learning.confirmed_repeats on a health-only run) is carried forward into
`values` unchanged and listed in `carried` (not graded), for at most 30 days since it was last
measured (`values_at`, which the skill stores beside `values` as the next prior_at).

A signal that was not measured is tagged "unmeasured", never green. Overall is red if any
signal is red, amber if any is amber or two or more are unmeasured, else green. Every
threshold is a default; see references/kb-health.md for the reasoning behind each.
stdlib only.
"""
import json
import sys
from datetime import datetime

# key: (green_edge, amber_edge, direction). "low": value <= green_edge is green, <= amber_edge
# is amber, else red. "high": value >= green_edge is green, >= amber_edge is amber, else red.
DEFAULTS = {
    "freshness.sessions_days": (5, 10, "low"),
    "capture.oldest_pending_days": (3, 7, "low"),
    "capture.pending": (5, 10, "low"),
    "capture.unarchived_ended_sessions": (0, 2, "low"),
    "reuse.share": (0.60, 0.40, "high"),
    "lookups.share": (0.50, 0.25, "high"),
    "learning.stuck_at_none": (0, 3, "low"),
    "learning.unmarked_ledger": (0, 5, "low"),
    "learning.confirmed_repeats": (0, 2, "low"),
    "backlog.inbox_oldest_days": (14, 60, "low"),
}


CARRY_DAYS = 30


def grade(v, g, a, direction):
    if direction == "high":
        return "green" if v >= g else "amber" if v >= a else "red"
    return "green" if v <= g else "amber" if v <= a else "red"


def main():
    try:
        d = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"unreadable input: {e}"}))
        return 2
    m = d.get("metrics") or {}
    err = d.get("error") or m.get("error")
    if err:
        print(json.dumps({"error": err}))
        return 2
    now = datetime.fromisoformat(d["now"]).replace(tzinfo=None) if d.get("now") else datetime.now()
    prior = d.get("prior") or {}
    T = dict(DEFAULTS)
    for k, v in (d.get("thresholds") or {}).items():
        if k in T and isinstance(v, list) and len(v) == 2:
            T[k] = (v[0], v[1], T[k][2])
    sig, values = {}, {}

    def put(key, value, why, tag=None):
        if tag is None:
            g, a, direction = T[key]
            tag = grade(value, g, a, direction)
        sig[key] = {"tag": tag, "value": value, "why": why}
        if key in prior:
            sig[key]["prev"] = prior[key]
        values[key] = value

    def unmeasured(key, why):
        sig[key] = {"tag": "unmeasured", "value": None, "why": why}

    f = (m.get("freshness") or {}).get("sessions") or {}
    if f.get("measured"):
        put("freshness.sessions_days", f["days_ago"], f"newest session note {f['days_ago']} d old")
    else:
        unmeasured("freshness.sessions_days", f.get("why", "not measured"))

    c = m.get("capture") or {}
    if c.get("measured"):
        put("capture.oldest_pending_days", c["oldest_pending_days"],
            f"{c['pending']} session(s) pending ({c.get('pending_files', c['pending'])} file(s)), oldest {c['oldest_pending_days']} d")
        put("capture.pending", c["pending"], f"{c['pending']} pending")
        put("capture.unarchived_ended_sessions", c["unarchived_ended_sessions"],
            f"{c['unarchived_ended_sessions']} ended substantive session(s) with no pending or archive copy")
    else:
        unmeasured("capture", c.get("why", "not measured"))

    r = m.get("reuse") or {}
    if r.get("measured"):
        put("reuse.share", r["share"], f"{r['linked']} of {r['matured']} matured notes have a real inbound link")
    else:
        unmeasured("reuse.share", r.get("why", "not measured"))

    lk = m.get("lookups") or {}
    if lk.get("measured"):
        put("lookups.share", lk["share"], f"{lk['consulted']} of {lk['sessions']} sessions consulted the knowledge base")
    else:
        unmeasured("lookups.share", lk.get("why", "not measured"))

    lg = m.get("learning") or {}
    mem, led = lg.get("memory") or {}, lg.get("ledger") or {}
    if mem.get("measured"):
        put("learning.stuck_at_none", mem["stuck_at_none"], f"{mem['stuck_at_none']} memory entries still fold_status none")
        n = d.get("confirmed_repeats")
        if n is not None:
            put("learning.confirmed_repeats", n, f"{n} of {len(mem['repeat_candidates'])} repeat candidate(s) confirmed")
    else:
        unmeasured("learning.stuck_at_none", mem.get("why", "not measured"))
    if led.get("measured"):
        put("learning.unmarked_ledger", led["unmarked_over_window"],
            f"{led['unmarked_over_window']} of {led['items']} ledger items carry no Promoted or Proposed marker")
    else:
        unmeasured("learning.unmarked_ledger", led.get("why", "not measured"))

    b = m.get("backlog") or {}
    if b.get("measured"):
        put("backlog.inbox_oldest_days", b["oldest_inbox_days"],
            f"{b['inbox']} inbox item(s), oldest {b['oldest_inbox_days']} d")
    else:
        unmeasured("backlog.inbox_oldest_days", b.get("why", "not measured"))

    # A value this run did not measure (a health-only or quiet run adjudicates no repeats; a signal
    # came back unmeasured) keeps the last verdict's number, so the next trend still has a prior.
    # It is carried, not graded: it stays out of `signals` and never moves the overall tag.
    # A carried value expires after CARRY_DAYS so a stale number is never shown as a fresh trend.
    # `prior_at` stamps each value with when it was last measured; one with no stamp (a prior written
    # before stamps existed) is carried once and stamped now.
    prior_at = d.get("prior_at") or {}
    values_at = {k: now.isoformat() for k in values}
    carried = []
    for k in sorted(prior):
        if k not in T or k in values or not isinstance(prior[k], (int, float)):
            continue
        try:
            age = (now - datetime.fromisoformat(prior_at[k]).replace(tzinfo=None)).days if k in prior_at else 0
        except ValueError:
            age = 0
        if age <= CARRY_DAYS:
            values[k] = prior[k]
            values_at[k] = prior_at.get(k, now.isoformat())
            carried.append(k)

    tags = [s["tag"] for s in sig.values()]
    red = [k for k, s in sig.items() if s["tag"] == "red"]
    amber = [k for k, s in sig.items() if s["tag"] == "amber"]
    gaps = [k for k, s in sig.items() if s["tag"] == "unmeasured"]
    overall = "red" if red else "amber" if amber or len(gaps) >= 2 else "green"
    parts = []
    if red:
        parts.append("red: " + ", ".join(red))
    if amber:
        parts.append("amber: " + ", ".join(amber))
    if gaps:
        parts.append("not measured: " + ", ".join(gaps))
    headline = "; ".join(parts) if parts else f"all {len(tags)} signals green"
    print(json.dumps({"signals": sig, "overall": {"tag": overall, "headline": headline},
                      "values": values, "values_at": values_at, "carried": carried}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
