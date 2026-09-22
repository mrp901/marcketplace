# Worked example

Against `profiles/example.md` (Northwind Logistics, Freight Ops).

**Dispatch payload (abbreviated):**

```
item:
  tag: pr:260922-02
  category: kb-doc
  text_as_ticked: capture that dock-scheduling won't support multi-yard allocation this quarter
  ref: <link to a Slack thread in #freight-ops-eng>
mode: capture
output_location: kb.paths.inbox
```

**Fetched source (the thread):** Tomasz: "confirmed with the team, multi-yard allocation
is not making this quarter's dock-scheduling release - we're deferring it to keep the
single-yard rewrite on track. Priya's aware." Priya: "yep, correct, flagged it in the
roadmap review too."

**Classification:** decision-shaped - a choice was made (defer, not build) with a stated
reason.

**Duplicate check:** one `kb: search` on "multi-yard allocation" against
`Product/FreightOps/Research/` and `Inbox/` turns up nothing recent. Proceeds to write.

**Note written**, `Inbox/2026-09-22-multi-yard-allocation-deferred.md`:

```yaml
---
type: Decision Record
title: Multi-yard allocation deferred this quarter (22 Sep 2026)
description: Dock-scheduling will not support multi-yard allocation this quarter, deferred to protect the single-yard rewrite.
tags: [kb-doc, freight, dock-scheduling]
status: draft
generated: { by: kb-note, at: 2026-09-22T09:14:00+10:00 }
---

# Multi-yard allocation deferred this quarter (22 Sep 2026)

**Source:** #freight-ops-eng thread, Tomasz Wieckowski and Priya Kanth, 22 Sep 2026.

## Decision

**Multi-yard allocation is deferred out of this quarter's dock-scheduling release.**
Tomasz confirmed with the team; the single-yard rewrite stays the priority instead. Priya
confirmed the same call was flagged in roadmap review.

## Context

Thread does not say why single-yard was prioritised over multi-yard specifically beyond
"keep the rewrite on track" - that reasoning is not in the source, so it is not asserted
here.
```

**Index line**, `Inbox/index.md`:

```markdown
* [Multi-yard allocation deferred this quarter (22 Sep 2026)](2026-09-22-multi-yard-allocation-deferred.md) - Dock-scheduling will not support multi-yard allocation this quarter, deferred to protect the single-yard rewrite.
```

**Log line**, `log.md` under today's heading:

```markdown
* **Creation**: [Multi-yard allocation deferred](Inbox/2026-09-22-multi-yard-allocation-deferred.md) - captured from #freight-ops-eng, roadmap-relevant.
```

**Return JSON:**

```json
{
  "status": "done",
  "report_line": "captured decision: multi-yard allocation deferred this quarter · teammate_chat · <note link>",
  "artefacts": [{"kind": "kb_note", "ref": "Inbox/2026-09-22-multi-yard-allocation-deferred.md"}],
  "next_action": null
}
```
