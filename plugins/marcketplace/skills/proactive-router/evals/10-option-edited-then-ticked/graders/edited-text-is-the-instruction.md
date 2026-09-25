---
type: llm
focus: trace
weight: 1
---
Option `FIG-204/d1b` was edited by the user (from "Email only: reaches them, no history
in-product" to "Email only, but batch the alerts hourly so dispatchers get one digest
rather than a stream") and then ticked. A good run:

- Classifies the line as edited-and-ticked (the canvas text differs from the stored
  `text`), and treats the edit as a variation of that option, so the dispatch payload
  carries the edited text as `text_as_ticked` and the stored text as `original_text`.
- Prepares a dispatch to `idea-scout` in `decide` mode for that one line; a sub-line
  saying a tool category could not be resolved is an acceptable outcome of the dispatch
  step.
- Increments `tally.idea-decision.edited` (or records the edit in the tally) on the
  state write.
- Does NOT rewrite the option back to its original wording, and does NOT write `pick one`.

Fail this if the run restores the original wording, dispatches with the original text
instead of the edit, treats the edit as a brand-new line, or acts on `d1a` or `d1c`.
