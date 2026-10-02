# Lens: challenge

The strongest honest case against the idea, so the user finds the hole before someone in
the room does. It takes a side. A challenge that ends "on balance it depends" has not done
its job.

## Inputs

The known packet only. No web, no codebase. This lens is cheap on purpose so it can run
first, every time, in seconds.

## Where to dig, in order

Work through these and keep the ones that actually bite on this idea; most ideas have one
or two real weaknesses, not five.

1. **The load-bearing assumption.** The single belief the idea needs to be true that
   nobody has shown is true: "dispatchers want a push" when the evidence is that they asked
   for a report. Name it and name what evidence is missing.
2. **Who loses.** The user, team or customer this makes worse off - extra noise, a broken
   habit, a support burden, a sales promise it undercuts.
3. **The cheaper 80%.** A smaller change (a setting, a column, a doc, an email) that gets
   most of the value. If one exists, that is the challenge.
4. **Wrong problem.** The ticket solves a symptom; the cause sits elsewhere.
5. **Timing.** Why now is the wrong time: a dependency not yet built, a decision pending
   upstream, a sibling idea that changes the shape of this one.

## Shape

Follow the output contract in `SKILL.md`. The verdict is a position ("Don't build the alert
yet; the drift data it needs is a nightly batch, so the alert is a day late by design").
Each finding's "so what" names the decision it pushes. Sources here are the packet itself
(a comment, a line in the ticket, something the user said) - quote the exact phrase that
exposes the weakness, so the user can see it is not invented.

**Forks for the user.** When a weakness has two or more real ways forward, end the lens
with up to two forks, each a question and 2 to 4 concrete options. In the Next watch these
become the board's decision groups; in a session they are just the last thing on screen.

## Worked example (fictional, against `profiles/example.md`)

> **Verdict** - Build it, but as a digest first: an alert that fires per drift will be muted
> inside a week.
>
> - Dispatchers already re-check plans "every couple of hours" (FIG-204 comment, Tomasz,
>   12 Sep), so the gap is minutes, not hours · FIG-204 comments · **so what:** the value
>   case rests on speed, and it is thinner than the ticket implies; size it smaller.
> - Nothing in the ticket says who acts on the alert at 2am · FIG-204 description · **so
>   what:** forces the channel decision before the threshold decision.
>
> **Checked, no bearing** - linked sibling FIG-188 (different user, different trigger).
> **Would change my mind** - a support ticket where a missed drift cost a delivery.
