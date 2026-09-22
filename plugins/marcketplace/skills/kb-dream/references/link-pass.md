# The link pass

A systematic missing-and-broken cross-reference pass over every note changed this run
(filed from the inbox, edited by any curation pass, or newly written by signal extraction)
- absorbed from `source/_workspace-wikilink-finder.SKILL.md`, adapted to
`kb-conventions.md`'s link-style contract instead of a wikilinks-only assumption.

## Honouring `kb.link_style`

Write every link in whichever style `profile.kb.link_style` names -
`relative_markdown` (`[label](../path.md)`) or `wikilink` (`[[Note Title]]`) - never mix
styles within one note. `scripts/link_resolver.py` implements the mechanical half of both
checks below; it degrades to "resolve manually, connector has no bulk listing" when the
knowledge base is a remote connector with no directory-listing call, rather than failing.

## Broken links

For each link in a changed note, check the target exists:

- **Unambiguous** - the target's basename exists at exactly one other path in the
  knowledge base. Repoint the link and log a `**Update**` line. This is the single most
  common defect in practice: a note filed or moved elsewhere whose old folder's index (or
  another note) still links to it under the old path.
- **Ambiguous** - the basename exists at more than one path, or the path is mangled in a
  way that doesn't resolve to a clean basename. Surface with the candidate paths; never
  guess between them.
- **Forward reference** - the basename exists nowhere. Leave it. A link to a note that
  doesn't exist yet is valid, not-yet-written knowledge under this contract, not an error.

## Missing links

A systematic scan, not a vibe check: for each changed note, look for people, tickets and
named interactions (per the knowledge base's own linking conventions - typically people, tickets, named
meetings/incidents) mentioned in prose but not linked, and for another note whose subject
the changed note discusses without a cross-reference. **Conservative bias throughout**: a
missed link beats a noisy one. Product areas, teams and abstract concepts are never
auto-linked even when a note for them exists - only concrete named entities are.

**Act versus surface.** Repointing an unambiguous broken link is mechanical and reversible
(pass 4's act column) and this skill does it directly. A missing-link *addition* is a
content judgement, not a mechanical repair - it changes what a note points at, not just
fixes what it already claimed - so it is surfaced as a proposed addition rather than made,
by default. No profile key currently exists to configure this the other way; see this
skill's `HISTORY.md` port entry for the open question this leaves for the orchestrator.

## Where results land

Broken-link repoints get one `**Update**` line each in `log.md` (see
`kb-conventions.md`'s index/log maintenance contract) and one row in the dream note's
"What I curated" table. Missing-link proposals get one Surfaced bullet each, batched by
source note when there are several for the same file rather than one bullet per link.
