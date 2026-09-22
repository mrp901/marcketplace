# History

## 2026-09-22 port to marcketplace

Ported from `source/cloud-idea-ticket/SKILL.md`, renamed `cloud-idea-ticket` ->
`idea-ticket`. This is the wave's first port to also serve as a hub handler while keeping
its original interactive, directly-invoked path alive - see the design decisions below for
how the two share one confirmation gate.

**Behaviours dropped and why:**

- The fixed tracker cloud id (see `profiles/extract/idea-ticket.local.md`) and the org name
  spelled out inline are gone from the body; both are now `profile.tracker.cloud_id` and
  `profile.org.name`, resolved once at onboarding per `../../shared/onboarding.md` and
  `../../shared/profile-schema.md`'s discovery procedures, with the fallback-via-discovery
  language folded into that same mechanism rather than stated inline here.
- The three named voice-reference tickets from the source's Step 3 are dropped as hardcoded
  anchors - see "Voice calibration" below for what replaced them.
- Concrete tool names (`mcp__Atlassian_Rovo__searchJiraIssuesUsingJql`,
  `mcp__Atlassian_Rovo__createJiraIssue`, `getAccessibleAtlassianResources`) are gone in
  favour of the `ideas: search issues (JQL)` / `ideas: create issue` category verbs from
  `../../shared/tool-capabilities.md`.
- The explicit "model: opus" literal is now `profile.budgets.models.critic`, with the
  unavailable-tier behaviour pointed at `../../shared/model-tiers.md` rather than restated.

**Behaviours added:**

- A `## Handler mode` heading with two modes (`draft`, `file`), matching
  `../../shared/handler-contract.md`'s `ticket-idea` row and its two-tick irreversible-write
  rule. `draft` never files; `file` is the only mode permitted to create the ticket, exactly
  as the source's own Step 5/Step 6 split already implied, now made explicit and returning
  the shared JSON contract.
- Voice matching via `../../shared/voice.md`'s `ticket_prose` register in place of the
  source's hand-picked reference tickets, with the AI-tells specifics from Step 3 and the
  audit rubric's voice criterion carried into `references/ticket-format.md` verbatim rather
  than folded into the generic shared avoid-list, per the task brief's instruction to keep
  the source's more concrete list.
- An explicit statement in `## Handler mode` that the hub-dispatch path (`draft` then
  `file`, gated by the hub's two ticks) and the direct-invocation path (one continuous
  conversation, gated by the user's explicit approval in place of a second tick) run the
  identical Steps 1-7 and differ only in who delivers the confirmation gate. This is new:
  the source never had a hub to reconcile against, so the shared-pipeline framing did not
  need writing out before.

**Decisions made where the source skill was silent:**

- **Voice calibration key.** The task brief names `profile.user.voice_calibration` as the
  key that carries reference tickets where the user has personally set the calibration.
  This key does not appear anywhere in `../../shared/profile-schema.md`'s table. Per
  `PORTING.md`'s "Inventing profile keys" rule, it is used in `SKILL.md` and
  `references/ticket-format.md` exactly as the brief specified, marked optional in `##
  Needs`, and flagged here rather than added to the schema myself - the orchestrator should
  decide whether it belongs in `profile-schema.md` proper (most likely alongside
  `voice.registers`, or as a nested field under `voice` rather than `user`) or whether it
  should be dropped in favour of the register mechanism alone.
- **No `profile.budgets.idea-ticket` key exists.** Every other budgeted skill
  (`briefing`, `proactive-router`, `action-sweep`, `idea-scout`, `idea-deep-dive`,
  `idea-wireframe`, `kb-dream`) has a `budgets.<skill>` subtree in
  `profiles/example.md` and `profile-schema.md`. `idea-ticket` has none. Rather than
  inventing one, this port states its caps as fixed values in `## Budget` (one or two
  duplicate-check searches, one optional vault check, two revision cycles, one create
  call) and flags the gap here. A future `budgets.idea-ticket` key, if the orchestrator
  adds one, would likely hold `{duplicate_searches: 2, revision_cycles: 2}`.
- **`web: search` in `## Needs`.** `../../shared/tool-capabilities.md`'s category table
  lists `idea-ticket` as a user of `web: search`, but the source skill explicitly forbids
  going and researching a vendor ("What's out of scope is *going and researching it*").
  Resolved by listing `web` as optional and capping it at "at most one confirming call if a
  named vendor fact is genuinely in doubt" - consistent with the source's actual
  discipline (vendor anchors from existing knowledge only) while not silently dropping a
  category the shared reference says this skill uses. Flagged for the orchestrator in case
  the intent was something else entirely (e.g. a future capability this skill hasn't grown
  into yet).
- **Draft artefact location for the `draft` mode.** `../../shared/handler-contract.md`'s
  payload shape says a draft-only handler's `output_location` "takes nothing; the draft's
  location is the handler's own business and is reported in `artefacts`" - so this skill
  returns the drafted title+body as an inline artefact reference rather than writing it
  anywhere durable (no kb write, no tracker draft object exists to point at). This mirrors
  `kb-note`'s own resolution of an underspecified `output_location` contract point.

**Open questions for the orchestrator:**

- `profile.user.voice_calibration` and `profile.budgets.idea-ticket` (above) both need a
  real decision, not a guess by this port.
- The `web: search` category's exact scope for this skill (above) - confirm or correct the
  reading taken here.
- `handler-contract.md`'s category table lists `idea-ticket` handler mode as `draft
  (two-tick to file)` - matching what was built - but does not say what `item.idea_key`
  (present in the general dispatch payload shape) means for a `ticket-idea` item that by
  definition has no tracker key yet at `draft` time. This skill ignores `item.idea_key` on
  `draft` and reads it only on `file`, where the hub's confirming line would carry the
  draft's own reference as the effective idea_key equivalent - not stated anywhere in the
  contract, inferred here.
