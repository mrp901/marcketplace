# Inspecting the tracker for house style

Step 3 of `SKILL.md`. The point is to follow the conventions the team already uses, not a
template baked into this skill. Do it before drafting (New mode) or before rewriting
(Refine mode; the target is already fetched in Step 2, so its project and type are known),
and let what you find override `profile.tracker.*` defaults.

## Procedure

1. `tracker: search issues (JQL)` in `profile.tracker.project_key` (or the target ticket's own
   project), the same issue type as the target, ordered by most recently updated, small
   limit. Prefer stories that are resolved or in progress over untouched ones; those have
   survived contact with a team. In Refine mode, exclude the target itself (already read in
   Step 2).
2. `tracker: get issue` on up to three of them. Read description, labels, parent or epic
   link, linked issues and any custom fields that are populated. Read comments only if the
   description looks thin.
3. If the project has no recent stories of that type, widen once to the same type across
   the instance (a second search, the most this step makes), then stop. Do not crawl.

## What to infer

| Aspect | Look for |
|---|---|
| Summary style | Length, prefix or product tag, verb-first or noun-first, a "As a..." form or not |
| Story line | Whether a User Story sentence exists and where it sits (top of description, own field) |
| AC format | Heading name, bullets vs numbered vs Given/When/Then, one assertion per bullet or not |
| Labels | Which labels recur, and what each appears to mean |
| Field usage | Which optional fields are routinely populated (component, fix version, priority, custom fields) |
| Hierarchy | Whether stories hang off an epic, how epics are named, whether children link to a parent or to a separate planning ticket |
| Linking | Which link types are used for dependencies and duplicates |

Only record a convention seen in at least two of the sampled issues; one occurrence is an
accident, not a convention. Where the sample disagrees with itself, say so and ask.

## If nothing usable is found

No tracker connected, an empty project, or samples too inconsistent to read a convention
from: ask once, in the batched question round, for the three things that matter most (the
AC format, whether a story line is used, and the epic or parent rule). Do not invent
defaults. If the user answers "no convention", write plain bullets under an "Acceptance
criteria" heading and say you did.

## Reporting

Open the draft with one line stating what was inferred and from how many issues ("followed
the style of three recent FLT stories: verb-first summaries, bulleted ACs, epic parent
required"). The user can then correct the inference rather than discover it later.

## Relationship to idea-ticket

`../../idea-ticket/references/ticket-format.md` defines a fixed format for ideas-board
tickets (Context, The ask, Options). That is a different ticket shape for a different
board and is not duplicated here. Only its "Cut the AI tells" list is shared, by reference.
