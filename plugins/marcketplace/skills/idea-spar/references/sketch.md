# Sketch

Two or three rough layout options for the same job, side by side, so the user can point at
one and argue. Wireframe fidelity, built from a fixed set of mock components that read the
way real UI reads. The sketch exists to compare options, not to specify one.

## What a sketch is

- **2 to `sketch_options` options**, labelled A, B, C, each the same screen or short flow
  solving the same job a different way (inline vs drawer vs new tab; one table vs grouped
  cards; filter-first vs search-first). Never one option; never three that differ only in
  styling.
- **One line under each option: the trade-off**, in the form `+ <what it buys> / − <what
  it costs>`. That line is the only prose an option carries.
- **Up to three numbered notes per option, outside the frame**, each one line, each tied to
  a finding from a lens or to an open fork. A note that only describes what the drawing
  already shows is cut.

## Components, not inventions

Build every option only from these parts. If the idea needs something not on the list,
use the nearest part and say so in a note. Each part has a fixed look in
`sketch-kit.html` and a fixed ASCII form for sessions.

| Part | Use for | ASCII form |
|---|---|---|
| shell | The product's real frame: top bar, nav rail, breadcrumb - only what the real product has | `┌─ Cloud › Spend ───┐` |
| card | A summary metric or a grouped block | `┌ Title ──┐ $41k ▲6%` |
| table | Rows of records; 3-5 columns, 2-3 rows | `Account  Spend  Δ` |
| filter | Filter bar or dropdown | `[Account ▾] [Month ▾]` |
| tabs | Peer views of one thing | `Overview │ Accounts │ Tags` |
| drawer | Detail without leaving the page | `│▒▒ detail ▒▒│` on the right |
| modal | A blocking decision | double-ruled box |
| button | One primary action per view, at most one secondary | `[Apply]` `(Cancel)` |
| chip | Status, tag, count | `(3 new)` |
| chart | Any chart, as a placeholder | `▁▂▃▅▆▇` |
| empty | No data, loading, error | `- nothing yet -` |
| text | Body copy, always as grey bars | `▭▭▭▭▭` |

## Labels, not copy

How people read UI: they scan for a label they recognise, an affordance (button, chevron,
checkbox) and a number. They don't read sentences in a screen. So:

- **Every label is at most three words**, in the product's own vocabulary from the captures
  or the ticket ("Cloud spend", not "Your cloud spending overview").
- **No sentences inside a frame.** Helper text, descriptions and explanations are grey
  bars (`text`). If a sentence feels necessary for the option to make sense, the layout is
  wrong; change the layout.
- **Numbers are obviously synthetic** (`$41.2k`, `12%`), never real customer data.
- **One primary action per view.** Two primary buttons is a decision the sketch is hiding;
  turn it into options.

## Grounding

Before drawing, read the most recent captures under `profile.kb.paths.screenshots` for the
screen the idea touches (at most 3 images). Reproduce the real shell and the real component
the idea changes, in greyscale. No capture: draw a neutral shell and add a note "shell
inferred, no capture". Never invent navigation, tabs or features the product doesn't have.
An earlier wireframe drew a navigation rail that didn't exist and marked a shipped feature
as out of scope, both contradicted by captures one folder away; this rule is why.

## Two renderings

- **In a session: ASCII, inline**, built from the ASCII forms above, options side by side
  when they fit in about 100 columns, stacked otherwise. Fast, and easy for the user to
  react to in chat. This is the default.
- **In a pack: HTML** from `sketch-kit.html` - copy its `<style>` block and use only its
  classes. Greyscale with one accent for note markers. No external requests, no images, no
  brand colours, no shadows, no gradients.

## Before showing it - the subtraction pass

Remove until it hurts: delete the weakest note on each option; delete any component that
doesn't change between options and isn't needed to recognise the screen; replace any
remaining sentence with a label or a grey bar. Then check each option's trade-off line
still holds.

## Worked example (ASCII, fictional)

```
 A: inline banner             B: drawer                  C: digest tab
┌─ Freight › Loads ──────┐  ┌─ Freight › Loads ─┬────┐  ┌─ Freight › Loads ──────┐
│ (2 drifting) [Review]  │  │ Load  Route  ETA  │▒▒▒▒│  │ Loads │ Drift (2)       │
│ Load  Route  ETA       │  │ L-12  ▭▭▭   14:20 │▒▒▒▒│  ├────────────────────────┤
│ L-12  ▭▭▭   14:20 ⚠    │  │ L-19  ▭▭▭   16:05 │▒▒▒▒│  │ Load  Drift  Since      │
└────────────────────────┘  └───────────────────┴────┘  │ L-12  +38km  09:10      │
+ seen at once / − noisy     + detail in place / − hidden └────────────────────────┘
                                                         + calm / − easy to miss
① banner needs a mute rule (challenge: muted in a week)
② drawer reuses load_variance fields (reality)
```
