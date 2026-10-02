# The pack

One shareable page the user can open in a meeting or send to a stakeholder. It carries only
what survived the session (or, in the Next watch, what the three lenses produced
unattended). It is a brief for a conversation, not a report: someone should be able to
read it in two minutes standing up.

## Structure, in order

1. **Title** - `<idea key> · <idea title>` (or the user's own name for a prose idea).
2. **The question** - one sentence: what decision this pack is for ("Should FIG-204 ship
   as a per-drift alert or a digest?"). In a session, take it from the user; unattended,
   write it from the challenge lens's verdict.
3. **Where it stands** - three lines, one per lens that ran: the lens name and its
   verdict sentence, verbatim.
4. **Challenge**, **Reality**, **Market** - each lens's findings exactly as the output
   contract in `SKILL.md` shapes them, minus anything the user rejected in the session.
   A lens that didn't run is omitted, not stubbed.
5. **Sketch** - the HTML rendering from `sketch.md`, if a sketch was made.
6. **Decisions for you** - the open forks, each a question with 2 to 4 options.
7. **Sources** - one line per source actually used, linked. Nothing listed that wasn't read.

No introduction, no methodology, no "about this document", no summary of the ticket. The
known packet is never restated; the reader either has it or has the ticket link in the
title.

## Publishing

`page: publish` with a self-contained HTML page (inline styles, the sketch kit's `<style>`
block for the sketch, light and dark themes, readable at phone width). Republish to the
same page when the user asks for a revision in the same session, so the link they already
shared stays good. Record the link in `state.ideas.<key>.pack_ref` when the idea has a key.

**`page` unresolved:** write the same content as Markdown to
`<profile.kb.paths.research>/<key>-pack.md` (frontmatter per
`../../../shared/kb-conventions.md`, `status: draft`, no `verified`, `generated.by:
idea-spar`), and return that path as the link, saying it is a kb file because no page
publisher is connected.

## Worked example (fictional, abbreviated)

```markdown
# FIG-204 · Load-plan variance alerts

**The question:** per-drift alert or a digest, and which channel first?

**Where it stands**
- Challenge - Build it, but as a digest first: a per-drift alert will be muted inside a week.
- Reality - Smaller than it looks: drift is already calculated, just never surfaced.
- Market - Table stakes in mid-market freight visibility; build it plainly.

## Decisions for you
- Channel first: email digest (cheap, exists) / in-app (new service) / both
- Threshold: fixed for all routes / per customer
```
