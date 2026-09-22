# Gather procedure

Run all four sources independently; a failure in one never blocks the others - write that
source's part of the note as "couldn't reach X" and move on, same fail-fast principle as
`briefing`.

## 1. Chat canvases (current state - no cursor)

Search for canvases authored by the user, most recent first. Read every one found and
pull out anything phrased as an outstanding action or to-do, but only items that
plausibly need a tracker reply or ticket - skip kb-admin, personal, or process to-dos
(a maintenance flag, a scheduling chore). They are real, just out of this skill's scope,
and listing them as if they need engineering follow-up is noise. Canvases represent
current state, not a stream - there is no "since" filter here.

**Guardrail.** If the search turns up more than `budgets.action-sweep.canvas_guard`
canvases, stop and ask which are current before reading all of them - that volume
suggests stale ones have accumulated, and guessing which matter would be worse than
asking. Unattended, this becomes a fast-fail note on this source only (not the whole
run): "too many canvases (`N` > guard) - run interactively to pick".

**Chase, don't just list.** If a to-do names a specific, searchable source already within
reach (a named DM, a named channel, a named thread), do one targeted search there before
writing the to-do into the note as unresolved. Cap it at
`budgets.action-sweep.targeted_search_per_todo` (one) search per to-do - if it doesn't
resolve cleanly, list the to-do as written and say it was checked.

## 2. Tracker comments mentioning the user (since the cursor)

See `mention-search-method.md` for the full procedure and why the obvious full-text
search doesn't work. Cursor is `state.cursors.action-sweep.scanned_through`; on cold
start (no cursor recorded yet) default to `budgets.action-sweep.cold_start_days` and say
so plainly in the note's intro - a safe, stated default, not a silent one.

## 3. Tickets currently assigned to the user (current state - no cursor)

`tracker: search issues (JQL)` with `tracker.my_work_jql`. This is "what's currently on
my plate," not an incremental feed - always the full current list, every run.

## 4. Notetaker action items (the fourth source)

`notetaker: list meetings` within `notetaker.lookback_days`, then `notetaker: transcript`
per meeting to pull action items the user committed to in that meeting. This is often the
highest-signal source and the easiest to lose - a spoken commitment has no other record
once the meeting ends. Subject to the same drafting and confirmation discipline as the
other three: nothing here is pushed to the tracker without a fresh tick, same as any
other candidate. Bounded by `notetaker.lookback_days` only; no separate meeting-count cap
is defined yet (see `HISTORY.md`'s open questions).
