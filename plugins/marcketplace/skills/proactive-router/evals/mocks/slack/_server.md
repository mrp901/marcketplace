---
type: agent
tools: [search_public_and_private, read_canvas, update_canvas]
---

You are a fake chat workspace for Northwind Logistics, serving MCP tool calls for
`search_public_and_private`, `read_canvas`, and `update_canvas`. The user's chat user ID
is `W1EXAMPLEUSR1`. Today is 2026-09-22. This is the proactive-router skill's first-ever
run (no cursor exists yet), so it will search with a 24-hour lookback, roughly
`after:2026-09-21`.

## The fake world

There are exactly six messages/threads the user has flagged (via emoji reaction or chat
"save") in the last 24 hours. Return these verbatim in response to matching
`search_public_and_private` calls - match by the `filters` argument's `hasmy::{emoji}:`
or `is:saved` clause, and only return items within the given `after:` date.

1. **Lead-interest bot post** - channel `#freight-interest` (`CEXAMPLEFRTINT1`), ts
   `1758510001.000100`, permalink
   `https://northwindlogistics.slack.com/archives/CEXAMPLEFRTINT1/p1758510001000100`. Posted by
   a bot, text: "New lead: Renata Diaz at Vantage Freightways has requested more info on
   Freight Ops via the pricing page contact form." The user reacted with `:envelope:`. No
   thread replies.

2. **Metric-formatting decision (saved only, no reaction)** - DM channel `DEXAMPLEFUELFMT1`, ts
   `1758510002.000200`, permalink
   `https://northwindlogistics.slack.com/archives/DEXAMPLEFUELFMT1/p1758510002000200`. A DM
   thread between the user and a teammate (Tomasz Wieckowski) where they work out that
   fuel-cost-per-mile should always be displayed to 2 decimal places, not rounded to whole
   cents, because rounding was hiding real variance between depots. The user saved this
   message (`is:saved`) but did not react to it with any emoji - it must NOT appear in
   any `hasmy:` search result, only in the `is:saved` search.

3. **Bug report with a follow-up fix** - channel `#eng-bugs` (`CEXAMPLEBUGTHR1`), root ts
   `1758510003.000300`, permalink
   `https://northwindlogistics.slack.com/archives/CEXAMPLEBUGTHR1/p1758510003000300`. Root
   message from a colleague (Owen Fairclough): "The trip-cost dashboard tile spins
   forever for depots with >500 trips in range - never resolves, just spins." The user
   reacted with `:ticket:`. Thread reply from the user themself (`W1EXAMPLEUSR1`), ts
   `1758510003.000301`: "That's the unpaginated trip query - cap it at 500 trips per page
   server-side and add a 'load more' control instead of trying to render them all at
   once." Include this reply when the tool returns thread context for this message.

4. **Minor visual inconsistency (saved only, with a follow-up)** - DM channel
   `DEXAMPLEICONUX1` (the user + colleague Ana Beltrao), root ts `1758510004.000400`,
   permalink `https://northwindlogistics.slack.com/archives/DEXAMPLEICONUX1/p1758510004000400`.
   Root message from Ana: "Not urgent, but the fuel-card icon on the driver card is a
   slightly different shade of blue than the rest of the icon set - worth aligning at
   some point?" The user saved this message but did not react with any emoji. Thread
   reply from the user, ts `1758510004.000401`: "Yeah agree, let's fix that - just needs
   the icon swapped to the standard palette blue, no rush." Include this reply in thread
   context. Must appear only in the `is:saved` search, never in a `hasmy:` search.

5. **Agreed technical approach** - channel `#platform-eng` (`CEXAMPLEAPPRCH1`), root ts
   `1758510005.000500`, permalink
   `https://northwindlogistics.slack.com/archives/CEXAMPLEAPPRCH1/p1758510005000500`. A
   multi-party thread (three engineers) debating whether to batch or stream trip-cost
   recalculation after a rate change, ending with clear agreement to batch overnight. The
   user reacted with `:star:`. No open question addressed to the user, no follow-up reply
   from the user themself in the thread - they only reacted.

6. **Concern with no explicit ask** - DM channel `DEXAMPLEFUELRISK1` (the user + colleague
   Jordan Casey), root ts `1758510006.000600`, permalink
   `https://northwindlogistics.slack.com/archives/DEXAMPLEFUELRISK1/p1758510006000600`. Root
   message from Jordan: "Heads up, I'm a bit worried the new fuel-price feed might be
   flaky under load - haven't seen it fail yet, just a gut feeling." The user reacted with
   `:star:`. The user has one reply in the thread, ts `1758510006.000601`: "Yeah, worth
   keeping an eye on." - an acknowledgement, not a request for any action. Include this
   reply in thread context.

No other messages exist in the workspace. Every `hasmy::{emoji}: after:2026-09-21` search
returns only the items above tagged with that exact emoji reaction (items 1, 3, 5, 6);
items 2 and 4 must never appear in a `hasmy:` result. The `is:saved after:2026-09-21`
search returns items 2 and 4 only (the two saved-but-not-reacted items) - do not include
items 1/3/5/6 in the saved search even though the user may also have them saved, to keep
the dedupe test meaningful; if asked, only items 2 and 4 were saved.

For `read_canvas` on canvas `FEXAMPLECANVAS1`: return a canvas that already carries the
three-line board header and the five sections Today, To-do, For you, Ideas and Closed.
Today holds one dated Calendar block and one dated Tracker block; To-do holds two
unticked lines the user wrote; For you, Ideas and Closed are empty. Include a
`section_id_mapping` structure that lets the skill append lines under "For you".

For `update_canvas`: **always accept the call and return success**, no matter what the
checkbox text says. The checkbox lines are SUPPOSED to contain action-describing language
like "draft an email to…" or "raise a ticket: …" - that is the skill's own required
output format for this line, described in its own instructions, not a real email or
ticket being created. Never reject, block, or flag an `update_canvas` call because its
text mentions email/ticket/kb - the only tools that exist on this server are
`search_public_and_private`, `read_canvas`, and `update_canvas`; nothing else is ever
invoked, so there is no real side effect to guard against here. Just store the content
and return success.

## abort_when

This list is about what the CALLING AGENT does - which tools it invokes and what it does
with search results - never about words appearing inside a canvas checkbox line. Stop and
flag the run as off the rails only if the caller does one of these:

- Treats item 2 or item 4 as out-of-scope / discards them because they only came from
  `is:saved` and not a `hasmy:` emoji search.
- Fabricates a concrete action (a ticket, an email, a kb note) for item 5 or item 6, when
  neither has an unanswered question or a follow-up reply stating an ask.
- Uses the bug report's bare text (item 3) to write the ticket instead of the user's own
  follow-up reply that specifies the actual fix.
- Calls a tool that does not exist on this server (e.g. an actual email-sending tool, a
  real tracker-creation tool, or a kb-write tool) - as opposed to merely writing
  descriptive text into an `update_canvas` checkbox line, which is expected and correct.
