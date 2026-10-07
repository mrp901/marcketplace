# idea-spar - design rationale (for editors; not loaded at runtime)

## 2026-10-02 replaces idea-scout, idea-deep-dive and idea-wireframe

The three skills ran as a pipeline on their own schedule: scout picked the next
un-investigated idea and wrote a first-pass note, deep-dive chased its open questions
across four circles, wireframe drew an annotated mockup of an investigated idea. The user
reported none of it was useful and that they never sought it out. An interview found why:

- **Wrong content, not wrong idea.** Selection wasn't the problem. The notes restated what
  the user already knew (the ticket, the kb, their own conversations) and dressed it up as
  findings. The user *is* the context; restating it costs a read and adds nothing.
- **Wrong place.** Vault notes and canvas lines are not where the user goes when thinking an
  idea through. They reach for help mid-brainstorm and when prepping a conversation, and
  want it inline in the session or as a shareable link.
- **What did help:** engineering reality (what the code does, what makes it cheap or
  expensive), a contrarian challenge, and market data with its implication for positioning
  ("is it relevant, how, does it change the outcome"), not a competitor list.
- **Wireframes missed the product and read as AI output:** too much copy, components that
  don't behave like real UI. Wanted: rough sketches of 2-3 alternative options, wireframe
  fidelity, built from mock design-system components.
- **Proactive only when an idea moves into Next.** Nothing else unprompted.

Design choices that follow:

- **One skill, lens files.** Chosen over a skill per lens: the user uses the lenses together
  in one sitting, the packet-drop rule has to see what every lens already said, and "pack it"
  and the Next watch use all three. Lens files keep each one editable on its own; split a
  lens out later if it turns out to be the only one used.
- **The known packet** is the mechanism against restating: context goes in, is never
  summarised back, and any candidate finding it already contains is dropped. Phrased as a
  conditional plus a positive output contract (verdict, sourced findings with a "so what",
  checked-no-bearing, would-change-my-mind), not a "don't restate" prohibition, because
  prohibitions negotiate badly on shaping problems.
- **Sketch kit.** A fixed component list with ASCII and HTML forms, labels of three words or
  fewer, body copy as grey bars, one trade-off line per option. Addresses the copy-heavy,
  un-UI-like output directly.
- **Pack via `page: publish`**, new tool category, with a kb-file fallback. Shareable link
  replaces the vault as the primary home.

Carried over from the retired skills, because each rule exists for a reason:

- The qualifying gate and its "no flag-and-proceed" stance (idea-scout, 29 Aug 2026: two
  off-domain picks; a flagged off-domain note still costs a read). Applied only to the Next
  watch. Roadmap remains the trigger, never a qualifier.
- Captures before drawing (idea-wireframe: a drawn nav rail that didn't exist and a shipped
  feature marked out of scope, contradicted by captures one folder away).
- The subtraction pass (models add and rarely remove).
- The `decide` mode for `idea-decision` ticks, now writing a per-idea decision log that the
  next session's known packet reads.
- Roadmap watch mechanics (cursor, `roadmap_last_seen`, first run seeds and posts nothing),
  retargeted from "left a parked slot" to "moved into Next".

Dropped: board-order selection, the investigated/wireframed labels (no tracker write at
all now), deep-dive's four-circle loop and Run state, the taste log and `react` mode, the
`idea-refresh` line and `inline:requeue`, the critic round, first-pass research notes.

## 2026-10-07 state shards

The state page passed 49 KB and a full-body-replace write became unsafe to re-type, so `cursors`, `ideas` and `runs` move to its own shard. See `shared/state-schema.md`, "Shards".
