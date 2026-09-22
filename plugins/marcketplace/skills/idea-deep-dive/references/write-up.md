# Write-up

Whichever way the run ends, this is the whole write-up: note, surface, notify.

## The note

Update the idea's existing note in place if one exists; never create a second note for the
same idea. No existing note -> create
`kb.paths.research/<idea-key>-<slug>.md` following `kb.conventions_file`'s frontmatter and
section conventions plus the two fields below, and every rule in `../../../shared/kb-conventions.md`
(frontmatter contract, the type registry's single authority, link style, index and log
maintenance).

- Frontmatter carries `deep_dive_status: complete | stuck | loop-limit` (this run's end
  state) so a later run can detect a resume.
- **Resolved findings** - a section (new, or appended to if it exists from a prior run):
  every resolved question's answer, in prose, with its citation - this is where an answer
  actually lives, not just the log line that references it.
- **Open questions** - refreshed: resolved items removed (they are in Resolved findings now);
  every question still in the queue is kept here regardless of whether it has been attempted
  yet - untried (including an incidental spawn never reached before the run ended), PENDING
  (shown with what it is waiting on), or stuck (flagged with its missing input - normally one
  question, but a depth-cap cascade produces a whole chain of stuck items; list every one of
  them, not just the leaf). Empty in a **complete** run.
- **Decisions for you** - its own section, separate from Open questions, untouched.
- **Run state** - the queue as it stands at the end of the run: remaining question IDs,
  chain-depth, which circles each has already exhausted, PENDING/blocked-on relationships.
  This is what makes the note the actual resume point, not just a status line.
- **Deep-dive log** - loops used vs. budget, each question resolved with which circle
  answered it and how many searches that attempt used (including the sweep's own counts, all
  four), any spawned-question lineage ("Q4 - spawned by Q2, blocking; resolved via code, 2
  searches"), and status this run ended on.

## The surface

Append-only, to `surface.id`, section "Ideas: decisions for you" (`chat: read canvas` first
for current section addressing; create the section if it is somehow missing, and say so).
Only an actionable end state gets an item; a clean **complete** run with nothing in Decisions
for you writes nothing here. One checklist line per item, same tagging convention `idea-scout`
uses so the two skills' items sit in one list:

- **complete**, with items in Decisions for you -> one line per decision:
  `- [ ] (<idea-key>) {the fork, options implied}`.
- **stuck** -> one line per stuck item (a depth-cap cascade gets one line per item in the
  chain, root to leaf): `- [ ] (<idea-key> - stuck) {the question, what was checked, what's
  needed from the user}`.
- **loop-limit reached** -> `- [ ] (<idea-key> - paused) {how many questions remain; a re-run
  continues from the note, no separate tracking file}`.

Never tick or delete an item written by another run (this skill's own earlier pass, or
`idea-scout`) - ticking or closing those out is the user's call or that other run's, not this
write-up's.

## Notify

Fired once per run, after the note is saved and the surface step (if any) completes, per
`../../../shared/notify.md`. Body shape (`notify.md`'s per-skill table):

```json
{"ticket": "<idea-key>", "outputUrl": "<path to the note>"}
```

## Settling the shared section

This skill appends to the same surface section `idea-scout` writes to, and both revisit it.
Before appending this run's items, settle this skill's own existing lines in that section
per "Settle before you append" in `../../shared/surface-protocol.md`: confirm what a tick
claims against real state, leave an edited line's wording alone, never re-add a deleted
line, and never re-post an item still sitting there untouched. Settle only lines this skill
wrote; `idea-scout`'s lines are its own to settle.
