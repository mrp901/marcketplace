# The monthly voice review

Runs on the first full-mode dream of a calendar month, or on request. This is
`shared/voice.md`'s "Periodic review" step; that file is the authority, this reference
only says what `kb-dream` specifically does to trigger and record it.

## Steps

1. **Re-sample.** Re-run `voice.md`'s calibration procedure's sampling step (chat
   messages, sent mail, `generated.by: human:<user>` kb notes) for everything since
   `state.cursors.kb-dream.last_voice_review_at`, not the full history again.
2. **Refresh exemplars.** Update each register note's 3-5 verbatim exemplars per
   `voice.md`'s structure, favouring the freshest strong examples over the oldest.
3. **Promote from the ledger.** Scan `state.voice_edits` (ring buffer, up to 30 entries)
   for a recurring edit pattern - the same kind of change made more than once since the
   last review. A recurring pattern is promoted either into a new observed trait on the
   relevant register note, or into `Voice/ai-patterns-to-avoid.md` if it matches an
   AI-tell shape rather than a register-specific preference.
4. **Human-verified is untouchable.** A voice note carrying `verified: { by: human:<user>
   }` is never machine-edited in substance or voice by this step, per `voice.md`'s own
   rule and this skill's rule 3. A review that wants to change a verified voice note
   surfaces the proposed change instead of applying it - same shape as a fold proposal,
   written as a Surfaced bullet, never written into the note itself.

## Write-back

`profile.voice.sample_counts` updated with this review's sample counts,
`state.cursors.kb-dream.last_voice_review_at` = now. What changed goes into the dream
note's "What I curated" table like any other curation action, one row per register note
touched.
