# Proposal-driven eval

Full detail for the unattended entry point: the hub has dispatched a ticked `skill_eval`
proposal (`state.proposals[].kind: skill_eval`, raised by kb-dream's monthly registry
review per `../../../shared/state-schema.md`'s "Proposal kinds"). There is no free-form
feedback and no one to check in with, so the eval has to be assembled from what the state
document already knows rather than asked for.

## Assembling the eval

1. **Read the proposal.** `item.text_as_ticked` carries the proposal's `candidate` (the
   skill whose output keeps being edited) and `category` (the taxonomy category from
   `../../../shared/handler-contract.md` its dispatches fall under). These name the target
   skill for Step 1 of the main flow.
2. **Pull the tally.** `state.tally.<category>`: `edited` against `ticked` is the whole
   evidence base for "the output keeps being edited" - this is what earned the proposal in
   the first place, so it is never re-derived from scratch, only read.
3. **Pull matching voice edits.** Scan `state.voice_edits` (ring buffer, max 30) for
   entries whose `tag` traces back to a dispatch of `candidate`. Each entry names a
   register and points at what was drafted versus what the user actually sent or kept -
   this is the closest thing to a before/after pair this path has, and it stands in for
   the concrete rewrite a human would otherwise paste in Step 1.
4. **Read a small sample of the actual edits**, where the entries' refs are still
   reachable (a sent reply, a kept note). Two or three is enough - this is evidence
   gathering, not a research pass, and the budget in `SKILL.md` reflects that.

## The thin-evidence stop

If the tally shows a high edit rate but the sampled edits don't converge on anything
specific - different registers, different sections, no repeated shape - there is no
concrete change to ground, only a vague sense that something is off. Do not synthesise
against a guess: this is unattended, and a bad guess written into a skill's `SKILL.md`
under Step 6's "don't inflate" rule is worse than no change at all. Stop here and return
`partial` with `report_line: "insufficient signal to synthesise · <category> edit rate up,
no consistent pattern in the sample · <link to tally>"` (`../../../shared/handler-contract.md`'s
200-character cap applies). The proposal stays open for the next registry review to
re-evaluate with more data.

## Where a pattern does converge

Compose the "feedback" input to Step 3's synthesis subagent from what the sample actually
shows - phrased as observation, not as if a human wrote it: "N of M sampled edits to the
`<register>` register shorten the opening line" reads honestly; putting words in the
user's mouth as a fabricated quote does not. Everything else in Step 3 runs unchanged: the
same rules, the same subagent brief, the same discipline against inflating a small pattern
into a large rewrite.

## No checkpoint, so extra caution on scope

Step 4's "Did I get this right?" checkpoint cannot run unattended, which removes the one
safety net the interactive path has against an over-read. Two things compensate:

- **Cap changes to what the sample directly shows.** Where the interactive path can ask
  "is this a one-off?", this path has no one to ask - so a pattern seen in fewer than two
  of the sampled edits is named as a possible one-off in the change summary rather than
  written into the skill as a rule.
- **The draft is a proposal, not an application.** Nothing here reaches the installed
  skill or changes behaviour on its own; the draft note under `profile.kb.paths.drafts`
  is exactly as reversible as any other unread proposal, and the user reviews it whenever
  they next open the drafts folder or the surfaced report line.

## Writing the draft note

Same shape as `../../kb-note/references/note-template.md`'s frontmatter contract, adapted:
`type` per the live `profile.kb.types_registry` (closest match to a proposal/draft-shaped
note; register one if genuinely nothing fits, per
`../../../shared/kb-conventions.md`'s type-registry rule), `status: draft`,
`generated: {by: skill-eval, at: <ISO 8601>}`, plus a `supersedes_on:` line naming the
event that makes the draft obsolete ("proposal accepted or rejected"). Body: the change
summary first (grouped changes, the evidence each answers, before/after where the sample
showed one), then the complete revised `SKILL.md` in a fenced block. Index and log lines
per `../../../shared/kb-conventions.md`'s maintenance contract, filed under
`profile.kb.paths.drafts`, never the inbox - this is a transient artefact, not curated
knowledge.
