# Acceptance criteria

Carried over from `source/cloud-idea-deep-dive/SKILL.md`'s own "Acceptance criteria" section
(there is no separate `evals/` directory for this skill to re-fictionalise instead). Useful as
a manual review checklist until this skill gets real eval cases; terms generalised to this
port's vocabulary (idea key, circle names, `references/` files) but the substance is
unchanged.

**Setup**

AC1: The very first action is checking for an existing note, followed immediately by the
appropriate fetch (full issue on a fresh pass, delta on a resume); budget and
codebase-availability setup happen identically on both paths, before the loop starts; an
unspecified budget defaults to `budgets.idea-deep-dive.loop_budget`.
AC2: Open-questions vs. decisions-for-you split holds; a decision never enters the loop or
gets marked stuck.

**Circles and the batch sweep**

AC3: Circles `kb` and `people` run once each, combined across every seeded question, before
the per-question loop, as an explicitly capped and consistently-described allowance (one
query per source, four sources, logged); resolved items do not count against the loop budget.
AC4: A survivor begins the loop at whichever of `code`/`web` actually applies to it, with a
stated tiebreak when both plausibly apply (`code` before `web`) and no forced either/or when
a question's cues genuinely span both; a freshly spawned question begins at `kb` - with no
step-number/circle collision anywhere in the text.
AC5: Circle `code` only for feasibility-shaped questions, via `codebase.access` at
`codebase.path`, checked via its availability status once per run.
AC6: Circle `web` only for market-shaped questions, always named plus sourced; a search that
runs out without a citable source counts as unresolved, not a written-down impression.
AC7: Per-circle caps (`circle_caps.{kb,people,code,web}`, plus the sweep's 1-per-source) hold,
each scoped to one question's one attempt at that circle; the sole exception (a deliberate
reopen) is itself bounded - at most once per question per circle, capped below the circle's
own allowance - so no question's total at one circle is ever unbounded; every count actually
used is recorded in the log.

**Spawned questions**

AC8: A spawned question is caught whether or not the question that surfaced it resolves in
the same pass, then deduped, then classified, in that order, before being routed anywhere.
AC9: BLOCKING jumps the queue and parks the parent as PENDING; when the child resolves, the
parent either resolves immediately (if the child's answer settles it) or re-enters and
continues only into circles it had not yet tried (never re-attempting an exhausted one),
costing its own loop either way; INCIDENTAL goes to the back.
AC10: Deduped against every existing pile - seeded, queued, resolved, stuck, PENDING,
decisions-for-you - before being added.
AC11: A BLOCKING chain that would exceed `depth_cap` halts the run (the same halt as any
stuck question), with the capped question marked stuck and every PENDING ancestor in the
chain cascaded to stuck too - and the write-up/surface item can render every item in that
cascade, not just one.
AC12: Every question taken off the queue costs exactly one loop; the budget is checked before
a question is taken, never charged to one left uninvestigated.

**Stopping and honesty**

AC13: Exactly three exit conditions - complete and loop-limit (checked before taking a
question, in that order), and stuck (discovered mid-investigation, overriding either of the
other two the instant it is found) - with no internal contradiction between them and no
mechanism that can manufacture a spurious stuck exit from an ordinary, bounded re-entry.
AC14: A stuck write-up names the specific missing input and exactly what was checked
(circles, search counts, checked-vs-unavailable), never a vague "could not resolve".
AC15: "Could not check" and "checked, found nothing" stay distinct in the log AND the surface
item (when the end state produces one).

**Runtime**

AC16: Every search - the upfront sweep and every per-question search across all four circles
- is dispatched as a subagent returning a compact result, stated as a complete,
non-contradictory rule; only Step 0's issue/note reads and the final write-up are done
directly by the primary model.

**Write-up and delivery**

AC17: Updates the existing note in place (with a stated tiebreak if more than one matches);
never creates a second note for the same idea.
AC18: Resolved answers land in a "Resolved findings" section (not just a log line); "Open
questions" and "Decisions for you" are separate sections; a "Deep-dive log" records loop
count, per-question circle and search count (sweep included), and spawn lineage.
AC19: Surface item (when the end state is actionable) uses the shared section, is
append-only (never ticks or removes another run's item), and its content is matched to end
status; notify fires with the correct payload every run; the couldn't-check/found-nothing
distinction survives into a stuck item's wording when relevant.
AC20: A resume is detected from the note's `deep_dive_status` field, checked before any
issue-fetch call is made; prior resolved findings and run state (queue, chain-depth,
exhausted circles, pending relationships) are read as given, not re-derived - including which
circles a carried-forward question starts at, which is never reset to `kb` just because the
run is new; only a delta fetch is made, triaged before entering the loop; budget and
codebase-availability setup both run identically on a resume as on a fresh pass.

**Guardrails**

AC21: No writes to the ideas board at all (labels, comments, transitions, edits) unless the
user explicitly asks in that run - no confusing exception.
AC22: The codebase connector's preferred access path is stated, with its fallback (if any)
explicitly scoped to what it does and does not substitute for.
