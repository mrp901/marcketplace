# Releasing

Every change to this plugin gets a runtime check before it merges. The repo checks (validate,
plugin test, scrub, line budget, `check_refs.py`, unit tests) read files in this repository. A
plugin like this also runs in places the repository does not contain, and a change can pass
every repo check and still break there.

## Why

Three consecutive releases each broke in a runtime the repo does not contain (a scheduled local task calling a removed skill, a housekeeping rule acting on state older runs had written, a note contract applied to notes that already existed), and every repo check passed.

The checklist below makes that runtime check a written step of every PR instead of something a
reviewer remembers.

## The runtimes

| Runtime | What runs there | How it updates |
|---|---|---|
| Cloud routines | Each scheduled skill, from a fresh clone of `main`, with connectors only | On every run: they see `main` the moment it merges |
| Synced plugin copy | Local Claude Code sessions, hooks, and any local task that invokes a skill | On its own schedule, after the hosted copy updates and Claude Code restarts. It lags `main` |
| Local scripts and tasks | `~/.claude/scripts`, `env` and hooks in `~/.claude/settings.json`, the OS scheduler | Never, unless the owner edits them. They keep what they were written against |
| Profile and state documents | The live profile, board, and per-skill state shards | Written by whichever plugin version ran last, so old and new versions overlap for a while |
| The knowledge base | Notes that already exist | Never rewritten by a release. They were made under the old contract |

## Checklist

Answer each item in the PR body with **checked** (and how), **not affected** (and why), or
**gap** (named, with who owns closing it).

1. **Cloud routines.** Does each routine whose skill changed still run from a fresh clone with connectors only: no local files, no shell, no state on disk?
2. **Synced copy.** Does anything local depend on the new version? If yes, the PR body says "update the plugin and restart after merge" and what breaks until then.
3. **Outside the repo.** Run `python3 plugins/marcketplace/scripts/runtime_refs.py` on the branch (see below; on Windows `python` may be the right command, since `python3` can be the Store stub). Every hit is fixed or named.
4. **Profile and state.** Every new key has a default. Every renamed or removed key has a migration row in `shared/state-schema.md` or an alias. An older version writing the same document on the same day cannot drop or corrupt the new keys. Name how an older version writes this document (whole-document replace or key merge) and confirm it keeps keys it does not know.
5. **Existing content.** Does any new or changed rule (clock, prune, lock, counter, matcher) act on notes, board lines or state that already exist (seeded, hand-made, moved, or written by an older version)? Name the oldest real example you ran it against and what it does to it, especially anything it deletes or counts.
6. **Rollback.** If this merge is reverted, what state or content does the new version leave behind that the old one misreads?

### `runtime_refs.py`

It diffs `--base` (default `origin/main`) against `--head` (default `HEAD`), collects the names
the diff removes (skills, as `<skill>` and `/<plugin>:<skill>`; profile keys no live table row lists any more; env vars scripts and hooks read; removed script files), and greps `~/.claude/scripts`, `~/.claude/settings.json` and
`~/.claude/skills` for them. `--extra <path>` adds places to look (another machine's task
folder, say). It prints `file:line: <name> (removed in this diff)` per hit, exits 1 on any hit,
and `--json` gives the same for an agent. It is read-only. It runs on the machine that has the
runtimes, so CI does not run it; CI runs only its unit test.

A path that does not exist is an error when you passed it and a warning when it is a default, and a run that scanned no file exits 2, so a clean run cannot mean "looked at nothing". A clean run means no local file names a removed thing. It does not cover the OS scheduler's own
entries, other machines, or anything that calls a skill by a name built at run time.

## Reviewer brief

An independent reviewer reports findings against this checklist, item by item, and states what
it did not check (another machine, the live board, a runtime it had no access to). A report that
says "no issues" without saying what it looked at is not a pass.

## After merge

1. Update the plugin on the hosted side and restart Claude Code. Confirm the version-drift
   SessionStart check is quiet.
2. Re-run `runtime_refs.py` if it was run before a rebase.
3. The first scheduled run of each touched skill is the real test. Read its run log, not just
   its status.
