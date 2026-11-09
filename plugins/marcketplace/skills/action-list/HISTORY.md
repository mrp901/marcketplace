# action-list - design rationale (for editors; not loaded at runtime)

## 2026-11-09 customer notes as context and as I-owe candidates (1.13.0)

When a candidate or the prep names a customer, its living note is read first (one read, max 3 per
run). Its `We owe` lines are extra I-owe candidates, verified against their linked source like any
other; only the user's own promises get the ranking boost (unchanged rule). Detail in
`references/i-owe.md` and `references/one-to-one-prep.md`; the note's contract is
`shared/customer-notes.md`.
## 2026-11-04 "I owe" section and 1:1 prep (1.12.0)

The owner works in attended sessions and through this skill, rarely from the board, and loses
track of things he told people he would do ("I can check about Q2", "you said you would go back
to Lisa"). The only record of those was scattered: a chat message, a to-do `action-sweep` had
found, an open thread in a session note. So `build` now leads with an **I owe** section (who
it is owed to, what, when promised, age in business days, a link) and ranks an owed row above
any other of equal urgency; `prep` is a second shape of the same skill, "prep my 1:1 with
<person>", built from the same sources plus the kb's earlier 1:1 notes.

**Design choices, with reasoning:**

- **No new sources, one new read.** The extraction subagents already read chat, tracker,
  transcripts and session notes, so each is asked to flag commitments rather than a new
  subagent being added. State adds one read, `action-sweep`'s shard (its to-dos), because from
  1.12.0 those are no longer on the board and this skill is where they now surface. Promises
  older than the list window are why the chat search reaches back 14 days (up to 3 pages) and
  session-note threads 30 days; both horizons are constants here, not profile keys, because a
  skill reads only its own `budgets` subtree.
- **A quote or no row, and promises are not asks.** "I owe" is a claim about what the user said.
  Only a to-do whose evidence carries the user's own promise ("I'll", "you said you would", "as
  you told Ivan") is owed and earns the ranking boost; a to-do where someone tagged or asked the
  user is "Waiting on you": listed, no boost. An offer ("let me know if ...") is not a promise.
  Extractors (cheap tier) return every candidate and decide nothing; the worker applies "What
  counts". An early draft told extractors to drop non-promises, which would have lost oddly
  phrased real ones.
- **Verification is capped at 10 per build** (and per prep), owed rows first, so the read count
  is bounded; the rest are listed `unverified` with their age. A to-do found done is recorded in
  this skill's `settled` list so `action-sweep` prunes it; nothing else closes an off-board
  to-do.
- **Owed rows are not described twice.** A promise that is also a ranked action carries a `Row`
  pointer; the row holds the draft and the section holds the promise.
- **1:1 prep finds its sources through the kb's own conventions**, not a hardcoded folder: the
  people file, the conventions file's folder table, then a search. The owner's vault keeps 1:1
  prep notes under onboarding and meeting notes under meetings; another org's will differ.
  Names resolve through `people`, `kb.people_file` and `people_confusions` and an ambiguous
  first name is asked once, never defaulted (the owner's vault has several pairs and a foursome
  of people who share a first name).
- **Prep does not move `last_window_end`.** It is not a window.

**Open questions:** how many past meetings "recent themes" should read (4 now); whether prep
should also look at the calendar for the next 1:1's time (it does not, so the note carries a
date, not a time); whether "what do I owe people" deserves its own short output instead of a
full list with only the section.

## 2026-11-03 notetaker none (1.10.3)

The user has no notetaker. With `notetaker.service: none` the transcript source is skipped
silently, not reported as unreachable.

## 2026-10-13 built from a working afternoon

The user had Claude build a ranked "post-lunch" action list with ready drafts into the
knowledge base inbox, then came back with "bootstrap a few things listed in the lunch
file", worked one item through to a spec pull request and three tracker writes, and closed
the list with "all items on that list are done". Asked which part of that session to keep,
they chose the action list: building one, working one, or both, with the mode asked when
unclear.

**Design choices, with reasoning:**

- **Direct only, no board, no dispatch.** The hub owns ticks and handler dispatch
  (`../../shared/handler-contract.md`), and the board holds things that need a tick. A
  list worked with the user beside Claude is a different shape: a person clearing a block
  of time. So this skill has no `## Handler mode`, never writes to the surface, reads the
  board only for a "backlog, not today" section, and works items itself in conversation
  rather than handing them to marcketplace handlers.
- **Overlap with `action-sweep`, deliberately kept.** Both read chat, tracker and
  meetings for things the user owes. `action-sweep` turns each find into a board line that
  waits for a tick; `action-list` ranks a whole window against the free time in the
  calendar and drafts everything up front, in one note. This skill's description
  asks for a list "to work through now" and ends "Not for sweeping actions onto the
  board", so "sweep my actions" and "what's outstanding" still reach `action-sweep` and
  `briefing`; their descriptions were left unchanged.
- **Lists live in drafts, not the inbox.** `kb-dream`'s inbox triage files anything it
  can, and can run several times a day, so a list in the inbox could be filed away before
  it was worked. A list is a transient draft under `kb-conventions.md`: unindexed, with a
  `supersedes_on` note, reaped once closed or stale.
- **Unattended fast-fails.** `build` could run unattended, but nothing schedules it yet;
  until a schedule is added on purpose, both modes need the user.
- **Every external write gets its own yes.** The user chose this over one yes per item.
  It follows `idea-ticket`'s direct-invocation gate: show the full text, wait, write.
  Messages are drafted, never sent, per the plugin-wide rule.
- **Re-check before acting.** On the source run the list said a ticket question was open;
  the user had answered it an hour later. The list is a snapshot, so `work` reads each
  item's source again before acting on it.
- **Follow the item's own process by its files.** The source run's item named a
  repository's spec-authoring skill, its git working agreement and its templates. Reading
  and following those in order, in a separate worktree, is what produced a reviewable pull
  request; a general approach would not have.
- **Read the answer, not the option.** Several answers on the source run redirected the
  recommendation in the free-text field ("not a bug, but a task", "say Claude thinks").
  `references/working-items.md` makes acting on that text the rule.
- **Close on the user's word only**, with a banner rather than a rewrite, and the one
  status change this skill makes. `kb-conventions.md` says no skill promotes its own
  output; the user saying it is done is the user doing so.
- **No new profile keys.** Everything it needs already exists. The one addition is a
  `codehost` tool category with a single read verb, for merged pull requests, served by
  the `gh` CLI under "Local CLI first" (there is no connector) and optional, so an install
  without it degrades to the other sources.

**Open questions:**

- Whether `build` should also run on a schedule (a lunchtime list waiting in the inbox).
  Left direct until a run shows the user wants it unasked.
- No evals ship yet; `proactive-router` is the only skill with any. A first case would
  grade that `work` re-checks an item before acting on it.
