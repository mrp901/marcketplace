#!/usr/bin/env python3
"""Hard allowlist gate for briefing's one notify send.

Implements a standing user rule: briefing (the only skill that ever posts, per
../../../shared/notify.md) may send to the user's home channel and nowhere else - not the
tracker-feed channels it reads (../references/feed-cross-check.md), not any other
channel id, ever. Deterministic, no model judgement: exits 0 only when the target
matches the allowed channel exactly and is not on the deny-list, so the block holds even
if a future profile edit ever pointed `notify.fallback_channel_id` at a feed channel.

Usage:
    guard_notify_channel.py <target_channel_id> <allowed_channel_id> [<blocked_channel_id> ...]

The caller passes every configured `profile.chat.tracker_feed_channels.*` id as a
blocked id (skip ones set to `none`). An install may add further standing blocks in the
NOTIFY_BLOCKED_CHANNEL_IDS environment variable (comma separated); they are unioned with
the arguments. No channel id is hardcoded here: ids are the organisation's private data
and live in the profile, never in the plugin.

Exits 0 and prints "ok" when target_channel_id == allowed_channel_id and target_channel_id
is not blocked. Exits 1 and prints the reason otherwise. Run this before every
`chat: send message` call in ../../../shared/notify.md (the chat_message mode and the
webhook-failure fallback alike) and treat a non-zero exit as blocking the send
unconditionally - never send anyway, never retry against a different channel.
"""
import os
import sys

BLOCKED_ENV = "NOTIFY_BLOCKED_CHANNEL_IDS"


def blocked_ids(argv_blocked):
    """Union of the blocked ids given as arguments and in the environment variable."""
    out = set()
    for raw in list(argv_blocked) + os.environ.get(BLOCKED_ENV, "").split(","):
        value = raw.strip()
        if value and value.lower() != "none":
            out.add(value)
    return out


def main(argv):
    if len(argv) < 2:
        print(
            "usage: guard_notify_channel.py <target_channel_id> <allowed_channel_id> "
            "[<blocked_channel_id> ...]",
            file=sys.stderr,
        )
        return 1

    target, allowed = argv[0], argv[1]
    blocked = blocked_ids(argv[2:])

    if not target or not allowed:
        print("BLOCKED: target and allowed channel ids must both be non-empty", file=sys.stderr)
        return 1

    if target in blocked:
        print(
            f"BLOCKED: {target} is a hard-blocked channel (tracker-feed source, "
            "read-only, never a send target)",
            file=sys.stderr,
        )
        return 1

    if target != allowed:
        print(
            f"BLOCKED: {target} is not the allowed channel ({allowed}); briefing only "
            "ever sends to profile.notify.fallback_channel_id",
            file=sys.stderr,
        )
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
