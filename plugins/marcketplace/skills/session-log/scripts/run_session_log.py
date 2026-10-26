#!/usr/bin/env python3
"""Drain the session-log pending queue unattended, for a scheduler (cron, launchd, Windows Task Scheduler).

    python3 run_session_log.py [--profile <ref>] [--kb-root <dir>] [--model sonnet]
                               [--allowed-tools "<comma list>"] [--timeout 3000]

The hooks only fill `pending/`; nothing empties it unless someone runs this skill. On 26 Oct 2026
the queue had grown to 10 sessions over five days with no note written, and every downstream pass
(kb-dream, vault-pulse) had nothing new to work with. This runner closes that gap: it starts one
headless Claude Code session with `/marcketplace:session-log profile=<ref> unattended` and records
what happened in `last-drain.txt` beside `pending/`, so a failed run leaves evidence. It exits with
the session's exit code (124 on timeout), and exits 0 without starting a session when the queue is
empty.

Resolution, in order:
- profile ref: --profile, then MARCKETPLACE_PROFILE, then ~/.claude/marcketplace/profile.ref.
- queue: SESSION_LOG_DIR, then ~/.claude/marcketplace/session-log-dir.ref, then ~/.claude/session-log.
- allowed tools: --allowed-tools, then SESSION_LOG_ALLOWED_TOOLS, then a file-and-python default. A
  headless session cannot ask for permission, so the kb and wiki tools the skill reaches state and
  the knowledge base with must be listed by name; see references/hooks-setup.md.

It sets MARCKETPLACE_HEADLESS=1 for the session, so archive_session.py does not queue the run's own
transcript; the sweep also skips any `/marcketplace:<skill> ... unattended` session. Stdlib only.
"""
import argparse
import datetime
import os
import shutil
import subprocess
import sys

DEFAULT_TOOLS = ("Read,Write,Edit,Glob,Grep,ToolSearch,Bash(python *),Bash(python3 *),Bash(mv *),"
                 "PowerShell(python *),PowerShell(Move-Item *)")


def pointer(name):
    path = os.path.join(os.path.expanduser("~"), ".claude", "marcketplace", name)
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.readline().strip()
    except OSError:
        return ""


def queue_dir():
    return (os.environ.get("SESSION_LOG_DIR") or pointer("session-log-dir.ref")
            or os.path.join(os.path.expanduser("~"), ".claude", "session-log"))


def write_record(base, header, body):
    os.makedirs(base, exist_ok=True)
    with open(os.path.join(base, "last-drain.txt"), "w", encoding="utf-8") as handle:
        handle.write(header + "\n" + body)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--profile", default="")
    parser.add_argument("--kb-root", default="")
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--allowed-tools", default="")
    parser.add_argument("--timeout", type=int, default=3000)
    args = parser.parse_args()

    base = queue_dir()
    started = datetime.datetime.now()
    stamp = started.isoformat(timespec="seconds")

    pending = os.path.join(base, "pending")
    waiting = [f for f in (os.listdir(pending) if os.path.isdir(pending) else []) if f.endswith(".jsonl")]
    if not waiting:
        write_record(base, "[%s] exit=0 queue empty, no session started" % stamp, "")
        return 0

    ref = args.profile or os.environ.get("MARCKETPLACE_PROFILE", "") or pointer("profile.ref")
    if not ref:
        write_record(base, "[%s] FAILED: no profile ref" % stamp,
                     "Pass --profile, set MARCKETPLACE_PROFILE, or run any marcketplace skill "
                     "interactively once so onboarding writes ~/.claude/marcketplace/profile.ref.\n")
        return 1

    binary = os.environ.get("CLAUDE_BIN") or shutil.which("claude")
    if not binary:
        write_record(base, "[%s] FAILED: claude CLI not found" % stamp,
                     "Put claude on PATH for the scheduler's environment, or set CLAUDE_BIN.\n")
        return 1

    tools = args.allowed_tools or os.environ.get("SESSION_LOG_ALLOWED_TOOLS") or DEFAULT_TOOLS
    command = [binary, "-p", "/marcketplace:session-log profile=%s unattended" % ref,
               "--model", args.model, "--allowedTools", tools]
    env = dict(os.environ, MARCKETPLACE_HEADLESS="1")

    try:
        done = subprocess.run(command, cwd=args.kb_root or None, env=env, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=args.timeout)
        code, output = done.returncode, (done.stdout or "") + (done.stderr or "")
    except subprocess.TimeoutExpired as err:
        code, output = 124, "Timed out after %d seconds.\n%s" % (args.timeout, err.stdout or "")
    seconds = (datetime.datetime.now() - started).total_seconds()
    write_record(base, "[%s] exit=%d duration=%ds files_waiting=%d" % (stamp, code, seconds, len(waiting)),
                 output)
    return code


if __name__ == "__main__":
    sys.exit(main())
