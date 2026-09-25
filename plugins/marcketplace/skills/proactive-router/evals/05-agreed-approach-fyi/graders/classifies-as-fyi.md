---
type: llm
focus: trace
weight: 1
---
The batch-vs-stream recalculation thread (permalink containing `CEXAMPLEAPPRCH1`) is a
multi-party engineering debate that ended in clear agreement - no open question addressed
to the user, and the user only reacted, they didn't reply with any ask.

A good run:
- Classifies it `fyi`, writes NO For you line for it, and records one line naming what
  was agreed (batch overnight) in `runs.proactive-router.fyi` on the state write, so the
  briefing message can list it.
- Does NOT invent a ticket, email, or kb-note action for this item.

Fail this if the run fabricates a concrete action (a ticket, email draft, or kb note) for
this item, or writes any board line for it: an FYI never goes on the board.
