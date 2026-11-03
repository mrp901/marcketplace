# State write (flow step 12)

Seed first. The write copies into this skill's shard any of its own `items`, `tally`,
`suppressions`, `outcomes` and `voice_verdicts` entries the main document still holds and
the shard lacks, bar tags in `closed` (a copy; `briefing`'s 1.6.0 migration removes the
original), per `../../../shared/state-schema.md` "Shards". The shared rule alone has been
skipped: this shard was created at 1.3.0, before seeding existed.

Then write `cursors.kb-dream` (`last_dream_at`, `last_full_dream_at` if full,
`last_registry_review_at` if run, `last_voice_review_at` only when the re-sample completed,
`last_health_values` when the verdict was measured; drop `open_followups` if the shard still
holds it, the escalation ledger is gone), its own `items` with this run's `dream:` tags (tags
in briefing's `closed` pruned), `voice_verdicts`, `runs.kb-dream` (with `health`, when
measured), all in its shard;
`voice.sample_counts` if the re-sample completed; `proposals` (main document) only for a
60-day dismissal or a new proposal; `ideas` pruned of ideas no longer anywhere (monthly
only).
