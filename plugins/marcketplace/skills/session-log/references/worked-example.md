# Worked example

Against `profiles/example.md` (Northwind Logistics, Freight Ops), a live session that
corrected a figure.

**Gate check:** the session corrected a fact (an earlier cost-table draft used the wrong
comparison baseline) and made a decision (use like-for-like MTD instead) - worth a note.

**Note written**, `Sessions/2026-09-22-cost-table-baseline-corrected.md`:

```yaml
---
type: Session Log
title: Cost-table comparison baseline corrected (22 Sep 2026)
description: Dashboard cost-table now compares like-for-like MTD, not prior full month.
tags: [session, freight, dashboard]
status: draft
generated: { by: session-log, at: 2026-09-22T17:40:00+10:00 }
---

# Session - Cost-table comparison baseline corrected (22 Sep 2026)

**When:** 2026-09-22, ~40 min · **Where:** Freight Ops dashboard work · **Prompted by:** Priya asked why the top-cost-increases table looked wrong against last month's export.

## Decisions

- **Compare like-for-like MTD, not full prior month.** The earlier draft compared a
  partial current month against a complete prior month, overstating every increase. Feeds
  [decision record](../Decisions/2026-09-22-cost-table-baseline.md).

## Facts and corrections

- **Corrected:** the top line item's increase is 6.1%, not the 14% first reported - the
  14% figure compared partial-to-full months.

## Open threads

- [ ] Confirm with Tomasz whether the same baseline bug affects the quarterly rollup.

## Proposed follow-ups

- [ ] `Decisions/2026-09-22-cost-table-baseline.md` - new record for the MTD comparison
      call. Not written yet.
```

**Index line**, `Sessions/index.md`:

```markdown
* [Cost-table comparison baseline corrected (22 Sep 2026)](2026-09-22-cost-table-baseline-corrected.md) - Dashboard cost-table now compares like-for-like MTD, not prior full month.
```

**Log line**, `log.md` under today's heading:

```markdown
* **Creation**: [Session - cost-table baseline corrected](Sessions/2026-09-22-cost-table-baseline-corrected.md) - MTD comparison fix, 14% figure was a baseline artefact.
```

**A same-run stale line, corrected unasked:** if an earlier line logged today already
described the cost table using the old 14% figure, the fix is a new append-only line, not
an edit of the old one:

```markdown
* **Correction**: the earlier "top line item up 14%" entry today used a partial-month
  baseline. Corrected figure is 6.1% - see [session note](Sessions/2026-09-22-cost-table-baseline-corrected.md).
```
