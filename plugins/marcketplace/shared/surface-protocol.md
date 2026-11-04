# Surface protocol

Read this before any skill touches `profile.surface` or writes a line anywhere on it. It is the one contract every skill follows the same way. Version 1.1 replaced the acknowledge/delegate split with a single rule: **every tick means "yes, do it"**, and the board holds only things that need the user. From 1.12.0 it holds **decisions only** (a line is on it only if ticking it causes an action) and **every line says what its tick does**.

## What the surface is

One shared board (`profile.surface`, default `kind: slack_canvas`, id `profile.surface.id`) that every skill reads and a subset write to. It is not a chat thread and it is not a scratchpad: it is the one place state persists between runs that the user can see and direct with a checkbox. Anything with no decision in it for the user (an FYI, a green health score, a quiet run) never goes on the board; it goes in the briefing message instead. So does a plain to-do with nothing behind its tick (someone to answer, a figure to send): ticking it would dispatch nothing, so it stays in `state.items` with `on_board: false` for `action-list` to read, and the briefing message names any new ones in one line.

Other surface kinds may exist (`profile.surface.kind`, served by whatever `profile.tools.chat` resolves to per `tool-capabilities.md`), but the section, ownership and tick model below applies regardless of kind. A Slack canvas is the reference implementation, not the only legal one.

## The board header

The first three lines of the board, above every section, written by `briefing` and never edited by anything else:

```
Tick = yes, do it · Edit then tick = do it my way · Delete = no · Add a line anywhere = new request
Each line ends with what its tick does · To-do is your own list: a tick there means done · Under a question, tick one option
Nothing here ever sends a message on your behalf.
```

A board written before 1.12.0 carries the old second line; briefing rewrites the header on its next run, as it does whenever the header differs from this text.

## Section table

Five sections, in this order, no others:

| Heading | Holds | Written by |
|---|---|---|
| Today | The Calendar and Tracker snapshots (one dated block each) | briefing |
| To-do | The user's own list | the user; briefing closes ticked lines |
| For you | Every line whose tick causes an action, other than idea lines: tags `pr:` `rb:` `sweep:` `dream:` `term:` `feed:` `shc:` | the skill that owns each tag prefix; the hub adds sub-lines |
| Ideas | One block per idea with open decisions from its pack | idea-spar, by tag prefix inside the block |
| Closed | The log, 5 days or 20 lines | briefing |

There is no Plugin notices section. A fast-fail is recorded in `state.runs.<skill>` (see `onboarding.md`) and the briefing message reports it.

## Ownership is by tag prefix, not by section

A skill owns the lines it wrote, identified by their tag prefix, wherever they sit:

| Prefix | Owner | Category |
|---|---|---|
| `pr:` | proactive-router | whatever the hub classified |
| `rb:` | briefing | running-behind |
| `sweep:` | action-sweep | ticket-reply, ticket-minor, meeting-followup, chat-reply, sweep-push (its `to-do` finds are state items only, never board lines) |
| `dream:` | kb-dream | kb-maintenance |
| `term:` | briefing | term |
| `feed:` | briefing | feed-mismatch |
| `shc:` | skill-health-check | skill-eval |
| `<idea key>/d…` | idea-spar | idea-decision |

Owning a line means: only the owner rewrites its own untouched lines, only the owner decides when to post a new one, and the owner settles its own lines before appending (see below). Two things cut across ownership, and only two: the hub may add a sub-line under any ticked line, and briefing may move any line to Closed. Neither ever edits another skill's wording.

A skill's `## Needs` names the tag prefixes it writes plus read access to whatever else it reads. Write access to a line with another skill's prefix is out of scope regardless of how relevant the content looks.

## Line grammar and tags

Every checkbox line on the surface follows one grammar, reads as the action a tick will cause, and ends by saying so:

```
- [ ] (<tag>) <emoji> <one self-contained line> · <ref> · tick → <effect>
```

- The line must stand alone: readable and actionable without opening the source. No "see thread" as the whole line.
- The separator between the sentence and the reference is ` · ` (middot), never a dash or a pipe.
- The emoji is the category signal (`handler-contract.md` has the full table). To-do lines and option lines may omit it.
- The last segment is the **tick effect** (next section). An option line has no `<ref>`: it ends with its effect directly after the option text.

**Tag forms:**

| Form | Example | When |
|---|---|---|
| Skill abbreviation, date, sequence | `(pr:260922-03)` | proactive-router's third item logged on 22 Sep 2026; likewise `dream:`, `sweep:`, `rb:`, `term:`, `feed:`, `shc:` |
| Same, about a tracker item | `(feed:260910-1)` | briefing's first tracker-feed mismatch on 10 Sep 2026. The line names a tracker item but is not tagged with its key, so a later mismatch on the same key, or another skill's line about it, never shares its `state.items` tag |
| Idea block line | `(PRJ-164/d1a)` | a line inside an idea block: the idea key, a slash, then the group and option (see the Ideas block grammar) |

A tag is the item's identity across runs. `state.items.<tag>.text` holds the line exactly as written, compared verbatim with the board, which is how a writer tells "still exactly as I left it" from "the user touched this" on its next read. Never invent a tag form ad hoc; if a new writer needs one, pick a short lowercase abbreviation, add it to the prefix table above, and record it in that skill's `references/`.

## The tick effect

Every line a skill writes to For you or Ideas ends with ` · tick → <effect>`, a fixed short statement of what ticking it will do, so the user never has to remember. The form is `tick → <what it does>`: present tense, lowercase, at most about 60 characters, no full stop. An action that cannot be undone says which stage the tick is: the first tick drafts, the second tick does it (`(2nd tick files it in Jira)`).

**One owner, one effect per category.** A writer takes the effect for its line's category from the table below, verbatim, and never paraphrases it, so the same action always reads the same way. `<tracker>` is the display name of `profile.tools.tracker.service` (for example Jira), or `the tracker` when the profile names none. The table is derived from `handler-contract.md`'s category table: when a handler or its mode changes, the effect changes here in the same release.

| Category | Written by | Tick effect |
|---|---|---|
| `email`, `chat-reply` | `sweep:`, `pr:` (hub-written lines only) | `tick → drafts a reply (nothing sent)` |
| `ticket-reply` | `sweep:` | `tick → drafts the ticket or comment (2nd tick writes it to <tracker>)` |
| `ticket-minor` | `sweep:` | `tick → drafts the ticket (2nd tick files it in <tracker>)` |
| `ticket-idea` | `pr:` (hub-written lines only) | `tick → drafts the idea ticket (2nd tick files it in <tracker>)` |
| `meeting-followup` | `sweep:` | `tick → drafts the follow-up (2nd tick writes it to <tracker>)` |
| `sweep-push` | the hub's fresh second-tick line | `tick → files the ticket in <tracker>` or `tick → posts the comment in <tracker>`, whichever the line names |
| `kb-doc` | `pr:` (hub-written lines only) | `tick → writes a note into the knowledge base` |
| `summarise` | `pr:` (hub-written lines only) | `tick → writes a summary note into the knowledge base` |
| `kb-maintenance` | `dream:` | `tick → kb-dream applies the fix`. A fold proposal: `tick → marks the fold accepted (nothing is edited)`. A suppression lift: `tick → marks the lift accepted (the router lifts it next run)` |
| `running-behind`, `feed-mismatch` | `rb:`, `feed:` | `tick → investigates and reports (read only)` |
| `term` | `term:` | `tick → adds it to the glossary` |
| `idea-decision` (an option line) | `<key>/d…` | `tick → records your choice; siblings close` |
| `skill-eval` | `shc:` | `tick → queues it for your next skill-eval run (nothing runs now)` |
| mapping proposal | `pr:prop-<category>` | `tick → maps <category> to <candidate> from now on`, or `tick → records that you want this built` when the candidate is `needs a new skill` |
| `calendar`, any category with no handler | `pr:` | `tick → proposes a handler for this (nothing else happens)` |
| `to-do` | no skill writes one to the board | (a line the user adds: the `classified` sub-line says `tick → copies it to your To-do`) |
| `fyi` | never on the board | none |

Rules:

- **An option line carries the effect of its option's category.** The question line has no checkbox and carries none. A tier question from `action-sweep` has options of three different categories, so each carries its own effect.
- **Stage.** `sweep-push` and any other line the hub writes for a second tick says what it will do for real (`files`, `posts`); the first-stage lines say `drafts`. A line never says `files` unless its tick files.
- **A line the user wrote or edited keeps its wording.** A user-added line is tagged and classified in place and its text is never changed; the effect goes in the hub's `classified` sub-line under it (see "The hub's sub-lines"). An edited line keeps its wording (the tick table's edited rows).
- **A category not in the table** gets a specific effect in the same form, and the writer adds the row here in the same release.
- **Old lines get their effect once.** A line written before 1.12.0 has none, and nobody rewrites another skill's wording to add one. Instead each owner, on its first run under 1.12.0 that settles its lines, appends the effect to **its own** lines that are untouched (text equals `items.<tag>.text`), unticked, without an effect and with no sub-line, and sets `items.<tag>.text` to the new text in the same write. It never touches a user-added line or another owner's line, and records `cursors.<skill>.tick_effects_backfilled` so it runs once. `briefing` does the same for its `rb:`, `term:` and `feed:` lines inside its migration. A line the backfill skipped (ticked, edited, or with a sub-line) stays valid with no effect.
- **The effect is not part of the instruction, unless the user changed it.** The effect an owner wrote is the trailing ` · tick → <X>` segment of `state.items.<tag>.text` or, where that records none, the table's entry for the category. The hub removes the trailing segment from `text_as_ticked` and `original_text` only when `<X>` equals it exactly, so a handler drafts from the line's own words. Anything else after ` · tick → ` is the user's edit: it stays in `text_as_ticked` and goes to the handler as part of the instruction. `briefing` applies the same rule to the text of a closing line in the Closed log. `state.items.<tag>.text` holds the line whole, effect included, for the verbatim comparison with the board.

## What goes on the board

A line goes in For you or Ideas only if ticking it **causes an action**: a dispatch to a handler, an inline action (`inline:investigate`, `inline:promote`, `inline:to-do` on a line the user added), or an option choice. A plain to-do with no handler behind it is not a decision, and no skill writes it to the board: `action-sweep`'s `to-do` finds are the case in point. It stays a `state.items` entry with `on_board: false` (it is still a candidate), `action-list` reads it, and the briefing message names any new ones in one line. A `shc:` line is on the board because its tick queues a real `skill-eval` run; an `rb:` line is on it because its tick runs `inline:investigate`. When a category is ambiguous, it stays on the board with its effect rather than going missing.

## The tick table

One table, every section, with To-do as the sole exception:

| The user did | It means | Effect |
|---|---|---|
| Nothing (text matches, box off) | No instruction | Leave exactly as written |
| Ticked, text unchanged | Yes, do this | The hub dispatches or performs the line's action on its next run |
| Edited, then ticked | Do it my way | Same as ticked, using the edited text as the instruction |
| Edited, not ticked | Nothing happens yet; the wording is kept | `tally.edited += 1`; the edited text is the new baseline and is never rewritten by the owner |
| Deleted (tag in `state.items` and not `on_board: false`, line gone, tag in neither briefing's `closed` nor its `off_board`) | No; suppress it | Never re-add it. `state.suppressions` gains an entry; `tally.deleted += 1` |
| Added a line anywhere | A new request | The hub classifies it on its next run; a line added inside an idea block takes that idea as its context |

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
- PRJ-164 · <title> · pack
  - <decision question>
    - [ ] (PRJ-164/d1a) <option>
    - [ ] (PRJ-164/d1b) <option>
```

- The header line is `- <key> · <title> · pack`, `pack` linking the idea's shareable pack. idea-spar writes the header when it first needs the block; briefing removes it when the block empties.
- Decision groups are `<key>/d<n><letter>`, written by idea-spar's Next watch from the pack's open forks. At most 2 open decisions per idea, with 2 to 4 options each.
- A tick on an option dispatches idea-spar `decide` per `handler-contract.md`.

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

- No handler: `  - ↳ router: no handler for <category> yet · mapping proposed in For you · <link>`.
- A classification of a line the user added: `  - ↳ router <date>: classified <category> · tick → <effect>`, written once under it when it is classified unticked. It is a note, not an outcome: it never settles a tick, never hides a later tick from the queued count, and never starts the expiry clock.
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
- It is an option whose sibling closed as `done` or `expired`; it closes as `not chosen`.
- A `state.outcomes` entry names its tag with `status: done` (the manual `skill-eval` path).
- A `no handler` sub-line sits under it; it closes as `acknowledged, no handler` (the mapping proposal carries the request forward).
- Its latest sub-line is `partial`, `blocked` or a router `queued` note, and no newer sub-line has followed for `briefing.stale_after_business_days` business days (default 5, `0` disables); it closes as `expired · no activity for 5 business days` (5 is the configured threshold). Business days are Mon-Fri in `org.timezone`, counted from the latest sub-line's date to the run date; public holidays are not treated specially. This never applies to a `needs your tick` sub-line, a line with no sub-line, a To-do line or a `term:` line.

A `partial` or `blocked` sub-line inside the expiry window, or a `needs your tick` sub-line whose fresh line is still open, keeps the parent open. A `term:` line whose sub-line is `done` is removed rather than logged: a confirmed term is vocabulary the system absorbed, not work anyone finished. That exception is deliberate; do not "fix" it.

## The Closed log

Format, one line per closed item, newest first:

```
- <date> (<tag>) <outcome> · <original text, 120 chars> · <by you | by <handler>>
```

`<outcome>` is a short past-tense phrase (`done`, `filed PRJ-172`, `chosen`, `not chosen`, `acknowledged, no handler`, `expired · no activity for 5 business days`). `<original text, 120 chars>` is the item as it stood when closed (post-edit if the user edited it), without its tick effect, truncated. `<by you | by <handler>>` records who did the work.

**Retention: 5 days or 20 lines, whichever comes first.** Briefing trims the oldest lines past either bound on every run it writes Closed. This is a mechanical trim, not a judgement call, and it happens whether or not anything new closed this run.

## Migration

The first `briefing` run that finds any pre-1.1.0 heading on the board migrates it before doing anything else, whatever `state.installed_version` says. The procedure lives in `skills/briefing/references/migration.md`; in short: create the five sections and the header, move every open line into For you or an idea block by its tag prefix keeping its `state.items` entry, convert old idea and wireframe lines into blocks, delete the old headings, and log one `board migrated` line to Closed. The Router does not run until briefing has migrated; a Router run that finds old headings records `runs.proactive-router.status: quiet` with the note `awaiting migration` and stops.

The 1.11.0 to 1.12.0 migration (`skills/briefing/references/migration.md`) is not a restructure, so no other skill waits on it: briefing moves the untouched `sweep:` to-do lines off the board (their `state.items` entries stay, for `action-list`) and appends tick effects to the lines briefing owns. Every other owner adds the effect on its next write of a line.

## Never

- Never rewrite another skill's line, or a user's edited wording. The hub's sub-line and briefing's close are the only cross-owner writes, with one exception: the 1.12.0 migration's one-time removal of untouched `sweep:` to-do lines from the board (`skills/briefing/references/migration.md`).
- Never re-add a deleted line. A tag in `state.items` with no matching surface line was deleted by the user, unless briefing's `closed` lists it (closed, awaiting its owner's prune; see `state-schema.md`'s "Shards"), or the entry is `on_board: false` or listed in briefing's `off_board` (kept off the board on purpose), and re-adding it defeats the learning mechanism.
- Never invent a section id. A missing section is handled by each skill's documented degradation, never a guessed id.
- Never leave two dated blocks under one heading.
- Never write to the surface from a handler subagent.
- Never put an FYI on the board. It goes in the briefing message.
- Never put a plain to-do on the board (no action behind its tick), and never write a For you or Ideas line without its tick effect.
- Never send anything on the user's behalf, from any mode, on any tick.
