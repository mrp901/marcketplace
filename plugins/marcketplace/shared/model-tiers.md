# Model tiers

Three tiers, set as profile keys under `budgets.models`:

```yaml
budgets:
  models: {worker: sonnet, search: haiku, critic: opus}
```

- **`worker`** - the default model every skill runs on: handlers, drafting, the bulk of
  every skill's own reasoning.
- **`search`** - a cheap, fast model for narrow, high-volume lookups dispatched as
  subagents, where the result is a short structured answer and raw source content should
  never land in the caller's own context.
- **`critic`** - a stronger model reserved for judgement calls that are worth paying for:
  an independent audit of another step's output, or a synthesis step that has to hold a
  lot of context at once and reason carefully about trade-offs.

## Which steps use which tier

| Skill | Step | Tier | Why |
|---|---|---|---|
| idea-ticket | draft audit (a fresh subagent checks a ticket draft before it goes to the user) | `critic` | the point of the audit is a sharper, more careful reader than the one that wrote the draft; the source skill deliberately does not let this step inherit the default model |
| idea-wireframe | critic round (ranks the wireframe against recent prior wireframes) | `critic` | judgement is the one place worth the stronger model; the critic only ever sees a screenshot and a one-line problem statement, so the call stays cheap even on the stronger tier |
| idea-deep-dive | every circle 1/2/3/4 search, dispatched as a subagent with one narrow job | `search` | vault, chat and web lookups are near-free structured lookups; tiering by task (not by step) keeps raw thread/page/file content out of the primary model's context |
| skill-eval | Step 2 synthesis (revises a `SKILL.md` from captured feedback) | `critic` | this is the hard reasoning step - holding the whole original skill, the specific feedback and the discipline not to over-edit all at once |

Every other skill and step runs on `worker` by default, including all of reply-draft,
kb-note, action-sweep's drafting, briefing, proactive-router's classification and
dispatch, session-log, and kb-dream's curation passes. Voice-matching handlers (reply-
draft, kb-note, idea-ticket's own drafting step) stay on `worker` - only the audit/critic
step above escalates, never the drafting itself.

## Escalating for one step and returning

A skill that needs a higher tier for a single step spawns a **fresh subagent** explicitly
set to that tier for that step only - it does not switch its own running model. The
escalation is scoped to the one call: the subagent gets only what that step needs (per
idea-wireframe, a genuinely fresh context with no inherited build reasoning, so the critic
does not anchor on the primary model's own thinking), returns its narrow result, and the
calling skill resumes on `worker` for everything after.

## Stating an unavailable tier

If the tier a step asks for is not available in the running environment, the skill falls
back to the strongest model it can get for that call **and says so plainly in its output**
- never silently downgrades. This is the same pattern the source skills already used for
the opus audit and synthesis steps: fall back, then say which model actually ran the step,
rather than letting a silent substitution pass as if the requested tier had run.
