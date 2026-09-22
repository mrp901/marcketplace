# Output format and worked examples

## Sweep-run summary (end of the sweep flow)

Report a flat list, no headers:

```
<Short label> - [KEY](url)
<Short label> - [KEY](url), <any status note, e.g. Parked for now until FLT-149>
```

One line per candidate, in the order they appear in the note. Add a status note only
where relevant (parked, blocked, unclear routing) - not on every line.

## Worked example - drafting, against `profiles/example.md`

Sweep finds a Slack canvas to-do committing to a small fix, and a tracker mention still
unaddressed. Note gets a `### Draft - Truncate long load names in the summary table
[ROUTE: small]` block and a `## Needs your reply` line. Two delegate lines land on the
surface's Actions section:

```
- [ ] (sweep:260922-1) [minor] draft ready - truncate long load names in the summary table · Inbox/2026-09-22-action-sweep.md#draft-truncate-long-load-names
- [ ] (sweep:260922-2) reply needed on FLT-166, still unaddressed since 18 Sep · Inbox/2026-09-22-action-sweep.md#needs-your-reply
```

## Worked example - `targeted` handler dispatch

Payload: `item.tag: sweep:260922-1`, `item.category: ticket-minor`, `mode: targeted`.
Re-reads the anchor in the note, confirms the draft still stands (no one else has since
commented on the area it touches), and returns:

```json
{
  "status": "needs_confirmation",
  "report_line": "draft ready to push: Story to FLT-401, truncate long load names · Inbox/2026-09-22-action-sweep.md#draft-truncate-long-load-names",
  "artefacts": [{"kind": "sweep_draft", "ref": "Inbox/2026-09-22-action-sweep.md#draft-truncate-long-load-names"}],
  "next_action": {"category": "sweep-push", "text": "push: file Story 'truncate long load names' to FLT-401", "ref": "Inbox/2026-09-22-action-sweep.md#draft-truncate-long-load-names"}
}
```

The hub writes the fresh `sweep-push` delegate line under the sub-line; only its tick
dispatches `push`.

## Worked example - `push` handler dispatch (the confirming tick)

Payload: `item.category: sweep-push`, `mode: push`, `item.ref` the same anchor. Re-reads
the note fresh (picking up any edit made since drafting), files the Story against
`tracker.default_parent_epic`, and returns:

```json
{
  "status": "done",
  "report_line": "filed FLT-407: truncate long load names in the summary table · https://northwindlogistics.atlassian.net/browse/FLT-407",
  "artefacts": [{"kind": "tracker_issue", "ref": "FLT-407"}],
  "next_action": null
}
```
