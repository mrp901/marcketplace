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
| `SessionStart` | sweep recent transcripts for sessions `SessionEnd` missed (`pending-sessions.md`), then count `pending/` and tell Claude the backlog exists | `SessionStart` does support `additionalContext`; the sweep is capped and cursored |

The write-up then happens inside a real session, with a real model and full tool access -
either because the user asked, or because the `SessionStart` nudge offered. That trades
"automatically, at the moment of exit" for "reliably, at the start of the next session."
Given the constraints that's the better trade: the automatic version would silently do
nothing at exactly the moment it matters, which is worse than a one-turn delay.

That trade only holds if someone acts on the nudge. Until 1.10.0 the nudge told the session
not to raise the backlog "unless it is large or old" without saying what large or old meant,
so in practice nobody offered and the queue grew for days (10 sessions, five days, 26 Oct
2026). The nudge now names its edges - 5 sessions or 3 days, the same edges `vault-pulse`
scores amber - and past either one tells the session to offer the drain once. For a queue
that should never depend on a person, schedule it (below).

## Shipped as plugin hooks

`../../hooks/hooks.json` wires both, using `${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py` so
the install location never needs configuring by hand:

```json
{
  "hooks": {
    "SessionEnd": [
      {"hooks": [{"type": "command", "command": "P=python3; $P -c '' </dev/null 2>/dev/null || P=python; $P \"${CLAUDE_PLUGIN_ROOT}/scripts/archive_session.py\"", "timeout": 15}]}
    ],
    "SessionStart": [
      {"hooks": [{"type": "command", "command": "P=python3; $P -c '' </dev/null 2>/dev/null || P=python; $P \"${CLAUDE_PLUGIN_ROOT}/scripts/pending_sessions.py\""}]}
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

The same `hooks.json` also names a hooks module under `"modules"` (`../../hooks/register.ts`),
the plugin's observer. It is a separate mechanism (TypeScript run inside Claude Code, not a
command), touches neither script, and leaves both hooks exactly as above.

## Draining on a schedule

`../scripts/run_session_log.py` runs this skill headless over the
queue, for cron, launchd or Windows Task Scheduler. It exits without starting a session when
`pending/` is empty, records each run in `last-drain.txt` beside `pending/`, and sets
`MARCKETPLACE_HEADLESS=1` so its own transcript is never queued (the sweep also skips any
`/marcketplace:<skill> ... unattended` session).

- **When:** once a working day, after the day's sessions end and before the overnight
  `kb-dream`, so the dream curates fresh notes. Run it on the machine whose `pending/` it
  drains. A cloud routine could reach `pending/` only when it sits in a synced folder, and
  then only page by page through the kb connector - megabytes per transcript, with no local
  `read_transcript.py` digest - so a local scheduler is the practical home for this run.
- **Allowed tools:** a headless session cannot ask for permission, so pass every tool the
  skill touches by name in `--allowed-tools` or `SESSION_LOG_ALLOWED_TOOLS`: file tools and
  `python`, the file move from `pending/` to `archive/`, the wiki read and write tools for
  state, and the kb write tools when the kb is reached through a connector rather than a
  local path. A tool left out fails that step silently in a `-p` run, so read
  `last-drain.txt` after the first scheduled run.
- **Unattended means no questions:** the "is this worth a note?" gate, name checks and
  duplicate checks resolve to their conservative default (`../../../shared/onboarding.md`,
  step 0), and anything that needed a person is named in the note's open threads.

## Things worth knowing

- **Transcripts contain everything the session saw** - file contents, secrets that
  happened to be on screen, names. Archiving them into a synced folder means they inherit
  that folder's sharing. `.utility/` keeps them out of the kb's own search and graph, not
  out of whatever syncs the folder itself. Prune `archive/` periodically, or point
  `SESSION_LOG_DIR` at a local, unsynced path instead.
- **The queue is not self-clearing.** Moving processed files from `pending/` to
  `archive/` is this skill's job, per `pending-sessions.md`. If write-ups seem to repeat,
  that's the step that got skipped. If the queue only ever grows, nothing is running this
  skill: see "Draining on a schedule".
- **Don't call a headless model from the hook itself.** It's tempting - a model call to do
  the summary from the hook. From `SessionEnd` it won't fit the budget; from `Stop` it
  fires after every assistant turn, not at the end, producing partial summaries all
  session and risking recursion. Unattended write-ups belong on a schedule *outside* the
  session, run over `pending/`, never inside a hook.
- **Cowork has no hook configuration and no reachable transcript file** - none of this
  applies there. In Cowork, invoke this skill directly; it reads the live conversation
  instead of an archived transcript, which is why its frontmatter omits `sources` in that
  case.
