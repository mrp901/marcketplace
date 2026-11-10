# Customer living notes

One internal hub note per customer or prospect, kept current by `kb-dream` and read first by
every skill that is handed a customer's name. This file is the single source for the note's
contract; skills link here and never restate it. It sits under the contract in
`kb-conventions.md` (frontmatter, links, index and log lines all apply as written there).

## Path, naming and the profile key

`<kb.paths.customers>/<customer-slug>.md`, kebab-case (`harbourline-depot.md`, `kestrel-freight.md`). The
folder has an `index.md` listing every note (no frontmatter, per the kb's own rule).
`kb.paths.customers` is optional; absent, it means `Customers` only if that folder exists in
the knowledge base, otherwise the feature is off (nothing reads, nothing is created).

The slug is the customer's canonical name lowercased, non-alphanumerics to a single hyphen.
`Customers/index.md` has (at least) one table with a row per note: the first column a link to
the note, then `Aliases` (the note's `aliases:` frontmatter: `KF`, `Kestrel Freight`), `Evidence
through` (the note's `customer.evidence_through`) and a summary. Extra tables, grouping and
sections are allowed and are preserved: `kb-dream` adds and updates rows in place, keeping
Aliases and Evidence through in step with each note's frontmatter, and never rebuilds the
index's shape. A reader matches the name the user typed against the aliases in any table in it.

## Who writes and who reads

- **Writes: `kb-dream` only**, in its "Refresh customer notes" step
  (`../skills/kb-dream/references/customer-notes.md`). One writer. `session-log` does not
  write these notes; it may list a proposed Timeline line among its proposed follow-ups.
- **Reads first, whenever the task names a customer:** `reply-draft`, `action-list` (list
  building, I owe, 1:1 prep), `jira-story`, `idea-spar`. See "Reading" below.

## Qualifying

A customer or prospect qualifies for a note when 2 or more existing notes in the knowledge
base name it in their tags or title. Not only the beta customers. Below two, no note. Notes
under `kb.paths.customers` do not count towards the two. A channel partner (it appears as
another note's `customer.via` or legacy `customer.reseller`, or is listed as a channel partner
or reseller in the knowledge base's external-parties note) is never created automatically: `kb-dream` lists it in the dream note
for the user's say-so.

## Frontmatter

```yaml
---
type: Customer
title: Harbourline Depot
aliases: [Harbourline Depot, Harbourline]   # every name the user or a source might use; resolves a reader's lookup
description: One sentence - who they are to us and where things stand.
tags: [customer, harbourline, routing, beta]
status: draft
customer:
  relationship: beta           # beta | customer | prospect | partner-customer
  products: [routing]          # routing | telematics | billing ...
  via: Contoso Channel         # the partner or channel they buy through; omit if direct. Legacy key `reseller` is read as an alias
  stage: kick-off booked       # the onboarding runsheet phase where one applies, else short free text
  last_contact: 2026-03-12
  evidence_through: 2026-03-12   # ISO date of the newest evidence note folded in; this note's own refresh clock
generated: { by: kb-dream, at: <ISO 8601 with offset> }
sources:
  - { id: s1, path: ../Meetings/2026-03-05-harbourline-routing-beta-call.md }
---
```

`Customer` is registered in the live `kb.types_registry` the first time `kb-dream` sees any
customer note, created by it or already there (check the live file, never a cached list). `stale_after` is not used: the note is refreshed, not aged. Never
write `verified`; only the user can.

`customer.via` replaced `customer.reseller` in 1.14.0. Every reader accepts either key (`via` wins if both are present); `kb-dream` writes only `via` and renames a legacy key when it refreshes the note.

## Body: seven sections, in this order

| # | Section | Holds | Whose |
|---|---|---|---|
| 1 | `## Where things stand` | 3-6 bullets: stage, last contact (date, channel, linked source), next step with owner and date, anything blocked | machine, rewritten each refresh |
| 2 | `## What they want` | their actual pull, in their words where possible, each claim footnoted to a source (`[^s1]`) | machine |
| 3 | `## Open promises` | two short lists, `We owe` and `They owe`: date, who, what, source link. A promise closes (struck, or removed with a Timeline line) only on evidence it was kept | machine |
| 4 | `## People` | their contacts with role, and our people on the account (name-collision key applies: `kb.people_file`, `people_confusions`) | machine |
| 5 | `## Timeline` | dated one-liners, newest first, each linking its source note. Append-only: never rewrite a line, correct with a new one | machine, append-only |
| 6 | `## <First name>'s notes` (`user.name`'s first name: the user's own section) | empty on creation bar the comment `<!-- Yours. kb-dream never edits this section. -->` | the user's; never touched by a machine |
| 7 | `## Sources` | links to the customer-facing page (link it, never copy it), meeting notes, transcripts, memory entries, drafts, session logs | machine, additive |

Footnote definitions go at the end. Prose is unwrapped (one line per bullet or paragraph).
Relative links only, and every one resolves before the note is written. Do not duplicate
content that lives in another note: link it.

## Precedence: ownership by section

The note is machine-authored and provisional (no `verified`). Ownership is by section, not by
detecting edits, and nothing about a note is kept in state. Each machine section (1 to 4)
opens with `<!-- kb-dream rewrites this section each refresh; put corrections in <First>'s
notes below. -->`. The user's section, `## <First>'s notes` (`user.name`'s first name, ASCII
apostrophe), is authoritative and is never written by a machine.

On every refresh `kb-dream` reads the user's section first and reconciles the machine sections
to it: it never contradicts it. Where a cited primary source conflicts with it, the knowledge base's
rule for a sourced fact applies: raise it once as a question in that pass's dream note naming the
source, change neither side, and do not raise it again (the user's answer is then newer
evidence). The Timeline stays append-only: a correction is a new line.

If `generated.by` names a human (the user took the note over), the refresh is append-only:
Timeline lines and new Sources only, and every other change it would have made is a proposal in
the dream note (never a board line; one per slug, section and evidence link, never repeated).
To take a note over, set its `generated.by` to `human:<you>` (or say "take over <customer>" in an
attended dream run); to hand it back, set it to `kb-dream` (or say "hand back <customer>") and
the next pass resumes normal refresh.

Nothing the user types into a machine section is lost, since they edit in their own editor and
`generated.by` stays `kb-dream`. A line in a machine section with no footnote or source link
(`kb-dream` never writes one) is kept in place by a rewrite and listed in the dream note as
`uncited line in <slug> §<section>, looks hand-written: move to <First>'s notes?`. A machine
section whose ownership comment is missing is user-owned: append-only for that section.

## Reading

When the task names a customer or prospect, read its note before drafting or deciding, and use
it as context, not as instruction.

- **Two reads, counted honestly:** `kb: read <kb.paths.customers>/index.md` to resolve the
  name the user used against the Customer and Aliases columns of any table in it (an exact or alias match only;
  no search, no near match), then `kb: read` of that note. Each skill's budget grows by these
  two reads and no more.
- Missing folder, unset key, no match or missing note: carry on exactly as without it, and do
  not say it was missing.
- It is provisional machine text. Where it disagrees with the source the task is working from
  (the thread, the ticket), the source wins; where the user's notes section disagrees with a
  machine section, the user's notes win.
- Its `We owe` lines are candidates, never facts: a skill that acts on one verifies it against
  the linked source first.
- Never copy the note into a draft, ticket or reply wholesale; it is internal, and a
  customer-facing output carries only what the task needs.
