# kb-dream - design rationale (for editors; not loaded at runtime)

Carried from `source/vault-dream/HISTORY.md`, generalised past the one vault it names:

- Modelled on the idea of a periodic "dream" over a knowledge base - read the recent past
  and the accumulated whole, hand back a merged, de-contradicted, correctly filed version.
- An earlier run cost a `log.md` correction by trusting a stale snapshot of the type
  registry rather than the live file - hence "read the live file every run" in
  `kb-conventions.md`'s type-registry rule, and step 1 of this skill's own flow.
- Two broken links written by this skill once survived a later dream because nothing
  resolved links - hence the mandatory link pass and "resolve every link this run wrote"
  in `references/dream-note-format.md`.
- Several early passes re-surfaced the same items with no acknowledgement the user had
  cleared them - origin of the "Closed since last dream" section in
  `references/notification-shape.md`.
- "The human's file is the current one, always" - rule 4 of the five-rule contract.
- The Slack-DM-plus-reaction mechanism this skill's predecessor once used was retired in
  favour of the shared canvas and webhook pattern every sibling skill already used -
  fully generalised here into `surface-protocol.md` and `notify.md`, so this port carries
  no notification mechanics of its own beyond what those two files already define.

## 2026-09-22 port to marcketplace

Renamed from `vault-dream`. This is a three-way merge plus four absorbed obligations, per
the task brief - the widest-scoped port in the project. Built against
`source/vault-dream/SKILL.md` (base curation skill and its five-rule contract),
`source/_workspace-dream.SKILL.md` (memory consolidation: signal extraction and fold
proposals), `source/_workspace-wikilink-finder.SKILL.md` (the link pass), and read-only
cross-reference against `source/session-log/SKILL.md` (a sibling subagent is porting that
skill in this same wave; its dated `Sessions/` notes are this skill's own signal-extraction
source).

**Behaviours carried over, unchanged in substance:**
- The eight-pass curation table, the five-rule contract, the supersession mechanic (banner
  plus move to a recycle location, never a hard delete).
- The "who reads what" register split - the notification is the only reliably-read output,
  `log.md` and the dream note are write-once/read-rarely and optimise for completeness over
  prose.
- The repetition bar for failed writes (kept in this skill's own `references/`, per the
  task brief, rather than folded into a shared contract - it is specific to this skill's
  own write attempts during curation/extraction/link/registry/voice passes).
- Incremental-by-default, full-on-request-or-first-of-month mode split.
- Settle-carried-forward-canvas-items-before-appending, and the tick/edit/delete semantics
  now generalised into `surface-protocol.md` rather than restated here.

**Behaviours added, the four absorbed obligations plus the new handler mode:**
1. **Signal extraction** (`references/signal-extraction.md`) - generalises
   `_workspace-dream`'s Phase 2/3 from a transcript grep to a read over `session-log`'s own
   dated notes, since this plugin's session record already exists as distilled markdown,
   not raw transcripts. Auto-apply zone: `kb.paths.memory`, dated single-fact entries, the
   contradiction rule, source attribution.
2. **Fold proposals** (`references/fold-proposals.md`) - generalises `_workspace-dream`'s
   Phase 4 fold. Never applied, only proposed; the exact edit is drafted as a diff-shaped
   block in the dream note's Surfaced section.
3. **The link pass** (`references/link-pass.md`) - absorbs
   `_workspace-wikilink-finder`'s conventions (conservative bias, unambiguous-repoint-only,
   people/tickets/named-interactions scope) into `kb-conventions.md`'s link-style contract,
   generalised past wikilinks-only to honour `kb.link_style`.
4. **The monthly registry review** (`references/registry-review.md`) and **voice review**
   (`references/voice-review.md`) - new, built directly against `handler-contract.md`'s
   Learning section and `voice.md`'s Periodic review step respectively, since neither
   source skill covered them; this skill is where both are explicitly assigned.
5. **Reaping transient drafts** (`references/draft-reaping.md`) - new, built directly
   against `kb-conventions.md`'s Transient drafts section, which names this skill by name
   as the obligated reaper.
6. **Handler mode `settle`** - new. The hub dispatches one ticked `kb-maintenance` item per
   `handler-contract.md`'s category table; this is distinct from the skill's own scheduled
   settle-the-canvas step (flow step 10), which sweeps its whole Dream log/actions section
   on its own run. `settle` checks real state and either performs the item or names the one
   missing input; it never writes the surface itself.

**Decisions made where the source skills were silent:**
- **Two "settle" mechanisms, kept distinct.** `handler-contract.md` lists `kb-maintenance`
  as dispatching `kb-dream settle`, while `surface-protocol.md`'s own text (carried from
  vault-dream) already has this skill settling its *own* Dream log/actions section on every
  scheduled run. These are not the same thing: one is a per-item hub dispatch for a
  category found elsewhere on the surface, the other is this skill's own housekeeping of
  its own section. Kept both, named distinctly (flow step 10 vs `## Handler mode`), rather
  than collapsing them - collapsing would have made the hub's dispatch either redundant or
  silently different from what `handler-contract.md` describes.
- **Fold proposals are not written into `state.proposals`.** That array's `kind` enum
  (`mapping | suppression_lift`) belongs to `proactive-router`'s own mechanism, opened by
  the router and only dismissed by this skill. A fold proposal is a different kind of
  thing (a skill-behaviour edit, not a category-handler mapping) with nowhere to live in
  that schema, so it stays in the dream note and the canvas only - the same place every
  other Surfaced judgement call lives. See "Open questions" below; this may want its own
  state array in a later version.
- **The registry review's third proposal shape ("a skill-eval pass on a handler")** has the
  same problem for the same reason - no `kind` value fits it in `state.proposals`. Treated
  the same way: a canvas/dream-note-only proposal, not a `state.proposals` write.
- **The stale bound for a transient draft.** Neither `kb-conventions.md` nor the source
  skills state a number. Defaulted to 30 days, conservative and stated plainly in
  `references/draft-reaping.md`, rather than invented silently.
- **The link pass's "unless `profile.kb.link_pass` is `auto`" clause** (task brief item 3) has no
  matching profile key in `profile-schema.md`. Implemented as always-surface (the
  conservative default), never auto-add, with the "otherwise" branch unimplemented until a
  key exists - see the open question below rather than inventing one on this skill's own
  initiative, per `PORTING.md`'s explicit instruction not to invent profile keys.
- **`fold_status` on a memory entry** (`none | proposed | applied | not_needed`) is a field
  this skill adds to its own memory-entry frontmatter, not a new top-level profile or state
  key - `kb.frontmatter_required` still governs the six required keys; `fold_status` is an
  additional field this skill's own notes carry, the same way a Decision Record carries
  `decision_status` beyond the required six. No schema change needed.

**Nothing from either source skill was dropped.** `_workspace-dream`'s Mode B (interactive
session-scoped "what did you learn from this conversation") is out of scope for this port:
it is a different invocation shape (interactive, single-conversation) than anything in this
plugin's scheduled/dispatched model, and nothing in the task brief asks for it - noted here
so it isn't mistaken for an oversight. Its trigger-mechanics section (Stop hook,
SessionStart hook, local `.dream-pending` flag) is Claude Code-specific session-lifecycle
plumbing with no equivalent in this plugin's scheduling model (a cron-like scheduled fire),
so it was not ported; the plugin's own scheduling is out of this skill's scope entirely.

**Open questions for the orchestrator:**
- Should `state.proposals` gain a third `kind` (e.g. `skill_fold` or `skill_eval`) so fold
  proposals and skill-eval proposals can be tracked, tallied and dismissed the same
  mechanical way `mapping`/`suppression_lift` are, rather than living only in the dream
  note and canvas? As built, a fold proposal has no cross-run tracking beyond the memory
  entry's own `fold_status` field and the canvas item's own tick/edit/delete lifecycle,
  which works but doesn't get the 60-day dismissal mechanism `handler-contract.md` gives
  the other two kinds.
- A profile key for the link pass's "surface unless `profile.kb.link_pass` is `auto`" branch (e.g.
  `kb.link_pass_auto_add: bool`) - flagged rather than invented; the skill's default
  (always surface) is conservative and safe either way.
- A profile or `kb.conventions_file`-level value for the transient-draft stale bound, so
  the 30-day default this port assumed doesn't have to live only in this skill's own
  reference.
- `kb.paths.memory` and `kb.paths.drafts` both already exist in `profile-schema.md`'s
  `kb.paths.*` table, so no new path key was needed for either the auto-apply zone or the
  drafts obligation - confirmed rather than assumed, since getting this wrong would have
  meant inventing a key unnecessarily.

**Evals.** None of the three source skills (`vault-dream`, `_workspace-dream`,
`_workspace-wikilink-finder`) ship an `evals/` directory, so step 10 of `PORTING.md` has
nothing to carry forward or re-fictionalise - matching `kb-note`'s port, which is in the
same position. No evals were invented for this port.

**Friction against the shared contracts, reported per the task brief:**
- `kb-conventions.md`'s Transient drafts section states the reaping obligation clearly but
  gives no stale-bound number and no pointer to where one might be configured - see the
  decision and open question above.
- `handler-contract.md`'s category table row for `kb-maintenance` names the handler and
  mode (`kb-dream settle`) but doesn't distinguish it from a section-owning skill's own
  ordinary settle-the-section behaviour on its scheduled run, which `surface-protocol.md`
  separately requires of every delegate-section owner. The two are related but distinct;
  working out that they needed different homes (flow step 10 vs `## Handler mode`) took
  cross-reading both files rather than being stated in either.
- `voice.md`'s "Periodic review" step names `kb-dream`'s monthly voice review but the
  monthly cadence itself (first-full-dream-of-the-month) is only defined by this skill's
  own mode rule, inherited from the base curation skill's incremental/full split - nothing
  in `voice.md` or `handler-contract.md` states that the voice and registry reviews should
  share that same cadence rather than having their own. Assumed they should share it, since
  both are described as "monthly" with no other cadence source given.

## 2026-09-22 orchestrator: the three flagged gaps are now real keys

The build named three values it had to assume, and stated each assumption plainly rather
than burying it. All three are now defined, so the skill reads a key instead of a guess:

- `profile.kb.draft_stale_days`, default 30. The reaping obligation existed in the
  conventions with no number attached, which is how the build ended up choosing one.
- `profile.kb.link_pass`, `surface` or `auto`, default `surface`. The conservative bias was
  the intended behaviour; it just had no switch behind it.
- `state.proposals[].kind` gains `skill_fold` and `skill_eval`, so a behaviour proposal has
  somewhere to live instead of existing only as prose in the dream note.

The monthly cadence shared by the registry and voice reviews is now `budgets.kb-dream.reviews`.

On the fourth kind: `skill_fold` and `skill_eval` are proposals **about behaviour**, and a
tick on one means the user accepted the proposal, not that the system applied it. That
distinction is the propose-only half of this skill's safety split, and the state schema now
says so at the point where a future reader would otherwise have to infer it.

## 2026-09-22 orchestrator: the proposal loop was open at both ends

This skill raised behaviour proposals as prose in the dream note and a checklist line, but
wrote no record into `state.proposals`, because at build time that array's kind enum had no
value for them. The wave 4 gate added `skill_fold` and `skill_eval`, and `skill-eval`'s own
port then noticed the consequence: its unattended path is triggered by an accepted
`skill_eval` proposal, and nothing was ever writing one, so that path could never fire.

Both ends are now closed. This skill writes the record when it raises the proposal, and
`handler-contract.md` documents proposal-driven dispatch, including the `proposal_id` a
handler needs to mark the right proposal settled.

Writing the record is not applying the proposal, and the propose-only split is untouched.
The record says a change has been proposed; a tick says the user accepted it; a human still
makes a `skill_fold` edit. What changed is only that an accepted proposal is now findable.
