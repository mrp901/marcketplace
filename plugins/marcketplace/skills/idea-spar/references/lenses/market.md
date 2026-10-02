# Lens: market

What is out there, whether it matters to our positioning, and whether it changes the
outcome. A list of competitors who also have the feature is not market research; it is
the starting material. The output is what that means for this decision.

## Inputs

The known packet, `profile.org.product_scope` and `profile.org.modules_context` (our
positioning, quoted, never paraphrased), then at most `budgets.idea-spar.web_searches`
targeted `web: search` calls, each a `budgets.models.search`-tier subagent that returns
vendor, what they ship, how they frame it, and the source URL.

## The three questions, for every vendor or pattern found

1. **What's out there.** Who ships this or something close, and how they frame it (their
   words, not ours). Name the vendor and the source.
2. **Is it relevant to our positioning?** Compare with the positioning line. A vendor
   selling to a different buyer, at a different price point, or for a different job is
   noise; say so in one clause and move it to "Checked, no bearing".
3. **Does it change the outcome?** Exactly one of:
   - **Table stakes** - buyers will expect it because peers we compete with have it; not
     building it costs deals. Say which deals or segment.
   - **Differentiator** - nobody in our segment does it well; building it is a story.
   - **Trap** - others built it and it didn't land (deprecated, buried, complained about).
   - **No effect** - true but irrelevant to the decision; goes to "Checked, no bearing".

Only table stakes, differentiator and trap become findings.

## Shape

The output contract in `SKILL.md`. Each finding: the vendor fact · the source URL · **so
what:** the classification above and the decision it moves ("table stakes against the two
vendors in our last three lost deals - build it, but don't market it").

Never state a vendor capability the search didn't return. A vendor known from memory but
not confirmed this session is written as "unconfirmed" or left out.

## Worked example (fictional, against `profiles/example.md`)

> **Verdict** - Table stakes in mid-market freight visibility; build it plainly, don't lead
> with it.
>
> - Two visibility vendors in our segment ship plan-variance alerts on by default, framed
>   as "exceptions" · vendor product pages (links) · **so what:** table stakes; the
>   differentiation case in the ticket doesn't hold, so it shouldn't carry roadmap weight.
> - One vendor lets customers set the threshold per lane and markets that as the feature ·
>   vendor docs (link) · **so what:** moves the threshold fork toward per-customer.
>
> **Checked, no bearing** - an enterprise suite's ETA prediction (different buyer).
> **Would change my mind** - evidence our buyers rank alerts below reporting accuracy.
