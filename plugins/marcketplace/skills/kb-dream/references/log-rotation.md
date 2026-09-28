# Rotating an oversized log

`kb-conventions.md` gives every writer skill (`idea-scout`, `idea-wireframe`, `kb-note`,
`reply-draft`, `session-log`) the same rule: once `kb.paths.log` is past
`kb.log_size_cap_kb.writers`, defer the log line rather than retype a large full-replace
file. That rule is only safe if the deferral is short. This skill is the only one that
rotates the log, so this skill is what bounds how long a writer stays stuck.

## The trigger is the writers' cap, not this skill's own

Step 2 already reads `kb.paths.log`. Take its size from that same read. If it is over
`kb.log_size_cap_kb.writers` (default 20 KB), rotate **on this run**, incremental or full.
Do not wait for the first full dream of the month, and do not wait for the log to reach
`kb.log_size_cap_kb.dream` (default 40 KB).

The two caps answer different questions. `dream` is how large a file this skill will
retype for its own ordinary log lines. `writers` is the point at which every other writer
starts deferring. Rotating only at `dream`, or only on a full pass, leaves a window of
days to weeks in which every writer run defers its line and nothing clears the backlog.
Incremental dreams fire far more often than full ones, so tying rotation to the next dream
of either kind bounds a writer's deferral to at most one dream interval.

## How to rotate

Never destroy an input (rule 1 of the five-rule contract). Rotation is a move of old
entries into an archive file, never a trim.

1. **Split.** Keep in `log.md` the newest dated sections that together fit under half of
   `kb.log_size_cap_kb.writers`, and always today's heading, even if it is empty. Every
   older dated section moves.
2. **Write the archive first.** Create `log-archive/YYYY-MM-DD-log.md` beside
   `kb.paths.log` (rotation date; `-2` suffix if one exists), holding the moved sections
   verbatim, newest first, under a one-line header naming the date range. Read it back and
   confirm every moved date heading is present before touching `log.md`.
3. **Then rewrite `log.md`.** The kept sections, plus one pointer line directly under the
   title: `Older entries: [<first date> to <last date>](log-archive/YYYY-MM-DD-log.md)`,
   newest archive first. That pointer is the archive's one inbound link; it is not added to
   any `index.md`.
4. **Log the rotation itself** under today's heading: `**Update**` naming the archive path,
   the date range moved, and the old and new sizes.

If step 2's write or read-back fails, stop: leave `log.md` exactly as it was and record a
failed write in Flags. The same rotation failing on a later run meets the repetition bar
(`repetition-bar.md`) and becomes a Surfaced item, which is how a stuck log reaches the
user instead of deferring every writer indefinitely.

## Backfill what the writers deferred

After a successful rotation, add the log lines writers deferred while the log was over
cap: a note this run can already see (a folder `index.md` entry, or a writer's own
"log line outstanding" disclosure on the surface) that is dated after the log's newest
line and has no log line of its own. One line each, the verb the writer would have used,
marked `(backfilled)`. This stays within `budgets.kb-dream.incremental_reads`; a deferral
that can't be matched to a note from evidence in hand goes in Flags, never guessed.

## Reporting

One row in the dream note's "What I curated" table for the rotation, one for the backfill
(`+N deferred entries backfilled`). A rotation is never a quiet run: it always writes a
dream note.
