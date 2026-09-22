# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
