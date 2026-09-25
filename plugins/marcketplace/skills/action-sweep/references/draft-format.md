# Draft format

`targeted` and `meeting` write one draft per ticked line to `kb.paths.drafts/<tag>.md`
(`Drafts/sweep-260922-1.md`), following `../../../shared/kb-conventions.md`'s transient
drafts contract. The sweep itself writes no note: the For you line is the record of a
find, and a draft exists only once the user has ticked it. A second dispatch for the same
tag overwrites the draft; `push` re-reads it fresh, so an edit the user makes to the
draft between the two ticks is what gets filed.

## Frontmatter

```yaml
---
type: Draft
title: Draft - <short title> (<tag>)
description: <one line: what will be filed or commented, and where>
tags: [action-sweep, draft, <org.product_tag or similar, if set>]
status: draft
generated: { by: action-sweep, at: <ISO 8601> }
supersedes_on: pushed to the tracker, or the For you line closed without a push
source: <item.ref>
tier: small | larger | larger+defined | modification
---
```

`type: Draft` may be a new type for a given kb; check `kb.types_registry`'s live file
first per `kb-conventions.md` and add it there with a one-line justification if
genuinely unregistered. Drafts are never indexed; the kb log gets one `**Creation**`
line if under its size cap.

## Body

```markdown
# Draft - <short title> (<tag>)

**Line:** <item.text_as_ticked, verbatim>
**Source:** <what was read: the thread, the ticket, the meeting, in one line each>
**Route:** <tier> -> <project or parent, issue type> per sizing-and-routing.md

## Ticket
{One ticket-draft block per ticket-draft-formats.md, shape A for a new ticket or shape B
for a comment on an existing one.}

## Open questions
- {anything the draft had to assume, one bullet each; empty section omitted}
```

Plain, no scene-setting. If a line doesn't change what gets filed, cut it.

`../scripts/check_sweep_draft.py` validates the frontmatter and section shape before
the write.

## The push re-read

`push` reads the draft at `item.ref` in full, trusts the **Ticket** block as it stands
(the user may have edited it), files or comments per the **Route** line, and reports the
key. It never re-derives the draft from the source thread; the draft is the thing the
user approved.
