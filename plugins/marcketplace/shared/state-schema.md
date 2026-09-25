# State schema

## Purpose

State is the plugin's working memory: run history, cursors, the category-to-handler
registry and its tally, the item ledger the surface protocol needs to interpret ticks,
the idea pipeline's requeue flags, and per-machine tool-prefix resolutions. Like the
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

## The commented YAML

```yaml
state_version: 1
installed_version:           # from plugin.json; a newer plugin.json triggers the migrations below
profile_ref:                  # pointer back to the sibling profile doc

runs:
  <skill>: {last_run_at, status: ok | quiet | partial | fast-fail | error, machine, note, ref}
  # note: one line on what the run did (or why it stopped); ref: a link to the run's artefact
  # proactive-router adds fyi: [<one line each, max 10>]
  # skill-health-check adds scores: {<skill>: {tag: green | amber | red, why, ref, checked_at}}

cursors:
  briefing: {last_run_ts, last_seen: {<channel_id>: <ts>}}
  proactive-router: {last_scanned}
  action-sweep: {scanned_through, chat_since}
  idea-scout: {roadmap_checked_at}
  kb-dream: {last_dream_at, last_full_dream_at, last_registry_review_at, last_voice_review_at}
  session-log: {last_pending_processed}
  skill-health-check: {last_checked: {<skill>: <date>}}

ideas:
  <idea key>: {roadmap_last_seen, requeue_scout: false, requeue_wireframe: {feedback}}

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
  <tag>: {section, written_by, written_at, text_hash, ref, category, group, idea_key}
  # pruned when the line reaches Closed; group is the question's tag stem on an option line

outcomes: []                 # ring buffer, max 50, newest first: {tag, handler, status, report_line, recorded_at}
voice_edits: []              # ring buffer, max 30: {tag, register, draft_hash, sent_ref, recorded_at}

machines:
  <machine_id>: {tools: {chat: "mcp__...__", tracker: "...", ...}, kb_access, codebase_access, resolved_at}
```

The tracker labels (`investigated`, `wireframed`) remain the idea pipeline's first-pass
idempotency keys. A second pass on the same idea is driven by `ideas.<key>` instead: a
requeue flag set by one tick, cleared by the skill that acts on it, never a label change.

## Key-by-key table

| Key | Written by | Read by | Retention |
|---|---|---|---|
| `state_version` | onboarding, on bootstrap | every skill (compatibility check) | permanent |
| `installed_version` | onboarding, on every run (refresh from plugin.json) | every skill (migration check) | permanent, overwritten each run |
| `profile_ref` | onboarding, on bootstrap | every skill | permanent |
| `runs.<skill>` | that skill, at the end of its own run | briefing (the Runs report), skill-health-check | permanent, one entry per skill, overwritten each run |
| `runs.proactive-router.fyi` | proactive-router | briefing | overwritten each run |
| `runs.skill-health-check.scores` | skill-health-check | briefing | one entry per skill scored, overwritten when re-scored |
| `cursors.briefing` | briefing | briefing | permanent, overwritten each run |
| `cursors.proactive-router` | proactive-router | proactive-router | permanent, overwritten each run |
| `cursors.action-sweep` | action-sweep | action-sweep | permanent, overwritten each run |
| `cursors.idea-scout` | idea-scout | idea-scout | permanent, overwritten each run |
| `cursors.kb-dream` | kb-dream | kb-dream | permanent, overwritten each run |
| `cursors.session-log` | session-log | session-log | permanent, overwritten each run |
| `cursors.skill-health-check` | skill-health-check | skill-health-check | permanent, one entry per skill checked |
| `ideas.<key>.roadmap_last_seen` | idea-scout (roadmap watch) | idea-scout | permanent, overwritten when the slot changes |
| `ideas.<key>.requeue_scout` | proactive-router (`inline:requeue`, sets); idea-scout (clears) | idea-scout | until cleared |
| `ideas.<key>.requeue_wireframe` | idea-wireframe `react` (sets); idea-wireframe (clears) | idea-wireframe | until cleared |
| `glossary` | proactive-router (`inline:promote` on a ticked `term:` line) | briefing | permanent, additive |
| `nicknames` | briefing (carried and added to) | briefing, kb-dream, session-log | permanent, additive |
| `registry.<category>` | proactive-router (a tick sets `set_by: user_tick`; shipped defaults ship with `set_by: shipped`) | proactive-router | permanent until reassigned |
| `tally.<category>` | proactive-router, per run outcome | proactive-router, kb-dream (monthly registry review), skill-health-check | permanent, counters only increment |
| `proposals` | proactive-router (opens on `unmapped_ticks >= 3`), kb-dream (folds and lifts) | proactive-router, kb-dream (dismisses after 60 days untouched) | until resolved or dismissed |
| `suppressions` | proactive-router (on delete) | proactive-router | permanent until lifted |
| `patterns_blocked` | proactive-router (after 3 deletions of the same channel+category pattern) | proactive-router | permanent until lifted |
| `items.<tag>` | whichever skill wrote the surface line | proactive-router, briefing, action-sweep (dedupe) | pruned when the line reaches Closed |
| `outcomes` | proactive-router, after each dispatch or inline action; skill-eval, when a manual run finishes | briefing (handler outcome summary and the manual close) | ring buffer, max 50, newest first |
| `voice_edits` | reply-draft, kb-note | kb-dream (monthly voice review), skill-health-check | ring buffer, max 30 |
| `machines.<machine_id>` | onboarding, on tool discovery | every skill (reads its own machine's prefixes) | permanent, one entry per machine, re-resolved on failure |

## Write discipline

- **Re-read immediately before writing.** State changes often enough between a skill's
  read at run start and its write at run end that a stale in-memory copy is not safe to
  write back verbatim. Re-read right before the write, apply this run's changes to the
  fresh copy, then write. One state read and one state write per run, per
  `token-discipline.md`.
- **Write only your own subtrees plus the shared counters.** A skill never rewrites another
  skill's `runs.<skill>`, `cursors.<skill>` or `items` entries it did not itself write.
  The shared exceptions are `tally.<category>`, which any dispatch outcome may increment
  by exactly the amount this run's ticks, edits and deletes justify; `ideas.<key>`, which
  the hub sets and the idea skills clear; and `outcomes`, which the hub and a manual
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
- **`ideas.<key>`** entries stay while the idea is in the pipeline; kb-dream's monthly
  pass drops any entry whose idea no longer exists on the board or the tracker.
- **`glossary` and `nicknames`** are additive and have no cap.
- **Everything else** (`registry`, `tally`, `proposals`, `suppressions`,
  `patterns_blocked`, `machines`) has no automatic pruning; `proposals` entries are
  dismissed (not deleted) by kb-dream after 60 days untouched.

## Migrations

`installed_version` records the plugin version a skill last ran under. Every skill
compares it against the plugin's own `plugin.json` version at run start; a skill running
under a newer plugin version than `installed_version` records runs the migrations listed
below for the versions between the two, in order, before doing anything else, then writes
the new `installed_version`.

| From version | To version | Migration |
|---|---|---|
| 1.0.0 | 1.1.0 | Add `ideas: {}`, `cursors.action-sweep.chat_since`, `cursors.idea-scout`, and `ref` on every existing `runs.<skill>` entry (empty). Drop any `proposals` entry with `kind: skill_eval` (status `dismissed`, never deleted). The board itself is migrated by `briefing` alone, per `skills/briefing/references/migration.md`; every other skill that finds `installed_version` behind records `runs.<skill>.status: quiet`, note `awaiting migration`, and stops |

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
