# Signals

What each of the six families measures, from what, and what it cannot tell you.
`../scripts/pulse_metrics.py` produces them; none is estimated.

| Family | Question | Source | Blind spot |
|---|---|---|---|
| Freshness / heartbeat | Is anything still running? | `state.runs.<skill>.last_run_at` against `briefing.expected_runs`; newest dated note under `kb.paths.sessions` and `kb.paths.dreams` | a quiet dream writes no note, so the file date alone would mislead: the run record is the heartbeat, the file date is corroboration |
| Capture | Is every substantive session reaching the knowledge base? | `pending/` depth and age; ended transcripts under the Claude projects directory that `../../../scripts/pending_sessions.py` calls substantive and that have no copy in `pending/` or `archive/` | a session written up live and never archived reads as a miss only if substantive work followed the log call, which is the sweep's own rule |
| Reuse | Do notes get used by other notes? | inbound relative links, from notes created 7-35 days ago, excluding index files, logs, dreams, drafts, inbox and transcripts as sources and targets | links are a proxy for use: a note can be read often and never linked |
| Consultation | Does work start from the vault? | tool calls in the last window's sessions with 6+ typed messages: any tool matching `lookup_pattern`, or Read, Grep or Glob under `kb.local_root` | counts a lookup anywhere in the session, not only before the first write |
| Learning | Do corrections take effect? | Memory entries at `fold_status: none` past 14 days; ledger items with no `Promoted:` or `Proposed:` marker; title-overlap pairs between this window's memory entries and older ones | the overlap test only suggests pairs; the skill adjudicates them, and a repeat worded differently is missed |
| Backlog | Is the loop closing? | `cursors.kb-dream.open_followups`; Inbox depth and the age of the oldest file | an item's file date is its last edit, so a touched old item reads younger |

## Not measured, by design

- Whether a note is **correct**. `kb-dream` owns fact and name checks.
- Whether the user **agrees** with it. Only a human verification says that.
- Voice quality. `skill-health-check` and the voice review own it.

## First run

There is no prior, so no trend. The first reading is the baseline, and the first few
amber signals are the real backlog, not new faults. Say so in the entry.
