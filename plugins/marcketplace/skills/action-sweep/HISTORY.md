# action-sweep - design rationale (for editors; not loaded at runtime)

- The full-text tracker mention search (`comment ~ "<name>"` JQL) was tested directly
  against the reference instance and does not reliably return results. The
  assignee/watcher/reporter-plus-comment-scan method that replaces it is load-bearing;
  see `references/mention-search-method.md`.
- The two hard stops - never guess a routing tier, never push without this run's
  explicit go-ahead - were built in deliberately and are guardrails, not defaults to
  relax with more usage.
- "Chase, don't just list" (one targeted search per to-do before giving up on it) exists
  because a bare unresolved to-do is a worse output than a resolved one, but an unbounded
  chase risks burning the whole run's budget on one ambiguous item.

## 2026-09-22 port to marcketplace

Renamed from `canvass` to `action-sweep`. Ported per `PORTING.md`, generalising the
confirmation model into the surface's two-tick flow and adding the notetaker source, per
the task brief.

**Behaviours carried over, unchanged in substance:**
- The whole gather -> draft -> stop -> push-on-go-ahead shape.
- The cold-start 7-day lookback, stated plainly in the note.
- The canvas-count guardrail (stop and ask above `budgets.action-sweep.canvas_guard`).
- "Chase, don't just list" with its one-search-per-item cap.
- The additive-comment rule - never overwrite an existing ticket's description or AC.
- The one-note-per-day overwrite-not-duplicate rule.
- The assignee/watcher/reporter mention-search method and the explicit statement that the
  obvious full-text search doesn't work.
- The three-tier sizing rule (small / larger / larger+defined) and the refusal to guess.

**Behaviours added (per the task brief):**
- A fourth gather source: notetaker meeting action items within `notetaker.lookback_days`,
  subject to the same drafting/confirmation discipline as the other three.
- Handler status: three modes (`targeted`, `meeting`, `push`) per `handler-contract.md`.
- The two-tick confirmation flow replacing the source's single "the user says push it in
  chat" gate: sweep mode posts one delegate line per routable candidate; a first tick
  dispatches `targeted`/`meeting` (drafts/re-confirms, returns `needs_confirmation`); the
  hub's resulting `sweep-push` line's tick is the only thing that dispatches `push`,
  which is the only mode that writes to the tracker.

**Decisions made where the source skill and the shared references were silent:**
- **Cursor moved from the note's own frontmatter into `state.cursors.action-sweep.
  scanned_through`.** The source skill's own ground rule said "state lives in the vault
  note itself, not a separate tracking file - one place for the cursor, not two copies to
  drift." `state-schema.md` already lists `cursors.action-sweep: {scanned_through}` as a
  shared-schema key, so the marketplace's own state document is now that one place
  instead of the note. This is a real behaviour change, not a relocation - flagging it
  explicitly since the source's own stated reasoning ("one place, not two") was used to
  justify the opposite choice originally. If the orchestrator wants the note to stay
  authoritative instead, `state.cursors.action-sweep` would need to be dropped from the
  schema, since keeping both is exactly the two-copies-drift problem the source warned
  about.
- **Where the "larger" tier's tracker write actually happens.** `handler-contract.md`'s
  category table separately lists `ticket-idea -> idea-ticket draft` (two-tick to
  `file`), which is the ideas-board specialist. The source skill pushed all three tiers
  itself. I kept action-sweep's own `push` mode responsible for all three tiers
  (unchanged from source) rather than routing "larger" candidates out to `idea-ticket`,
  because PORTING.md instructs against inventing new cross-skill delegation the shared
  references don't state outright, and `handler-contract.md` never says action-sweep's
  own "larger" tier candidates should be re-tagged `ticket-idea` instead of
  `ticket-reply`/`ticket-minor`. **Open question for the orchestrator:** should a
  "larger"-tier candidate from a sweep get a `ticket-idea` delegate line (dispatching to
  `idea-ticket`) instead of staying inside action-sweep's own push? That would remove
  ideas-board logic (and the `idea-ticket` audit step's stronger critic model, per
  `model-tiers.md`) from this skill entirely, which may be the intended design - as
  written, this port preserves the source's single-skill-does-all-tiers behaviour instead
  of guessing at that split.
- **No explicit meeting-count cap for the notetaker source.** `profiles/example.md`'s
  `budgets.action-sweep` block has no notetaker key; I bounded the fourth source by
  `notetaker.lookback_days` alone (time window, not a count). See
  `profiles/extract/action-sweep.local.md`'s notes. Flagging in case
  `budgets.action-sweep.notetaker_meetings` (or similar) should be added to
  `profile-schema.md` once real usage shows a 7-day window can return enough meetings to
  matter.
- **Unclear-routing candidates get no delegate line at all**, rather than a delegate line
  that asks the classification question on the surface. A surface tick can only mean
  "dispatch" or "close" per `surface-protocol.md`'s two section types - there is no tick
  shape for "here is my answer to your classification question." Keeping the item
  unrouted in the note (with a stated callout) and out of the surface entirely was the
  only structural way to keep "never guess" true under an unattended run. Open question:
  should the note's "Unclear routing" section itself feed some other mechanism (a
  Plugin notices fast-fail-style line) so it isn't only discoverable by opening the note?

**Nothing was dropped.** Every fixed fact in the source's "Fixed facts" section moved to
`profile.*` (see `profiles/extract/action-sweep.local.md`); the sizing
rule, both ticket-draft shapes, the note structure, the gather procedure and the mention-
search method all moved to `references/` with pointer lines left in `SKILL.md`, per
`line_budget.py`'s relocation requirement.

**Open questions for the orchestrator**, beyond the two flagged above:
- No `evals/` directory exists under `source/canvass/` to carry forward or
  re-fictionalise - this port ships with none, same as the source. Flagging so this isn't
  mistaken for an omission during QA.
- `tracker.issue_types.bug` could not be extracted from this source (only `story` and
  `epic` ids are named as fixed facts) - noted in the extract file's "ambiguous or
  missing values" section rather than guessed.

## 2026-09-22 orchestrator sign-off on the two open questions

**The sizing tiers stay with this skill.** The port asked whether a "larger" candidate
should be handed to `idea-ticket` rather than filed here, since that skill specialises in
ideas-board tickets. Decision: keep all three tiers here, as the source had them. The
sizing call and the draft are made together from one gathered context; handing off would
mean re-deriving that context in another skill, and `idea-ticket`'s value is its audit loop
over a rough problem a human described, not over an already-drafted sweep candidate.

The known consequence, recorded so nobody is surprised by it: a larger-tier candidate filed
from a sweep does not pass through `idea-ticket`'s critic audit, where the same idea raised
directly through `idea-ticket` would. That is an accepted difference, not an oversight. If
it turns out to matter, the change is small: have the `targeted` mode return
`next_action.category: ticket-idea` for the larger tier instead of `sweep-push`, and the
tick dispatches the specialist, at the cost of one extra tick.

**The cursor stays in the shared state document.** The port noticed that the source's own
ground rule said state belongs in the note, one place not two, and that the shared schema
says otherwise. Both are right about different things. The source's rule was about to-dos
and flags, where two copies drift and cost twice. A cursor is not that: it is machine
bookkeeping every skill keeps in one shared place, and the note may be unreachable on a run
where the knowledge base connector is down, which is exactly when the cursor still needs to
be correct. The note continues to print `scanned_through` for a human reader; that printed
value is an echo, not the source of truth.

## 2026-09-24 `targeted`/`meeting` draft directly when dispatched with no anchor

`proactive-router`'s shared category table (`categories.md`/`handler-contract.md`) routes
`ticket-reply` and `ticket-minor` items to `action-sweep`'s `targeted` mode regardless of
where they were classified - including items the hub itself classified straight from a
Slack reaction or saved message, which never passed through this skill's own sweep and so
never got a note anchor. `targeted`'s contract only documented the anchor-read path,
leaving that case undefined; a real run hit it with five backlog items on the surface,
four of which had no anchor to read.

Considered four alternatives (full write-up and diagrams in the session that found this):
a new `targeted-adhoc` mode; the hub synthesising the anchor itself before dispatch; and a
new `ticket-direct` category with its own handler. Rejected the hub option outright - it
would have the hub writing into a kb note, which only handlers are supposed to do (see
`../../shared/handler-contract.md`'s inline-vs-dispatch boundary: the hub's only writable
store is the surface). Rejected the new-category option as the most correct in isolation
but the most new surface for two categories that don't need a whole second handler. Landed
on extending `targeted`/`meeting` in place: branch on whether `item.ref` already resolves
to a note anchor, and if not, draft into today's note directly (same sizing and
draft-format logic, same note this skill already owns and writes in sweep mode) before
continuing exactly as the anchor-found path. `push`'s existing re-read-the-note-fresh step
needed no change - it already re-reads whatever is on record when it fires, whether that
draft was written during a sweep or during this dispatch.

The "never re-runs the sweep" hard stop stays intact: drafting one item is not gathering
all four sources again, so this doesn't reopen the sweep, it just gives `targeted` a
second way to produce the same anchor a sweep would have.
