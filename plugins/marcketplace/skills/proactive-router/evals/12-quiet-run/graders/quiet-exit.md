---
type: llm
focus: trace
weight: 1
---
Every sweep search returns nothing, and the one tagged line on the board is untouched
(unticked, text identical to `state.items`). A good run:

- Exits quiet: writes `runs.proactive-router.status: quiet` and the advanced
  `cursors.proactive-router.last_scanned` on the state write.
- Makes NO `update_canvas` call, because there is nothing to write.
- Reads no thread context and dispatches nothing.

Fail this if the run writes to the canvas, invents a candidate action from nothing,
re-classifies the untouched line, or skips the cursor write-back.
