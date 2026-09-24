# Sweep note structure

One dated note per run, named per `kb-conventions.md`'s dated-file rule:
`kb.paths.inbox` + `YYYY-MM-DD-action-sweep.md`. **One note per day - a same-day re-run
overwrites it, it does not create a second file.** This is the one place in this skill's
kb writing that departs from `kb-conventions.md`'s general "don't overwrite, add a
distinguishing slug" rule: a same-day action sweep is a re-run of the same mechanical
process, not a separate occasion, and that skill-specific carve-out is documented here
exactly as `kb-conventions.md` itself anticipates.

## Frontmatter

```yaml
---
type: Action Sweep
title: Action Sweep (<readable date>)
description: Outstanding actions from chat canvases, tagged tracker comments, assigned tickets, and recent meetings.
tags: [action-sweep, <org.product_tag or similar, if set>]
status: draft
generated: { by: action-sweep, at: <ISO 8601> }
scanned_through: <ISO 8601, this run's start time>
---
```

`type: Action Sweep` may be a new type for a given kb - check `kb.types_registry`'s live
file first per `kb-conventions.md`; if genuinely unregistered, add it there with a
one-line justification rather than adding it silently.

## Body sections, in this order

```markdown
# Action Sweep (<date>)

## From chat canvases
* {item, grouped under a `### <canvas name>` heading per canvas if more than one}

## Needs your reply (tagged, no response yet, no ticket already in motion)
* [KEY](url) {summary} - {one-line context on what's being asked}

## From recent meetings
* {action item}, {meeting name/date} - {one-line context}

## New tickets and amendments
{One full ticket-draft block per item, per `ticket-draft-formats.md`. Each new-ticket
draft is tagged with its routing tier per `sizing-and-routing.md`.}

## Currently assigned to you
* [KEY](url) {summary} - {status}
```

Omit a section entirely (never write "none found") only if genuinely empty - say so in
one line instead. Plain bullets, no scene-setting sentences, no editorialising about how
thorough the sweep was - if a line doesn't change what the user does next, cut it.

Cold start (no prior `scanned_through`) gets one stated line under the title: "No prior
sweep found - defaulting to a `cold_start_days`-day lookback."

## Anchors for delegate lines

Every candidate that becomes a delegate line on the surface (see `SKILL.md`'s
`## Surface`) needs a stable anchor back into this note - a heading or an ticket-draft
block's own `### Draft - <short title>` line is sufficient; the delegate line's `ref`
points at `<note path>#<anchor>`.

An anchor doesn't only come from the sweep flow's own step 3. `targeted`/`meeting`
handler dispatch creates one the same way, mid-run, for an item that arrived with no
anchor at all (a `proactive-router` classification, not one of this skill's own
candidates) - see `SKILL.md`'s Handler mode. Same note, same day, same "New tickets and
amendments" section; the only difference is when the draft got appended.
