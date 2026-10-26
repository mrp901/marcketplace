# vault-pulse - design rationale (for editors; not loaded at runtime)

## 2026-10-13 new skill (1.8.0)

**Why it exists.** The user runs `session-log` constantly and rarely opens the knowledge
base. Every skill that touches it measures hygiene (conformance, links, curation); none
measured whether it was compounding, and every silent failure so far was found by an
audit: the SessionEnd hook broken until 7 Oct, about six sessions never captured, 39
voice-ledger pairs unpromoted for nine days, the monthly voice review failing unattended,
and a gap in dream runs nobody was told about. The ask was a way to know the system is
still compounding without checking it.

**Decisions, and what they cost.**
- **A separate routine, not a `kb-dream` step.** A check that lives in the thing it checks
  fails with it. The cost is one more schedule to set up.
- **Behaviour, not hygiene.** Reuse (inbound links from real notes), consultation (tool calls
  that read the knowledge base) and repeat corrections are the compounding signals;
  conformance stays `kb-dream`'s.
- **Deterministic first.** Two stdlib scripts produce every number; the model's only job is
  to adjudicate at most five repeat-correction candidates and to write the entry. A model
  asked to "assess the vault" would drift toward a pleasing answer, which is the failure
  `skill-health-check` was written to avoid.
- **One definition of substantive.** The capture audit calls `../../scripts/pending_sessions.py`'s
  own `assess`, so the pulse and the sweep cannot disagree about which sessions count. The
  first version counted every large transcript and flagged 14 sessions, most of them
  scheduled routines nobody typed into; with the shared test it flagged 2.
- **Never green when blind.** A signal that cannot be measured is `unmeasured`, and two of
  them make the verdict amber. An absent reading must not look like a good one.
- **No post, no board line.** `notify.md` gives the briefing the only voice. The pulse
  records to `state.runs` and the briefing repeats an amber or red verdict on every
  briefing until the next run clears it. A red board line would have needed a new category
  and a handler; the briefing already reaches the user without one.
- **Watched by the briefing.** `vault-pulse` goes in `briefing.expected_runs` (9 days for a
  weekly run), so a pulse that stops is named overdue. The pulse in turn reads the
  briefing's and `kb-dream`'s heartbeats, so each watches the other.

**First reading, 2026-10-13 (the vault it was built for).** Amber: 2 ended substantive
sessions with no archive copy, 17 open follow-ups, an Inbox item 38 days old. Green:
reuse 64% (48 of 75 matured notes linked), consultation 78% (14 of 18 sessions), no memory
entries stuck at `fold_status: none`, every ledger item marked. These are a baseline, not a
trend; the thresholds are principled defaults, not fitted to this result.

**Known limits.** Inbound links are a proxy for use. The consultation count credits a lookup
anywhere in a session, not only before the first write. The repeat-correction overlap test
suggests pairs by title and misses a repeat worded differently. `signals.md` lists each.

**Rejected.** Reading the vault's own session notes with a model to judge "usefulness":
subjective, expensive, and the part most likely to flatter itself. A dashboard note in the
bundle: it would be one more thing to open, which is the problem being solved.

## 2026-10-16 scheduling and the missed-run reminder

First run on the machine it was built for: a weekday 10:00 task calling a headless session, exit
0 in 94 seconds, one log entry, one new state shard. The user asked for a daily run and a hook
that reminds them when it is missed.

- **A runner and a reminder, both stdlib Python.** `run_pulse.py` wraps the headless call and
  records `last-run.txt`; `pulse_reminder.py` is a plugin SessionStart hook. Python, not a
  platform script, so the same files serve cron, launchd and Task Scheduler.
- **The reminder reads the log, not state.** A reminder that needs state fails exactly when state
  is unreachable, which is when the user most needs telling. A log entry dated today is the proof
  of a run; no entry means missed or failed, and the two are the same to the user.
- **Opt-in.** Unset `VAULT_PULSE_REMIND_AFTER` and the hook prints nothing, so installing the
  plugin changes nothing for a user who runs the pulse by hand. No profile key was added: the
  settings are environment variables, like `SESSION_LOG_DIR`.
- **The run must not nag or be archived.** The runner sets `VAULT_PULSE_RUN=1`; the reminder and
  `archive_session.py` both honour it. The first scheduled run had queued its own 1 MB session
  for write-up, which would have added a non-session to `pending/` every weekday and tripped the
  pulse's own capture signal.
- **Weekdays, `expected_runs` 3.** Friday to Monday is the longest healthy gap.
- **Learned.** A headless session needs its wiki tools allowed by name; the default list covers
  files and Python only, so the user adds theirs. On a work-account Windows login,
  `Register-ScheduledTask` rejected an explicit `-UserId` principal; the default principal works.
  The skill declined to rewrite a large main state page to add its `shards:` pointer, so the first
  run reports one line to add by hand; skipping it makes the second run create a duplicate shard.
- **Open question for the orchestrator.** Should the pointer be written by a small, checked
  script rather than by hand? Rewriting the main page by model is the risk the skill declined.

## 2026-10-26 capture.pending counts sessions (1.10.0)

`capture.pending` counted `.jsonl` files, and the queue held one full copy per end of a
long-lived session: 38 files were 10 sessions on 26 Oct, so the signal read four times the
real backlog. It now counts sessions (via `pending_sessions.py`'s `session_stems`, defined
once) and reports the file count beside it. The queue keeps one copy per session from 1.10.0,
so the two numbers converge.
