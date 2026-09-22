# idea-wireframe - design rationale (for editors; not loaded at runtime)

- A revision of an earlier wireframe found a build-order deck written the day after the
  first run had reframed the module and moved the next phase from one area to another.
  Origin of the sweep-before-standing-list rule in Step 2.
- The first run on that same idea drew a navigation rail that does not exist, used a chart
  granularity that did not match the real data, and marked something "out of scope" that
  was already shipped on the dashboard - all contradicted by captures sitting one folder
  away. Origin of the mandatory captures-before-drawing rule in Step 2.
- Self-contained HTML (not a hosted canvas format) because it is cheaper, lands as a local
  file in the knowledge base, and is the format the user asked for.
- A later optimisation capped capture reads at 5 (+2 competitor) chosen by relevant
  surface - images were the largest single input cost - capped sweep reads at 5, dropped a
  house-style skim of the prototypes folder (the style lives in the skill itself, not in
  past output), and replaced a render-then-manually-adjust loop with CSS-relative marker
  placement. The posted nudge was changed to open with the user's own mention link, for
  parity with the other skills' mobile-notification mechanism (previously omitted).

## 2026-09-22 port to marcketplace

Renamed from `cloud-idea-wireframe`. Ported per `PORTING.md`, reading
`source/cloud-idea-wireframe/SKILL.md` and this file in full, `plugins/marcketplace/shared/`,
`profiles/example.md`, and `briefing` as the structural exemplar.

**Behaviours carried over, unchanged in substance (the two history lessons above, kept
enforceable rather than advisory):**
- The captures-mandatory rule is stated as a requirement in `SKILL.md` Step 2 itself (not
  only in `references/selection-and-context.md`), with the exact failure mode from the
  source's first run restated so a future reader sees the cost of skipping it, not just an
  instruction to follow. The "no capture -> annotate as inferred" fallback survived
  unchanged.
- The sweep-before-standing-list rule is likewise stated in `SKILL.md` Step 2 as an ordering
  requirement, not just documented in the reference file - the numbered read order in
  `references/selection-and-context.md` still puts the sweep first, before the taste log
  and the standing research note, exactly as the source did.
- The image/read/critic budget and its explicit "never outranks a correctness check"
  override survived into `SKILL.md`'s own `## Budget` section rather than being pushed
  entirely into a reference, since it is a standing constraint the skill applies every run,
  not background detail.
- The self-contained HTML choice and its reasoning (cheap, lands as a real file, matches
  what was asked for) is kept in this file rather than restated in `SKILL.md`, since it is a
  decision record, not an instruction the model needs on every run.
- The critic round: fresh subagent, `budgets.models.critic` tier, images and a one-line
  problem only, prior wireframes labelled "previous attempts, not exemplars", rank rather
  than score, one revision cap tied to "ranks last and reads as filler" together, never
  either alone.
- The one-idea-per-run ordering (file -> indexes -> label -> surface -> notify) and its two
  failure branches (file failed -> don't label; label refused after a successful save ->
  retry once, then say so and note the idea will repeat).

**Behaviours generalised (source -> shared contract):**
- Fixed Jira/Slack/vault facts moved to `profile.tracker.*`, `profile.ideas.*`,
  `profile.surface.*`, `profile.notify.webhooks.idea-wireframe`, `profile.kb.*` - see
  `profiles/extract/idea-wireframe.local.md` for the values found and their source lines.
  No new profile key was needed; every fixed fact in the source mapped onto an existing key.
- Tool names (`searchJiraIssuesUsingJql`, `getJiraIssue`, `editJiraIssue`,
  `sharepoint_search`, `slack_read_canvas`, `slack_update_canvas`) replaced with the
  category verbs from `shared/tool-capabilities.md` (`ideas: search issues (JQL)`,
  `ideas: get issue`, `ideas: add label`, `kb: search`, `chat: read canvas`,
  `chat: update canvas`).
- The Slack canvas item and workflow webhook generalised to
  `shared/surface-protocol.md`'s line grammar and `shared/notify.md`'s `idea-wireframe` body
  shape (`{"ticket": ..., "outputUrl": ...}`, unchanged in shape - the notify contract
  already matched the source exactly).
- The house style, annotation conventions, frame rotation table, selection JQL, precedence
  rules and the wrapper-note worked example moved to `references/` per the line budget; each
  left a pointer line behind in `SKILL.md`.

**Behaviours dropped, and why:**
- None. Every step and rule in the source `SKILL.md` had a generalised home - either a
  profile/state key, a shared contract this skill now points at, or a `references/` file.

**Decisions made where the source skill was silent:**
- **No `## Handler mode` section.** `idea-wireframe` does not appear in
  `handler-contract.md`'s category table, so it is not dispatched by the hub - it runs on
  its own schedule or direct invocation only, the same as the source. Confirmed this
  reading against the category table before omitting the section, per `PORTING.md`'s
  definition of done.
- **No cursor in `state.cursors`.** `state-schema.md` already states plainly that idea-scout
  and idea-wireframe carry no cursor, the tracker label being the idempotency key - kept
  that as-is rather than inventing one.
- **`ideas.roadmap_field` ordering direction.** The source says "roadmap-first (Now > Next >
  Later > unset)" - a fixed three-value vocabulary specific to the source instance. Since
  `profile.ideas.roadmap_field` is documented as free-form and "reported, never a
  qualifier", I generalised the ordering rule to "nearest slot first, then furthest, then
  unset" rather than hardcoding three literal values that a different install's roadmap
  field might not share. Flagging this in case the orchestrator wants the ordering made
  explicit as a small profile-driven vocabulary instead of a generalised description.
- **The wrapper note's `type` value.** The source hardcodes `type: Prototype`. Since
  `kb-conventions.md` is explicit that the live type registry is the only authority and a
  skill must check it every time rather than assert from memory, I kept `Prototype` only as
  the worked example's illustrative value in `references/kb-write.md`, and put the
  check-the-live-registry-first instruction in `SKILL.md` Step 6 itself as a requirement,
  not a suggestion.

**Open questions for the orchestrator:**
- `profile.ideas.roadmap_field`'s vocabulary (see above) is read but never enumerated
  anywhere in `profile-schema.md` - confirm whether it should stay free-text (as I've
  treated it) or gain a documented small vocabulary like `ideas.labels` has.
- `kb.sweep_queries`' default in `profiles/example.md` is a fictionalised, generic set
  ("freight ops dashboard", "dock scheduling", "competitor brief"). The source install's
  real queries include a product-codename-shaped term that scrubs as a FAIL pattern
  (`product-codenames`); I did not attempt to extract or fictionalise a closer match to the
  real query wording beyond what `profiles/example.md` already carries, since inventing a
  more specific fictional value risked looking like a real extracted literal. Flagging in
  case the orchestrator wants a closer stand-in.
- This skill and `idea-scout` both read `profile.kb.paths.research` and both write near
  `profile.kb.paths.prototypes`/`.paths.research`'s sibling folders; I did not coordinate
  directly with the sibling porting `idea-scout` beyond skimming its source `SKILL.md` for
  the note shape, per the task brief. Worth a cross-check at the wave gate that both ports
  describe the scout note's frontmatter and folder identically.
