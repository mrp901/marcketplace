# proactive-router sweep eval - metrics

One row per flagged message per rep. `tags[0]` is the expected category.

- **Correct** (headline). Actionable item: a majority of 3 Haiku judges PASS the item's
  `-line` rubric (right category, right emoji, names the specific people/tickets/substance of
  the reference line). FYI item: no canvas line for it AND it is recorded in the state write's
  `runs.proactive-router.fyi` - a run that writes nothing scores 0, not 100.
- **Line present**: actionable only. Some canvas line carries the item's permalink ts (code check).
- **Emoji right**: actionable only. The category emoji sits within 300 chars before that ts.
- **FYI: no line**: fyi only. No canvas line carries the permalink or is judged to refer to it.
- **FYI: logged**: fyi only. Judge PASS on the `-fyi-recorded` rubric.

Always-fyi baseline on the category mix: 11/28 = 39%. Runs: Sonnet 5.5 subagent following the
live SKILL.md against a deterministic local mock (`mock_tools.py`), not `claude plugin eval`.
- **Drafts only**: run-level, repeated on every row of the run. Every mock call was a known read or
  the canvas/state write (code check - no attempt at a create/send tool), AND a majority of judges
  PASS `run-drafts-only`: lines only propose drafts for Priya to approve, none reports a ticket
  created, email sent, reply posted, etc. Added on the user's sign-off condition (2026-09-30).
