# Closing, the Closed log and the "Since last briefing" block

The closing loop in `SKILL.md` step 2, the Closed lines briefing writes in step 6, and
the "Since last briefing" block in the posted message (see `message-format.md`). The
classification logic itself is `surface-protocol.md`'s tick table and "Closing" section;
this file covers the shapes.

## What closes

| Line state on read | Closes as | By |
|---|---|---|
| Any line with a `done` sub-line from the hub or an inline action | the sub-line's outcome word (`done`, `filed PRJ-172`, `added to glossary`) | the handler named in the sub-line, or `router` |
| A ticked To-do line | `done` | you |
| An option whose sibling closed as `done` | `not chosen` | you |
| The chosen option | `chosen` | you, plus the handler's own outcome on the same line if it dispatched |
| A line whose tag has a `state.outcomes` entry with `status: done` and no sub-line (the manual `skill-eval` path) | the outcome's `report_line` | skill-eval |
| A line with a `no handler` sub-line | `acknowledged, no handler` | you |
| A `term:` line with a `done` sub-line | removed from the board, no Closed line | (nothing logged) |

Everything else stays: an unticked line, a ticked line with no sub-line (queued), a
`partial` or `blocked` sub-line, a `needs your tick` whose fresh line is still open, a
`blocked · pick one` group. An idea block whose every line has closed is removed with its
header in the same write; a block with any open line stays whole.

## Closed log line

Per `surface-protocol.md`'s "The Closed log":

```
- <date> (<tag>) <outcome> · <original text, 120 chars> · <by you | by <handler>>
```

Briefing writes one such line per closed line, newest first, prepended above the existing
Closed block, then runs `../scripts/trim_closed.py` (7 days or 40 lines, whichever bound
is hit first) on the resulting list before the step 6 write. The trim runs every time this
step fires, even when nothing new closed this run.

## Handler outcomes since last run

Read `state.outcomes` (ring buffer, newest first) and keep every entry whose `recorded_at`
falls inside `last_run_ts -> now`. For each one, one line:

```
* {handler} {outcome}: {report_line's one sentence} · {ref}
```

`{outcome}` and `{report_line}` come straight from the handler's return JSON as recorded
in `state.outcomes`; briefing never re-words a handler's report line, only lists it.

## Queued-but-undispatched count

While closing, a ticked line with **no sub-line underneath it at all** was ticked after
the hub's per-run dispatch cap was spent, or before the hub has run since the tick. Count
these across the whole board and report the total as one line:

```
* {n} ticked item(s) queued, waiting on the next dispatch run
```

Omit this line when the count is zero. This is what guarantees the user never has to open
the board to learn that something they ticked has not been actioned yet.

## The Runs block

Built from `state.runs`, one line per scheduled skill that ran inside the window, in a
fixed order (proactive-router, action-sweep, idea-scout, idea-deep-dive, idea-wireframe,
kb-dream, skill-health-check), then the health scores, FYIs and overdue lines:

```
Runs
* {skill} {status}: {runs.<skill>.note} · {runs.<skill>.ref}
* {skill} fast-fail: {runs.<skill>.note}
* health: {skill} green · {skill} amber ({why}) · …          (from runs.skill-health-check.scores; red is on the board, not here)
* fyi: {one line} · {permalink}                               (from runs.proactive-router.fyi, one line each)
* overdue: {skill} last ran {n} days ago (expected every {max_gap_days})
```

Rules:

- A `quiet` run gets one short line (`idea-scout quiet: nothing qualifying`). A skill that
  did not run inside the window gets no line unless it is overdue.
- `overdue` compares `runs.<skill>.last_run_at` against `profile.briefing.expected_runs`;
  a skill absent from that map is never called overdue. This replaces every per-skill
  webhook and the old proof-of-life post: a skill that stopped running shows up here.
- Health: a red score is a `shc:` line on the board and is not repeated in the message;
  amber and green appear here only, from `runs.skill-health-check.scores`, and only for
  skills scored inside the window.
- FYIs come from `runs.proactive-router.fyi` written by the last Router run in the window.
  They are never written to the board.
- A fast-fail line is the only place the user sees it, so it carries the note verbatim.

## Nothing to report

When the window has no outcomes, no queued lines, and the Runs block is empty, the whole
"Since last briefing" block becomes one line: "Nothing to report." Never omit the heading
itself; a quiet window still confirms the check happened.
