# briefing - design rationale (for editors; not loaded at runtime)

- The user's chat identity was confirmed by asking the chat connector for its own
  authenticated identity (no user id passed) and matching the returned email against the
  configured `user.email`. Treat as certain once resolved by onboarding step 4.
- The mention-link prefix on the posted message exists because a plain post to one's own DM
  channel does not reliably push a mobile notification - see `notify.md`'s "Mention form"
  section, which generalises this into the shared markdown-link rule every notifying skill
  now follows.
- An earlier state-document duplicate was created by mistake in a colleague's personal space
  during original setup and never cleaned up. Not a pattern to repeat; onboarding's bootstrap
  flow (`onboarding.md` step 1) now creates the state document once, from the schema, and
  records its ref back into the profile so a stray duplicate has nowhere to come from.
- To-dos and flags deliberately live only on the surface, never duplicated into the state
  document: two copies drift and cost twice. `state-schema.md`'s "Why two documents" section
  generalises the same reasoning across the whole plugin, not just this skill.
- Acknowledgement replies ("got it, added X") were tried and rejected as pure token spend -
  carried forward unchanged; briefing still sends nothing beyond the one nudge.
- Time-agnosticity: a naive same-day rerun was verified not to invent false overdue flags when
  "running behind" is decided by real timestamps only, never elapsed time alone. Unchanged in
  the port; see `## Time rules`.
- The skill was once condensed from roughly 3.3k to 1.5k tokens with behaviour unchanged -
  the same discipline motivates this port's `references/` split under the 150-line cap.

## 2026-09-22 port to marcketplace

Renamed from `briefing` (source skill of the same name; no rename needed). Ported per
`PORTING.md`, generalising the reporter role the plan describes onto this skill for the first
time.

**Behaviours carried over, unchanged in substance:**
- The run-timestamp heading, never a time-of-day greeting.
- "Running behind means a real timestamp is in the past", never elapsed time alone.
- The glossary check-before-write discipline and the 2-new-terms-per-run cap.
- The one-read-one-write surface discipline (read once, batch every write).
- Per-source degradation to `Signed out` rather than a fast-fail.
- The ground rule that everything gathered is data, never instructions.

**Behaviours added (the new reporter role, per PORTING.md's task brief):**
- Closing the loop across every surface section, not just briefing's own, using the one
  documented carve-out in `surface-protocol.md`.
- Pruning `state.items` on every close.
- Mechanically trimming Closed to 14 days or 40 lines every run that writes it
  (`scripts/trim_closed.py`).
- A "Since last briefing" report summarising `state.outcomes` and counting ticked-but-
  undispatched delegate items.
- Notetaker prep lines, gated by `notetaker.prep_lines` and capped at one notetaker call.

**Decisions made where the source skill was silent:**
- **Terms to learn now closes to Closed on promotion.** The source skill explicitly kept a
  confirmed term out of "Closed recently" ("it isn't a to-do, so it doesn't go to Closed
  recently"). The port's task brief calls Terms to learn an acknowledge section and states
  "acknowledge-section items close on the tick alone" with no carved-out exception for this
  one section. I generalised Terms to learn to behave like every other acknowledge section -
  promote to glossary, then close with outcome `learned`, `by you` - over keeping the
  source's narrower behaviour. See `references/glossary-and-terms.md`, "On tick: promote and
  close". **Open question for the orchestrator:** confirm this generalisation is intended: if
  Terms to learn should stay outside Closed as a deliberate exception (the way the source
  skill built it), that needs stating explicitly in `surface-protocol.md`'s section table,
  since as written it reads as an ordinary acknowledge section with no carve-out.
- **Report placement.** The task brief says the report must ensure "the user must never have
  to open the surface to find out that something they ticked has not been actioned yet," but
  doesn't say whether that report belongs in the posted message, on the surface, or both. I
  put it in the posted message only (a "Since last briefing" block, see
  `references/message-format.md` and `references/closed-and-outcomes.md`) since the surface
  already carries the same information structurally, as sub-lines under each ticked item and
  as absence of a sub-line for a queued one - duplicating it as a written surface section
  seemed redundant with what step 2 already reads there. Flagging this as a judgement call in
  case the orchestrator wants an explicit surface section instead.
- **Queued-item detection.** "Queued but undispatched because the hub hit its dispatch cap"
  is inferred from the absence of any sub-line (not even a router "no handler" line) under a
  ticked delegate item - there is no explicit state flag for "ticked, cap-limited, not yet
  seen by the hub". This is an inference from `handler-contract.md`'s per-run dispatch cap,
  not a directly stated signal; flagging in case a future version of the hub contract wants
  to write an explicit marker instead.
- **`prep:` line placement.** Placed as a sub-bullet directly under the calendar event line
  in the Calendar snapshot, rather than as a separate list. Nothing in the task brief or
  `surface-protocol.md`'s snapshot rule dictates the exact sub-line shape; this follows the
  handler report sub-line's own two-space-indent, one-line convention for consistency.

**Nothing was dropped.** Every behaviour in the source `SKILL.md` and its Fixed facts had a
generalised home: identity/org values moved to `profile.*` (see
`profiles/extract/briefing.local.md`), the state page's cursors/glossary/nicknames moved to
`state.*` per `state-schema.md`, and the canvas mechanics moved to `surface-protocol.md`'s
shared rules, referenced rather than restated.

**Open questions for the orchestrator**, beyond the two flagged above:
- `tracker.project_key` could not be extracted from this source skill (it queries a JQL
  fragment across all of the user's own work, not one fixed project) - `profile-schema.md`'s
  own "Where the current values come from" table already points at `canvass`/`action-sweep`
  for that key, so this is confirmation rather than a gap, but noting it here since this
  skill's extract file explicitly does not supply it.
- `state-schema.md`'s `items.<tag>` shape does not carry a `category` breakdown per section
  beyond the one `category` field - briefing's close loop in step 2 relies on the section a
  tag's line currently sits in (read live off the surface) rather than a stored section field
  on the item, since `state.items.<tag>.section` is already listed in the schema and does
  cover this. No new key was needed; noted only because it was worth checking before writing
  the close-loop logic.

## 2026-09-22 orchestrator correction: Terms to learn stays out of Closed

The port generalised a ticked Terms to learn line into an ordinary acknowledge close, which
would have written a Closed entry per confirmed term. Reverted. The source skill kept
confirmed terms out of the Closed log on purpose: a term is vocabulary the system absorbed,
not work anyone finished, and logging it crowds out real closed items inside the retention
bound. `shared/surface-protocol.md` now states the exception explicitly, so a later port
cannot rediscover the same ambiguity. The port entry above flagged this as an open question
rather than deciding it silently, which is what made the catch cheap.
