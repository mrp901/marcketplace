# Notify

How the plugin tells the user something happened, outside of the surface itself. One
skill posts: `briefing`. Every other skill records what it did in `state.runs.<skill>`
(`state-schema.md`) and the briefing's Runs report carries it to the user. The same news
never goes out twice.

## Who posts

| Skill | Posts | Records to `state.runs` |
|---|---|---|
| briefing | the one briefing message, per `profile.notify` below | yes |
| every other skill | nothing | yes: `status`, one-line `note`, `ref` to its artefact |

A skill that used to fire its own webhook (idea-scout, idea-deep-dive, idea-wireframe,
kb-dream, skill-health-check) no longer does. Its `runs.<skill>` entry, written every run
including a quiet one, is the record; `profile.briefing.expected_runs` is the proof of
life (a skill that has not run within its `max_gap_days` is named in the Runs report as
overdue). A handler dispatched by the hub never posts either; its result goes back to the
hub in the return JSON (`handler-contract.md`).

## Mode

`profile.notify.mode` is one of:

- **`webhook`**: POST the briefing message to `profile.notify.webhooks.briefing`.
- **`chat_message`**: post the briefing message directly to
  `profile.notify.fallback_channel_id` via the `chat` tool category, no webhook involved.
- **`none`**: post nothing. The board is the only output.

## Webhook POST shape

A plain HTTPS POST, `Content-Type: application/json`, no chat-service auth token; the
destination workflow behind the URL turns the body into a post. Body:

```json
{"text": "<the whole formatted briefing message>"}
```

Single text field. The receiver does no further formatting: what's sent is exactly what
posts.

## `chat_message` fallback

When `profile.notify.mode` is `chat_message`, or a webhook POST fails (below), briefing
posts the same full message directly to `profile.notify.fallback_channel_id` using
`chat: send message`. No separate formatting pass; only the transport changes.

The fallback post is also where briefing's **own** fast-fail goes. Every other skill's
fast-fail is a `state.runs` record the next briefing reports; briefing has no later
briefing to report it, so it posts one line to the fallback channel itself:
`briefing: fast-fail · missing <keys> · run /marcketplace:briefing interactively once`.

## Mention form: markdown link, not a raw mention token

The briefing message opens with a markdown link, never a raw mention token:

```
[@<name>](<profile-relevant deep link to the user>)
```

A workflow-relayed post does not reliably resolve a raw mention token into a working
notification; a markdown link always renders as a clickable link regardless of how the
post reached the channel. `profile.notify.mention_form` records this choice
(`markdown_link`).

## Egress failure fallback

If the webhook POST fails for any reason, briefing falls back to `chat_message` against
`profile.notify.fallback_channel_id` with the identical content, and says in
`runs.briefing.note` that the webhook path was unavailable. One webhook attempt, one
fallback post, done. Never retry the webhook itself within the same run.

## Security note

**A webhook URL stored in a shared document is usable by anyone who can read that
document.** Because `profile` and `state` are shared cloud-connector documents, a webhook
URL recorded in the profile is exposed to the document's full read audience. Onboarding
says this plainly when `notify.mode: webhook` is chosen, and offers `chat_message` first
wherever it cannot confirm the profile document has tight read permissions.
