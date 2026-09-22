# Curation passes

Each finding is either **acted** (confident, mechanical, reversible) or **surfaced**
(needs the user, or would overrule a human). Act only when all three hold: mechanically
checkable; reversible in one move (recycle location plus connector history, never a hard
delete, never flattened history, never a touched `verified` note); not an overrule of
`verified: { by: human:<user> }` content or a pick between two human-reviewed notes. Fail
any one and surface instead. When in doubt, surface.

| Pass | Act | Surface |
|---|---|---|
| **1. Inbox triage** (primary job; ignore `index.md`) | Obvious `type` and one clear owning folder: full frontmatter, kebab-case name, move, add to that folder's `index.md`, log. Bias toward filing - the inbox's rule is "it doesn't stay". | Ambiguous item; a fragment that belongs merged into an existing note; anything reading as a decision for the user. Leave it in `kb.paths.inbox`. |
| **2. Conformance** | Invalid or missing YAML; missing any of `kb.frontmatter_required`; wikilinks where `kb.link_style` is `relative_markdown` (or vice versa); spaces in filenames; a folder without `index.md`; an index entry missing or drifted from the note's own description. | A `type` that looks wrong for the content. |
| **3. Duplicates and contradictions** | Obvious duplicate: merge to the fuller note, cross-link, supersede-and-recycle the thin one per the supersession mechanic below. A fact already superseded by a later note or `log.md` correction: update the stale mention, keep the old value in a banner with why. | Two substantial notes that overlap with unique content each (propose the merge); a contradiction the precedence rule can't call (same date, recency unknowable). |
| **4. Orphans and broken links** | See `link-pass.md`. |
| **5. Staleness and follow-ups** | - | A note past its own stale bound; open follow-ups or threads named in session notes since the last dream, consolidated into one list. |
| **6. Name and fact watch** | A `known_fact_errors` or `people_confusions` entry reintroduced in new capture being filed, or in any machine-authored note: fix, log `**Correction**`. | Same error in an established human-verified note: surface, don't rewrite. Never report the human's own writing as a corrected-fact hit. |
| **6b. Provenance timestamps** (machine-authored notes) | - | A note's own `generated.at` falling outside the plausible window set by other evidence (file save time, a chat message timestamp, a `log.md` line). Flag both timestamps and their source; never silently correct. |
| **7. Cross-session insight** | - | One to three things now true that no single note captures: a pattern across sessions, a decision whose consequences haven't propagated, a recurring question, two notes that should know about each other. Proposals, not edits. |
| **8. Machine-voice check** (scope: `generated.by` is an agent, never `human:<user>`) | A machine-authored note reads machine-sounding: heavy em-dash use in place of a plain sentence, a colon-truncated fragment standing in for a sentence, a bracket placeholder, an orphaned one-line label with nothing after it. Rewrite the specific sentence in the same pass you already touch that note for another reason. Never a standalone vault-wide sweep for this alone. | Anything in a `human:<user>`-generated note, even if it superficially matches a pattern here. The user's own house style is not machine voice. If genuinely unsure whether a note is machine- or human-authored, surface rather than touch it. |

## Known errors

Passes 6 and 6b check newly filed or machine-authored content against
`profile.known_fact_errors` and `profile.people_confusions` - facts and name pairs that
have been wrong before and must not silently reintroduce. This list is a floor, not a
ceiling: pass 6b and pass 7 findings qualify on their own evidence even when nothing in
the list names them.

## The supersession mechanic

Superseding a note is never a delete. It is a banner on the surviving note plus a move of
the old file to the knowledge base's recycle location (a dot-hidden or otherwise
non-indexed subfolder under `kb.paths.utility`, `<utility>/dream-recycle/<YYYY-MM-DD>/
<original-name>`), never `rm`. If the connector can't move a file, leave it, banner it,
and surface "needs a manual move" rather than forcing a write the connector can't do
safely.

## The five-rule contract

Carried intact from the base skill, non-negotiable:

1. **Never destroy an input.** No hard deletes, ever - see the supersession mechanic above.
2. **Never flatten history.** Preserve every supersession banner and the "why it changed"
   line; write one when you supersede anything.
3. **Never overrule a human silently.** Don't machine-edit the substance of
   `verified: { by: human:<user> }` content, and per pass 8, don't machine-edit its voice
   either. When you edit any note, set `generated: { by: kb-dream, at: <now> }` and leave
   `verified` exactly as is - deleting it erases a real review, bumping it fabricates one.
   `generated` postdating `verified` is legal and honest; note the divergence in the
   curated table.
4. **The human's file is the current one.** Human-generated content is the up-to-date
   version. Human beats machine: correct or supersede the machine note, never flag the
   human file. Newer human content beats older human content: state which is live, don't
   ask. Still surface: two human artefacts of the same date, or where applying the rule
   means removing human reasoning.
5. **The dream note is the reviewable output.** Everything changed and concluded, in one
   dated note.

## The repetition bar for failed writes

See `repetition-bar.md` - this rule belongs to `kb-dream` alone, not the shared contracts.
