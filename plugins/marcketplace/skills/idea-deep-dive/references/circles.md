# The four circles, in order

Cost order as much as an epistemic one: `kb` and `people` are near-free structured lookups;
`code` and `web` are the expensive circles. Caps below come from
`budgets.idea-deep-dive.circle_caps` (`kb`, `people`, `code`, `web`); defaults shown are the
source install's own values.

## 1. `kb` - my knowledge, the knowledge base

Prior research on this idea, adjacent decisions already recorded, the product/service map for
feasibility context, and the idea's own description and comments already in hand. Never
skipped - cheapest, most authoritative. Cap: `circle_caps.kb` searches (default 2) per
question, against `kb.paths.research` and whatever else `kb.conventions_file` points a search
at. Sourced answer -> record in "Resolved findings" (`write-up.md`), mark resolved.

## 2. `people` - what people have told me

Chat, email, and the notetaker, as three peer platforms subject to the same per-platform cap
(`circle_caps.people`, default 2 searches each). Never skipped.

- **Chat and email** - canvases, channels, threads, DMs, messages. Targeted search by topic
  and named people, cross-checked against `kb.people_file` before naming anyone.
- **Notetaker** - meeting transcripts within `notetaker.lookback_days`. Meetings are often
  where a question was already answered out loud and never written down; treat a transcript
  hit exactly like a chat or email hit - same cap, same sourcing requirement (meeting title
  and date stand in for a permalink).

Sourced answer from any platform -> record, mark resolved. A platform this profile has not
configured (`profile.tools.notetaker` unset, for instance) degrades to unavailable for that
platform only, per `tool-capabilities.md` - the other two platforms in this circle still run.

## 3. `code` - the codebase

Feasibility-shaped questions only - what is actually built, how a flow really works, what a
data model or API can and cannot do. Cue words: *built, supports, implemented, API, schema,
data model, capacity, currently does*. Cap: `circle_caps.code` searches (default 3),
symbol/filename before full-text; read only the matched region, never a whole file. Unavailable
for the whole run (see `loop-protocol.md` Step 0, point 3) -> say so once; this is "could not
check", distinct from "checked, no answer" - move straight to the stuck-check for any question
that needed it. Sourced answer -> record `{answer, source = repo + path/line or commit}`,
mark resolved.

## 4. `web` - competitors in the market

Market-shaped questions only - positioning, what other products train users to expect,
competitor capability, licensing/commercial terms set by a third party. Cue words: *compete,
market, expect, industry-standard, what do others charge/offer, licence permits*. Cap:
`circle_caps.web` searches (default 4). Every answer names a competitor or source-holder plus
what they do or permit plus a citable source; if the searches run out without a citable
source, that is an unresolved question, not an unsourced impression written down anyway.

## Applicability

A question's cues can point at only one of `code`/`web`, at both, or at neither:

- **Only one applies** -> try only that one.
- **Both plausibly apply** (e.g. part "what does our system do", part "what does a third
  party's terms allow") -> try `code` first, then `web` if `code` did not resolve it -
  ground-truth-about-us before external context - rather than picking one and forfeiting the
  other.
- **Neither plausibly applies** (pure archaeology, or nothing external or internal could
  settle it) -> do not guess and burn a search; that absence of an applicable circle is itself
  what the stuck-check names as the gap.

Circles `kb` and `people` are never skipped, for any question.
