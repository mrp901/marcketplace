Return the state document `990111222`. It parses as YAML with these relevant fields (every
other subtree exists with its documented default or is empty):

```yaml
state_version: 1
installed_version: 1.1.0
profile_ref: confluence:8f2e4a91-example-cloud-id/889000111
runs:
  proactive-router: {last_run_at: 2026-09-21T23:30:00+10:00, status: ok, note: "1 dispatched", ref: ""}
cursors:
  briefing: {last_run_ts: 2026-09-22T06:45:00+10:00}
  proactive-router: {last_scanned: 2026-09-21T23:30:00+10:00}
ideas: {}
registry: {}          # shipped defaults apply
tally: {}
proposals: []
suppressions: []
patterns_blocked: []
outcomes: []
items:
  FIG-204/d2a: {section: Ideas, written_by: idea-scout, written_at: 2026-09-21T02:10:00+10:00, text: "One fixed distance/time drift for every route", text_hash: h-d2a, ref: "", category: idea-decision, group: FIG-204/d2, idea_key: FIG-204}
  FIG-204/d2b: {section: Ideas, written_by: idea-scout, written_at: 2026-09-21T02:10:00+10:00, text: "A threshold set per customer", text_hash: h-d2b, ref: "", category: idea-decision, group: FIG-204/d2, idea_key: FIG-204}
machines:
  eval-machine: {tools: {chat: "mcp__slack__"}, resolved_at: 2026-09-21T23:30:00+10:00}
```

The `text_hash` on each item is the hash of the `text` shown beside it, given in full so
the skill can compare the canvas line's current text against it directly. A line whose
canvas text equals its `text` is untouched (or only ticked); one whose text differs was
edited by the user.
