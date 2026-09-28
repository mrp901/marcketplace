# Escalating chronic follow-ups

Curation pass 5 consolidates open follow-ups (a session note's unticked "Proposed
follow-ups", an Open thread) into the dream note's Flags. Flags are write-once,
read-rarely by design, so a follow-up that stays open there is effectively invisible: it
can be listed dream after dream and never reach the user. This procedure gives such a
follow-up exactly one path to the board.

## The ledger

`state.cursors.kb-dream.open_followups` holds one entry per open follow-up, keyed
`<source note path>#<slug of the follow-up's own text>`:

```yaml
open_followups:
  Sessions/2026-09-09-dock-rules-restore.md#restore-15-files-from-version-history:
    text: restore the 15 overwritten dock-rule files from version history
    first_flagged_at: 2026-09-10
    dreams_open: 3
    escalated_tag: dream:260928-1      # absent until escalated
```

Every dream, in pass 5, after consolidating this run's list:

- **Still open.** The source checkbox is still unticked, and no evidence in hand shows it
  done (a `log.md` line, the target file now existing, a "not needed" note). Carry the
  entry forward and `dreams_open += 1`. An entry is still open even when this run read no
  new session note mentioning it. The ledger is what remembers it, not the session read.
- **Resolved.** It was ticked or marked "not needed" in its source note, or evidence shows
  it done. Drop the entry and count it in the note's "closed since last dream".
- **New:** add it with `dreams_open: 1`.

Checking an entry costs nothing beyond reads this run already makes. An entry whose source
note wasn't read this run is carried forward on the ledger alone, not re-fetched. A quiet
run doesn't reach pass 5, so `dreams_open` counts dreams that actually curated.

## Escalate at three

When `dreams_open` reaches 3 and `escalated_tag` is absent, the follow-up becomes a
Surfaced bullet in this run's dream note. It then gets its `dream:` line through
`notification-shape.md`'s ordinary one-line-per-Surfaced-bullet rule, with no extra canvas
read or write, because it rides the run's one update batch:

```
- [ ] (dream:<yymmdd>-N) 🧹 settle the follow-up open <dreams_open> dreams since <first_flagged_at>: <text> · <source note link>
```

Record the tag in `escalated_tag` and in `state.items` exactly like any other `dream:`
line (flow step 11). The threshold is three because two consecutive dreams can fall in one
busy week. A third means the follow-up has outlived the ordinary cadence at which the user
clears the board.

## After escalation

The board line now carries the follow-up. Never post a second line for the same ledger
entry, and settle the line per `notification-shape.md` like any other of this skill's
lines.

- **Ticked:** the hub dispatches `settle`. If evidence is in hand, settle does the work (a
  Decisions record it can write, for example). If the follow-up is already true, settle
  returns `done`. If it needs a human action, settle returns `partial` naming that one
  input, which is the usual outcome for a chronic follow-up. The line stays open under the
  hub's sub-line.
- **Deleted:** the user has dismissed it. Drop the ledger entry and stop listing it in
  Flags; never re-add it.
- **Resolved at source:** drop the entry. A later tick then reaches `settle`, which
  returns `done` naming who closed it.

Until then, Flags lists the follow-up by its tag (`escalated as dream:260928-1`) rather
than repeating it in full.
