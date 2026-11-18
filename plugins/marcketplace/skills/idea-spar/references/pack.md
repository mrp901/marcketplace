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
   verdict, the same claim at the same confidence, in the voice below.
4. **Your claims** - every claim from the known packet with its verdict and source, from
   whichever lens reached it; a claim no lens reached reads "not checked". Never omitted
   while a claim exists.
5. **Challenge**, **Reality**, **Market** - each lens's findings in the output contract's three
   parts (claim · source · **so what**), worded per "Voice" below at the same confidence, without the
   lens's "Your claims" line (section 4 carries it), minus anything the user rejected in the session.
   A lens that didn't run is omitted, not stubbed.
6. **Sketch** - the HTML rendering from `sketch.md`, if a sketch was made.
7. **Decisions for you** - the open forks, each a question with 2 to 4 options.
8. **Sources** - one line per source actually used, linked. Nothing listed that wasn't read.

No introduction, no methodology, no "about this document", no summary of the ticket. The
known packet is never restated (section 4's claims aside); the reader either has it or has the ticket link in the
title.

## Voice

The pack goes out as the user's own, so it is written in their voice: load the
`exec_update` register (or the one the user names) and the avoid-list per
`../../../shared/voice.md`. The test is ownership: the user reads it and understands it as
if they wrote it.

- Each line sits at the confidence the evidence supports. Where it leaves room, hedge the
  way the register's hedging trait says this user does; where it doesn't, state it plainly.
  A hedge that marks real uncertainty is theirs; the avoid-list's filler hedges stay out.
- Each claim is one they could defend in the room without re-opening a source. Reasoning
  they would have to reconstruct if asked is cut; the source link carries it.
- Anyone else's words are visibly theirs: a blockquote with name and date, never folded
  into the user's sentences.

No calibrated register or no `exec-update` note: write plainly against the avoid-list and
prefix the pack `voice: uncalibrated`. The two voice reads don't count against `kb_reads`.

```markdown
Before: In short, drift is computed every 15 minutes so the alert needs no new
analytics, and Tomasz says the routing team owns the job, which means ...

After:  - Drift is computed every 15 minutes · route_variance.py:40-88 ·
          **so what:** the alert needs no new analytics.
        > "The routing team owns that job." - Tomasz, 12 Sep
```

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

**Your claims**
- "Drift only lands in the nightly batch" - not supported: the job runs every 15 minutes.
- "Dispatchers want a push" - not checked.

## Decisions for you
- Channel first: email digest (cheap, exists) / in-app (new service) / both
- Threshold: fixed for all routes / per customer
```
