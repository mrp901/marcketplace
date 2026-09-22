# Log entry format

One file per skill, `kb.paths.utility/skill-health/<skill-slug>.md`, newest entry prepended
to the top. No frontmatter - see `kb-conventions.md`'s `.utility/` rule.

```markdown
## 2026-09-10 - amber

Evidence window: 2026-08-24 to 2026-09-10 (4 kb notes, 1 tracker ticket)

- FIG-164 deep-dive note: no correction found, links resolve, cited by the FIG-164 wireframe.
- FIG-165 deep-dive note: superseded by the user's own addition on 2026-09-08 correcting the
  amortisation figure - the note used the old 8.5% instead of the July 13.4% update.
- Ticket FIG-171 (idea-ticket): edited by the user 20 minutes after creation, priority changed.
- Evidence sources available: kb frontmatter/links (full), tracker changelog (full), voice
  ledger (none - this skill drafts no prose).
```

Fictionalised against `profiles/example.md` (Northwind Logistics / Freight Ops); the tracker
keys above are the ideas-board project's, not a real value from any live install.

`../scripts/check_log_entry.py` validates a proposed entry against this shape before it's
written: a `## YYYY-MM-DD - <tag>` heading, an `Evidence window:` line, 2 to 4 evidence
bullets, and one `Evidence sources available:` line. It exits non-zero on a shape mismatch
rather than letting a malformed entry land in the log.

## Surface line, amber and red only

Per `surface-protocol.md`'s line grammar, tag form `shc:<YYMMDD>-<n>`:

```
- [ ] (shc:260910-1) :large_yellow_circle: `idea-deep-dive` - superseded once, one stale tracker edit - `.utility/skill-health/idea-deep-dive.md`
```

`:large_yellow_circle:` for amber, `:red_circle:` for red. The one or two things that drove
the tag, not the full evidence list - the log file is the detail, the surface line is the
pointer. Where the diagnosis is obvious, the line may end with "- run `skill-eval` next" in
place of the file pointer's lead-in text, never both crowding a 200-character-equivalent
line.
