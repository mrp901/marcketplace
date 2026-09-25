---
type: llm
focus: trace
weight: 1
---
The user added a third, ticked line under the FIG-204 drift-threshold question that is
not in `state.items` ("Per customer, but default every new customer to 30 minutes..."). A
good run:

- Recognises it as a user-added line inside the FIG-204 idea block and reads it as an
  answer to that block's open question, so it is classified `idea-decision` in group
  `FIG-204/d2` with `idea_key: FIG-204`, and given a `pr:` tag in the same write.
- Because it is the only ticked line in the group, treats it as the chosen option and
  prepares a dispatch to `idea-scout` in `decide` mode carrying the user's own text as
  `text_as_ticked`. A sub-line saying a tool category could not be resolved is an
  acceptable outcome of the dispatch step.
- Does NOT treat the line as a swept chat message (there is no permalink; it needs none),
  does not write `pick one`, and does not act on `d2a` or `d2b`.

Fail this if the run ignores the added line, discards it for lacking a permalink or a tag,
classifies it as something other than a decision on FIG-204, or writes `pick one`.
