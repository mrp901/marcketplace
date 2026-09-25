# Fold proposals

This is the safety split that matters most in this skill. Signal extraction writes freely
into `kb.paths.memory` - that is the auto-apply zone, and nothing there steers behaviour.
The moment a settled correction would change what another skill *does*, this skill stops
writing and starts proposing.

## When a correction is "settled"

A memory entry is a fold candidate once it is a **correction** (not a preference or a
decision - those may also be worth folding, but the correction shape is the strongest
signal something a skill got wrong needs fixing) and it has stood for at least one prior
dream cycle without being itself contradicted. A correction seen for the first time this
run is written to memory and left `fold_status: none`; it becomes a candidate on the
*next* dream that finds it still standing. This one-cycle wait is deliberate: a correction
that gets re-corrected within a day should never turn into a skill-file edit proposal for
the wrong version of the fact.

## Identifying the governing skill

For each candidate, name the skill whose output that correction constrains - the skill
whose `SKILL.md`, `references/`, or profile-driven rule produced the wrong behaviour in
the first place. Evidence for this comes from the memory entry's own `source` (which
session, doing what) and, where the correction concerns a category this plugin already
taxonomises, `handler-contract.md`'s category table. Never guess past what the source
supports - if the governing skill genuinely isn't identifiable from the evidence in hand,
leave `fold_status: none` and surface the correction itself as a cross-session insight
(pass 7) instead of forcing a fold proposal onto the wrong target.

## Drafting the proposal

The proposal is the exact edit, not a description of one: a diff-shaped block naming the
target file, the line or section it touches, and the replacement text - written so a human
(or a later `skill-eval` pass) could apply it verbatim. It goes in the dream note's
Surfaced section and, if it is actionable in one tick, a matching `dream:` line in For
you.

```markdown
- [ ] **Fold: `<skill>/SKILL.md` <section>.** <one clause of what's wrong now>.
  Proposed edit:
  > <the exact replacement line or block>
  Source: [<memory entry>](../<path>.md), settled since <date>.
```

## Never applied, only proposed

This skill never edits another skill's `SKILL.md`, `references/`, or any profile/state key
that changes behaviour, under any circumstance, including an unattended run and including
a ticked board line - the `settle` handler mode (see `SKILL.md`'s `## Handler mode`)
checks whether the edit has already landed by other means and updates the memory entry's
`fold_status` to `applied` if so, but it does not perform the edit itself. Tick the fold
proposal only tells `kb-dream` to check again next pass, never to write the change.
