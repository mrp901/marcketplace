# Selection and context-gathering

Full detail for `SKILL.md` Steps 1 and 2.

## Step 1 - Select

**Requeued first.** Any idea with `state.ideas.<key>.requeue_wireframe.feedback` set is
this run's pick before the query below is even made, oldest `requested_at` first, one per
run. Its feedback text is the brief: the thing to change, in the user's words. The old
wireframe and wrapper note are read as the starting point, the `wireframed` label is
already present and stays, and the flag is cleared in the final state write. No tracker
write is needed to requeue, which is why one tick is enough.

Otherwise, `ideas: search issues (JQL)` against `profile.ideas.project_key`, fields
`summary, labels, status, updated, <profile.ideas.area_field>, <profile.ideas.roadmap_field>`:

```
project = <ideas.project_key> AND issuetype = <ideas.issue_type.name>
AND labels IN (<ideas.labels.investigated>) AND labels NOT IN (<ideas.labels.wireframed>)
ORDER BY updated DESC
```

Roadmap-first (nearest slot first, then furthest, then unset), then freshest within a slot.
If the roadmap field comes back empty on a candidate, fetch it rather than guess at its
slot. A tie inside one slot (updated within minutes of each other, suggesting a batch
labelling run) breaks toward whichever idea a wireframe would change an open decision for:
a candidate still in early discovery beats one already marked ready for delivery; a
candidate with no linked design beats one that already has one. Name whoever was passed
over, both in the run's own output and in the surface item's second line.

No results and nothing requeued -> exit quietly: `runs.idea-wireframe.status: quiet`, no
file, label or board line.

## Step 2 - Read, in order

Read the idea's full description, all comments, roadmap slot and theme via `ideas: get
issue`. Then the knowledge base, in this order - not a fixed checklist, an order, because
the sweep and the captures must land before the standing view is trusted:

1. **Sweep for what's new.** `kb: search` across `profile.kb.sweep_queries`, scoped to
   anything written after the earlier of the idea's `updated` timestamp or 7 days ago.
   Read hits under the product area, decisions and meeting-note folders; a slide deck or
   spreadsheet counts as a hit even if only its companion markdown note can be read
   directly - say so if only the binary exists. This exists because a document written the
   day after an earlier run once reframed a whole module and moved the next phase
   elsewhere; the standing list below is a snapshot, and snapshots go stale.

2. **Indexes before notes.** The product area's own index, the research folder's index, and
   the decisions index - they carry supersession notes in prose that a note on its own
   won't.

3. **Look at the product before drawing it - mandatory.** List `profile.kb.paths.screenshots`
   (newest first) and read the captures that cover the surface the idea touches. Take from
   them, specifically: navigation, filter controls and labels, chart types and time
   granularity, table columns, empty/inherited/unmapped-state conventions, footers, the
   flavour of sample data. Never infer appearance from prose when a capture exists for that
   surface. This is not a style preference - a first run drew a navigation rail that did
   not exist, used the wrong chart granularity, and declared something "out of scope" that
   two captures away was already shipped, all contradicted by captures sitting one folder
   over. No capture for the relevant surface -> annotate the appearance as inferred,
   plainly, in the wireframe itself.

4. **Taste.** A log of one line per past wireframe naming what the user actually did with
   it (`reaction: keep | drop | rework: <text> | unknown`), under
   `profile.kb.paths.prototypes`, filled in by the `react` handler mode from the user's
   ticks. It outranks every default in this skill: a frame the user dropped twice is a
   frame to stop using; a rework's text is the sharpest brief available. Skim the
   prototypes index only to avoid repeating a subject - never for shape or style. Copying
   the look of the last wireframe is the failure this rule exists to prevent.

5. **Standing list.** The matching note under `profile.kb.paths.research` is the brief - its
   position, its named risks, and its open decisions say what needs to become visible; its
   Decisions section (answers the user ticked on the board) outranks the note's own
   earlier hedges, so a decided fork is drawn as decided, not as a choice.
   Missing entirely -> build from the tracker fields and whatever context is in hand, and
   flag the missing note both in an annotation and in the surface item (the scouting skill
   itself may be failing). Product-area overview and discovery-brief notes, if any, read as
   intent; captures win on appearance, the newer artefact wins on direction. Read the
   service-map note only if feasibility is genuinely in play. Read
   `profile.kb.conventions_file` for house conventions. Check names against
   `profile.kb.people_file` first - a knowledge base with two people sharing a first name
   is common, and roles disambiguate better than names do.

## Precedence when sources disagree

Dated, human-authored artefacts (`generated: { by: human:<user> }`, decks, decisions) win;
between two of those, later beats earlier. Next, agent-written notes. Last, anything sitting
in an inbox or drafts folder - a lead, not a finding. Whenever a later artefact overrides an
earlier one, name both in an annotation rather than silently following the newer one.
