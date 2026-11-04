# I owe

What the user told someone they would do, kept at the top of every list `build` writes and
filtered to one person in `prep`. A promise is the easiest thing to lose: it was said in
passing, to one person, and nothing reminds the user of it. This section is that reminder.

## What counts

A commitment is a statement by the user, to a named person or group, that they will do,
check or come back with something, **with a concrete object**. Keep the user's own words.

- First person: "I'll ...", "I can check about Q2", "I'll get back to you", "let me find
  out", "leave it with me", "I'll come back to you on ...".
- Attributed, where someone else records it: "you said you would go back to Lisa", "as you
  told Ivan", "you promised ...".
- Not a commitment: an acknowledgement with no object ("sounds good", "will do"), something
  someone else will do, a promise already delivered, a condition that never came up ("if it
  does, I'll ..."). Those are dropped, not listed.

## Where candidates come from

The extraction subagents of `SKILL.md` step 2 already read these; each is asked to flag any
candidate that is a commitment and to return it in the shape below. Nothing is read twice.

| Source | Reads | Horizon |
|---|---|---|
| Chat | the user's own messages: one `from:me` search, `after:` set 14 days back, paged up to 3 pages | 14 days |
| Tracker | the user's own comments on the tickets already read | 14 days |
| Meetings | transcripts: what the user said they would do (none when `notetaker.service` is `none`) | the list window |
| Session notes | unchecked `Open threads` lines in `kb.paths.sessions` notes that name a person | 30 days |
| State | `action-sweep`'s `items` with `category: to-do`, on the board or off it. Their text already says who and where ("you said so in #planning", "as you told Ivan") | 30 days |

A to-do from state has `written_at` (when it was found), not when it was promised: take the
promise date from the permalink's own timestamp, else from the text, else `written_at`
shown as `~`. The same promise often surfaces twice (a chat message and its to-do); dedupe by
permalink and keep the one with the most evidence.

## What an extractor returns

```
owed_to:     <person, or the channel or team, as written>
what:        <the thing promised, one clause, a concrete verb and object>
quote:       <the user's words, verbatim>
promised_at: <date and time of the message, meeting or note>
link:        <permalink, ticket, note or meeting>
source:      chat | tracker | meeting | session-note | state
```

`owed_to` is resolved against `kb.people_file` and `people_confusions` before it is written
(people sharing a first name are a real case): an ambiguous first name is flagged
`[TBC: which <name>?]` in the section, never defaulted.

## Verify

`SKILL.md` step 3 applies to every owed row. Look for a later message, ticket comment,
transcript line or note showing the user did it (or the person withdrew the ask). Done:
the row moves to **Dropped** with that evidence. Nothing found: it stays, and a source that
could not be read is named under "Couldn't confirm", never assumed delivered.

## The section

Placed after the window read and the time available, before "If you only do three things".
One table, oldest promise first:

```markdown
## I owe

| Owed to | What you said you'd do | Promised | Age | Link | Row |
|---|---|---|---|---|---|
| Ana Reyes | Send the depot-map feedback: "I'll get it to you after lunch" | Wed 14 Oct, 10:12 | 0 bd | [DM](...) | #1 |
| Lisa Chen | Go back to her about the Q2 figures: "I can check about Q2" | Mon 5 Oct, 16:40 | 7 bd | [thread](...) | - |
```

- **Age** is business days: the weekdays (Mon-Fri, `org.timezone`) after the promise date up
  to and including today, so a promise made today is `0 bd`. Public holidays are not
  treated specially, as in `briefing`.
- **Row** is the `#` of the ranked action that does it, or `-` when nothing in the window
  does. An owed item with a ranked row is not described twice: the row carries the draft, this
  line carries the promise.
- Where the sources show nothing owed, one line says so and names the sources read.

## Ranking

An owed item ranks above any other row of equal urgency (`SKILL.md` step 4), oldest promise
first, and the ranked row's "why" quotes the promise. A promise with a deadline inside the
window is already first; a promise with none is not pulled above one that has.
