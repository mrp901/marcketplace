# Note template

## Frontmatter

```yaml
---
type: <registered type - Decision Record-shaped or Reference-shaped, checked live>
title: <human title, dated notes carry a parenthetical readable date, e.g. (24 Aug 2026)>
description: <one sentence, used by the index and log>
tags: [kb-doc, <two or three from kb.tag_hints or existing vocabulary>]
status: draft
generated: { by: kb-note, at: <ISO 8601> }
---
```

Never write `verified` - this note has had no human review yet. Filename follows
`kb-conventions.md`'s dated-file rule when the note is anchored to a specific occasion
(a decision made in a specific meeting, a fact learned on a specific date); otherwise a
short descriptive kebab-case slug naming the substance.

## Body, decision-shaped

```markdown
# <title>

**Source:** <one line - what item.ref was (thread, ticket, email), who said it, when>

## Decision

**<the decision, stated plainly>.** <why, and what was rejected, if the source says so>

## Context

<what prompted it, grounded in the source's actual words - names, numbers, specifics>
```

## Body, reference-shaped

```markdown
# <title>

**Source:** <one line - what item.ref was, who said it, when>

## What this records

<the durable fact or constraint, stated plainly. If the source is ambiguous about any
part of it, say so here rather than picking a reading.>
```

## Index line

```markdown
* [<title>](<relative path>.md) - <description, verbatim from frontmatter>
```

## Log line

```markdown
* **Creation**: [<title>](<relative path to note>) - <one line on what it covers>
```
