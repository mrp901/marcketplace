# Specificity test and guardrails

Step 6 of `SKILL.md`. Two separate discriminators; do not conflate them.

## 1. Under-specified vs over-specified

Two failure modes exist, and pulling too hard on either costs points. This is not one knob
to crank up.

- **Under-specified**: something occurs once or twice in the product and needs the actual
  instance named (which column, which field, which state) even when its content is
  legitimately generic. "Hovering a lane shows supporting detail" needs to become
  "hovering the Depot ID column shows supporting detail". The tooltip's content stays
  generic; only the instance gets named.
- **Over-specified**: something that recurs everywhere, or where the user has already
  confirmed parity with an existing pattern, does not need a mechanism invented under it.
  Once an answer establishes "same as the existing pattern", stop. Do not ask a follow-up for
  the mechanism behind a confirmed parity answer, and do not write a bespoke mechanism
  yourself either.

The discriminator: are you missing *which instance* this applies to, or *a mechanism that a
confirmed parity answer already made unnecessary*? The first needs a question or a name; the
second needs you to stop.

**Never use "same as the existing pattern" as a stand-in for an unconfirmed mechanism.**
The phrase is only honest once parity is confirmed, either by the user or by something you
have verified is a real, recurring convention. Writing "via the same badge other carriers
already use" when you have never confirmed the badge exists invents a mechanism dressed as
a resolution. That is worse than leaving the bullet openly vague, because it reads as
settled when it is not. If you cannot confirm it, ask, or write it as an open question in
the ticket.

## 2. Decide it yourself (guardrail) vs ask

Some blind-pass findings are not a specificity problem at all; they are a missing defensive
guardrail (delivery-failure tracking, tenant isolation, not losing data on a rename). The
test is not vague-versus-abstract. It is: **does the answer depend on a product or business
choice that could reasonably go more than one way, or is it implementation diligence any
competent build would need regardless of how other choices land?**

- "Should a failed alert delivery be silently swallowed?" has one sane answer whatever
  threshold value gets picked. Write it in as a guardrail; do not ask.
- "Should the alert show dollar cost or just usage?" could go either way depending on
  product intent. Ask.

When a finding could plausibly be either, treat it as a decision and ask. Guardrails are for
cases where asking would only delay an obvious answer.

## 3. Resolve, do not park

Where the blind pass finds a gap, the default is to close it in this pass: by a question in
the batch, by a guardrail you add, or by deleting a bullet that describes a scenario that
cannot occur. A gap left in the ticket as "TBD" is a last resort, only for a decision that
genuinely belongs to someone not in the conversation, and it is stated as an open question
in the ticket with an owner if known.

## 4. Splitting a story

When a story carries more than one customer outcome, split it. A child story is the
smallest shippable customer outcome: something a customer or user can see, use or be
protected by on its own. Never split by technical layer (API, then UI, then migration);
a layer is not shippable and does not deliver anything to anyone. Check the split against
the parent epic's existing children first, per the hierarchy convention found in Step 3.

## 5. Why the blind pass is blind

Step 4 of `SKILL.md`. Reviewing your own writing in the same context you wrote it in misses
a specific class of gap: unstated dependencies, contradictions between two ACs that each
look fine alone, and assumptions about existing features that were never verified. A blind
pass with fresh eyes over just the text catches these; a self-review by whoever just wrote
or read the answers already has the answer in mind and stops looking.

The story line is included, not just the ACs. It usually carries the actual goal in one
sentence ("so I'm not surprised by penalty charges"), and that goal is often what lets the
blind pass catch a gap the ACs alone do not reveal: ACs that are internally consistent
about late-delivery *rate* thresholds while the story's real goal is about penalty
*charges*, a gap invisible without the "why" line.

## 6. Sorting what survives the diff

Step 5 of `SKILL.md`. Two buckets:

- **Genuinely undecided**: a real product or UX decision nobody has made yet (what happens
  when two carriers try to link the same depot account). Ask about these.
- **Legitimately abstract**: a reference to existing or contextual behaviour that does not
  reduce to a fixed list ("the standard lane-table column rules" when the real answer is "it
  depends on the view"). Do not push for a fixed answer here; apply the test in section 1.

On a from-scratch draft (New mode), or a ticket with no parent epic, no sibling tickets and
no relevant prior session context, the diff against what is decided will often come back
empty: there is nothing yet to have settled anything. That is the expected result of a
truly cold start, not a broken step. It means Step 5 has to do more work on its own,
sorting the blind pass's raw findings by judgement rather than by "was this already
decided"; the guardrail discriminator in section 2 is the judgement call that comes up
most.

## 7. Voice

Step 8 of `SKILL.md`. Match the register of the story itself, not a generic PM template:
direct, plain sentences, guardrails stated as consequences ("not a blank cell that looks
broken") rather than abstract requirements ("must handle empty states gracefully"). When
summarising what you changed and why, be terse and thematic: a short list of what moved and
the reason, not a re-explanation of the whole ticket. If something regressed from a prior
pass, say so plainly instead of hedging around it.
