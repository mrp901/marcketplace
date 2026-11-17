# Session eval

The one place the user rates a session themselves. Every other signal the plugin reads
(corrections, edits, ticks, outcomes) is behaviour the user left behind; this is their direct
verdict on whether the session landed and was worth the time, captured while they still
remember it. skill-health-check reads it as evidence
(`../../skill-health-check/references/evidence-gathering.md`, "Session evals") and kb-dream
reads it for recurring friction (`../../kb-dream/references/signal-extraction.md`).

## When to ask

All of these, or don't ask:

- Log mode, not capture mode.
- Interactive: no `unattended` token (`../../../shared/onboarding.md`, Step 0).
- The note is for the live conversation. An archived transcript from the pending queue is
  never rated, even in an attended drain: a rating given hours or days later is a guess.
- The gate passed and a note is being written. With no note there is nowhere to record it.

Ask once, after gathering (Flow step 2) and before writing, in a single call to the
interactive question tool, never as a markdown list. It should take under 15 seconds.

## The questions

| Header | Question | Options (single-select unless noted) |
|---|---|---|
| Landed | Did this session get you what you came for? | Yes, fully · Mostly · Partly · No |
| Time | Was it worth the time it took? | Faster than doing it myself · About right · Took too long · Not worth it |
| Friction | Where did it cost you? (multi-select) | None · Too many questions · Rework or wrong assumption · Slow tools or retries |

Don't mark any option as recommended: the user rates, the skill doesn't lead.

**Free text.** The tool's built-in free-text option replaces a pick rather than adding to
one. A question answered that way is recorded as `other` (`**Landed:** other`) and the text
goes, verbatim, in **Said**, prefixed with the question's header when more than one question
was answered in free text (`Landed: "..."`). Never map free text onto an option label.

## Recording

The note's `## How it went` section, shape in `note-template.md`. Use the option labels as
given, lower-case, so a reader can match them as text: `**Landed:** mostly · **Time:**
took too long · **Friction:** rework or wrong assumption, slow tools or retries`.

**Skills run** lists the plugin skills actually invoked in the session (by skill name, from
the conversation), so a rating can be attributed. It never lists session-log itself, which
runs every eval and would make every rating ambiguous. A session that ran none says `none`.

**A second log run in the same live session** updates the note in place
(`proposed-followups.md`). Ask the eval only if the note has no `## How it went` yet;
otherwise keep the section as it is.

If the user dismisses or skips the call, write nothing: no section, no placeholder, no
inferred rating. A free-text comment about how the user's writing should read also goes in
`## Voice and tone feedback`, per that section's rule; a comment correcting a fact also goes
in `## Facts and corrections`.
