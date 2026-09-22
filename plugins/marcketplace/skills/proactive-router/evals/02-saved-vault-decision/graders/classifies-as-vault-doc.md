---
type: llm
focus: trace
weight: 1
---
The metric-formatting decision (permalink containing `DEXAMPLEFUELFMT1`) was surfaced only via
`is:saved` - the user never reacted to it with an emoji. A good run still logs a surface
line for it:

- Uses the 📖 emoji (kb documentation).
- Describes the actual decision: fuel-cost-per-mile should display to 2 decimal places
  rather than rounding to whole cents, because rounding hid real variance between depots.

Fail this if the item is missing entirely (e.g. discarded because it wasn't a `hasmy:`
emoji hit), uses the wrong emoji, or the described content is vague/wrong.
