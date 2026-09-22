# Signal extraction

Generalises `source/_workspace-dream.SKILL.md`'s Phase 2/3 (auto-apply zone) to a
knowledge base whose session record is `session-log`'s dated notes, not a raw transcript
grep - this skill never reads a session transcript directly.

## Source

Every `kb.paths.sessions` note written since `state.cursors.kb-dream.last_dream_at`
(incremental) or all of them (full), up to `budgets.kb-dream.sessions_incremental` /
`.sessions_full`. Read each note's `## Decisions`, `## Facts and corrections` and
`## Open threads` sections - these are session-log's own distillation, already filtered
for signal, so this pass reads them rather than re-deriving signal from source material a
second time. `../scripts/signal_grep.py` runs a deterministic first pass over the same notes
for the four signal shapes below and hands back match context only (never full notes) to
narrow what needs a close read; it degrades to "no local read available, work from the
connector read alone" when the knowledge base is remote-only.

## The four signal shapes

- **Corrections** (highest value) - a `Facts and corrections` bullet prefixed
  **Corrected**, or session prose matching a correction shape.
- **Preferences** - a stated standing preference ("always...", "never...", "from now
  on...", "default to...").
- **Decisions** - a `## Decisions` bullet, or prose committing to a choice among named
  alternatives.
- **Recurring friction** - the same complaint or workaround appearing in more than one
  session note since the last dream.

For each finding, record: the fact, the date (the session note's own date, never today's),
confidence (explicit instruction is high, implied is medium), and any conflict with an
existing `kb.paths.memory` entry.

## Writing the memory entry (auto-apply zone)

One file per fact, dated single-fact entries under `kb.paths.memory`, following
`kb-conventions.md`'s frontmatter contract plus these fields specific to memory entries:

```yaml
---
type: Memory
title: <one clause naming the fact> (<readable date>)
description: One sentence.
tags: [memory, ...]
status: draft
generated: { by: kb-dream, at: <ISO 8601> }
source: <session note path>
fold_status: none | proposed | applied | not_needed
---
```

Rules, carried from the source pattern:

1. **Never duplicate.** Search `kb.paths.memory` first; update the existing file rather
   than writing a second one for the same fact.
2. **Absolute dates always.** "Yesterday" becomes the session note's own ISO date.
3. **Contradiction rule.** A newly found fact that contradicts an existing memory entry
   updates that file in place and appends `(Updated <date>, previously: <old value>)` -
   it does not get a second entry. This is the memory area's own append-only discipline,
   distinct from the knowledge base's own supersession mechanic, because a memory entry
   is small enough to correct in place without losing the prior value.
4. **Source attribution.** Every entry names the session note it came from.

`fold_status` starts `none`. It becomes `proposed` the moment `fold-proposals.md`'s pass
drafts a proposal against it, and `not_needed` if the settled correction turns out to be
purely factual with no skill output it constrains. `applied` is set only once real state
shows the proposed edit already landed in the target skill's own file - this skill still
never writes that edit itself; see `fold-proposals.md`.

