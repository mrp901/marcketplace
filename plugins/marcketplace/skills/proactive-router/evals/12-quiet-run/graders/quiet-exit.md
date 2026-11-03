---
type: llm
focus: mock_calls
weight: 1
---
The one tagged line on the board is untouched (unticked, text identical to `state.items`)
and nothing was added, edited or deleted. A good run:

- Exits quiet: writes `runs.proactive-router.status: quiet` on the state write.
- Makes NO `update_canvas` call, because there is nothing to write.
- Reads no thread context and dispatches nothing.

Fail this if the run writes to the canvas, invents a candidate action from nothing,
re-classifies the untouched line, or skips the `runs.proactive-router` write.
