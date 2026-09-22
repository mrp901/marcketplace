---
type: llm
focus: trace
weight: 1
---
The trip-cost dashboard bug thread (permalink containing `CEXAMPLEBUGTHR1`) has a bare bug
report from a colleague ("tile spins forever for depots with >500 trips") and a follow-up
reply from the user themself specifying the actual fix (cap the query at 500 trips per
page server-side, add a "load more" control).

A good surface line:
- Uses the 🎫 emoji.
- States the fix the user's own reply specified (pagination / load-more), not just a
  generic restatement of the bug symptom.

Fail this if the line only restates the bug ("dashboard tile hangs") without naming the
specified fix, or if the item is missing/misclassified.
