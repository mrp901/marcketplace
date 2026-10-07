# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- State shards (draft). Full-body-replace connectors made every run resend the whole state
  document, which passed 49 KB and became unsafe for a model to re-type. A skill's
  `runs.<skill>`, `cursors.<skill>` and skill-owned keys can now live in a small sibling
  document named by `shards.<skill>` in the main state document, so a quiet run rewrites a
  few hundred bytes. Opt-in per skill, additive, created lazily; a 30 KB size guard makes a
  skill record `partial` instead of re-typing a document it cannot reproduce faithfully.
  `machines` is now written only when a tool prefix changed. See `shared/state-schema.md`.
- Local CLI first for tracker reads. On a machine with a shell and Atlassian's Teamwork
  Graph CLI (`twg`) installed and signed in, `tracker`/`ideas` `search issues (JQL)` and
  `get issue` run through the CLI's summarised output instead of the connector, to keep
  large issue payloads out of context. Onboarding step 4 probes once per machine (cached
  in `state.machines.<id>.cli`, re-probed after 7 days, account-matched against
  `user.tracker_account_id`). Writes and wiki reads stay on the connector. Cloud sessions
  and routines, which have no `twg`, are unchanged. A failed CLI read falls back to the
  connector silently. New profile key `tools.<category>.cli: auto | off`; handler
  payloads carry an optional `cli` block.

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
