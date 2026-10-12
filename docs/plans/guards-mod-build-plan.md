# marcketplace 1.4.0: a guards mod that ships inside the plugin

## Context

The plugin's hard rules (one notify channel, two-tick irreversible writes, handlers never
touch the board, the 45 KB state guard, no questions in an unattended run, never set up the
`twg` CLI, the surface line grammar) are enforced today by prose in `shared/*.md` and by
scripts the model must remember to run. A cloud routine that forgets one of them either
hangs (a question nobody answers), posts to the wrong channel, or corrupts state.

Claude Code function hooks ("mods") run inside the engine and can refuse a tool call
deterministically. A mod is one TypeScript module named in the plugin's existing
`hooks/hooks.json` under `modules`, beside the two classic Python hooks, which stay as
they are. Verified in this session: adding `"modules": ["./register.ts"]` to the real
`hooks.json` passes `claude plugin validate --strict` (CLI 2.1.296).

Scope is only what benefits unattended cloud routines. Out of scope, by that filter: the
session ledger and running distillation (laptop write-ups), the board pane and the
pending-sessions band (terminal UI), the onboarding short-circuit (its cache would not
survive a fresh cloud container), the hillclimb mock-tool idea.

Decisions already taken with the user: guards block from the first release (with a kill
switch), channel ids are learned from the profile read in the session, and CI gains the
CLI so `plugin validate` and `plugin test` run on every push.

## Immediate steps (agreed 2026-10-11)

1. Commit this plan to `docs/plans/guards-mod-build-plan.md` on branch
   `claude/peaceful-edison-8fwkcy` and push. House style applies: Australian English, no em
   dash (the scrub check does not scan `docs/`, but the plan is repo content).
2. Run the phase 0 spikes below in the scratchpad against a copy of the plugin, nothing
   written to the repo except a short `docs/plans/guards-mod-spike-results.md` recording
   each answer. Spike 0d (the laptop `-p` run) cannot be done here; it runs in this cloud
   container instead and the result is marked as cloud, not laptop.
3. Commit the spike results and report what each answer changes in phases 1, 2 and 5.

## Design decisions

- **Pure core, thin wiring.** `hooks/register.ts` and `hooks/lib/observe.ts` are the only
  files that touch `$`. Everything else in `hooks/lib/` is `(input) -> output`, because the
  test kit's `$.tool.call` drops `agentId` (types line 12648), so every per-agent guard
  can only be tested by importing the pure function.
- **Content detection over tool names for the two documents.** A state-document write is
  any call whose string args contain `state_version:` or `shard_version:`; a profile
  observation is any tool *result* whose text contains `fallback_channel_id:`. Tool-name
  regexes are kept only for send, tracker create/comment and canvas update, with content
  hints (`- [ ] (` lines, `section_id`) for the canvas, and an env override.
- **Session state in `$.state`, nothing in `$.store`.** Context must survive a worker
  restart mid-routine; nothing should persist across sessions.
- **Two tiers.** Tier A guards are deterministic and deny in the default mode. Tier B
  guards are heuristic: they log in `on` and deny only in `strict`. Mode comes from the env
  var `MARCKETPLACE_GUARDS` (`off | warn | on | strict`, default `on`), which a cloud
  environment can set.
- **Fail closed only on write-class calls.** The one `tool.call` hook's `.catch` recomputes
  "is this a write-class call" from `e` alone (no `$` calls inside a catch) and denies
  those; reads pass through.
- **No `userConfig` in v1.** It lives in settings `pluginConfigs`, which a cloud routine
  environment cannot be assumed to carry.

## Files

```
plugins/marcketplace/
  .claude-plugin/plugin.json        version 1.4.0, "types": "./types/index.d.ts"
  hooks/hooks.json                  + "modules": ["./register.ts"]  (classic hooks unchanged)
  hooks/register.ts                 wiring: one hook per event, .catch policy, session.start line
  hooks/lib/config.ts               mode, default tool-name regexes, env names, write-class test
  hooks/lib/context.ts              pure: parse prompt text and dispatch payload; context types
  hooks/lib/observe.ts              scan tool results for profile ids, state-doc ids and keys
  hooks/lib/guards.ts               pure: decide(call, ctx) -> { verdict, guard, reason, tier }
  hooks/lib/lint.ts                 pure: canvas line lint
  hooks/lib/yaml-lite.ts            pure: fence extraction, top-level keys, UTF-8 byte size
  hooks/lib/text.ts                 pure: bounded walk of string values in an object
  hooks/context.test.ts, guards.test.ts, lint.test.ts, yaml-lite.test.ts   unit tests
  hooks/engine.test.ts              engine-level tests via claude plugin test
  types/index.d.ts                  PluginState contract (no imports)
  shared/guards.md                  what is enforced, tiers, kill switch, reading a deny, gaps
  scripts/scrub_check.py            skip plugins/marcketplace/.claude-plugin/types
repo root:
  tsconfig.mods.json                type-check config kept outside the plugin folder
  .gitignore                        + plugins/marcketplace/.claude-plugin/types/
  ci/validate.yml                   CLI install, validate --strict, plugin test (user copies to .github)
  CHANGELOG.md, README.md, PORTING.md, docs/skill-flow.md
  plugins/marcketplace/shared/{notify,tool-capabilities,state-schema}.md
  plugins/marcketplace/skills/session-log/references/hooks-setup.md
```

House style applies to the TypeScript too: `scrub_check.py` scans every file under
`plugins/`, so no em dash literal anywhere (write `\u2014` in the lint regex and fixtures),
no real Slack ids (fixtures use `profiles/example.md`'s `CEXAMPLE...` ids), Australian
English in comments and deny text.

## State contract (`types/index.d.ts`)

```ts
export type GuardMode = 'off' | 'warn' | 'on' | 'strict'
export type MainContext = { unattended: boolean; skill?: string; profileRef?: string }
export type AgentContext = {
  kind: 'handler' | 'reader' | 'other'; handler?: string; mode?: string
  unattended: boolean; budgetToolCalls?: number; calls: number; noted: boolean; parentAgentId?: string
}
export type Learned = {
  fallbackChannelId?: string; feedChannelIds: string[]; surfaceId?: string
  stateDocs: Record<string, { bytes: number; topKeys: string[]; runsKeys: string[] }>
}
declare module 'claude-code' {
  interface PluginState {
    marcketplace: { main: MainContext; learned: Learned; agents: StateFamily<AgentContext>; loaded: string }
  }
}
```

## Context observer (foundation)

- `prompt.submit`: if the text contains `/marcketplace:`, set `main = { unattended:
  /\bunattended\b/.test(text), skill, profileRef }`. Never infer unattended otherwise
  (onboarding step 0). Fallback if the routine's opening prompt does not raise this event
  (spike 0d): the `Skill` tool call args and the dispatch payload carry the token anyway.
- `tool.call { tool: 'Skill' }` observer: with `agentId` set, update that agent's `handler`
  from the skill name; without, update `main.skill`.
- `agent.spawn`: classify the prompt. `handler` iff it has a `^mode:` line, an `^item:`
  line, `/marcketplace:` and the token `unattended` (the exact payload is in
  `skills/proactive-router/references/dispatch.md` and `shared/handler-contract.md`);
  `budgetToolCalls` from `^budget:.*tool_calls:\s*(\d+)`. Otherwise `reader` when main or
  the parent agent is unattended, else `other`. Store under the `agentId` that `await
  next(e)` returns; inherit `unattended` from main or `agents[parentAgentId]`.
- After `next(e)` on every `tool.call`: `text = r.text ?? stringify(r.result)` capped at
  300 KB. If it contains `fallback_channel_id:` learn it plus the `tracker_feed_channels`
  child values and `surface.id`. If it contains `state_version:` or `shard_version:` record
  `{ bytes, topKeys, runsKeys }` keyed by every id-like arg of the call (any arg whose key
  matches `/id$|path/i`), so the later write matches on whichever arg the connector uses.

## Guards (all decided in `decide(call, ctx)`)

| Guard | Match | Verdict | Tier |
|---|---|---|---|
| twg setup | `Bash` and `/\btwg\s+(login|setup|upgrade|install)\b/` | deny | A |
| unattended ask | `AskUserQuestion` and (main or agent unattended) | deny: do not ask, fast-fail per onboarding | A |
| em dash on the surface | canvas write with `\u2014` in any string arg | deny listing the lines | A |
| feed channel | send tool with a channel arg equal to a learned feed id | deny | A |
| handler posts or writes the board | send or canvas write from an agent of kind `handler` or `reader` | deny: return the handler JSON instead | A |
| irreversible write by mode | tracker create or comment from a `handler` agent whose mode is not `push` or `file` | deny: first-pass mode, return `needs_confirmation` | A |
| channel gate | send from the main loop: channel arg must equal the learned fallback id; no profile observed yet or no channel-like arg: deny | deny | B, promoted to A after the phase 1 smoke run |
| state size | write whose args hold a state or shard fence over 45 KB (UTF-8 bytes) | deny | A (pure function of the write, no cached read needed) |
| state dropped keys | same write, doc id matched to a cached read: a top-level key present at read is absent in the write, and the write does not shrink the doc | deny naming the keys | B |
| foreign runs modified | main-doc or shard write where another skill's `runs.<x>` or `cursors.<x>` block text changed (removal allowed: briefing's shard cleanup deletes them legitimately) | deny | B, phase 3b, optional |
| tag form | canvas checkbox line whose tag is not `(pr|sweep|rb|term|feed|shc|dream):\d{6}-\d+`, `pr:prop-[a-z-]+`, or `[A-Z][A-Z0-9]+-\d+/d\d+[a-z]` | deny | B |
| budget | handler agent: at `calls === budget` append one user-role meta note "budget reached: return status partial now"; at `calls > budget + 5` deny write-class calls | note, then deny | B |

Documented as not enforced in `guards.md`: middot before the ref and 2 to 4 options per
group (a partial section write cannot see the group), one dated block per heading,
read-once/write-once (log-only counter; denying would break the re-read-before-write
rule), a plain-text question (it ends the turn, nothing hangs).

`warn` mode: `$.ui.log('marcketplace guard WOULD DENY <guard>: <reason>')` plus a `system`
notice row. `off`: register nothing but the `session.start` line. Tool-name overrides: env
`MARCKETPLACE_GUARD_TOOLS` holding JSON `{ send?, create?, comment?, canvas? }` regex
sources merged over the defaults.

## Wiring in `register.ts`

- One `on('tool.call', hook)` with no matcher: build `ctx` from two `$.state.get` calls,
  `decide`, deny or log, `const r = await next(e)`, `observe(r)`, return `r` unchanged.
  `.catch(($, e, next) => next.called ? next(e) : (isWriteClass(e) ? { deny: '...' } : next(e)))`.
- `on('agent.spawn')` with a pass-through `.catch` (never block a spawn on a parse bug).
- `on('prompt.submit')` and `on('session.start')` logging `marcketplace guards 1.4.0
  loaded, mode <m>`, no `.catch`.
- Per-agent counter writes use `ifVersion` with one retry (two calls in one agent can race).
- Reuse: `profiles/example.md` for fixtures; `shared/handler-contract.md` payload as the
  dispatch-parse fixture; `scripts/scrub_check.py` `SKIP_DIRS` (line 19) is basename-based,
  so add a path-specific skip for `.claude-plugin/types` rather than the name `types`.

## Phases

0. **Spikes, nothing shipped.** (a) `claude plugin test` on a one-line test with no API
   key: runs offline? (b) a test importing `./lib/x.ts`: allowed? (c) what the kit's
   `$.tool.call` returns on a deny (`{ deny }` versus `isError` + `text`). (d) `claude -p
   --plugin-dir plugins/marcketplace "hello"` with a `prompt.submit` log line: does the
   opening prompt raise it? (e) `validate --strict` with `modules`, `types` and two
   `$.env.get` literals. Each answer feeds phases 1, 2 and 5.
1. **Plumbing, context observer, smoke line.** hooks.json, plugin.json, `types/index.d.ts`,
   `context.ts`, `observe.ts`, `text.ts`, `register.ts` with the session.start log, scrub
   skip, gitignore, `tsconfig.mods.json`. Unit tests for `context.ts`. Ship as 1.4.0 on the
   branch, run one cloud briefing and one router routine, confirm the loaded line and, via
   a temporary `ui.log`, that the profile ids were learned.
2. **Tier A guards and lint.** `guards.ts`, `lint.ts`, `config.ts`, unit tests, engine
   tests for twg, AskUserQuestion, em dash, feed channel, handler-writes-board.
3. **State guards.** `yaml-lite.ts`, size (A), dropped keys (B). 3b foreign-runs modified
   only after 3 has run clean for a week.
4. **Budget and channel gate promotion.** Budget note then deny; promote the channel gate
   to tier A once phase 1's smoke run proves profile observation in the cloud.
5. **Docs, CI, release.** `shared/guards.md`; `notify.md` (the mod enforces the gate, the
   script stays as the model-visible check); `tool-capabilities.md` (hint names are also the
   mod's default patterns, with the override env); `state-schema.md` migration row `1.3.2 ->
   1.4.0: no state change`; `hooks-setup.md` (modules beside classic hooks); README install
   and checks; PORTING.md step 11 adds `claude plugin test`; `docs/skill-flow.md` one line;
   CHANGELOG 1.4.0. CI in `ci/validate.yml`: `npm i -g @anthropic-ai/claude-code@2.1.296`
   (pinned exactly; spike 0a showed tests run offline from that install), `claude plugin
   validate --strict plugins/marcketplace`, `claude plugin test plugins/marcketplace`. Tell
   the user to copy it to `.github/workflows/` per `ci/README.md`.

Dependencies: 2 and 3 depend on 1 and can proceed in parallel; 4 on 2; 5 on all.

## Tests

Unit (import the pure module):
- `context`: the verbatim dispatch payload parses to `{ kind: 'handler', handler:
  'action-sweep', mode: 'targeted', budgetToolCalls: 25 }`; a reader prompt with no `mode:`
  is `reader` when main is unattended; `mode:` without the `unattended` token is `other`.
- `guards` irreversible: `createJiraIssue` from mode `targeted` denies naming
  `needs_confirmation`; mode `push` allows; `createConfluencePage` from kb-note `capture`
  allows (not a tracker tool).
- `guards` handler surface: `slack_update_canvas` from a `handler` agent denies; from the
  main loop with the hub as skill allows.
- `guards` budget: call 24 of 25 silent; call 25 returns `note`; call 31 denies
  `slack_send_message` and allows `getJiraIssue`.
- `lint`: `- [ ] (pr:260922-03) ✉️ draft a reply · <url>` passes; `(pr:prop-calendar)`
  passes; `(FLT-164/d1a)` passes; `(todo-1)` fails; any string with `\u2014` fails naming
  the line; an untagged To-do line is ignored.
- `yaml-lite`: fence extraction from a markdown body and from a storage-format
  `<ac:structured-macro>` body; top-level keys ignore comments and nested keys; 45 KB is
  measured in UTF-8 bytes on a body with multibyte emoji.

Engine (`engine.test.ts` via `claude plugin test`):
- twg: `mock.env(on, { MARCKETPLACE_GUARDS: 'on' })`, bottom `Bash` hook answers `ran`;
  `twg login` denies; `twg whoami -o json` reaches the bottom.
- unattended ask: `$.prompt.submit` with the token, then `AskUserQuestion` denies; without
  the token it reaches the bottom.
- channel gate: bottom `getConfluencePage` answers the example profile YAML; send to
  `CEXAMPLEHOME01` allows, to `CEXAMPLEFEED01` denies, to another id denies; a send before
  any read denies in `strict` and logs in `on`.
- state size: 46 KB fence denies; 44 KB allows; 46 KB body without `state_version:` allows.
- dispatch parse: bottom `agent.spawn` answers `{ model, agentId: 'agent-1' }`; a
  `state.set` observer on `marcketplace.agents` sees `{ kind: 'handler', mode: 'targeted' }`.
- warn mode: a send to a feed id reaches the bottom and `mock.session(on)` holds one
  `system` row naming the guard.

## Type-checking without node_modules

`'claude-code'` resolves to the engine-written `.claude-plugin/types/claude-code/index.d.ts`,
laid beside the plugin the first time a session loads it with `--plugin-dir`. That folder
carries em dashes and is 800 KB, so it is gitignored and scrub-skipped, never committed.
Locally: `claude --plugin-dir plugins/marcketplace` once, then `tsc -p tsconfig.mods.json`
from the repo root (compiler options from the types file header: es2023, module esnext,
moduleResolution bundler, strict, noEmit, jsx react with factory `h`, plus
`allowImportingTsExtensions` for `./lib/*.ts` imports). CI relies on `validate --strict`
plus `plugin test`, since neither a `-p` run nor `plugin test` writes the types folder and
the npm package does not ship it. See `guards-mod-spike-results.md`.

## Risks

| Risk | Mitigation |
|---|---|
| Real connector tool names miss the regexes | content hints for canvas and state docs; env override; `warn` logs every unmatched write-class-looking call so the first cloud run lists what the regexes saw |
| Briefing wrongly blocked at its one send | channel gate starts tier B; the deny text names the expected id so the transcript is diagnosable; feed deny only on learned ids |
| `prompt.submit` not raised for a routine's opening prompt | spike 0d; fallback is the `Skill` tool args and the dispatch payload |
| A guard bug kills reads | the `.catch` denies write-class calls only, computed from `e` |
| Counter race in one agent | `ifVersion` with one retry |
| `claude plugin test` needs credentials in CI | ruled out by spike 0a: tests run with no credentials |
| Validation does not type-check, and CI cannot | every hook gets an engine test; `tsc` runs locally |
| Em dash in deny text or fixtures fails scrub | `\u2014` escapes only; scrub runs in CI |
| Workflow file cannot be pushed from this session | edit `ci/validate.yml`; the user copies it into `.github/workflows/` |

## Verification

1. `claude plugin validate --strict plugins/marcketplace` lists the gating hook with
   `.catch`, the two env names and the `marcketplace` state keys.
2. `claude plugin test plugins/marcketplace` green; `tsc -p tsconfig.mods.json` green locally.
3. `python3 plugins/marcketplace/scripts/scrub_check.py plugins/` zero FAIL with the types
   folder present on disk; `line_budget.py --all` and `check_refs.py` exit 0.
4. Laptop: `claude --plugin-dir plugins/marcketplace`, run `/marcketplace:briefing
   profile=... unattended` once with `MARCKETPLACE_GUARDS=warn`; zero `WOULD DENY` lines on
   a healthy run.
5. Cloud: one scheduled briefing and one router run; the transcript shows the loaded line;
   a test profile with a mis-pointed `fallback_channel_id` produces a deny and a fast-fail
   line in `runs.briefing`.
6. Negative drill: dispatch a fake handler payload via the Agent tool asking it to file a
   ticket in `targeted` mode; confirm the deny text and the `needs_confirmation` return.
