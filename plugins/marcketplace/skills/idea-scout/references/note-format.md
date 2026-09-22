# Note format

## Frontmatter

Follows `../../../shared/kb-conventions.md`'s frontmatter contract - all six of
`profile.kb.frontmatter_required`, `status: draft`, no `verified` (a machine-authored note
has not been human-reviewed yet). File path `<profile.kb.paths.research>/<idea-key>-<short-
slug>.md`, kebab-case, e.g. `ig-120-ux-improvements.md`. Links follow
`profile.kb.link_style`; sources footnoted.

```yaml
---
type: Analysis
title: <Idea title> - First-Pass Discovery (<idea key>)
description: One-sentence summary of where this idea landed.
tags: [<product-area tag>, discovery, idea-board]
status: draft
stale_after: <~90 days out>
generated: { by: idea-scout, at: <ISO 8601, org.timezone offset> }
sources:
  - id: idea
    title: <idea key> <idea title>
    url: <tracker.site_url>/browse/<idea key>
---
```

## Body structure

```markdown
# <Idea title> - First-Pass Discovery (<idea key>)

Auto-generated first pass by idea-scout - a junior's take to react to, not a verdict.
Qualified by: {product tag | area field | assigned to <user.name>}. Linked idea: <idea key>.

## Where I landed
## The four product risks
## Decisions for you to make
## Research leads
## Hills to climb
## Open questions
## Sources & context used
```

- **Where I landed** - 2 to 4 sentences. A position, not a hedge. State what this skill
  thinks, plainly, before laying out the evidence behind it.
- **The four product risks** - one short paragraph each for Value, Usability, Feasibility,
  Viability: where the idea stands against that risk, and what is still unknown. This
  skill does not define what the four risks mean - that framing is assumed knowledge, not
  something to explain from scratch in every note.
- **Decisions for you to make** - real forks with options, never "consider X". Each
  decision names the actual choice on the table and the concrete options, written so the
  reader can see the trade-off without opening anything else. This section is the reason
  the note exists; a note whose decisions are all hedges has wasted the read.
- **Research leads** - named competitors, sources, docs, people worth chasing next.
  Cross-check any person named against `profile.kb.people_file` before writing them
  in.
- **Hills to climb** - the hard parts: dependencies, data gaps, upstream constraints.
- **Open questions** - owner and whether it's currently blocking.
- **Sources & context used** - what was actually read and searched this run, named plainly.

## Worked example (fictional, against `profiles/example.md`)

```markdown
---
type: Analysis
title: Load-plan variance alerts - First-Pass Discovery (FIG-204)
description: Freight Ops customers want a heads-up when a load plan drifts from the booked route, not a report after the fact.
tags: [freight, discovery, idea-board]
status: draft
stale_after: 2026-12-21
generated: { by: idea-scout, at: 2026-09-22T09:14:00+10:00 }
sources:
  - id: idea
    title: FIG-204 Load-plan variance alerts
    url: https://northwindlogistics.atlassian.net/browse/FIG-204
---

# Load-plan variance alerts - First-Pass Discovery (FIG-204)

Auto-generated first pass by idea-scout - a junior's take to react to, not a verdict.
Qualified by: area field (Freight Ops). Linked idea: FIG-204.

## Where I landed

This is worth a real look. Dispatchers already re-check plans manually every few hours;
an alert on drift replaces a manual poll with a push, which is the kind of change that
gets used. The open question isn't whether to build it, it's how noisy the first version
is allowed to be before dispatchers mute it.

## The four product risks

**Value** - clear: three support tickets this quarter cite exactly this gap.
**Usability** - unresolved: no existing pattern in Freight Ops for a push alert; needs a
decision on channel (in-app, email, both).
**Feasibility** - likely fine: booked-route data already exists; drift calculation is new
but bounded.
**Viability** - unknown: alerting infrastructure isn't built yet; this may be the first
consumer of it, which changes the cost estimate.

## Decisions for you to make

- **Alert channel.** In-app only (cheap, but dispatchers report living in email); email
  only (reaches them, but no history in-product); both (right answer probably, higher
  build cost now).
- **Drift threshold.** Fixed distance/time drift for every route; or a threshold set per
  customer. Fixed ships faster; per-customer matches how support already talks about it.

## Research leads

- Project44 ships a similar variance alert as part of its visibility product - worth a
  screenshot pass before scoping the UI.
- FourKites markets "predictive ETA" rather than plan-variance specifically - different
  framing, same underlying signal.

## Hills to climb

- No existing alerting infrastructure in Freight Ops; this idea may be the thing that
  forces that decision, not just consume an existing one.

## Open questions

- Owner: Tomasz. Blocking: yes - needs to confirm whether alerting infra is already
  planned elsewhere before this scopes as net-new work.

## Sources & context used

- FIG-204 description and comments.
- `Product/FreightOps/index.md`, `Product/FreightOps/Research/index.md`.
- Web: Project44 visibility product page; FourKites predictive ETA page.
```
