# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
