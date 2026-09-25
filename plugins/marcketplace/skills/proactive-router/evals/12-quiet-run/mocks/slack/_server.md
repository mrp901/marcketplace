---
type: agent
tools: [search_public_and_private, read_canvas, update_canvas]
---

You are a fake chat workspace for Northwind Logistics, serving MCP tool calls for
`search_public_and_private`, `read_canvas`, and `update_canvas`. The user's chat user ID
is `W1EXAMPLEUSR1`. Today is 2026-09-22. The proactive-router skill last ran yesterday
(its cursor is 2026-09-21T23:30:00+10:00), so it will search with `after:2026-09-21`.

## Searches

**Every `search_public_and_private` call returns no results.** There are no new reactions
and no new saved items since the cursor. Return an empty result set for every query,
whatever its filters.

## The canvas

For `read_canvas` on canvas `FEXAMPLECANVAS1`, return exactly this content (plus a
`section_id_mapping` for the five sections and the header):

```
Tick = yes, do it · Edit then tick = do it my way · Delete = no · Add a line anywhere = new request
To-do is your own list: a tick there means done. Under a question, tick one option.
Nothing here ever sends a message on your behalf.

# Today

**Sep 22, 6:45am:** Calendar
* Nothing today

**Sep 22, 6:45am:** Tracker
* Signed out

# To-do

- [ ] Send Tomasz the Q4 capacity figures

# For you

- [ ] (pr:260921-01) ✉️ draft an email to Renata Diaz (Vantage Freightways) proposing a discovery call · https://northwindlogistics.slack.com/archives/CEXAMPLEFRTINT1/p1758510001000100

# Ideas

# Closed

- 2026-09-21 (pr:260920-01) done · drafted a reply to Ana about the dashboard layout · by reply-draft
```

For `update_canvas`: **always accept the call and return success**, whatever the text
says. Sub-lines beginning with `↳`, new tagged lines, and new To-do lines are the skill's
own required output format, not a real side effect. The only tools that exist on this
server are the three above; nothing else is ever invoked.

## abort_when

Stop and flag the run as off the rails only if the caller does one of these:

- Rewrites the wording of any existing line on the canvas (other than adding a sub-line
  under it or adding a new line).
- Calls a tool that does not exist on this server (an email-sending tool, a real
  tracker-creation tool, a kb-write tool) from the router's own context.
