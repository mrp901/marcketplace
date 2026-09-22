# marcketplace

A private, single-plugin Claude Code marketplace of product-management skills, driven by a
per-organisation profile document instead of hardcoded organisation details. Point the
`marcketplace` plugin at a profile (a Confluence page or a SharePoint/OneDrive file) and it
runs the same daily briefing, router, handler, idea-pipeline, and knowledge-base curation
skills against any organisation.

## Install

```
/plugin marketplace add mrp901/marcketplace
/plugin install marcketplace@marcketplace
```

Every skill in this plugin takes two invocation arguments: `profile=<ref>` (which profile
document to read; see `shared/onboarding.md` once ported) and `unattended` (present on any
scheduled or non-interactive run; its absence means the skill may ask questions).

Example:
```
/marcketplace:briefing profile=confluence:<cloudId>/<pageId> unattended
```

## Contributing / porting a skill

See [PORTING.md](PORTING.md) for the full procedure a subagent (or a person) follows to port
one skill into this plugin, including the house style, the scrub and line-budget checks, and
the definition of done.

## Status

This repository is under active construction (see `CHANGELOG.md`). The full usage guide,
skill roster, and cutover checklist land at `v1.0.0`.
