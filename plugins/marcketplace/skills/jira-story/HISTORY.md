# History

## 2026-10-13 port to marcketplace

Ported from a private `jira-story` skill (single `SKILL.md` plus `references/antipatterns.md`),
same name. Written as a directly invoked skill, not a hub handler.

**Behaviours generalised:**

- **Ticket conventions are now discovered, not hardcoded.** New Step 3 inspects (after Step 2 reads the target in Refine mode) the
  connected tracker (recent issues of the target project and type, up to three read in
  full) and infers summary style, labels, field usage, AC format and hierarchy or epic-link
  convention; if nothing usable is found it asks once. Detail in
  `references/inspect-tracker.md`. The source assumed one house format.
- Concrete tracker tool names are gone in favour of `tracker:` category verbs.
- The blind pass is named as reviewer-tier judgement (`profile.budgets.models.critic`), not
  extraction, with the unavailable-tier rule pointed at `../../shared/model-tiers.md`.
- The vault destination became a generic knowledge-base destination per
  `../../shared/kb-conventions.md` and `profile.kb.*`; a bare file path stays supported.
- `references/antipatterns.md` kept all eight lessons; every example re-fictionalised
  against Northwind Logistics in `profiles/example.md`.
- The specificity test, the guardrail-or-ask discriminator and the new "split by customer
  value" and "resolve, do not park" rules moved verbatim-in-substance into
  `references/specificity-and-guardrails.md` to hold `SKILL.md` under 150 lines.

**Dropped, and why:**

- Personal naming, the proactive-router and brainstorming skill dependencies, and the
  "independent of brainstorming" claim: org- and person-specific, not part of the method.
- The persistent-memory note and the `lessons.md` fallback: marcketplace forbids per-skill
  memory files. Durable tone or quality feedback now routes to the voice ledger as
  `../../shared/voice.md` describes, or ends with the conversation.
- The vault-specific destination rules (vault CLAUDE.md, OKF frontmatter, index and log
  handling): replaced by the generic knowledge-base pointer.
- The real example ticket keys and tenant/site names.

**Behaviour ADDED (not in the source):**

- A hard rule: never create or edit without the user's go-ahead on the final text (Step 9
  and Ground rules). The source allowed pushing straight to the tracker when told to.

**Content moved back from the source after review:** the blind-pass rationale, the
"legitimately abstract" example and cold-start note, and the Voice section now live in
`references/specificity-and-guardrails.md` (sections 5 to 7), re-fictionalised against
Northwind.

**Decisions where the source was silent:**

- `idea-ticket`'s ticket-format is not duplicated: it fixes an ideas-board shape (Context,
  Ask, Options) that does not apply to stories. Only its "Cut the AI tells" list is shared,
  by reference from Step 8.
- Created no `budgets.jira-story` key; caps are stated in `## Budget`.
- Added a rule that a convention needs two sampled issues before it counts, so one odd
  ticket is not read as house style.

**Open questions for the orchestrator:**

- `tracker: edit issue` and `tracker: link issues` are now rows in
  `../../shared/tool-capabilities.md`, with jira-story added to the `Used by` column of the
  tracker rows it uses; confirm the hint names. `tracker: add comment` was dropped from
  `## Needs` (unused).
- A `budgets.jira-story` subtree (`{inspect_reads: 3, blind_passes: 2}`) if caps should be
  configurable.
- A profile key for "the tracker's AC convention once inferred" so a second run does not
  re-inspect; not invented here.
- `tracker.ticket_template` exists but is described for idea-ticket and action-sweep; confirm
  whether Step 3's inferred style should defer to it when set. For now `## Needs` lists it as
  an optional hint and sampled issues win.
- Whether the blind pass should be allowed on the `worker` tier when `critic` is
  unavailable, or fall back as stated (strongest available, say so).
- AC-quality lessons (as opposed to voice) have no durable home: the source kept them in a
  persistent-memory note or `lessons.md`, and marcketplace forbids a per-skill memory file.
  Step 10 routes only genuine before/after voice pairs to the voice ledger, so a lesson like
  "parity phrasing used for an unconfirmed mechanism" ends with the conversation. Decide
  whether the orchestrator wants a shared home for them (a ledger section, or a state key).
- The compounding loop now reads the `ticket_prose` register and the voice ledger's
  jira-story entries at the start of each pass; the ledger has no per-skill tag, so
  "jira-story entries" means entries whose subject is a story's ACs. Confirm that is enough.
- Step 3's budget is two searches plus three reads (one search plus a single widen).
