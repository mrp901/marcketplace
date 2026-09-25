# Gather procedure

Run all seven sources independently; a failure in one never blocks the others. Record
that source as "couldn't reach X" in `runs.action-sweep.note` and move on, same fail-fast
principle as `briefing`. Every thread, transcript or canvas body is read by a
`budgets.models.search`-tier subagent that returns a short structured answer (what is
asked, who owes it, the permalink, and nothing else), capped at
`budgets.action-sweep.thread_reads` reads across the whole run; raw bodies never enter
this skill's own context (`../../../shared/token-discipline.md`).

## 1. Chat canvases (current state, no cursor)

Search for canvases authored by the user, most recent first. Read every one found and
pull out anything phrased as an outstanding action or to-do, but only items that
plausibly need a tracker reply or ticket; skip kb-admin, personal, or process to-dos.
Canvases represent current state, not a stream; there is no "since" filter here.

**Guardrail.** If the search turns up more than `budgets.action-sweep.canvas_guard`
canvases, stop this source and ask which are current before reading all of them.
Unattended, this becomes a one-line note on this source only (not the whole run): "too
many canvases (`N` > guard) - run interactively to pick".

**Chase, don't just list.** If a to-do names a specific, searchable source already within
reach (a named DM, a named channel, a named thread), do one targeted search there before
posting the to-do as unresolved. Cap it at `budgets.action-sweep.targeted_search_per_todo`
(one) search per to-do.

## 2. Tracker comments mentioning the user (since `scanned_through`)

See `mention-search-method.md` for the full procedure and why the obvious full-text
search doesn't work. On cold start (no cursor recorded yet) default to
`budgets.action-sweep.cold_start_days` and say so in the run record; a safe, stated
default, not a silent one.

## 3. Tickets currently assigned to the user (current state, no cursor)

`tracker: search issues (JQL)` with `tracker.my_work_jql`. This is "what's currently on
my plate", not an incremental feed: always the full current list, every run. Only a
ticket with an open question addressed to the user, or a due date passed, produces a
line; the rest are the briefing's Tracker snapshot's job, not this skill's.

## 4. Notetaker action items

`notetaker: list meetings` within `notetaker.lookback_days`, then `notetaker: transcript`
per meeting (via the subagent) to pull action items the user committed to in that
meeting. Often the highest-signal source and the easiest to lose: a spoken commitment has
no other record once the meeting ends. Subject to the same drafting and confirmation
discipline as every other source.

## 5. Commitments the user made in chat (since `chat_since`)

`chat: search messages` with `from:me after:<chat_since>` (the form is documented in
`../../../shared/tool-capabilities.md`). The subagent reads each hit and returns only
first-person promises with a concrete object: "I'll send the figures Friday", "leave the
rollback with me", "I'll raise a ticket for that". An acknowledgement ("sounds good",
"will do" with no object) is not a commitment. Each commitment routes to `to-do` unless
it is itself a ticket to raise (`ticket-minor`/`ticket-reply`) or a reply owed
(`chat-reply`).

## 6. Threads waiting on the user (since `chat_since`)

`chat: search messages` with `with:me is:thread after:<chat_since>`. Keep only threads
where someone other than the user spoke last and the last message asks the user
something, or answers a question the user asked and now awaits their reply. Routes to
`chat-reply`. A thread the user already replied to after the ask is dropped.

## 7. Unanswered mentions (since `chat_since`)

`chat: search messages` for the user's own mention, `after:<chat_since>`. Keep only
mentions the user has neither replied to nor reacted to. A bare "cc" mention with no ask
is dropped, not listed. Routes to `chat-reply`, or `to-do` when the mention hands the user
a task rather than a question.

## Dedupe across every source

One find can surface through several sources (a meeting commitment that is also a chat
promise, a mention inside a thread already waiting on the user). Dedupe by permalink or
ticket key against this run's other finds and against every tag in `state.items`, so a
find already on the board, whoever put it there, is never posted twice. When two sources
describe one find, keep the one with the most concrete action.
