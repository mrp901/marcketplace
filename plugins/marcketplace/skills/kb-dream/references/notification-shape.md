# Canvas and notification

## Settle carried-forward items first

`chat: read canvas`, section "Dream log/actions" (create it if somehow missing). Every
checklist item this skill has ever written lives there, untagged in the sense that its
findings aren't tied to a tracker key - use the `dream:<yymmdd>-N` tag form from
`surface-protocol.md` for identity. A ticked item means "do this next pass", not "done".
For each ticked item:

- Check real state first (knowledge base file, `log.md`, a memory entry's `fold_status`) -
  already done: leave it, note who closed it.
- Not done, and answerable from evidence already in hand this run: do it now.
- Can't be done from this run: leave it ticked and open; name the one missing input.

Never tick or delete an item yourself except as the outcome of settling it this way -
reading is silent, an unticked item just rolls forward.

## Then post this run's items

One `chat: update canvas` batch (delete closed items, append new ones), one line per
Surfaced bullet, every Surfaced bullet, no exception for one that looks small:

```
- [ ] {one self-contained line} - tick to have me take this on next pass
```

If a bullet doesn't deserve a canvas item, it wasn't a Surfaced item and belongs in Flags
instead. No batching, nothing actionable means nothing appended, a quiet run appends
nothing and skips the canvas call entirely - but still notifies (below).

## Then notify

Per `../../shared/notify.md`, `notify.proof_of_life.kb-dream: true` by default - fires
every run including a quiet one, as proof of life. Opens with the markdown-link mention
form, never a raw mention token. Body shape, per `notify.md`'s table:

```
[@<name>](<deep link>) *Dream - <readable date/time>*

:broom: *Curated*
- {one line per act}
(or "Nothing to curate, the bundle was already clean")

:mag: *Surfaced*
- {one line per judgement call, fold proposal, or insight}
(or "Nothing needing your call")

:triangular_flag_on_post: *Flags*
- {conformance / stale / name-fact watch, condensed}
(or "All clear")

:white_check_mark: *Closed since last dream*
- {item} - you'd already done it
- {item} - you ticked it; I did it this pass
- {item} - you ticked it; still open, I need {the one missing input}
(or "Nothing from last time was ticked or done" / "First dream, nothing to compare")

:bar_chart: *Registry & voice* (monthly runs only)
- {registry review summary, at most 3 proposals}
- {voice review summary}

:file_folder: *Note*
- `<kb.paths.dreams>/YYYY-MM-DD-dream.md`
```

Two or three bullets a section; depth lives in the note. A quiet dream sends just the
header plus "Nothing to curate" - still a full notification, proof of life on a silent
run. "Closed since last dream" is filled from the recent-past read plus the ticked canvas
items settled above. Full sentences here are correct; the compression rules for `log.md`
and the dream note do not apply to this notification.
