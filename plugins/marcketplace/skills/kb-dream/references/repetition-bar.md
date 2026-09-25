# The repetition bar for failed writes

A write this skill attempted and the system rejected (a tracker label, a field edit, a
connector refusal encountered while curating or reaping) is worth one line in the dream
note's Flags section. It is **not** a Surfaced item until the *same* target fails again on
a later attempt.

- Two different targets whose writes were both rejected today is two single failures, not
  a pattern. Log both in Flags; don't manufacture an insight from them. The user would
  have noticed on the next run if the same thing failed again.
- The same target's same write rejected on a retry (this run versus a previous run's
  `log.md`) **is** repetition. That earns a Surfaced item and its own `dream:` line on the
  board, because a human would want to know the second time, not the first.

Same bar applies to any recurring mechanical failure: repetition means the same target
twice, not two targets once. This rule is specific to `kb-dream`'s own writes during a
curation, extraction, link, registry or voice pass - it is not a general property of the
shared handler contract, which has no equivalent bar.
