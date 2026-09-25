# proactive-router - design rationale (for editors; not loaded at runtime)

- The chat user id was confirmed by asking the chat connector for its own authenticated
  identity (no user id passed) and matching the returned email. Treat as certain.
- The daily-sweep cadence (rather than firing per-reaction) exists because the reference
  chat workspace's workflow tooling has no native outbound-webhook step for a "reaction
  added" trigger; polling closes the gap with no extra app and no webhook/bearer-token
  plumbing, at the cost of up to a day's delay before a reaction shows up on the surface.
- Five searches per run (one per starter emoji, plus one `is:saved`) was chosen
  deliberately over a single combined query: the chat search surface's `hasmy:` and
  `is:saved` filters can't be OR'd into one call, and running them separately is what
  makes the dedupe-by-permalink step possible at all.
- `is:saved` is a standing part of the search surface, not a fallback for when the emoji
  searches come back empty - the bug this run once hit (17 on-theme saved items discarded
  as "not a `hasmy:` match") is exactly what the dedupe-and-log-once rule in the flow
  exists to prevent.
- The `summarise` / `fyi` split (references/classification.md) is new in this port: the
  source skill folded both under one star emoji. Splitting them gives `summarise` an
  actual handler instead of leaving "I need the gist" and "there is nothing here"
  indistinguishable on the surface.

## 2026-09-22 port to marcketplace

Renamed from: `proactive-router` (unchanged name; the skill itself is the same, its role
in the system is what changed).

**Behaviours kept.** The daily chat sweep, the five-search budget, the allowlist
principle verbatim, the follow-up-before-fyi check, the saved-item dedupe rule, the
worked-examples calibration table (now `references/classification.md`).

**Behaviours added (the hub role).** Reading every delegate section, not just Proactive
opportunities, and classifying each line's tick/edit/delete state against
`state.items` text hashes. Dispatching one subagent per ticked, mapped item, per
`../../shared/handler-contract.md`'s payload and return contract. Writing report
sub-lines and `needs your tick` follow-up lines into sections this skill does not own
(the surface protocol's one carve-out). The two-tick flow for irreversible handler modes.
Tally, suppression, pattern-blocking and the three-unmapped-ticks proposal mechanism.
`references/categories.md`'s fixed candidate table for proposals.

**Behaviours dropped.** None outright - the source skill's log-only v1 scope ("no handler
exists yet for any category, so nothing beyond the canvas checkbox happens") is
superseded by the hub role rather than removed; a category with no handler still lands on
the surface exactly as before, it just now also accumulates toward a proposal instead of
sitting inert forever.

**Decisions made where the source and shared references were silent.**

- The source only ever wrote to one section (Proactive opportunities) and never
  interpreted a tick itself - promotion on tick was explicitly deferred to a future
  `/briefing` pass. This port makes the router that future pass's dispatch half. Where
  the source was silent on exact mechanics (which items to dispatch first when several
  are ticked at once), this port dispatches oldest-first, since nothing in
  `handler-contract.md` specifies an order and oldest-first is the least surprising
  default for "which three ticks fire this run".
- Where a dispatched handler needs a tool category this skill's own `## Needs` doesn't
  list (email, tracker, kb, etc., depending which handler is being dispatched),
  `references/dispatch.md` resolves it on demand via the same mechanism onboarding step 4
  uses, caching into `state.machines` like any other resolution. `onboarding.md` and
  `tool-capabilities.md` describe resolution as driven by a skill's own `## Needs`; the
  hub's needs can't enumerate every handler's categories without effectively duplicating
  the whole roster, so this port treats "resolve on demand for the handler about to run"
  as the reading that keeps both documents true at once. Flagged for the orchestrator to
  confirm.
- `ticket-reply` (action-sweep `targeted`) is used both for "an existing ticket has an
  unanswered question" and for "a bug's fix is concrete enough to raise as a new ticket"
  - the source drew these as two different rows in its intent table but
  `handler-contract.md`'s v1 taxonomy only has one ticket-needing-a-reply category that
  isn't `ticket-idea` (feature/ideas-board) or `ticket-minor` (small/non-urgent). Read
  `ticket-reply` as covering both until a v2 taxonomy splits them.

## Open questions for the orchestrator

- Confirm the tool-category resolution-on-demand reading above, or say explicitly that a
  handler's needed categories should instead be pre-declared somewhere the hub can read
  without loading that handler's `SKILL.md` (its own `HISTORY.md`? a manifest file?).
- `handler-contract.md`'s dispatch section says the hub's run is "roughly 60 to 90k input
  tokens" - that estimate assumed a hub that only read its own section. Reading four
  delegate sections plus dispatching may run higher; worth re-measuring after the first
  live dry run rather than tuning the budget number blind here.
- No skill in the current 13-skill roster owns calendar actions. `references/
  categories.md` names this plainly ("needs a new skill") rather than forcing `calendar`
  onto an existing handler that doesn't fit - flagging in case a future wave wants to
  fold it into `action-sweep` instead of shipping a dedicated skill.

## 2026-09-22 orchestrator correction: summarise dispatches, it does not run inline

The port implemented `summarise` as `inline:summarise`, with the hub writing a note into
the knowledge base from its own context off a single tick. The port flagged this itself as
the one write-adjacent path that did not come back from a dispatched handler, which is what
made it cheap to catch.

Changed so `summarise` dispatches to `kb-note` in `capture` mode. The reasoning is
privilege, not tidiness. The hub runs unattended, on a schedule, and is the component that
decides what work happens; every store it can write to is a store a misclassification can
corrupt. It now writes to exactly one thing, the surface, and every other write happens
inside a handler the user's tick selected. `shared/handler-contract.md` now states the rule
generally: an inline action never writes outside the surface, and an action whose output is
a durable artefact is a dispatch. `inline:investigate` stays inline because it only reads
and reports.

The single-tick question was never the problem. A knowledge-base write is additive and
reversible, so it does not need the two-tick flow, exactly as `kb-note` argues for its own
`capture` mode. What mattered was which component held the write access.

## 2026-09-25 canvas redesign (1.1.0): every tick means yes, do it

The board moved to five sections and one tick rule, and this skill became the only thing
that acts on a tick. Why: under the old acknowledge/delegate split, five sections closed
on a tick without anything happening, idea decisions and wireframe reactions were never
recorded, and edits were only read in two sections. Now every line in To-do, For you and
Ideas is read against `state.items`, and a tick anywhere is dispatched, performed inline,
or resolved as an option pick. Inline actions gained `promote` (terms), `requeue` (a parked
idea that moved) and `to-do`, all writing only to the surface and the state document.
`shc:` ticks are queued rather than dispatched, because `skill-eval` stays manual. `fyi`
left the board: it is recorded in `runs.proactive-router.fyi` for the briefing message,
since a line with nothing to do had no business asking for a tick. Option groups: one
tick proceeds, two get `blocked · pick one`, an edited option is a variation of that
option. A line the user adds inside an idea block takes the idea as context. Six eval
cases were added for these paths; their dispatch graders accept a documented
"could not resolve a tool category" sub-line because the mocks cover chat and state only.
The sweep sources are unchanged.
