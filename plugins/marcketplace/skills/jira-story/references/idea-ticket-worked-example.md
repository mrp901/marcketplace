# Worked example

Against `profiles/example.md` (Northwind Logistics, Freight Ops). Product tag `[Freight]`,
ideas project `FIG`.

Raw input from the user: *"the delivery-time chart comparison is wrong, it's comparing this
week so far to all of last week"*

---

**Title:** `[Freight] Delivery-time chart should compare the same weekdays, not whole weeks`

**Context**

In the dispatch and yard modules we only have weekly totals, but in Route Planner we have
daily ones. The Delivery Time chart still compares like they're the same - it takes this
week's days so far and puts them against the *whole* of last week. On a Wednesday that's 3
days against 7, and the chart reports "-57% vs last week" as if delivery hours have
collapsed.

Anyone glancing at the dashboard early in the week reads that as a real drop. It gets worse
the earlier in the week you look, and it always resolves itself by Sunday, which is exactly
when nobody's checking.

**The ask**

**When we show a prior-week comparison, compare the same weekdays - Mon-Wed against
Mon-Wed - and say on the chart which days we used.**

**Options**

- **Compare this week's days so far to the same weekdays of last week** (Mon-Wed vs
  Mon-Wed) - smallest change, fixes the chart as it stands.
- **Add a full date range picker** and then compare the range to the equivalent previous
  range - more work, but it fixes every period comparison, not just this chart.
- **Keep the current comparison** and just label it "vs whole of last week" - no maths
  change, only stops it being misread.

**Open Questions**

- Does this affect the other dashboard widgets and the summary email, or just this chart?
- For depots whose working week isn't Monday to Friday, do we compare on the depot's working
  week or on calendar weekdays? That changes what "the same weekdays" means.

**Related**

- FLT-512 - another idea in the garden touching period selection. Worth a look for whoever
  picks either up; not a dependency.

---

**Dispatch payload (abbreviated, hub `draft` mode):**

```
item:
  tag: pr:260922-05
  category: ticket-idea
  text_as_ticked: draft an idea ticket about the delivery-time chart comparison bug
  ref: <link to the Slack thread it came from>
mode: draft
```

**Return JSON, `draft` mode:**

```json
{
  "status": "needs_confirmation",
  "report_line": "drafted [Freight] same-weekday comparison ticket, audit clean · ticket_prose · <draft link>",
  "artefacts": [{"kind": "idea_ticket_draft", "ref": "<draft link>"}],
  "next_action": {"category": "ticket-idea", "text": "file the ticket: [Freight] Delivery-time chart should compare the same weekdays, not whole weeks", "ref": "<draft link>"}
}
```

**Return JSON, `file` mode, after the second tick:**

```json
{
  "status": "done",
  "report_line": "filed FLT-519 · [Freight] Delivery-time chart should compare the same weekdays · <issue link>",
  "artefacts": [{"kind": "idea_ticket", "ref": "FLT-519"}],
  "next_action": null
}
```

Note what the example does: it names the modules, gives the actual numbers, has three
options written in the same shape so the trade-off is visible, and asks its open questions
as scope questions rather than risks.
