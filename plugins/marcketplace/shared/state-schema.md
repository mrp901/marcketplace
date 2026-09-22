# State schema

## Purpose

State is the plugin's working memory: run history, cursors, the category-to-handler
registry and its tally, the item ledger the surface protocol needs to interpret ticks,
and per-machine tool-prefix resolutions. Like the profile, it lives in a cloud-connector
document the user owns - a Confluence page or a SharePoint/OneDrive file - and never local
-only. The state document points back to the profile via `profile_ref`, and the profile
points to state via `state_ref`; they are two sibling documents, never one.

## Why two documents

State is written five to ten times a day; the profile is written once at bootstrap and
occasionally after that when the user changes something. Most of the connectors this
plugin supports (Confluence pages, SharePoint files) are full-body-replace: a write
resends the entire document, not a diff. That asymmetry is the whole argument for keeping
them apart:

- **Write-frequency asymmetry against full-body-replace connectors.** If profile and state
  shared one document, every routine run of every skill would resend the profile's org
  facts, tool choices and voice configuration along with its own cursor bump - multiplying
  the chance a stale in-flight write clobbers a profile edit the user just made. Splitting
  them means the high-frequency writer (a skill updating its own cursor) never touches the
  low-frequency content (the user's org facts).
- **Blast radius.** A bad state write - a malformed cursor, a corrupted tally - should
  never be able to take the profile down with it. Two documents means a broken state write
  degrades to "this skill re-scans from a stale cursor next run," not "the user's org
  facts are gone."
- **Ownership.** The user edits the profile directly, deliberately, rarely. Only the
  plugin edits state, and only its own subtrees. Mixing the two blurs a line that matters:
  a skill should never be in a position to overwrite something the user hand-edited.
- **Concurrency.** Two routines (the router and the reporter, per the two-routines
  decision) can run close together. Two separate state writes competing for one document
  is a narrower, more frequent race than either routine competing with a profile edit the
  user makes maybe once a month. Isolating the high-contention writes to their own document
  keeps the retry-once-on-conflict rule (below) cheap and rare in practice.

## The commented YAML

```yaml
state_version: 1
installed_version:           # from plugin.json; a newer plugin.json triggers the migrations below
profile_ref:                  # pointer back to the sibling profile doc

runs:
  <skill>: {last_run_at, status: ok | quiet | fast-fail | error, machine, note}

cursors:
  briefing: {last_run_ts, last_seen: {<channel_id>: <ts>}}
  proactive-router: {last_scanned}
  action-sweep: {scanned_through}
  kb-dream: {last_dream_at, last_full_dream_at, last_registry_review_at, last_voice_review_at}
  session-log: {last_pending_processed}
  skill-health-check: {last_checked: {<skill>: <date>}}

glossary: {<term>: <meaning>}
nicknames: {<email>: <nickname>}

registry:
  <category>: {handler: <skill> | inline:<name> | null, mode, since, set_by: shipped | user_tick}

tally:
  <category>: {proposed, ticked, deleted, edited, unmapped_ticks, last_ticked_at}

proposals: [{id, kind: mapping | suppression_lift | skill_fold | skill_eval, category, candidate, opened_at, status}]
suppressions: [{source_id, category, pattern: "<channel_id>:<category>", added_at}]
patterns_blocked: []

items:
  <tag>: {section, written_by, written_at, text_hash, ref, category}    # pruned when the item's line reaches Closed

outcomes: []                 # ring buffer, max 50, newest first
voice_edits: []              # ring buffer, max 30: {tag, register, draft_hash, sent_ref, recorded_at}

machines:
  <machine_id>: {tools: {chat: "mcp__...__", tracker: "...", ...}, kb_access, codebase_access, resolved_at}
```

Idea scout and wireframe carry no cursor in `cursors` - the tracker label
(`investigated`, `wireframed`) is their idempotency key, so there is nothing to remember
between runs beyond what the tracker itself already holds.

## Key-by-key table

| Key | Written by | Read by | Retention |
|---|---|---|---|
| `state_version` | onboarding, on bootstrap | every skill (compatibility check) | permanent |
| `installed_version` | onboarding, on every run (refresh from plugin.json) | every skill (migration check) | permanent, overwritten each run |
| `profile_ref` | onboarding, on bootstrap | every skill | permanent |
| `runs.<skill>` | that skill, at the end of its own run | briefing (reporter), skill-health-check | permanent, one entry per skill, overwritten each run |
| `cursors.briefing` | briefing | briefing | permanent, overwritten each run |
| `cursors.proactive-router` | proactive-router | proactive-router | permanent, overwritten each run |
| `cursors.action-sweep` | action-sweep | action-sweep | permanent, overwritten each run |
| `cursors.kb-dream` | kb-dream | kb-dream | permanent, overwritten each run |
| `cursors.session-log` | session-log | session-log | permanent, overwritten each run |
| `cursors.skill-health-check` | skill-health-check | skill-health-check | permanent, one entry per skill checked |
| `glossary` | briefing (promotes a ticked "Terms to learn" line) | briefing | permanent, additive |
| `nicknames` | briefing (carried and added to) | briefing, kb-dream, session-log | permanent, additive |
| `registry.<category>` | proactive-router (a tick sets `set_by: user_tick`; shipped defaults ship with `set_by: shipped`) | proactive-router | permanent until reassigned |
| `tally.<category>` | proactive-router, per run outcome | proactive-router, kb-dream (monthly registry review) | permanent, counters only increment |
| `proposals` | proactive-router (opens on `unmapped_ticks >= 3`) | proactive-router, kb-dream (dismisses after 60 days untouched) | until resolved or dismissed |
| `suppressions` | proactive-router (on delete) | proactive-router | permanent until lifted |
| `patterns_blocked` | proactive-router (after 3 deletions of the same channel+category pattern) | proactive-router | permanent until lifted |
| `items.<tag>` | whichever skill wrote the surface line (via the hub for delegate items) | proactive-router, briefing | pruned when the item's line reaches Closed |
| `outcomes` | proactive-router, after each dispatch | briefing (handler outcome summary) | ring buffer, max 50, newest first |
| `voice_edits` | reply-draft, kb-note | kb-dream (monthly voice review) | ring buffer, max 30 |
| `machines.<machine_id>` | onboarding, on tool discovery | every skill (reads its own machine's prefixes) | permanent, one entry per machine, re-resolved on failure |

## Write discipline

- **Re-read immediately before writing.** State changes often enough between a skill's
  read at run start and its write at run end that a stale in-memory copy is not safe to
  write back verbatim - re-read right before the write, apply this run's changes to the
  fresh copy, then write.
- **Write only your own subtrees plus tally increments.** A skill never rewrites another
  skill's `runs.<skill>`, `cursors.<skill>` or `items` entries it did not itself write.
  The one shared exception is `tally.<category>`, which any dispatch outcome may increment
  by exactly the amount this run's ticks/edits/deletes justify - never a wholesale rewrite
  of the tally block.
- **Pass the page version where the connector supports it.** Confluence and similar
  connectors expose a version number on read; carry it into the write call so the
  connector itself can reject a write that landed on a version other than the one just
  read.
- **Retry once on conflict.** A version conflict means someone else wrote in between - re-
  read, reapply this run's own changes on top of the new version, write once more. A
  second conflict is not retried again; log the failure in `runs.<skill>.note` and stop.
- **Never rewrite a block you cannot parse - fast-fail instead.** If a subtree you need to
  read or update does not parse as expected (corrupted YAML, an unrecognised shape), do
  not attempt to repair or replace it. Treat it the same as a missing key: fast-fail per
  `onboarding.md`, naming the block, and leave the document untouched.

## Retention

- **`outcomes`** is a ring buffer capped at 50 entries, newest first. When a write would
  exceed 50, the oldest entry is dropped.
- **`voice_edits`** is a ring buffer capped at 30 entries, newest first, dropped the same
  way.
- **`items`** entries are pruned once the surface line they describe reaches the Closed
  section - at that point the item's ledger entry has done its job (letting the surface
  protocol tell an edit from an untouched line) and is removed. Pruning `items` is
  briefing's job, since briefing is the skill that moves lines into Closed.
- **`glossary` and `nicknames`** are additive and have no cap; they are small, low-churn
  maps that are cheap to keep in full.
- **Everything else** (`registry`, `tally`, `proposals`, `suppressions`,
  `patterns_blocked`, `machines`) has no automatic pruning; `proposals` entries are
  dismissed (not deleted) by kb-dream after 60 days untouched, and a dismissed proposal
  stays in the list with `status: dismissed` as a record that it was raised.

## Migrations

`installed_version` records the plugin version a skill last ran under. Every skill
compares it against the plugin's own `plugin.json` version at run start; a skill running
under a newer plugin version than `installed_version` records runs the migrations listed
below for the versions between the two, in order, before doing anything else, then writes
the new `installed_version`.

| From version | To version | Migration |
|---|---|---|
| 1 | 1 | none - the empty migration for the current version, listed so the table format is proven before a real migration is ever needed |

A migration is always **additive**: it may add a new key with its default value, or
reshape a key it explicitly names, but it never deletes a key it does not understand.
An unrecognised key found during a migration is left exactly as it is - a future version
that does understand it will pick it up unmodified. This mirrors the "never rewrite a
block you cannot parse" rule above: migrations extend the schema forward, they do not
clean up anything they were not written to touch.

## Proposal kinds

`proposals[].kind` takes one of four values, and the distinction is about who acts on an
accepted proposal:

| Kind | Raised by | A tick means |
|---|---|---|
| `mapping` | proactive-router | Map this category to this handler from now on |
| `suppression_lift` | kb-dream | Stop blocking this source-and-category pattern |
| `skill_fold` | kb-dream | A settled correction should become a rule in the named skill |
| `skill_eval` | kb-dream | A handler's output keeps being edited; run skill-eval over it |

The last two are **proposals about behaviour, and a tick is the user accepting the
proposal, never the system applying it.** kb-dream drafts the edit; a human makes it. This
is the propose-only half of that skill's safety split and no tick collapses it.
