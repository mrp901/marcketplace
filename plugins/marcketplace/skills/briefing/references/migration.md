# Migrating the board to the five-section layout

Runs once, on the first `briefing` run whose `state.installed_version` is older than
1.1.0 and whose board still carries any of the old headings (Running behind, Terms to
learn, Proactive opportunities, Ideas: decisions for you, Wireframes to review, Actions,
Dream log / actions, Skill health, Plugin notices). It is the only write of that run:
briefing composes no message and refreshes no snapshot until the board is in the new
shape, and every other skill that finds `installed_version` behind records
`runs.<skill>.status: quiet`, note `awaiting migration`, and stops (see
`../../../shared/state-schema.md`'s migrations table), so nothing races this write.

## Steps, all inside one `chat: update canvas` batch

1. **Create the new sections and the header.** The three header lines from
   `../../../shared/surface-protocol.md`, then Today, To-do, For you, Ideas, Closed, in
   that order. Calendar and Tracker's current dated blocks move under Today unchanged.
2. **Move open lines by tag, keeping `state.items` hashes.** Every checkbox line whose
   tag is in `state.items` moves, with its sub-lines, wording and tick state untouched:
   - `pr:` (Proactive opportunities), `rb:` (Running behind), `sweep:` (Actions),
     `dream:` (Dream log / actions), `shc:` (Skill health) go to For you, in that order,
     oldest first within a prefix.
   - Terms to learn lines get a `term:<yymmdd>-N` tag in this write (they had none) and go
     to For you; `state.items` gains an entry for each.
   - To-do lines stay in To-do.
   - A `dream:` line in the old free-text form (`{line} - tick to have me take this on
     next pass`) is rewritten into the protocol grammar, `🧹 {line} · <ref>`, since it was
     never in the user's wording; every other line keeps its exact text.
3. **Convert old Ideas and Wireframe lines into idea blocks.** For each distinct idea key
   in Ideas: decisions for you and Wireframes to review, one block under Ideas:
   - The header `- <key> · <title> · note · wireframe`, with each link present only where
     the artefact exists (the research note under `kb.paths.research`, the wireframe
     under `kb.paths.prototypes`); the title comes from the old line's text.
   - Each old decision line becomes one decision question with its options split out
     where the line already implied them (`<key>/d1a`, `<key>/d1b`, …). Where the line
     stated no options, it becomes a one-line question: `(<key>/d1) <text> · edit this
     line with your answer and tick`.
   - Each old wireframe line becomes the three-option reaction group
     (`<key>/w-keep`, `<key>/w-rework`, `<key>/w-drop`).
   - A ticked old line stays ticked on its converted form (the first option, where the
     line was split), so the hub acts on it next run rather than losing the tick.
   - `state.items` gains one entry per new line with `group` and `idea_key` set; the old
     entries are dropped.
4. **Delete the old headings** and any Plugin notices content. Fast-fail notices are not
   carried: the skills they named will record `state.runs` on their next run.
5. **Log one line to Closed:** `- <date> (migration) board migrated to the five-section
   layout · <n> lines moved, <m> idea blocks created · by briefing`.

Then write state: `installed_version` = this plugin's version, `items` as rebuilt,
`runs.briefing` with `note: board migrated`.

## If the board cannot be read as either layout

Do not guess. Record `runs.briefing.status: error`, note `board layout unrecognised`,
post that one line to `profile.notify.fallback_channel_id` per `../../../shared/notify.md`,
and stop. The user runs briefing interactively once to sort it out.
