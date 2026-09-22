# Knowledge base conventions

The generic version of `source/session-log/references/vault-conventions.md`. Any skill that reads or writes `profile.kb.*` (session-log, kb-note, kb-dream, idea-scout, idea-deep-dive, idea-wireframe, voice calibration) follows this contract. It generalises what the source vault-conventions file documented as instance-specific observation into rules any knowledge base of kind `obsidian_okf | plain_markdown | notion | confluence` can follow.

## The knowledge base as a concept

`profile.kb` names one connected store: `kb.name`, `kb.kind`, `kb.local_root` and/or `kb.remote {service, library, path_prefix}`, a `kb.conventions_file` (default `CLAUDE.md`), a `kb.types_registry`, a `kb.people_file`, and `kb.link_style`. A skill locates the kb root by discovering it (checking connected folders/libraries for `kb.conventions_file` alongside an index carrying the bundle's version marker), never by hardcoding a path - a user's device or drive layout changes, and a stale path fails silently. `kb.paths.*` names the standard subfolders every skill can assume exist or create on first use: `inbox, research, prototypes, screenshots, sessions, dreams, decisions, memory, voice, log, product_index, service_map, utility`.

Read `kb.conventions_file` before writing anything. It is the live authority, and it changes; where it disagrees with any shared reference (including this one), `kb.conventions_file` wins, and the divergence gets a line in the writing skill's output.

## The frontmatter contract

Every note in the knowledge base carries all six of `profile.kb.frontmatter_required`:

| Key | Purpose |
|---|---|
| `type` | The note's registered type (see the type registry below) |
| `title` | Human title. Dated notes carry a parenthetical readable date - `(24 Aug 2026)`, day and abbreviated month - in the title only; the filename stays ISO-first kebab-case |
| `description` | One sentence, used by index entries and previews |
| `tags` | Reuse existing tags before inventing one; two or three topical plus one kind-tag is the house pattern |
| `status` | The note's own lifecycle state (`draft`, `stable`, etc. - vocabulary is kb-local) |
| `generated` | `{ by: <actor>, at: <ISO 8601> }` - see provenance below |

**`generated` versus `verified` - the provenance semantics.** `generated.by` names whichever actor last changed the note's *content* - not who first wrote it. When a machine edits a note whose `generated.by` was a human, `generated` updates to the machine and the current timestamp; `generated.at` postdating `verified.at` is legal and honest, and OKF treats the two fields as independent by design. **A machine never edits the substance or the voice of human-verified content.** `verified: { by: human:<user> }` marks a real human review; a machine that edits a `verified` note's substance or its prose voice is overruling that review silently, which this contract forbids outright - the machine may only touch mechanical conformance (frontmatter shape, link repair, index entries) on a verified note, and even then must say so rather than silently updating `generated`. Never delete `verified` (it erases a real review) and never bump its date to make it look re-confirmed (it fabricates one). A machine-authored note (no human review yet) never carries `verified` at all - writing one would claim a machine-confirmed trust tier the kb has never used.

## The type registry and its single authority

`profile.kb.types_registry` points at one live file inside the kb (typically alongside the conventions file) listing every registered `type` value in use. **That live file is the only authority for what types exist.** A skill must never assert a type is "new" or "not yet registered" from memory, from a cached snapshot, or from a reference document bundled with a skill - it checks the live registry file at run time, every time it's about to make that claim.

The cautionary tale this rule exists to prevent, from the source: `session-log` once asserted `type: Session Log` was unregistered, sourced from a dated audit snapshot bundled as a reference, when the live registry file had already been updated the day before. The mistake cost a `log.md` correction entry. Treat any bundled snapshot of "what types exist" (including anything shipped in a skill's own `references/`) as **learning material for the kb's style**, never as the current state of its registry - re-derive the current state from the live file before asserting anything about it. If a genuinely new type is needed, add it to the live registry file in the same turn, with a one-line justification, rather than proposing it for later.

## Link styles

`profile.kb.link_style` is `relative_markdown` or `wikilink`, and it governs every link a skill writes into the kb:

- **`relative_markdown`** - `[week one retro](../Onboarding/week-one-retro.md)`. Labels are readable prose, not filenames. Never an absolute `/path` - legal in most kb formats but resolved unreliably by local tooling (Obsidian included). Broken links are fine: a link to a note that doesn't exist yet is a forward reference to not-yet-written knowledge, not an error to delete or "tidy up".
- **`wikilink`** - `[[Note Title]]` form, used only where `profile.kb.link_style` is explicitly set to it. Where the kb's own tooling treats wikilinks as native (Obsidian) but the kb is also read by anything that doesn't resolve them (a plain markdown viewer, an export pipeline), `relative_markdown` is the safer default and onboarding should say so when the choice is ambiguous.

Whichever style is configured, apply it consistently across every note a skill writes in one run - never mix styles within a single note or a single skill's output.

## Index and log maintenance contract

Every new note, every time, without exception:

1. **An index line.** The affected folder's `index.md` gets one line, `* [Title](file.md) - description` (or the wikilink equivalent), newest first, description lifted verbatim from the note's own frontmatter. This is also what gives the note its one required inbound link - a note nothing links to is unreachable in the bundle regardless of how correct its own content is, so skipping the index entry doesn't just break conformance, it makes the note functionally invisible.
2. **A log line.** The kb's root log (`kb.paths.log`, typically `log.md`) gets one line under today's date heading, newest first, leading bold verb (`**Creation**`, `**Update**`, `**Merge**`, `**Correction**`, `**Deprecation**`) - path or link, what changed, a concise why. One line, not a paragraph: the log is a ledger a future session or an audit reads, not prose that reads well start to finish.

**The log is append-only.** A line that goes stale within the same session - including one this same run wrote earlier today - is never rewritten in place. Add a `**Correction**` entry pointing at what's true now and linking whatever explains the full sequence (a session note, a dream note). This applies immediately, in the same turn the staleness is noticed, not as a separate cleanup pass later - the fix for the exact failure mode the source `session-log` skill once hit: an earlier log line went stale after a subsequent edit, and it should have been corrected in the same run rather than only mentioned elsewhere.

Where the kb's connector is full-replace rather than append (a SharePoint/OneDrive markdown file rewritten whole on every write, rather than a true append API), and the log file has grown past `profile.kb.log_size_cap_kb.writers` (default 20 KB for ordinary writers, 40 KB for `kb-dream`'s own passes), a skill defers its log line - says so in its own output/surface item - rather than risking a large retype. `kb-dream` owns rotating an oversized log on its own pass.

## Dated file naming

Any note anchored to a specific date or run - a session note, a dream note, an action sweep - is named `YYYY-MM-DD-short-slug.md` inside its owning folder. ISO date first so the folder sorts chronologically for free; kebab-case; no spaces. The slug names the *substance*, not the medium or the mechanism (`2026-08-24-vault-okf-migration.md`, never `2026-08-24-claude-session.md`). If a file already exists for that date and the new content is a genuinely separate occasion (not a continuation of the same run), add a distinguishing slug rather than overwriting; a same-day re-run of the same mechanical process (an action sweep, for instance) does overwrite rather than duplicate - each skill's own contract says which case applies.

## `.utility/` is tooling space, not content

`kb.paths.utility` (or a top-level `.utility/` folder) holds machinery the kb needs to function but that is never itself a note: session transcript archives, pending-processing markers, skill-health logs, dream recycle bins. It is **never indexed** (no `index.md` entry, ever) and **never curated** by any pass that walks the kb's content (conformance checks, link passes, the type registry, staleness flags) - a curation pass reads a count from it at most (e.g. "N sessions await processing") and never treats its contents as notes to fix, link, or supersede. A skill writing to `.utility/` does so directly, with no maintenance-contract obligations beyond whatever that specific mechanism requires (e.g. moving a processed transcript from `pending/` to `archive/`).
