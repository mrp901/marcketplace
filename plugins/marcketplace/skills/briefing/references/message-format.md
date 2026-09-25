# Posted message format

The one message the plugin sends, via `../../../shared/notify.md`. No footer, no "Sent
using" tag, no acknowledgement text beyond this shape.

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

* {handler} {outcome}: {one sentence} · {link}
* {n} ticked item(s) queued, waiting on the next dispatch run
Runs
* {skill} {status}: {note} · {link}
* health: {skill} green · {skill} amber ({why})
* fyi: {one line} · {permalink}
* overdue: {skill} last ran {n} days ago (expected every {max_gap_days})
(or "Nothing to report" if there are no outcomes, nothing queued and no runs in the window)

{link emoji} [Full briefing & to-dos]({surface.url})
```

Full sentences, no padding, one blank line between sections. Emoji per section are the
plugin's own house set (calendar, chat, tracker, link), not the category emoji from
`handler-contract.md`, which only appear inside board lines, never in the posted message.
See `closed-and-outcomes.md` for how each line of "Since last briefing" is built.

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

* reply-draft done: drafted a reply to Ana's dashboard question · teammate-chat · Drafts/pr-260910-02.md
* 1 ticked item queued, waiting on the next dispatch run
Runs
* proactive-router ok: 2 new lines, 1 dispatched · https://northwindlogistics.slack.com/docs/TEXAMPLE001/FEXAMPLECANVAS1
* idea-scout ok: first pass on FIG-204, 2 decisions on the board · Product/FreightOps/Research/fig-204-load-plan-variance-alerts.md
* kb-dream quiet: nothing new since the last dream
* health: idea-scout green · reply-draft amber (2 of 3 drafts edited before sending)
* fyi: batch-overnight recalculation agreed in #platform-eng · https://northwindlogistics.slack.com/archives/CEXAMPLEAPPRCH1/p1758510005000500
* overdue: action-sweep last ran 11 days ago (expected every 8)

:point_right: [Full briefing & to-dos](https://northwindlogistics.slack.com/docs/TEXAMPLE001/FEXAMPLECANVAS1)
```

## Glossary use inside the message

Before writing an unfamiliar acronym, project codename or internal term into any section
above, check it against `state.glossary` and `state.nicknames` per
`glossary-and-terms.md`. A confirmed glossary entry may be used inline with its short
gloss, e.g. "LoadBalance (the Freight Ops yard-allocation flow)". Never invent or guess a
definition in the posted text; an unrecognised term is used verbatim and left for the
user to interpret. Capturing it is step 5's `term:` line job, never an editorial aside
inside the briefing itself.
