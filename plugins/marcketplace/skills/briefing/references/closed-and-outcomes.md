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
| An option whose sibling closed as `done` or `expired` | `not chosen` | you |
| The chosen option | `chosen` | you, plus the handler's own outcome on the same line if it dispatched |
| A line whose tag has a `state.outcomes` entry with `status: done` and no sub-line (the manual `skill-eval` path) | the outcome's `report_line` | skill-eval |
| A line with a `no handler` sub-line | `acknowledged, no handler` | you |
| A line whose latest sub-line is `partial`, `blocked` or a router `queued` note, with no newer sub-line for `briefing.stale_after_business_days` business days (below) | `expired · no activity for 5 business days` | you |
| A `term:` line with a `done` sub-line | removed from the board, no Closed line | (nothing logged) |

Every tag closed or removed here also goes into `closed` in briefing's shard (`SKILL.md`
step 3); that is how the owner, and the hub, tell a closed line from a deleted one.

Everything else stays: an unticked line, a ticked line with no sub-line (queued), a
`partial` or `blocked` sub-line inside the expiry window, a `needs your tick` whose fresh line is still open, a
`blocked · pick one` group. An idea block whose every line has closed is removed with its
header in the same write; a block with any open line stays whole.

## Expiry of stuck lines

Nothing acts on a `partial`, `blocked` or router `queued` sub-line by itself, so without a
limit the line sits open for ever. The threshold is `briefing.stale_after_business_days`:
absent means 5, `0` disables expiry.

- Look only at the line's **latest** sub-line (`↳ <handler> <date[ time]>: ...`). It must be
  `partial`, `blocked` or a router `queued` note (`↳ router <date>: queued for ...`), and no
  newer sub-line may follow it.
- Business days are Mon-Fri in `org.timezone`, counted from the latest sub-line's date to the
  run date (times of day ignored): the weekdays after the sub-line's date, up to and including
  the run date. Expire when that count reaches the threshold. A `partial` dated Mon 28 Sep
  expires on the run of Mon 5 Oct. Public holidays are not treated specially.
- Never expire a `needs your tick` sub-line, a line with no sub-line, a To-do line or a `term:`
  line. A `blocked · pick one` sub-line is waiting on the user and stays.
- The Closed line reads `expired · no activity for N business days` (N is the threshold) and
  the by-field is `by you`, like `not chosen`. The tag goes into `closed` (step 3).
- Idea-decision option groups: an expired option closes like any close, so its siblings close
  `not chosen` under the sibling rule above, and the question's block is removed once no open
  line is left in it.

## Closed log line

Per `surface-protocol.md`'s "The Closed log":

```
- <date> (<tag>) <outcome> · <original text, 120 chars> · <by you | by <handler>>
```

Briefing writes one such line per closed line, newest first, prepended above the existing
Closed block, then runs `../scripts/trim_closed.py` (5 days or 20 lines, whichever bound
is hit first) on the resulting list before the step 6 write. The trim runs every time this
step fires, even when nothing new closed this run.

## Handler outcomes since last run

Read `state.outcomes` (the hub's and `skill-eval`'s rings, each in its own shard, merged
newest first) and keep every entry whose `recorded_at` falls inside `last_run_ts -> now`. For each one, one line:

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

## Expired lines

Every line closed as `expired` in this run is named in the "Since last briefing" block, so
nothing leaves the board unseen: one line, the count then the tags.

```
* {n} line(s) expired, no activity for {N} business days: {tag}, {tag}, ...
```

Omit it when none expired. It counts toward "Nothing to report" like the queued line.

## The Runs block

Built from `state.runs`, one line per scheduled skill that ran inside the window, in a
fixed order (proactive-router, action-sweep, idea-spar, kb-dream, skill-health-check), then the health scores, FYIs and overdue lines:

```
Runs
* {skill} {status}: {runs.<skill>.note} · {runs.<skill>.ref}
* {skill} fast-fail: {runs.<skill>.note}
* health: {skill} green · {skill} amber ({why}) · …          (from runs.skill-health-check.scores; red is on the board, not here)
* kb health {tag}: {runs.kb-dream.health.why} · {runs.kb-dream.ref}   (the knowledge base's compounding verdict; see the rule below)
* fyi: {one line} · {permalink}                               (from runs.proactive-router.fyi, one line each)
* overdue: {skill} last ran {n} days ago (expected every {max_gap_days})
```

Rules:

- A `quiet` run gets one short line (`idea-spar quiet: nothing moved into Next`). A skill that
  did not run inside the window gets no line unless it is overdue.
- `overdue` compares `runs.<skill>.last_run_at` against `profile.briefing.expected_runs`;
  a skill absent from that map is never called overdue. This replaces every per-skill
  webhook and the old proof-of-life post: a skill that stopped running shows up here.
- Health: a red score is a `shc:` line on the board and is not repeated in the message;
  amber and green appear here only, from `runs.skill-health-check.scores`, and only for
  skills scored inside the window.
- KB health: `runs.kb-dream.health` (kb-dream's one-line verdict, until 1.11.0 the
  `vault-pulse` skill's) is reported on every briefing while its tag is amber or red, so a
  bad reading cannot be missed by skipping one message, with its date when `health.at` is
  older than the briefing window (a run with no local access leaves the last verdict as it
  was). A green reading adds nothing: kb-dream's own Runs line already covers the run. The
  verdict never writes to the board, so this line is the only place the user sees it. A
  profile or state still carrying `runs.vault-pulse` is ignored.
- FYIs come from `runs.proactive-router.fyi` written by the last Router run in the window.
  They are never written to the board.
- A fast-fail line is the only place the user sees it, so it carries the note verbatim.

## Nothing to report

When the window has no outcomes, no queued lines, and the Runs block is empty, the whole
"Since last briefing" block becomes one line: "Nothing to report." Never omit the heading
itself; a quiet window still confirms the check happened.
