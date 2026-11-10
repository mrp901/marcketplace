# Profile schema

## Purpose

The profile is the one document that says who the user is and which organisation this
install runs for. It lives in a cloud-connector document the user owns (a Confluence page
or a SharePoint/OneDrive file, picked at first run per `onboarding.md`) - never as a file
in this repository and never local-only. A real user's filled-in profile is private data;
`profiles/example.md` in this repo is a fictional stand-in used as the bootstrap skeleton
and the eval fixture, nothing more.

The profile never holds cursors, tallies, run history or per-machine tool prefixes - that
is all state, described in `state-schema.md`, a sibling document the profile points to via
`state_ref`. Keeping the two separate matters because they are written at very different
rates and by very different owners; see state-schema.md's "Why two documents" section for
the full reasoning. The profile changes rarely and only the user (or onboarding, on the
user's behalf, once) writes to it; skills only read it, except to fill in a key that was
missing and has just been asked or discovered.

## The commented YAML

```yaml
profile_version: 1
state_ref:                 # pointer to the sibling state doc, e.g. confluence:<cloudId>/<pageId>

org:
  name:                    # organisation's full name
  product_scope:           # the product or product area this install is scoped to
  product_tag:             # short tag used to qualify tickets/ideas as in-scope (e.g. a summary marker)
  modules_context:         # one line of product/domain context a skill can quote verbatim
  timezone:                # IANA zone, e.g. Australia/Sydney

user:
  name:                    # display name
  email:                   # primary work email
  chat_user_id:            # chat service's user id for this person
  tracker_account_id:      # tracker service's account id for this person

tools:                     # which SERVICE serves each category; prefixes live in state.machines
  chat: {service: slack}
  email: {service: outlook | gmail}
  calendar: {service: outlook | google_calendar}
  tracker: {service: jira}
  ideas: {service: jira_product_discovery}
  wiki: {service: confluence | sharepoint}
  notetaker: {service: granola | otter | fireflies | teams | none, tested: false}
  kb: {service: sharepoint | device_bridge | filesystem}
  codebase: {service: device_bridge | filesystem | none}
  codehost: {service: github | none}                     # optional; action-list reads merged pull requests
  web: {service: websearch}
  page: {service: claude_artifact | confluence | none}   # publishes idea-spar's shareable pack

chat:
  team_id:                 # chat workspace/team id
  team_url:                 # chat workspace URL, e.g. https://<org>.slack.com
  tracker_feed_channels:    # channels where an automation posts tracker events; briefing cross-checks them
    work_started:           # channel id, or none; claims that work started on an issue
    fix_version:            # channel id, or none; claims that an issue's fix version was set or changed

calendar:
  day_window: "00:00-23:59 local"

briefing:
  stale_after_business_days: 5   # optional; business days of no activity before briefing expires a stuck line; 0 disables
  expected_runs:             # skill -> max days between runs before the Runs report calls it overdue
    proactive-router: 2
    action-sweep: 8
    idea-spar: 8
    kb-dream: 8
    skill-health-check: 8

tracker:
  cloud_id:                 # tracker's cloud/site id
  site_url:                 # tracker's base URL
  project_key:               # the day-to-day delivery project
  issue_types: {story, epic, bug}    # name -> id map, filled by discovery
  component: {name, id}
  default_parent_epic:       # ticket key new small tickets parent to by default
  ticket_template:           # which ticket-draft template shape to use
  parked_prefix: "[PARKED]"
  my_work_jql:                # JQL fragment for "assigned/reported/watched by me"

ideas:
  project_key:                # the ideas-board project
  issue_type: {name, id}
  area_field:                  # custom field that carries the product-area tag
  area_value:                   # the value that qualifies an idea as in scope
  roadmap_field:                 # custom field that carries roadmap slot (the Next watch's trigger, never a qualifier)
  qualifiers: [summary_has_product_tag, area_field_has_area_value, assignee_is_me]  # first-match gate
  next_roadmap_values: ["Next"]   # roadmap slots that mean "about to be worked"; an idea moving into one gets a pack

notetaker:
  lookback_days: 7
  prep_lines: true

kb:
  name:                        # display name of the knowledge base
  kind: obsidian_typed | plain_markdown | notion | confluence   # any kind beginning obsidian_ is read as obsidian_typed
  local_root:                   # local path, if a device bridge is used
  remote: {service, library, path_prefix}
  conventions_file: CLAUDE.md
  types_registry:                # where the type vocabulary lives
  people_file:                    # where the name/role/nickname registry lives
  link_style: relative_markdown | wikilink
  link_pass: surface | auto          # default surface: propose additions, never add them unattended
  draft_stale_days: 30               # a transient draft untouched this long is reaped
  frontmatter_required: [type, title, description, tags, status, generated]
  tag_hints: []
  paths:
    inbox:
    drafts:
    research:
    screenshots:
    sessions:
    dreams:
    decisions:
    memory:
    voice:
    log:
    product_index:
    service_map:
    utility:
    customers:                       # optional; one living note per customer, shared/customer-notes.md
  log_size_cap_kb: {writers: 20, dream: 40}
  sweep_queries: []

codebase:
  path:
  access: device_bridge | local | none

surface:
  kind: slack_canvas
  id:
  url:
  home_channel_id:

notify:
  mode: webhook | chat_message | none
  fallback_channel_id:
  mention_form: markdown_link
  webhooks: {briefing}       # the only webhook since 1.1.0; any other per-skill key here is unused and ignored
  proof_of_life: {}          # unused since 1.1.0: briefing.expected_runs is the proof of life

people: [{name, nickname, chat_id, email, role, decision_maker}]
people_confusions: []      # known mis-merges, transcription errors
known_fact_errors: []      # facts that have been wrong before and must not silently reintroduce

voice:
  guide_path: Voice/
  registers: [teammate_chat, exec_update, customer_facing, ticket_prose]
  calibration_refs: []
  calibrated_at:
  sample_counts: {}

budgets:
  briefing: {connector_calls: 3, notetaker_calls: 1, surface_reads: 1, surface_writes: 1, feed_issue_keys: 20}
  proactive-router: {thread_reads: 6, dispatches: 3}
  action-sweep: {canvas_guard: 5, cold_start_days: 7, targeted_search_per_todo: 1, thread_reads: 6, chat_pages: 3}
  jira-story:     {investigation_calls: 4, web_searches: 1, audit_rounds: 2}   # idea mode only
  idea-spar: {web_searches: 4, code_reads: 8, kb_reads: 3, findings_per_lens: 5, sketch_options: 3, next_per_run: 1}
  kb-dream: {incremental_reads: 25, sessions_incremental: 5, sessions_full: 10, customers_per_pass: 3, reviews: monthly, health: {window_days: 7}}   # health optional: lookup_pattern (regex), thresholds {<signal key>: [green_edge, amber_edge]}
  skill-health-check: {kb_reads: 15}
  models: {worker: sonnet, search: haiku, critic: opus}
```

## Key-by-key table

| Key | Readers (skills) | Source | Notes |
|---|---|---|---|
| `profile_version` | onboarding (all skills, via the shared procedure) | default | bumped only when the shape changes |
| `state_ref` | onboarding (all skills) | ask (set once at bootstrap) | never guessed; onboarding step 2 fails fast without it |
| `org.name` | all skills (org context in prose and notes) | ask | |
| `org.product_scope` | all skills | ask | |
| `org.product_tag` | idea-spar, jira-story (idea mode), proactive-router | ask | used by `ideas.qualifiers: summary_has_product_tag` |
| `org.modules_context` | briefing, idea-spar | ask | one line, quoted verbatim, not summarised |
| `org.timezone` | briefing, kb-dream, action-sweep, session-log, action-list | discover (system clock) | |
| `user.name` | briefing, kb-dream, reply-draft, session-log, action-list | ask | |
| `user.email` | reply-draft, session-log, kb-dream (voice calibration) | discover (chat auth test) | |
| `user.chat_user_id` | briefing, proactive-router, action-sweep, kb-dream, action-list | discover (chat auth test) | |
| `user.tracker_account_id` | action-sweep, jira-story (idea mode), briefing, action-list | discover (tracker "myself") | |
| `tools.*` | onboarding (all skills) | default, refined by discovery | prefixes never stored here, only the service name |
| `tools.<category>.cli` | onboarding step 4 (local CLI probe) | default (`auto`) | `off` skips the local CLI probe for that category; see `tool-capabilities.md` "Local CLI first" |
| `chat.team_id` | briefing, kb-dream | discover (parsed from surface URL) | |
| `chat.team_url` | briefing, kb-dream | discover (parsed from surface URL) | |
| `chat.tracker_feed_channels.work_started` | briefing | ask | identity-shaped: never defaulted. A channel id, or `none` if the install has no such feed |
| `chat.tracker_feed_channels.fix_version` | briefing | ask | same as `work_started` |
| `calendar.day_window` | briefing | default | |
| `briefing.stale_after_business_days` | briefing | default | 5; `0` disables expiry. Mon-Fri in `org.timezone`, public holidays not excluded |
| `briefing.expected_runs` | briefing | default | one entry per scheduled skill; a skill missing from the map is never called overdue |
| `tracker.cloud_id` | briefing, action-sweep, idea-spar, jira-story, skill-health-check, action-list | discover (accessible-resources) | |
| `tracker.site_url` | same as `tracker.cloud_id` | discover (accessible-resources) | |
| `tracker.project_key` | action-sweep, action-list, jira-story | ask | |
| `tracker.issue_types` | action-sweep, action-list, jira-story | discover (create-metadata) | |
| `tracker.component` | action-sweep, jira-story (idea mode), action-list | default (may be empty) | |
| `tracker.default_parent_epic` | action-sweep, jira-story | ask | |
| `tracker.ticket_template` | action-sweep, jira-story | default | |
| `tracker.parked_prefix` | action-sweep | default | |
| `tracker.my_work_jql` | briefing, action-sweep, action-list | default | |
| `ideas.project_key` | idea-spar, jira-story (idea mode) | ask | |
| `ideas.issue_type` | idea-spar, jira-story (idea mode) | discover (create-metadata) | |
| `ideas.area_field` | idea-spar, jira-story (idea mode) | discover (create-metadata) | |
| `ideas.area_value` | idea-spar, jira-story (idea mode) | ask | |
| `ideas.roadmap_field` | idea-spar (Next watch) | discover (create-metadata) | the trigger, never a qualifier |
| `ideas.qualifiers` | idea-spar (Next watch), jira-story (idea mode) | default | first-match gate, generalised from the source's single hardcoded gate |
| `ideas.next_roadmap_values` | idea-spar (Next watch) | default | the slots that mean "about to be worked"; moving into one is the only roadmap change that produces a pack |
| `notetaker.lookback_days` | action-sweep, briefing, action-list | default | not read when `tools.notetaker.service` is `none` |
| `notetaker.prep_lines` | briefing | default | |
| `kb.name` | session-log, kb-dream, idea-spar, action-sweep, action-list | ask | |
| `kb.kind` | session-log, kb-dream, action-list, jira-story | ask | `obsidian_typed`, `plain_markdown`, `notion` or `confluence`; any value beginning `obsidian_` is read as `obsidian_typed` (nothing branches on `kb.kind` except `confluence`) |
| `kb.local_root` | session-log, kb-dream (health verdict), action-list | default (empty until a device bridge is linked) | |
| `kb.remote` | session-log, kb-dream, action-list | default | |
| `kb.conventions_file` | session-log, kb-dream, action-list, jira-story | default | |
| `kb.types_registry` | session-log, kb-dream, action-list | default | |
| `kb.people_file` | session-log, kb-dream, action-sweep, action-list | ask | name-collision key |
| `kb.link_style` | session-log, kb-dream, idea-spar, action-list, jira-story | ask | |
| `kb.frontmatter_required` | session-log, kb-dream, action-list, jira-story | default | |
| `kb.tag_hints` | session-log | default | |
| `kb.paths.*` | session-log, kb-dream, idea-spar, action-sweep, reply-draft (voice), action-list, jira-story | default (asked only for `inbox`/`sessions` if the org has no convention) | |
| `kb.paths.customers` | kb-dream (writes), reply-draft, action-list, jira-story, idea-spar (read first) | optional; default `Customers` if that folder exists, else the feature is off | `shared/customer-notes.md` |
| `kb.log_size_cap_kb` | session-log, kb-dream, idea-spar, action-list | default | |
| `kb.sweep_queries` | kb-dream | default | |
| `codebase.path` | idea-spar (reality lens) | optional | only asked if `codebase.access != none` |
| `codebase.access` | idea-spar (reality lens) | default | |
| `surface.kind` | proactive-router, briefing | default | |
| `surface.id` | proactive-router, briefing, idea-spar, action-sweep, kb-dream, skill-health-check, action-list | ask | every surface-owning skill needs it; action-list only reads the board for its backlog section |
| `surface.url` | same as `surface.id` | ask | |
| `surface.home_channel_id` | briefing, kb-dream (webhook fallback) | ask | |
| `notify.mode` | briefing | ask | briefing is the only skill that posts |
| `notify.fallback_channel_id` | briefing | ask | |
| `notify.mention_form` | briefing | default | |
| `notify.webhooks.briefing` | briefing | optional | the only webhook key read; per-skill keys left over from 1.0.0 are ignored |
| `notify.proof_of_life` | none | unused | kept in the shape so an old profile still parses; `briefing.expected_runs` replaced it |
| `people[]` | briefing, session-log, kb-dream, action-sweep, action-list | ask | |
| `people_confusions` | kb-dream, session-log, action-list | optional, starts empty | |
| `known_fact_errors` | kb-dream, session-log | optional, starts empty | |
| `voice.guide_path` | reply-draft, session-log, jira-story, kb-dream | default | |
| `voice.registers` | reply-draft, session-log, kb-dream, action-list, jira-story | default | the base four; further registers are discovered from `kb.paths.voice`, per `voice.md` |
| `voice.calibrated_at` | reply-draft, session-log, jira-story, kb-dream | default (empty until first calibration) | never asked, never defaulted to a fake date |
| `voice.calibration_refs` | jira-story (idea mode) | optional | Tracker keys whose prose is the strongest reference for the `ticket_prose` register. Weighted above general samples during calibration |
| `voice.sample_counts` | kb-dream | default | |
| `budgets.<skill>` | that skill only | default | a skill only ever reads its own subtree |
| `budgets.kb-dream.customers_per_pass` | kb-dream | default 3 | customer notes refreshed per incremental pass; the rest carry to the next |
| `budgets.kb-dream.health` | kb-dream | default | optional: `window_days` (default 7), `lookup_pattern` (regex for the consultation signal), `thresholds` (`{<signal key>: [green_edge, amber_edge]}`); moved here from `budgets.vault-pulse` in 1.11.0, which is still read as an alias for `window_days`, `lookup_pattern` and `thresholds` |
| `budgets.jira-story` | jira-story (idea mode) | default | `{investigation_calls, web_searches, audit_rounds}`; the pre-1.11.0 `budgets.idea-ticket` is read as this key |
| *Retired in 1.11.0* | none | none | `chat.starter_emoji`, `chat.include_saved_items`, `budgets.proactive-router.searches` (the reaction and saved-message sweep is gone), `briefing.expected_runs.vault-pulse` (`vault-pulse` folded into `kb-dream`; the briefing's overdue rule skips an `expected_runs` key that names a skill not installed, so it is never called overdue) and `budgets.vault-pulse` (read as an alias of `budgets.kb-dream.health`, see above). An old profile that still carries them parses and they may be deleted |
| `budgets.models` | idea-spar, skill-eval, action-list, jira-story | default | see `model-tiers.md` |

## Naming inside the `kb` block, and why it trips people

Two groups of keys live under `kb` and the difference is easy to mis-cite from memory:

- **Top level (`kb.<name>`)**: `kb.name`, `kb.kind`, `kb.local_root`, `kb.remote`,
  `kb.conventions_file`, `kb.types_registry`, `kb.people_file`, `kb.link_style`,
  `kb.frontmatter_required`, `kb.tag_hints`, `kb.log_size_cap_kb`, `kb.sweep_queries`.
  These describe the knowledge base itself: what it is, how to reach it, and the rules it
  keeps. There is one of each.
- **Under `kb.paths.<name>`**: `inbox`, `drafts`, `research`, `screenshots`,
  `sessions`, `dreams`, `decisions`, `memory`, `voice`, `log`, `product_index`,
  `service_map`, `utility`, and optionally `customers`. These are locations inside it: where a given kind of thing is
  written or found.

The trap is that `kb.paths` holds a few single files (`log`, `product_index`,
`service_map`) as well as folders, so "is it a file?" does not decide the group. The rule
that does: **`kb.paths` answers "where does this go?", everything else answers "what is
this knowledge base like?"** `kb.people_file` is a property of the knowledge base, so it
is top level; `kb.paths.sessions` is a destination, so it is not. When in doubt, check
this list rather than reasoning by analogy with a neighbouring key.

## Discovery procedures

- **`user.email`, `user.chat_user_id`** - chat auth test with no user id argument; the
  response names the authenticated user.
- **`user.tracker_account_id`** - tracker "myself" endpoint.
- **`tracker.cloud_id`, `tracker.site_url`** - tracker "accessible resources" call; the
  first (or only) resource is the cloud id and base URL.
- **`tracker.issue_types`, `ideas.issue_type`, `ideas.area_field`, `ideas.roadmap_field`** -
  tracker "create metadata" for the relevant project; read the field and issue-type ids
  off the response rather than asking the user to know them.
- **`chat.team_id`, `chat.team_url`** - parsed out of the surface URL the user gave for
  `surface.url` (a chat canvas/doc URL carries the team id as a path segment).
- **`chat.tracker_feed_channels.*`** - not discoverable. Ask which channel carries each
  feed. A channel link the user pastes carries the id. A bare name is looked up with the
  chat connector only if exactly one channel matches it, and is asked again otherwise. The
  user can answer `none` for a feed the install doesn't have; that is recorded literally,
  and a missing key is never turned into `none`.
- **`org.timezone`** - the system clock's configured zone at onboarding time, confirmed
  once, not re-derived every run.
- **tool prefixes** (not stored in the profile; land in `state.machines`) - `ToolSearch`
  per category, per onboarding step 4.

## Adding a key

A key is added to this schema only when some skill's `## Needs` heading actually requires
it - never speculatively, never "in case a future skill wants it". Every key ships with a
default in this document (even if that default is an empty value) so a fresh profile is
never missing a key outright, with one exception: **identity keys are never defaulted.**
`user.*`, `org.name`, `state_ref`, `surface.id`, `chat.team_id`, the channel ids
(`surface.home_channel_id`, `notify.fallback_channel_id`, `chat.tracker_feed_channels.*`)
and anything else that names a specific person, organisation, document or channel must be
asked or discovered - a plausible-looking default for an identity key is worse than a
missing one, because a missing key fails loudly and a wrong default fails silently.
