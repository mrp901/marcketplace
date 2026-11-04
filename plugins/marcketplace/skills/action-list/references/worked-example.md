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
## I owe

| Owed to | What you said you'd do | Promised | Age | Link | Row |
|---|---|---|---|---|---|
| Ana Reyes | Send the depot-map feedback: "I'll get it to you after lunch" | Wed 14 Oct, 10:12 | 0 bd | [DM](https://northwindlogistics.slack.com/archives/DEXAMPLE0001/p1760400720000100) | #1 |
| Owen Fairclough | Go back to him on the Q3 carrier rates: "I can check about Q3" | Mon 5 Oct, 16:40 | 7 bd | [thread](https://northwindlogistics.slack.com/archives/CEXAMPLEFRTOPS1/p1759646400000200) | - |

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

## prep

Priya, 08:50 the next day: "prep my 1:1 with Tomasz". `people` has one Tomasz, so no
question. The kb's folder table names `Meetings/` for dated conversations and the people
file links `Meetings/2026-10-07-tomasz-1on1.md`, the last 1:1. Five subagents return. The
note, `Drafts/2026-10-15-0852-tomasz-1on1-prep.md`, is one screen:

- **You owe him:** the FLT-1188 scope answer (promised 9 Oct, 4 bd), quoted.
- **He owes you:** the carrier-export sample, "I'll send you one Monday" (12 Oct, 3 bd).
- **His open asks:** whether the MTD comparison includes cancelled loads (FLT-166, 2 bd).
- **Carried from 7 Oct:** "agree an owner for the dock-sync notes", still open.
- **Recurring:** in three of the last four meetings, who owns the multi-yard scope call,
  each time left with Ana. Marked unresolved.

Nothing is sent; `session-log` is not offered, because nothing was worked.
