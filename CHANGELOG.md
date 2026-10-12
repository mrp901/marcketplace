# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [1.5.0] - 2026-10-13

A new direct skill, `action-list`, for the stretch of a day the board does not cover:
sitting down to clear a block of work. It builds a ranked, time-boxed list with ready
drafts into the knowledge base inbox, works a list item by item with the user, and closes
it on their word. This release also carries the organisation-literal clean-up below.

The repository carried its source organisation's private data in two places that the scrub
check could not see: the check's own pattern table, and the notify guard's hardcoded
deny-list. This release moves both out of the repository without weakening either check,
and finishes generalising the porting notes.

### Added
- `skills/action-list/` - `SKILL.md`, `HISTORY.md` and four references (list format,
  working an item, closing a list, a worked example against `profiles/example.md`).
  Direct only: no `## Handler mode`, never writes to the board, never dispatches a handler,
  never sends a message, and gates every tracker write, push and pull request on its own
  yes. Lists are transient drafts under `kb.paths.drafts`, so inbox triage leaves them be.
- A `codehost` tool category with one read verb, `codehost: list merged pull requests`
  (`shared/tool-capabilities.md`, `shared/profile-schema.md`, `profiles/example.md`).
  Optional. Served by the `gh` CLI, added to "Local CLI first" and to the onboarding probe
  (`gh auth status`); there is no connector, so without `gh` it degrades.
- Built-in WARN shapes `onedrive-path` (`OneDrive - <org>`) and `tracker-custom-field`
  (`cf[...]`, `customfield_...`), replacing the organisation-specific FAIL patterns that
  covered the same ground.
- `cursors.action-list` in `shared/state-schema.md`, and a 1.4.0 to 1.5.0 migration row
  (no change to the main document; the skill creates its own shard).
- README skill table row and a node in `docs/skill-flow.md`'s "your day" band.

### Changed
- `scrub_check.py` keeps only organisation-neutral shape patterns in the repository. The
  organisation's real names, ids, keys, vendors and codenames load from a gitignored
  `scripts/scrub_denylist.local.txt` (or the file named by `SCRUB_DENYLIST`), with
  `scrub_denylist.example.txt` documenting the format. The first line of output says which
  denylist loaded, or that none did; a named-but-missing or malformed denylist exits 2
  rather than silently checking less. `--list-patterns` shows each pattern's source.
- `guard_notify_channel.py` takes the blocked channel ids as trailing arguments (the caller
  passes every `profile.chat.tracker_feed_channels.*` id, per `shared/notify.md`) plus an
  optional `NOTIFY_BLOCKED_CHANNEL_IDS` environment variable, instead of two channel ids
  written into the script. Check order is unchanged: deny-list first, then exact allowlist
  match. See `skills/briefing/HISTORY.md`, 2026-10-12.
- CI (`ci/validate.yml`, `.github/workflows/validate.yml`) loads the denylist from the
  `SCRUB_DENYLIST` repository secret when it is set.
- `PORTING.md`, `docs/plans/canvas-redesign-issues.md`, `shared/profile-schema.md` and
  `skills/briefing/HISTORY.md` speak of "the source organisation" and role words; no
  organisation, repository, product or person name from the source install remains.
- `shared/onboarding.md` probes for `gh` alongside `twg`.

## [1.4.1] - 2026-10-11

### Added
- A hooks module (`hooks/register.ts`) beside the two classic session-log hooks. In this
  release it only observes and refuses nothing: it records whether a run is unattended and
  which skill it runs, which subagents are hub dispatches (handler, mode, tool-call
  budget), the profile's notify, feed and surface ids, and each state document's size and
  keys. It says what it saw in transcript notices the model never reads, beginning
  `marcketplace observer`, so a routine's transcript shows the module loaded. A failure in
  the observer is reported once per hook and never blocks a call. The guards that act on
  what it learns arrive in a later release (`docs/plans/guards-mod-build-plan.md`).
- `MARCKETPLACE_GUARDS` environment variable: `off` stops all observation except the load
  notice; `on` is the default. `warn` and `strict` are accepted and do nothing different
  until 1.4.0.
- Tests for the module (`claude plugin test plugins/marcketplace`, offline) and a local
  type-check config (`tsconfig.mods.json`). `ci/validate.yml` installs Claude Code 2.1.296
  and runs `claude plugin validate --strict .` and the tests.

### Changed
- `scrub_check.py` skips the TypeScript declarations Claude Code writes into
  `.claude-plugin/types/` when it loads the plugin from a folder; the folder is gitignored.

## [1.4.0] - 2026-10-09

A week of voice corrections and working sessions was mostly never captured: 39 ledger pairs
sat unpromoted, the monthly voice review failed and then waited a month, and about six
substantive sessions never reached the session queue. This release closes each route.

### Changed
- kb-dream promotes from `Voice/edits-ledger.md` on every non-quiet dream, unattended and
  from the knowledge base alone: a pattern recurring in 2+ ledger entries goes into its
  register note (or the avoid-list) automatically, citing the entries; a singleton becomes a
  `dream:` line, applied on tick. The chat and mail re-sample stays attended-only, falls due
  when `last_voice_review_at` is 30 days old and retries on every dream until done, instead
  of only on the first full dream of a month. See
  `skills/kb-dream/references/voice-review.md`.
- The voice register set is open-ended: the four in `voice.registers` are a floor, further
  register notes are discovered from `kb.paths.voice`, and kb-dream proposes a new register
  when 3+ ledger entries fit none. `shared/voice.md` now defines the edits ledger's writers
  and entry shape (compatible with existing entries, plus a `Said:` form and kb-dream's
  `Promoted:`/`Proposed:` markers).
- Session notes gain a `## Voice and tone feedback` section (verbatim corrections to how the
  user's writing reads), which kb-dream's extraction routes to the edits ledger, never to
  memory.

### Added
- The `SessionStart` hook sweeps recent Claude Code transcripts for substantive sessions the
  `SessionEnd` archive missed and queues them in `pending/` (conservative threshold, 2-hour
  idle rule, capped and cursored, `SESSION_LOG_SWEEP=0` to disable,
  `pending_sessions.py --dry-run` to preview). See
  `skills/session-log/references/pending-sessions.md`.

### Fixed
- action-sweep: a ticket's Open questions holds only other people's unaddressed mentions on
  the source issue and is omitted when there is none. The drafter's own doubts stay in the
  draft's own Open questions and are settled before the push tick (a ticket was filed with
  them).
- Timestamps: `generated.at`, the log date heading, `runs.<skill>.last_run_at` and cursors
  use the current time in `org.timezone` with its offset, not a UTC date or a placeholder
  midnight (kb-note, and the action-sweep, briefing and router state writes). See
  `shared/kb-conventions.md` and `shared/state-schema.md`.
- Size guard: measure the document just read instead of carrying "over the guard" forward
  from an earlier run's note. Skills kept skipping their `items` and `outcomes` writes after
  state had fallen well under 45 KB.

## [1.3.2] - 2026-10-09

### Fixed
- action-sweep missed tracker tags addressed to the user. Comments were fetched as markdown,
  which replaces a mention's account id with a placeholder, and a search-tier "is this really
  a question" filter then dropped real tags as "in passing". Comments are now fetched in the
  tracker's structured format and a tag matches on account id or the literal `@<user.name>`;
  every tag the user hasn't since addressed is a find, bar an explicitly bare "cc"/"fyi", and
  routes to `to-do` because it needs the user's own judgement. The tag scan covers issues the
  user is assignee or reporter on and still watches; an unwatch is a deliberate opt-out. See
  `skills/action-sweep/references/mention-search-method.md`.

## [1.3.1] - 2026-10-09

### Fixed
- The 45 KB size guard deadlocked the 1.3.0 shard migration on any install whose state was
  already over 45 KB: adding the `shards` pointer grows the main document, the guard refused
  that write, and every skill then stopped writing state, so cursors froze and runs repeated
  the same window. The guard now always allows a write that leaves a document smaller than
  it was and under 45 KB (re-read and compared afterwards). When the main document is over
  the guard, briefing's 1.3.0 migration shards every skill in one run and writes pointer and
  cleanup together, and a skill that cannot record `partial` anywhere says so in its run
  output instead of stalling silently.

## [1.3.0] - 2026-10-07

### Added
- State shards (draft). Full-body-replace connectors made every run resend the whole state
  document, which passed 49 KB and became unsafe for a model to re-type. Every skill's
  `runs.<skill>`, `cursors.<skill>` and skill-owned keys now live in a small sibling
  document named by `shards.<skill>` in the main state document, created by onboarding on
  the skill's first run after the migration, so a quiet run rewrites a few hundred bytes. A
  45 KB size guard makes a skill record `partial` instead of re-typing a document it cannot
  reproduce faithfully. `machines` is now written only when a tool prefix changed. See
  `shared/state-schema.md`.

## [1.2.0] - 2026-10-02

The idea pipeline is replaced by one interactive skill.

### Changed
- `idea-scout`, `idea-deep-dive` and `idea-wireframe` are replaced by `idea-spar`, a
  sparring partner for an idea you are actively working. Three lenses, each in its own
  reference file: **challenge** (the strongest case against), **reality** (what the code
  does today and what that makes cheap or expensive), **market** (what's out there, whether
  it matters to our positioning, whether it changes the outcome). Context you already have
  (the ticket, the kb, what you said) goes in as a known packet and is never restated.
  Every finding carries a source and a "so what".
- Wireframes are replaced by **sketches**: 2-3 alternative layouts at wireframe fidelity,
  built from a fixed mock component kit (`references/sketch-kit.html`), labels of three
  words or fewer, body copy as grey bars, one trade-off line per option. ASCII inline in a
  session, HTML in a pack.
- Output lands inline in the session; "pack it" publishes a shareable page (new tool
  category `page: publish`, falling back to a kb file).
- The only proactive run is the **Next watch**: an idea that moves into a
  `ideas.next_roadmap_values` slot gets a full pack, its forks go on the board as
  `<key>/d…` decision groups, and the briefing reports the pack link. `idea-decision` ticks
  dispatch `idea-spar` `decide`, which writes the idea's decision log.

### Added
- Profile keys `ideas.next_roadmap_values`, `tools.page`, `budgets.idea-spar`; state keys
  `cursors.idea-spar`, `ideas.<key>.pack_ref`, `ideas.<key>.pack_pending`.
- State and board migration 1.1.0 to 1.2.0: briefing closes old `<key>/q…`, `<key>/w-…`
  and `<key>/r` lines as `retired`; open `<key>/d…` groups stay and dispatch to idea-spar.
- `briefing` cross-checks two tracker-feed chat channels (work started, fix version
  changed) against the live tracker in one batched call and posts one `feed:` line in For
  you per contradicted claim. A tick runs `inline:investigate` (new category
  `feed-mismatch`). New profile keys: `chat.tracker_feed_channels.{work_started,
  fix_version}` and `budgets.briefing.feed_issue_keys`.

### Fixed
- `kb-dream` rotates `log.md` on its next run once it passes the writers' size cap, and an
  oversized log no longer counts as a quiet run, so a writer skill stops deferring its log
  line for weeks.
- `kb-dream` escalates a follow-up still open after three dreams to a `dream:` line.
- `proactive-router` retries its own blocked `pr:` lines once the profile key a block names
  is filled in.
- `skill-health-check` no longer counts every `voice_edits` entry as an edit: an entry
  records a draft, and only `edited: true` (set by the later comparison in `reply-draft` or
  `kb-dream`) counts. Stops `kb-note` drifting toward red on drafts kept as written.
- `skill-health-check`'s scoring rubric agrees with the skill: only a red score gets a board
  line.
- `reply-draft`'s worked example writes the draft to `Drafts/`, not `Inbox/`, so the model
  stops copying a path `kb-dream`'s draft reaping never looks in.
- `idea-ticket` no longer calls `voice.calibration_refs` undefined; the profile schema
  defines it.
- `state.items.<tag>` stores the line's verbatim `text` instead of a `text_hash` no script
  computed; the hub compares text directly (matches the router eval fixtures).
- `proactive-router` lists `machines` in the state it writes, and drops porting-era
  wording from its intro.

### Removed
- Categories `wireframe-reaction` and `idea-refresh`, the `inline:requeue` action, the
  `react` mode and taste log, the `investigated`/`wireframed` tracker labels (no skill
  writes a tracker label now), profile keys `ideas.labels`, `ideas.parked_roadmap_values`,
  `kb.paths.prototypes` and the three old `budgets` subtrees, and state keys
  `ideas.<key>.requeue_scout` and `.requeue_wireframe`.

## [1.1.0] - 2026-09-25

The canvas redesign: every tick means "yes, do it".

### Changed
- The board has five sections (Today, To-do, For you, Ideas, Closed) and a three-line
  header. The acknowledge/delegate split is gone; one tick table applies everywhere, with
  To-do as the only exception. Ownership is by tag prefix, not by section.
- Choices are option groups: a question line with one checkbox per option. Ticking two
  gets a `blocked · pick one` sub-line.
- One flow: the Router acts on every tick (dispatch, inline action, or option
  resolution); the Briefing only closes lines and reports.
- FYIs never go on the board. They are one line each in the briefing message.
- The Briefing is the only skill that posts. Every other skill records to `state.runs`
  and the message's new Runs block reports it, including fast-fails, amber and green
  health scores, and skills overdue against `briefing.expected_runs`. Per-skill webhooks
  and the proof-of-life post are gone.
- Fast-fails go to `state.runs`; the Plugin notices section is gone.
- `idea-scout` writes decision groups into idea blocks, records your ticked decisions in
  the research note (`decide` mode), watches the roadmap for a parked idea coming back,
  and refreshes requeued ideas first. `idea-deep-dive` writes its forks as option groups.
- `idea-wireframe` records your reaction to the taste log (`react` mode) and reworks on
  request; the critic ranks against real reactions. Requeues use state, not labels.
- `action-sweep` sweeps three new chat sources (your commitments, threads waiting on you,
  unanswered mentions), posts one line per find, and writes no dated note; a first tick
  drafts into `kb.paths.drafts/<tag>.md`, and `push` re-reads that draft. An unclear tier
  is a question with one option per tier. `reply-draft` accepts `chat-reply`.
- `skill-health-check` puts only a red score on the board; amber and green go to state. It
  owns the "output keeps getting edited" signal. `skill-eval` is manual only: run with no
  target, it lists queued red lines as candidates, and its outcome closes the line.
  `kb-dream` no longer self-settles its lines or raises `skill_eval` proposals.
- New shared contract `token-discipline.md`: quiet exits, fast-fail early, one job per
  run, subagents for bulk reading, lazy references, read once and write once, and never
  trading away a quality step. Every scheduled skill documents its quiet-exit condition.
- `plugin.json` now carries the same version as this changelog.

### Added
- `handler-contract.md` categories `chat-reply`, `to-do`, `term`, `idea-decision`,
  `wireframe-reaction`, `idea-refresh`, `skill-eval`; inline actions `inline:promote`,
  `inline:requeue`, `inline:to-do`; the `manual:skill-eval` queued sub-line.
- `state-schema.md`: `ideas.<key>` requeue flags, `runs.<skill>.ref`,
  `cursors.action-sweep.chat_since`, `cursors.idea-scout`, and the 1.0.0 to 1.1.0
  migration row. `profile-schema.md`: `ideas.parked_roadmap_values`,
  `briefing.expected_runs`, `budgets.action-sweep.thread_reads`.
- `briefing/references/migration.md`: the one-time board migration on the first run
  under 1.1.0.
- Six `proactive-router` eval cases: option pick, two picks, a line added under an idea
  block, an option edited then ticked, an `shc:` tick, a quiet run.
- `docs/skill-flow.md` redrawn for the new tick flow, and `docs/plans/` holding the
  redesign plan this release implements.

### Removed
- The `fyi` board line, the `skill_eval` proposal kind, `skill-eval`'s unattended
  proposal-driven mode and its handler mode, `action-sweep`'s dated Inbox note
  (`check_sweep_note.py` became `check_sweep_draft.py`), and every per-skill webhook.

## [1.0.0] - 2026-09-22

Thirteen skills, complete and validated against a fictional organisation.

### Added
- Daily loop: `briefing` (also the reporter) and `proactive-router` (the hub).
- Handlers: `reply-draft`, `kb-note`, `action-sweep`, `idea-ticket`.
- Idea pipeline: `idea-scout`, `idea-deep-dive`, `idea-wireframe`.
- Knowledge layer: `session-log` with plugin hooks, `kb-dream`.
- Meta: `skill-eval`, `skill-health-check`.
- Ten shared contracts, 54 reference files, 11 scripts.
- `check_refs.py`, which found eleven broken cross-references on its first run.

### Notes
- No organisation-specific literal appears anywhere under `plugins/`, enforced on
  every change.
- Every skill's always-loaded file is under 150 lines; the detail sits in references
  loaded on demand.
- Nothing irreversible happens without a tick, and a tick on one item is never
  authorisation for another.

## [0.1.0] - 2026-09-22

Foundation wave. Repository skeleton for the `marcketplace` Claude Code plugin marketplace:
marketplace and plugin manifests, the QA scripts that every later wave depends on
(`scrub_check.py` for organisation-literal detection, `line_budget.py` for the 150-line
`SKILL.md` cap), the porting procedure for subagents (`PORTING.md`), the GitHub Actions
validation workflow, and the stub README and `.gitignore`. No skills are ported yet.
