#!/usr/bin/env python3
"""SessionStart hook: remind the user to run vault-pulse when a scheduled run was missed.

Opt in by setting VAULT_PULSE_REMIND_AFTER to a local time (HH:MM) in the `env` block of the
user's settings; with it unset this hook prints nothing. It also stays silent when:
- today is not one of VAULT_PULSE_REMIND_DAYS (ISO weekday numbers, default "1-5", Monday is 1);
- the local time is before VAULT_PULSE_REMIND_AFTER (give the scheduled run time to finish);
- the vault-pulse log already has an entry dated today;
- this is the scheduled run itself (scripts/run_pulse.py sets VAULT_PULSE_RUN=1); or
- the user was already reminded in the last two hours.

The log is `<kb.paths.utility>/vault-pulse/log.md`. Its directory is VAULT_PULSE_DIR, else the
sibling `vault-pulse` of the session-log directory (SESSION_LOG_DIR, then
~/.claude/marcketplace/session-log-dir.ref), the same pointer pending_sessions.py uses. When the
scheduled runner left a last-run.txt beside the log, its first line is quoted in the reminder so
the user can see why the run failed. VAULT_PULSE_NOW (ISO 8601) fixes the clock for tests.

Output is the hook JSON: a systemMessage for the user and additionalContext for the model.
Reads two small files and writes one marker; never touches the knowledge base's notes.
"""
import datetime
import json
import os
import re
import sys

THROTTLE_MINUTES = 120


def home_file(*parts):
    return os.path.join(os.path.expanduser("~"), ".claude", *parts)


def pointer(name):
    try:
        with open(home_file("marcketplace", name), encoding="utf-8") as handle:
            return handle.readline().strip()
    except OSError:
        return ""


def pulse_dir():
    explicit = os.environ.get("VAULT_PULSE_DIR")
    if explicit:
        return explicit
    sessions = os.environ.get("SESSION_LOG_DIR") or pointer("session-log-dir.ref")
    if not sessions:
        return ""
    return os.path.join(os.path.dirname(os.path.normpath(sessions)), "vault-pulse")


def parse_days(text):
    days = set()
    for part in text.split(","):
        part = part.strip()
        if re.fullmatch(r"[1-7]", part):
            days.add(int(part))
        elif re.fullmatch(r"[1-7]-[1-7]", part):
            low, high = int(part[0]), int(part[2])
            days.update(range(low, high + 1))
    return days or {1, 2, 3, 4, 5}


def last_entry_date(log_path):
    try:
        with open(log_path, encoding="utf-8") as handle:
            for line in handle:
                found = re.match(r"## (\d{4}-\d{2}-\d{2})", line)
                if found:
                    return found.group(1)
    except OSError:
        pass
    return ""


def first_line(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            return handle.readline().strip()
    except OSError:
        return ""


def main():
    if os.environ.get("VAULT_PULSE_RUN") == "1":
        return 0
    after = os.environ.get("VAULT_PULSE_REMIND_AFTER", "").strip()
    found = re.fullmatch(r"(\d{1,2}):(\d{2})", after)
    if not found:
        return 0
    stamp = os.environ.get("VAULT_PULSE_NOW")
    try:
        now = datetime.datetime.fromisoformat(stamp) if stamp else datetime.datetime.now()
    except ValueError:
        return 0
    if now.isoweekday() not in parse_days(os.environ.get("VAULT_PULSE_REMIND_DAYS", "1-5")):
        return 0
    if (now.hour, now.minute) < (int(found.group(1)), int(found.group(2))):
        return 0

    directory = pulse_dir()
    if not directory:
        return 0
    last = last_entry_date(os.path.join(directory, "log.md"))
    if last == now.date().isoformat():
        return 0

    marker = home_file("marcketplace", ".pulse-reminded")
    try:
        with open(marker, encoding="utf-8") as handle:
            reminded = datetime.datetime.fromisoformat(handle.readline().strip())
        if datetime.timedelta(0) <= now - reminded < datetime.timedelta(minutes=THROTTLE_MINUTES):
            return 0
    except (OSError, ValueError):
        pass
    try:
        os.makedirs(os.path.dirname(marker), exist_ok=True)
        with open(marker, "w", encoding="utf-8") as handle:
            handle.write(now.isoformat(timespec="seconds"))
    except OSError:
        pass

    message = "Vault pulse has not run today (last log entry: %s). Run /marcketplace:vault-pulse." % (last or "never")
    attempt = first_line(os.path.join(directory, "last-run.txt"))
    if attempt:
        message += " The scheduled run last tried: %s (details in %s)." % (attempt, os.path.join(directory, "last-run.txt"))
    print(json.dumps({
        "systemMessage": message,
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "Reminder for the user: %s Mention this once at the start of the conversation; do not run the pulse unless they ask." % message,
        },
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
