# History

## 2026-09-22 built for marcketplace

`kb-note` has no source predecessor - it generalises the capture half of
`source/session-log/SKILL.md` (one note, not a whole session) and applies
`shared/voice.md`'s drafting discipline for the first time end to end. Built directly
against `shared/handler-contract.md`, `shared/kb-conventions.md` and `shared/voice.md`
rather than against an inherited SKILL.md.

**Design decisions, with reasoning:**

- **Dead or empty reference link.** The skill never writes a note from
  `item.text_as_ticked` alone when the source can't be read. Reasoning: the tick's
  wording is a pointer at the source, chosen by the router's classification step, not a
  substitute for it - a note built only from that wording risks recording something the
  source never actually said, which is exactly what "never invent a fact" forbids.
  Returns `status: blocked` with a report line naming what was unreachable, so the user
  can re-point the item rather than silently getting a thin, possibly wrong note.

- **Decision-shaped vs reference-shaped, and the `type` each gets.** Classified by
  content, not by the `kb-doc` category tag (which covers both): a source that commits to
  a choice among alternatives is decision-shaped, a source that states a durable fact or
  constraint with no choice made is reference-shaped. The frontmatter `type` for each is
  resolved against the live `kb.types_registry` file at run time, per
  `kb-conventions.md`'s type-registry rule - never asserted from this skill's own
  `references/note-template.md`, which is example material, not the registry. This skill
  does not hardcode "Decision Record" or "Reference" as the only legal values; it treats
  them as the likely closest matches and checks the live file before writing either.

- **Near-duplicate handling.** One cheap `kb: search` on two or three keywords from the
  extracted fact, against the inbox (and the decisions folder for a decision-shaped
  note), before writing. A close match means no second note - `status: done`, empty
  `artefacts`, report line points at the existing note. Deliberately not a sprawling
  search (one call, not a research pass) and deliberately not a silent edit of the
  existing note if it looks stale or contradicted - that's a conflict for a human to
  resolve, flagged in the report line, not something this skill decides on its own.

**Why `capture` is not a two-tick mode.** `handler-contract.md`'s irreversible-write rule
gates ticket filing, comment pushing, message sending - actions with an external,
hard-to-undo effect on someone else's system. Writing a markdown file into the user's own
knowledge base is additive, lands nowhere but the user's own store, and is trivially
reversible by editing or deleting it. Treating it as a first tick requiring a second
confirming tick would add friction the rule was never meant to create. This is stated
directly in `## Handler mode` in `SKILL.md` so a later reader doesn't "fix" it into a
two-tick flow by analogy with `idea-ticket` or `action-sweep`.

**Open questions for the orchestrator:**

- No profile or state key needed that the schemas don't already define. `kb.paths.inbox`,
  `kb.paths.decisions`, `kb.paths.log`, `kb.types_registry`, `voice.registers` and
  `state.voice_edits` all exist already.

**Friction against the three contracts** (handler-contract.md, voice.md,
kb-conventions.md), reported per the task brief:

- `handler-contract.md`'s payload shows `output_location: <where the handler's artefact
  should land>` but never says what form that value takes for a kb write - a folder path
  under `kb.paths`? A specific note path? This skill treats it as an optional override of
  `kb.paths.inbox` and falls back to `kb.paths.inbox` when absent, but the contract itself
  doesn't say that's the right default.
- `voice.md`'s per-draft recording section says `kb-note` "checks this by re-reading the
  thread or sent mail for the same item on its next dispatch" - but `kb-note` is a
  one-shot handler with no next dispatch for the same tag (each ticked item dispatches
  once). The re-check almost certainly belongs to `kb-dream`'s pass over the note instead,
  which the same paragraph also says a sentence later ("`kb-note` checks this on
  `kb-dream`'s pass over the note"). The two clauses in that sentence read as
  contradictory about which skill does the re-check; this build assumes the second
  clause (kb-dream's pass) is authoritative and `kb-note`'s own job is only to record the
  entry, not to re-check it.
- `kb-conventions.md`'s frontmatter table lists `status` with "vocabulary is kb-local" and
  no default named anywhere. This skill writes `status: draft` for every note it produces
  (nothing it captures has been human-reviewed yet), but that default isn't stated in the
  shared reference - a different handler could reasonably pick a different default value
  for the same reason.
- `handler-contract.md`'s category table maps `kb-doc -> kb-note capture` with no mention
  of a confirming mode, while every other row with a bracketed mode name in that column
  either has an explicit two-tick note (`ticket-idea`, `ticket-minor`) or is plainly a
  single-shot inline action. `kb-note`'s single-mode status had to be inferred from that
  absence plus the irreversible-write rule's own wording, rather than stated outright.

## 2026-09-25 canvas redesign (1.1.0): every tick means yes, do it

No behaviour change. It reads `item.category` (`kb-doc` or `summarise`) explicitly, since
`summarise` dropped the star from its emoji when FYIs left the board, and its Budget links
the shared token discipline.
