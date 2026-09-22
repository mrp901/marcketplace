# session-log - design rationale (for editors; not loaded at runtime)

- The "is this worth a note" gate exists because the source vault's own conventions warn
  against notes nobody links to and against letting capture accumulate. Unchanged in the
  port.
- The type-registry cautionary tale is the single most important behaviour this skill
  carries: it once asserted a note type was unregistered from a cached snapshot bundled as
  a reference, when the live registry file had already been updated the day before, and
  the mistake cost a log correction entry. Generalised into `shared/kb-conventions.md`'s
  "The type registry and its single authority" section, and restated prominently in
  `SKILL.md` step 3 rather than only in a reference file, because it is the one mistake
  this skill must never repeat quietly.
- The real-timestamp-with-offset caution (system clock, never memory, because the UTC
  offset changes across daylight saving) is unchanged in substance.
- The maintenance contract's "the log is append-only, a stale line is corrected in the same
  turn" rule is unchanged, now pointing at `kb-conventions.md`'s shared statement of it
  rather than restating the full reasoning.
- `SessionEnd` cannot invoke a model or block the session, so the hooks are split across
  `SessionEnd` (archive only) and `SessionStart` (report the backlog) rather than attempted
  as one hook. This reasoning is preserved in full in `references/hooks-setup.md`.

## 2026-09-22 port to marcketplace

Renamed from `session-log` (source skill of the same name; no rename needed). Ported per
`PORTING.md`.

**Behaviours carried over, unchanged in substance:**
- The "is this worth a note" gate.
- The type-registry live-authority rule and its cautionary tale.
- Real-timestamp-from-system-clock, with the daylight-saving offset caution.
- The four-section note body (Decisions, Changes, Facts and corrections, Open threads),
  with corrections given their own bullet prefix.
- `generated`/`verified` handling when a session edits an existing note, including the
  "leave `verified` alone, but say so in the Changes table" behaviour.
- Propose-don't-make for topic-note edits, the asymmetry-of-cost reasoning, and the
  same-live-session update-in-place exception.
- The Decision Record vocabulary (`decision_status`, `jira`, `owner`, `deciders`,
  `date_raised`, numbered `##` sections).
- Linking rules (relative markdown only, no wikilinks, broken forward-references are fine)
  and the names-check-before-you-write discipline.
- The pending-sessions queue: archive on `SessionEnd`, report on `SessionStart`, process
  oldest first, move `pending/` -> `archive/`, judgement on grouping same-day sessions.
- `read_transcript.py`'s changed-vs-read-only file separation and its tolerance of unknown
  transcript line shapes.

**Behaviours generalised:**
- The vault's specific frontmatter/tag/type/linking rules moved to
  `shared/kb-conventions.md`; this skill's `references/` now hold only what's genuinely
  session-note specific (the four-section body, the Decision Record vocabulary, the
  propose-don't-make mechanics) and point at the shared file for everything else. Most of
  the old `references/vault-conventions.md` (the six-key coverage table, the type-value
  inventory, the tag-cluster counts, the actor/provenance discussion) is now redundant with
  `kb-conventions.md`'s frontmatter contract and provenance rule - dropped rather than
  copied, since duplicating it would let the two drift and reintroduce the exact
  cached-vs-live failure mode this skill exists to avoid. Nothing substantive was lost: the
  frontmatter-contract table, the provenance/`generated`-vs-`verified` rule, the type-
  registry live-authority rule, the index/log maintenance contract, dated-file naming and
  the transient-drafts contract all now live in `kb-conventions.md`, generalised rather
  than restated.
- `.utility/`'s never-indexed, never-curated status is inherited from `kb-conventions.md`
  rather than restated; `references/pending-sessions.md` only adds what's specific to this
  skill's own use of it (the pending/archive move, the cursor).

**Hooks, scripts and the pointer-file convention:**
- `source/session-log/scripts/archive_session.py` and `pending_sessions.py` hardcoded a
  single org-specific cloud-synced vault path as a fallback candidate (lines 29-35 and 26-30
  respectively, per `PORTING.md`'s own pointer). Removed entirely. Both scripts now resolve
  their archive directory as: `SESSION_LOG_DIR` env var, then a pointer file at
  `~/.claude/marcketplace/session-log-dir.ref` (a single line, the resolved local path),
  then a local default (`~/.claude/session-log`). The pointer file is written by the
  `SKILL.md` flow's step 1 the first time it resolves the kb's local root - this mirrors
  `shared/onboarding.md`'s own env-var-then-pointer-file pattern for locating the profile
  document, applied here because the hook scripts run standalone with no tool access and
  cannot do kb discovery themselves.
- `read_transcript.py` had no vault-specific hardcoding, but its `--list` default and
  `archive_session.py`'s resolution logic were inconsistent (`SESSION_LOG_PENDING` vs
  `SESSION_LOG_DIR`). Harmonised: `--list` now tries `SESSION_LOG_PENDING` first (an
  explicit override, unchanged), then falls through to the same `SESSION_LOG_DIR` ->
  pointer-file -> default chain the other two scripts use, rather than jumping straight to
  a bare local default.
- All three scripts were run standalone after porting, with no MCP/tool context: with
  `SESSION_LOG_DIR` set, with only the pointer file set (no env var), and with neither set
  (falls through to the local default and behaves as a quiet no-op, per the source's
  original design). All three paths worked as intended - see this run's report for the
  exact commands.
- `plugins/marcketplace/hooks/hooks.json` wires both hooks via
  `${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py`, replacing the source's hand-edited
  `settings.json` instructions. The Windows-path variant and the `matcher` note from the
  source's install section were dropped as installation footnotes no longer relevant once
  the plugin resolves its own root.

**Not a handler.** Per the task brief, `session-log` never appears in
`handler-contract.md`'s category table and carries no `## Handler mode` heading - it runs
on the user's own invocation or the pending-sessions queue, never on a surface tick.

**Decisions made where the source skill was silent:**
- **Who writes the pointer file, and when.** The source never had this problem (a single
  hardcoded path). Decided: the skill itself writes it, on step 1 of every run, once the kb
  root is actually resolved - not onboarding, since onboarding's own pointer-file
  convention is scoped to the profile document, not to a skill-specific local cache. Open
  question for the orchestrator: whether a second skill that also needs a local kb path
  cache should reuse this exact pointer file name/shape, or whether each skill should own
  its own - I used a skill-specific filename (`session-log-dir.ref`) rather than a shared
  one, on the assumption that a shared kb-local-root cache doesn't yet exist as a documented
  convention anywhere in `shared/`.
- **`known_fact_errors` as an optional Need.** `profile-schema.md`'s key-by-key table lists
  only `kb-dream` as a reader. This skill's source content (the vendor-name correction, the
  "Names - check before you write them" section) reads as exactly the standing-correction
  use case `known_fact_errors` exists for, distinct from `people_confusions`'s name-
  collision scope. I listed it as optional in `## Needs` rather than silently expanding the
  schema (frozen for this run) or inventing a new key - flagging here per `PORTING.md`'s
  "Inventing profile keys" caution. See `profiles/extract/session-log.local.md`'s notes
  section for the exact source lines.
- **`kb.tag_hints`'s real value includes a product codename**, per
  `vault-conventions.md`'s tag-cluster counts. Recorded faithfully in the extract file
  (which is not scrub-checked, per `PORTING.md` step 11) with a note explaining the
  fictionalisation, per the extract/fictionalise split `PORTING.md` step 1 describes;
  every ported reference uses a placeholder cluster instead.

**Nothing was dropped without a generalised home**, except the vault-conventions.md
inventory tables named above (type-value counts, six-key coverage percentages, tag-cluster
counts, optional-key-usage counts) - these were observational snapshots of one vault's
current state, exactly the kind of thing the type-registry rule warns against trusting as
ongoing fact. Their *lessons* (all six frontmatter keys, always; reuse tags; provenance
semantics; type registry is live-only) survive in `kb-conventions.md`; their specific
counts do not, because a count from one audit of one vault is not a rule any other
knowledge base should inherit.

**Open questions for the orchestrator**, beyond the two flagged above:
- `kb.log_size_cap_kb.writers` is not extractable from this source skill at all (see the
  extract file's notes). The schema default (20 KB) is used implicitly by pointing at
  `kb-conventions.md`'s log-size-cap rule; flagging in case `kb-dream`'s own port (running
  concurrently in this same wave) supplies a real observed value worth reconciling against.
- The pointer-file naming decision above (`session-log-dir.ref`, skill-specific rather than
  a shared kb-local-root cache) is a judgement call with no precedent in `shared/` to check
  it against - worth a second look once more than one skill needs local-path caching for a
  standalone script.
