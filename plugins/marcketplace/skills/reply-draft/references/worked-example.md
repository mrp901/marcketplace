# Worked example

Against `profiles/example.md` (Northwind Logistics, Freight Ops).

**Dispatch payload (abbreviated):**

```
item:
  tag: pr:260922-05
  category: email
  text_as_ticked: draft a reply to Owen's email asking about the multi-yard allocation timeline and whether we can join their Friday call
  ref: <link to an email thread with Owen Fairclough, Support Lead>
mode: draft
output_location: kb.paths.drafts
```

**Fetched source (the thread, most recent message):** Owen: "Two things - when's
multi-yard allocation landing, our customer's asking, and can someone from your side join
our Friday 2pm call with them to talk through it directly?"

**Parts of the ask found:** (1) multi-yard allocation timeline, (2) can someone join
Friday's call.

**Gap check:** the timeline is a known fact - deferred this quarter, per the kb decision
note captured earlier the same day (see `kb-note`'s worked example). Whether someone can
join Friday's call is a commitment only the user can make - marked as a gap.

**Register:** `customer_facing` - Owen is internal, but the reply is about representing
the team on an external call and the thread reads as customer-adjacent in tone; picked
`customer_facing` over `teammate_chat` per the mixed-audience rule, since the content of
the reply is what Owen will relay to the customer.

**Draft written:**

```
Hi Owen,

Multi-yard allocation is deferred out of this quarter's dock-scheduling release - we're
keeping the single-yard rewrite on track instead. Happy for you to pass that along.

[[GAP - confirm whether Priya or Tomasz can join Owen's Friday 2pm customer call]]

Let me know if there's anything else the customer needs ahead of Friday.
```

**Draft note**, `Inbox/2026-09-22-reply-owen-multi-yard-timeline.md`:

```yaml
---
type: Draft Reply
title: Reply drafted - multi-yard allocation timeline for Owen (22 Sep 2026)
description: Reply to Owen Fairclough on the multi-yard allocation timeline and Friday's customer call.
tags: [email, customer_facing, freight, dock-scheduling]
status: draft
generated: { by: reply-draft, at: 2026-09-22T09:41:00+10:00 }
---

# Reply drafted - multi-yard allocation timeline for Owen (22 Sep 2026)

**Source:** email thread with Owen Fairclough, 22 Sep 2026.

**Register:** customer_facing

## Draft

Hi Owen,

Multi-yard allocation is deferred out of this quarter's dock-scheduling release - we're
keeping the single-yard rewrite on track instead. Happy for you to pass that along.

[[GAP - confirm whether Priya or Tomasz can join Owen's Friday 2pm customer call]]

Let me know if there's anything else the customer needs ahead of Friday.

## Gaps

- Who (if anyone) can join Owen's Friday 2pm customer call - a commitment only the user
  can make.
```

**Return JSON:**

```json
{
  "status": "done",
  "report_line": "drafted a reply to Owen · customer_facing · 1 gap marked · <draft link>",
  "artefacts": [{"kind": "reply_draft", "ref": "Inbox/2026-09-22-reply-owen-multi-yard-timeline.md"}],
  "next_action": null
}
```
