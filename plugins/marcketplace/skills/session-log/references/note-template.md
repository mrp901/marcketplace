# Note template

## Path

`kb.paths.sessions` + `YYYY-MM-DD-short-slug.md`, per `kb-conventions.md`'s dated-file
naming rule - ISO date first, kebab-case, slug names the substance not the medium
(`2026-09-22-vault-okf-migration.md`, never `2026-09-22-claude-session.md`). If a note
already exists for that date and the new content is a genuinely separate occasion, add a
distinguishing slug rather than overwriting; a continuation of the same live session
updates the existing note in place instead (see `proposed-followups.md`'s "same live
session" clause).

## Frontmatter

```yaml
---
type: Session Log
title: <human title, dated - "(24 Aug 2026)" form, day + abbreviated month>
description: One sentence, used by the sessions index and previews.
tags: [session, <two or three from kb.tag_hints or existing vocabulary>]
status: draft
generated: { by: session-log, at: <ISO 8601, org.timezone offset> }
sources:
  - id: session-transcript
    resource: <relative path to the archived transcript, if one exists>
    title: session transcript
    last_modified: <date>
---
```

All six of `kb.frontmatter_required` - every note in the kb carries all six, so a note
missing one reads as an error even where the kb's own format would accept a bare `type`.
Omit `sources` entirely when the session left no archived transcript (an omitted field is
honest; a fabricated path is not). Never write `verified` on this note - it has had no
human review yet, and a machine-authored note claiming one would be the first kind of
trust tier the kb has never used (`kb-conventions.md`'s provenance rule).

## Body

Four sections, in this order; drop any that are genuinely empty rather than padding them:

```markdown
# Session - <title>

**When:** <date>, ~<duration> · **Where:** <tool/root> · **Prompted by:** <the ask>

## Decisions

- **<Decision>.** <Why, and what was rejected.> Feeds [decision record](../<kb.paths.decisions>/....md).

## Changes to the knowledge base

| Note | Change |
|---|---|
| [<note>](<relative link>) | <what changed> |

## Facts and corrections

- **Corrected:** <what was wrong>, <what's true now>. <what superseded it>.
- **Learned:** <fact>, from <source>.

## Open threads

- [ ] <What's unresolved, and what would resolve it.>
```

Give corrections their own bullet prefix; never fold one silently into "facts" as though
it were always the case. A knowledge base's own history is only useful if what it used to
believe, and why that changed, stays visible - that is exactly what a **Corrected** line
records and a smoothed-over "fact" line destroys.

## When the session changed an existing note

`generated.by` tracks who last changed the *content*, not who first wrote it - so when
this skill edits a note whose frontmatter says `generated: { by: human:<user> }`, that
becomes this skill and the timestamp becomes now (`kb-conventions.md`'s provenance rule).
Most notes pair `generated` and `verified` with identical timestamps, written and
confirmed in one motion; updating `generated.at` breaks that pairing; `verified.at` now
predates the content it claims to cover. This is legal - the two fields are independent by
design - but it needs to be visible, in the Changes table, not left silent:

```markdown
| [service map](../Product/service-map.md) | Detail added. `generated` now postdates
`verified: { by: human:<user>, at: 2026-08-18 }` - the human review predates this edit and
hasn't been redone. |
```

Leave `verified` alone otherwise: never delete it (erases a real review) and never bump
its date (fabricates one that didn't happen).
