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

# Worked example - unattended, proposal-driven path

kb-dream's monthly registry review raises `state.proposals: [{kind: skill_eval, category:
kb-doc, candidate: kb-note, opened_at: 2026-09-01, status: open}]` - `tally.kb-doc.edited`
has climbed to 6 against 9 ticked. Priya ticks the Dream log/actions line accepting it; the
hub dispatches `skill-eval` mode `eval`.

**Tally read:** 6 of 9 `kb-doc` dispatches were edited before being kept. **Voice-edits
sample:** three reachable entries, all against `kb-note`'s `teammate_chat` register,
diffing to the same shape - each kept version drops the note's closing restatement
sentence.

**Pattern converges** (2 of 3 is enough to name, not enough to call universal): synthesis
runs with feedback composed as "3 of 3 sampled edits to `kb-note` drafts removed the note's
final summarising sentence; too small a sample to be certain it is universal." Revision
sharpens `kb-note`'s existing "what this records" guidance rather than adding a new rule,
and the change summary names the small sample size explicitly.

**Draft written** to `profile.kb.paths.drafts`, `status: draft`, `supersedes_on: proposal
accepted or rejected`. Return JSON:

```json
{
  "status": "done",
  "report_line": "drafted a kb-note revision from 3 sampled edits · dropped closing sentence pattern · <draft link>",
  "artefacts": [{"kind": "skill_eval_draft", "ref": "Drafts/2026-09-22-kb-note-eval-proposal.md"}],
  "next_action": null
}
```
