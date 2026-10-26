# History

## 2026-10-26 Step 5 checks the assembled length (1.10.1)

On 8 Oct 2026 a Haiku subagent running this skill dropped 16 characters across three long blocks while hand-concatenating the 950-character slices, and reported the file as "roughly" the right length. The timestamp self-check passed; a per-block length diff against `window.__TX` in the live tab found the three short blocks, which were re-pulled and patched. The finding stood in the knowledge base's memory from 8 Oct and was proposed as a fold by `kb-dream` on 15 Oct (`dream:261015-4`); the user accepted it on 26 Oct.

Step 5 now checks the file's character count after every batch against `min(chars, 8550 * batches)`, which localises a loss to one batch and costs one local command per batch rather than any extra page-script call. It also names the heredoc's trailing newline, which the existing "concatenate with nothing between" rule already forbade but the append instruction quietly reintroduced at every batch boundary.

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
