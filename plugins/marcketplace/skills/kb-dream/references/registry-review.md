# The monthly registry review

Runs on the first full-mode dream of a calendar month (see `SKILL.md`'s mode rule), or on
request. Reads `state.tally`, `state.outcomes`, `state.suppressions`,
`state.patterns_blocked` and `state.proposals` - all written by `proactive-router`, none
of them by this skill - and produces a compact summary plus at most three proposals.

## Reading the tally

For each `category` in `state.tally`: `proposed`, `ticked`, `deleted`, `edited`,
`unmapped_ticks`. A category the user keeps ticking despite having no handler
(`unmapped_ticks` climbing without a `state.registry[category]` entry) is the strongest
signal for a mapping proposal below - `handler-contract.md`'s own three-unmapped-ticks
proposal already fires at the router level; this review is the monthly, broader check that
catches a pattern the router's own per-run threshold hasn't yet crossed.

## At most three proposals

Pick from these two shapes, most evidence-backed first, and stop at three even where
more evidence exists - a longer list stops being worth reading:

1. **A mapping** for a category the user keeps ticking with no handler. Names the
   category and a candidate handler, evidenced by the tally counts that support it.
2. **A lift** for a suppression pattern (`state.suppressions`) that now looks wrong - the
   same `channel:category` pattern the user is starting to tick again despite the
   suppression, or a pattern whose deletions were long enough ago that it may no longer
   apply.

A handler whose output the user keeps editing is no longer this review's to raise:
`skill-health-check` reads the same tally and voice ledger, scores the handler amber or
red, and a red puts the "run skill-eval on it?" question on the board. One path to
`skill-eval`, not two.

Each proposal is one line in the dream note's Surfaced section and, if it's actionable in
one tick, one `dream:` line in For you.

**A proposal is also written into `state.proposals`,** with `kind` set to the matching
value: `suppression_lift` for a block that now looks wrong, `skill_fold` for a settled
correction that should become a rule in a named skill. `mapping` stays
`proactive-router`'s to raise, not this skill's.

Writing the record is what makes the board line mean anything: a tick on it dispatches
`settle`, which finds the proposal by its `id` and marks it accepted (a lift is applied to
`state.suppressions` there; a fold is never applied, only marked accepted for a human to
make). A proposal that exists only as prose in the dream note can be read but never acted
on.

Writing the record is not applying the proposal. The propose-only rule is unchanged: this
skill writes a record that a change has been proposed, never the change itself.

## Sixty-day dismissal

The one write this skill does make to `state.proposals`: any entry whose `opened_at` is 60
or more days in the past and whose `status` is still open gets `status: dismissed`. This
is `handler-contract.md`'s own explicit assignment ("dismissed by kb-dream's monthly
pass, not by the router itself") - purely a status flip on an existing record, never a new
proposal and never a deletion.

## Write-back

`state.cursors.kb-dream.last_registry_review_at` = now, whether or not any proposal was
raised.
