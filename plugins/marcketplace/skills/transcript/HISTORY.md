# History

## 2026-11-02 Step 5 writes batches with the write tool and checks checksums (1.10.2)

Transcribing a long meeting (about 500 entries, 51,000 characters, six batches) hit three things the 1.10.1 length check did not cover. The shell heredoc rejected a batch on quoting, and had done so in a separate run, so Step 5 now uses the file-write tool per batch. A batch came out 4 characters over: the length check caught it but could not say where, so a rolling prefix checksum at each 950-character boundary, computed in the page and over the file, now finds the bad slice at once (it was in the last slice of batch 1; it was "So this one is the one" for "So this is the one"). Batch results from the browser tool are separated by the tool's own label with one trailing space, which Step 5 now names so it is stripped exactly and not eyeballed. The page also lost `window.__TX` after batch 3; a re-harvest rebuilt identical text (same entry count and characters, same checksums), so Step 4 now says to re-run it. The checksum hashes UTF-16 code units so the local side matches the page for emoji.

## 2026-10-26 Step 5 checks the assembled length (1.10.1)

A Haiku subagent running this skill dropped 16 characters across three long blocks while hand-concatenating the 950-character slices, and reported the file as "roughly" the right length. The timestamp self-check passed; a per-block length diff against `window.__TX` in the live tab found the three short blocks, which were re-pulled and patched. The finding was recorded in the knowledge base's memory, proposed as a fold by `kb-dream`, and accepted by the user.

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
