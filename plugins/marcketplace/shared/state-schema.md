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
page passed 49 KB). So every skill keeps what it writes on a routine run in its own small
sibling document, and a quiet run rewrites a few hundred bytes. Sharding `runs` and
`cursors` alone (1.3.0) was not enough: `items` and `outcomes` stayed in a 27 KB main
document that every run posting a board line had to re-type, and runs judged that too risky
and skipped it, freezing the ledger the hub reads ticks against. **No routine run writes the
main document.**

- **What lives in a shard.** `runs.<skill>`, `cursors.<skill>`, any key only that skill
  writes (`ideas` for `idea-spar`; `tally`, `suppressions` and `patterns_blocked` for
  `proactive-router`; `closed` for `briefing`; `voice_verdicts` for `kb-dream`), and the
  writer's own entries of the three shared lists: `items` (the lines it owns by tag prefix),
  `outcomes` (`proactive-router`'s, and `skill-eval`'s one per run) and `voice_edits`
  (`reply-draft`'s and `session-log`'s capture mode; `kb-note`'s shard is frozen). Every skill has a shard.
- **What stays in the main state document.** Only keys written on a rare, user-driven
  event: `state_version`, `installed_version`, `profile_ref`, `shards`, `glossary` (a ticked
  `term:` line), `nicknames` (a new one), `registry` (a ticked mapping), `proposals`,
  `machines` (a tool re-resolved or re-probed).
- **Reading a list.** `state.items`, `state.outcomes` and `state.voice_edits`, wherever any
  skill's text names them, mean the union of the main document's entries and every shard's,
  and a write to one means the writer's own shard. Entry by entry (an `items` tag, a `tally`
  category, one list entry), the shard's copy wins; the main document's copy counts only
  while no shard holds that entry, and never once its tag is in `closed`. Those main copies
  are what the 1.6.0 migration removes. An `items` entry belongs to the owner of its tag
  prefix, whatever its `written_by` says. `outcomes` and `voice_edits` read newest first
  across the union. A skill that needs only its own entries reads its own shard and its
  own entries still in the main document.
- **Closures.** Briefing closes other skills' lines but never writes their shards. It adds
  each tag it closes or removes to `closed: {<tag>: <closed_at>}` in its own shard; every
  owner drops its own `items` entries whose tag is in `closed` on its next write, and
  every reader treats such a tag as closed, never as deleted. Briefing drops a `closed`
  entry once neither the main document nor any shard's `items` holds that tag.
- **Off the board.** A line with no action behind its tick (a plain to-do) is not on the
  board, but its `items` entry stays so `action-list` can read it (surface-protocol.md,
  "What goes on the board"). The owner of the tag writes `on_board: false` on its entry
  when it decides not to post the line. When `briefing`'s 1.12.0 migration takes an
  existing line off the board it cannot write the owner's shard, so it records the tag in
  `off_board: {<tag>: <moved_at>}` in its own shard; the owner sets `on_board: false` on
  its entry on its next write, and briefing drops the `off_board` entry once the entry
  carries it. Every reader treats a tag in `off_board`, or an entry with `on_board: false`,
  as open and not on the board: never deleted, never closed, never re-posted by its owner.
- **Retired shards.** A shard whose skill no longer exists (`vault-pulse`, `kb-note`,
  `idea-ticket`, retired in 1.11.0) is ignored by readers, and nothing requires deleting its
  page. The one exception is `kb-note`'s `voice_edits`: that shard is frozen (read-only, never
  written again) and still read, with `reply-draft`'s and `session-log`'s, deduplicated by
  `tag` (see the 1.10.4 to 1.11.0 migration row).
- **Pointer.** The main document carries `shards: {<skill>: <ref>}`, same ref format as
  `state_ref`; an absent `shards` key reads as `{}`. Onboarding step 2 reads this skill's shard by id.
- **A shard document** holds `shard_version: 1`, `skill`, `state_ref` (pointer back to the
  main document) and only that skill's subtrees, in the same shape as the main document.
- **Creating a shard.** Onboarding creates it on a skill's first run after the 1.3.0
  migration, when `shards.<skill>` is absent: copy that skill's subtrees from the main
  document into a new sibling document, write `shards.<skill>` in the main document in the
  same run, and leave the old subtrees in the main document until the next run confirms the
  shard reads back. The next run then deletes them from the main document. Shard first,
  pointer second, cleanup third, so a failure at any step leaves a readable state. When the
  main document is over the size guard, pointer and cleanup go in one write as soon as the
  new shard reads back: that write shrinks the main document, so the guard allows it,
  whereas a pointer-only write would grow it and be refused every run. Until
  the pointer exists, a skill reads and writes its subtrees in the main document as before.
  While the 1.6.0 migration is pending (`installed_version` below 1.6.0), a skill with no
  shard leaves creating it to `briefing`, whose migration write carries the pointer. A
  skill seeds its shard on every write with any of its own entries the main document holds
  and its shard lacks, bar tags in `closed` (a copy; `briefing`'s 1.6.0 migration removes
  the original).
- **Cross-shard access.** `kb-dream`'s monthly prune of `ideas.<key>` entries for ideas that
  no longer exist is the one routine write into another skill's shard (`idea-spar`'s); it
  reads and writes that shard by id and touches nothing else in it. The only other is
  `briefing` creating a shard during a migration. Readers of `voice_edits` also read the
  frozen `kb-note` shard (see Retired shards); nothing writes there.
- **Readers.** `briefing`, `proactive-router`, `action-sweep` and `skill-health-check` read
  every skill's `runs` or `items`, so each reads the main document plus every shard named
  in `shards`, by id. Every skill that owns a tag prefix also reads `briefing`'s shard for
  `closed`. `action-list` reads only `action-sweep`'s shard (its to-do `items`, on the
  board or off it), beside its own. A shard that cannot be read is reported as `runs: unreadable` for that skill;
  it never fails the reader, and a reader that cannot read a shard does not treat that
  skill's lines as deleted.
- **Size guard.** A skill that is about to write a document over 45 KB, main or shard,
  does not re-type it in full: it records `runs.<skill>.status: partial` with note
  `state too large to rewrite safely - shard or prune <document>` and stops. A write that
  cannot be reproduced faithfully is worse than a skipped one. **One exception, so the
  guard can never become permanent:** a write that leaves the document smaller than it was
  on read and under 45 KB (the migration, a pointer-plus-cleanup, a prune) is always
  allowed, and is re-read straight after and compared with what was intended; on a
  mismatch, restore the copy read at run start. When the only document the skill could
  record `partial` in is the oversized one itself, it records nothing and says so in its
  run output instead (briefing names it in its message), so the stall is never silent. The
  main document, with only shared keys left, should sit well under the limit; a shard that
  nears it means that skill's own subtree needs pruning. **Measure, don't assume:** the
  size is the byte length of the document body read this run, taken fresh each time. Never
  carry "over the guard" forward from an earlier run's note: after the reference instance's
  state fell to 27 KB, three later runs still reported it over the guard and skipped their
  `items` and `outcomes` writes. Under the guard, a rewrite is expected, not optional.

### Which write touches which page

A routine run writes one small page, its own shard. The main document is written only on
the events in the last column, and with only rare keys left in it, it stays small.

| Run | Reads | Writes on a routine run | Writes the main document only when |
|---|---|---|---|
| briefing | main + every shard | its shard (`runs`, `cursors`, `items` for `rb:` `term:` `feed:`, `closed`) | a migration, or a new nickname |
| proactive-router | main + every shard | its shard (`runs`, `items` for `pr:`, `outcomes`, `tally`, `suppressions`, `patterns_blocked`) | a `term:` promote, a mapping proposed or ticked |
| action-sweep | main + every shard (dedupe) | its shard (`items` for `sweep:`) | never |
| kb-dream | main, its shard, briefing's, the hub's (registry review), reply-draft's and session-log's (voice) | its shard (`items` for `dream:`, `voice_verdicts`); idea-spar's shard (monthly prune) | it records or dismisses a proposal |
| idea-spar, skill-health-check | main, its shard, briefing's (skill-health-check: every shard) | its shard (`items` for its own lines) | never |
| reply-draft, session-log (capture) | main, its shard | its shard (`voice_edits`) | never |
| skill-eval | main, the hub's, reply-draft's and session-log's | its shard (one `outcomes` entry) | never |
| action-list | main, its shard, `action-sweep`'s (to-do `items`) | its shard | never |
| jira-story, session-log | main, its shard | its shard | never |
| any skill, onboarding step 4 | | | it resolved or re-probed a tool prefix (`machines`) |

## The commented YAML

```yaml
state_version: 1
installed_version:           # from plugin.json; a newer plugin.json triggers the migrations below
profile_ref:                  # pointer back to the sibling profile doc
shards: {}                    # {<skill>: <ref>} - each skill's runs/cursors live in its own doc (see Shards)
# runs, cursors and ideas live in shards; of the keys after them, one marked "shard" lives in
# its writer's shard and the rest stay in the main document.

runs:
  <skill>: {last_run_at, status: ok | quiet | partial | fast-fail | error, machine, version, note, ref}
  # note: one line on what the run did (or why it stopped); ref: a link to the run's artefact
  # version: the plugin.json version this run read (onboarding step 6); "unknown" if it could not be read
  # proactive-router adds fyi: [<one line each, max 10>]
  # skill-health-check adds scores: {<skill>: {tag: green | amber | red, why, ref, checked_at}}
  # kb-dream adds health: {tag: green | amber | red, why, at}; why is one line under 200 characters, written to read alone in a chat message

cursors:
  briefing: {last_run_ts, last_seen: {<channel_id>: <ts>}}   # every channel briefing reads, feed channels included
  action-sweep: {scanned_through, chat_since}
  idea-spar: {roadmap_checked_at}
  kb-dream: {last_dream_at, last_full_dream_at, last_registry_review_at, last_voice_review_at,
             last_health_values: {<signal key>: <number>}}   # last health verdict's scored values, the next one's trend
  session-log: {last_pending_processed}
  skill-health-check: {last_checked: {<skill>: <date>}}

ideas:
  <idea key>: {roadmap_last_seen, pack_ref, pack_pending: false}

glossary: {<term>: <meaning>}
nicknames: {<email>: <nickname>}

registry:
  <category>: {handler: <skill> | inline:<name> | manual:<name> | null, mode, since, set_by: shipped | user_tick}

tally:                        # shard: proactive-router
  <category>: {proposed, ticked, deleted, edited, unmapped_ticks, last_ticked_at}

proposals: [{id, kind: mapping | suppression_lift | skill_fold, category, candidate, opened_at, status}]
suppressions: [{source_id, category, pattern: "<channel_id>:<category>", added_at}]   # shard: proactive-router
patterns_blocked: []          # shard: proactive-router

closed: {<tag>: <closed_at>}  # shard: briefing - tags it closed or removed whose owner has not yet pruned them
off_board: {<tag>: <moved_at>} # shard: briefing - tags it moved off the board (1.12.0 migration) whose owner has not yet marked them on_board: false
voice_verdicts: {<tag>: true | false}   # shard: kb-dream - its edited verdict on another skill's voice_edits entry

items:                        # shard: each writer's own entries, by tag prefix
  <tag>: {section, written_by, written_at, text, ref, category, group, idea_key,
          status: open | blocked, blocked_reason, blocked_on, blocked_at, retried_for,
          on_board: false}
  # text: the line exactly as written, compared verbatim with the board to spot an edit
  # pruned by its owner once briefing lists the tag in closed; group is the question's tag stem on an option line
  # status and the blocked_* fields are optional (absent = open); only the hub sets them, on pr: lines
  # on_board: absent = on the board; false = a to-do kept off it for action-list (its owner sets it)

outcomes: []                 # shard: each writer's; ring buffer, max 50, newest first: {tag, handler, status, report_line, recorded_at}
voice_edits: []              # shard: each writer's; ring buffer, max 30: {tag, register, draft_hash, sent_ref, recorded_at, edited}
                             # one entry per draft; edited is absent until a comparison sets it (or kb-dream's voice_verdicts does)

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
| `runs.<skill>.version` | that skill, in the same write: the `version` in `.claude-plugin/plugin.json` as this run read it | briefing (the mixed-versions line) | overwritten each run |
| `runs.proactive-router.fyi` | proactive-router | briefing | overwritten each run |
| `runs.skill-health-check.scores` | skill-health-check | briefing | one entry per skill scored, overwritten when re-scored |
| `cursors.briefing` | briefing | briefing | permanent, overwritten each run |
| `cursors.action-sweep` | action-sweep | action-sweep | permanent, overwritten each run |
| `cursors.idea-spar` | idea-spar (Next watch) | idea-spar | permanent, overwritten each run |
| `cursors.kb-dream` | kb-dream | kb-dream | permanent, overwritten each run; `last_health_values` is the previous verdict's scored values |
| `runs.kb-dream.health` | kb-dream, on a run that could measure it (a local shell and `kb.local_root`); left as it was otherwise | briefing (Runs block) | overwritten by the next run that measures |
| `cursors.session-log` | session-log | session-log | permanent, overwritten each run |
| `cursors.action-list` | action-list (`build`) | action-list | permanent, overwritten each run; `last_window_end` is where the next build opens |
| `cursors.skill-health-check` | skill-health-check | skill-health-check | permanent, one entry per skill checked |
| `ideas.<key>.roadmap_last_seen` | idea-spar (Next watch) | idea-spar | permanent, overwritten when the slot changes |
| `ideas.<key>.pack_ref` | idea-spar, whenever it publishes a pack for a keyed idea | idea-spar (`decide`, the decision log's sources), briefing (via `runs.idea-spar.ref`) | overwritten by the next pack |
| `ideas.<key>.pack_pending` | idea-spar (Next watch sets on a move into Next, clears once the pack is published) | idea-spar | until cleared |
| `glossary` | proactive-router (`inline:promote` on a ticked `term:` line) | briefing | permanent, additive |
| `nicknames` | briefing (carried and added to) | briefing, kb-dream, session-log | permanent, additive |
| `registry.<category>` | proactive-router (a tick sets `set_by: user_tick`; shipped defaults ship with `set_by: shipped`) | proactive-router | permanent until reassigned |
| `tally.<category>` | proactive-router, per run outcome, in its shard | proactive-router, kb-dream (monthly registry review), skill-health-check | permanent, counters only increment |
| `proposals` | proactive-router (opens a mapping on the first unmapped tick), kb-dream (folds and lifts) | proactive-router, kb-dream (dismisses after 60 days untouched) | until resolved or dismissed |
| `suppressions` | proactive-router (on delete; removes a pattern whose `suppression_lift` proposal is accepted), in its shard | proactive-router, kb-dream | permanent until lifted |
| `patterns_blocked` | proactive-router (after 3 deletions of the same channel+category pattern), in its shard | proactive-router, kb-dream | permanent until lifted |
| `items.<tag>` | whichever skill wrote the surface line, in its own shard (the owner of the tag prefix) | proactive-router, briefing, action-sweep (dedupe) | pruned by its owner once the tag is in `closed` |
| `items.<tag>.status`, `.blocked_reason`, `.blocked_on`, `.blocked_at`, `.retried_for` | proactive-router, on its own `pr:` lines only, when a dispatch returns `blocked` | proactive-router (blocked-line retry) | cleared on retry; pruned with the item |
| `items.<tag>.on_board` | the owner of the tag's prefix (`action-sweep` for an unposted `sweep:` to-do), `false` only | action-list (reads `action-sweep`'s `category: to-do` entries), proactive-router and briefing (never read as deleted) | pruned with the item |
| `off_board.<tag>` | briefing, in its shard, for each line its 1.12.0 migration took off the board | action-sweep (sets `on_board: false`), proactive-router (not deleted) | dropped once the owner's entry carries `on_board: false` |
| `closed.<tag>` | briefing, in its shard, for every tag it closes or removes | every skill that owns a tag prefix; proactive-router (closed, not deleted) | dropped once no document's `items` holds the tag |
| `outcomes` | proactive-router, after each dispatch or inline action; skill-eval, when a manual run finishes; each in its own shard | briefing (handler outcome summary and the manual close), kb-dream, skill-health-check | ring buffer per shard, max 50, newest first |
| `voice_edits` | reply-draft, session-log capture mode (append, each in its own shard); reply-draft (sets `edited` on its own entries) | kb-dream (voice re-sample), skill-health-check, skill-eval | ring buffer per shard, max 30 |
| `voice_verdicts.<tag>` | kb-dream, in its shard, when it settles an entry still missing `edited` | readers of `voice_edits` (an entry's own `edited` wins) | dropped once the tag leaves every `voice_edits` ring |
| `machines.<machine_id>` | onboarding, on tool discovery | every skill (reads its own machine's prefixes) | permanent, one entry per machine, re-resolved on failure |
| `machines.<machine_id>.cli`, `.cli_probed_at` | onboarding step 4 (local CLI probe); any skill clears `cli.<category>` when a CLI read fails and it falls back | every skill using a tracker or ideas read verb | re-probed after 7 days; absent on machines without the CLI |

## Write discipline

- **Write the smallest document that holds your change.** A skill writes its shard, not the
  main document. It writes the main document only when one of the main document's own keys
  changed (see "Which write touches which page"), never to add an `items`, `outcomes` or
  `voice_edits` entry.
- **Re-read immediately before writing.** State changes often enough between a skill's
  read at run start and its write at run end that a stale in-memory copy is not safe to
  write back verbatim. Re-read right before the write, apply this run's changes to the
  fresh copy, then write. One state read and one state write per run, per
  `token-discipline.md`.
- **Write only your own subtrees, in your own shard.** A skill never rewrites another
  skill's `runs.<skill>`, `cursors.<skill>` or `items` entries it did not itself write, and
  one document has one writer. `tally.<category>` is incremented by the hub alone, by
  exactly the amount this run's ticks, edits and deletes justify; `ideas.<key>` is written
  only by idea-spar; and `outcomes`, which the hub and a manual `skill-eval` run both
  append to, is kept by each in its own shard. A skill that needs another skill's entry
  changed records the fact in its own shard (`closed`, `voice_verdicts`) and leaves the
  entry to its owner.
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
- **Stamp the real local time.** `runs.<skill>.last_run_at`, every cursor and every `at:`
  is the current time in `org.timezone` with its offset, read from the clock at write time
  (`date`), never a UTC date reinterpreted as local and never a placeholder midnight. A
  cursor stamped before the real run time repeats a window; one stamped after skips it.

## Retention

- **`outcomes`** is a ring buffer capped at 50 entries, newest first, in each writer's shard.
- **`voice_edits`** is a ring buffer capped at 30 entries, newest first, in each writer's
  shard. kb-dream drops a `voice_verdicts` entry once its tag is in no ring.
- **`items`** entries are pruned once the surface line they describe reaches the Closed
  section. Briefing moves lines into Closed and lists each tag in its shard's `closed`;
  each owner prunes its own entries for those tags on its next write. Briefing drops a
  `closed` entry once no document's `items` still holds the tag.
- **Off-board `items`** (`on_board: false`) are pruned by their owner like any entry once the
  tag is in `closed`, and also when `written_at` is more than 30 days old: a to-do not worked
  in a month is stale, and `action-list` verifies the source before ranking anyway.
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
| 1.2.0 | 1.3.0 | Add `shards: {}` to the main document. Each skill that owns subtrees then creates its own shard on its next run, per **Shards**; until it does, it keeps using the main document. `briefing` runs this row and writes `installed_version` 1.3.0. If the main document is already over the size guard, `briefing` instead shards every skill in this one run, per `skills/briefing/references/migration.md` |
| 1.3.0 | 1.3.1 | No state change (the size guard gains its shrinking-write exception). `briefing` writes `installed_version` 1.3.1 |
| 1.3.1 | 1.3.2 | No state change (action-sweep's tracker-tag detection and routing change). `briefing` writes `installed_version` 1.3.2 |
| 1.3.2 | 1.4.0 | No state change. `cursors.kb-dream.last_voice_review_at` now advances only when a voice re-sample completes (ledger promotion keeps its markers in the knowledge base), and session-log's transcript sweep keeps its cursor in a local file beside `pending/`, not here. `briefing` writes `installed_version` 1.4.0 |
| 1.4.0 | 1.4.1 | No state change (the plugin gains an observe-only hooks module; it keeps its own session state, never this document). `briefing` writes `installed_version` 1.4.1 |
| 1.4.1 | 1.5.0 | No state change to the main document. `action-list` creates its own shard (`runs.action-list`, `cursors.action-list`) on its first run, per **Shards**. `briefing` writes `installed_version` 1.5.0 |
| 1.5.0 | 1.6.0 | `items`, `outcomes` and `voice_edits` entries, and `tally`, `suppressions` and `patterns_blocked`, move from the main document to their writers' shards, per **Shards**; every skill gets a shard. Each skill seeds its own shard on its first write; `briefing` creates the shards that do not exist yet and removes from the main document what now lives in a shard, in one shrinking write, per `skills/briefing/references/migration.md`. Entries with no installed owner stay where they are. `briefing` writes `installed_version` 1.6.0 when nothing owned is left in the main document |
| 1.6.0 | 1.7.0 | No state change (two direct skills added, neither writes state). briefing writes installed_version 1.7.0 |
| 1.7.0 | 1.8.0 | No state change to the main document. `vault-pulse` creates its own shard (`runs.vault-pulse`, `cursors.vault-pulse`) on its first run, per **Shards**. `briefing` writes `installed_version` 1.8.0 |
| 1.8.0 | 1.9.0 | No state change. A runner script and a session-start reminder were added for `vault-pulse`; both read files, neither writes state. `briefing` writes `installed_version` 1.9.0 |
| 1.9.0 | 1.10.0 | No state change. `session-log` gains a headless runner and the queue keeps one copy per session; both are local files, neither touches state. `briefing` writes `installed_version` 1.10.0 |
| 1.10.0 | 1.10.1 | No state change (two instruction folds: `voice.md`'s edits-ledger After side, `transcript`'s Step 5 length check). `briefing` writes `installed_version` 1.10.1 |
| 1.10.1 | 1.10.2 | No state change (`transcript` Step 5 checksums and write-tool batches; both hooks recognise a session-log run inside a session; `kb-dream` pass 1 fills Inbox YAML). `briefing` writes `installed_version` 1.10.2 |
| 1.10.2 | 1.10.3 | No state change (`profile.tools.notetaker.service` may be `none`; `budgets.action-sweep.chat_pages` is a new optional key with default 3; `idea-spar` stamps local time; `session-log` writes `runs.session-log` in the standard shape; the four 1.3.0 shard owners seed their shards on every write). `briefing` writes `installed_version` 1.10.3 |
| 1.10.3 | 1.10.4 | No state change (`briefing` expires an open line whose latest sub-line is `partial`, `blocked` or a router `queued` note after `briefing.stale_after_business_days` business days, default 5; that profile key is new and optional). `briefing` writes `installed_version` 1.10.4 |
| 1.10.4 | 1.11.0 | Skills are removed and no key is added to the main document. `vault-pulse` folds into `kb-dream`: its shard (`runs.vault-pulse`, `cursors.vault-pulse`) is retired and ignored, and `kb-dream` writes `runs.kb-dream.health` and `cursors.kb-dream.last_health_values` in its own shard on its next run. `kb-note` folds into `session-log` (capture mode): `session-log` writes new `voice_edits` entries only to its own shard and does not copy the old ones; the `kb-note` shard is frozen (read-only, never written again), and readers (`kb-dream`, `skill-eval`, `skill-health-check`) read `reply-draft`'s shard, `session-log`'s shard and that frozen shard, deduplicated by `tag`; `kb-dream` records its `voice_verdicts` against the entry wherever it sits. `idea-ticket` folds into `jira-story` (idea mode); its shard held only `runs` and is ignored. `kb-dream` drops `cursors.kb-dream.open_followups` on its next shard write (the follow-up escalation is cut; an existing escalated `dream:` line closes like any other, and 1.10.4's expiry catches a stuck one). `proactive-router` no longer writes `cursors.proactive-router.last_scanned` (the chat sweep is cut); readers ignore it. In its main-document write `briefing` rewrites any `registry.<category>.handler` that names `idea-ticket` (`ticket-idea`) to `jira-story`, and any that names `kb-note` (`kb-doc`, `summarise`) to `session-log`, keeping `mode` and `set_by` (an in-flight `file` second tick stays `file`); until it has, any handler name in the registry, a sub-line or `outcomes` that names a retired skill reads as its replacement; then writes `installed_version` 1.11.0 |
| 1.11.0 | 1.12.0 | The board holds decisions only, and every For you or Ideas line ends with its tick effect. New optional keys, none in the main document: `runs.<skill>.version` (each skill's next run stamps it), `items.<tag>.on_board` (`false` on a to-do `action-sweep` does not post, and on its entry for any tag in briefing's `off_board`, set on its next write) and `off_board: {<tag>: <moved_at>}` in `briefing`'s shard. In its ordinary board batch and shard write `briefing` takes each untouched, unticked `sweep:` line whose `items` entry has `category: to-do` off the board and into `off_board` (the entry stays, so `action-list` still reads it), appends the tick effect to its own untouched, unticked `rb:`, `term:` and `feed:` lines (and to those `items` entries' `text`), logs one `(migration)` line to Closed, then writes `installed_version` 1.12.0. Other owners' lines keep their wording and gain an effect only when their owner next writes them; an old line with none stays valid. No state shape is removed, so no other skill waits on this migration |

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
