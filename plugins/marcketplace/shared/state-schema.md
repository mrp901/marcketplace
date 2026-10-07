# State schema

## Purpose

State is the plugin's working memory: run history, cursors, the category-to-handler
registry and its tally, the item ledger the surface protocol needs to interpret ticks,
idea-spar's per-idea roadmap memory, and per-machine tool-prefix resolutions. Like the
profile, it lives in a cloud-connector document the user owns (a Confluence page or a
SharePoint/OneDrive file) and never local-only. The state document points back to the
profile via `profile_ref`, and the profile points to state via `state_ref`; they are two
sibling documents, never one.

## Why two documents

State is written five to ten times a day; the profile is written once at bootstrap and
occasionally after that when the user changes something. Most of the connectors this
plugin supports (Confluence pages, SharePoint files) are full-body-replace: a write
resends the entire document, not a diff. That asymmetry is the whole argument for keeping
them apart:

- **Write-frequency asymmetry against full-body-replace connectors.** If profile and state
  shared one document, every routine run of every skill would resend the profile's org
  facts, tool choices and voice configuration along with its own cursor bump, multiplying
  the chance a stale in-flight write clobbers a profile edit the user just made.
- **Blast radius.** A bad state write (a malformed cursor, a corrupted tally) should never
  be able to take the profile down with it.
- **Ownership.** The user edits the profile directly, deliberately, rarely. Only the
  plugin edits state, and only its own subtrees.
- **Concurrency.** Two routines can run close together. Isolating the high-contention
  writes to their own document keeps the retry-once-on-conflict rule (below) cheap and
  rare in practice.

## Shards

A full-body-replace write resends the whole document, so state's cost grows with every
skill that writes to it, and a routine that only bumps a cursor still resends everything.
Left alone this grows past what a run can safely re-type (the reference instance's state
page passed 49 KB). So every skill that owns `runs`, `cursors` or other keys of its own keeps them
in its own small sibling document (a skill that writes only shared keys, such as `kb-note`,
`reply-draft` and `skill-eval`, has no shard), and a quiet run rewrites a few hundred bytes.

- **What lives in a shard.** `runs.<skill>`, `cursors.<skill>`, and any key only that skill
  writes (`ideas` for `idea-spar`). These are the subtrees the write discipline already
  says no other skill may write.
- **What stays in the main state document.** Everything shared or low-frequency:
  `state_version`, `installed_version`, `profile_ref`, `shards`, `glossary`, `nicknames`,
  `registry`, `tally`, `proposals`, `suppressions`, `patterns_blocked`, `items`,
  `outcomes`, `voice_edits`, `machines`.
- **Pointer.** The main document carries `shards: {<skill>: <ref>}`, same ref format as
  `state_ref`; an absent `shards` key reads as `{}`. Onboarding step 2 reads this skill's shard by id.
- **A shard document** holds `shard_version: 1`, `skill`, `state_ref` (pointer back to the
  main document) and only that skill's subtrees, in the same shape as the main document.
- **Creating a shard.** Onboarding creates it on a skill's first run after the 1.3.0
  migration, when `shards.<skill>` is absent: copy that skill's subtrees from the main
  document into a new sibling document, write `shards.<skill>` in the main document in the
  same run, and leave the old subtrees in the main document until the next run confirms the
  shard reads back. The next run then deletes them from the main document. Shard first,
  pointer second, cleanup third, so a failure at any step leaves a readable state. Until
  the pointer exists, a skill reads and writes its subtrees in the main document as before.
- **Cross-shard access.** `kb-dream`'s monthly prune of `ideas.<key>` entries for ideas that
  no longer exist is the one write into another skill's shard (`idea-spar`'s); it reads and
  writes that shard by id and touches nothing else in it.
- **Readers.** `briefing` and `skill-health-check` read `runs.<skill>` for every skill, so
  each reads the main document plus every shard named in `shards`, by id. A shard that
  cannot be read is reported as `runs: unreadable` for that skill; it never fails the
  reader.
- **Size guard.** A skill that is about to write a document over 45 KB, main or shard,
  does not re-type it in full: it writes `runs.<skill>.status: partial` with note
  `state too large to rewrite safely` and stops. A write that cannot be reproduced
  faithfully is worse than a skipped one. The main document, with only shared keys left,
  should sit well under the limit; a shard that nears it means that skill's own subtree
  needs pruning.

## The commented YAML

```yaml
state_version: 1
installed_version:           # from plugin.json; a newer plugin.json triggers the migrations below
profile_ref:                  # pointer back to the sibling profile doc
shards: {}                    # {<skill>: <ref>} - each skill's runs/cursors live in its own doc (see Shards)

runs:
  <skill>: {last_run_at, status: ok | quiet | partial | fast-fail | error, machine, note, ref}
  # note: one line on what the run did (or why it stopped); ref: a link to the run's artefact
  # proactive-router adds fyi: [<one line each, max 10>]
  # skill-health-check adds scores: {<skill>: {tag: green | amber | red, why, ref, checked_at}}

cursors:
  briefing: {last_run_ts, last_seen: {<channel_id>: <ts>}}   # every channel briefing reads, feed channels included
  proactive-router: {last_scanned}
  action-sweep: {scanned_through, chat_since}
  idea-spar: {roadmap_checked_at}
  kb-dream: {last_dream_at, last_full_dream_at, last_registry_review_at, last_voice_review_at,
             open_followups: {<note path>#<slug>: {text, first_flagged_at, dreams_open, escalated_tag}}}
  session-log: {last_pending_processed}
  skill-health-check: {last_checked: {<skill>: <date>}}

ideas:
  <idea key>: {roadmap_last_seen, pack_ref, pack_pending: false}

glossary: {<term>: <meaning>}
nicknames: {<email>: <nickname>}

registry:
  <category>: {handler: <skill> | inline:<name> | manual:<name> | null, mode, since, set_by: shipped | user_tick}

tally:
  <category>: {proposed, ticked, deleted, edited, unmapped_ticks, last_ticked_at}

proposals: [{id, kind: mapping | suppression_lift | skill_fold, category, candidate, opened_at, status}]
suppressions: [{source_id, category, pattern: "<channel_id>:<category>", added_at}]
patterns_blocked: []

items:
  <tag>: {section, written_by, written_at, text, ref, category, group, idea_key,
          status: open | blocked, blocked_reason, blocked_on, blocked_at, retried_for}
  # text: the line exactly as written, compared verbatim with the board to spot an edit
  # pruned when the line reaches Closed; group is the question's tag stem on an option line
  # status and the blocked_* fields are optional (absent = open); only the hub sets them, on pr: lines

outcomes: []                 # ring buffer, max 50, newest first: {tag, handler, status, report_line, recorded_at}
voice_edits: []              # ring buffer, max 30: {tag, register, draft_hash, sent_ref, recorded_at, edited}
                             # one entry per draft; edited is absent until the later comparison sets true/false

machines:
  <machine_id>: {tools: {chat: "mcp__...__", tracker: "...", ...}, kb_access, codebase_access, resolved_at,
                 cli: {tracker: "<path to twg>", ideas: "..."}, cli_probed_at}
                 # cli is optional: present only for categories whose local CLI passed the probe
```

`ideas.<key>` is idea-spar's only memory of an idea: the roadmap slot it last saw, the
link to the idea's latest pack, and whether a Next-watch pack is still owed. No skill writes
a tracker label on an idea.

## Key-by-key table

| Key | Written by | Read by | Retention |
|---|---|---|---|
| `state_version` | onboarding, on bootstrap | every skill (compatibility check) | permanent |
| `installed_version` | onboarding on bootstrap; afterwards only the skill that completes a migration (for 1.0.0 to 1.1.0, `briefing`) | `briefing` (the migrating skill); other skills check the board's headings instead | permanent; never bumped by a skill that skipped a pending migration |
| `profile_ref` | onboarding, on bootstrap | every skill | permanent |
| `runs.<skill>` | that skill, at the end of its own run | briefing (the Runs report), skill-health-check | permanent, one entry per skill, overwritten each run |
| `runs.proactive-router.fyi` | proactive-router | briefing | overwritten each run |
| `runs.skill-health-check.scores` | skill-health-check | briefing | one entry per skill scored, overwritten when re-scored |
| `cursors.briefing` | briefing | briefing | permanent, overwritten each run |
| `cursors.proactive-router` | proactive-router | proactive-router | permanent, overwritten each run |
| `cursors.action-sweep` | action-sweep | action-sweep | permanent, overwritten each run |
| `cursors.idea-spar` | idea-spar (Next watch) | idea-spar | permanent, overwritten each run |
| `cursors.kb-dream` | kb-dream | kb-dream | permanent, overwritten each run; `open_followups` drops an entry once it resolves or its escalated line is deleted |
| `cursors.session-log` | session-log | session-log | permanent, overwritten each run |
| `cursors.skill-health-check` | skill-health-check | skill-health-check | permanent, one entry per skill checked |
| `ideas.<key>.roadmap_last_seen` | idea-spar (Next watch) | idea-spar | permanent, overwritten when the slot changes |
| `ideas.<key>.pack_ref` | idea-spar, whenever it publishes a pack for a keyed idea | idea-spar (`decide`, the decision log's sources), briefing (via `runs.idea-spar.ref`) | overwritten by the next pack |
| `ideas.<key>.pack_pending` | idea-spar (Next watch sets on a move into Next, clears once the pack is published) | idea-spar | until cleared |
| `glossary` | proactive-router (`inline:promote` on a ticked `term:` line) | briefing | permanent, additive |
| `nicknames` | briefing (carried and added to) | briefing, kb-dream, session-log | permanent, additive |
| `registry.<category>` | proactive-router (a tick sets `set_by: user_tick`; shipped defaults ship with `set_by: shipped`) | proactive-router | permanent until reassigned |
| `tally.<category>` | proactive-router, per run outcome | proactive-router, kb-dream (monthly registry review), skill-health-check | permanent, counters only increment |
| `proposals` | proactive-router (opens a mapping on the first unmapped tick), kb-dream (folds and lifts) | proactive-router, kb-dream (dismisses after 60 days untouched) | until resolved or dismissed |
| `suppressions` | proactive-router (on delete) | proactive-router | permanent until lifted |
| `patterns_blocked` | proactive-router (after 3 deletions of the same channel+category pattern) | proactive-router | permanent until lifted |
| `items.<tag>` | whichever skill wrote the surface line | proactive-router, briefing, action-sweep (dedupe) | pruned when the line reaches Closed |
| `items.<tag>.status`, `.blocked_reason`, `.blocked_on`, `.blocked_at`, `.retried_for` | proactive-router, on its own `pr:` lines only, when a dispatch returns `blocked` | proactive-router (blocked-line retry) | cleared on retry; pruned with the item |
| `outcomes` | proactive-router, after each dispatch or inline action; skill-eval, when a manual run finishes | briefing (handler outcome summary and the manual close) | ring buffer, max 50, newest first |
| `voice_edits` | reply-draft, kb-note (append); reply-draft, kb-dream (set `edited`) | kb-dream (monthly voice review), skill-health-check | ring buffer, max 30 |
| `machines.<machine_id>` | onboarding, on tool discovery | every skill (reads its own machine's prefixes) | permanent, one entry per machine, re-resolved on failure |
| `machines.<machine_id>.cli`, `.cli_probed_at` | onboarding step 4 (local CLI probe); any skill clears `cli.<category>` when a CLI read fails and it falls back | every skill using a tracker or ideas read verb | re-probed after 7 days; absent on machines without the CLI |

## Write discipline

- **Write the smallest document that holds your change.** A skill with a shard writes its
  shard, not the main document. A skill without one writes the main document, and only when
  something in it changed.
- **Re-read immediately before writing.** State changes often enough between a skill's
  read at run start and its write at run end that a stale in-memory copy is not safe to
  write back verbatim. Re-read right before the write, apply this run's changes to the
  fresh copy, then write. One state read and one state write per run, per
  `token-discipline.md`.
- **Write only your own subtrees plus the shared counters.** A skill never rewrites another
  skill's `runs.<skill>`, `cursors.<skill>` or `items` entries it did not itself write.
  The shared exceptions are `tally.<category>`, which any dispatch outcome may increment
  by exactly the amount this run's ticks, edits and deletes justify; `ideas.<key>`, which
  only idea-spar writes; and `outcomes`, which the hub and a manual
  `skill-eval` run both append to.
- **Pass the page version where the connector supports it.** Confluence and similar
  connectors expose a version number on read; carry it into the write call so the
  connector itself can reject a write that landed on a version other than the one just
  read.
- **Retry once on conflict.** A version conflict means someone else wrote in between:
  re-read, reapply this run's own changes on top of the new version, write once more. A
  second conflict is not retried again; log the failure in `runs.<skill>.note` and stop.
- **Never rewrite a block you cannot parse; fast-fail instead.** If a subtree you need to
  read or update does not parse as expected, do not attempt to repair or replace it.
  Treat it the same as a missing key: fast-fail per `onboarding.md`, naming the block,
  and leave the document untouched.

## Retention

- **`outcomes`** is a ring buffer capped at 50 entries, newest first.
- **`voice_edits`** is a ring buffer capped at 30 entries, newest first.
- **`items`** entries are pruned once the surface line they describe reaches the Closed
  section. Pruning `items` is briefing's job, since briefing is the skill that moves
  lines into Closed.
- **`ideas.<key>`** entries stay while the idea exists; kb-dream's monthly pass drops any
  entry whose idea no longer exists on the tracker.
- **`glossary` and `nicknames`** are additive and have no cap.
- **Everything else** (`registry`, `tally`, `proposals`, `suppressions`,
  `patterns_blocked`, `machines`) has no automatic pruning; `proposals` entries are
  dismissed (not deleted) by kb-dream after 60 days untouched.

## Migrations

`installed_version` records the plugin version the state and board were last migrated to.
Only the skill that owns a migration runs it (for 1.0.0 to 1.1.0, `briefing`): it runs the
steps listed below for the versions between `installed_version` and the plugin's own
`plugin.json` version, in order, before doing anything else, then writes the new
`installed_version`. The trigger for every other skill is the board, not the version: a
skill that reads or writes the board and finds it still in the pre-migration shape (for
1.1.0, any pre-1.1.0 heading) records `runs.<skill>.status: quiet`, note `awaiting
migration`, and stops, and never writes `installed_version`. A skill that never touches
the board has nothing to race and runs as normal.

| From version | To version | Migration |
|---|---|---|
| 1.0.0 | 1.1.0 | Add `ideas: {}`, `cursors.action-sweep.chat_since`, `cursors.idea-scout`, and `ref` on every existing `runs.<skill>` entry (empty). Drop any `proposals` entry with `kind: skill_eval` (status `dismissed`, never deleted). The board itself is migrated by `briefing` alone, per `skills/briefing/references/migration.md`; every other skill that reads or writes the board and finds any pre-1.1.0 heading records `runs.<skill>.status: quiet`, note `awaiting migration`, and stops |
| 1.1.0 | 1.2.0 | The idea pipeline (`idea-scout`, `idea-deep-dive`, `idea-wireframe`) is replaced by `idea-spar`. Add `cursors.idea-spar` absent (its first run seeds and briefs nothing). Reshape each `ideas.<key>` to `{roadmap_last_seen, pack_ref: "", pack_pending: false}`, keeping `roadmap_last_seen` and dropping `requeue_scout` and `requeue_wireframe`. Set `registry.idea-decision.handler` to `idea-spar` (mode `decide`) and `registry.wireframe-reaction` and `registry.idea-refresh` to `handler: null`. Leave `cursors.idea-scout` in place, unread. On the board, `briefing` closes every open `<key>/q…`, `<key>/w-…` and `<key>/r` line as `retired` and prunes its `items` entry; open `<key>/d…` groups stay and now dispatch to `idea-spar` |
| 1.2.0 | 1.3.0 | Add `shards: {}` to the main document. Each skill that owns subtrees then creates its own shard on its next run, per **Shards**; until it does, it keeps using the main document. `briefing` runs this row and writes `installed_version` 1.3.0 |

A migration is always **additive**: it may add a new key with its default value, or
reshape a key it explicitly names, but it never deletes a key it does not understand.
An unrecognised key found during a migration is left exactly as it is.

## Proposal kinds

`proposals[].kind` takes one of three values, and the distinction is about who acts on an
accepted proposal:

| Kind | Raised by | A tick means |
|---|---|---|
| `mapping` | proactive-router | Map this category to this handler from now on |
| `suppression_lift` | kb-dream | Stop blocking this source-and-category pattern |
| `skill_fold` | kb-dream | A settled correction should become a rule in the named skill |

`skill_fold` is a **proposal about behaviour, and a tick is the user accepting the
proposal, never the system applying it.** kb-dream drafts the edit; a human makes it.
The former `skill_eval` kind is gone: the only path to `skill-eval` is now a red
`skill-health-check` score on the board, which the user ticks and then runs `skill-eval`
on themselves (see `handler-contract.md`, `manual:skill-eval`).
