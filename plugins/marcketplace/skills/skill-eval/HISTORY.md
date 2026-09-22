# History

## 2026-09-22 port to marcketplace

Ported from `source/skill-eval/SKILL.md`. The source was already close to generic - almost
no org-specific content - so most of the work was fitting it to this plugin's reality
(installed skills, proposal consumption, profile-driven model tier) rather than stripping
literals.

**Renamed from:** `skill-eval` (unchanged).

**Behaviours dropped, and why:**

- The source's own packaging step (`python -m scripts.package_skill`, `SendUserFile`) is
  named generically here as "this session's file-sending capability" per the task brief -
  this plugin does not assume a specific packaging tool or send mechanism exists in every
  running environment.
- The handoff target for building from scratch, test suites and description optimisation
  changed from the source's own skill-building tool to Claude's own skill-creator, per the
  task brief - this plugin ships no skill-builder of its own.

**Behaviours added:**

- **A second entry point.** The source only ever ran interactively, triggered by a human's
  reaction. This port adds an unattended, proposal-driven entry point that runs when the
  hub dispatches an accepted `skill_eval` proposal from `state.proposals` (raised by
  kb-dream's monthly registry review). See `references/proposal-driven-eval.md`.
- **A `## Handler mode` heading**, since the proposal-driven path is now a hub dispatch.
  Mode `eval`, returning the standard handler contract JSON; never `needs_confirmation`
  since a knowledge-base draft is additive and reversible.
- **Never writes the installed skill.** The source's Step 3 packaged and sent the revision
  for the user to save themselves, which already matched "never writes the install cache."
  This port states the rule explicitly and up front, since in this plugin the skill being
  amended may live in a read-only installed cache whose source repository is not even
  checked out on the machine - there is no ambiguity to resolve here, only a rule to make
  louder than the source needed to.
- **Model tier from the profile.** `budgets.models.critic` replaces the source's hardcoded
  `model: "opus"`, per `../../shared/model-tiers.md` - including stating a downgrade
  plainly rather than doing it silently, which the source already did in spirit ("If opus
  is unavailable, fall back...") and this port carries forward unchanged in substance.

**Decisions made where the source and the shared references were silent:**

- **What the unattended path's "feedback" is, absent a human.** Built from
  `state.tally.<category>` (the edit-vs-ticked ratio that earned the proposal) plus a
  small sample of matching `state.voice_edits` entries. Composed as observation ("N of M
  sampled edits show X"), never fabricated as a quoted human sentence - see
  `references/proposal-driven-eval.md`'s "Assembling the eval."
- **A thin-evidence stop for the unattended path.** Where the interactive path can ask "is
  this a one-off?", the unattended path cannot ask anyone. Rather than guess, it returns
  `partial` with "insufficient signal to synthesise" and leaves the proposal open for the
  next registry review. This is new; the source had no unattended path to need it.
- **Where the unattended proposal lands.** Written as a transient draft under
  `profile.kb.paths.drafts` (never the inbox), following `kb-note`'s frontmatter shape and
  `kb-conventions.md`'s transient-drafts contract (`status: draft`, `supersedes_on:`
  naming acceptance or rejection as the superseding event).

**Open questions for the orchestrator:**

- `../../shared/handler-contract.md`'s v1 category taxonomy table has no row for this
  dispatch path. Every other handler is reached because the router classified a message
  into a known category; this one is reached because a `state.proposals` entry was ticked
  under kb-dream's own Dream log/actions section. The `## Handler mode` heading in
  `SKILL.md` describes the mode's contract on the assumption that the hub dispatches it
  directly off the proposal tick (the same way it already writes report sub-lines into
  sections it doesn't own, per `../../shared/surface-protocol.md`'s "one carve-out"), but
  nothing in the shared contracts states that dispatch path explicitly for a
  `state.proposals` tick as opposed to a `state.items` tick. Flagging rather than editing
  `handler-contract.md`, which is frozen for this port.
- kb-dream's own `HISTORY.md` (read as part of this port's research, not edited) notes that
  its `references/registry-review.md` does not currently write `skill_eval` proposals into
  `state.proposals` - it treats the whole third proposal shape as canvas/dream-note-only,
  flagging the same `kind`-enum gap this port is now downstream of. `state-schema.md`
  already lists `skill_eval` in the `kind` enum, so this port assumes kb-dream's write path
  will be completed (by kb-dream's own port or a later pass) rather than inventing a
  substitute mechanism here. If kb-dream ships without that write path, this skill's
  unattended entry point has nothing to be dispatched by until that gap closes.
- No new profile or state key was needed. `budgets.models.critic`, `kb.paths.drafts`,
  `kb.conventions_file`, `kb.types_registry`, `kb.frontmatter_required`, `kb.link_style`,
  `kb.paths.log`, `state.proposals`, `state.tally`, and `state.voice_edits` all already
  exist in the shared schemas.

**Friction against the shared contracts, reported per the task brief:**

- `state-schema.md`'s proposal-kinds table gives `skill_eval` one line ("A handler's
  output keeps being edited; run skill-eval over it") but says nothing about the payload
  shape a dispatch built from this proposal carries - in particular, whether
  `item.text_as_ticked` is expected to hold the proposal's `candidate` and `category`
  verbatim, or some other rendering. This port assumes the former (the simplest reading)
  and states it in `SKILL.md`'s Handler mode section, but a future reader building the
  hub's own dispatch-from-proposals logic should confirm this against whatever that build
  actually produces.
- `../../shared/handler-contract.md`'s payload table does not include a `state.proposals`
  entry's own `id` field anywhere in the dispatch payload, which this skill would want in
  order to write `status: settled` (or similar) back onto the specific proposal once its
  draft is written - the contract as written gives no field to carry that id through. Not
  invented here; flagged as a gap the orchestrator may want to close if proposal
  lifecycle tracking (open -> dispatched -> settled) is meant to be end to end.
