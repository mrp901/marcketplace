---
type: llm
focus: trace
weight: 1
---
The Ideas block for FIG-204 has one decision group with three options, and exactly one
of them (`FIG-204/d1b`, "Email only") is ticked. A good run:

- Treats `d1b` as the chosen option and the other two as its unticked siblings.
- Prepares a dispatch to `idea-scout` in `decide` mode for that one line, with
  `item.idea_key: FIG-204`, `item.group: FIG-204/d1` and `text_as_ticked` carrying the
  "Email only" text. Whether the subagent completes or the hub instead writes a sub-line
  saying a tool category could not be resolved, both are acceptable outcomes of the
  dispatch step.
- Does NOT write a `blocked · pick one` sub-line, and does not act on `d1a` or `d1c`.

Fail this if the run writes `pick one`, dispatches or acts on more than one option,
rewrites any option's wording, or ignores the tick entirely.
