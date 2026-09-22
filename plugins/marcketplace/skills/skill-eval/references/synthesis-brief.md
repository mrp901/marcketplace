# Synthesis brief

Full detail for `SKILL.md` Steps 2-3, interactive path.

## Step 2 - capturing the eval

**Inputs.** Required: the skill name (infer from context rather than asking) and the
evaluation feedback (free-form or structured, e.g. "Dimension X: 6/10 because Y"). Usually
already in context: the output being evaluated - if not, ask to paste it. Optional but
high-value: examples of better or worse wording, and one sentence of task context on what
the skill was asked to do. Chase optional inputs only when their absence would weaken
synthesis, and do not turn this into an intake form - if the triggering message already
said everything needed, skip straight to the confirmation below.

**The confirmation.** A short structured read of what the user said, not a transcript:

- The dimensions they used, in their words. If they scored things, keep the scores. If
  they did not name dimensions, name the themes extracted and mark them as inference, so
  they can be corrected.
- What passed - explicitly, since it tells synthesis what not to touch.
- What failed, each with the specific evidence given.
- Anything unsure, as a question.

**If the feedback is vague** ("it's not quite right", "the tone is off") - stop and ask
before spawning anything, with narrow questions anchored to the actual output: "Which part
specifically?", "Can you show me how you'd have written that line?", "Is this a one-off for
this input, or does it happen every run?" That last question matters most: a one-off is not
a skill defect and should not become a rule.

## Step 3 - the synthesis subagent

Give the fresh critic-tier subagent: the current `SKILL.md` in full plus any bundled files
the feedback touches, the output that was evaluated, the user's feedback verbatim
(including scores and rewritten examples - never paraphrased, the exact words are the
signal), the one-sentence task context, and any user or org context that matters to the
skill's domain.

**Instructions for the subagent**, verbatim:

> You are amending an existing skill, not writing a new one. Produce a revised `SKILL.md`
> that addresses this specific feedback and changes nothing else.
>
> 1. **Amend, don't replace.** Preserve the skill's original intent, structure, section
>    order and voice. Change only the sections the feedback actually touched. A section
>    that drew no comment comes through byte-identical.
> 2. **Ground every change in the feedback.** For each change, point at the sentence that
>    demanded it. If you can't, don't make it.
> 3. **Show before/after.** Where the user gave a concrete example of better wording, put
>    that example into the skill as a good/bad pair it can teach from. Instructions that
>    show beat instructions that assert.
> 4. **Group and prioritise.** Several things at once - voice, structure, one section -
>    become separate grouped changes, ordered by how much each affected output quality.
>    Say which are load-bearing and which are minor.
> 5. **Distinguish rules from one-offs.** A complaint about this run is not automatically a
>    rule for every run. If a piece of feedback looks input-specific, say so and propose it
>    as a question rather than writing it in.
> 6. **Don't inflate.** A paragraph per complaint bloats the skill until nothing in it is
>    salient. Prefer sharpening an existing line over appending a new one. If a new
>    constraint contradicts an existing line, edit that line - don't leave both.
> 7. **Protect what worked.** Anything praised is load-bearing; a fix for one dimension must
>    not quietly break it.
>
> **Return:** a change summary (one entry per grouped change, the feedback it answers, the
> section it touches, a before/after snippet); the complete revised `SKILL.md`, ready to
> save; and open questions - anything ambiguous, anywhere you guessed, or anywhere the
> feedback might hurt the skill elsewhere. Say so plainly; the user would rather be argued
> with than agreed with.

## Step 4 - checkpoint

Show the change summary, ask "Did I get this right?" If synthesis missed the point -
solved a different problem, over-corrected, wrote a rule where the user meant a one-off,
rewrote something they liked - take the correction and re-run Step 3 with the misread
named explicitly. Cap at two re-synthesis cycles; past that, stop and show the best draft
with the specific unresolved points, so the user can edit directly.

## Edge cases

- **Skill name doesn't exist.** List the closest matches and ask which was meant; if one
  was invoked earlier, name and confirm it.
- **Can't read the target skill** (permissions, path not found). Say so, name the paths
  tried, and ask the user to paste contents. Never synthesise against an unread skill -
  that is a replacement posing as an amendment.
- **Feedback is entirely positive.** No changes needed, and saying so is valid. Offer to
  write what worked into the skill as a worked example.
- **Feedback contradicts itself**, or the skill's purpose. Surface the tension plainly
  rather than picking a side silently.
- **The problem isn't the skill.** Thin input or a bad run, not the instructions. Say so.
- **Feedback targets a bundled file**, not `SKILL.md` - a reference doc, script, or
  subagent prompt. Amend that file instead and propose the whole package.
- **The skill is a draft, not installed.** Read it from wherever it lives and propose the
  revision back the same way.
