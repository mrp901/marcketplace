# Next watch

The skill's only proactive behaviour. An idea moving into a Next slot on the roadmap is the
moment the user starts preparing to talk about it, so a pack waiting for them then is
useful. Before that moment, unprompted research is noise; this watch never runs a lens for
any other reason.

## Detection

1. One `ideas: search issues (JQL)` for ideas in `profile.ideas.project_key` updated since
   `cursors.idea-spar.roadmap_checked_at`, with fields covering `ideas.roadmap_field`,
   summary, assignee and `ideas.area_field`. Format the cursor in the `updated >=` clause as
   wall-clock time in `org.timezone`, `"yyyy-MM-dd HH:mm"`, with no offset: Jira reads a
   JQL date in the user's profile timezone, so a UTC clock time would be read as local.
2. For each result, compare the current slot with `state.ideas.<key>.roadmap_last_seen`.
   An idea whose current slot is in `profile.ideas.next_roadmap_values` and whose stored
   slot exists and is not has **moved into Next**. Store every current slot.
3. **No stored slot means seed, never a move.** On the first run (no cursor) and for any
   idea seen for the first time, store its slot and brief nothing. An idea already sitting
   in Next when the watch first sees it is not "moving"; the user can spar on it directly.
4. Every idea that moved into Next and passes the gate below gets
   `state.ideas.<key>.pack_pending: true`.

## The gate

The ideas board spans more than this install's product. Apply `profile.ideas.qualifiers`
first-match, from the search result's own fields only (no per-candidate full fetch):
`summary_has_product_tag`, `area_field_has_area_value`, `assignee_is_me`. A field that
can't confirm a qualifier fails it. A candidate failing every test is skipped silently: no
pack, no line, nothing recorded but the stored slot. A flagged off-domain pack still costs
the user a read, so there is no softer outcome. The roadmap slot itself is the trigger,
never a qualifier: "scheduled" is not "ours".

## The run

Take at most `budgets.idea-spar.next_per_run` ideas with `pack_pending`, oldest move first;
the rest wait for the next run.

1. `ideas: get issue` (full fields and comments) and build the known packet per `SKILL.md`.
2. Run all three lenses in order - challenge, reality, market - each against the same
   output contract. Unattended, nobody is there to reject a finding, so apply the packet
   drop rule strictly and keep `findings_per_lens` as a ceiling, not a target.
3. Sketch 2 to 3 options per `sketch.md` when any lens surfaced a layout or flow fork. No
   UI fork, no sketch; say so in one line in the pack.
4. Publish the pack per `pack.md`. Set `pack_ref`, clear `pack_pending`.
5. Board: `chat: read canvas`, settle this skill's own lines per
   `../../../shared/surface-protocol.md`, then in one write: the idea's block header if
   missing (`- <key> · <title> · pack`, with `pack` linking the page) and one decision group
   per real fork from the pack's "Decisions for you", at most 2, 2 to 4 options each, tagged
   `(<key>/d<n><letter>)`, category `idea-decision`, each ending with its tick effect
   (see "Line shape"). No fork: write nothing to the board; the
   pack still reaches the user through the briefing.
6. State: `cursors.idea-spar.roadmap_checked_at`, `ideas.<key>`, `items` (each option with
   `group: <key>/d<n>` and `idea_key`), `runs.idea-spar` with `note: "pack for <key>: <the
   question>"` and `ref: <pack link>`. Briefing reads `runs.idea-spar` and reports the pack.
   Stamp `runs.idea-spar.last_run_at` and the cursor with the current time in `org.timezone`
   and its offset, read from the clock at write time, never `+00:00`
   (`../../../shared/state-schema.md`, "Stamp the real local time"). The write first copies
   in any of its own `items` and `ideas` entries the main document still holds and its shard
   lacks (bar tags in `closed`), per `state-schema.md` "Shards"; the shared rule alone has
   been skipped.

**Order matters: pack, then board, then state.** The pack can't be published or saved:
leave `pack_pending` set so the next run retries, write no board line, and say so in
`runs.idea-spar.note`.

## Line shape

```
- FIG-204 · Load-plan variance alerts · pack
  - Channel first?
    - [ ] (FIG-204/d1a) 🔀 Email digest first: cheap, the digest job exists · tick → records your choice; siblings close
    - [ ] (FIG-204/d1b) 🔀 In-app first: needs a notification service built · tick → records your choice; siblings close
    - [ ] (FIG-204/d1c) 🔀 Both at once · tick → records your choice; siblings close
```

Every option is self-contained, reads as the decision a tick records, and ends with the
`idea-decision` effect from `../../../shared/surface-protocol.md`'s table, verbatim: `tick →
records your choice; siblings close`. The question line has no checkbox and no effect.
