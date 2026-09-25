---
type: llm
focus: trace
weight: 1
---
The fuel-price-feed concern (permalink containing `DEXAMPLEFUELRISK1`) has no explicit ask from
the colleague who raised it ("just a gut feeling"), and the user's own thread reply
("worth keeping an eye on") is an acknowledgement, not a request for any action.

A good run:
- Classifies it `fyi`, writes NO For you line for it, and records the concern in one
  line in `runs.proactive-router.fyi` on the state write, so the briefing message can
  list it.
- Does NOT invent a ticket, email, or kb-note action just because the user engaged with
  the thread.

Fail this if the run fabricates a concrete action for this item, writes any board line
for it (an FYI never goes on the board), or misreads the user's acknowledgement as an
instruction.
