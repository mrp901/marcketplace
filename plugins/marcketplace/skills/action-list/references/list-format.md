# List format

The shape `build` writes. It is a plan for one stretch of one day, read on a screen in a
few minutes and then worked, so it leads with what to do and keeps the evidence one click
away.

## Path and frontmatter

`kb.paths.drafts` + `YYYY-MM-DD-HHMM-<window>-actions.md`
(`2026-10-09-1238-post-lunch-actions.md`). A list is a transient draft under
`kb-conventions.md`'s "Transient drafts" rule: it is not indexed into the topic structure,
and `kb-dream` reaps it once it is closed or stale, so the inbox triage never files it away
before it is worked. The time in the name keeps a second list for the same window apart
from the first; the new one gets a one-line pointer banner on the old one, never a delete.

```yaml
---
type: <the live registry's plan-shaped type, checked every run; if none exists, add one to the live registry in the same turn, per kb-conventions>
title: <Window> actions (<D Mon YYYY>)
description: Ranked action list and ready-to-send drafts for <user>'s <window>, built from <the sources actually read>.
tags: [actions, <two or three topic tags from what the list covers>]
status: draft
generated: { by: action-list, at: <ISO 8601, org.timezone offset> }
stale_after: <the next day>
supersedes_on: closed on the user's word, or past stale_after
---
```

## Body, in order

1. **Window read** - the exact window, and the line "Nothing has been sent, posted or
   edited anywhere. `[TBC: ...]` marks a fact I couldn't verify."
2. **The time available** - the free block from the calendar, the next commitment, and
   which rows fit before it.
3. **I owe** - what the user told people they would do: who it is owed to, what, when it
   was promised, its age in business days, a link, and the ranked row that does it, per
   `i-owe.md`, with a second "Waiting on you" table for asks that carry no promise. Always
   present; one line when nothing is owed.
4. **If you only do three things** - the top three, each one sentence, each quoting the
   promise or the ask that makes it urgent.
5. **Ranked actions** - one table: `#`, action (a concrete verb and object), who's waiting
   and why now (quoted, timestamped), source (a link), effort, and the draft it uses.
6. **Dropped** - resolved or not the user's, one line each with the evidence.
7. **Drafts** - one `###` per draft: channel, recipients and subject, the draft as a
   quote block, then "Check before sending" bullets naming each assumption.
8. **Couldn't confirm** - what the sources could not settle.
9. **Backlog, not today** - the board's open lines and any older open threads, grouped,
   with no ranking. Read only; the board stays the board's.

## Rules for the content

- A row past the verification cap is marked `unverified` with its age, never silently
  treated as open or done.
- Every rank cites its evidence. "Kim can't brief finance without it" quoting Kim beats
  "important follow-up".
- An effort is an honest guess in minutes, and "5m + wait" where the item waits on someone.
- A draft is written in the register its audience calls for, per `../../../shared/voice.md`,
  and run against the shared AI-patterns list before it lands.
- A promise of something the product does not do yet is never drafted as fact. Name the
  gap in "Check before sending" instead.
- Names are checked against `kb.people_file` before they are written.
