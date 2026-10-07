# Tool capabilities

The indirection layer that lets a `SKILL.md` name what it needs done, not which concrete tool does it. A skill's `## Needs` lists categories and verbs from this table; the runtime resolves each to an actual tool prefix at run start. This keeps every skill portable across services - Slack or Teams, Jira or Linear, Confluence or SharePoint - without a single edit to the skill itself.

## Category verbs

The starting set below is not exhaustive on its own; it is extended with every verb the skills actually call for, drawn from the source skills' real tool calls.

| Verb | What it does | Typical tool names (hints only) | Used by |
|---|---|---|---|
| `chat: read canvas` | Read the surface's current content and section addressing | `slack_read_canvas` | briefing, proactive-router, idea-spar, kb-dream, action-sweep, skill-health-check |
| `chat: update canvas` | Write one batch of operations against a surface addressing snapshot | `slack_update_canvas` | briefing, proactive-router, idea-spar, kb-dream, action-sweep, skill-health-check |
| `chat: search messages` | Search reactions, saved items, DMs and channel history; see the search forms below | `slack_search_public_and_private` | briefing, proactive-router, action-sweep |
| `chat: read thread` | Fetch one specific thread or message by its permalink, when a reference already names it | `slack_read_thread`, `slack_get_permalink` | reply-draft, kb-note, action-sweep |
| `chat: search users` | Resolve a name to a user id when not already known | `slack_search_users` | briefing |
| `chat: send message` | Post directly to a channel - the `chat_message` notify fallback | `slack_send_message` | briefing, kb-dream, notify fallback (any skill) |
| `tracker: search issues (JQL)` | Query the issue tracker for a candidate set | `searchJiraIssuesUsingJql` | briefing, action-sweep, idea-ticket |
| `tracker: get issue` | Fetch one issue's full fields, comments, links | `getJiraIssue` | action-sweep, idea-ticket |
| `tracker: create issue` | File a new issue | `createJiraIssue` | action-sweep (push), idea-ticket (file) |
| `tracker: add comment` | Post a non-destructive comment to an existing issue | `addCommentToJiraIssue` | action-sweep (push) |
| `ideas: search issues (JQL)` | Query the ideas board for a candidate | `searchJiraIssuesUsingJql` (ideas project) | idea-spar |
| `ideas: get issue` | Fetch one idea's full fields and comments | `getJiraIssue` (ideas project) | idea-spar |
| `ideas: create issue` | File a new idea, unlabelled | `createJiraIssue` (ideas project) | idea-ticket (file) |
| `wiki: get page by id` | Fetch a page by its id - never search | `getConfluencePage` | onboarding (profile/state docs), any skill reading a wiki-hosted kb |
| `wiki: update page` | Full-replace or patch a page | update-page equivalent | onboarding (profile/state docs), kb-note, kb-dream when `kb.kind: confluence` |
| `kb: search` | Search the knowledge base connector for matching files | `sharepoint_search` | action-sweep, idea-spar, kb-dream, session-log |
| `kb: read` | Read one kb file by path or resource id | `read_resource` | idea-spar, kb-dream, session-log, kb-note |
| `kb: write` | Create or full-replace a kb file, byte-checked where the connector requires it | `sharepoint_upload_file` | idea-spar, kb-dream, session-log, kb-note |
| `calendar: list today` | Today's events only, local timezone window | `outlook_calendar_search` | briefing |
| `email: search` | Search mail for threads/mentions | mail-search equivalent | reply-draft, action-sweep |
| `email: sent` | List the user's own sent mail, for voice calibration | mail-sent equivalent | voice calibration |
| `notetaker: list meetings` | List recent recorded meetings | meetings-list equivalent | action-sweep (fourth source), briefing (prep lines) |
| `notetaker: transcript` | Fetch one meeting's transcript | transcript-fetch equivalent | action-sweep |
| `codebase: search` | Search the connected codebase for a term or symbol | device-bridge or filesystem search | idea-spar (reality lens) |
| `codebase: read` | Read one file from the connected codebase | device-bridge or filesystem read | idea-spar (reality lens) |
| `web: search` | General web search for market/competitor research | web-search equivalent | idea-spar (market lens), idea-ticket |
| `page: publish` | Publish (or republish in place) one self-contained HTML page and return a shareable link | an artifact or doc publisher | idea-spar (the pack) |

A category a skill doesn't use is simply absent from its `## Needs` - this table is the full catalogue across all the skills, not a per-skill checklist.

## Chat search forms

`chat: search messages` takes a free-text query plus filters. The forms the plugin relies on, in the reference (Slack-shaped) syntax; another chat service's connector maps them to its own equivalents at resolution time, and a form the connector cannot express degrades to "not searched" for that source, never to a guess:

| Form | Returns | Used by |
|---|---|---|
| `hasmy::<emoji>: after:<date>` | Messages the user reacted to with that emoji since the date | proactive-router |
| `is:saved after:<date>` | Messages the user saved since the date | proactive-router |
| `from:me after:<date>` | The user's own messages since the date; action-sweep reads these for first-person commitments ("I'll send", "I'll check", "leave it with me") | action-sweep |
| `with:me is:thread after:<date>` | Threads the user is a participant in; action-sweep keeps only those where someone else spoke last | action-sweep |
| `@<user> after:<date>` (the user's own mention) | Messages that mention the user; action-sweep keeps only those with no reply or reaction from the user | action-sweep |

Every form is bounded by a cursor date and returns permalinks, which is what `state.items` dedupes on. Thread bodies are never pulled into the calling skill's context; a `search`-tier subagent reads them and returns a short structured answer, per `token-discipline.md`.

## Resolution rule

Every category resolves to a concrete tool prefix through `state.machines[<machine_id>].tools.<category>`, populated once by onboarding step 4 (`onboarding.md`) via `ToolSearch` and cached there. **Prefixes never appear hardcoded in a skill.** A skill names the category and verb; the runtime looks up that machine's cached prefix and calls the resolved tool. When the cache is stale (a tool renamed, a connector swapped) onboarding's one re-resolution on failure refreshes it before any skill proceeds.

## Local CLI first, for tracker reads

When a run is local, a machine with a shell may also have the service's own command-line client installed and signed in. Its output is usually smaller than a connector's (it returns a summarised view and writes the full payload to a file instead of into context), so for the read verbs below the runtime calls the CLI first and keeps the connector for everything else. Today that means one CLI: Atlassian's Teamwork Graph CLI (`twg`), for `tracker` and `ideas` when their `service` is a Jira flavour.

| Verb | CLI call (`twg`) | Notes |
|---|---|---|
| `tracker: search issues (JQL)` / `ideas: search issues (JQL)` | `twg jira workitem query --jql "<jql>" --limit <n> -o json --agent-fields @compact` | add `--fields <a,b,...>` when the skill needs fields beyond the compact set |
| `tracker: get issue` / `ideas: get issue` | `twg jira workitem get <key> [<key> ...] -o json --agent-fields @compact` | batches keys in one call; add `--comments`, `--remote-links` or `--full` only when the step reads them |

Rules:

- **Reads only.** Every write verb (`create issue`, `add comment`, `wiki: update page`) stays on the connector, and so does `wiki: get page by id`, because the profile, state and kb documents it reads are written back in the same run and must round-trip through one backend.
- **Resolved per machine, never assumed.** Onboarding step 4 probes for the CLI and records the result in `state.machines[<machine_id>].cli` (see `onboarding.md`). A machine without a shell, without the binary, or not signed in (every cloud session and routine, today) simply has no `cli` entry and uses the connector, with no `Signed out` and no note.
- **Connector stays resolved.** The connector prefix in `tools.<category>` is still resolved and cached alongside, because writes need it and because it is the fallback.
- **Fall back once, silently.** If a CLI call fails (non-zero exit, an auth or contract error, or output that doesn't parse), make the same read through the connector and carry on; clear that machine's `cli.<category>` so later runs skip the CLI until the next probe. A CLI failure is never a fast-fail and never makes a section read `Signed out` while the connector works.
- **Read the summary, not the payload.** Use the output's `stdout_inline` block; when it is absent, read the `output_files.compact` file it names. Open `output_files.stdout` only for a field the compact view left out. Never print a whole payload into context (`token-discipline.md`).
- **Never set it up.** A skill never runs the CLI's `login`, `setup`, `upgrade` or install commands, and never passes a token as a flag. A missing or signed-out CLI is just "no CLI on this machine".
- **Quote shell-special arguments.** In PowerShell, `@compact` must be quoted (`'@compact'`), or the shell eats it as splatting and the flag arrives empty.
- `profile.tools.<category>.cli: off` opts a category out of the probe entirely.

## Degradation rule

A category that cannot be resolved (no service configured, `ToolSearch` finds nothing, the resolved tool errors on first call) makes the section of the surface that depends on it read `Signed out` - per the snapshot rule in `surface-protocol.md` - and **the run continues**. Losing `calendar` doesn't stop `tracker` from being read; losing `web` doesn't stop a note from being written with what's already in hand.

The one exception is an **identity-critical category** - one the run cannot proceed at all without (chiefly `chat` for surface access, since every skill's dispatch and reporting model depends on it, and whichever category resolves the profile/state documents themselves). Losing one of those fast-fails per `onboarding.md`'s fast-fail procedure: `runs[skill].status = fast-fail` with the note, stop - rather than limping through a run that can't record what it did.

## Tool names are hints only

Every name in the "typical tool names" column is illustrative, drawn from what the reference instance happened to be connected to. **These names must never appear in a `SKILL.md`.** A skill body writes `` `chat: update canvas` `` or `` `tracker: create issue` ``, never `slack_update_canvas` or `createJiraIssue` - the concrete name belongs only in `state.machines`, resolved at run time, so the same skill works unmodified against a differently-connected instance.
