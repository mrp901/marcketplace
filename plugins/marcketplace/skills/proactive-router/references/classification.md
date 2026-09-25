# Classification - worked examples

Calibrate specificity against these. The bar is "would the user recognise this as exactly
what they'd have written themselves", not a generic category label. Drawn from a real
pass over saved items and reactions; re-fictionalised here against `profiles/example.md`
(Northwind Logistics / Freight Ops) - names, companies and products are invented.

Note where each came from: several are saved items, not emoji reactions. A saved item
matching one of these rows is a hit to log, never an out-of-scope result just because no
emoji touched it.

| Message (paraphrased) | Call | Logged line |
|---|---|---|
| Bot post in a lead-interest channel: a named person at a named company has requested more info on the org's product | Draft an email to organise a call and demo | `✉️ draft an email to {name} ({company}) proposing a discovery call / demo · {permalink}` |
| Tracker bot DM notifying activity on a ticket, terse/empty visible text | There's probably a ticket comment to action | `🎫 check {ticket} for a comment likely awaiting your reply · {permalink}` |
| Colleague's follow-up in a design channel proposing a new capability | Raise an ideas-board entry off this | `🎫 raise an idea: {capability, in their own words} · {permalink}` |
| Colleague's DM raising a small UX idea, not urgent | Note it for a future maintenance pass - don't ticket it now | `🎫 [minor, park] {the idea} - revisit on a future maintenance pass · {permalink}` |
| Colleague flags a concern in DM with no explicit ask, and the user's own reply doesn't add one either | Probably no action - just worth noting | no board line; `runs.proactive-router.fyi` gets `{concern, one line} · {permalink}` |
| Colleague reports a bug; the user's own follow-up reply says what should happen instead | Needs a ticket per the follow-up | `🎫 raise a ticket: {the fix the follow-up specified} · {permalink}` |
| Colleague flags a small visual inconsistency; the user's follow-up confirms it should change | Needs a minor ticket per the follow-up | `🎫 [minor] raise a ticket: {the fix} · {permalink}` |
| Teammate hands the user a ticket, reassigning it to them | They need to read it - a summary would help | `📝 summarise {ticket} for review · {permalink}` |
| Colleague asks the user a direct question in a thread and nobody has answered | A reply is needed, and only the user can give it | `💬 reply to {name} in #{channel}: {what the reply needs to settle} · {permalink}` |
| The user promised in chat to do something themself ("I'll send the figures Friday") | Only the user can do it; a reminder on their own list is the whole action | `☑️ to-do: send {name} the figures by Friday · {permalink}` |
| Multi-party thread where a technical approach was debated and agreed | Internal discussion, not much action the user themself needs to take | no board line; `runs.proactive-router.fyi` gets `{approach} agreed in thread · {permalink}` |
| A process/decision worked out in DM (e.g. how a metric should be formatted) | Worth capturing, not acting on | `📖 kb note: document {the decision} · {permalink}` |

## The `summarise` / `fyi` split

They are different categories with different outcomes (`categories.md`). `summarise` is
for "I've been handed something and need the gist" - a ticket reassignment, a long thread
the user was pulled into - and it gets a board line. `fyi` is for "there is genuinely
nothing here" - no reply needed, no reading required beyond what already happened - and
it never gets a board line: it is one line in `runs.proactive-router.fyi`, which the
briefing message lists. Don't default to `fyi` because writing a summary feels like more
work; don't default to `summarise` because a message looks important - check which one
the content actually calls for.

## Before landing on `fyi`

Check whether the user's own later reply in the same thread states or implies a concrete
ask. Several real cases look inert on the reacted-to message alone but the actual
instruction sits in the user's own follow-up - a colleague reports a bug with no proposed
fix, and the user's reply says what the fix should be. When that's present, classify on
the follow-up, not the original message. Only after checking this, if there's still
nothing to act on, record `fyi` with the one-line reason and write nothing to the board -
never invent an action the content doesn't support.
