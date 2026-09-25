# Glossary and `term:` lines

The glossary loop, unchanged in mechanism from the source skill except for who promotes.
It rides entirely on connector calls already made for the message; it never adds a lookup
of its own.

## Checking before writing

Before writing any acronym, project codename or internal term into the posted message,
check it against `state.glossary` (term -> confirmed one-line meaning) and
`state.nicknames` (email -> nickname). A confirmed glossary entry may be quoted inline
with its short gloss (see `message-format.md`'s worked example). Never invent or guess a
definition; if a term isn't in the glossary, use it verbatim in the message and leave
interpretation to the user.

## Capturing new terms

While composing the message, note anything that reads as domain jargon, a project
codename or an internal acronym (not a person's name, not a tracker key, not a common
English word) that is not already in `state.glossary`, `state.nicknames`, or already
sitting (ticked or unticked) as a `term:` line in For you. For each one:

- Add an unticked line to For you in the protocol grammar, tag `(term:<yymmdd>-N)`,
  category `term`, emoji 📘, text `add to glossary: <term> = <the best one-line reading
  directly supportable from the surrounding message or ticket text>`, and a ref to where
  the term was seen. Never a guess that can't be pointed back to a source.
- Cap this at 2 new terms per run. Skip the rest silently rather than cluttering the
  board or spending an extra lookup to chase down a definition.

This is the entire "ask": no chat question, no interruption. The user reviews, edits the
reading if it is wrong, and ticks on their own time.

## On tick: the Router promotes, briefing removes

A tick means "yes, add it". The hub's `inline:promote` (see
`../../../shared/handler-contract.md`) writes the line's text as the user left it into
`state.glossary`, keyed by the term, and adds a `done · added to glossary` sub-line.
Briefing, on its next run, removes the line. **Nothing is written to Closed.** A confirmed
term is a piece of vocabulary the system has absorbed, not a task anybody completed;
logging it as closed work pads the log with entries the user never asked for and pushes
real closed items out of the retention window sooner. `surface-protocol.md` carries the
same exception under "Closing". Do not "fix" this into consistency with the other lines.
