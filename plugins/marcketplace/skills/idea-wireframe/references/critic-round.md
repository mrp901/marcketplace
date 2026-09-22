# Render and criticise

Full detail for `SKILL.md` Step 5.

## Render and self-check - required, not optional

Screenshot the built HTML (a headless browser, full page) and check the image yourself
before anything else happens: markers land on the elements they describe, nothing is
clipped, the side rail stays aligned. Fix anything wrong before moving on.

## The critic round

The build itself runs on whatever model the current session is on. The critic round always
escalates to `profile.budgets.models.critic` (per `../../../shared/model-tiers.md`), spawned
as a **genuinely fresh subagent** - the screenshot, screenshots of the last two or three
prior wireframes from `profile.kb.paths.prototypes`, and the idea's one-line problem
statement. Never the HTML source, never this run's build reasoning, never earlier
iterations. Judgement is the one place worth paying for the stronger tier, and it stays
cheap because the critic only ever sees images and a one-line problem, never raw source.
Inheriting the build's own reasoning would hand the critic the exact anchoring effect it
exists to escape. If the critic tier is unavailable, fall back to the strongest available
model and say so plainly on the surface line rather than silently downgrading.

**Label the prior shots as previous attempts, not exemplars.** If every one of them shares
the same shape (the same frame, the same artboard count), an unlabelled comparison
penalises this run for diverging from that shape, which is the opposite of the point. Once
the taste log carries real reactions to specific wireframes, rank against the ones the user
actually argued with instead of an arbitrary recent set.

Ask the critic to **rank**, not to score against a stated bar: which of the shown
wireframes would the user argue with hardest, which reads as filler, and why. Don't tell it
what a passing bar looks like.

## Revision - at most once

Revise only if this run's wireframe ranks last **and** the critic calls it filler - rank
alone, at this sample size, is noise. When both conditions hold, change the frame or the
fork being resolved, not the polish, then ship regardless of the second round's outcome.
One revision, ever, in a single run.
