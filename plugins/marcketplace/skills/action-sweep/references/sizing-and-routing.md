# Sizing and routing

Apply this per new-ticket candidate (shape A in `ticket-draft-formats.md`). **Never
default to a tier when unsure - say so in the draft and ask instead.** A wrong routing
choice creates the wrong kind of tracker artefact, which is exactly the kind of mistake
worth a pause over. This refusal to guess is one of this skill's two hard stops; see
`SKILL.md`'s `## Ground rules`.

- **Small** -> routes to `tracker.default_parent_epic` as a `tracker.issue_types.story`.
  A scoped tweak to existing behaviour (a naming fix, a colour change, a truncation
  rule). Doesn't need an ideas-board entry first. Tagged `ticket-minor` on the surface.
- **Larger** -> routes to `ideas.project_key` as `ideas.issue_type`, with
  `ideas.area_field` set to `ideas.area_value`. A real feature idea that hasn't been
  scoped or validated - still has open questions that need discovery before it's
  buildable. Never set a roadmap-slot field here; that's a prioritisation call this skill
  never makes.
- **Larger + defined** -> routes to `tracker.project_key` as a new
  `tracker.issue_types.epic`, no parent. Already discovered and agreed, big enough to
  need its own epic with child stories under it. This skill creates the epic shell only;
  breaking it into child stories is a separate, later step, not automated here.

**If a candidate doesn't clearly fit one tier**, write it into the note under an
"Unclear routing" callout naming what's ambiguous, and do **not** post a delegate line
for it on the surface - an item with no delegate line can never be ticked into a push, so
this is the structural way "ask rather than guess" survives an unattended run with no one
to ask. It resolves only when the user edits the note directly to state a tier, or an
interactive run asks and gets an answer, at which point the next sweep picks it up as a
now-routable candidate.

## Modifications (shape B) never route through this table

A modification (new information for an existing item, not a new one) always becomes a
non-destructive comment on its source ticket - see `ticket-draft-formats.md`, "Ground
rules". It carries no tier and is never a candidate for the sizing question above.
