# Linking and names

## Linking

`kb-conventions.md`'s link-style contract governs every link this skill writes
(`relative_markdown` or `wikilink`, per `kb.link_style`) - this file adds only what's
specific to a session note.

From `kb.paths.sessions`, everything else in the kb is typically one level up:
`../<kb.paths.decisions>/...`, `../Product/...`.

Link generously but not decoratively. Every note touched, every decision record fed, every
person or concept with a note of its own - link those, because they're what makes a
session findable from the places it's relevant. Don't link a term just because a note
happens to exist for it; a link should mean "this is relevant here", not "this word has a
page".

## Names - check before you write them

Before writing any person's name into a note, check `kb.people_file`. This is the
knowledge base's highest-frequency error class, and a session note that names people is
exactly where it recurs.

Check `people_confusions` (when set) for known mis-merges before writing a name down - two
people who share a first name, a nickname that's been misattributed once already, a
notetaker's transcript consistently mis-rendering someone's name. If a name is genuinely
ambiguous in the source, write what the source actually supports and flag the ambiguity
rather than guessing; a wrong name in a note propagates every time the note is read or
linked from.
