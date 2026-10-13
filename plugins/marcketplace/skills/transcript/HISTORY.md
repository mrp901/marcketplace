# History

## 2026-10-13 port to marcketplace

Ported from a private `transcript` skill that was already generic in method; this was a conformance pass, not a redesign. The working technique (probe, time-boxed resumable in-page harvest, 950-character slice pull, nine slices per batch) is unchanged.

**Generalised:**

- The "this tenant" note on `GraphAccessToTranscriptsDisabled` now reads "if tenant policy disables Graph transcript access".
- Concrete browser, batch, file-delivery and device-write tool names are replaced with category verbs (`browser: list tabs`, `browser: navigate`, `browser: run page script`, `browser: batch calls`, `browser: read page`, `browser: page text`, `deliver file to user`). The batch item JSON is described rather than quoted, since it named a concrete tool.
- The description now starts "Use when" and states triggers only.

**Moved, not compressed:** the probe, harvest and resume-check scripts and the "why the fragile-looking bits are that way" rationale now live verbatim in `references/page-scripts.md`; `SKILL.md` keeps the flow and points at them from Steps 3 and 4. The manual-console fallback is now Flow Step 7 so the section order is Needs, Budget, Flow, Ground rules.

**Dropped:** the "Hard rules" and "Routes that do not work" headings, folded into `## Ground rules`; arrows and em dashes replaced with plain text (the file header title is now "<Meeting name> - transcript").

**Open questions:**

- Resolved after review: the `browser` verbs, `shell: run command` and `deliver file to user` are now rows in `../../shared/tool-capabilities.md` (hints: the Chrome browser tools, a shell tool, a file-delivery tool), and `## Needs` says to resolve them via onboarding step 4. Confirm the hint names, and whether onboarding step 4 should probe a `browser` category at all.
- `## Needs` carries no profile keys and the skill does not run onboarding resolution; confirm that is right for a direct-use skill with no profile dependency.
