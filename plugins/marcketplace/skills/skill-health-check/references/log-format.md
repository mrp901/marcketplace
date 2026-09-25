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

## Board line, red only

Per `surface-protocol.md`'s line grammar, tag form `shc:<YYMMDD>-<n>`, category
`skill-eval`, reading as the action a tick causes:

```
- [ ] (shc:260910-1) 🔴 idea-deep-dive scored red: two notes superseded by your own corrections this fortnight. Run skill-eval on it? · .utility/skill-health/idea-deep-dive.md
```

The one or two things that drove the tag, not the full evidence list; the log file is the
detail, the line is the pointer. A tick means "yes, queue it": the hub writes
`↳ router: queued for your next skill-eval run` and nothing runs until the user runs
`skill-eval`, which lists queued lines as candidates.

## Amber and green

No board line. Every score, whatever its colour, is written to
`state.runs.skill-health-check.scores.<skill>`:

```yaml
scores:
  idea-deep-dive: {tag: red, why: "two notes superseded by your corrections", ref: ".utility/skill-health/idea-deep-dive.md", checked_at: 2026-09-10T03:00:00+10:00}
  reply-draft: {tag: amber, why: "2 of 3 drafts edited before sending", ref: ".utility/skill-health/reply-draft.md", checked_at: 2026-09-10T03:00:00+10:00}
  kb-note: {tag: green, why: "3 notes verified as written", ref: ".utility/skill-health/kb-note.md", checked_at: 2026-09-10T03:00:00+10:00}
```

The briefing's Runs block reports amber and green from here in one `health:` line; red is
on the board and not repeated in the message.
