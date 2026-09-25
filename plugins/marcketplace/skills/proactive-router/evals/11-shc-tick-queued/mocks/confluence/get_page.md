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
  shc:260921-1: {section: For you, written_by: skill-health-check, written_at: 2026-09-21T03:00:00+10:00, text: "🔴 idea-deep-dive scored red: two notes superseded by your own corrections this fortnight. Run skill-eval on it?", text_hash: h-shc1, ref: ".utility/skill-health/idea-deep-dive.md", category: skill-eval, group: "", idea_key: ""}
machines:
  eval-machine: {tools: {chat: "mcp__slack__"}, resolved_at: 2026-09-21T23:30:00+10:00}
```

The `text_hash` on each item is the hash of the `text` shown beside it, given in full so
the skill can compare the canvas line's current text against it directly. A line whose
canvas text equals its `text` is untouched (or only ticked); one whose text differs was
edited by the user.
