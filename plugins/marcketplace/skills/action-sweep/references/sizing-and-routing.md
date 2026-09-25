# Sizing and routing

Apply this per new-ticket candidate (shape A in `ticket-draft-formats.md`). **Never
default to a tier when unsure - say so in the draft and ask instead.** A wrong routing
choice creates the wrong kind of tracker artefact, which is exactly the kind of mistake
worth a pause over. This refusal to guess is one of this skill's two hard stops; see
`SKILL.md`'s `## Ground rules`.

- **Small** -> routes to `tracker.default_parent_epic` as a `tracker.issue_types.story`.
  A scoped tweak to existing behaviour (a naming fix, a colour change, a truncation
  rule). Doesn't need an ideas-board entry first. Category `ticket-minor` on the board.
- **Larger** -> routes to `ideas.project_key` as `ideas.issue_type`, with
  `ideas.area_field` set to `ideas.area_value`. A real feature idea that hasn't been
  scoped or validated - still has open questions that need discovery before it's
  buildable. Never set a roadmap-slot field here; that's a prioritisation call this skill
  never makes.
- **Larger + defined** -> routes to `tracker.project_key` as a new
  `tracker.issue_types.epic`, no parent. Already discovered and agreed, big enough to
  need its own epic with child stories under it. This skill creates the epic shell only;
  breaking it into child stories is a separate, later step, not automated here.

**If a candidate doesn't clearly fit one tier**, post it as a question with one option
per tier (see `output-format.md`), each option carrying the category that tier maps to
(`ticket-minor` for small, `ticket-reply` for the two larger tiers) and the tier named in
its text. Nothing is drafted until the user ticks one; the hub then dispatches `targeted`
with the chosen option as `item.text_as_ticked`, and the tier is read from it. This is the
structural way "ask rather than guess" survives an unattended run with no one to ask: an
option group can only ever resolve to one tier, chosen by the user.

## Where the action lands

| Find | Category | Handler on tick |
|---|---|---|
| A ticket to raise or a comment owed on an existing one | `ticket-reply` / `ticket-minor` | this skill, `targeted` |
| A commitment from a recorded meeting | `meeting-followup` | this skill, `meeting` |
| A chat thread or mention waiting on the user's reply | `chat-reply` | `reply-draft`, which drafts and never sends |
| Something only the user can do, with no artefact to draft | `to-do` | the hub's `inline:to-do`: one line on the user's own list |

One find, one action. A find that could be two things (a reply owed that also needs a
ticket) is posted as the more concrete one, and the draft names the other.

## Modifications (shape B) never route through this table

A modification (new information for an existing item, not a new one) always becomes a
non-destructive comment on its source ticket - see `ticket-draft-formats.md`, "Ground
rules". It carries no tier and is never a candidate for the sizing question above.
