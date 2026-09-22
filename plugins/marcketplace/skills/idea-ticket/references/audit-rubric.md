# Audit rubric

Given to the fresh critic-tier subagent in Step 4, along with only the drafted title and
body plus the original raw input - never the reasoning behind phrasing choices. It should
judge the ticket cold, the way a teammate opening it fresh would.

**Rubric - score each pass/fail with a one-line reason:**

1. **Structure correct.** Title matches `<profile.org.product_tag> <problem statement>`
   (not a fix description); Context / The ask / Options appear in that order; Open
   Questions and Research leads are present only when genuinely warranted.
2. **Voice match.** Present tense, plain English, first-person plural, short declaratives.
   No framework jargon, no hedging, no boilerplate headers. Reads like the user wrote it,
   not like a research brief. Check it against `ticket-format.md`'s "Cut the AI tells" list
   and `../../shared/voice.md`'s shared avoid-list; name any specific tell found.
3. **Zero-context clarity.** Someone who has never seen the screen can read Context alone
   and know exactly what's wrong, because it names the actual modules, screens, tiles,
   labels and numbers. "A percentage is misleading" fails. "In TEM and Mobile we don't have
   daily data, but for Cloud we do - so the Cloud Spend tile is comparing 12 days of this
   month to 31 of last" passes.
4. **Options are parallel.** The options use the same sentence shape and level of detail,
   with only the genuinely different part varying, so the trade-off is visible at a glance.
   If a reader would have to ask "how is 2 different from 1?", this fails.
5. **Concision.** About a screen's length. No sentence restates a point already made. No
   section exists just to look thorough.
6. **Register correct.** Open Questions read as scoping questions, not risks or blockers.
   Any linked sibling ticket is presented as a sibling idea, not as a constraint or a
   committed future state.
7. **Scope discipline.** Vendor mentions are one-liners for orientation. No comparison
   tables, no multi-line competitive analysis, no evidence anyone went and researched a
   competitor.
8. **Precedent handled.** If Step 2 found a true duplicate, that is surfaced to the user
   rather than silently proceeded past; any sibling idea found is cross-linked under
   Related.

If every criterion passes: proceed to Step 6 with this draft.

If anything fails: revise the draft to address the specific reasons given (not a generic
rewrite), then send the revised draft through this audit again per Step 5 - a fresh
critic-tier subagent call, not the same one continuing.
