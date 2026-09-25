# Gathering evidence, by skill type

For every skill in the roster (`SKILL.md` step 1), gather from whichever of these apply. A
skill can match more than one row - `action-sweep`, for instance, is both a kb-writing skill
(when it writes a note) and a tracker-writing skill (when it pushes). Gather every row that
applies to that skill; skip a row cleanly (and say so in the evidence-sources line) when it
doesn't.

## Knowledge-base-writing skills

Any skill whose `## Surface` or `## Flow` names a `kb: write`. Find the notes it produced
since the evidence window opened (match `generated.by` in frontmatter against the skill's own
name, or the folder/naming pattern that skill's own `SKILL.md` documents - e.g. `Dreams/` for
`kb-dream`). For each note:

- **Was it later corrected or superseded by a note the user wrote** (`generated: { by:
  human:<user> }`)? This is the strongest negative signal available - `kb-conventions.md`'s
  own precedence rule already treats a human correction of machine content as "the machine
  note was wrong"; this skill reuses that rule rather than re-deriving it.
- **Does it carry `verified: { by: human:<user> }`?** Positive signal - the user reviewed and
  accepted it as written.
- **Do its relative links resolve, and does it appear in its folder's `index.md` and in the
  root log?** Objective and cheap to check - actually walk the paths, don't rely on an
  impression of the note's conformance.
- **Is it cross-linked *to* by anything later?** A note nothing downstream ever references is
  a weaker outcome than one a later note or ticket cites.
- **Was the surface item it came from ticked and cleared within a reasonable time**, or does
  it still sit open untouched? Read the line the note's skill owns on the board (`chat: read
  canvas`). A long-stale item is a weaker outcome than one closed out
  quickly.

## Tracker-writing skills

Any skill whose `## Handler mode` or `## Flow` names a `tracker: create issue` or `tracker:
add comment`. Look at issues created or commented on since the evidence window opened
(`tracker: search issues (JQL)`, scoped to that skill's own project/component where known).
For each:

- **Was it materially edited shortly after creation** (title, description, priority changed
  within the same day or two, via `tracker: get issue`)? Suggests the draft needed real
  correction.
- **Did it progress through a normal transition** (triaged, actioned) rather than sit
  untouched or get closed as invalid?

## The hub's outcome record and tally

Read `state.outcomes` (ring buffer) and `state.tally` for every handler this skill's roster
covers, per `shared/state-schema.md` and `shared/handler-contract.md`. This needs no
connector call beyond the state read every run already makes - it is the cheapest evidence
source in this skill and should never be skipped for a handler that has one.

- **Repeated `blocked` or `partial` outcomes** for one handler is a direct negative signal -
  the handler contract's own return values already say the dispatch didn't finish cleanly;
  this skill just counts how often.
- **A category whose lines the user keeps editing** (`tally.<category>.edited`, rising faster
  than `.ticked`) says the classification or drafting for that category keeps missing the
  mark, even when individual dispatches report `done`. This signal is this skill's to
  raise: an edit rate above half over at least three ticks is an amber on the handler for
  that category, and above two thirds over at least five is a red. `kb-dream`'s registry
  review no longer raises a separate proposal for it.

## The voice ledger

For a drafting skill (`reply-draft`, `kb-note`, `idea-ticket` - anything listing `voice` in
its own `## Needs`), read `state.voice_edits` entries recorded since the window opened. Each
entry (`{tag, register, draft_hash, sent_ref, recorded_at}`) is a direct measure of how often
the user edited a draft before acting on it. A cluster of edits in one register is a sharper
signal than a general "voice felt off" impression - name the register in the evidence bullet.
This is cheap: the ledger is already maintained by the drafting skills themselves per
`voice.md`'s compounding mechanism, so this skill only reads it, never recomputes it.

## Skills with no reliable automatic signal

A skill whose only externally-visible act is a chat post with no tick/edit mechanism (the
reporter, `briefing`, for its own posted message - not its surface writes, which are covered
above) has no reliable automatic signal for whether the user read or acted on it. Say this
plainly in the log rather than fabricating a score: record only what's checkable (did it post
on schedule, did it hit the right channel/format) and mark the rest "no automatic signal
available".

## What this skill judged too expensive to add

Re-reading full transcript content behind a voice-ledger entry, or re-diffing a tracker
issue's full changelog field-by-field, would turn this skill from a cheap periodic check into
a heavy per-item audit - exactly the shape `skill-eval`'s own single-run, human-triggered
capture already covers better. This skill stays at the level of "did the outcome/tally/ledger
already say something happened", never "let me re-read everything and form my own opinion of
the quality".
