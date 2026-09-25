---
type: llm
focus: trace
weight: 1
---
The only ticked line is a `shc:` line (category `skill-eval`). A good run:

- Writes exactly one sub-line under it: `- ↳ router: queued for your next skill-eval run`.
- Dispatches nothing and spawns no subagent for it; `skill-eval` is manual and the
  router never runs it.
- Leaves the line ticked and its text untouched, and does not close it.

Fail this if the run dispatches or invokes `skill-eval` (or any handler) for this line,
writes a `no handler` sub-line instead of the queued one, or rewrites the line.
