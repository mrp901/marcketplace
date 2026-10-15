# Scheduling the pulse, and the missed-run reminder

The pulse measures the machine it runs on, so it is scheduled on that machine, not as a cloud
routine. Two small scripts make that practical: `../scripts/run_pulse.py` runs it headless from any
scheduler, and the plugin's SessionStart hook (`../../../scripts/pulse_reminder.py`) tells the user
in a session when a run was missed. Neither is required; `Run /marcketplace:vault-pulse` still works
by hand.

## Cadence and the expected-runs value

The measurement window is the last seven days, so any cadence from daily to weekly gives the same
kind of reading. Set `briefing.expected_runs.vault-pulse` to the longest healthy gap plus a day or
two of slack, so the briefing names the pulse overdue if it stops.

| Cadence | `expected_runs.vault-pulse` | `VAULT_PULSE_REMIND_DAYS` |
|---|---|---|
| Weekdays | 3 (covers Friday to Monday) | `1-5` (the default) |
| Weekly, Monday | 9 | `1` |

## The runner

```
python3 <plugin>/skills/vault-pulse/scripts/run_pulse.py --kb-root <kb.local_root>
```

It starts one headless session with `/marcketplace:vault-pulse profile=<ref> unattended`, writes the
outcome to `<kb.paths.utility>/vault-pulse/last-run.txt` (a header line with the exit code and
duration, then the session output), and exits with the session's exit code. The profile ref comes from
`--profile`, then `MARCKETPLACE_PROFILE`, then `~/.claude/marcketplace/profile.ref`.

A headless session cannot ask for permission, so the tools it needs must be allowed up front. The
default list covers file access and Python. Add the wiki read and write tools the skill uses to reach
state (the hints are in `../../../shared/tool-capabilities.md`) through `VAULT_PULSE_ALLOWED_TOOLS` or
`--allowed-tools`, as a comma-separated list of tool names. If the first run fails on a denied tool,
`last-run.txt` says which.

The runner sets `VAULT_PULSE_RUN=1` for the session. The plugin's archive hook and the reminder both
read it: the scheduled run is a measurement, so it is not archived for write-up and is not reminded.

## Registering the schedule

Weekdays at 10:00 on Windows, from PowerShell. Leave `-Principal` out: the default is the current
user, interactive, which is what a run that needs the user's Claude login requires (an explicit
`-UserId` was rejected on a work-account login).

```
$action   = New-ScheduledTaskAction -Execute 'python' -Argument '"<plugin>\skills\vault-pulse\scripts\run_pulse.py" --kb-root "<kb.local_root>"'
$trigger  = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At '10:00'
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 30)
Register-ScheduledTask -TaskName 'vault-pulse' -Action $action -Trigger $trigger -Settings $settings
```

`-StartWhenAvailable` runs a missed start as soon as the machine is next awake. On macOS or Linux use
a crontab line such as `0 10 * * 1-5 python3 <plugin>/skills/vault-pulse/scripts/run_pulse.py --kb-root <kb.local_root>`
(or a launchd agent with the same command), and make sure `claude` is on the scheduler's `PATH` or set
`CLAUDE_BIN`.

## The reminder

Opt in by adding to the `env` block of the user's settings:

```
"env": { "VAULT_PULSE_REMIND_AFTER": "10:45", "VAULT_PULSE_REMIND_DAYS": "1-5" }
```

With `VAULT_PULSE_REMIND_AFTER` unset the hook prints nothing. Set, it speaks only on a listed
weekday, after that local time, when the log has no entry dated today, and at most once every two
hours. It reads the log (`<kb.paths.utility>/vault-pulse/log.md`), not state, so it still works when
state is unreachable. When `last-run.txt` exists its first line is quoted, so the user sees at once
that the scheduled run failed and with what exit code.

## One-time step on the first run

The first run creates the skill's own state shard. When the main state document is too large to
rewrite safely, the run reports the one `shards:` line to add by hand. Add it before the second run,
or that run will not find its shard, will create another, and the trend is lost.
