# Worked example

Against `profiles/example.md` (Northwind Logistics, Freight Ops, project `FLT`). Refine
mode, destination tracker. Keys and numbers are invented. Step 2 fetches FLT-230 first;
Step 3 then samples recent FLT stories.

**Step 3 finding (stated to the user):** "Followed the style of three recent FLT stories:
verb-first summaries, a one-line story, bulleted ACs under an Acceptance criteria heading,
epic parent required."

**Input story FLT-230, as found:**

> As a dispatcher, I want to be alerted when a carrier's late-delivery rate climbs, so I'm
> not surprised by penalty charges.
> - The alert triggers at the agreed threshold.
> - Alerts are clearly distinguished from other notifications.
> - Cross-carrier duplicate-link behaviour is undefined.

**Blind pass (story line plus ACs only) flags:**

1. "The agreed threshold": agreed with whom, and a rate or a penalty amount? The story's
   goal is about penalty charges, but the AC is about rate.
2. "Clearly distinguished": no named visual treatment.
3. Duplicate-link line: a label, not a scenario.
4. Nothing says what happens when delivery of the alert itself fails.
5. Nothing says which channel the alert goes to.

**Diff against what is decided:** the parent epic FLT-401 already fixes the notification
tray as the delivery channel, so the "which channel" question is dropped. Survivors:
rate-or-penalty and the duplicate-link scenario are genuine decisions (ask). Failed alert
delivery is a guardrail (write it in; one sane answer). "Clearly distinguished" is
under-specified, so name the instance by asking what the tray looks like today.

**One batched question round:** rate or penalty value; what the tray's existing alert rows
look like; if carrier B links a depot account carrier A holds, block, share, or ask A.

**Draft after the answers, before the antipattern pass (penalty value, existing amber row,
block with message):**

> - An alert is raised when projected penalty charges for the month pass the amount set at
>   the levels that make sense (lane, carrier, depot, total).
> - The alert appears in the notification tray as an amber row.
> - If carrier B tries to link a depot account carrier A already holds, the link is
>   refused and B sees which field to correct.
> - A failed alert delivery is retried and recorded.

**Antipattern pass:** "at the levels that make sense" is a weasel phrase beside a concrete
list (antipattern 6); cut to "at four levels: lane, carrier, depot, total". The other
bullets pass.

**Final:**

> - An alert is raised when projected penalty charges for the month pass the amount set at
>   four levels: lane, carrier, depot, total.
> - The alert appears in the notification tray as an amber row.
> - If carrier B tries to link a depot account carrier A already holds, the link is
>   refused and B sees which field to correct.
> - A failed alert delivery is retried and recorded.

**Push:** `tracker: edit issue` with the full description, then `tracker: link issues` from
FLT-230 to the penalty-calculation story it relied on. Summary to the user, one line per
changed AC.
