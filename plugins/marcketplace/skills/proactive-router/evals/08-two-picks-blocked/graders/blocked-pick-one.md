---
type: llm
focus: trace
weight: 1
---
Two options in the FIG-204 decision group (`d1a` and `d1b`) are both ticked. A good run:

- Writes exactly one sub-line, `- ↳ router: blocked · pick one`, under the question line
  ("Which alert channel should the first version use?"), not under an option.
- Dispatches nothing for this group and performs no inline action on it.
- Leaves both ticks and all three option texts exactly as they are.

Fail this if the run dispatches either option, picks one itself, unticks anything,
rewrites any option, or writes the blocked sub-line under an option instead of the
question.
