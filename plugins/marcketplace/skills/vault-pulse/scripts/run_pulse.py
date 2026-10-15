#!/usr/bin/env python3
"""Run the vault-pulse skill unattended, for a scheduler (cron, launchd, Windows Task Scheduler).

    python3 run_pulse.py [--profile <ref>] [--kb-root <dir>] [--out-dir <dir>] [--model sonnet]
                         [--allowed-tools "<comma list>"] [--timeout 1500]

It starts one headless Claude Code session with `/marcketplace:vault-pulse profile=<ref> unattended`
and records what happened in `<out-dir>/last-run.txt` (a header line, then the session's output),
so a run that failed leaves evidence. It exits with the session's exit code (124 on timeout).

Resolution, in order:
- profile ref: --profile, then MARCKETPLACE_PROFILE, then ~/.claude/marcketplace/profile.ref
  (the same order as shared/onboarding.md).
- out dir: --out-dir, then the sibling `vault-pulse` of the session-log directory
  (SESSION_LOG_DIR, then ~/.claude/marcketplace/session-log-dir.ref), which is where the skill
  writes its own log, then ~/.claude/vault-pulse.
- allowed tools: --allowed-tools, then VAULT_PULSE_ALLOWED_TOOLS, then a file-and-python default.
  A headless session cannot ask for permission, so the wiki read and write tools the skill uses
  to reach state must be listed by name; see references/scheduling.md.

It sets VAULT_PULSE_RUN=1 for the session, which tells scripts/pulse_reminder.py not to remind
the run itself. Stdlib only; reads nothing from the knowledge base and writes only last-run.txt.
"""
import argparse
import datetime
import os
import shutil
import subprocess
import sys

DEFAULT_TOOLS = "Read,Write,Edit,Glob,Grep,ToolSearch,Bash(python *),Bash(python3 *),PowerShell(python *)"


def pointer(name):
    path = os.path.join(os.path.expanduser("~"), ".claude", "marcketplace", name)
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.readline().strip()
    except OSError:
        return ""


def resolve_out_dir(arg):
    if arg:
        return arg
    sessions = os.environ.get("SESSION_LOG_DIR") or pointer("session-log-dir.ref")
    if sessions:
        return os.path.join(os.path.dirname(os.path.normpath(sessions)), "vault-pulse")
    return os.path.join(os.path.expanduser("~"), ".claude", "vault-pulse")


def write_record(out_dir, header, body):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "last-run.txt"), "w", encoding="utf-8") as handle:
        handle.write(header + "\n" + body)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--profile", default="")
    parser.add_argument("--kb-root", default="")
    parser.add_argument("--out-dir", default="")
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--allowed-tools", default="")
    parser.add_argument("--timeout", type=int, default=1500)
    args = parser.parse_args()

    out_dir = resolve_out_dir(args.out_dir)
    started = datetime.datetime.now()
    stamp = started.isoformat(timespec="seconds")

    ref = args.profile or os.environ.get("MARCKETPLACE_PROFILE", "") or pointer("profile.ref")
    if not ref:
        write_record(out_dir, "[%s] FAILED: no profile ref" % stamp,
                     "Pass --profile, set MARCKETPLACE_PROFILE, or run any marcketplace skill "
                     "interactively once so onboarding writes ~/.claude/marcketplace/profile.ref.\n")
        return 1

    binary = os.environ.get("CLAUDE_BIN") or shutil.which("claude")
    if not binary:
        write_record(out_dir, "[%s] FAILED: claude CLI not found" % stamp,
                     "Put claude on PATH for the scheduler's environment, or set CLAUDE_BIN.\n")
        return 1

    tools = args.allowed_tools or os.environ.get("VAULT_PULSE_ALLOWED_TOOLS") or DEFAULT_TOOLS
    command = [binary, "-p", "/marcketplace:vault-pulse profile=%s unattended" % ref,
               "--model", args.model, "--allowedTools", tools]
    env = dict(os.environ, VAULT_PULSE_RUN="1")

    try:
        done = subprocess.run(command, cwd=args.kb_root or None, env=env, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=args.timeout)
        code, output = done.returncode, (done.stdout or "") + (done.stderr or "")
    except subprocess.TimeoutExpired as err:
        code, output = 124, "Timed out after %d seconds.\n%s" % (args.timeout, err.stdout or "")
    seconds = (datetime.datetime.now() - started).total_seconds()
    write_record(out_dir, "[%s] exit=%d duration=%ds" % (stamp, code, seconds), output)
    return code


if __name__ == "__main__":
    sys.exit(main())
