# History

## 2026-09-22 built for marcketplace

`reply-draft` has no source predecessor - it is the `email` category's handler, built
directly against `shared/handler-contract.md`, `shared/voice.md` and
`shared/kb-conventions.md`, using `kb-note` (the other new handler) as its structural
sibling. Nothing was ported or inherited.

**Design decisions, with reasoning:**

- **`draft` is the only mode, permanently, not just at v1.** `handler-contract.md`'s
  category table already names this ("single-shot; drafts only, never sends"). This
  build states the reasoning directly in `## Handler mode` so a later contributor doesn't
  add a `send` confirming mode by analogy with `action-sweep`'s `push` or `idea-ticket`'s
  `file`: a send is exactly the irreversible external write the two-tick flow exists to
  gate, and the surface cannot show the user the final wording before it goes - a draft
  they paste themselves is the safer and, per the task brief, the actually better product.

- **Where the draft goes.** `handler-contract.md`'s `output_location` rules split
  handlers into three shapes: a kb writer (folder under `kb.paths`, default `inbox`), a
  tracker writer (project/parent key), and a "produces only a draft" handler that "takes
  nothing... reported in `artefacts`". `reply-draft` doesn't fit the third shape cleanly
  in practice, because a reply can run well past the 200-character `report_line` cap, so
  the full text has to live somewhere the user can actually open. This build treats it as
  a kb writer for output-location purposes only: `output_location` (a folder under
  `kb.paths`) or, absent that, `kb.paths.inbox`, exactly like `kb-note`. The `report_line`
  then does what the third shape's spirit intends - names the register and gap count and
  points at the link - while the artefact itself lives in the kb so it survives past the
  200 characters. See the open question below; this reading isn't stated outright in
  `handler-contract.md`.

- **Thread cap.** Most recent 20 messages, plus the opening message if it falls outside
  that window. Reasoning: the most recent messages carry the live ask, but a long
  thread's opening message often carries the original framing or the actual multi-part
  question a later reply-all narrows down to one part of - dropping it risks answering
  only the most recent fragment. Anything beyond the cap is named, not silently dropped,
  in the draft note's `**Source**` line, so the user knows to skim further back before
  sending on a thread that runs deeper than 20 messages.

- **Pushback and "no" - not softened.** The draft states a clear no or pushback plainly,
  at the register's own directness level, rather than adding hedging the register's own
  exemplars wouldn't use. Reasoning: `voice.md`'s avoid-list already bans invented
  hedging as an AI tell ("no over-hedging" - if it's worth saying, say it plainly), and
  voice calibration pulls the register's directness straight from the user's own real
  sent messages, not from a house style. Adding diplomatic softening the person
  themselves doesn't use is itself the AI tell this whole skill exists to avoid, not a
  courtesy. The register still governs tone - a customer-facing no is phrased differently
  from a teammate-chat no - but the padding gets cut, not the no.

- **Chat thread vs email, same category.** Detected from `item.ref`'s form (an email
  link vs a chat permalink) rather than from anything in the payload naming which it is,
  since `handler-contract.md`'s payload shape carries no explicit thread-kind field. Both
  go through the identical Flow (read, find every part of the ask, flag gaps, draft,
  self-check, write); only the drafted text's shape differs (subject line and formal
  greeting/sign-off for email; shorter, no subject, greeting only if the register's own
  exemplars use one, for chat) - see `references/reply-shapes.md`.

- **The marked gap format.** `[[GAP - <what's needed>]]`, double-bracketed and in
  capitals. Reasoning: it has to fail to look like real prose in any language the draft
  is written in, so it cannot slip through a fast skim-and-send. A softer form (a
  bracketed note in sentence case, an inline comment) risks reading as parenthetical
  colour rather than a stop sign. The draft note also lists every gap again under its own
  `## Gaps` heading, so a gap is visible even to someone who only reads the note's
  metadata and not the draft body itself.

**Open questions for the orchestrator:**

- No profile or state key needed that the schemas don't already define. `kb.paths.inbox`,
  `kb.types_registry`, `voice.registers` and `state.voice_edits` all exist already, the
  same set `kb-note` uses.
- Whether a "produces only a draft" handler is actually meant to write into the kb at
  all, given `handler-contract.md`'s own wording for that shape ("takes nothing... the
  draft's location is the handler's own business"). This build reads "the handler's own
  business" as licence to choose the kb as that business, since there's no other
  reachable, user-facing store defined anywhere in the shared references for a draft this
  long. If that reading is wrong, the alternative is a fourth `output_location` shape
  added to `handler-contract.md` naming the kb explicitly for over-length drafts, rather
  than every future long-draft handler re-deriving the same workaround independently.
- Whether a `type: Draft Reply` note in the kb should get the full index-line and
  log-line ceremony `kb-conventions.md` mandates for every note, given it's inherently
  transient - superseded the moment the user actually sends their own reply, and never
  updated back to reflect what was actually sent. This build follows the contract
  literally (no exception is written into `kb-conventions.md` for transient notes), but
  flags that a kb left running for months could accumulate a long tail of stale draft
  notes with no defined reaping pass. `kb-dream`'s existing curation contract doesn't
  currently name draft-reply staleness as something it checks for.
- Whether `email: search` is the right category for fetching a specific thread by
  `item.ref` rather than searching for one. `tool-capabilities.md`'s `email: search`
  entry is described as "search threads/mentions", not "fetch one thread by id/link" -
  this skill uses it as the closest existing category rather than inventing a new verb,
  since `reply-draft` is already listed as a reader of it in that table's "Used by"
  column.

**Friction against the three contracts** (handler-contract.md, voice.md,
kb-conventions.md):

- `handler-contract.md`'s three `output_location` shapes don't cover "a draft too long
  for the report line but not meant to be durable knowledge" - see the open question
  above. This build treats it as the closest of the three (kb writer) rather than
  inventing an unlisted fourth shape on its own initiative.
- `tool-capabilities.md` has no verb for "fetch one chat thread by permalink" - only
  `chat: search messages`. This skill's step 2 assumes the resolved `chat` tool prefix
  can fetch a specific thread given its link (the same assumption `action-sweep` and
  `kb-note` make reading `item.ref`), but the category table doesn't name that
  capability explicitly for chat the way it names `email: search` for mail.
- `voice.md`'s per-draft recording section says the comparison against what the user
  actually sent happens "on a later dispatch against the same source" for `reply-draft`
  specifically (unlike `kb-note`, which defers entirely to `kb-dream`). Nothing in the
  shared references says how a later dispatch is meant to recognise "the same source" -
  by `item.ref` matching, by `tag`, or by thread-id extracted from the ref. This build
  assumes `item.ref` matching (the same thread link ticked twice) without a stated
  mechanism to fall back on if the hub never re-dispatches the same ref twice in
  practice.

## 2026-09-22 orchestrator decision: drafts get their own location

The build put draft notes under the inbox, and flagged two worries about it: the contract
had no shape covering a long-but-transient draft, and nothing reaped them. Both were real.

`profile.kb.paths.drafts` now exists as a location of its own, and `kb-conventions.md`
gains a Transient drafts section: a draft carries `status: draft` and a note of what event
supersedes it, and `kb-dream` reaps superseded and stale ones under the never-destroy rule,
moving them to recycle rather than deleting. The inbox is an input queue for knowledge
worth keeping, which a superseded reply draft is not.

`handler-contract.md` now carries the fourth `output_location` shape this needed, so the
next handler producing a long draft does not re-derive the answer.

## 2026-09-25 canvas redesign (1.1.0): every tick means yes, do it

Accepts `chat-reply` alongside `email`: a chat thread or mention waiting on the user, found
by the Router's sweep or by `action-sweep`'s new chat sources. Same `draft` mode, same
register selection from the audience, and still never a `send` mode.
