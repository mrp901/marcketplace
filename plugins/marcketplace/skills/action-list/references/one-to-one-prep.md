# 1:1 prep

A short note for one conversation with one person: what is owed each way, what they have
asked, what was left open last time and what keeps coming back. It is read on a screen in
two minutes before the meeting. `build`'s formatting rules carry over (a transient draft in
`kb.paths.drafts`, quoted evidence, `[TBC: ...]` for a fact the sources cannot settle,
nothing sent), per `list-format.md`.

## Resolve the person

1. Match the user's words against `people` (name, nickname, `email`, `chat_id`, role) and
   `kb.people_file`. The match's `chat_id` and `email` scope every search below: a search by
   name alone finds the wrong person.
2. A first name that fits more than one person is resolved from
   context (the team, the meeting, the user's wording) or asked once with the candidates and
   their roles. Never pick the likelier one.
3. Apply `people_confusions` to every name read from a transcript before matching: a mangled
   name in a transcript is the same person, not a new one.
4. Say the resolved full name and role at the top of the note.

## Find where the kb keeps 1:1 notes

Do not hardcode a folder. In order, stop when found:

1. The person's entry in `kb.people_file`, if it links their notes.
2. `kb.conventions_file`'s own folder table or the folder `index.md` files: the folder
   described as 1:1 prep, meetings or onboarding.
3. `kb: search` for the person's name with `1:1`, `one-to-one`, `agenda` or `prep` in the
   title, filename or tags.

Take the newest two prep or agenda notes that name the person, and the meeting notes with
them in the last 60 days. If none exists, say so in one line: the first prep has no "carried"
section.

## The five extractions

Each is a search-tier subagent, in parallel, returning every candidate quoted with a link and
a timestamp and deciding nothing. Nothing is sent or edited.

| # | Section | Reads |
|---|---|---|
| 1 | You owe them | The "I owe" pipeline (`i-owe.md`) with `who` = the person, plus "I'll ..." lines in the person's earlier 1:1 notes. Extractors return every candidate; the worker applies "What counts" |
| 2 | They owe you | The person's own promises to the user ("I'll send you", "I can check"): chat DMs and threads, their tracker comments, transcripts, earlier 1:1 notes; and tickets assigned to them that the user is waiting on |
| 3 | Their open asks | What they sent the user since the last 1:1 (or 14 days) that expects an answer and has none: chat, email, tracker comments mentioning the user. A bare cc or fyi is dropped |
| 4 | Carried from earlier 1:1s | In the newest two prep or agenda notes: unchecked items, lines under "carry over", "follow up", "next time" or "parked", and questions with no recorded answer |
| 5 | Recurring themes | The last 4 meetings with them (transcripts, or meeting and session notes naming them): a subject in two or more, with the dates and a quote from each |

## Verify and write

Step 3 of `SKILL.md` applies, including its cap of 10 verified candidates (owed rows first;
the rest are listed `unverified` with their age): re-check each is still open and drop what
is resolved, with the evidence. A "carried" item that a later note or meeting settles is
dropped, not carried again. A theme is kept only when it is still unresolved or the user
would want it raised; say "settled on <date>" in one clause otherwise.

A critic-tier subagent reads the note cold against the sources: a wrong person, a name
collision, an item the sources show done, a row with no quote. Fix what it finds.

## Format

Path: `kb.paths.drafts` + `YYYY-MM-DD-HHMM-<person>-1on1-prep.md`. Frontmatter as in
`list-format.md`: the title `1:1 prep: <Person> (<D Mon YYYY>)`, `generated` by
`action-list`, `stale_after` the next day, and the same `supersedes_on`. A second prep for the
same person and day gets the new time in its name and a pointer banner on the first.

Body, in order, each section capped at 7 rows (the rest as `+N more`, naming where):

1. **Who and what was read** - full name, role, the last 1:1 found (date, link), the
   sources read, and "Nothing has been sent, posted or edited anywhere. `[TBC: ...]` marks a
   fact I couldn't verify."
2. **If you only raise three things** - one sentence each, quoting the words that make it
   matter.
3. **You owe them** - the `i-owe.md` table without its "Owed to" column.
4. **They owe you** - what, their words, promised, age in business days, link.
5. **Their open asks of you** - the ask quoted, when, age, link.
6. **Carried from earlier 1:1s** - the item, the note it came from (linked), and whether it
   is still open.
7. **Recurring themes** - the subject in one line, the dates, a short quote from each.
8. **Couldn't confirm** - what the sources could not settle, and any source that could not
   be read.

Offer to draft any message the note implies; the prep itself drafts none. All five empty: write
no note, say so in one line and record `runs.action-list` as `quiet`.
