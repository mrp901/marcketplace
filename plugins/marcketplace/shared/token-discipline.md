# Token discipline

Guidelines, not hard caps, for keeping every scheduled run as cheap as its actual work.
Every `SKILL.md` links here from its `## Budget`. Nothing here ever trades away a quality
step; rule 7 says so and outranks the other six.

1. **Quiet exit first.** Each skill starts with its cheapest "anything to do?" check and
   stops with `runs.<skill>.status: quiet` when there is nothing. Each skill writes its
   own condition into its `SKILL.md`'s `## Budget`. For example:
   - proactive-router: no new reactions or saves since the cursor, and no surface line
     differs from `state.items`.
   - idea-scout: no qualifying idea, no requeued idea, and no roadmap change.
   - idea-wireframe: nothing eligible and nothing requeued.
   - kb-dream: nothing new in the inbox or the log since the last dream, and not a
     monthly run.
   - skill-health-check: no runs since the last check.
   - action-sweep: every search returns nothing new.
   - briefing never exits quiet: its snapshots and report are the point of the run.
2. **Fast-fail early.** Precondition checks (profile keys, state readable, the
   identity-critical connector) come before any expensive read. This extends
   `onboarding.md`'s fast-fail rule: fail on the first missing thing, not after a sweep.
3. **One job per run.** A skill does its one job and stops. It does not pick up
   neighbouring work "while it's here"; anything else it notices becomes a For you line
   for a later run, if it needs the user, or nothing at all.
4. **Subagents for bulk raw reading.** Reading threads, transcripts, web pages or
   knowledge-base search results goes to a `budgets.models.search`-tier subagent that
   returns a short structured answer, so raw content stays out of the skill's own
   context (`model-tiers.md`). Don't use a subagent for a single small read; the
   overhead outweighs the saving.
5. **Load references lazily.** Open a `references/` file only in the step that needs it,
   never all of them up front.
6. **Read once, write once.** One surface read, one surface write batch, one state read
   and one state write per run. Use cursors so nothing is re-read.
7. **Never trade away quality steps.** Critic audits, voice registers, verification and
   source citations are never skipped to save tokens. If a budget runs out, return
   `partial` and say what's left, rather than doing a thinner job and calling it done.
