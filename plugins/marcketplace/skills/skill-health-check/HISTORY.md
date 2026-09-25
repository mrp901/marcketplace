# skill-health-check - design rationale (for editors; not loaded at runtime)

## 2026-09-22 port to marcketplace

Renamed from `skill-health-check` (source skill of the same name; no rename needed). Ported
per `PORTING.md`. The source skill had no `HISTORY.md` of its own, so this file starts here.

**Behaviours carried over, unchanged in substance:**
- It never edits a skill, never calls `skill-eval` or a skill-proposal tool, never schedules
  anything. This is the single most load-bearing property of the skill and nothing in the
  port touches it.
- Scoring is always against gathered evidence, never an impression; a skill with nothing
  gatherable is skipped rather than scored thin.
- Green is quiet on the surface (still gets a log entry and a webhook, per the source's own
  "webhook call for the record, no canvas item" behaviour).
- The `.utility/` boundary: no frontmatter, never indexed, never curated by `kb-dream`'s
  passes - this is tooling about the skills, not knowledge about the org.
- Reading the top of a skill's own log first and only gathering evidence dated after it.
- The log entry shape (dated heading, evidence window, 2-4 bullets, evidence-sources line)
  and the green/amber/red tags.
- "Never tick or remove a canvas item here" and "a repeated amber gets its own new line" -
  carried into the new acknowledge-section surface rules unchanged.

**Behaviours added (per the porting brief):**
- **Roster now derives from the plugin.** `scripts/list_roster.py` enumerates skill
  directories under `skills/` rather than the source's hardcoded eight-skill list. A named
  skill still scores just that one; an unnamed run skips any skill with no evidence since its
  last check.
- **Two new evidence sources**, both read straight off the state document already read every
  run at no extra connector cost: the hub's `state.outcomes`/`state.tally` (repeated
  `blocked`/`partial`, or a category whose lines keep getting edited), and the voice ledger
  (`state.voice_edits`) for drafting skills. See `references/evidence-gathering.md`.
- **The cursor moved into state.** `state.cursors.skill-health-check.last_checked.<skill>` is
  now the primary "since when" pointer (the schema already defined this key); the log file's
  own top entry is kept as a fallback read for a skill state hasn't got a cursor for yet,
  rather than the sole source of truth the source skill used.
- **The relationship to `skill-eval` is now explicit** in `SKILL.md`'s prose and in
  `references/log-format.md`'s surface-line example: a red result with an obvious diagnosis
  may name `skill-eval` as the next step, but this skill never runs it and never drafts the
  edit.
- **Two deterministic scripts** added per PORTING.md step 8's rule (a mechanically-checkable
  rule gets a script, not a paragraph): `scripts/list_roster.py` for the roster itself, and
  `scripts/check_log_entry.py` to validate a proposed log entry's shape before it's written.
  Neither existed in the source skill.

**Behaviours dropped, and why:**
- Nothing was dropped outright. The source's "ask once whether to include a custom skill in
  the roster" no longer applies, because the new roster derivation makes every installed
  skill part of the roster by construction - there's no hardcoded list to fall behind, so
  nothing to ask about.

**Decisions made where the source skill was silent:**
- **Whether `skill-eval` and `proactive-router` sit in their own roster.** The source's
  roster excluded both implicitly (its list named eight specific skills, and neither
  appeared). The new roster derivation includes every installed skill directory except this
  skill's own by construction, so both are now in-roster by default. In practice both will
  usually be skipped at step 1 for lack of gatherable evidence - `skill-eval` edits
  `SKILL.md` files, which nothing in `state-schema.md` tracks provenance for, and
  `proactive-router`'s own output *is* the outcomes/tally record this skill reads about other
  handlers, not a kb note or ticket of its own. I left both in the roster rather than
  special-casing an exclusion, since "no evidence, so skipped" already produces the right
  behaviour without a second exclusion list to maintain. **Open question for the
  orchestrator:** confirm this is the right call, or say explicitly that `skill-eval` and/or
  `proactive-router` should be permanently excluded from the roster the way this skill excludes
  itself.
- **Which tool verb covers "was this ticket edited shortly after creation".**
  `tool-capabilities.md` has no changelog/history verb for the tracker category; I used
  `tracker: get issue` (which the table already says fetches "full fields, comments, links")
  read alongside the search result's own `created`/`updated` timestamps as a proxy, rather
  than inventing a new verb. This is an approximation - it catches "the ticket has changed
  since creation" but not a full field-by-field diff. **Open question for the orchestrator:**
  a `tracker: get changelog` verb, if the underlying connectors support one cheaply, would
  make this evidence sharper.
- **`profile.budgets.skill-health-check` does not exist in `profile-schema.md`.** Every other
  budget-carrying skill has a `budgets.<skill>` entry in the schema's YAML and key-by-key
  table; this skill does not. I referenced `budgets.skill-health-check.kb_reads` (default 15)
  in `SKILL.md`'s Budget section as a placeholder shaped like its siblings, per PORTING.md's
  "use the closest existing key or a placeholder... flag it, do not invent it" rule. **Flag
  for the orchestrator:** add a `budgets.skill-health-check` row to `profile-schema.md` (and
  to `profiles/example.md`'s `budgets:` block) with real defaults, or say explicitly that
  this skill runs unbudgeted against the shared per-connector-call degradation rules alone.

**Nothing else was dropped.** The source install's own values (org name, canvas id/url, chat
team id, the skill-health-check webhook URL, the illustrative `IG-*` ticket keys in the
worked log entry) all moved to `profile.*`/fictionalised examples - see
`profiles/extract/skill-health-check.local.md`.

**Open questions for the orchestrator, collected:**
1. Should `skill-eval` and/or `proactive-router` be permanently excluded from the roster,
   rather than left to be skipped for lack of evidence each run?
2. Is a `tracker: get changelog` verb worth adding to `tool-capabilities.md` for sharper
   "was this materially edited" evidence?
3. `profile.budgets.skill-health-check` needs a real home in `profile-schema.md` and
   `profiles/example.md` - it does not exist yet and this port only placeholders it.

## 2026-09-25 canvas redesign (1.1.0): every tick means yes, do it

Only a red score reaches the board now, as a `(shc:…) 🔴 <skill> scored red: <why>. Run
skill-eval on it?` line; amber and green go to `runs.skill-health-check.scores` and the
briefing's Runs block. A tick on a red line is queued by the Router, never dispatched:
`skill-eval` stays manual and lists queued lines as candidates. This skill took over the
"output keeps getting edited" signal from `kb-dream`'s registry review (it already read
the tally and the voice ledger), with stated thresholds in
`references/evidence-gathering.md`. The per-skill webhook is gone. Of the port's open
questions, the roster one stands as decided then; `budgets.skill-health-check` has had
its schema row since the 1.0.0 orchestrator pass.
