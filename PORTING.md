# Porting a skill into marcketplace

This is the procedure for one Sonnet subagent porting one Bluewater skill (or building one
new skill) into `plugins/marcketplace/skills/<new-name>/`. Follow it in order. It assumes no
context beyond this file, `plugins/marcketplace/shared/`, `profiles/example.md`, your source
skill folder under `source/<old-name>/`, and one already-ported exemplar (`briefing`, after
wave 1).

## Read first

1. This file, end to end.
2. Every file under `plugins/marcketplace/shared/` (profile-schema.md, state-schema.md,
   onboarding.md, surface-protocol.md, handler-contract.md, notify.md, tool-capabilities.md,
   kb-conventions.md, voice.md, model-tiers.md, token-discipline.md).
3. `profiles/example.md`.
4. `source/<old-name>/SKILL.md` and any `HISTORY.md`, `references/`, `scripts/`, `evals/`
   alongside it.
5. One already-ported exemplar skill, if one exists yet (`briefing` after wave 1) - read its
   `SKILL.md` and directory layout as a template for structure and tone, not for content.

## House style

- Australian English throughout (behaviour, prioritise, organise, analyse).
- No em dashes anywhere, in prose, tables, comments, or code. Use `" - "`, `";"`, or the
  middot separator `" · "` instead.
- The frontmatter `description` starts with the literal words "Use when" and states
  triggering conditions only - never a summary of what the skill does or how.
- `SKILL.md` is a hard cap of 150 lines including frontmatter. There is no soft version of
  this rule.
- Context, worked examples, acceptance criteria, tables, and rationale belong in
  `references/`, not in `SKILL.md`. A pointer line replaces the moved content.
- A deterministic rule (a line grammar, a budget check, a threshold) gets a script under
  `scripts/`, not a paragraph of prose asking the model to remember it.
- No broadcast steps beyond the source skill's one notify step (see `shared/notify.md`).
- No per-skill memory file. State lives in the shared state document only
  (`shared/state-schema.md`).

## Steps

1. **Inventory.** Run:
   ```
   python3 plugins/marcketplace/scripts/scrub_check.py --report source/<old-name>/SKILL.md
   ```
   Classify every reported hit as one of: a profile key (look up the Bluewater ("BW") source
   column in `shared/profile-schema.md` to find the matching key), a state key, drop
   (Bluewater-specific behaviour that does not generalise), or fictionalise (keep the shape,
   replace the value). Do the same for any other file in the source skill folder that scrub
   flags.

2. **Extract.** Write `profiles/extract/<new-name>.local.md`: a YAML fragment holding the
   actual Bluewater values found in step 1, each annotated with the source file and line it
   came from. Do not touch `profiles/bluewater.local.md` directly - the orchestrator merges
   `profiles/extract/*` into it in wave 5.

3. **Skeleton.** Build the new `SKILL.md` in this order:
   - frontmatter (`name`, `description`)
   - one-paragraph role statement
   - `## Needs` (profile keys and tool categories the body uses; mark optional ones)
   - `## Budget`
   - `## Flow` (numbered steps)
   - `## Surface` (only if the skill reads or writes the surface)
   - `## Handler mode` (only if the skill appears in `handler-contract.md`'s handler table)
   - `## Ground rules`

   Paste the source skill's steps into `## Flow` first, unedited, then work through the
   remaining steps to relocate and rewrite in place.

4. **Line budget.** Run:
   ```
   python3 plugins/marcketplace/scripts/line_budget.py plugins/marcketplace/skills/<new-name>/SKILL.md
   ```
   It lists movable blocks (fenced code over 6 lines, tables over 8 rows, lists over 10
   consecutive items, and sections headed "Acceptance criteria", "Worked example",
   "Examples", or "Format"). Move each block verbatim to `references/<topic>.md` (the tool
   suggests a filename) and leave one pointer line in its place, e.g. "See
   `references/loop-protocol.md` for the full stop-check table." Re-run until PASS. Relocate
   content to shrink the file; never compress sentences together to hit the cap - that is a
   `line_budget.py` failure. See "Common mistakes" below.

5. **Fixed facts to profile/state.** Replace every Bluewater-specific fixed value with
   `` `profile.<path>` `` or `` `state.<path>` `` in backticks, using the keys from
   `shared/profile-schema.md` and `shared/state-schema.md`. No "Fixed facts" heading may
   survive the port - its content becomes `## Needs` plus profile-driven rules in `## Flow`.
   An org-specific rule (e.g. a specific budget threshold, a specific channel routing
   decision) becomes a rule driven by a profile key, not a hardcoded number.

6. **Tool names.** Replace every concrete tool name (`slack_read_canvas`, `getConfluencePage`,
   etc.) with the matching category verb from `shared/tool-capabilities.md` (e.g. "chat: read
   canvas", "wiki: get page by id"). Add the line: "Resolve tools via onboarding step 4;
   prefixes come from `state.machines`."

7. **Surface and notify.** Adopt the section headings, line grammar, and tags from
   `shared/surface-protocol.md` for any surface interaction. Replace webhook-specific blocks
   with a reference to `shared/notify.md`. If this skill is a handler (listed in
   `handler-contract.md`), it returns the handler contract JSON on completion and never
   writes the surface directly - the hub is the surface's only writer.

8. **Scripts.** Port any deterministic scripts from `source/<old-name>/scripts/`, removing
   hardcoded paths (for example `session-log`'s `archive_session.py` lines 29-35 and
   `pending_sessions.py` lines 26-30) in favour of an environment variable plus a pointer
   file. If the skill produces output that can be checked mechanically (a line grammar, a
   budget, a required field), add a deterministic checker script.

9. **HISTORY.md.** Rewrite inherited entries using role words instead of literals (e.g. "the
   chat surface" not "#marc-briefing"), keeping dates and lessons intact. Append a new
   section:
   ```
   ## <date> port to marcketplace
   ```
   covering: renamed-from, behaviours dropped and why, behaviours added, decisions made where
   the source skill was silent, and open questions for the orchestrator.

10. **Evals.** Keep the source skill's eval cases. Re-fictionalise every mock and grader
    against `profiles/example.md` so no Bluewater literal survives. Prompts use
    `profile=<example ref> unattended`.

11. **QA.** Run, in order:
    ```
    claude plugin validate .
    python3 plugins/marcketplace/scripts/scrub_check.py plugins/
    python3 plugins/marcketplace/scripts/line_budget.py --all
    python3 plugins/marcketplace/scripts/check_refs.py
    grep -rn "$(python3 -c 'print(chr(0x2014))')" plugins/marcketplace/skills/<new-name>
    ```
    `scrub_check.py` must report zero FAIL, and every WARN must be reviewed by hand (a WARN
    never fails the build automatically, but an unreviewed WARN can hide a real literal).
    `line_budget.py --all` must exit 0. The `description` frontmatter field must start with
    "Use when". The em dash grep must return nothing.

12. **Hand back. Do not commit.** Several subagents share this one working directory
    during a wave, so `git add` / `git commit` / `git push` from a subagent will collide on
    the git index and corrupt a sibling's work. The orchestrator commits at the wave gate.
    Instead, end your run with a report containing: the files you created or changed, the
    output of every QA check in step 11, the commit message you would have written (see
    below), every decision you made that the shared references did not cover, and anything
    you believe is wrong in the plan or the references.

    Commit message to propose:
    ```
    port(<new-name>): from <old-name>
    ```
    with 3 to 6 body bullets summarising what moved, what generalised, and what was dropped.
    For a wholly new skill (no source counterpart), use `add(<new-name>): <one line>`.

## Scrub regexes

Do not re-derive the pattern table by hand - run:
```
python3 plugins/marcketplace/scripts/scrub_check.py --list-patterns
```
to see every FAIL and WARN pattern with its name, severity, and case sensitivity. The
allowlist file `plugins/marcketplace/scripts/scrub_allowlist.txt` documents how to exempt a
genuinely fictional token that happens to match a WARN-class shape.

## Definition of done

- [ ] `claude plugin validate .` passes.
- [ ] `scrub_check.py plugins/` reports zero FAIL, and every WARN on this skill's files has
      been reviewed (not just passed through).
- [ ] `check_refs.py` exits 0: every `references/`, `scripts/` and `../../../shared/` path you
      wrote actually resolves from the file it is written in. A path that is correct from
      `SKILL.md` is wrong by one level inside `references/`; this is the single most common
      mistake in the whole port.
- [ ] `line_budget.py --all` exits 0 (this skill's `SKILL.md` is <= 150 lines).
- [ ] `## Needs` lists every profile key, state key, and tool category the body actually uses,
      and nothing else.
- [ ] A `references/` file exists for every block `line_budget.py` flagged, each with a
      pointer line left behind in `SKILL.md`.
- [ ] `HISTORY.md` has a "port to marcketplace" entry with dropped/added behaviours and open
      questions.
- [ ] `profiles/extract/<new-name>.local.md` is written.
- [ ] Evals are re-fictionalised and reference `profiles/example.md`.
- [ ] If this skill is a handler, it returns the handler contract JSON and never writes the
      surface.
- [ ] The proposed commit message is in your hand-back report.
- [ ] You ran no `git add`, `git commit` or `git push`.

## Common mistakes

- **Committing.** You share the working directory with sibling subagents. Write files, run
  the checks, report. The orchestrator commits.

- **Compressing sentences to hit the line cap.** Joining two sentences, deleting a worked
  example's steps, or cutting a caveat to save lines defeats the point of the cap - it is
  supposed to force content out of the model's always-loaded context, not out of existence.
  Relocate to `references/` instead; never compress.
- **Inventing profile keys.** If a Bluewater value doesn't map cleanly onto an existing key in
  `shared/profile-schema.md`, do not invent a new key on your own initiative. Flag it in the
  HISTORY.md port entry's "open questions for the orchestrator" list and use the closest
  existing key or a placeholder in the meantime.
- **Writing concrete MCP tool names.** `slack_read_canvas`, `getConfluencePage`,
  `jira_search`, and similar belong only in `shared/tool-capabilities.md` as hints; SKILL.md
  and references speak in category verbs.
- **Letting a "Fixed facts" heading survive.** If you find yourself keeping this heading
  because it's easier than reclassifying its contents, stop - every line under it needs to
  become a `## Needs` entry, a profile-driven rule, or a dropped behaviour with a reason in
  HISTORY.md.
