# Frame and build

Full detail for `SKILL.md` Steps 3 and 4.

## Step 3 - Frame

Rotate through five lenses by idea number modulo 5 - a free pick is not the default; five
runs of free picks once collapsed into one repeated three-artboard shape.

0. **Moment of confusion** - the point where the user cannot read the screen.
1. **A year after it ships** - at scale, with the mess that accrues.
2. **A tenth of the effort** - the smallest thing that resolves the open fork.
3. **Competitor's screen beside ours** - the same job, their framing.
4. **Missing data** - nothing loaded, partial, or unmapped.

This is a lens, not a cage: if the captures make the rotated lens nonsensical for this
idea, drop to the next one down, naming both the assigned lens and the one used in the
wireframe's header. Then set the artboard count and defend it in one clause - a single
artboard is legitimate and often the stronger choice; three artboards is not a default to
reach for out of habit.

## Step 4 - Build

One self-contained HTML file: inline `<style>`, no external requests, JavaScript only if
tiny and inline. Artboards show the specific screen(s) or short flow the idea changes, not
the whole product.

### House style

- Greyscale with one accent colour: paper white, near-black ink, mid fills, light borders,
  the single accent reserved for markers and callouts only. No brand colours, gradients, or
  shadows beyond a hairline. A system sans-serif stack.
- Reproduce the real shell from the captures read in Step 2 - navigation, breadcrumb,
  primary action, filters, footer - in greyscale. Never invent a shell, and never copy one
  from a previous wireframe unchecked against a current capture. Data appears as grey
  placeholder bars and obviously-synthetic figures - never real customer names or numbers,
  never a live figure lifted straight from a capture.
- **Annotations are the point of the artefact.** Numbered accent markers on the regions
  that matter, matching numbered notes in a side rail. Each note is one to two sentences
  tied to a source - a risk it addresses, a decision it forces, an open question - framed
  against the four product risks (value, usability, feasibility, viability). Position every
  marker with CSS relative to the element it describes; a hardcoded pixel offset is a
  defect, not a shortcut, because it breaks the moment the artboard reflows.
- Header band: idea key and title, a plain "low-fidelity wireframe - for reaction, not a
  spec" label, the date, and a short paragraph covering what the wireframe shows, what was
  assumed, and which frame was used. Footer: which skill generated it, plus the relative
  paths of everything read, including the capture folder. Sensible max-width, wraps at
  narrow widths, prints cleanly.

The as-built-versus-fix pair (showing the current state beside the proposed one) fits
naturally where a capture directly contradicts the research note, but it is overused -
don't reach for it out of habit.

### Subtract, deliberately

Models add and rarely remove. Once a draft is complete, subtract explicitly: delete the two
weakest annotations, and, if more than one artboard was drawn, drop the one carrying the
fewest annotations. Restore an annotation only if losing it breaks a claim the wireframe
makes elsewhere. Ten seconds of reading is the whole budget for the person looking at it.
