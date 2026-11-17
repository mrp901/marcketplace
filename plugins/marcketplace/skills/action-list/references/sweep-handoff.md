# Sweep handoff

How `build` uses what `action-sweep` already found, so the two skills never read the same
source twice or draft the same find twice. `action-sweep` is the one gatherer for chat,
tracker and meetings; `build` takes its finds and extracts only the rest.

## Sweep's items (step 2)

Every `sweep:` entry in `action-sweep`'s shard is a candidate, whatever its category
(`chat-reply`, `ticket-reply`, `ticket-minor`, `meeting-followup`, `to-do`), on the board
or off it, with its `text` and `ref` as the evidence. It is classified and dated per
`i-owe.md`.

## The rest (step 2)

One search-tier subagent per source, in parallel:

- email addressed to the user;
- the kb inbox and the open threads of recent `kb.paths.sessions` notes;
- merged pull requests that involve the user;
- the delta on sweep's sources: chat threads and mentions after
  `cursors.action-sweep.chat_since`, tracker mentions after `scanned_through`
  (`../../action-sweep/references/mention-search-method.md`) with the user's own tracker
  comments ("I owe"), and meeting transcripts after `runs.action-sweep.last_run_at` (none
  when `notetaker.service` is `none`).

The user's own chat promises come from the 14-day `from:me` search "I owe" keeps
(`i-owe.md`), not from sweep: sweep's subagents keep only what they judge a promise, and
extractors here decide nothing.

## Fallback, checked every build (step 2)

A sweep source is extracted here for the whole window when `runs.action-sweep` is absent,
its `last_run_at` is before the window opens, or its `note` says that source couldn't be
reached. A chat cap needs no fallback: sweep holds `chat_since` back, so the delta re-reads
the unread range. Sweep's freshness is checked, never assumed.

## Settling (step 3)

A `sweep:` item verified done, on the board or off it, goes to "Dropped" with the evidence
and is recorded in this skill's shard as `settled: {<tag>: <settled_at>}`. `briefing`
closes its board line, if it has one, and `action-sweep` prunes the entry
(`../../../shared/state-schema.md`, "Closing a settled item"). A `sweep:` item marked on the
board whose line is gone (deleted or closed) is dropped.

## No double drafting (step 5)

A find with a live `sweep:` line on the board is ranked but never drafted here. Its row
points at the line: "draft ready under sweep:<tag>" when the board shows one, else "tick
sweep:<tag> to draft it". A tier question is pointed at, never answered here, so
`action-sweep`'s tier rule holds. A find with no board line (a to-do, an email, this
skill's own find) is drafted as usual.
