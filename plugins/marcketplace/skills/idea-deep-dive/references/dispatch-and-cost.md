# Dispatch and cost

Keep this section byte-identical run to run - it is meant to be a stable, cache-eligible
prefix, not something reworded per invocation.

**Tier the model by task, not by step.** Every search - the upfront sweep, and any
per-question search in circles `kb`, `people`, `code`, or `web` - is dispatched as a subagent
on `budgets.models.search` (a cheap, fast tier - see `../../../shared/model-tiers.md`) with
one narrow job, returning only a compact result (`found`, `answer`, `source`, plus a
`question#` on sweep calls since one dispatch covers many questions). Raw thread, page,
transcript or file content never lands in this session's context this way.

**What stays on the primary model, never delegated:**

- Step 0's own reads: the idea's issue or its recent comments, an existing note, the note-glob
  check, the one-time codebase availability check.
- Cross-checking a question against the idea's comments already read in Step 0 - that is a
  comparison against material already in context, not a new search; only an actual
  circle search is delegated.
- The final write-up itself - updating the note, the surface item, the notification - a
  write, not a search.
- Classification and judgment: blocking vs. incidental, dedupe, depth-cap, stuck-or-not.

**Why this split.** Vault, chat, email, notetaker and web lookups are near-free structured
lookups on a cheap tier; the primary model's job is holding the run's state (the queue,
chain-depths, what is exhausted where) and making the judgment calls, not reading raw source
content. Tiering by task rather than by step means the same rule applies whether a search
happens in the upfront sweep or three loops deep in a spawned chain.

**Unavailable tier.** If `budgets.models.search` is not available in the running environment,
fall back to the strongest model that is, and say so plainly in the run's report - never
silently downgrade. See `../../../shared/model-tiers.md`, "Stating an unavailable tier".
