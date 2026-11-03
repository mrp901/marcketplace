# Worked example

Against `profiles/example.md` (Northwind Logistics, Freight Ops). Product tag `[Freight]`,
ideas project `FIG`.

Raw input from the user: *"the freight cost tile comparison is wrong, it's comparing MTD to
all of last month"*

---

**Title:** `[Freight] Prior-month comparison should be like-for-like MTD, not full month`

**Context**

In the dispatch and yard modules we don't have daily data, but for Freight Cost we do. The
Freight Cost tile still compares like they're the same - it takes month-to-date spend and
puts it against the *whole* of last month. On 12 September that's 12 days against 31, and
the tile reports "-58% prior month" as if spend has collapsed.

Anyone glancing at the dashboard mid-month reads that as a real drop. It gets worse the
earlier in the month you look, and it always resolves itself by month end, which is exactly
when nobody's checking.

**The ask**

**When we show a prior-period comparison, compare the same number of days - 1-12 Sep
against 1-12 Aug - and say on the tile which range we used.**

**Options**

- **Compare MTD to the same days of the previous month** (1-12 Sep vs 1-12 Aug) - smallest
  change, fixes the tile as it stands.
- **Add a full date range picker** and then compare the range to the equivalent previous
  range - more work, but it fixes every period comparison, not just MTD.
- **Keep the current comparison** and just label it "vs full previous month" - no maths
  change, only stops it being misread.

**Open Questions**

- Does this affect the other dashboard widgets and the summary email, or just this tile?
- For accounts whose billing cycle isn't the calendar month, do we compare on billing cycle
  or calendar days? That changes what "the same days" means.

**Related**

- FRT-164 - another idea in the garden touching period selection. Worth a look for whoever
  picks either up; not a dependency.

---

**Dispatch payload (abbreviated, hub `draft` mode):**

```
item:
  tag: pr:260922-05
  category: ticket-idea
  text_as_ticked: draft an idea ticket about the freight cost tile MTD comparison bug
  ref: <link to the Slack thread it came from>
mode: draft
```

**Return JSON, `draft` mode:**

```json
{
  "status": "needs_confirmation",
  "report_line": "drafted [Freight] MTD comparison ticket, audit clean · ticket_prose · <draft link>",
  "artefacts": [{"kind": "idea_ticket_draft", "ref": "<draft link>"}],
  "next_action": {"category": "ticket-idea", "text": "file the ticket: [Freight] Prior-month comparison should be like-for-like MTD, not full month", "ref": "<draft link>"}
}
```

**Return JSON, `file` mode, after the second tick:**

```json
{
  "status": "done",
  "report_line": "filed FRT-171 · [Freight] Prior-month comparison should be like-for-like MTD · <issue link>",
  "artefacts": [{"kind": "idea_ticket", "ref": "FRT-171"}],
  "next_action": null
}
```

Note what the example does: it names the modules, gives the actual numbers, has three
options written in the same shape so the trade-off is visible, and asks its open questions
as scope questions rather than risks.
