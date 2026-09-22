# Loop protocol

The full mechanics behind `SKILL.md`'s Flow steps 1, 3 and 4. Read `circles.md` alongside
this for what each circle is for; this file is about the control flow that moves a question
through them.

## Step 0 - set up and seed the question list

Always, in this order, regardless of fresh pass or resume:

1. Check for an existing note at `kb.paths.research/<idea-key>-*.md` (most recently modified,
   if more than one matches - that should not normally happen; flag it if it does). This is
   the very first thing that happens, before any `ideas: get issue` call.
   - Found, with `deep_dive_status` present and not `complete` -> **resume**. Fetch only
     comments/updates since the note's last-updated timestamp (not the full issue). Load the
     note's "Resolved findings" and "Run state" as given - nothing they cover gets
     re-investigated. Any new comment this delta fetch returns is triaged exactly like a
     mid-loop spawn (dedupe against Run state and Resolved findings, classify, route into Open
     questions or Decisions-for-you, or discard as already covered) before the merged queue
     enters "The loop" - a delta fetch that is never triaged is pointless.
   - Otherwise (no note; note with no `deep_dive_status`; or `complete` but the user wants to
     push further) -> **fresh pass**. `ideas: get issue` on the idea key, full fields,
     markdown format: full description, all comments, links, attachments.
2. Resolve the loop budget: the value given, or `budgets.idea-deep-dive.loop_budget` (default
   8). Applies identically on a resume - a resumed run gets its own fresh budget, it does not
   inherit or subtract from a prior run's.
3. Confirm codebase availability (`codebase.access`, folder connected at `codebase.path`)
   once - record the answer for the whole run. Always done, identically, on both a fresh pass
   and a resume - availability can change between runs, so a resume re-checks it rather than
   trusting last time's answer. Not linked this run -> circle `code` is unavailable for the
   whole run, say so once.
4. Now branch: **resume** -> skip straight to "The loop" with the note's queue (Run state) as
   seeded. **Fresh pass** -> continue with seeding (`SKILL.md` step 2).

**Seeding, fresh pass only.** Open questions (evidentiary gaps a fact could settle) vs.
Decisions for you (judgment calls only the user or a named decision-maker can make) are kept
in two separate piles for the whole run; only Open questions feed the loop. Genuinely
half-and-half ("does the market have budget for this?") is evidentiary if a fact would settle
it, a decision if nothing could; when truly unclear, default to Decisions-for-you - nothing
bad happens to a question sitting there. A note's existing "Open questions" become the seed
list if one exists (its established position is not re-litigated); no note at all -> build
the seed list from the issue, framed against the four product risks (Value, Usability,
Feasibility, Viability) the way `idea-scout`'s note already does. Number the open questions
(whichever blocks the most other questions or the idea's core viability goes first; ties by
order of appearance). Every seed question starts at chain-depth 0.

## The batch sweep (circles `kb` + `people`, once, fresh pass only)

One dispatch per cheap source - `kb`, `chat`, `email`, `notetaker` - each its own subagent
call on `budgets.models.search`, never combined, each covering every seeded open question at
once. This is the sweep's entire allowance for these questions, not one search per question.
Each dispatch returns a list of `{question#, found, answer, source}` records, one per question
it could resolve.

Record whatever this resolves in "Resolved findings" (see `write-up.md`) - it never enters
the per-question loop and never costs a loop. Log all four query counts used (exactly 1 each,
sweep included - an unlogged cap cannot be audited later).

A question still unresolved after the sweep proceeds to "The loop", entering at whichever of
circle `code` or `web` actually applies to it (see `circles.md`'s applicability rules) - not
at `kb` or `people`, which it already had tried. Does not apply to a question spawned later,
mid-loop, or to a resumed run's queue - those questions get their own individual `kb`/`people`
search inside the loop if they need it.

## Spawned questions

Investigating a question can surface a new one whether or not the original question itself
gets resolved in the same pass - check for this every time a circle is searched, not only
when the original comes up empty. Handle a newly surfaced question in this order:

1. **Dedupe first.** Substantially the same as something already seeded, queued, resolved,
   stuck, PENDING, or in Decisions-for-you -> do not add it; note the cross-reference against
   the existing item and stop here.
2. **Classify** (not a duplicate): evidentiary gap, or a call only a person can make - same
   test as Step 0's seeding. A spawned decision goes straight to Decisions-for-you, untouched
   by the loop.
3. **Route** a spawned evidentiary question as BLOCKING (the question that surfaced it cannot
   be answered without it) or INCIDENTAL (true and worth knowing, not a dependency):
   - **BLOCKING** -> insert it immediately next in the queue, tag "spawned by Q#, blocks Q#".
     The question that surfaced it becomes **PENDING** - parked, not resolved, not stuck -
     until this new one resolves. Chain-depth = parent's depth + 1.
   - **INCIDENTAL** -> append to the end of the queue, tag "spawned by Q#", chain-depth 0 (a
     new thread, not a dependency).
4. **Depth cap.** Chain-depth may not exceed `budgets.idea-deep-dive.depth_cap` (default 3).
   If resolving a question at the cap would itself require spawning a further BLOCKING
   dependency, do not create that dependency: mark the capped question STUCK - reason: "needs
   a further, unnamed dependency resolved beyond the chain-depth cap" - and cascade STUCK up
   through every PENDING ancestor in the same chain, since each was blocked transitively on
   this one. This is the same run-halting stop as any other stuck question, not a smaller,
   local one; report the full chain root-to-leaf.

A PENDING question is still a member of the queue - parked, not removed, just not at the
front and not under active investigation until its blocker clears. When the blocker resolves,
the parent is taken up again - this is a fresh take-off-the-queue event and always costs
exactly one loop. Check first whether the blocker's answer directly settles the parent (it
often will - mark it resolved immediately, no further search needed); if not, the parent
continues forward into whichever circles it had NOT yet tried (an exhausted circle is not
retried unless the deliberate-reopen exception applies); if it has none left to try, it goes
straight to the stuck-check.

Every spawned question, blocking or incidental, costs a loop the moment it is taken off the
queue - there is no separate allowance. Heavy spawning legitimately ends a run at the loop
limit sooner; that is a correct outcome, not a bug.

## The loop

A loop is charged the moment a question is taken off the queue for investigation - regardless
of which circle resolves it, whether it becomes PENDING, or whether it turns out stuck.
PENDING questions are queue members, not removed from it - so "the queue is empty" already
means every question, including any that were ever PENDING, has reached resolved or stuck.
The run ends the moment one of three things is true: the queue is empty (complete), a
question is stuck (halt immediately, no skipping ahead), or the budget is fully spent with
questions still queued (loop-limit).

- **Stop-check (before taking a question - only complete/loop-limit are decided here):**
  queue empty -> stop, status **complete**. Otherwise, if the loop count already equals the
  budget -> stop, status **loop-limit reached**, without taking another question (so the
  budget is spent only on questions actually investigated, never on one left untouched).
  Stuck is different - it is never decided by this pre-take check; it is discovered
  mid-investigation of a question already taken (see Stuck-check below), and when it happens
  it overrides whatever this check would otherwise say, halting the run immediately.
- **Take & charge:** take the next queued question, increment the loop count now.
- **Route to a starting circle:** a batch-sweep survivor starts at whichever of `code`
  (feasibility-shaped) or `web` (market-shaped) applies per `circles.md`'s applicability rules
  - skipping `kb`/`people`, which it already had. A freshly spawned mid-loop question (never
  through any circle) starts at `kb` and proceeds through `people`, then `code`/`web` as
  applicable. A re-entering PENDING question, and every question carried forward into a
  resumed run's queue, starts wherever its own recorded history says to: whichever circles Run
  state shows it has NOT yet exhausted, in circle order - never restarting at `kb` just
  because the run itself is new.
- **Investigate**, in circle order, only through circles that apply to and have not already
  been exhausted for this question. See `circles.md` for each circle's caps and what a sourced
  answer looks like. At any point, whether or not this question resolves: if the search also
  surfaced a genuine new question, handle it per "Spawned questions" above - this can happen
  on a resolved question exactly as on an unresolved one.
- **After investigating:**
  - Resolved -> back to the stop-check for the next question.
  - Not resolved, but it spawned a BLOCKING question -> this question is now PENDING (not
    stuck); back to the stop-check for the next question.
  - Not resolved, and every circle that plausibly applies has been tried or found
    unavailable, with nothing left to check -> **Stuck-check**: mark STUCK, record exactly
    what was checked (naming which circles, how many searches each, and whether each was
    checked-and-empty or unavailable-to-check) and what is missing (a specific input, a named
    person, "codebase access needed and was not available", or "no circle plausibly applies -
    needs the user to say what would answer this"), and **stop the whole run here**. If this
    question blocks a PENDING parent, the parent is stuck too; report the whole chain.

## Exhaustion and the deliberate reopen

A circle is **exhausted** for a question the moment it has been searched at all for that
question (even just once) without resolving it - exhaustion is about having tried, not about
spending the full cap. An exhausted circle is not retried later just because the question
re-enters the queue (e.g. a PENDING parent resuming after its blocker clears continues
forward only into circles it has not tried yet).

The one exception: a **deliberate reopen** - the newly resolved blocker's answer names a
concrete new thing to search for in a circle already tried (a specific file, term, or thread
that was not known before) - is allowed **at most once per question per circle**, capped
below that circle's original allowance (e.g. `code` reopens at 2 further searches, not 3), and
logged as a distinct new attempt; if that does not resolve it either, the circle is exhausted
for good and no second reopen is allowed. This is a judgment call each time, never an
automatic default, and it never lets a question's total searches at one circle run unbounded.

Record every count actually used at every circle - sweep included - in the Deep-dive log; an
unlogged cap cannot be audited later.
