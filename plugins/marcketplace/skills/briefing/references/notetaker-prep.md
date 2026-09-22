# Notetaker prep lines

New responsibility, gated entirely by `profile.notetaker.prep_lines` and capped at
`profile.budgets.briefing.notetaker_calls` (default 1) - it never grows briefing's connector
budget beyond what's already allowed.

## When it fires

Only when `profile.notetaker.prep_lines` is true. If false or unset, skip this step entirely
- no notetaker call, no `prep:` lines, and step 4's calendar sub-bullet for prep never
appears.

## What counts as prep-worthy

For each of today's calendar events (from step 4's calendar call, already made):

1. **A recurring meeting with a prior transcript or notes.** If the notetaker holds a
   transcript or notes for the previous instance of that recurring meeting (matched by
   title, or by the notetaker's own recurrence grouping if it exposes one), that counts.
2. **A document link in the event description.** If the calendar event's own description
   carries a link to a document (an agenda, a brief, a design doc - any URL that reads as a
   working document rather than a meeting-join link), that counts too, with no notetaker call
   needed for this case.

## The one call

Spend the single notetaker call (`notetaker: list meetings`, scoped to
`notetaker.lookback_days`) once, covering every recurring event found in the same pass -
never one call per event. If the list call surfaces a matching prior instance, a second call
(`notetaker: transcript`) is not made here; the prep line points at the notetaker's own
record rather than pulling the transcript's full content into this run's context - briefing
summarises status, it does not do the notetaker's job of surfacing meeting content.

## The line

One `prep:` sub-line directly under the calendar event it belongs to, in the Calendar
snapshot (see `message-format.md`):

```
* {time range} {subject}
  prep: {one clause - what's available and where, not a summary of its contents}
```

Example: `prep: last instance's notes cover the multi-yard allocation question raised again
today` - naming what's relevant to today's meeting, not restating the whole prior transcript.

## Degradation

If the notetaker call fails or the service isn't connected, no `prep:` lines appear this run
- the Calendar snapshot itself is unaffected (it degrades independently per
`tool-capabilities.md`'s per-category rule), and nothing about the failure is reported beyond
that silence; prep lines are a nice-to-have layered on a snapshot that already stands without
them.
