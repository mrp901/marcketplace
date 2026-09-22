# Hooks setup, and why it's shaped this way

## The constraint

The obvious design is "a `SessionEnd` hook that summarises the session." That doesn't
work, and it's worth knowing why before trying to fix it:

- `SessionEnd` hooks share a roughly 1.5 second budget (raisable per-hook, capped at 60s
  total). Reading a transcript, calling a model, and writing several kb files does not
  fit.
- `SessionEnd` does not support `additionalContext` - the field other hooks use to hand
  text back to Claude. There is nothing to hand it back to: the session is already
  terminating.
- Exit code 2 on `SessionEnd` shows stderr and nothing else. It cannot block the session
  from ending, so it can't hold the door open while write-up work finishes.

So `SessionEnd` cannot do the interesting part. What it can do is guarantee the raw
material survives somewhere findable.

## The shape that does work

Split it in two:

| Hook | Job | Why it can do it |
|---|---|---|
| `SessionEnd` | copy the transcript to `pending/`, write a metadata sidecar | a file copy fits comfortably in the budget |
| `SessionStart` | count `pending/` and tell Claude the backlog exists | `SessionStart` does support `additionalContext` |

The write-up then happens inside a real session, with a real model and full tool access -
either because the user asked, or because the `SessionStart` nudge offered. That trades
"automatically, at the moment of exit" for "reliably, at the start of the next session."
Given the constraints that's the better trade: the automatic version would silently do
nothing at exactly the moment it matters, which is worse than a one-turn delay.

## Shipped as plugin hooks

`../../hooks/hooks.json` wires both, using `${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py` so
the install location never needs configuring by hand:

```json
{
  "hooks": {
    "SessionEnd": [
      {"hooks": [{"type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/archive_session.py\"", "timeout": 15}]}
    ],
    "SessionStart": [
      {"hooks": [{"type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/pending_sessions.py\""}]}
    ]
  }
}
```

Both scripts resolve *where* to archive to (not their own location) via
`SESSION_LOG_DIR`, then the pointer file, then a local default - see
`pending-sessions.md`'s "The pointer file" section. Neither script depends on the plugin
being installed at any particular path, and both run correctly with no pointer file and no
env var set at all (they just fall back to `~/.claude/session-log`), so a fresh install
works before this skill has ever run.

## Things worth knowing

- **Transcripts contain everything the session saw** - file contents, secrets that
  happened to be on screen, names. Archiving them into a synced folder means they inherit
  that folder's sharing. `.utility/` keeps them out of the kb's own search and graph, not
  out of whatever syncs the folder itself. Prune `archive/` periodically, or point
  `SESSION_LOG_DIR` at a local, unsynced path instead.
- **The queue is not self-clearing.** Moving processed files from `pending/` to
  `archive/` is this skill's job, per `pending-sessions.md`. If write-ups seem to repeat,
  that's the step that got skipped.
- **Don't call a headless model from the hook itself.** It's tempting - a model call to do
  the summary from the hook. From `SessionEnd` it won't fit the budget; from `Stop` it
  fires after every assistant turn, not at the end, producing partial summaries all
  session and risking recursion. Unattended write-ups belong on a schedule *outside* the
  session, run over `pending/`, never inside a hook.
- **Cowork has no hook configuration and no reachable transcript file** - none of this
  applies there. In Cowork, invoke this skill directly; it reads the live conversation
  instead of an archived transcript, which is why its frontmatter omits `sources` in that
  case.
