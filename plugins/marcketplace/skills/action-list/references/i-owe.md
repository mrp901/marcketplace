# I owe

What the user told someone they would do, kept at the top of every list `build` writes and
filtered to one person in `prep`. A promise is the easiest thing to lose: it was said in
passing, to one person, and nothing reminds the user of it. This section is that reminder.

## Who decides what

Extractors (search tier) **return every candidate with its evidence and decide nothing**:
anything that might be a promise, an ask or an offer, quoted, whether or not it will survive.
The worker (`budgets.models.worker`) applies "What counts" below and sorts each candidate
into I owe, Waiting on you, or out. Dropping at extraction would lose real promises that
were phrased oddly.

## What counts (applied by the worker)

A **promise** is a statement by the user, to a named person or group, that they will do,
check or come back with something, **with a concrete object**. Keep the user's own words.

- First person: "I'll ...", "I can check about Q2", "I'll get back to you", "let me find
  out", "leave it with me", "I'll come back to you on ...".
- Attributed, where someone else records it: "you said you would go back to Ana", "as you
  told Ivan", "you promised ...".
- **Not a promise:** an acknowledgement with no object ("sounds good", "will do"); something
  someone else will do; a promise already delivered; a condition that never came up ("if it
  does, I'll ..."); and an **offer**: "let me know if ...", "happy to help", "shout if you
  need anything". An offer commits the user to nothing until the other person takes it up.
- **Waiting on you** is a different thing: someone tagged the user, asked them something or
  handed them a task, with no promise from the user. It is listed, so it is not lost, but
  it is not owed and gets no ranking boost.

## Where candidates come from

The extraction subagents of `SKILL.md` step 2 already read these. Nothing is read twice.

| Source | Reads | Horizon |
|---|---|---|
| Chat | the user's own messages: one `from:me` search, `after:` set 14 days back, paged up to 3 pages | 14 days |
| Tracker | the user's own comments on the tickets already read | 14 days |
| Meetings | transcripts: what the user said they would do (none when `notetaker.service` is `none`) | the list window |
| Session notes | unchecked `Open threads` lines in `kb.paths.sessions` notes that name a person | 30 days |
| State | `action-sweep`'s `items` with `category: to-do`, on the board or off it | 30 days |

A to-do from state is classified by its own evidence. "You said so in #planning", "as you
told Ivan", "you said you would" carry the user's promise: **I owe**. "He tagged you", "she
asked you" carry none: **Waiting on you**. A to-do whose text shows neither is Waiting on
you. Its `written_at` is when it was found, not when it was promised: take the date from
the permalink's own timestamp, else from the text, else `written_at` shown as `~`. The same
promise often surfaces twice (a chat message and its to-do); dedupe by permalink and keep the
one with the most evidence.

## Customer notes

When a candidate names a customer or prospect, read that customer's note before ranking
(`../../../shared/customer-notes.md`, "Reading": the customers index once per run, then each
note; at most 3 notes per run). Its `## Open promises` > `We owe` lines are **extra candidates**, not rows: each goes
to the worker with its linked source as its evidence and is classified by "What counts" like
any other. Only a promise the user themself made earns the ranking boost; a `We owe` line made
by someone else is not owed by the user and is dropped, unless it is an ask of the user, which is
Waiting on you. A line with no source link, or whose source cannot be read, is `unverified` and never
boosted. Verification (step 3) applies unchanged and a line the source shows kept is dropped.
The note is provisional machine text: where it disagrees with the source, the source wins.

## What an extractor returns

```
who:         <the person, channel or team, as written>
quote:       <the words, verbatim, with the sentence around them>
at:          <date and time of the message, meeting or note>
link:        <permalink, ticket, note or meeting>
source:      chat | tracker | meeting | session-note | state
```

The worker adds `what` (one clause, a concrete verb and object) and the class. `who` is
resolved against `kb.people_file` and `people_confusions` before it is written (people
sharing a first name are a real case): an ambiguous first name is flagged
`[TBC: which <name>?]`, never defaulted.

## Verify, within the cap

`SKILL.md` step 3 verifies at most 10 candidates per build, one targeted read each, owed rows
first. Look for a later message, ticket comment, transcript line or note showing the user did
it (or the person withdrew the ask). Done: the row moves to **Dropped** with that evidence,
and a to-do that came from state is recorded in this skill's shard as
`settled: {<tag>: <settled_at>}`, so `action-sweep` prunes its entry
(`../../../shared/state-schema.md`, "Closing an off-board to-do"). A candidate past the cap
stays listed, marked `unverified, <age> bd`, and a source that could not be read is named
under "Couldn't confirm"; neither is ever assumed delivered.

## The section

Placed after the window read and the time available, before "If you only do three things".
Two tables, oldest first.

```markdown
## I owe

| Owed to | What you said you'd do | Promised | Age | Link | Row |
|---|---|---|---|---|---|
| Ana Reyes | Send the depot-map feedback: "I'll get it to you after lunch" | Wed 14 Oct, 10:12 | 0 bd | [DM](...) | #1 |
| Ana Reyes | Go back to them about the Q2 figures: "I can check about Q2" | Mon 5 Oct, 16:40 | 7 bd | [thread](...) | - |

**Waiting on you** (asked of you, no promise from you)

| From | The ask | Since | Age | Link | Row |
|---|---|---|---|---|---|
| Tomasz Nowak | Whether the MTD comparison includes cancelled loads: "he tagged you" | Tue 6 Oct | 6 bd | [FLT-166](...) | - |
```

- **Age** is business days: the weekdays (Mon-Fri, `org.timezone`) after the date up to and
  including today, so something from today is `0 bd`. Public holidays are not treated
  specially, as in `briefing`.
- **Row** is the `#` of the ranked action that does it, or `-` when nothing in the window
  does. A row with a ranked action is not described twice: the row carries the draft, this
  line carries the promise or the ask.
- A row not verified (over the cap) carries `unverified` after its age.
- Where the sources show nothing, one line says so and names the sources read.

## Ranking

Only a **promise** earns the boost: it ranks above any other row of equal urgency
(`SKILL.md` step 4), oldest first, and the ranked row's "why" quotes it. A Waiting-on-you row
ranks like any other "someone is waiting" row. A promise with a deadline inside the window
is already first; a promise with none is not pulled above one that has.
