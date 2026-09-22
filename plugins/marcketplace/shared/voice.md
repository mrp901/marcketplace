# Voice

A new capability with no single direct source - it generalises the discipline `source/cloud-idea-ticket/SKILL.md` applies by hand (calibrated against three named prior tickets, a "Cut the AI tells" list, an independent audit) into a standing, compounding mechanism every drafting skill shares.

## Purpose

`reply-draft`, `kb-note` and `idea-ticket` produce prose the user is meant to read as their own - a draft they can send or file with light editing, not one that announces itself as machine-written. Voice matching is not a style guideline layered on afterwards; it is load-bearing for whether the draft is usable at all. Every handler that drafts prose lists `voice` in its `## Needs`.

## Structure in the knowledge base

Rooted at `profile.kb.paths.voice`:

| File | Contents |
|---|---|
| `Voice/index.md` | Pointer index into the register notes below, no frontmatter |
| `Voice/teammate-chat.md` | Register note - see shape below |
| `Voice/exec-update.md` | Register note |
| `Voice/customer-facing.md` | Register note |
| `Voice/ticket-prose.md` | Register note |
| `Voice/ai-patterns-to-avoid.md` | One shared list, not per-register |
| `Voice/edits-ledger.md` | Dated before/after pairs |

`profile.voice.registers` names the four registers above; a kb may add a register by extending that list and creating the matching note, following the same shape.

**Each register note** carries:
- 3 to 5 verbatim exemplars, each with a source reference (the message, email or note it came from)
- 8 to 12 observed traits: sentence length, typical openers, sign-offs, punctuation habits, words used and words avoided, list style, hedging level
- A register-specific "never" list, distinct from the shared avoid-list below (e.g. a customer-facing register might ban an internal codename the teammate-chat register uses freely)

## The AI-patterns-to-avoid list

Built by contrasting the user's own samples against typical model output, plus their own explicit standing bans wherever a memory or profile rule states one. Seed it with this concrete starting set - never remove an entry without the user's own instruction, only add to it:

- **No em dashes, ever.** Use " - ", ";" or a middot separator instead.
- **Australian English spelling** throughout - behaviour, prioritise, organise, analyse, colour, and so on, never the US variants.
- **No summarising closers.** Don't restate the point in a final "In summary" / "Overall" sentence - if the piece made its point, it's already made.
- **No "I hope this helps"**, or any variant sign-off performing helpfulness rather than saying something.
- **No over-hedging.** "It's worth considering", "this could potentially", "arguably" - if it's worth saying, say it plainly.
- **No padded parallel bullets.** Bullets padded to look thorough, or written at mismatched levels of detail so a reader has to work to see the actual contrast between them.
- Framework nouns as filler: opportunity, alignment, stakeholder, value proposition, holistic, leverage (as a verb), surface (as a verb), robust, seamless, delve, underscore, "it's important to note".
- Boilerplate section headers beyond what the register's own convention calls for - no invented "Problem Statement" / "Proposed Solution" / "Success Criteria" scaffolding.
- Manufactured balance - "While X, it's also true that Y" doing the work of one sentence pretending to be two.
- Restating the same point in two different sections of the same piece.
- Em-dash-heavy, three-clause sentences generally - short declaratives are the default register across all four lists, not just teammate-chat.

## Calibration procedure

Runs interactively on the first run of any voice-listing skill, and is re-run by `kb-dream`'s monthly voice review.

**Sampling sources:** up to 200 of the user's own chat messages (excluding bot posts and one-word replies), 50 sent emails, and kb notes carrying `generated.by: human:<user>` (see `kb-conventions.md`'s provenance rule - these are the human-verified equivalent for voice purposes, the clearest evidence of the user's own written register).

**Per-register classification:** each sample is classified into the register it best represents (teammate-chat, exec-update, customer-facing, ticket-prose) before being used - a sample never informs a register it wasn't written in. A sample that doesn't fit any of the four is left unclassified and not used.

**Budget:** 6 connector calls, one kb write batch for the whole calibration pass - not one write per register.

**Write-back:** the register notes and the shared avoid-list are written or refreshed, `profile.voice.calibrated_at` is set to now, and `profile.voice.sample_counts` records how many samples fed each register.

Unattended runs never calibrate - calibration is interactive only (see the risk note below on why). A handler that finds `voice.calibrated_at` empty and is running unattended proceeds anyway, prefixing its draft with `voice: uncalibrated` so the user knows to read it more critically than a calibrated draft.

## Compounding mechanism

Voice matching is a system that improves with use, not a one-time setup:

1. **Per-draft recording.** `reply-draft` and `kb-note` record an entry in `state.voice_edits` (ring buffer, max 30) whenever the user's kept or sent version differs from what was drafted. `reply-draft` checks this by re-reading the thread or sent mail for the same item on its next dispatch; `kb-note` checks it on `kb-dream`'s pass over the note. Each entry: `{tag, register, draft_hash, sent_ref, recorded_at}`.
2. **Periodic review.** `kb-dream`'s monthly voice review re-samples everything since `profile.voice.registers`' `last_voice_review_at`, refreshes the exemplars in each register note, and looks across `state.voice_edits` for a recurring edit pattern - the same kind of change made more than once. A recurring pattern is promoted: either into a new observed trait on the relevant register note, or into the shared avoid-list if it matches an AI-tell shape rather than a register-specific preference. What changed is written to that run's dream note, same as any other curation action.

## Machine-generated but curatable; human-verified is untouchable

Voice notes are `generated.by: <the calibrating or reviewing skill>` by default - machine-generated, and so `kb-dream` may curate them (refresh exemplars, tidy conformance, promote a pattern) under its ordinary contract. **The moment a voice note carries `verified: { by: human:<user> }`** - the user has read and confirmed it themselves - it becomes exactly like any other human-verified kb note under `kb-conventions.md`: never machine-edited in substance or voice again. A review that wants to change a verified voice note surfaces the proposed change for the user to accept, rather than applying it.

## Handler usage rule

A handler drafting prose:

1. **Loads only the register it needs** for the item at hand - never all four, and never the full avoid-list plus every register note when one register note and the shared avoid-list will do.
2. **Self-checks against the avoid-list before returning** - reads its own draft against every line in `Voice/ai-patterns-to-avoid.md` and revises anything that matches, before the draft ever reaches the surface or a report line.
3. **States the register in its report sub-line** - the `handler-contract.md` report line names which register it drafted in (e.g. "drafted a reply · teammate-chat · ..."), so the user can see at a glance whether the right voice was applied without opening the draft.
