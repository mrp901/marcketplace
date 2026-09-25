# Surface protocol

Read this before any skill touches `profile.surface` or writes a line anywhere on it. It is the one contract every skill follows the same way. Version 1.1 replaced the acknowledge/delegate split with a single rule: **every tick means "yes, do it"**, and the board holds only things that need the user.

## What the surface is

One shared board (`profile.surface`, default `kind: slack_canvas`, id `profile.surface.id`) that every skill reads and a subset write to. It is not a chat thread and it is not a scratchpad: it is the one place state persists between runs that the user can see and direct with a checkbox. Anything with no decision in it for the user (an FYI, a green health score, a quiet run) never goes on the board; it goes in the briefing message instead.

Other surface kinds may exist (`profile.surface.kind`, served by whatever `profile.tools.chat` resolves to per `tool-capabilities.md`), but the section, ownership and tick model below applies regardless of kind. A Slack canvas is the reference implementation, not the only legal one.

## The board header

The first three lines of the board, above every section, written by `briefing` and never edited by anything else:

```
Tick = yes, do it · Edit then tick = do it my way · Delete = no · Add a line anywhere = new request
To-do is your own list: a tick there means done. Under a question, tick one option.
Nothing here ever sends a message on your behalf.
```

## Section table

Five sections, in this order, no others:

| Heading | Holds | Written by |
|---|---|---|
| Today | The Calendar and Tracker snapshots (one dated block each) | briefing |
| To-do | The user's own list | the user; briefing closes ticked lines |
| For you | Every line that needs the user's tick, other than idea lines: tags `pr:` `rb:` `sweep:` `dream:` `term:` `shc:` | the skill that owns each tag prefix; the hub adds sub-lines |
| Ideas | One block per idea with open decisions, wireframe reactions or a refresh question | idea-scout, idea-deep-dive, idea-wireframe, by tag prefix inside the block |
| Closed | The log, 7 days or 40 lines | briefing |

There is no Plugin notices section. A fast-fail is recorded in `state.runs.<skill>` (see `onboarding.md`) and the briefing message reports it.

## Ownership is by tag prefix, not by section

A skill owns the lines it wrote, identified by their tag prefix, wherever they sit:

| Prefix | Owner | Category |
|---|---|---|
| `pr:` | proactive-router | whatever the hub classified |
| `rb:` | briefing | running-behind |
| `sweep:` | action-sweep | ticket-reply, ticket-minor, meeting-followup, chat-reply, to-do, sweep-push |
| `dream:` | kb-dream | kb-maintenance |
| `term:` | briefing | term |
| `shc:` | skill-health-check | skill-eval |
| `<idea key>/d…`, `<idea key>/r` | idea-scout | idea-decision, idea-refresh |
| `<idea key>/q…` | idea-deep-dive | idea-decision |
| `<idea key>/w-…` | idea-wireframe | wireframe-reaction |

Owning a line means: only the owner rewrites its own untouched lines, only the owner decides when to post a new one, and the owner settles its own lines before appending (see below). Two things cut across ownership, and only two: the hub may add a sub-line under any ticked line, and briefing may move any line to Closed. Neither ever edits another skill's wording.

A skill's `## Needs` names the tag prefixes it writes plus read access to whatever else it reads. Write access to a line with another skill's prefix is out of scope regardless of how relevant the content looks.

## Line grammar and tags

Every checkbox line on the surface follows one grammar, and reads as the action a tick will cause:

```
- [ ] (<tag>) <emoji> <one self-contained line> · <ref>
```

- The line must stand alone: readable and actionable without opening the source. No "see thread" as the whole line.
- The separator between the sentence and the reference is ` · ` (middot), never a dash or a pipe.
- The emoji is the category signal (`handler-contract.md` has the full table). To-do lines and option lines may omit it.

**Tag forms:**

| Form | Example | When |
|---|---|---|
| Skill abbreviation, date, sequence | `(pr:260922-03)` | proactive-router's third item logged on 22 Sep 2026; likewise `dream:`, `sweep:`, `rb:`, `term:`, `shc:` |
| Idea block line | `(PRJ-164/d1a)` | a line inside an idea block: the idea key, a slash, then the group and option (see the Ideas block grammar) |

A tag is the item's identity across runs. `state.items.<tag>` holds what was written and its text hash, which is how a writer tells "still exactly as I left it" from "the user touched this" on its next read. Never invent a tag form ad hoc; if a new writer needs one, pick a short lowercase abbreviation, add it to the prefix table above, and record it in that skill's `references/`.

## The tick table

One table, every section, with To-do as the sole exception:

| The user did | It means | Effect |
|---|---|---|
| Nothing (hash matches, box off) | No instruction | Leave exactly as written |
| Ticked, text unchanged | Yes, do this | The hub dispatches or performs the line's action on its next run |
| Edited, then ticked | Do it my way | Same as ticked, using the edited text as the instruction |
| Edited, not ticked | Nothing happens yet; the wording is kept | `tally.edited += 1`; the edited text is the new baseline and is never rewritten by the owner |
| Deleted (tag in `state.items`, line gone) | No; suppress it | Never re-add it. `state.suppressions` gains an entry; `tally.deleted += 1` |
| Added a line anywhere | A new request | The hub classifies it on its next run like a swept message; a line added inside an idea block takes that idea as its context |

**To-do is the exception.** It is the user's own list. A tick there means "done" and briefing moves the line to Closed on its next run. Nothing dispatches from To-do, and no skill writes into it except the hub's `inline:to-do` action, which adds a line the user asked for.

The edited-not-ticked row is the single most important one: an owner that "fixes" a user's edited wording back to its own phrasing destroys the one channel the user has to refine what's on the board without losing the tick's effect. Never do it, for any line, for any reason.

## Option groups

A choice is a plain question line with one checkbox per option under it, indented two spaces:

```
- <question, one line>
  - [ ] (<tag>a) <option>
  - [ ] (<tag>b) <option>
```

- Tick one to choose it. The hub acts on the chosen option; the others close as `not chosen` in the same close.
- Ticking two gets a `  - ↳ router: blocked · pick one` sub-line under the question, and nothing happens until exactly one is ticked.
- An edited option is a variation of that option: edit it, tick it, and the edited text is what happens.
- A line added under the question is a new option, classified like any user-added line.
- Two to four options per question. A question with one option is a plain line.

The question line carries no checkbox and no tag of its own; `state.items` records each option with `group: <the question's tag stem>` so the hub can find its siblings.

## The Ideas block grammar

The Ideas section holds one block per idea that has anything open. Blocks are removed by briefing once they have no open lines.

```
- PRJ-164 · <title> · note · wireframe
  - <decision question>
    - [ ] (PRJ-164/d1a) <option>
    - [ ] (PRJ-164/d1b) <option>
  - How does the wireframe land?
    - [ ] (PRJ-164/w-keep) 👍 Keep this wireframe direction
    - [ ] (PRJ-164/w-rework) 🔁 Rework: edit this line to say what to change
    - [ ] (PRJ-164/w-drop) 🗑️ Drop it
  - [ ] (PRJ-164/r) ⬆️ Moved <parked slot> → <slot>. Refresh the research?
```

- The header line is `- <key> · <title> · <link text per artefact>`: `note` links the research note, `wireframe` links the wireframe, each present only once it exists. Whichever idea skill first needs the block writes the header; briefing removes it when the block empties.
- Decision groups are `<key>/d<n><letter>` (idea-scout) and `<key>/q<n><letter>` (idea-deep-dive). At most 2 open decisions per idea, with 2 to 4 options each. A stuck or paused deep-dive question is one line, `(<key>/q<n>) <question> · edit this line with your answer and tick`.
- Wireframe reactions are one group of three (idea-wireframe).
- The refresh line `<key>/r` is idea-scout's roadmap watch.
- Ticks on any of these dispatch per `handler-contract.md`: decisions to idea-scout `decide`, reactions to idea-wireframe `react`, the refresh line to `inline:requeue`.

## The snapshot rule

Snapshot blocks (Calendar and Tracker under Today, and any future read-only block) hold **one dated block each**, in the form `**{Day date, HH:MMam/pm}:** ` followed by the list. Rules, all mandatory:

1. **Replaced in the same batch.** The new dated block and the removal of the old one are both operations inside one write call. Two dated blocks under one heading is two contradictory answers to the same question and reads as a run that never happened.
2. **Written every run, even when unchanged.** The refreshed stamp on identical content is the signal the check happened.
3. **`Signed out` body for a dead connector.** A block whose source connector failed still gets a fresh stamp; the body is the single word `Signed out`. The run continues (see `tool-capabilities.md`).

Worked example (tracker block after a 5:13pm run; project key and names fictionalised):

```
**Sep 10, 5:13pm:** Tracker

* [PRJ-231](…) Dashboard: top cost increases table - In Review, assigned J. Alvarez
* [PRJ-166](…) Prior-month comparison should be like-for-like MTD - Parking lot, unassigned
```

## The section_id_mapping reuse rule

A read of the surface returns a `section_id_mapping` (or equivalent addressing structure for the surface kind in use). That mapping is **valid only until anything writes to the surface**. Consequences:

- One read and one write batch per skill per run. Read once at the start, hold the mapping, issue every operation for the run inside one write call.
- If anything else has written to the surface between the read and the write, re-read before writing. Never reuse a stale mapping, and never invent a section id when one isn't found: fall back to the documented degradation for that skill (create the section conservatively, say so in `state.runs.<skill>.note`) rather than guessing an id.
- **Handlers never write to the surface.** A dispatched handler subagent returns its result to the hub (`handler-contract.md`'s return JSON); it never calls the surface-update tool itself. If a skill is not the hub and owns no tag prefix, it does not hold write access to the surface at all in its `## Needs`.

## Settle before you append

Any skill that writes lines it will revisit on a later run settles its existing lines before adding new ones. The order is always the same: read, settle what is already there, then append this run's lines.

Settling means checking each of its own prior lines against the tick table:

- A **ticked** line: leave it for the hub. The owner never acts on its own ticks; the hub dispatches them, including back to the owner as a handler. Do not re-post an item that has been dealt with.
- An **edited** line: the user's wording is authoritative and stands.
- A **deleted** line: it is gone deliberately. Never re-add it, in this run or any later one.
- An **untouched** line: leave it exactly as written, and do not post a duplicate just because this run rediscovered the same underlying thing.

Never tick or delete one of your own lines. A writer that appends without settling produces a board that grows monotonically and repeats items the user has already handled.

## The hub's sub-lines

The hub may append a report sub-line, and a `needs your tick` follow-up line, beneath a ticked line anywhere on the board. It may not touch anything else: not the parent line's text, not an untouched line, not a heading, not another skill's sub-line.

When a line has been dispatched and a handler has returned, the hub adds one sub-line directly under it:

```
  - ↳ <handler> <date time>: <done | partial | blocked | needs your tick> · <one sentence> · <link>
```

Two-space indent, `↳` arrow, handler name, timestamp, one of the four fixed outcome words, one sentence of what happened, one link. An inline action uses `router` as the handler name.

Documented variants, the only ones:

- No handler: `  - ↳ router: no handler for <category> yet · tick recorded (n of 3) · <link>`.
- Two options ticked: `  - ↳ router: blocked · pick one`.
- A `shc:` tick: `  - ↳ router: queued for your next skill-eval run`.

`needs your tick` is not a terminal outcome: it means the handler reached an irreversible step (file the ticket, post the comment) and stopped short of doing it, so the hub adds a **fresh line** whose tick is the second, irreversible tick (below).

## The `needs your tick` two-tick flow

Some actions are irreversible once fired (file a ticket, push a comment) and the surface's tick is the only consent mechanism in this system. For these, dispatch happens in two stages carried by two separate ticks:

1. **First tick** on the original line dispatches the handler in a drafting mode. The handler produces the artefact (a drafted ticket, a drafted comment) and returns `needs_confirmation`.
2. The hub writes a fresh line under the original line's sub-line, naming the specific irreversible step (`file the ticket`, `push the comment`).
3. **Second tick**, on that fresh line, dispatches the handler again in its confirming mode (`push`, `file`), and only that mode is allowed to perform the actual external write.

Drafting is free to redo; the external write is not; and the two are separated by a tick each rather than a single "are you sure?" question a scheduled run can't ask. **No mode of any skill ever sends a message on the user's behalf**; a drafted reply is always pasted and sent by the user.

## Closing

Briefing is the only skill that moves lines to Closed, and it closes a line only when one of these holds:

- A `done` sub-line sits under it (a handler or inline action finished).
- It is a To-do line and it is ticked.
- It is an option whose sibling closed as `done`; it closes as `not chosen`.
- A `state.outcomes` entry names its tag with `status: done` (the manual `skill-eval` path).

A `partial` or `blocked` sub-line, or a `needs your tick` sub-line whose fresh line is still open, keeps the parent open. A `term:` line whose sub-line is `done` is removed rather than logged: a confirmed term is vocabulary the system absorbed, not work anyone finished. That exception is deliberate; do not "fix" it.

## The Closed log

Format, one line per closed item, newest first:

```
- <date> (<tag>) <outcome> · <original text, 120 chars> · <by you | by <handler>>
```

`<outcome>` is a short past-tense phrase (`done`, `filed PRJ-172`, `chosen`, `not chosen`, `acknowledged, no handler`). `<original text, 120 chars>` is the item as it stood when closed (post-edit if the user edited it), truncated. `<by you | by <handler>>` records who did the work.

**Retention: 7 days or 40 lines, whichever comes first.** Briefing trims the oldest lines past either bound on every run it writes Closed. This is a mechanical trim, not a judgement call, and it happens whether or not anything new closed this run.

## Migration

The first `briefing` run under a plugin version newer than `state.installed_version` migrates a board laid out under the old section table before doing anything else. The procedure lives in `skills/briefing/references/migration.md`; in short: create the five sections and the header, move every open line into For you or an idea block by its tag prefix keeping its `state.items` hash, convert old idea and wireframe lines into blocks, delete the old headings, and log one `board migrated` line to Closed. The Router does not run until briefing has migrated; a Router run that finds old headings records `runs.proactive-router.status: quiet` with the note `awaiting migration` and stops.

## Never

- Never rewrite another skill's line, or a user's edited wording. The hub's sub-line and briefing's close are the only cross-owner writes.
- Never re-add a deleted line. A tag in `state.items` with no matching surface line was deleted by the user, and re-adding it defeats the learning mechanism.
- Never invent a section id. A missing section is handled by each skill's documented degradation, never a guessed id.
- Never leave two dated blocks under one heading.
- Never write to the surface from a handler subagent.
- Never put an FYI on the board. It goes in the briefing message.
- Never send anything on the user's behalf, from any mode, on any tick.
