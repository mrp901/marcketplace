# idea-scout - design rationale (for editors; not loaded at runtime)

- 29 Aug 2026: the roadmap clause was removed from the search after it produced two
  consecutive off-domain picks (one on Product Area *Integrations*; one on *Workflows* and
  *Reporting*). Ruling: the scout must confirm an idea is in scope before spending a run on
  it. Roadmap is still read and may be quoted in the note, but it never qualifies.
- The old "work it up anyway and flag it" behaviour for a non-qualifying idea was removed:
  a flagged off-domain note still costs the user a read and still lands in the research
  folder, so it is worse than nothing.
- Chat house style follows `briefing` (reference implementation).
- 2026-09-01 optimisation: per-candidate full fetch replaced by verifying from the search
  result's own fields (summary, assignee and the area field were already requested); the
  full fetch now happens for the winner only. A general competitive-research skill
  invocation was dropped (it loads a second skill and produces a long brief nobody reads)
  in favour of a handful of targeted searches. Knowledge-base reads scoped via indexes. A
  size guard was added on the kb's root log to avoid retyping a large history file on a
  full-replace connector. A glossary explaining the four product risks was removed - the
  model already knows them.

## 2026-09-22 port to marcketplace

Renamed from `cloud-idea-scout`. Ported per `PORTING.md`.

**Behaviours carried over, load-bearing and unchanged in substance:**
- **The qualifying gate and its first-match semantics.** Generalised from the source's
  single hardcoded three-test gate onto `profile.ideas.qualifiers`, keeping the same
  order and the same "first candidate that passes any one test wins" logic. See
  `references/qualifying-gate.md`.
- **Roadmap reported, never qualifying**, carrying forward the 29 Aug 2026 lesson above -
  restated explicitly in `references/qualifying-gate.md` so a future edit can't
  accidentally fold it back into the qualifier list.
- **The deleted "work it up anyway and flag it" behaviour stays deleted.** A non-qualifying
  candidate is skipped silently, full stop - also restated in `references/qualifying-
  gate.md` so this lesson survives independently of this HISTORY file, which isn't loaded
  at runtime.
- **Fast-fail, including "cannot confirm is a fail".** No candidate passes, the search
  returns nothing, or a needed field is missing - stop, nothing written anywhere.
- **Verify-from-search-result optimisation.** Only the winning candidate gets a full fetch.
- **The four product risks as an unexplained framing device**, and **decisions, not
  hedges** as the standard for the note's central section.
- **The budget discipline**, including the dropped general competitive-research skill and
  the kb log size guard.

**Behaviours generalised (mechanical, not a design change):**
- Slack canvas mechanics moved to `../../shared/surface-protocol.md`'s shared section
  table, line grammar and tag rules - this skill now shares "Ideas: decisions for you"
  with `idea-deep-dive` as documented there, rather than describing the canvas contract
  itself.
- The webhook call moved to `../../shared/notify.md`; this skill states only its own body
  shape (already listed in that document's per-skill table).
- Fixed org, tracker, ideas-board and vault facts moved to `profile.*` - see
  `profiles/extract/idea-scout.local.md`.
- Tool names replaced with category verbs per `../../shared/tool-capabilities.md`.

**Behaviours dropped:** none. Every fixed fact in the source skill had a generalised home;
see the extract file's "Notes on ambiguous or missing values" for the handful of prose
generalisations (scope marker, log size cap) that did not need a new profile key.

**Decisions made where the source skill was silent:**
- **`ideas.qualifiers` list order.** The source's three tests had a fixed evaluation order
  (tag, then area field, then assignee) but never stated why that order, specifically,
  rather than another. Kept the source's order exactly rather than re-deriving one, since
  changing it silently would change which candidate wins on a tie between two qualifying
  tests further down the walk order.
- **Note's `tags` frontmatter value.** The source hardcoded a product-specific tag set.
  Generalised to `[<product-area tag>, discovery, idea-board]` in
  `references/note-format.md` - the worked example there fictionalises this fully against
  `profiles/example.md`.

**No evals to port.** `source/cloud-idea-scout` ships no `evals/` directory and no eval
cases anywhere in its `SKILL.md` or `HISTORY.md` - there is nothing to re-fictionalise for
step 10. Flagging this rather than silently skipping the step: if the orchestrator wants
eval coverage for this skill, it needs writing fresh, not carried over.

**Open questions for the orchestrator:**
- `kb.paths.people_file` is listed as optional in `## Needs` (used only when naming a
  person in Research leads) but `profile-schema.md`'s key table lists `kb.people_file`
  (no `paths.` prefix) as the canonical path for the people/org registry, while
  `kb.paths.*` is documented as the standard subfolder map. I used `kb.paths.people_file`
  in `## Needs` by direct analogy with `kb.paths.research` immediately above it, but the
  schema's own key is `kb.people_file`, not a `kb.paths` entry. This looks like a mismatch
  worth a mechanical check against the actual schema key before merge - I did not invent a
  new key, but I may have miscited an existing one from memory rather than re-checking the
  table at time of writing. See the correction below.
- The surface's "carried-forward settle" step (checking ticked lines against real state
  before writing new ones) is restated from the source in `## Flow` step 6 and `##
  Surface`, but `handler-contract.md`/`surface-protocol.md` don't separately name this
  "settle first, then append" sequencing as a shared rule the way they name the snapshot
  rule or the tick/edit/delete table. It is preserved here as this skill's own procedure
  rather than promoted to a shared rule, since `idea-wireframe`'s port (source behaviour,
  not checked in this run) may or may not need the identical sequencing.

## 2026-09-22 correction: `kb.people_file`, not `kb.paths.people_file`

`profile-schema.md`'s key table lists `kb.people_file` (a top-level key, alongside
`kb.name`, `kb.kind`, `kb.local_root`) as the name-collision registry path - it is not one
of the `kb.paths.*` subfolder map entries. `## Needs` corrected to `kb.people_file`. Noted
here per the open question above, rather than silently fixed with no trace, so the
orchestrator can confirm the correction is right rather than re-discovering the same
ambiguity independently.

## 2026-09-25 canvas redesign (1.1.0): every tick means yes, do it

Three additions. **The block and the `decide` mode:** scout now writes the idea's block
header and one option group per real fork (at most two open), and a tick on an option
dispatches `decide`, which records the choice in the note's Decisions section, dated and
"decided by you", and clears the question. It handles `idea-deep-dive`'s `q` lines too, so
one handler owns the note. Before this, a decision ticked on the board went nowhere but
Closed. **The roadmap watch:** one extra JQL per run over investigated ideas; an idea
leaving a `parked_roadmap_values` slot gets a `/r` line, and the tick (`inline:requeue`)
sets `state.ideas.<key>.requeue_scout`. Requeues use state, not labels, so one tick is
enough. **Requeued first:** a refresh updates the note in place and adds a Refresh log
entry. Removed: the self-settling of its own ticked lines (the hub acts on ticks now) and
the webhook (`runs.idea-scout` is the record). `cursors.idea-scout.roadmap_checked_at` is
the one new cursor; the schema's "scout carries no cursor" note was corrected.
