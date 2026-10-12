# Worked example

Against `profiles/example.md`: Priya Kanth, Product Manager at Northwind Logistics,
tracker project FLT, kb "Northwind Ops Vault". Fictional throughout.

## build

Priya, 12:35: "build me a list for this afternoon". No list for today in `Drafts/`, so
`build`. The cursor says yesterday 17:00; the calendar shows a free block to the 16:30
roadmap review.

Six search-tier subagents return 31 candidates. Verification drops nine: a question
Tomasz answered at 11:02, a ticket closed overnight, an email Priya already sent. The
critic flags one name: "Owen" on a carrier email is the carrier's Owen, not Owen
Fairclough, so the row is reworded. Written to
`Drafts/2026-10-14-1235-afternoon-actions.md`:

```markdown
**If you only do three things:**
1. Send Ana the depot-map feedback. You told her at 10:12: "I'll get it to you after lunch".
2. Answer Tomasz's two questions on FLT-1188 (In QA since 09:40).
3. Reply to the carrier's rate-change email; they asked for an answer "by end of day".

| # | Action | Who's waiting / why now | Source | Effort | Draft |
|---|---|---|---|---|---|
| 1 | Send Ana the depot-map feedback | Your promise, 10:12 | chat DM | 10m | A |
| 2 | Answer Tomasz on FLT-1188 | QA blocked on the scope question | FLT-1188 | 10m | B |
```

## work

Priya, 14:05: "work the afternoon list, item 2 first". Item 2 says FLT-1188 has two open
questions. Re-checked: Priya answered the first at 13:40, so only the second is open, and
the draft shrinks to one question.

That question needs a product call: does the route report open on the last 12 months, or
only the months with data? Asked once, recommending the full 12 because it shows the gap.
Priya: "full 12, current month plus trailing 11". The comment is shown in full; Priya says
yes; it is posted; the report gives its id.

Tomasz has also found a bug in the same ticket. Recommended: a Bug under the maintenance
epic. Priya: "not a bug, a story under FLT-1201, use my mock-up". Three siblings under
FLT-1201 are read for format, the story is drafted in that shape and shown, and created on
her yes. The mock-up cannot be attached through the connector, so the report says so and
leaves it as her step.

At 16:20 Priya: "all done". The list gets its banner, `status: deprecated` and a
`**Deprecation**` log line, and `session-log` is offered.
