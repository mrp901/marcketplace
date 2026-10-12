# Migrating the board to the five-section layout

Runs once, on the first `briefing` run that finds any of the old headings on the board,
whatever `state.installed_version` says (the headings are the trigger, so a version bumped
early by mistake can never strand an old board) (Running behind, Terms to
learn, Proactive opportunities, Ideas: decisions for you, Wireframes to review, Actions,
Dream log / actions, Skill health, Plugin notices). It is the only write of that run:
briefing composes no message and refreshes no snapshot until the board is in the new
shape, and every other skill that reads or writes the board and finds an old heading records
`runs.<skill>.status: quiet`, note `awaiting migration`, and stops (see
`../../../shared/state-schema.md`'s migrations table), so nothing races this write.

## Steps, all inside one `chat: update canvas` batch

1. **Create the new sections and the header.** The three header lines from
   `../../../shared/surface-protocol.md`, then Today, To-do, For you, Ideas, Closed, in
   that order. Calendar and Tracker's current dated blocks move under Today unchanged.
2. **Move open lines by tag, keeping their `state.items` entries.** Every checkbox line whose
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
     under the prototypes folder); the title comes from the old line's text.
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

## 1.1.0 to 1.2.0: retiring the old idea lines

The idea pipeline (`idea-scout`, `idea-deep-dive`, `idea-wireframe`) was replaced by
`idea-spar`, which writes only `<key>/d…` decision groups. Lines the retired skills wrote
have no owner and no handler now, so they close rather than wait forever. Unlike the
1.0.0 migration this is not the run's only write: the steps go inside the run's ordinary
`chat: update canvas` batch.

1. Every open line tagged `<key>/q…`, `<key>/w-…` or `<key>/r` moves to Closed as
   `- <date> (<tag>) retired · <text, 120 chars> · by briefing`, ticked or not. Its
   `state.items` entry is pruned.
2. Open `<key>/d…` groups stay exactly as they are; a tick on one now dispatches
   `idea-spar` `decide`.
3. A block header left with no open lines is removed, as usual. A header that keeps lines
   has its `note` and `wireframe` link text left alone; idea-spar adds `pack` when it next
   writes the block.
4. Apply the state steps in `../../../shared/state-schema.md`'s 1.1.0 to 1.2.0 row, then
   write `installed_version` = 1.2.0.

## 1.2.0 to 1.3.0: state shards

No board change. Inside the run's ordinary state write, add `shards: {}` to the main state
document if absent, then write `installed_version` = 1.3.0. Each skill creates its own shard
on its next run per `../../../shared/state-schema.md`'s "Shards"; briefing creates its own
the same way and never creates another skill's.

**If the main document is over the 45 KB size guard**, adding `shards: {}` grows it and the
guard refuses the write, so no skill could ever migrate. In that case, and only then,
briefing shards every skill in this run: for each skill with a `runs.<skill>`,
`cursors.<skill>` or skill-owned key in the main document, create its shard (copying those
subtrees verbatim, by cutting text, never by re-typing a re-serialised copy), and read each
back. Then write the main document once, with `shards` naming every new shard, those
subtrees removed and `installed_version` = 1.3.0. That write shrinks the document, so the
guard's exception allows it; re-read and compare it as the exception requires. A shard that
already exists for a skill (one a run created before the pointer could land) is reused
rather than duplicated, and its values win over the main document's older copy.

## 1.6.0 to 1.6.0: shared lists to their writers' shards

No board change. 1.3.0 sharded `runs` and `cursors`, but `items`, `outcomes` and the hub's
counters stayed in the main document, so every run that posted a board line had to re-type
all of it, and runs skipped that write instead. From 1.6.0 each of these lives in its
writer's shard (`../../../shared/state-schema.md`, "Shards"):

| In the main document | Moves to the shard of |
|---|---|
| `items.<tag>` | the owner of the tag's prefix (`../../../shared/surface-protocol.md`'s prefix table) |
| `outcomes` entries | `skill-eval` where `handler: skill-eval`, else `proactive-router` |
| `voice_edits` entries | `kb-note` or `reply-draft`, whichever an `outcomes` entry with the same tag names as handler |
| `tally`, `suppressions`, `patterns_blocked` | `proactive-router` |
| `runs.<skill>`, `cursors.<skill>` of a skill with no shard | that skill (the 1.3.0 rule) |

An entry with no installed owner (a retired skill's tag, a `voice_edits` entry no outcome
names) stays where it is; every reader still unions it, and no step deletes it.

Owners do most of this themselves: from 1.6.0 a skill seeds a key its shard lacks from its
own entries in the main document on its first write, and from then on writes only its
shard (onboarding step 6). This migration does the rest, inside a run's ordinary state
write, on every briefing run until the main document holds no owned entry:

1. **Plan, before writing anything.** An owned entry is *ready* when its owner's shard
   holds that same entry (the shard's copy wins), when its tag is in `closed`, or when its
   owner has no shard (step 2 creates it). An entry an existing shard lacks is not ready:
   removing it would lose it, so it waits for its owner to seed it. Work out the main
   document as it would stand with every ready entry removed and a pointer added for each
   shard step 2 creates. If that keeps more bytes than it removes and would still be over
   10 KB, change nothing this run and say so in `runs.briefing.note`; a later run, after
   more owners have seeded, tries again. So the migration never re-types more than it
   removes, except on a document small enough to re-type safely.
2. **Shard first.** For each owner with no shard, briefing among them, create its shard
   holding its `runs`, `cursors` and owned entries, copied verbatim by cutting text, never
   by re-typing a re-serialised copy, and read it back. A shard that does not read back
   with every copied entry drops out of this run's plan; its entries stay in the main
   document. Never write into a shard that already exists: its owner seeds it.
3. **Pointer and cleanup, one write.** Re-read the main document, add `shards.<skill>` for
   each shard step 2 confirmed, remove every ready entry, and once no owned entry is left,
   write `installed_version` = 1.6.0. This write shrinks the document, so the size guard's
   exception allows it at any size; re-read and compare it as the exception requires and,
   on a mismatch, restore the copy read at run start.
4. **Idempotent.** An entry already gone from the main document, or an owner that already
   has a shard, is skipped, so an interrupted run is finished by the next. A shard created
   in step 2 whose pointer did not land is never read; name its id in `runs.briefing.note`
   so the user can delete it, and create a fresh one next run.

A fresh instance has no owned entries in the main document and nothing to move: step 1
finds nothing, and `installed_version` = 1.6.0 is written to the main document, which is
small enough to re-type, in the same run.
