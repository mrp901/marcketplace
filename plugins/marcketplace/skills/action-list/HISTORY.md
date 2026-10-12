# action-list - design rationale (for editors; not loaded at runtime)

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
