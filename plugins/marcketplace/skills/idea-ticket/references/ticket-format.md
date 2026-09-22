# Ticket format

## Structure

**Title:** `<profile.org.product_tag> <short, concrete problem statement>` - describes the
problem, not the fix (e.g. `[Cloud] Prior-month comparison should be like-for-like MTD, not
full month`, not `[Cloud] Fix MTD bug`).

**Context** - What's happening, why it's wrong or confusing, and who it misleads. Ground it
in the real screen details from Step 1, and in the product's own vocabulary - name the
actual module, screen, tile and figure. Someone who has never opened the screen should
finish this section knowing exactly what's wrong.

Write it the way the user talks. Present tense, concrete nouns, direct statements of fact:

> In TEM and Mobile we don't have daily data, but for Cloud we do. So the Cloud Spend tile
> comparing month-to-date against the *whole* of last month is comparing 12 days to 31.

Not:

> Since we get daily data, we can do better than the current comparison approach.

The second one says nothing a reader can hold onto. Name the modules, name the tile, use
the numbers.

**The ask** - One or two sentences, bolded, stating the ideal end state plainly. This
describes what "fixed" looks like, not a spec for how to build it.

**Options** - 2-3 low-effort ways to get there. The point of this section is that a reader
can see the trade-off between the options *at a glance*, and that only works if the options
are written in parallel: same sentence shape, same level of detail, only the genuinely
different part changes. Let the contrast do the work.

Good - the difference jumps out because nothing else moved:

> - **Compare MTD to the same days of the previous month** (1-12 Sep vs 1-12 Aug).
> - **Add a full date range picker** and then compare the range to the equivalent previous
>   range.
> - **Keep the current comparison** and just label it "vs full previous month" so it isn't
>   misread.

Bad - same three ideas, but each is pitched at a different altitude, so the reader has to
work out whether option 2 is even a different thing from option 1:

> - Compare MTD to the same days of the previous month.
> - Introduce a more flexible period-selection model that gives users control over the
>   comparison basis.
> - Labelling change.

Rules for this section:

- Each option starts with a bolded verb phrase saying what would be built, then one clause
  on what it gets. Nothing longer.
- If two options are hard to tell apart, either sharpen the wording until the actual
  difference is visible, or drop one because it isn't a separate option.
- Frame them as options, not a commitment - "here are a few ways we could get there", never
  "we will do X".
- Cut the whole section if there's really only one sensible approach. Don't pad it to look
  thorough.

**Open Questions** - Real unresolved scoping decisions only, asked as questions about scope
("does this affect the forecast widget or just MTD?"), never as risks or blockers ("Risk:
billing-cycle misalignment may block implementation" is not the register). Omit the heading
entirely if there genuinely aren't any - a forced Open Questions section reads as filler.

**Research leads** *(optional)* - One or two short pointers on where a fuller investigation
should look, phrased as a pointer rather than a finding. One line, no table, no analysis.

**Related** - Cross-link any sibling idea found in Step 2, with a few words on how it
relates. A pointer for the reader, not a dependency.

Keep the whole thing to about a screen's length. If a draft is running past that, it has
crept into scouting-skill territory - cut back to the pointer, not the finding.

## Cut the AI tells

The draft has to read like the user wrote it in five minutes, not like a model produced it.
Specific things to strip, on top of `../../../shared/voice.md`'s shared avoid-list:

- **Abstraction where a fact belongs.** "We can do better" -> say what better is. "Users
  may be confused" -> say who, looking at what, and what they'd conclude.
- **Hedges.** "It's worth considering", "this could potentially", "arguably". If it's worth
  saying, say it.
- **Framework nouns.** Opportunity, alignment, stakeholder, value proposition, holistic,
  leverage (as a verb), surface (as a verb), robust, seamless. Also "delve", "underscore",
  "it's important to note".
- **Boilerplate section headers** beyond the ones above. No "Problem Statement", no
  "Proposed Solution", no "Success Criteria".
- **Manufactured balance.** Not every point needs a counterpoint. "While X, it's also true
  that Y" is usually one sentence pretending to be two.
- **Restating the ask in the Context, then again in the Options.** Say it once.
- **Em-dash-heavy, three-clause sentences.** Short declaratives are the default register.
