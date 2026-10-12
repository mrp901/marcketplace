# Voice

A new capability with no single direct source - it generalises the discipline `source/cloud-idea-ticket/SKILL.md` applies by hand (calibrated against three named prior tickets, a "Cut the AI tells" list, an independent audit) into a standing, compounding mechanism every drafting skill shares.

## Purpose

`reply-draft`, `kb-note` and `idea-ticket` produce prose the user is meant to read as their own - a draft they can send or file with light editing, not one that announces itself as machine-written. Voice matching is not a style guideline layered on afterwards; it is load-bearing for whether the draft is usable at all. Every handler that drafts prose lists `voice` in its `## Needs`.

## Structure in the knowledge base

Rooted at `profile.kb.paths.voice`:

| File | Contents |
|---|---|
| `Voice/index.md` | Pointer index into the register notes below, no frontmatter; lists every register, including any added later |
| `Voice/teammate-chat.md` | Register note - see shape below |
| `Voice/exec-update.md` | Register note |
| `Voice/customer-facing.md` | Register note |
| `Voice/ticket-prose.md` | Register note |
| `Voice/ai-patterns-to-avoid.md` | One shared list, not per-register |
| `Voice/edits-ledger.md` | Dated before/after pairs - see "The edits ledger" below for who writes it and its entry shape |

The register set is open-ended. `profile.voice.registers` names the four base registers above, which every install has and which drafting skills select by name (`reply-draft`'s table, for one); it is a floor, not a ceiling. Any further register note under `profile.kb.paths.voice`, listed in `Voice/index.md`, is a register too: its name is its filename stem with hyphens as underscores (`design-doc.md` is `design_doc`). A skill that needs the list discovers it from the folder and index, never from a hardcoded four. New registers are proposed by `kb-dream` from the edits ledger (see "Compounding mechanism") and created once the user accepts, following the same shape.

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

Runs interactively on the first run of any voice-listing skill, and is re-run by `kb-dream`'s voice re-sample on an attended dream (step 3 of the compounding mechanism).

**Sampling sources:** up to 200 of the user's own chat messages (excluding bot posts and one-word replies), 50 sent emails, and kb notes carrying `generated.by: human:<user>` (see `kb-conventions.md`'s provenance rule - these are the human-verified equivalent for voice purposes, the clearest evidence of the user's own written register).

**Per-register classification:** each sample is classified into the register it best represents (teammate-chat, exec-update, customer-facing, ticket-prose) before being used - a sample never informs a register it wasn't written in. A sample that doesn't fit any register is left unclassified and not used.

**Budget:** 6 connector calls, one kb write batch for the whole calibration pass - not one write per register.

**Write-back:** the register notes and the shared avoid-list are written or refreshed, `profile.voice.calibrated_at` is set to now, and `profile.voice.sample_counts` records how many samples fed each register.

Unattended runs never calibrate - calibration is interactive only (see the risk note below on why). A handler that finds `voice.calibrated_at` empty and is running unattended proceeds anyway, prefixing its draft with `voice: uncalibrated` so the user knows to read it more critically than a calibrated draft.

## Compounding mechanism

Voice matching is a system that improves with use, not a one-time setup:

1. **Per-draft recording.** `reply-draft` and `kb-note` record one entry in `state.voice_edits` (ring buffer, max 30) for every draft. A later comparison against the user's kept or sent version sets the entry's `edited` to `true` or `false`; until then it is absent, and the entry is a record of a draft, not evidence of an edit. Who performs the comparison differs by handler: `reply-draft` compares on a later dispatch against the same source, by re-reading the thread or sent mail; "the same source" means a matching `item.ref`. Where no later dispatch ever names that ref again, no comparison happens from this side and `kb-dream`'s pass picks the draft up as it does for `kb-note`, so nothing is lost, it just arrives later. `kb-note` never compares, because a ticked item dispatches once and it has no second run; `kb-dream` does that comparison for it during its own pass over the note. In both cases the handler's only job at draft time is to append the ledger entry, in its own state shard; `kb-dream` records its verdict on another skill's entry in its own shard's `voice_verdicts`, never on the entry itself (`state-schema.md`, "Shards"). Each entry: `{tag, register, draft_hash, sent_ref, recorded_at, edited}`.
2. **Ledger promotion, every dream.** `kb-dream` reads `Voice/edits-ledger.md` on every non-quiet run, unattended, from the knowledge base alone - no chat or mail read, so it never needs calibration. A pattern that recurs in 2 or more dated ledger entries is promoted automatically: a new observed trait on the relevant register note, or a line in the shared avoid-list if it matches an AI-tell shape rather than a register-specific preference, citing the ledger entries it came from (the user's own edits are the human evidence). A pattern seen in one entry only is proposed, not applied, as a `dream:` line the user can tick. When 3 or more entries fit no existing register, `kb-dream` proposes a new register the same way. A human-verified voice note is never auto-edited (see below). Mechanics: `skills/kb-dream/references/voice-review.md`.
3. **Periodic re-sample.** `kb-dream`'s voice review also re-samples everything since `state.cursors.kb-dream.last_voice_review_at`, refreshes the exemplars in each register note, and settles any `state.voice_edits` entry still missing `edited`. Re-sampling chat and mail is calibration, so it runs only on an attended dream; it is due once that cursor is 30 days old and is retried on every dream until it completes, never parked until the next month. What changed in either step is written to that run's dream note, same as any other curation action.

## The edits ledger

`Voice/edits-ledger.md` is the one place real before/after text lives (`state.voice_edits` holds only hashes), so it is the review's primary input.

**Who appends.** Any skill or session holding the user's own evidence about their writing - a before/after pair, or their verbatim words: a session where the user edits a draft and asks for it recorded; `reply-draft` or `kb-dream` when a comparison sets `edited: true` and the drafted and kept texts are both readable; and `kb-dream`'s signal extraction, routing a session note's `## Voice and tone feedback` bullets here rather than to memory. Appending is additive and needs no confirmation; every append carries the usual index and log lines, which is also what wakes the next dream.

**Entry shape**, newest first, one `##` section per occasion:

```markdown
## YYYY-MM-DD - <shape of writing> (<subject>)

Register: <existing register name, or the shape in words if none fits>. <Who drafted, who edited, where it went.>

1. **<The change, as a short title>.**
   - Before: <drafted text, verbatim or closely trimmed>
   - After: <what the user sent or kept, verbatim>
   - Rule: <the pattern the pair implies, in one line>
```

A stated instruction with no pair (a session's verbatim tone correction) takes `- Said: "<verbatim>"` in place of Before/After. `Rule` is optional where the pair speaks for itself. `kb-dream` alone adds a `- Promoted: <date> to <register note link>` or `- Proposed: <date> (<dream tag>)` sub-bullet under an item it has acted on, which is what stops a second run re-promoting or re-proposing it; nobody else edits an existing entry.

## Machine-generated but curatable; human-verified is untouchable

Voice notes are `generated.by: <the calibrating or reviewing skill>` by default - machine-generated, and so `kb-dream` may curate them (refresh exemplars, tidy conformance, promote a pattern) under its ordinary contract. **The moment a voice note carries `verified: { by: human:<user> }`** - the user has read and confirmed it themselves - it becomes exactly like any other human-verified kb note under `kb-conventions.md`: never machine-edited in substance or voice again. A review that wants to change a verified voice note surfaces the proposed change for the user to accept, rather than applying it.

## Handler usage rule

A handler drafting prose:

1. **Loads only the register it needs** for the item at hand - never all of them, and never the full avoid-list plus every register note when one register note and the shared avoid-list will do.
2. **Self-checks against the avoid-list before returning** - reads its own draft against every line in `Voice/ai-patterns-to-avoid.md` and revises anything that matches, before the draft ever reaches the surface or a report line.
3. **States the register in its report sub-line** - the `handler-contract.md` report line names which register it drafted in (e.g. "drafted a reply · teammate-chat · ..."), so the user can see at a glance whether the right voice was applied without opening the draft.
