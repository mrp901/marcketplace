# The knowledge-base health verdict

Curation (the passes) keeps the knowledge base conformant, linked and de-duplicated. It
does not tell the user whether the knowledge base is doing its job as the first port of call
for the AI harness: whether what is captured is fresh, gets found and read, and whether
corrections stick. The verdict does, in one line, at the end of a pass. Two stdlib scripts
measure it, never the model's impression, and it never edits a note, never writes a
`dream:` line and never posts. The briefing carries it
(`../../briefing/references/closed-and-outcomes.md`, "The Runs block"). It was the
`vault-pulse` skill until 1.11.0.

## When it runs

Flow step 10, on every pass that can measure: the non-quiet ones, and the quiet ones too,
because a stalled capture is exactly what a quiet dream sees. It reads local files and the
Claude session transcripts, so it needs a shell and `kb.local_root`. A run without them (a
cloud routine) skips it: `runs.kb-dream.health` stays as the last run that could measure
left it, and Flags says `Health: not measured (no local access)`. Never estimate a number
the scripts did not produce.

## Steps

1. **Measure.** `../scripts/kb_health_metrics.py --kb-root <kb.local_root> --days <window_days,
   default 7> --dreams <kb.paths.dreams> --sessions <kb.paths.sessions> --memory
   <kb.paths.memory> --ledger <kb.paths.voice>/edits-ledger.md`, plus `--lookup-pattern` if
   `budgets.kb-dream.health.lookup_pattern` is set. Read-only JSON out. A signal it cannot
   measure comes back `measured: false` with the reason; carry that through.
2. **Adjudicate repeats** (non-quiet runs only). `learning.memory.repeat_candidates` are
   title-overlap pairs, not verdicts. Read both entries of each (at most 5). A **repeat** is
   the same correction or preference recorded twice because the first did not change
   behaviour; two entries on one topic that add something new are not. Count the confirmed
   ones. A quiet run adjudicates nothing and omits `confirmed_repeats`.
3. **Score.** Pipe `{metrics, confirmed_repeats, thresholds, prior, now}` to
   `../scripts/kb_health_score.py`: `thresholds` from `budgets.kb-dream.health.thresholds`,
   `prior` from `cursors.kb-dream.last_health_values`.
4. **Record.** `runs.kb-dream.health` = `{tag, why, at}`: `tag` is the scorer's overall tag,
   `why` its headline led by the worst signal's action from the table, under 200 characters
   so it reads alone in a chat message (`unmarked voice-ledger items 5, run the voice
   review`). `cursors.kb-dream.last_health_values` = the scorer's `values`. The dream note's
   Flags gets `Health: <tag>: <why>`. A first reading has no prior: say it is the baseline,
   and that its amber signals are the real backlog, not new faults.

## Signals and edges

Overall: **red** if any signal is red; **amber** if any is amber, or two or more are
`unmeasured`; otherwise **green**. A signal that cannot be measured is never green. Override
an edge only in the profile (`budgets.kb-dream.health.thresholds`, `{"<signal key>":
[green_edge, amber_edge]}`, direction fixed by the signal) with the reason in that run's
dream note; an edge moved twice means the signal is being misread, so look at what it
measures instead.

| Signal key | Green / amber edge | What it measures, and why the edge sits there |
|---|---|---|
| `freshness.sessions_days` | 5 / 10 days | age of the newest session note. A weekend plus a normal gap is fine; ten days with none means capture, not a quiet week, unless `capture` says nothing ended. Action: run `/marcketplace:session-log` |
| `capture.oldest_pending_days` | 3 / 7 | age of the oldest session in `pending/`. The queue drains at session start; over a week is a queue nobody opens |
| `capture.pending` | 5 / 10 | sessions, not files (a newer copy replaces the older). The sweep queues at most 8 per start; past 10 it is outrunning the drain |
| `capture.unarchived_ended_sessions` | 0 / 2 | ended sessions `../../../scripts/pending_sessions.py` calls substantive yet with no pending or archive copy: the hook or sweep missed them. The sweep repairs one or two at the next start; three is a broken route. Action: check the SessionEnd hook |
| `reuse.share` | 0.60 / 0.40 | share of notes 7-35 days old with an inbound link from a real note (not an index, a log or a dream). An unlinked note is invisible in the graph; under 40% capture is a write-only archive. Action: link, supersede or deprecate the unlinked notes it lists |
| `lookups.share` | 0.50 / 0.25 | share of sessions with 6+ typed messages that read the knowledge base through a tool (any tool matching `lookup_pattern`, default vault, bwdocs, codemap, knowledge, kb, or a Read, Grep or Glob under `kb.local_root`). The compounding test: work that starts from the vault. Low for weeks means the lookup rule in the user's global instructions is not firing |
| `learning.stuck_at_none` | 0 / 3 | memory entries over 14 days old still at `fold_status: none`. The fold step closes these within a cycle or two; a pile means it has stalled |
| `learning.unmarked_ledger` | 0 / 5 | voice-ledger items over 7 days old with no `Promoted:` or `Proposed:` marker. 39 sat unpromoted for nine days once. Action: check `voice-review.md` Part A |
| `learning.confirmed_repeats` | 0 / 2 | a correction recorded twice means the first did not take effect. Zero is the goal; each pair names a memory that is not landing |

## Blind spots, by design

Inbound links are a proxy for use (a note can be read often and never linked). The
consultation count credits a lookup anywhere in a session, not only before the first write.
The repeat test suggests pairs by title and misses a repeat worded differently. It does not
measure whether a note is correct (the name and fact passes own that), whether the user
agrees with it (only a human verification says so) or voice quality (`skill-health-check`
and the voice review). Whether `kb-dream` itself is still running belongs to
`briefing.expected_runs`; the open-follow-ups count was dropped with the escalation pass.
