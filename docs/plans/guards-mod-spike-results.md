# Guards mod: phase 0 spike results

Run on 2026-10-11 in a Claude Code cloud container, Claude Code 2.1.296 (native build),
against a scratch copy of `plugins/marcketplace` with a small hooks module added beside the
existing classic hooks. Nothing from the spikes is in the plugin; this note records the
answers and what they change in `guards-mod-build-plan.md`.

## Answers

| Spike | Question | Answer |
|---|---|---|
| a | Does `claude plugin test` run with no credentials? | Yes. Five tests passed in under a second with an empty environment and an empty home folder, using both the container's CLI and a fresh `npm i @anthropic-ai/claude-code@2.1.296` install. |
| b | Can a test import a plain `./lib/*.ts` module? | Yes. A test imported a pure helper with an explicit `.ts` extension and called it directly. |
| c | What does the kit's `$.tool.call` return on a deny? | A plain `{ deny: "<text>" }`. An allowed call returns what the test's bottom hook answered, here `{ result: "ran" }`. |
| d | Does a headless run load the module and raise `prompt.submit` for its opening prompt? | Yes, in a cloud container with `claude -p --plugin-dir`. `session.start` fired with `isInteractive: false` and `surface: null`. `prompt.submit` fired for the opening prompt and its result carried origin `sdk`. A `twg login` call was refused before it ran, and the model read the refusal as a tool error. Not yet run on the laptop. |
| e | Does strict validation accept `modules`, `types` and literal env reads? | Yes. It lists the hooks, which gates carry a `.catch`, the env names read and the state keys written. |

## Other findings

- **Validation is not type-checking.** `validate --strict` passed a module that called
  `$.state.set` with one argument instead of `(ref, value)`. The tests caught it at run
  time. `tsc` with the engine's declarations also caught it (`Expected 2-3 arguments`).
- **The npm package matters.** The `@anthropic-ai/claude-code` already installed in this
  container is 2.1.42 and has no mod support. npm's `latest` is 2.1.296 and installs the
  same native binary, so CI must pin an exact version.
- **No types folder is written outside an interactive load.** Neither `claude plugin test`
  nor `claude -p --plugin-dir` wrote `.claude-plugin/types/`, and the npm package does not
  ship the declarations. CI therefore cannot type-check; it relies on validation plus tests.
- **The test kit's `$` has no state reader.** A test sees what the module stored by hooking
  `state.set` on its own `on` and recording `e.value`.
- **`$.state.set` refuses `undefined`.** Build values so an absent field is left out
  rather than set to `undefined`.
- **`$.ui.log` is dropped in tests** ("no implementation for ui.log"). In a headless run it
  reaches the JSON stream as a `system` message with subtype `ui_log`, naming the plugin.
- **`console` is not declared** in the hooks environment's types. Tests should assert, not
  print.
- **`session.end` budget** read about 1.5 seconds in a headless run.
- **Classic hooks and the module coexist.** The SessionEnd archive script ran in the same
  headless session as the module's own `session.end` hook.

## What changes in the plan

**Phase 1.** `prompt.submit` is a reliable source of the `unattended` flag for a routine's
opening prompt, so it stays the primary source; the `Skill` call and the dispatch payload
remain the source for subagents. Context values are written as `set(ref, value)` with no
`undefined` fields. Each hook gets at least one engine test, because the tests are the only
type net CI has.

**Phase 2.** Engine tests assert on `r.deny`. Deny text must stand alone as an
instruction, because the model reads it verbatim as a tool error and nothing else.

**Phase 5.** CI installs `@anthropic-ai/claude-code@2.1.296` exactly and runs
`validate --strict` and `plugin test` unconditionally; a version bump is a deliberate
change. Type-checking stays a local step: `tsconfig.mods.json` needs
`allowImportingTsExtensions`, and points at the engine-written types folder after an
interactive `--plugin-dir` load. PORTING.md's QA step names both.

**Still open.** Whether an installed plugin (not `--plugin-dir`) loads its module in a
scheduled routine, and whether the laptop behaves the same. Both are checked by the phase 1
smoke run.
