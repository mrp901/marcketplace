# Pending archived sessions

`kb.paths.utility`/`sessions/pending/` holds transcripts the `SessionEnd` hook archived
but nobody has written up yet - see `hooks-setup.md` for why the hook can only archive,
never summarise, and for how the pointer file below gets written.

## Working the queue

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/read_transcript.py --list      # what's waiting
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/read_transcript.py <file>      # digest one
```

Work through them oldest first, writing one note each per the main flow, then move the
processed file from `pending/` to `archive/` so it isn't picked up again - set
`cursors.session-log.last_pending_processed` to the same point. `.utility/` is tooling
space, never indexed and never curated by a content pass (`kb-conventions.md`), so this
move is plain file management, not a maintenance-contract write.

Several small sessions on one day are often better as one note covering the day than one
note per session - use judgement; the goal is a useful record, not one note per process
lifetime.

**One copy per session.** A long-lived session (a worktree job, a resumed or background
session) ends many times, and each copy is the full transcript so far. Since 1.10.0, both
`archive_session.py` and the sweep replace any older `pending/` copy of the same session
when they queue a newer one, and keep `queued_since` (when the session first entered the
queue). `archive_session.py` carries the earliest `tail_after` across the copies it
replaces, or none if any had none; the sweep rebuilds the tail from `archive/` instead. A
queue left over from before that may still hold several copies of one session (the session
id is the last part of the filename): read the newest, start from the earliest `tail_after`
across the copies (from the beginning if any copy lacks one), and move every copy to
`archive/` with it.

**Nothing drains the queue on its own.** The hooks only fill it. If nobody runs this skill,
it grows by a session or more a day; schedule an unattended run (`hooks-setup.md`,
"Draining on a schedule") rather than relying on someone remembering.

## The transcript sweep

`SessionEnd` misses sessions: a window closed by killing it, a hook broken by the
environment, a session that never ended cleanly. So `pending_sessions.py`, on every
`SessionStart`, first scans the local Claude Code transcripts
(`~/.claude/projects/*/*.jsonl`, or under `CLAUDE_CONFIG_DIR`) and copies any substantive
one with no queued or archived copy into `pending/`, with a sidecar whose `reason` is
`swept`. Then it counts the queue as before.

- **Substantive, conservatively:** at least 6 typed user messages and at least one write
  (a file edit or a connector create/update/send), or at least 15 typed messages with no
  write. Tool results, slash-command echoes, hook output and subagent turns never count.
  A trivial session stays out; the "is this worth a note?" gate still applies to what gets
  in.
- **Already covered:** a copy of the same session in `pending/` or `archive/` at least as
  new as the transcript, or a `session-log` run inside the transcript itself. A session
  resumed after an `archive/` copy or a `session-log` run is judged on its tail alone (a
  `pending/` copy is replaced, not built on, so it never starts a tail), and the sidecar's
  `tail_after` says where the uncovered part starts - write up only that part, updating the earlier note in
  place when it is the same piece of work.
- **Cheap:** transcripts touched in the last 2 hours are left alone (they may still be
  open), files under 64 KB are skipped unread, at most 20 are read and 8 queued per start,
  and `sweep-cursor.json` beside `pending/` carries the rest to the next start. The first
  run looks back 7 days.
- `SESSION_LOG_SWEEP=0` turns it off. `pending_sessions.py --dry-run` prints what it would
  queue and writes nothing.

## Transcript reading

`read_transcript.py` treats unknown line shapes as skippable rather than fatal, because
Claude Code's transcript JSONL is internal and shifts between versions; a digest missing a
few lines is useful, a traceback is not. It separates files the session **changed** from
files it only **read** - only the changed list belongs in the note's "Changes to the
knowledge base" table. Reading a file is not a change to it.

## The pointer file, and why archive_session.py and pending_sessions.py need one

Both hook scripts run standalone, outside any skill invocation, with no MCP or kb-discovery
access of their own - they cannot resolve `kb.local_root` the way a running skill can. They
resolve their working directory in this order:

1. `SESSION_LOG_DIR` environment variable, if set.
2. The pointer file at `~/.claude/marcketplace/session-log-dir.ref`, if one exists - a
   single line naming the resolved local path to `kb.paths.utility`/`sessions`.
3. `~/.claude/session-log` as a last-resort local default.

This skill is what writes that pointer file, once, the first time it successfully
resolves the kb's local root (step 1 of the main flow) - the same env-var-then-pointer-
file pattern `../../../shared/onboarding.md` uses to locate the profile document, applied
here to a path a bare hook script can reach without any tool access at all. A user who
would rather transcripts never touch a synced folder sets `SESSION_LOG_DIR` explicitly
instead, which always wins over the pointer file.
