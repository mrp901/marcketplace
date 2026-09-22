# Reply shapes and the draft note

## Email vs chat-thread reply

Both go through the same Flow, but the drafted text itself differs in shape:

- **Email.** Carries a suggested subject line (`Re: <original subject>`, unchanged unless
  the thread has drifted onto a different topic, in which case the new subject is named
  and the change is called out in the draft note, not silently substituted). A greeting
  line and a sign-off follow whichever the register note's exemplars show - not a default
  "Hi" / "Best" invented from nowhere.
- **Chat thread.** No subject line, no formal greeting or sign-off unless the register's
  own exemplars use one (an exec-update chat thread might; a teammate_chat one usually
  won't). Shorter by default - chat replies in the exemplars run shorter than email
  replies in the same register, and the draft should too.

## The draft note

Frontmatter:

```yaml
---
type: <registered type - check kb.types_registry live for a "Draft Reply"-shaped type
  before asserting one is missing; add one with a one-line justification if genuinely
  none exists>
title: Reply drafted - <short description of the thread's topic> (<dated, DD Mon YYYY>)
description: <one sentence: who this replies to and about what>
tags: [email, <register used>, <one or two topical tags>]
status: draft
generated: { by: reply-draft, at: <ISO 8601> }
---
```

Never write `verified` - no human has reviewed this draft yet.

Body:

```markdown
# <title>

**Source:** <email thread | chat thread> with <who>, <ISO date of the latest message
read>. <If the thread cap trimmed anything: "N earlier messages not read; skim before
sending if this runs deeper than shown here.">

**Register:** <register used>

## Draft

<the drafted reply text, in full, exactly as it would be pasted or sent - including any
`[[GAP - ...]]` markers left in place>

## Gaps

<one line per `[[GAP - ...]]` marker in the draft, or "None" if the reply needed no gap>
```

Index line and log line follow `kb-conventions.md`'s maintenance contract exactly, same
as any other kb write - one index line under `kb.paths.drafts`'s (or the override
folder's) `index.md`, one log line under today's date heading in `kb.paths.log`.
