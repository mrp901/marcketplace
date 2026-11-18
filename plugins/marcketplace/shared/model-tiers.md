# Model tiers

Three tiers, set as profile keys under `budgets.models`:

```yaml
budgets:
  models: {worker: sonnet, search: haiku, critic: opus}
```

- **`worker`** - the default model every skill runs on: handlers, drafting, the bulk of
  every skill's own reasoning.
- **`search`** - a cheap, fast model for narrow, high-volume extraction dispatched as
  subagents, where the result is a short structured answer and raw source content should
  never land in the caller's own context. It extracts and never judges: see "Extraction
  decides nothing" below.
- **`critic`** - a stronger model reserved for judgement calls that are worth paying for:
  an independent audit of another step's output, or a synthesis step that has to hold a
  lot of context at once and reason carefully about trade-offs.

## Which steps use which tier

| Skill | Step | Tier | Why |
|---|---|---|---|
| jira-story | blind pass, and idea mode's draft audit (a fresh subagent checks a story or ticket draft before it goes to the user) | `critic` | the point of the audit is a sharper, more careful reader than the one that wrote the draft; the source skill deliberately does not let this step inherit the default model |
| idea-spar | every web and codebase search behind the reality and market lenses and the prior-statement sweep, dispatched as a subagent with one narrow job | `search` | code and web lookups are near-free structured lookups; tiering by task (not by step) keeps raw file and page content out of the primary model's context |
| skill-eval | Step 2 synthesis (revises a `SKILL.md` from captured feedback) | `critic` | this is the hard reasoning step - holding the whole original skill, the specific feedback and the discipline not to over-edit all at once |
| action-list | `build` and `prep` extraction, one subagent per source | `search` | volume reading; every candidate comes back with its evidence and the ranking happens on `worker` |
| action-list | cold review of the built list | `critic` | an independent reader that did not rank or draft the list |
| action-sweep | every thread, transcript and canvas body read during gather, and the source-thread read behind a `targeted` draft | `search` | volume reading; which finds are kept, and how each routes, is decided on `worker` after the extractor returns |
| proactive-router | the thread read behind an added line that points at a thread | `search` | the read only; classification and dispatch stay on `worker` |

Every other skill and step runs on `worker` by default, including all of reply-draft,
session-log's capture mode, action-sweep's drafting, briefing, proactive-router's classification and
dispatch, session-log, and kb-dream's curation passes. Voice-matching handlers (reply-
draft, session-log's capture mode, jira-story's own drafting step) stay on `worker` - only the audit/critic
step above escalates, never the drafting itself.

## Extraction decides nothing

A `search`-tier subagent pulls items out of a source into a fixed structure and returns
**every candidate**, each with its evidence (a short quote and the permalink, ticket key or
meeting it came from). It never decides whether a candidate is relevant, real, noise, "only
in passing", a genuine ask or worth keeping. Every keep-or-drop filter in a skill's
instructions is applied by the calling skill on `worker` (or `critic`), after the
extractor returns.

A step that needs a judgement call - relevance, "is this an ask", "is this a commitment",
what to drop - is not extraction. Give it to `worker` or `critic`, or have the extractor
return everything and filter afterwards. Do not escalate a tier just because a job is big:
a large extraction is still `search`.

Why: a cheap model asked to filter as it reads drops real items silently, and nothing
downstream can recover what it never returned. A real tracker tag addressed to the user
was lost this way once, behind a "is this really a question for the user?" filter on the
cheap tier. Over-returning costs a few lines of structured output; under-returning costs a
missed action.

When writing a brief for a `search`-tier subagent, phrase it as "return every X, with its
quote and link", never "return only the X that matter". Write any filter into the calling
step instead.

## Escalating for one step and returning

A skill that needs a higher tier for a single step spawns a **fresh subagent** explicitly
set to that tier for that step only - it does not switch its own running model. The
escalation is scoped to the one call: the subagent gets only what that step needs (per
jira-story's audit, a genuinely fresh context with no inherited drafting reasoning, so the
critic does not anchor on the primary model's own thinking), returns its narrow result, and the
calling skill resumes on `worker` for everything after.

## Stating an unavailable tier

If the tier a step asks for is not available in the running environment, the skill falls
back to the strongest model it can get for that call **and says so plainly in its output**
- never silently downgrades. This is the same pattern the source skills already used for
the opus audit and synthesis steps: fall back, then say which model actually ran the step,
rather than letting a silent substitution pass as if the requested tier had run.
