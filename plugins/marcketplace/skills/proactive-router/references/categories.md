# Category taxonomy and proposal candidates

This mirrors `../../../shared/handler-contract.md`'s category table exactly - read that
file first for the allowlist principle and the full dispatch/return contract. This file
adds the one thing that belongs to the router alone: the fixed candidate table a
three-unmapped-ticks proposal draws from. Never invent a candidate at run time; if a
category genuinely isn't here, the proposal names it `needs a new skill`.

## v1 taxonomy

| Category | Emoji | What the proposed line names | Handler v1 |
|---|---|---|---|
| `email` | ✉️ | Who to write to and what the message should accomplish (organise a call, follow up a lead, answer a question) | reply-draft `draft` |
| `ticket-reply` | 🎫 | An existing ticket/thread with an open question addressed to the user, or a fix concrete enough to raise as a ticket | action-sweep `targeted` |
| `ticket-idea` | 🎫 | A feature or capability worth its own ideas-board entry | idea-ticket `draft` (two-tick `file`) |
| `ticket-minor` | 🎫 [minor] | A small, non-urgent fix or tweak - worth a ticket, not urgent | action-sweep `targeted` small tier (two-tick `push`) |
| `kb-doc` | 📖 | A decision, process or piece of context worth capturing as a kb note | kb-note `capture` |
| `summarise` | ⭐📝 | The user's been handed something and the useful action is a summary to read | kb-note `capture` |
| `fyi` | ⭐ | Genuinely nothing to act on | none by design - tick closes, no sub-line |
| `meeting-followup` | 🗓️ | A commitment or action item surfaced in a recorded meeting | action-sweep `meeting` |
| `sweep-push` | ⬆️ | A drafted action-sweep item ready for its confirming push | action-sweep `push` |
| `kb-maintenance` | 🧹 | A kb curation task (conformance, supersession, link repair) | kb-dream `settle` |
| `running-behind` | ⏰ | An overdue item worth a closer look before flagging further | `inline:investigate` |
| `calendar` | 📅 | A scheduling action (book, move, decline a meeting) | none at v1 |
| `term` | 📘 | A word or acronym worth adding to the glossary | not dispatched - briefing promotes |

`fyi` and `calendar` both show no handler, and they are not the same case. `fyi` closes
the instant it's ticked - there was never anything to build. `calendar` has no handler
*yet*; a tick on it goes through the unmapped path below exactly like a freeform category
the user's own words produced, accumulating toward a proposal. Never collapse the two.

## Candidate table for the three-unmapped-ticks proposal

Only a category that can actually reach `unmapped_ticks >= 3` needs an entry: one with no
`state.registry[category].handler` set. Every v1-mapped category above is excluded here
by construction - a proposal only fires for a gap.

| Category | Candidate |
|---|---|
| `calendar` | needs a new skill (no shipped skill manages scheduling actions at v1) |
| any freeform category classified in the user's own words, not matching a row above | needs a new skill |

A proposal for a freeform category names the category text itself (as classified in step
3 of the flow) rather than a generic label - the point of the proposal is to say plainly
what's missing, not to paper over it.
