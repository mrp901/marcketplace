Return the state document `990111222` as it exists before this skill has ever run. Its
body/properties include existing fields used by the `briefing` skill - `last_run_ts`,
`last_seen`, nicknames, and glossary entries - but it does NOT have a
`cursors.proactive-router.last_scanned` field yet. This is the first-ever run of
proactive-router, so the skill should fall back to a 24-hour lookback and say so in its
summary.
