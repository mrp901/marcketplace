# The dream note

`kb.paths.dreams/YYYY-MM-DD-dream.md` (`-2` suffix if one exists for that date). If the
folder doesn't exist: create it and its `index.md` (no frontmatter), register the note's
own `type` in the live `kb.types_registry` file with a one-line justification, and add the
folder to the knowledge base's own folder tables per its conventions file.

```yaml
---
type: Dream Log
title: Dream - <one clause of what happened> (<readable date>)
description: One sentence, lifted into the dreams folder's index.md.
tags: [meta, process, dream]      # existing vocabulary; at most one new topical tag
status: stable
generated: { by: kb-dream, at: <ISO 8601> }
---
# Dream - <title without date>

**When:** <date>, scheduled run · **Mode:** incremental | full · **Read:** log.md + N
session notes + inbox + <scope> · **Access:** <how this run reached the knowledge base>

## What I curated
| Change | File | Action | Why |
|---|---|---|---|

## Learned (signal extraction)
- **<fact>.** Recorded to [<memory entry>](../<path>.md). <source note, one clause>.

## Surfaced for you
- [ ] **<Judgement call, fold proposal, or insight>.** Why it needs you, concrete options.

## Flags
- **Stale:** ... · **Open follow-ups:** ... · **Name/fact watch:** clean | ... ·
  **Provenance timestamps:** clean | ... · **Failed writes:** ... (single occurrences;
  escalate on repeat, see `repetition-bar.md`) · **Machine-voice:** clean | N sentences
  rewritten · **Drafts reaped:** N · **Registry review:** (monthly only) · **Voice
  review:** (monthly only)
```

"What I curated" is a table because it is a ledger, not a narrative: one row per change,
four short cells, no cell running to a paragraph. Only "Surfaced" earns prose, and only
the sentence that makes the ask legible.

**Bad** (one row, one paragraph, mostly re-explaining a note that already exists):

> | Update | `log.md` - Backfilled three deferred entries for notes written by idea-scout
> and idea-wireframe. Each entry records what the note argues about the opportunity, the
> reasoning behind that position, which existing notes it links to, whether it has been
> added to the folder index, and the outcome of the attempted tracker label write, which
> was rejected by the screen scheme. |

**Good:**

> | Change | File | Action | Why |
> |---|---|---|---|
> | Update | `log.md` | +3 deferred entries backfilled | scout/wireframe runs exceeded connector rewrite threshold |
> | Index | `Dreams/index.md` | +1 row, newest first | today's dream note |

No `verified`. Drop empty sections. A near-empty dream is fine - "quiet dream, nothing to
curate; N follow-ups still open". A completely clean, insight-free pass may be a single
`log.md` line and no note at all - see `SKILL.md`'s quiet-run rule.

## Maintenance contract for this run's own writes

Every note or move this run makes owes, per `kb-conventions.md`'s index/log maintenance
contract: the affected folder's `index.md` line, the dreams folder's own `index.md` line,
and a root `log.md` line under today's heading with a bold verb. `log.md` is append-only:
a change that makes an earlier line stale gets a `**Correction**` entry, never a rewrite
in place - this applies to lines this same run wrote earlier today too.

**`log.md` line shape:** one line, not a paragraph - bold verb, path or link, what
changed, a very concise why. Keep every fact an audit would need (path, direction of a
move, old value of a corrected fact, the recycle path, whether a downstream write
succeeded or was rejected); cut everything that restates the note's own argument.

**Before finishing, resolve every link this run wrote** (dream note, index entries,
`log.md` lines) - a dead link written by this skill's own output surviving to the next
dream is the exact defect the link pass exists to catch, and it should never find one of
its own making.
