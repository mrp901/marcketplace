# Worked example - interactive path

Against `profiles/example.md` (Northwind Logistics, Freight Ops). The run being evaluated:
`idea-ticket` produced an ideas-board ticket for a dock-scheduling dashboard problem.

## Step 2 - captured eval

Priya scored six dimensions and gave prose on each. Confirmation back to her:

> **What you rated**
>
> - Structure 9/10 - title and section order right.
> - Voice 8/10 - "sounds like me, one hedge in the Context para."
> - Zero-context clarity 9/10 - "naming the yard code and shift is what makes it land."
> - **Options parallelism 4/10** - "all three options read like the same idea at different
>   altitudes. I couldn't see the trade-off."
> - Concision 7/10 - "the ask restates the Context."
> - Register 9/10 - open questions read as scope, not risk.
>
> **Working, don't touch:** the module-contrast framing in Context, the `[Freight] <problem>`
> title shape.
>
> **The load-bearing failure:** options parallelism. You gave a rewrite showing what you
> wanted.
>
> One check - is the ask/Context overlap a one-off on this input, or does it happen most
> runs?

Priya: "happens most runs."

## Step 3 - synthesis (critic-tier subagent)

Given the skill, ticket, feedback and the brief in `synthesis-brief.md`. Returned three
grouped changes.

## Step 4 - change summary shown to Priya

**1. Options parallelism (load-bearing - the 4/10)**

Answers: *"all three options read like the same idea at different altitudes."* Touches
the Options section.

Before - the rule was asserted but never demonstrated:

> Options - 2-3 low-effort ways to get there, written so the reader can see the trade-off.

After - the rule now teaches from Priya's own rewrite, with the failure mode next to it:

> The point of this section is that a reader can see the trade-off at a glance, and that
> only works if the options are written in parallel: **same sentence shape, same level of
> detail, only the genuinely different part changes.**
>
> Good - the difference jumps out because nothing else moved:
> > - **Compare this shift's dock throughput to the same shift last week** (Tue AM vs Tue AM).
> > - **Add a yard-pair filter** and then compare throughput within the same yard pair only.
> > - **Keep the current comparison** and just label it "vs same shift, prior week".
>
> Bad - same three ideas, each pitched at a different altitude:
> > - Compare this shift's throughput to the same shift last week.
> > - Introduce a more flexible period-selection model giving users control over the
> >   comparison basis.
> > - Labelling change.
>
> If two options are hard to tell apart, that's the signal: sharpen until the difference is
> visible, or drop one because it isn't a separate option.

Also added as an audit criterion: *"Options are parallel - if a reader would have to ask
'how is 2 different from 1?', this fails."*

**2. Restatement between Context and the ask (recurring - 7/10 concision)**

Answers: *"the ask restates the Context."* Confirmed recurring, so written in as a rule:
one line added to the "cut the AI tells" list - *"Restating the ask in the Context, then
again in the Options. Say it once."*

**3. Hedging (minor - 8/10 voice)**

Answers the one hedge Priya flagged. The existing hedges rule was right and just wasn't
being enforced, so no new text - the audit rubric's voice criterion tightened to *"name
any specific tell you find"* rather than pass/fail.

**Not changed:** Context framing, title shape, register, related-ticket handling - all
scored 8+ with no criticism.

**Open question raised by the subagent:** the parallelism rule and the "cut the section if
there's only one sensible approach" rule can pull against each other - sharpening two
similar options into genuinely distinct ones sometimes means admitting there's only one.
Flagged for Priya rather than resolved silently.

## Then

Priya confirmed the read was right. The revised `SKILL.md` was sent through the session's
file-sending capability, name unchanged, for her to review and save herself.

---

# Worked example - run with no target

Sunday's `skill-health-check` scored `kb-note` red (`tally.kb-doc.edited` at 6 against 9
ticked, three voice-ledger entries all in the `teammate_chat` register) and put one line
on the board: `(shc:260921-2) 🔴 kb-note scored red: 6 of 9 notes edited before you kept
them. Run skill-eval on it? · .utility/skill-health/kb-note.md`. Priya ticked it; the
Router wrote `↳ router: queued for your next skill-eval run`.

On Tuesday Priya runs `/marcketplace:skill-eval` with no target. The skill reads the board
once and lists one candidate: `kb-note · 6 of 9 notes edited before kept ·
.utility/skill-health/kb-note.md`. Priya picks it.

**Starting feedback** is the health log entry plus the three ledger entries it cites, all
diffing to the same shape: each kept version drops the note's closing restatement
sentence. Step 2 reflects that back; Priya confirms and adds "and it keeps opening with
'This note records…', which I always cut." Two patterns, both grounded.

**Synthesis** sharpens `kb-note`'s existing "what this records" guidance rather than adding
a new rule, adds the opener as a good/bad pair, and names the sample size. Priya confirms
the change summary; the revised `SKILL.md` is handed back as a file.

**Closing the loop:** one `state.outcomes` entry, `{tag: shc:260921-2, handler:
skill-eval, status: done, report_line: "skill-eval run on kb-note: dropped the closing
restatement and the stock opener", recorded_at: 2026-09-23T10:40:00+10:00}`. The next
briefing closes the `shc:` line as done by skill-eval. Nothing was installed by this
skill.
