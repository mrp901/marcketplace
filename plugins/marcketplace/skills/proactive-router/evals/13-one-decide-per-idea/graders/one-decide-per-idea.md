---
type: llm
focus: trace
weight: 1
---
Two decision groups on the FIG-204 idea each have one ticked option: `FIG-204/d1b` ("Email
only") and `FIG-204/d2b` ("Notify only above a set threshold"). Both are single picks, so
neither group is blocked. A good run:

- Prepares exactly one dispatch to `idea-spar` in `decide` mode, for `FIG-204/d1b` (the
  tiebreak: neither tick has an earlier `ticked_at`, so board order decides), with
  `item.idea_key: FIG-204`.
- Does not dispatch `FIG-204/d2b` this run, writes no sub-line under it, and leaves its
  tick as it is, so it goes next run.
- Counts the held tick as queued in its run note or report.
- Does NOT write `blocked · pick one` anywhere.

Fail this if the run dispatches both options, dispatches only `d2b`, unticks or rewrites
either option, writes a sub-line under `d2b`, or writes `pick one`.
