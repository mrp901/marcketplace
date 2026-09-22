# Scoring rubric

One status tag per skill per check, backed by evidence gathered per
`evidence-gathering.md`. Never assign a tag from impression; if a row of evidence wasn't
gathered (skipped because the skill doesn't match that type, or the source was genuinely
unreachable this run), it doesn't count for or against the tag - it's simply absent, and
that absence is named in the evidence-sources line below.

| Tag | Meaning |
|---|---|
| `green` | Evidence is clean: no correction, no repeated `blocked`/`partial`, conformance checks pass, voice-ledger edits (if any) are isolated rather than clustered. |
| `amber` | Minor conformance issues, or exactly one correction/edit-cluster/`blocked` outcome, nothing structural. |
| `red` | A pattern - more than one correction, a recurring `blocked`/`partial` handler outcome, broken links, or a note/ticket that needed real rework. |

Every log entry and, for amber/red, every surface line carries:

- **2 to 4 evidence bullets**, each naming the specific note, ticket, outcome or ledger entry
  it's about - never a vague "quality seemed off" bullet.
- **One evidence-sources line**, naming which of `evidence-gathering.md`'s rows were actually
  available this run (e.g. "kb frontmatter/links: full, tracker changelog: full, voice
  ledger: none - skill drafts no prose"). This is what stops a thin `green` (nothing checked
  because nothing was available) from reading the same as a well-evidenced one.

A skill this run found no gatherable evidence for at all is not scored - it was already
skipped in `SKILL.md` step 1, before scoring is reached.
