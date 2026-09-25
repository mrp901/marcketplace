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

# For you

# Ideas

- FIG-204 · Load-plan variance alerts · [note](Product/FreightOps/Research/fig-204-load-plan-variance-alerts.md)
  - Which alert channel should the first version use?
    - [ ] (FIG-204/d1a) In-app only: cheap, but dispatchers report living in email
    - [x] (FIG-204/d1b) Email only, but batch the alerts hourly so dispatchers get one digest rather than a stream
    - [ ] (FIG-204/d1c) Both: probably right, higher build cost now

# Closed
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
