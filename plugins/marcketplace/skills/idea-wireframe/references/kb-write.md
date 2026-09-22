# Saving the wireframe

Full detail for `SKILL.md` Step 6, following `../../../shared/kb-conventions.md` throughout.

## Files

Into `profile.kb.paths.prototypes`: `<idea-key>-<slug>.html` (the wireframe itself) plus a
compact wrapper note `<idea-key>-<slug>.md`.

## The note type

Check the live file at `profile.kb.types_registry` before asserting anything about what
types exist - never rely on this reference or any cached snapshot. If a wireframe-shaped
type (`Prototype` in the source instance) is not yet registered there, add it in the same
turn with a one-line justification rather than proposing it for later.

## Wrapper note frontmatter

```yaml
---
type: Prototype
title: <Idea title> - Low-Fi Wireframe (<idea key>)
description: One sentence on what it shows and the position it takes.
tags: [wireframe, prototype, idea-garden]
status: draft
generated: { by: idea-wireframe, at: <ISO 8601, org.timezone offset> }
sources:
  - scout note: <relative link to the research note read in Step 2>
  - idea: <the tracker browse URL>
---
```

No `verified` - nothing a machine writes carries it, per `kb-conventions.md`'s provenance
rule; it is added only by a human review.

## Body

A link to the HTML file, two to three sentences on what it shows, the frame used and the
shape that was rejected in Step 3, annotations keyed back to the four product risks and
decisions, and every source actually read in Step 2.

## Index, taste log and root log

1. One line in the prototypes folder's `index.md`: `* [<title>](<file>.md) - <description>`.
2. One line appended to the prototypes folder's taste log:
   `<idea key> | <frame used> | <fork resolved> | reaction: unknown` (create the file
   without frontmatter if it does not exist yet - it is a running log, not a note).
3. A line under the product area's own index pointing at the prototypes folder, if one does
   not already exist there.
4. A dated entry in the root log (`profile.kb.paths.log`), ISO date heading, leading bold
   verb - **only if the log file is under `profile.kb.log_size_cap_kb.writers`** (default
   20 KB). Over that bound, say the log line is outstanding on the surface item instead and
   leave rotation to the dreaming skill; do not retype a large full-replace file to add one
   line.

Uploads are byte-checked wherever the connector supports it: pass the expected byte count
and confirm it matches.

## Worked example

Fictionalised against `profiles/example.md` (Northwind Logistics / Freight Ops), for idea
`FIG-118`, frame 2 ("a tenth of the effort"):

```yaml
---
type: Prototype
title: Dock-Scheduling Conflict Warning - Low-Fi Wireframe (FIG-118)
description: One artboard showing the smallest warning that resolves the open double-booking fork from the research note.
tags: [wireframe, prototype, idea-garden]
status: draft
generated: { by: idea-wireframe, at: 2026-09-10T17:20:00+10:00 }
sources:
  - scout note: ../Research/fig-118-dock-scheduling-conflicts.md
  - idea: https://northwindlogistics.atlassian.net/browse/FIG-118
---
```

Body: "One artboard, the dock-scheduling grid with a single inline warning badge on a
conflicting slot. The research note left open whether conflict resolution needed a full
side panel or a lighter inline flag; this wireframe takes the inline position and costs the
side panel's detail view to do it - annotation 3 says so directly. Rejected: a full
modal-based resolution flow (frame 1's 'year after it ships' framing), since the captures
show the grid is already dense and a modal would hide the neighbouring slots a scheduler
needs to see while deciding. Read: `fig-118-dock-scheduling-conflicts.md`,
`Product/FreightOps/index.md`, three captures from `References/.../2026-08/`."
