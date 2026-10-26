# Scoring

`../scripts/score_pulse.py` holds the defaults; this file says what each signal means and why
the edge sits where it does, so a change is a decision and not a drift. Override any pair
in `profile.budgets.vault-pulse.thresholds` as `{"<signal key>": [green_edge, amber_edge]}`;
the direction (lower or higher is better) is fixed by the signal.

Overall: **red** if any signal is red; **amber** if any is amber, or two or more are
`unmeasured`; otherwise **green**. A signal that cannot be measured is never green.

| Signal key | Green / amber edge | Why that edge | Needs you (when amber or red) |
|---|---|---|---|
| `heartbeat.<skill>` | age / expected gap: 1.0 / 2.0 | on schedule, or one missed run; past two gaps it has stopped | name the skill; "run it once interactively and read its `runs` note" |
| `freshness.sessions_days` | 5 / 10 days | a weekend plus a normal gap is fine; ten days with no session note means capture, not a quiet week, unless `capture` says nothing ended | run `/marcketplace:session-log` |
| `capture.oldest_pending_days` | 3 / 7 | the queue is drained at session start; older than a week is a queue nobody opens | run `/marcketplace:session-log`, oldest first |
| `capture.pending` | 5 / 10 | sessions, not files (a newer copy of a session replaces the older one in `pending/`); the sweep queues at most 8 per start; past 10 it is outrunning the drain | same |
| `capture.unarchived_ended_sessions` | 0 / 2 | an ended session that qualifies as substantive (`../../../scripts/pending_sessions.py`'s own test) yet has no pending or archive copy means the hook or the sweep missed it. The sweep repairs it at the next session start, so one or two is amber; three is a broken route | check the SessionEnd hook; `../../../scripts/pending_sessions.py --dry-run` shows what the sweep would queue |
| `reuse.share` | 0.60 / 0.40 | share of notes 7-35 days old with at least one inbound link from a real note (not an index, a log or a dream). A note nothing links to is invisible in the graph; under 40% means capture is a write-only archive | list the unlinked notes from the entry: link, supersede or deprecate each |
| `lookups.share` | 0.50 / 0.25 | share of sessions with 6+ typed messages that read the knowledge base through a tool. The compounding test: work that starts from the vault, not beside it. Counts any tool matching `lookup_pattern` (default: vault, bwdocs, codemap, knowledge, kb) or a Read, Grep or Glob under `kb.local_root` | if low for several weeks: the lookup rule in the user's global instructions is not firing |
| `learning.stuck_at_none` | 0 / 3 | memory entries older than 14 days still at `fold_status: none`: learned but neither folded nor ruled not-needed. `kb-dream` closes these within a cycle or two, so a pile means its fold step has stalled | check `kb-dream`'s last dream note for the fold step |
| `learning.unmarked_ledger` | 0 / 5 | voice-ledger items older than 7 days with no `Promoted:` or `Proposed:` marker. 39 sat unpromoted for nine days once; that is the failure this catches | check the voice-review step in `kb-dream` |
| `learning.confirmed_repeats` | 0 / 2 | a correction recorded twice means the first did not take effect. Zero is the goal; each confirmed pair names a memory that is not landing | name the pair; check whether a fold or a skill rule is owed |
| `backlog.followups_open` | 10 / 20 | open follow-ups on `kb-dream`'s ledger; a list that only grows means the loop is not closing | answer the dream's "Surfaced for you" lines |
| `backlog.followups_oldest_days` | 14 / 30 | the oldest one, since an old item is a decision nobody is making | name it |
| `backlog.inbox_oldest_days` | 14 / 60 | Inbox is for triage, not storage; two months is not being triaged | triage the Inbox: name the oldest item |

## Trend

`prior` is last run's `values`. The entry shows the previous value beside the current one,
and a signal that has been amber or red on three consecutive runs is called out as
persistent in "Needs you", ahead of newer ones. The first run has no prior and says so.

## Changing an edge

Only in the profile, with the reason in the next log entry. If the same edge is moved twice
the reason is wrong: look at what the signal is measuring instead.
