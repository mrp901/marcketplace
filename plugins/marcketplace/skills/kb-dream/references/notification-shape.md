# Board lines and the run record

## Settle carried-forward lines first

`chat: read canvas`, For you. Every line this skill has ever written carries a
`dream:<yymmdd>-N` tag (`../../../shared/surface-protocol.md`), category `kb-maintenance`.
Settle per "Settle before you append":

- A **ticked** line is the hub's. It dispatches this skill's `settle` mode, which does
  the work and returns; briefing closes the line once the hub's `done` sub-line is there.
  This run leaves it alone and never re-posts what it describes.
- An **edited** line's wording stands. A **deleted** line is never re-added. An
  **untouched** line rolls forward.

Never tick, close or delete a line yourself. The old step where this skill settled its
own ticked items on the next pass is gone: one flow, the Router acts on every tick.

## Then post this run's lines

One `chat: update canvas` batch, one line per Surfaced bullet, every Surfaced bullet, no
exception for one that looks small, in the protocol grammar and reading as the action a
tick causes:

```
- [ ] (dream:260922-1) 🧹 merge the two onboarding retro notes into one, keeping the August one as current · Inbox/2026-08-24-onboarding-retro.md
- [ ] (dream:260922-2) 🧹 lift the suppression on #eng-bugs:ticket-minor, you have ticked three since it was blocked · state
- [ ] (dream:260922-3) 🧹 fold: add the "never assume a type is unregistered" rule to session-log/SKILL.md, per the memory entry · Memory/2026-09-12-type-registry.md
```

If a bullet doesn't deserve a board line, it wasn't a Surfaced item and belongs in Flags
instead. Nothing actionable means nothing appended and no canvas call.

## Then record the run

No post, no webhook. Write `state.runs.kb-dream`:

```yaml
kb-dream:
  last_run_at: 2026-09-22T02:05:00+10:00
  status: ok            # quiet on a genuinely quiet run
  note: "curated 4, surfaced 3 · flags: 1 stale name pair · closed since last dream: 2 done by you, 1 by me"
  ref: Dreams/2026-09-22-dream.md
```

`note` is at most two lines: the Curated count and Surfaced count, then the condensed
Flags and what closed since the last dream. Depth lives in the dream note. The briefing's
Runs block carries this to the user; `profile.briefing.expected_runs` calls this skill
overdue if it stops running, which replaces the old proof-of-life post. A monthly run
adds the registry and voice review summaries to the note's second line.
