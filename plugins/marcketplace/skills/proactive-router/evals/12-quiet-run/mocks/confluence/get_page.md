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
  pr:260921-01: {section: For you, written_by: proactive-router, written_at: 2026-09-21T23:30:00+10:00, text: "✉️ draft an email to Renata Diaz (Vantage Freightways) proposing a discovery call", text_hash: h-pr01, ref: "https://northwindlogistics.slack.com/archives/CEXAMPLEFRTINT1/p1758510001000100", category: email, group: "", idea_key: ""}
machines:
  eval-machine: {tools: {chat: "mcp__slack__"}, resolved_at: 2026-09-21T23:30:00+10:00}
```

The `text_hash` on each item is the hash of the `text` shown beside it, given in full so
the skill can compare the canvas line's current text against it directly. A line whose
canvas text equals its `text` is untouched (or only ticked); one whose text differs was
edited by the user.
