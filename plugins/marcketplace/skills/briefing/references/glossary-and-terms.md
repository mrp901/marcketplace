# Glossary and Terms to learn

The glossary loop generalised from the source skill, unchanged in mechanism. It rides
entirely on connector calls already made for the message; it never adds a lookup of its own.

## Checking before writing

Before writing any acronym, project codename or internal term into the posted message, check
it against `state.glossary` (term -> confirmed one-line meaning) and `state.nicknames`
(email -> nickname). A confirmed glossary entry may be quoted inline with its short gloss (see
`message-format.md`'s worked example). Never invent or guess a definition - if a term isn't
in the glossary, use it verbatim in the message and leave interpretation to the user.

## Capturing new terms

While composing the message, note anything that reads as domain jargon, a project codename or
an internal acronym - not a person's name, not a tracker key, not a common English word - and
that is not already in `state.glossary`, `state.nicknames`, or already sitting (ticked or
unticked) in the Terms to learn section. For each one:

- Add an unticked checkbox line with the term and the best one-line reading directly
  supportable from the surrounding message or ticket text - never a guess that can't be
  pointed back to a source.
- Cap this at 2 new terms per run. Skip the rest silently rather than cluttering the surface
  or spending an extra lookup to chase down a definition.

This is the entire "ask" - no chat question, no interruption. The user reviews and ticks (or
edits) the line on their own time, exactly like a To-do.

## On tick: promote and remove, never Closed

Per `SKILL.md` step 2, a ticked Terms to learn line does two things, in order, in the same
run:

1. **Promote.** The line's text as the user left it (their edit, if any, is authoritative per
   `surface-protocol.md`'s edited-not-ticked row) is written into `state.glossary`, keyed by
   the term.
2. **Remove the line** from the Terms to learn section. Nothing is written to Closed.

Terms to learn is the one acknowledge section that does not feed Closed, and this is
deliberate rather than an oversight. A confirmed term is a piece of vocabulary the system has
absorbed, not a task anybody completed; logging it as closed work pads the log with entries
the user never asked for and pushes real closed items out of the retention window sooner.
`surface-protocol.md` carries the same exception in its acknowledge-section definition. Do
not "fix" this into consistency with the other acknowledge sections.
