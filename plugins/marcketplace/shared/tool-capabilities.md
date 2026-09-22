# Tool capabilities

The indirection layer that lets a `SKILL.md` name what it needs done, not which concrete tool does it. A skill's `## Needs` lists categories and verbs from this table; the runtime resolves each to an actual tool prefix at run start. This keeps every skill portable across services - Slack or Teams, Jira or Linear, Confluence or SharePoint - without a single edit to the skill itself.

## Category verbs

The starting set below is not exhaustive on its own; it is extended with every verb the thirteen skills actually call for, drawn from the source skills' real tool calls.

| Verb | What it does | Typical tool names (hints only) | Used by |
|---|---|---|---|
| `chat: read canvas` | Read the surface's current content and section addressing | `slack_read_canvas` | briefing, proactive-router, idea-scout, idea-deep-dive, idea-wireframe, kb-dream, action-sweep, skill-health-check |
| `chat: update canvas` | Write one batch of operations against a surface addressing snapshot | `slack_update_canvas` | briefing, proactive-router, idea-scout, idea-deep-dive, idea-wireframe, kb-dream, action-sweep, skill-health-check |
| `chat: search messages` | Search reactions, saved items, DMs and channel history | `slack_search_public_and_private` | briefing, proactive-router, action-sweep |
| `chat: search users` | Resolve a name to a user id when not already known | `slack_search_users` | briefing |
| `chat: send message` | Post directly to a channel - the `chat_message` notify fallback | `slack_send_message` | briefing, kb-dream, notify fallback (any skill) |
| `tracker: search issues (JQL)` | Query the issue tracker for a candidate set | `searchJiraIssuesUsingJql` | briefing, action-sweep, idea-ticket |
| `tracker: get issue` | Fetch one issue's full fields, comments, links | `getJiraIssue` | action-sweep, idea-ticket |
| `tracker: create issue` | File a new issue | `createJiraIssue` | action-sweep (push), idea-ticket (file) |
| `tracker: add comment` | Post a non-destructive comment to an existing issue | `addCommentToJiraIssue` | action-sweep (push) |
| `tracker: update issue` | Edit fields or labels on an existing issue, never description/AC | `editJiraIssue` | idea-scout, idea-wireframe (labels) |
| `ideas: search issues (JQL)` | Query the ideas board for a candidate | `searchJiraIssuesUsingJql` (ideas project) | idea-scout, idea-wireframe |
| `ideas: get issue` | Fetch one idea's full fields and comments | `getJiraIssue` (ideas project) | idea-scout, idea-wireframe |
| `ideas: create issue` | File a new idea, unlabelled | `createJiraIssue` (ideas project) | idea-ticket (file) |
| `ideas: add label` | Append a workflow label (`investigated`, `wireframed`) | `editJiraIssue` | idea-scout, idea-wireframe |
| `wiki: get page by id` | Fetch a page by its id - never search | `getConfluencePage` | onboarding (profile/state docs), any skill reading a wiki-hosted kb |
| `wiki: update page` | Full-replace or patch a page | update-page equivalent | onboarding (profile/state docs), kb-note, kb-dream when `kb.kind: confluence` |
| `kb: search` | Search the knowledge base connector for matching files | `sharepoint_search` | action-sweep, idea-scout, idea-wireframe, kb-dream, session-log |
| `kb: read` | Read one kb file by path or resource id | `read_resource` | idea-scout, idea-wireframe, kb-dream, session-log, kb-note |
| `kb: write` | Create or full-replace a kb file, byte-checked where the connector requires it | `sharepoint_upload_file` | idea-scout, idea-wireframe, kb-dream, session-log, kb-note |
| `calendar: list today` | Today's events only, local timezone window | `outlook_calendar_search` | briefing |
| `email: search` | Search mail for threads/mentions | mail-search equivalent | reply-draft, action-sweep |
| `email: sent` | List the user's own sent mail, for voice calibration | mail-sent equivalent | voice calibration |
| `notetaker: list meetings` | List recent recorded meetings | meetings-list equivalent | action-sweep (fourth source), idea-deep-dive (circle 2), briefing (prep lines) |
| `notetaker: transcript` | Fetch one meeting's transcript | transcript-fetch equivalent | action-sweep, idea-deep-dive |
| `codebase: search` | Search the connected codebase for a term or symbol | device-bridge or filesystem search | idea-deep-dive (circle 3) |
| `codebase: read` | Read one file from the connected codebase | device-bridge or filesystem read | idea-deep-dive (circle 3) |
| `web: search` | General web search for market/competitor research | web-search equivalent | idea-scout, idea-deep-dive (circle 4), idea-ticket |

A category a skill doesn't use is simply absent from its `## Needs` - this table is the full catalogue across all thirteen skills, not a per-skill checklist.

## Resolution rule

Every category resolves to a concrete tool prefix through `state.machines[<machine_id>].tools.<category>`, populated once by onboarding step 4 (`onboarding.md`) via `ToolSearch` and cached there. **Prefixes never appear hardcoded in a skill.** A skill names the category and verb; the runtime looks up that machine's cached prefix and calls the resolved tool. When the cache is stale (a tool renamed, a connector swapped) onboarding's one re-resolution on failure refreshes it before any skill proceeds.

## Degradation rule

A category that cannot be resolved (no service configured, `ToolSearch` finds nothing, the resolved tool errors on first call) makes the section of the surface that depends on it read `Signed out` - per the snapshot rule in `surface-protocol.md` - and **the run continues**. Losing `calendar` doesn't stop `tracker` from being read; losing `web` doesn't stop a note from being written with what's already in hand.

The one exception is an **identity-critical category** - one the run cannot proceed at all without (chiefly `chat` for surface access, since every skill's dispatch and reporting model depends on it, and whichever category resolves the profile/state documents themselves). Losing one of those fast-fails per `onboarding.md`'s fast-fail procedure: one line under Plugin notices, `runs[skill].status = fast-fail`, stop - rather than limping through a run that can't record what it did.

## Tool names are hints only

Every name in the "typical tool names" column is illustrative, drawn from what the reference instance happened to be connected to. **These names must never appear in a `SKILL.md`.** A skill body writes `` `chat: update canvas` `` or `` `tracker: create issue` ``, never `slack_update_canvas` or `createJiraIssue` - the concrete name belongs only in `state.machines`, resolved at run time, so the same skill works unmodified against a differently-connected instance.
