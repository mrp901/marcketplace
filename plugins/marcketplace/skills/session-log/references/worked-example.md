# Worked example

Against `profiles/example.md` (Northwind Logistics, Freight Ops), a live session that
corrected a figure.

**Gate check:** the session corrected a fact (an earlier lane-table draft used the wrong
comparison baseline) and made a decision (use the same weekdays instead) - worth a note.

**Note written**, `Sessions/2026-09-22-lane-table-baseline-corrected.md`:

```yaml
---
type: Session Log
title: Lane-table comparison baseline corrected (22 Sep 2026)
description: Dashboard lane table now compares the same weekdays, not whole prior weeks.
tags: [session, freight, dashboard]
status: draft
generated: { by: session-log, at: 2026-09-22T17:40:00+10:00 }
---

# Session - Lane-table comparison baseline corrected (22 Sep 2026)

**When:** 2026-09-22, ~40 min · **Where:** Freight Ops dashboard work · **Prompted by:** Priya asked why the slowest-lanes table looked wrong against last week's export.

## Decisions

- **Compare the same weekdays, not whole prior weeks.** The earlier draft compared a
  partial current week against a complete prior week, overstating every increase. Feeds
  [decision record](../Decisions/2026-09-22-lane-table-baseline.md).

## Facts and corrections

- **Corrected:** the slowest lane's increase is 6.1%, not the 14% first reported - the
  14% figure compared partial-to-full weeks.

## Open threads

- [ ] Confirm with Tomasz whether the same baseline bug affects the monthly rollup.

## Proposed follow-ups

- [ ] `Decisions/2026-09-22-lane-table-baseline.md` - new record for the weekday comparison
      call. Not written yet.
```

**Index line**, `Sessions/index.md`:

```markdown
* [Lane-table comparison baseline corrected (22 Sep 2026)](2026-09-22-lane-table-baseline-corrected.md) - Dashboard lane table now compares the same weekdays, not whole prior weeks.
```

**Log line**, `log.md` under today's heading:

```markdown
* **Creation**: [Session - lane-table baseline corrected](Sessions/2026-09-22-lane-table-baseline-corrected.md) - weekday comparison fix, 14% figure was a baseline artefact.
```

**A same-run stale line, corrected unasked:** if an earlier line logged today already
described the lane table using the old 14% figure, the fix is a new append-only line, not
an edit of the old one:

```markdown
* **Correction**: the earlier "slowest lane up 14%" entry today used a partial-week
  baseline. Corrected figure is 6.1% - see [session note](Sessions/2026-09-22-lane-table-baseline-corrected.md).
```
