# idea-deep-dive - design rationale (for editors; not loaded at runtime)

No prior `HISTORY.md` existed for `source/cloud-idea-deep-dive` - this is the first entry.

## 2026-09-22 port to marcketplace

Renamed from `cloud-idea-deep-dive`. Ported per `PORTING.md`, from a 425-line source
`SKILL.md` (a "Fixed facts" section, four circles in full, the loop's control flow, and a
22-item acceptance-criteria list all inline) down to a 150-line `SKILL.md` plus five
`references/` files. This was flagged as the heaviest restructure in the project; the
relocation list below is the primary artefact for reviewing it.

### Where every source rule went

- **Frontmatter, role paragraph, "no budget given -> 8"** -> `SKILL.md` intro.
- **"Runtime strategy - keep this cheap"** (cost order, model tiering, what never
  delegates) -> `references/dispatch-and-cost.md`, kept as the stable cache-eligible prefix
  the source asked for, and pointed at from `SKILL.md`'s `## Budget`.
- **"Fixed facts"** -> fully dissolved. Every value moved to `profiles/extract/idea-deep-dive.local.md`
  with its source line, or generalised to a profile/state key referenced by name in
  `## Needs`: cloudId/project/issue type -> `tracker.cloud_id`, `ideas.project_key`,
  `ideas.issue_type`; the shared canvas and webhook -> `surface.id`/`surface.url` and
  `notify.webhooks.idea-deep-dive`; the vault -> `kb.name`, `kb.paths.research`; the
  codebase path and device-bridge-only access rule -> `codebase.path`, `codebase.access`
  (the "M365 fallback is for the vault, never a substitute for codebase access" caveat
  survives as prose in `references/circles.md`'s `code` section and `write-up.md`'s
  storage note is folded into the generic `kb-conventions.md`/`tool-capabilities.md`
  degradation rule rather than restated).
- **"The four circles, in order"** -> `references/circles.md`, in full: each circle's
  purpose, cue words, caps (now `circle_caps.{kb,people,code,web}`), the both-apply/
  neither-apply/only-one-applies rules, and the never-skip-1-or-2 rule (`kb`/`people`).
  Circle 2 gained the notetaker as a third peer platform here, per the task brief.
- **"Step 0 - Set up and seed the question list"** -> `references/loop-protocol.md`'s
  "Step 0" section, verbatim in substance (note-check-before-Jira-call order, resume
  detection via `deep_dive_status`, budget resolution, codebase-availability check, the
  open-questions/decisions-for-you split, question numbering and chain-depth-0 seeding).
- **"Batch sweep (circles 1+2, once...)"** -> `references/loop-protocol.md`'s "The batch
  sweep" section. Extended from 3 to 4 dispatches (one per cheap source: `kb`, `chat`,
  `email`, `notetaker`) - see "Decisions made" below.
- **"Spawned questions"** -> `references/loop-protocol.md`'s "Spawned questions" section,
  in full: dedupe-then-classify-then-route order, BLOCKING/INCIDENTAL handling, PENDING
  semantics, the depth-cap cascade, and "every spawned question costs a loop".
- **"The loop"** -> `references/loop-protocol.md`'s "The loop" section: the stop-check,
  take-and-charge, starting-circle routing (survivor vs. fresh spawn vs. resumed/PENDING),
  the per-circle investigate step, and the three post-investigation branches
  (resolved/PENDING/stuck).
- **Exhaustion definition and the deliberate-reopen rule** (embedded mid-paragraph in the
  source's "Runtime strategy" and "The loop" sections) -> pulled into its own
  "Exhaustion and the deliberate reopen" section in `references/loop-protocol.md` so the
  rule reads as one coherent unit instead of split across two source locations; also
  restated as a one-line ground rule in `SKILL.md` since it is easy to lose.
- **"Write-up"** -> `references/write-up.md`, in full: the note structure (frontmatter
  field, Resolved findings, Open questions, Decisions for you, Run state, Deep-dive log),
  the surface append rules (per end state, tagging convention shared with `idea-scout`,
  never tick/delete another run's item), and the notify payload shape.
- **"Guardrails"** -> split between `SKILL.md`'s `## Ground rules` (never invent an
  answer, never touch Decisions-for-you, never write to the ideas board without explicit
  ask, one idea per run, the couldn't-check/found-nothing distinction) and
  `## Surface`/`references/write-up.md` for the append-only, never-tick-another-run's-item
  specifics.
- **"Acceptance criteria" (AC1-AC22)** -> `references/acceptance-criteria.md`, kept in full
  as a manual review checklist (there is no `evals/` directory on the source skill to
  re-fictionalise instead), terms generalised to this port's vocabulary.

### Behaviours added, per the task brief

- **The notetaker joins circle 2 as a peer of chat and email**, same per-platform cap
  (`circle_caps.people`), same sourcing requirement (meeting title/date standing in for a
  permalink). See `references/circles.md`.

### Decisions made where the source skill was silent

- **The upfront sweep grew from 3 dispatches to 4.** The source's own text says "exactly
  three dispatches, one per cheap source" - a rule the task brief explicitly calls out as
  one that must not be lost. Read literally, "one per cheap source" is a structural
  invariant, not a fixed cardinality; since the task brief's headline change for this port
  is "the four circles gain a source" and directs folding the notetaker into circle 2 "subject
  to the same caps" with no carve-out excluding the sweep, I extended the sweep to one
  dispatch per cheap source including the notetaker - 4 total - rather than leaving the
  notetaker out of the sweep and only adding it to the per-question loop. **Flagging this for
  the orchestrator**: if the intent was for the notetaker to join only the per-question loop
  and the sweep to stay fixed at 3, that is a one-line change in
  `references/loop-protocol.md`'s "The batch sweep" section and `SKILL.md` step 3, but as
  written the sweep and the loop treat all three `people` platforms identically.
- **`notetaker.lookback_days` was already a defined profile key** (from `profile-schema.md`,
  read by `briefing` and `action-sweep`) but had no source value in this skill to extract,
  since the source predates the notetaker circle entirely. Used the existing key rather than
  inventing a new one; no value was extracted for it in
  `profiles/extract/idea-deep-dive.local.md` - the schema default (7 days) applies.
- **The AC section's home.** Treated it as reference material worth preserving (a precise,
  load-bearing behavioural spec) rather than dropped for having no `evals/` counterpart -
  moved to `references/acceptance-criteria.md` rather than deleted. If the orchestrator's
  intent for skills with no source `evals/` is to drop inline AC lists entirely, this is the
  file to remove.

### Nothing was dropped

Every rule in the source `SKILL.md` - including the ones explicitly called out as
easy-to-lose (upfront sweep count and its exclusivity, exhaustion-is-about-trying not
spending, the once-per-question-per-circle deliberate reopen with its reduced cap, logging
every count used, the resume-skips-fetch-not-Step-0 rule, circle 4's name-a-source
requirement, circles 1/2 never skipped) - has a home listed above. Model names, the fixed
Atlassian/Slack ids, and the webhook URL moved to `profiles/extract/idea-deep-dive.local.md`;
tool names (`getJiraIssue`, `slack_read_canvas`, and so on) were replaced with category verbs
from `tool-capabilities.md` throughout.

### Open questions for the orchestrator

- The sweep-dispatch-count decision above (3 vs. 4) is the one genuine judgment call in this
  port; everything else was a mechanical relocation or a direct instruction from the task
  brief.
- `codebase.access`'s enum in `profile-schema.md` is `device_bridge | local | none`; the
  source's fixed value ("device bridge only ... M365/SharePoint fallback ... is for the
  vault, and does not substitute for the codebase") extracts cleanly to `device_bridge` with
  no schema gap, but the specific "does not substitute" caveat is prose-only (in
  `references/circles.md` and `write-up.md`'s storage handling), not a separate profile flag
  - flagging in case a future skill needs that distinction as a queryable key rather than
  prose.
- This skill has no `## Handler mode` heading by design - `handler-contract.md`'s "Adding a
  handler" section names `idea-deep-dive` explicitly as one of the three idea-pipeline
  skills deliberately excluded from hub dispatch (schedule-driven, not tick-driven). No
  action needed; noted here so a reviewer does not read the absence as an oversight.

## 2026-09-22 orchestrator sign-off: the sweep is four dispatches, not three

The port asked whether extending the upfront sweep from three dispatches to four, to take in
the notetaker, contradicted a rule it had been told not to lose.

It does not, and the port read it correctly. The invariant was never the number three; it
was **one dispatch per cheap source, covering every seeded question at once, and that being
the sweep's entire allowance for those questions**. The notetaker is a cheap source in the
same circle as chat and email, so it gets one dispatch on the same terms. Four is the right
number now, and it would be five if another cheap source joined that circle later.

What would have been a real loss is a per-question notetaker search inside the sweep, or the
sweep quietly becoming a second allowance for questions it already covered. Neither
happened, and the count logging was extended to four so the run stays auditable.

The acceptance criteria were also right to keep. No source evals existed, so that section is
the only executable statement of what a correct run looks like; dropping it for lacking an
evals directory would have removed the skill's own self-check.

## 2026-09-25 canvas redesign (1.1.0): every tick means yes, do it

Forks now reach the board as option groups (`<key>/q1a`, `q1b`, …) inside the idea's
block, and a stuck or paused question is one line the user edits with an answer and
ticks. Both dispatch `idea-scout`'s `decide` mode, which writes into this skill's note and
clears Run state, so a resume never re-asks a decided question. The webhook is gone;
`runs.idea-deep-dive` carries the run to the briefing. No selector was added, per the
redesign's constraints; the key still comes from the caller, and a run with no key
records `quiet`.
