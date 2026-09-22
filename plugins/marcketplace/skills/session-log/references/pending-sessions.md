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
file pattern `../../shared/onboarding.md` uses to locate the profile document, applied
here to a path a bare hook script can reach without any tool access at all. A user who
would rather transcripts never touch a synced folder sets `SESSION_LOG_DIR` explicitly
instead, which always wins over the pointer file.
