# Posted message format

The one nudge briefing sends via `../../../shared/notify.md`. No footer, no "Sent using" tag,
no acknowledgement text beyond this shape - the notify transport handles delivery, this shape
handles everything the user reads.

```
[@{user.name}]({deep link to user}) here's your briefing for {Day date, HH:MMam/pm}

{calendar emoji} Calendar

* {time range} {subject} {collision flag if it overlaps something else today}
  prep: {prep line, if notetaker.prep_lines produced one for this event}
* Out today: {nicknames}

{chat emoji} Unread

* {tag or nickname} DM: {one plain sentence}
* #{channel} thread: {who, what, still open?}
(or "Nothing new since last briefing")

{tracker emoji} Tracker

* [KEY]({link}) {summary} - {status}, assigned {nickname/tag}
(or "Signed out")

Since last briefing

* {handler} {outcome}: {one sentence} - {link}
* {n} ticked item(s) queued, waiting on the next dispatch run
(or "Nothing to report" if state.outcomes has no entries since last_run_ts and nothing is queued)

{link emoji} [Full briefing & to-dos]({surface.url})
```

Full sentences, no padding, one blank line between sections. Emoji per section are the
plugin's own house set (calendar, chat, tracker, link - not the category emoji from
`handler-contract.md`, which only appear inside surface lines, never in the posted message).

## Worked example

Fictionalised against `profiles/example.md` (Northwind Logistics / Freight Ops), a run at
5:13pm local:

```
[@Priya Kanth](https://northwindlogistics.slack.com/team/W1EXAMPLEUSR1) here's your briefing for Sep 10, 5:13pm

:calendar: Calendar

* 2:00-2:30pm Dock scheduling sync
  prep: last instance's notes cover the multi-yard allocation question raised again today
* Out today: Tomasz

:speech_balloon: Unread

* Ana DM: wants a decision on the dashboard cost-table layout by Friday
* #freight-ops thread: Owen flagged a support ticket spike, still open

:ticket: Tracker

* [FLT-231](https://northwindlogistics.atlassian.net/browse/FLT-231) Dashboard: top cost increases table - In Review, assigned Tomasz
* [FLT-166](https://northwindlogistics.atlassian.net/browse/FLT-166) Prior-month comparison should be like-for-like MTD - Parking lot, unassigned

Since last briefing

* reply-draft drafted a reply to Ana's dashboard question - needs a tick to send
* 1 ticked item queued, waiting on the next dispatch run

:point_right: [Full briefing & to-dos](https://northwindlogistics.slack.com/docs/TEXAMPLE001/FEXAMPLECANVAS1)
```

## Glossary use inside the message

Before writing an unfamiliar acronym, project codename or internal term into any section
above, check it against `state.glossary` and `state.nicknames` per
`glossary-and-terms.md`. A confirmed glossary entry may be used inline with its short gloss,
e.g. "LoadBalance (the Freight Ops yard-allocation flow)" - a fictional stand-in for the kind
of internal shorthand a real glossary entry would carry. Never invent or guess a definition in
the posted text; an unrecognised term is used verbatim and left for the user to interpret -
capturing it is step 5's Terms to learn job, never an editorial aside inside the briefing
itself.
