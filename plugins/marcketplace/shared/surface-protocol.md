# Surface protocol

Read this before any skill touches `profile.surface` or writes a line anywhere on it. It generalises the canvas contract proven in the source `briefing`, `proactive-router`, `vault-dream`, `cloud-idea-scout` and `cloud-idea-wireframe` skills into one shared protocol every ported skill follows the same way.

## What the surface is

One shared board (`profile.surface`, default `kind: slack_canvas`, id `profile.surface.id`) that every skill reads and a subset write to. It is not a chat thread and it is not a scratchpad: it is the one place state persists between runs that the user can see and direct with a checkbox. Each section on the board has exactly one owning writer. No other skill edits that section, ever, no matter how relevant the content looks from outside.

Other surface kinds may exist (`profile.surface.kind`, served by whatever `profile.tools.chat` resolves to per `tool-capabilities.md`), but the section/owner/tick model below applies regardless of kind - a Slack canvas is the reference implementation, not the only legal one.

## Section table

| Heading | Owner | Type |
|---|---|---|
| Calendar, Tracker | briefing | snapshot |
| To-do | user (briefing closes) | acknowledge |
| Running behind | briefing writes, hub dispatches | delegate |
| Terms to learn | briefing | acknowledge (tick promotes to glossary; never logged to Closed) |
| Proactive opportunities | proactive-router | delegate |
| Ideas: decisions for you | idea-scout, idea-deep-dive (append only) | acknowledge at v1 |
| Wireframes to review | idea-wireframe | acknowledge |
| Actions | action-sweep | delegate (tick = push that draft) |
| Dream log / actions | kb-dream | delegate |
| Skill health | skill-health-check | acknowledge |
| Plugin notices | any skill, fast-fails only | info |
| Closed | briefing | log, 14 days or 40 lines |

Two rows list an owner pair (Running behind; Ideas). In each case the two named skills have distinct jobs on the same heading - a writer that produces the content, and either the hub that dispatches it or a second appender that only adds lines and never rewrites the first writer's lines. Nothing else touches those headings.

## The two section types, and why the distinction exists

Every section is either **acknowledge** or **delegate**. The type governs what a tick means, and getting it wrong means the surface lies about what a tick does.

- **Acknowledge.** A tick means "done / seen / confirmed" - a fact about the world the user is reporting, not an instruction to act. The reporter (briefing) is the one that notices the tick and moves the line to Closed. No handler is dispatched. To-do, Terms to learn, Ideas: decisions for you, Wireframes to review and Skill health are acknowledge sections.

  **One exception, in Terms to learn only.** A ticked term is promoted into `state.glossary` and its line is removed from the section. It is **not** written to Closed. A confirmed term is a vocabulary fact the system has absorbed, not a task anyone completed, and logging it as closed work pads the log with entries the user never asked for. This is deliberate, inherited from the reference implementation; do not "fix" it into consistency with the other acknowledge sections.
- **Delegate.** A tick means "you do it" - an instruction the hub (proactive-router) picks up, classifies if needed, and dispatches to a handler. The reporter only closes the line once a handler report sub-line exists underneath it - closing on the tick alone would claim work happened that didn't. Running behind, Proactive opportunities, Actions and Dream log/actions are delegate sections.

The distinction exists because the same UI gesture (a checkbox) has to carry two different kinds of commitment, and conflating them is exactly how a stray tick on an FYI line ends up filing a ticket, or a real delegated task sits forever because the reporter thought ticking it was the whole job.

## Line grammar and tags

Every checkbox line on the surface follows one grammar:

```
- [ ] (<tag>) <emoji> <one self-contained line> · <ref>
```

- The line must stand alone - readable and actionable without opening the source. No "see thread" as the whole line.
- Separator between the sentence and the reference is ` · ` (middot), never a dash or a pipe.
- The emoji is the category signal (`handler-contract.md` has the full table); acknowledge sections that carry no category (To-do, Terms to learn, Skill health) may omit it.

**Tag forms**, worked:

| Form | Example | When |
|---|---|---|
| Ticket-bound | `(PRJ-164)` | The line is about a specific tracker item; reuse its key verbatim, no prefix |
| Skill-abbreviation + date + sequence | `(pr:260922-03)` | proactive-router's third item logged on 22 Sep 2026 |
| Same, other skills | `(dream:260922-1)`, `(sweep:260922-2)`, `(rb:260922-1)` | kb-dream, action-sweep, running-behind respectively - one skill-abbreviation per writer, agreed once, never reused for a different writer |

A tag is the item's identity across runs. `state.items.<tag>` holds what was written and its text hash, which is how a writer tells "still exactly as I left it" from "the user touched this" on its next read. Never invent a tag form ad hoc; if a new writer needs one, pick a short lowercase abbreviation and record it in that skill's `references/` so it's stable.

## Tick / edit / delete / user-added semantics

`state.items` holds the text hash of what was written, so every writer can classify a line on its next read without guessing:

| State on re-read | Meaning | Effect |
|---|---|---|
| Untouched (hash matches) | No user action | Leave exactly as written |
| Ticked (checkbox on, text hash matches) | Acknowledge: closes · Delegate: hub dispatches | Reporter or hub acts per section type |
| Edited, not ticked (text hash differs, checkbox off) | **The user's edited wording is authoritative and is never rewritten by the owning skill.** | `tally.edited += 1`; the edited text stands as the new baseline for future hash comparison |
| Edited and ticked | Dispatch (or close) the edited text, not the original | Same as ticked, but the payload/record uses what the user now has written |
| Deleted (tag present in `state.items`, line absent from the surface) | The user dismissed it | **Never re-add it.** A suppression is added (`state.suppressions`); `tally.deleted += 1` |
| User-added line (new line, no matching tag) | The user is directing the system, not reporting on a prior write | In To-do it carries forward untouched by any writer but the reporter's close-on-tick. In Proactive opportunities it is classified next hub run like any other item and dispatched only if ticked |

The authoritative-edit rule is the single most important row here: an owning skill that "fixes" a user's edited wording back to its own phrasing destroys the one channel the user has to correct or refine what's on the board without losing the tick's effect. Never do it, for any section, for any reason.

## The snapshot rule

Snapshot headings (Calendar, Tracker, and any future skill-owned read-only section) hold **one dated block per heading**, in the form `**{Day date, HH:MMam/pm}:** ` followed by the list. Rules, all mandatory:

1. **Replaced in the same batch.** The new dated block and the removal of the old one are both operations inside one write call. Never leave the old block sitting below the new one - two dated blocks under one heading is two contradictory answers to the same question (same item, different state) and reads as a run that never happened.
2. **Written every run, even when unchanged.** The refreshed stamp on identical content is the signal the check happened. Skipping the write because "nothing changed" is the bug, not an optimisation - it leaves a stale timestamp that reads as a skipped run.
3. **`Signed out` body for a dead connector.** A snapshot section whose source connector failed still gets a fresh stamp; the body is the single word `Signed out`. The run continues; this is a degradation, not a fast-fail (see `tool-capabilities.md`).

Worked example, adapted from `source/briefing/SKILL.md` (tracker snapshot after a 5:13pm run; project key and names fictionalised):

**Right:**

```
# :ticket: Tracker

**Sep 10, 5:13pm:**

* [PRJ-231](…) Dashboard: top cost increases table - In Review, assigned J. Alvarez
* [PRJ-166](…) Prior-month comparison should be like-for-like MTD - Parking lot, unassigned
```

**Wrong** (what the replace prevents): a `**Sep 10, 5:13pm:**` block prepended above a surviving `**Sep 10, 6:27am:**` block under the same heading - two stamps, two lists, no way to tell which is current.

## The section_id_mapping reuse rule

A read of the surface returns a `section_id_mapping` (or equivalent addressing structure for the surface kind in use). That mapping is **valid only until anything writes to the surface**. Consequences:

- One read and one write batch per skill per run. Read once at the start, hold the mapping, issue every operation for the run inside one write call.
- If anything else has written to the surface between the read and the write (another skill's run overlapped, the user edited live), re-read before writing. Never reuse a stale mapping, and never invent a section id when one isn't found - fall back to the documented degradation for that skill (create the section conservatively, say so in the run's report) rather than guessing an id.
- **Critical invariant: handlers never write to the surface.** A dispatched handler subagent returns its result to the hub (`handler-contract.md`'s return JSON); it never calls the surface-update tool itself. This is what makes the hub the single writer of its own run - every operation against this run's `section_id_mapping` originates from one caller, so the mapping-validity rule above can't be violated by a handler racing the hub's own write. If a skill is not the hub and not the section's owning writer, it does not hold write access to the surface at all in its `## Needs`.

## Settle before you append

Any skill that writes items into a section it will revisit on a later run settles that
section's existing lines before adding new ones. The order matters and it is always the
same: read, settle what is already there, then append this run's items.

Settling means checking each of its own prior lines against what is now true:

- A **ticked** line: confirm against real state what the tick claims, then act on it per the
  section's type, and leave it for the reporter to close. Do not re-post an item that has
  been dealt with.
- An **edited** line: the user's wording is authoritative and stands. Never rewrite it back.
- A **deleted** line: it is gone deliberately. Never re-add it, in this run or any later one.
- An **untouched** line: leave it exactly as written, and do not post a duplicate of it just
  because this run rediscovered the same underlying thing.

Never tick or delete one of your own lines except as the outcome of settling it this way.
A writer that appends without settling produces a section that grows monotonically and
repeats items the user has already handled, which is the fastest way to make the surface
not worth reading.

This applies to every owning writer, and it applies per section rather than per skill: two
skills that append to the same section each settle their own lines and leave the other's
alone.

## The one carve-out: the hub's sub-lines

Delegate sections are owned by the skill that writes their items (Running behind by briefing, Actions by action-sweep, Dream log/actions by kb-dream), but the skill that dispatches their ticked items is the hub. So the hub must be able to write into sections it does not own, and the ownership rule above has exactly one carve-out:

**The hub may append a report sub-line, and a `needs your tick` follow-up line, beneath a ticked item in any delegate section. It may not touch anything else in that section** - not the parent item's text, not an untouched item, not the section heading, not another skill's sub-line. Everything else in a section it does not own is read-only to the hub.

Likewise the reporter (briefing) may tick-close an item from any section into Closed, because Closed is briefing's own heading and the close is a move, not an edit of the source line's wording.

No other cross-section write exists. If a skill finds itself wanting one, that is a design error to raise, not a rule to bend.

## Handler report sub-line grammar

When a delegate item has been dispatched and a handler has returned, the hub (or reporter, for sections the hub doesn't own) adds one sub-line directly under the parent item:

```
  - ↳ <handler> <date time>: <done | partial | blocked | needs your tick> · <one sentence> · <link>
```

Two-space indent, `↳` arrow, handler name, timestamp, one of the four fixed outcome words, one sentence of what happened, one link.

One documented variant exists: when a ticked item's category has no handler, the hub writes `  - ↳ router: no handler for <category> yet · tick recorded (n of 3) · <link>` instead. It carries no timestamp and no outcome word because nothing was dispatched and nothing ran. This is the only sub-line form that departs from the grammar above; see `handler-contract.md`'s unmapped-tick behaviour. `needs your tick` is not a terminal outcome: it means the handler reached an irreversible step (file the ticket, post the comment, send the message) and stopped short of doing it, so the hub adds a **fresh delegate line** whose tick is the second, irreversible tick - see below. The reporter closes a delegate item to Closed only once a `done` (or a resolved `needs your tick` that itself resolved to done) sub-line exists; a `partial` or `blocked` sub-line keeps the parent open for the next run.

## The `needs your tick` two-tick flow

Some actions are irreversible once fired (file a ticket, push a comment, send a reply) and the surface's tick is the only consent mechanism in this system - nothing executes without a tick (see `handler-contract.md`'s Learning section). For these, dispatch happens in two stages carried by two separate ticks:

1. **First tick** on the original delegate line dispatches the handler in a drafting mode. The handler produces the artefact (a draft reply, a drafted ticket) and returns `needs_confirmation`/`needs your tick` with a link to the draft.
2. The hub writes a fresh delegate line under the original item's sub-line, naming the specific irreversible step (`file the ticket`, `push the comment`).
3. **Second tick**, on that fresh line, dispatches the handler again in its confirming mode (`push`, `file`) - and only that mode is allowed to perform the actual external write.

This mirrors `canvass`'s (now `action-sweep`) draft-then-push confirmation exactly: drafting is free to redo, the external write is not, and the two are separated by a tick each rather than a single "are you sure?" question a scheduled run can't ask.

## The Closed log

Format, one line per closed item, newest first:

```
- <date> (<tag>) <outcome> · <original text, 120 chars> · <by you | by <handler>>
```

`<outcome>` is a short past-tense phrase (`done`, `filed PRJ-172`, `acknowledged, no handler`). `<original text, 120 chars>` is the item as it stood when closed (post-edit if the user edited it), truncated. `<by you | by <handler>>` records who actually did the work - the user themself (acknowledge sections, or a delegate item the user ticked and then did manually) or the handler that reported `done`.

**Retention: 14 days or 40 lines, whichever comes first.** The reporter (briefing) trims the oldest lines past either bound on every run it writes Closed - this is a mechanical trim, not a judgement call, and it happens whether or not anything new closed this run.

## Never

- Never edit outside your section, with exactly one carve-out (below). Every skill's `## Needs` names the one heading it owns (plus read access to whatever else it needs to read); write access to any other heading is out of scope regardless of how relevant the content looks.
- Never re-add a deleted line. A tag that appears in `state.items` with no matching surface line was deleted by the user; a suppression exists for a reason, and re-adding it defeats the entire learning mechanism.
- Never invent a section id. A missing section is handled by each skill's documented degradation (create conservatively and say so, or skip and flag in Plugin notices) - never a guessed id against a stale or absent mapping.
- Never leave two dated blocks under one heading. The snapshot rule's replace-in-batch requirement is not optional; a leftover second block is always a bug to fix on sight, in any skill that finds one under a heading it owns.
- Never write to the surface from a handler subagent. Handlers report back to the hub in the return JSON; the hub (or, for non-hub sections, the section's owning writer) is the only caller that ever issues a surface write for a given run.
