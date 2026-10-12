# The voice review

Two parts with two cadences. **Ledger promotion** runs on every non-quiet dream,
unattended, from knowledge-base reads alone. **Re-sampling** is calibration, so it needs
an attended run; it falls due monthly and is retried on every dream until it completes.
This is `shared/voice.md`'s "Compounding mechanism" (steps 2 and 3) and "The edits
ledger"; that file is the authority, this reference only says what `kb-dream` does to
trigger and record it.

## Part A - ledger promotion (every dream)

1. **Read the ledger.** One read of `Voice/edits-ledger.md`. Nothing new since the last
   dream and no item left un-acted (no `Promoted:`/`Proposed:` marker) means one Flags line
   and stop. Read the register notes only when there is a candidate to place.
2. **Group items into patterns** - the same kind of change, judged from the `Rule`, `Said`
   or Before/After text, not from identical wording. Count the distinct dated entries a
   pattern appears in; two items in one entry count once.
3. **Recurring (2+ entries): promote, unattended.** Add one observed trait to the register
   note the entries name, or one line to `Voice/ai-patterns-to-avoid.md` if it is an
   AI-tell shape rather than a register preference. Sharpen an existing trait that already
   says it rather than appending a near-duplicate. The line cites its evidence, e.g.
   `- Cuts explanatory asides; one line of rationale, inside the structure (ledger:
   2026-10-07 #6, 2026-10-08 #5)`, with the ledger linked once per note. Set the note's
   `generated` to this skill and now, per the provenance rule; leave `verified` as it is.
   Mark each source item `- Promoted: <date> to <register note link>`.
4. **Singleton (1 entry): propose.** A `dream:` line in the shape "add to <register>:
   <trait> · <ledger link>", marked `- Proposed: <date> (<dream tag>)` on the item. Not
   proposed again; a second entry matching it later promotes it under step 3, and a
   deleted line is never re-added.
5. **No register fits (3+ entries): propose a new register.** Entries whose `Register:`
   line names a shape no register covers count towards it; at 3, one `dream:` line naming
   the register and its entries. Accepting it is a `settle` tick: create the note in
   `voice.md`'s register shape from those entries (the After texts are the user's own words,
   so they serve as exemplars), add it to `Voice/index.md`, then promote its patterns.
   Below 3, those entries wait; their AI-tell patterns may still go to the avoid-list.
6. **Settle ticks** on any of these lines apply the proposal from the evidence already in
   the ledger and return `done`.

## Part B - re-sample (due monthly, retried until done)

Due when `state.cursors.kb-dream.last_voice_review_at` is 30 or more days old, whatever the
mode, so a skipped or failed month is picked up by the next dream rather than the next
month's first.

1. **Attended run: re-sample.** Re-run `voice.md`'s calibration sampling step (chat
   messages, sent mail, `generated.by: human:<user>` kb notes) for everything since
   `last_voice_review_at`, not the full history again.
2. **Refresh exemplars.** Update each register note's 3-5 verbatim exemplars per
   `voice.md`'s structure, favouring the freshest strong examples over the oldest.
3. **Settle `state.voice_edits`.** Any entry still missing `edited` whose `sent_ref` is a
   note (the comparison `voice.md` assigns to this skill): compare the note as it stands
   with what was drafted and record `voice_verdicts.<tag>: true` or `false` in this skill's
   own shard (the entry sits in `reply-draft`'s or `kb-note`'s, and is theirs to write);
   drop any verdict whose tag is in no ledger ring any more. Where both texts are readable,
   an edited one also becomes a ledger entry (Part A then promotes it).
4. **Unattended run: don't calibrate.** Run step 3 only, leave `last_voice_review_at`
   where it is, and write "Voice re-sample: due since <date>, needs an attended dream" in
   Flags. Once it has been due 7 days, surface one `dream:` line asking the user to say
   "dream" in a session; never repeat it while that line is open.

## Human-verified is untouchable

A voice note carrying `verified: { by: human:<user> }` is never machine-edited in
substance or voice by either part, per `voice.md`'s own rule and this skill's rule 3. A
promotion or refresh that wants to change a verified voice note surfaces the proposed
change instead of applying it - same shape as a fold proposal, written as a Surfaced
bullet, never written into the note itself.

## Write-back

Part A: the register and ledger edits, each a row in the dream note's "What I curated"
table, plus the usual index and log lines. Part B, only when the re-sample completed:
`profile.voice.sample_counts` with this review's counts and
`state.cursors.kb-dream.last_voice_review_at` = now.
