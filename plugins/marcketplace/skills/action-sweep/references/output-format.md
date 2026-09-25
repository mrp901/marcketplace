# Output format and worked examples

## For you lines (end of the sweep flow)

One line per find, in `../../../shared/surface-protocol.md`'s grammar, tag
`(sweep:<yymmdd>-N)`, category emoji from `handler-contract.md`, reading as the action a
tick causes. Against `profiles/example.md`:

```
- [ ] (sweep:260922-1) 🎫 [minor] draft a Story under FLT-401: truncate long load names in the summary table · https://northwindlogistics.slack.com/docs/TEXAMPLE001/FEXAMPLECANVAS9
- [ ] (sweep:260922-2) 🎫 draft a reply on FLT-166: Tomasz asked whether the MTD comparison should include cancelled loads · https://northwindlogistics.atlassian.net/browse/FLT-166
- [ ] (sweep:260922-3) 💬 draft a reply to Owen in #freight-ops: he's waiting on your call about the support-ticket spike · https://northwindlogistics.slack.com/archives/CEXAMPLEFRTOPS1/p1758600001000100
- [ ] (sweep:260922-4) ☑️ to-do: send Tomasz the Q4 capacity figures by Friday (you said so in #planning) · https://northwindlogistics.slack.com/archives/CEXAMPLEPLAN001/p1758600002000200
- [ ] (sweep:260922-5) 🗓️ draft the follow-up you took in Tuesday's dock sync: confirm multi-yard scope with Ana · notetaker:meeting/2026-09-20-dock-sync
```

A candidate whose tier is unclear is a question, not a guess:

```
- Which tier for "rework the load-plan export"? (from #freight-ops, 21 Sep)
  - [ ] (sweep:260922-6a) 🎫 [minor] small: a Story under FLT-401
  - [ ] (sweep:260922-6b) 🎫 larger: an idea on FIG for discovery first
  - [ ] (sweep:260922-6c) 🎫 larger, defined: a new epic in FLT
```

The run record (`runs.action-sweep.note`) is one line: `7 finds: 2 chat, 1 mention, 1
tracker, 1 meeting, 1 canvas, 1 tier question`.

## Worked example: `targeted` handler dispatch

Payload: `item.tag: sweep:260922-1`, `item.category: ticket-minor`, `mode: targeted`.
Reads the canvas to-do through a subagent, sizes it small, writes
`Drafts/sweep-260922-1.md` per `draft-format.md`, and returns:

```json
{
  "status": "needs_confirmation",
  "report_line": "drafted a Story under FLT-401: truncate long load names in the summary table · Drafts/sweep-260922-1.md",
  "artefacts": [{"kind": "sweep_draft", "ref": "Drafts/sweep-260922-1.md"}],
  "next_action": {"category": "sweep-push", "text": "push: file Story 'truncate long load names' under FLT-401 from the draft", "ref": "Drafts/sweep-260922-1.md"}
}
```

The hub writes the fresh `sweep-push` line under the sub-line; only its tick dispatches
`push`.

## Worked example: `push` handler dispatch (the confirming tick)

Payload: `item.category: sweep-push`, `mode: push`, `item.ref: Drafts/sweep-260922-1.md`.
Re-reads the draft fresh (picking up any edit the user made), files the Story against
`tracker.default_parent_epic`, and returns:

```json
{
  "status": "done",
  "report_line": "filed FLT-407: truncate long load names in the summary table · https://northwindlogistics.atlassian.net/browse/FLT-407",
  "artefacts": [{"kind": "tracker_issue", "ref": "FLT-407"}],
  "next_action": null
}
```
