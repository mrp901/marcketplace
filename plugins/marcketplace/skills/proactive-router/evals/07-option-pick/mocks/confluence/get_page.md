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
  FIG-204/d1a: {section: Ideas, written_by: idea-scout, written_at: 2026-09-21T02:10:00+10:00, text: "In-app only: cheap, but dispatchers report living in email", text_hash: h-d1a, ref: "", category: idea-decision, group: FIG-204/d1, idea_key: FIG-204}
  FIG-204/d1b: {section: Ideas, written_by: idea-scout, written_at: 2026-09-21T02:10:00+10:00, text: "Email only: reaches them, no history in-product", text_hash: h-d1b, ref: "", category: idea-decision, group: FIG-204/d1, idea_key: FIG-204}
  FIG-204/d1c: {section: Ideas, written_by: idea-scout, written_at: 2026-09-21T02:10:00+10:00, text: "Both: probably right, higher build cost now", text_hash: h-d1c, ref: "", category: idea-decision, group: FIG-204/d1, idea_key: FIG-204}
machines:
  eval-machine: {tools: {chat: "mcp__slack__"}, resolved_at: 2026-09-21T23:30:00+10:00}
```

The `text_hash` on each item is the hash of the `text` shown beside it, given in full so
the skill can compare the canvas line's current text against it directly. A line whose
canvas text equals its `text` is untouched (or only ticked); one whose text differs was
edited by the user.
