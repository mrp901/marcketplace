# Notify

How a skill tells the user something happened, outside of the surface itself. Every skill that posts a run summary reads `profile.notify` before composing anything.

## Mode

`profile.notify.mode` is one of:

- **`webhook`** - POST the run's summary to a per-skill webhook URL. The default for the reference instance; requires `profile.notify.webhooks.<skill>` to be set for every skill that notifies.
- **`chat_message`** - post the summary directly to `profile.notify.fallback_channel_id` via the chat tool category, no webhook involved.
- **`none`** - compose nothing beyond the surface write itself. No chat post, no webhook call, of any kind, for any skill.

A skill with nothing to notify (a quiet run, see the proof-of-life rule below) still follows this mode - a quiet run under `webhook` still POSTs; under `none` it posts nothing, same as a busy run.

## Webhook POST shape per skill

Every webhook call is a plain HTTPS POST, `Content-Type: application/json`, no chat-service auth token - the destination workflow or automation behind the URL is what turns the body into a formatted post. The body shape differs by what the skill has to report; do not invent a new shape for a skill not listed here without adding a row.

| Skill | Body shape | Notes |
|---|---|---|
| briefing | `{"text": "<the whole formatted briefing message>"}` | Single text field. The webhook receiver does no further formatting - what's sent is exactly what posts |
| kb-dream | `{"summary": "<the whole nudge text, newlines and all>"}` | Single summary field, fired every run including a quiet one (proof of life) |
| idea-scout | `{"ticket": "<tracker key>", "outputUrl": "<path to the written note, or empty string if it couldn't be saved>"}` | Ticket key plus output URL |
| idea-deep-dive | `{"ticket": "<tracker key>", "outputUrl": "<path to the note>"}` | Same shape as idea-scout |
| idea-wireframe | `{"ticket": "<tracker key>", "outputUrl": "<path to the .html wireframe>"}` | Same shape; path is the rendered artefact, not the wrapper note |
| skill-health-check | `{"ticket": "<skill-slug>", "outputUrl": "<path to the skill's health log entry>"}` | `ticket` here is a skill slug, not a tracker key - it is the thing that uniquely identifies which run this call is about, one call per skill scored |

A skill not in this table (a handler dispatched by the hub, for instance) does not fire its own webhook - its result goes back to the hub in the return JSON (`handler-contract.md`), and the hub's own run notifies, if at all, on the hub's own schedule.

## `chat_message` fallback to the home channel

When `profile.notify.mode` is `chat_message`, or a webhook POST fails (see egress-failure fallback below), the skill posts the same content it would have sent in the webhook body - the full text/summary field, not a truncated version - directly to `profile.notify.fallback_channel_id` using the `chat` category from `tool-capabilities.md`. No separate formatting pass; the content is identical, only the transport changes.

## Mention form: markdown link, not a raw mention token

Every notification that addresses the user opens with a markdown link, never a raw mention token:

```
[@<name>](<profile-relevant deep link to the user>)
```

Not `<@U0...>` or any other service-specific mention syntax. **Why:** a workflow-relayed post - one that goes out via an automation sitting behind a webhook, rather than a direct API call from an authenticated session - does not reliably resolve a raw mention token into a working notification/highlight for the user. A markdown link always renders as a clickable link regardless of how the post reached the channel, so it degrades gracefully where a raw token silently fails to ping anyone. `profile.notify.mention_form` records this choice (`markdown_link`) so a skill never has to re-derive it.

## Proof-of-life rule

Any skill whose scheduled cadence includes runs that find nothing to report still fires its notification every run, with a one-line "quiet run" body, wherever `profile.notify.proof_of_life.<skill>` is `true`. This exists because a genuinely silent skill and a broken one look identical from the outside otherwise - the only way to tell "nothing happened" from "didn't run" is a heartbeat. `kb-dream` ships with this on by default (`profile.notify.proof_of_life: {kb-dream: true}`); any skill that runs unattended on a schedule where silence is a plausible outcome should set the same flag rather than skipping notification on a quiet run.

A skill without the flag set skips notification on a genuinely quiet run - the flag is opt-in per skill, not a blanket rule, because not every skill's silence is ambiguous (a handler dispatched only when ticked has no "scheduled and found nothing" case to disambiguate).

## Egress failure fallback

If the webhook POST fails for any reason - can't reach the endpoint, non-2xx response, timeout - the skill falls back to `chat_message` against `profile.notify.fallback_channel_id` with the identical content, and says in its own run record (not in the posted message) that the webhook path was unavailable. This is a one-step fallback, not a retry loop: one webhook attempt, one fallback post, done. Never retry the webhook itself within the same run.

## Security note

**A webhook URL stored in a shared document is usable by anyone who can read that document** - unlike a chat-service API call, the webhook itself carries no per-user auth, so possession of the URL is the entire access control. Because `profile` and `state` are shared cloud-connector documents (Confluence page or SharePoint/OneDrive file), a webhook URL recorded in `profile.notify.webhooks.<skill>` is exposed to the document's full read audience, not just the user.

Onboarding must say this plainly when `notify.mode: webhook` is chosen. Where the surface or profile document's page permissions are loose (broad read access, a shared team space rather than a personal one), `chat_message` is the safer default - it relies on the chat service's own per-user auth rather than a bearer-less URL, so a reader of the profile document gains nothing from seeing `fallback_channel_id` that they didn't already have. Onboarding step 1 (see `onboarding.md`) offers `chat_message` first wherever it cannot confirm the profile document has tight read permissions.
