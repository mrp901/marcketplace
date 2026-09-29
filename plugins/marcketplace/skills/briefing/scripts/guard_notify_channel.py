#!/usr/bin/env python3
"""Hard allowlist gate for briefing's one notify send.

Implements a standing user rule: briefing (the only skill that ever posts, per
../../../shared/notify.md) may send to Marc's home channel and nowhere else - not the
tracker-feed channels it reads (../references/feed-cross-check.md), not any other
channel id, ever. Deterministic, no model judgement: exits 0 only when the target
matches the allowed channel exactly, and always rejects the hard-blocked ids below even
if a future profile edit ever pointed `notify.fallback_channel_id` at one of them.

Usage:
    guard_notify_channel.py <target_channel_id> <allowed_channel_id>

Exits 0 and prints "ok" when target_channel_id == allowed_channel_id and target_channel_id
is not one of HARD_BLOCKED_CHANNEL_IDS. Exits 1 and prints the reason otherwise. Run this
before every `chat: send message` call in ../../../shared/notify.md (the chat_message mode
and the webhook-failure fallback alike) and treat a non-zero exit as blocking the send
unconditionally - never send anyway, never retry against a different channel.
"""
import sys

# Standing deny-list: the tracker-feed channels briefing reads from
# (../references/feed-cross-check.md). Read-only sources, never send targets. Named
# explicitly here, in addition to the allowlist check below, because these are the two
# channels a mistake would most plausibly send to - they are already in front of
# briefing every run - and because the block must hold even if a future profile edit
# mistakenly reused one of these ids elsewhere.
HARD_BLOCKED_CHANNEL_IDS = {
    "C0BJVFV1T8E",  # work_started feed: epic-start automation, read-only, never a send target
    "C089X3K4CT0",  # fix_version feed: fix-version/sprint automation, read-only, never a send target
}


def main(argv):
    if len(argv) != 2:
        print("usage: guard_notify_channel.py <target_channel_id> <allowed_channel_id>", file=sys.stderr)
        return 1

    target, allowed = argv

    if target in HARD_BLOCKED_CHANNEL_IDS:
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
