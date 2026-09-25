# The qualifying gate

## Why this exists

The gate is what stops this skill from spending a run on an idea outside the product this
install is scoped to. It is generalised from a single hardcoded rule in the source skill
onto `profile.ideas.qualifiers`: a first-match list of qualifier tests, evaluated in order,
against the candidate fields the search already returned. Do not fetch a candidate in full
to evaluate the gate - verify from the search result's own fields only; the full fetch
(`ideas: get issue`) happens once, for the winner, in Step 2.

## The default qualifier list, worked

`profile.ideas.qualifiers` default: `[summary_has_product_tag, area_field_has_area_value,
assignee_is_me]`. Walk the candidates newest-first; for each one, test the qualifiers in
list order and stop at the first match:

1. **`summary_has_product_tag`** - the idea's summary contains the literal
   `profile.org.product_tag` string (e.g. `[Cloud]`), not a loose word match anywhere in
   the text. A summary that merely mentions the product area in prose without the tag does
   not pass this test.
2. **`area_field_has_area_value`** - `profile.ideas.area_field` (a multi-value field)
   includes `profile.ideas.area_value` among its values. Check every value the field
   carries, not just the first.
3. **`assignee_is_me`** - the idea is assigned to the running user. An idea assigned to the
   user qualifies whatever its stated topic is - their own ideas are always in scope for a
   first pass.

A candidate that fails every qualifier in the list is skipped silently: no note, no label,
no surface line, no notification, and no comment recorded anywhere. Move to the next
candidate. This applies even when the skipped candidate looks interesting or well-formed -
looking interesting is not a qualifier.

## Requeued ideas come first

Before the gate is evaluated at all, `state.ideas.<key>.requeue_scout: true` names an
idea the user asked to refresh (a tick on its `/r` line). That idea is this run's pick
regardless of labels or qualifiers; the note is refreshed in place and the flag cleared.
Two or more requeued: oldest requeue first, one per run.

## Roadmap is reported, never a qualifier

`profile.ideas.roadmap_field` (a scheduling slot - "when", not "what") is read and may be
quoted in the note or a research lead, but it is never added to the qualifier list and
never substitutes for one. This is deliberate, not an oversight: an earlier version of this
gate included a roadmap-slot clause (any idea already scheduled qualified regardless of
topic), and it was removed after producing two consecutive off-domain picks - an idea about
integrations, and one about workflows and reporting, neither in this install's product
scope. The lesson: a roadmap slot says an idea is *scheduled*, not that it is *this
product's*, and conflating the two wastes a run on the wrong thing. Never reintroduce
roadmap as a qualifying test, however tempting it looks as a proxy for "worth investigating
next."

The roadmap watch (`SKILL.md` step 1) is not a qualifier either. It only ever looks at
ideas already labelled investigated, and its only output is a `/r` question on the board:
"this idea left a parked slot, refresh the research?" The user's tick, not the slot,
requeues the idea.

## No flag-and-proceed for a non-qualifying candidate

An earlier version of this skill also tried a softer failure mode: when a candidate didn't
clearly qualify, work it up anyway and flag the result as possibly off-domain, rather than
skip it outright. That behaviour was deliberately deleted. A flagged off-domain note still
costs the user a read to discover it doesn't matter, and a note that might not matter is
worse than no note at all - it looks like real output while quietly wasting the one thing
this skill is supposed to protect, the user's attention. The only two outcomes for a
candidate are: it qualifies, and gets the full treatment: or it doesn't, and is skipped
with nothing written anywhere. There is no third, softer outcome.

## Fast-fail

Any of the following stops the run before anything is written, with nothing beyond the
session's own output:

- No candidate in the search results passes any qualifier.
- The search itself returns no results at all.
- A field the gate needs to evaluate a qualifier is missing or empty from the search
  result for every remaining candidate, so the gate cannot be evaluated at all.

**"Cannot confirm" is a fail, not a maybe.** A candidate whose fields don't clearly say yes
or no to a qualifier is treated exactly like a candidate that failed it - never assumed to
pass because the evidence is ambiguous. No note, no label, no surface line, no
notification follows a fast-fail; this run's outcome is recorded in `state.runs[idea-scout]`
only.
