# Closed log and handler-outcomes summary

The "Since last briefing" block in the posted message (see `message-format.md`), and the
Closed log lines briefing writes to the surface. Both draw on the same step 2/step 5 work;
this file covers the shapes, not the classification logic (that's `surface-protocol.md`'s
tick/edit/delete table, applied in `SKILL.md` step 2).

## Handler outcomes since last run

Read `state.outcomes` (ring buffer, newest first) and keep every entry whose `recorded_at`
falls inside `last_run_ts -> now`. For each one, one line:

```
* {handler} {outcome}: {report_line's one sentence} - {ref}
```

`{outcome}` and `{report_line}` come straight from the handler's return JSON
(`handler-contract.md`'s return contract) as already recorded in `state.outcomes` - briefing
never re-derives or re-words a handler's own report line, only lists it.

## Queued-but-undispatched count

While running step 2's close loop, a ticked delegate item with **no sub-line underneath it at
all** - not even a router "no handler" line - was ticked after the hub's per-run dispatch cap
(`handler-contract.md`, "Per-run budget") was already spent, or before the hub has run since
the tick. Count these across every delegate section and report the total as one line:

```
* {n} ticked item(s) queued, waiting on the next dispatch run
```

Omit this line when the count is zero. This is the mechanism that guarantees the user never
has to open the surface to learn that something they ticked has not been actioned yet - the
whole point of the reporter role.

## Nothing to report

When `state.outcomes` has no entries in the window and the queued count is zero, the whole
"Since last briefing" block becomes one line: "Nothing to report." Never omit the heading
itself - a quiet run still confirms the check happened, same logic as the snapshot rule's
"written every run" clause.

## Closed log line

Per `surface-protocol.md`'s "The Closed log":

```
- <date> (<tag>) <outcome> - <original text, 120 chars> - <by you | by <handler>>
```

Briefing writes one such line per item closed in step 2, newest first, prepended above the
existing Closed block, then runs `../scripts/trim_closed.py` (14 days or 40 lines, whichever
bound is hit first) on the resulting list before the step 6 write. The trim runs every time
this step fires, even when nothing new closed this run - it is a mechanical bound, not a
judgement call.
