# Propose topic-note edits; don't make them

When a session produced something that belongs in a standing note - a new fact for a
service map, a decision that warrants a record under `kb.paths.decisions`, a name to add
to `kb.people_file` - write it into the session note and list it as a proposal. Don't edit
those notes as part of this skill.

The reason is asymmetry of cost. Getting the session note wrong costs one file that's easy
to fix. Silently rewriting a standing note can destroy a carefully-worded position or a
supersession banner, and the damage isn't visible until much later. Present instead:

```markdown
## Proposed follow-ups

- [ ] `<kb.paths.decisions>/2026-09-22-<slug>.md` - new record for <decision>. Not written yet.
- [ ] `<kb.people_file>` - add <person>, <role>.
```

Then offer to make them. If the user says go ahead, do it in that turn and note it - the
restraint is about not doing it unasked, not about refusing.

## If the go-ahead comes later in the same live session

Not a separate future conversation - update the existing session note in place rather than
writing a second dated note for the same day: tick the relevant checkbox (or mark one "not
needed" with why), add anything new to Facts and Changes, and bump the note's own
`generated` to now. Apply the same-turn correction rule the same way if the
newly-approved action makes an earlier log line stale.

## Decision Record vocabulary

When a proposal is a `Decisions/`-shaped record, use the vocabulary the kb's existing
decision records already use rather than inventing keys: `decision_status` for the
decision's own workflow state (distinct from the OKF `status` field), `jira` or the
equivalent tracker key, `owner` in `human:<user>` actor form, `deciders` as plain names,
`date_raised` as `YYYY-MM-DD`. Decision Records also number their `##` sections
(`## 1. Decision required`, `## 2. Why this came up`, ...), which no other type does -
check the live registry and an existing example before inventing a shape.
