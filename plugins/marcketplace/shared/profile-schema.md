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
  notetaker: {service: granola | otter | fireflies | teams, tested: false}
  kb: {service: sharepoint | device_bridge | filesystem}
  codebase: {service: device_bridge | filesystem | none}
  web: {service: websearch}

chat:
  team_id:                 # chat workspace/team id
  team_url:                 # chat workspace URL, e.g. https://<org>.slack.com
  starter_emoji: [envelope, ticket, book, star]   # reaction set proactive-router polls for
  include_saved_items: true

calendar:
  day_window: "00:00-23:59 local"

briefing:
  expected_runs:             # skill -> max days between runs before the Runs report calls it overdue
    proactive-router: 2
    action-sweep: 8
    idea-scout: 8
    idea-wireframe: 8
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
  roadmap_field:                 # custom field that carries roadmap slot (reported, never qualifying)
  labels: {investigated, wireframed}
  qualifiers: [summary_has_product_tag, area_field_has_area_value, assignee_is_me]  # first-match gate
  parked_roadmap_values: ["Someday"]   # roadmap slots that mean parked; an idea leaving one gets a refresh question

notetaker:
  lookback_days: 7
  prep_lines: true

kb:
  name:                        # display name of the knowledge base / vault
  kind: obsidian_okf | plain_markdown | notion | confluence
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
    prototypes:
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
  briefing: {connector_calls: 3, notetaker_calls: 1, surface_reads: 1, surface_writes: 1}
  proactive-router: {searches: 5, thread_reads: 6, dispatches: 3}
  action-sweep: {canvas_guard: 5, cold_start_days: 7, targeted_search_per_todo: 1, thread_reads: 6}
  idea-ticket:    {investigation_calls: 4, web_searches: 1, audit_rounds: 2}
  idea-scout: {web_searches: 4, kb_notes: 3, note_words: 800}
  idea-deep-dive: {loop_budget: 8, circle_caps: {kb: 2, people: 2, code: 3, web: 4}, depth_cap: 3}
  idea-wireframe: {pngs: 5, competitor_pngs: 2, md_reads: 5, html_lines: 300, critic_rounds: 1}
  kb-dream: {incremental_reads: 25, sessions_incremental: 5, sessions_full: 10, reviews: monthly}
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
| `org.product_tag` | idea-scout, idea-ticket, proactive-router | ask | used by `ideas.qualifiers: summary_has_product_tag` |
| `org.modules_context` | briefing, idea-scout, idea-deep-dive, idea-wireframe | ask | one line, quoted verbatim, not summarised |
| `org.timezone` | briefing, kb-dream, action-sweep, session-log | discover (system clock) | |
| `user.name` | briefing, kb-dream, reply-draft, kb-note, session-log | ask | |
| `user.email` | reply-draft, kb-note, kb-dream (voice calibration) | discover (chat auth test) | |
| `user.chat_user_id` | briefing, proactive-router, action-sweep, idea-scout, idea-wireframe, kb-dream | discover (chat auth test) | |
| `user.tracker_account_id` | action-sweep, idea-ticket, briefing | discover (tracker "myself") | |
| `tools.*` | onboarding (all skills) | default, refined by discovery | prefixes never stored here, only the service name |
| `chat.team_id` | briefing, kb-dream, idea-scout, idea-wireframe | discover (parsed from surface URL) | |
| `chat.team_url` | briefing, kb-dream, idea-scout, idea-wireframe | discover (parsed from surface URL) | |
| `chat.starter_emoji` | proactive-router | default | |
| `chat.include_saved_items` | proactive-router | default | |
| `calendar.day_window` | briefing | default | |
| `briefing.expected_runs` | briefing | default | one entry per scheduled skill; a skill missing from the map is never called overdue |
| `tracker.cloud_id` | briefing, action-sweep, idea-scout, idea-deep-dive, idea-wireframe, idea-ticket, skill-health-check | discover (accessible-resources) | |
| `tracker.site_url` | same as `tracker.cloud_id` | discover (accessible-resources) | |
| `tracker.project_key` | action-sweep, idea-ticket | ask | |
| `tracker.issue_types` | action-sweep, idea-ticket | discover (create-metadata) | |
| `tracker.component` | action-sweep, idea-ticket | default (may be empty) | |
| `tracker.default_parent_epic` | action-sweep | ask | |
| `tracker.ticket_template` | idea-ticket, action-sweep | default | |
| `tracker.parked_prefix` | action-sweep | default | |
| `tracker.my_work_jql` | briefing, action-sweep | default | |
| `ideas.project_key` | idea-scout, idea-deep-dive, idea-wireframe, idea-ticket | ask | |
| `ideas.issue_type` | idea-scout, idea-deep-dive, idea-wireframe, idea-ticket | discover (create-metadata) | |
| `ideas.area_field` | idea-scout, idea-wireframe, idea-ticket | discover (create-metadata) | |
| `ideas.area_value` | idea-scout, idea-wireframe, idea-ticket | ask | |
| `ideas.roadmap_field` | idea-scout, idea-wireframe | discover (create-metadata) | reported, never a qualifier |
| `ideas.labels` | idea-scout, idea-wireframe | default | |
| `ideas.qualifiers` | idea-scout, idea-ticket | default | first-match gate, generalised from the source's single hardcoded gate |
| `ideas.parked_roadmap_values` | idea-scout (roadmap watch) | default | the slots that mean parked; leaving one is the only roadmap change that produces a board line |
| `notetaker.lookback_days` | action-sweep, idea-deep-dive, briefing | default | |
| `notetaker.prep_lines` | briefing | default | |
| `kb.name` | kb-note, session-log, kb-dream, idea-scout, idea-deep-dive, idea-wireframe, action-sweep | ask | |
| `kb.kind` | kb-note, session-log, kb-dream | ask | |
| `kb.local_root` | kb-note, session-log, kb-dream, idea-scout, idea-wireframe | default (empty until a device bridge is linked) | |
| `kb.remote` | kb-note, session-log, kb-dream, idea-scout, idea-wireframe | default | |
| `kb.conventions_file` | session-log, kb-dream, kb-note | default | |
| `kb.types_registry` | session-log, kb-dream | default | |
| `kb.people_file` | session-log, kb-dream, idea-scout, idea-wireframe, action-sweep | ask | name-collision key |
| `kb.link_style` | kb-note, session-log, kb-dream, idea-scout, idea-wireframe | ask | |
| `kb.frontmatter_required` | kb-note, session-log, kb-dream | default | |
| `kb.tag_hints` | kb-note, session-log | default | |
| `kb.paths.*` | kb-note, session-log, kb-dream, idea-scout, idea-deep-dive, idea-wireframe, action-sweep, reply-draft (voice) | default (asked only for `inbox`/`sessions` if the org has no convention) | |
| `kb.log_size_cap_kb` | session-log, kb-dream, idea-scout, idea-wireframe | default | |
| `kb.sweep_queries` | idea-wireframe, kb-dream | default | |
| `codebase.path` | idea-deep-dive | optional | only asked if `codebase.access != none` |
| `codebase.access` | idea-deep-dive | default | |
| `surface.kind` | proactive-router, briefing | default | |
| `surface.id` | proactive-router, briefing, idea-scout, idea-deep-dive, idea-wireframe, action-sweep, kb-dream, skill-health-check | ask | every surface-owning skill needs it |
| `surface.url` | same as `surface.id` | ask | |
| `surface.home_channel_id` | briefing, kb-dream (webhook fallback) | ask | |
| `notify.mode` | briefing | ask | briefing is the only skill that posts |
| `notify.fallback_channel_id` | briefing | ask | |
| `notify.mention_form` | briefing | default | |
| `notify.webhooks.briefing` | briefing | optional | the only webhook key read; per-skill keys left over from 1.0.0 are ignored |
| `notify.proof_of_life` | none | unused | kept in the shape so an old profile still parses; `briefing.expected_runs` replaced it |
| `people[]` | briefing, session-log, kb-dream, idea-scout, idea-wireframe, action-sweep | ask | |
| `people_confusions` | kb-dream, session-log | optional, starts empty | |
| `known_fact_errors` | kb-dream, session-log | optional, starts empty | |
| `voice.guide_path` | reply-draft, kb-note, idea-ticket, kb-dream | default | |
| `voice.registers` | reply-draft, kb-note, idea-ticket, kb-dream | default | |
| `voice.calibrated_at` | reply-draft, kb-note, idea-ticket, kb-dream | default (empty until first calibration) | never asked, never defaulted to a fake date |
| `voice.calibration_refs` | idea-ticket | optional | Tracker keys whose prose is the strongest reference for the `ticket_prose` register. Weighted above general samples during calibration |
| `voice.sample_counts` | kb-dream | default | |
| `budgets.<skill>` | that skill only | default | a skill only ever reads its own subtree |
| `budgets.models` | idea-ticket, idea-wireframe, idea-deep-dive, skill-eval | default | see `model-tiers.md` |

## Where the current values come from

This table is what a porting subagent uses to extract this install's real values into
`profiles/extract/<skill>.local.md`. Every pointer below was checked against the live
source file at the line or heading given; it points at *where* the value sits, never at
the value itself.

| Key | Source file | Line / heading |
|---|---|---|
| `user.chat_user_id` | `source/briefing/SKILL.md` | L12, "Fixed facts" bullet 1 |
| `notify.webhooks.briefing`, `notify.fallback_channel_id` | `source/briefing/SKILL.md` | L13, "Fixed facts" bullet 2 |
| `surface.id`, `surface.url` | `source/briefing/SKILL.md` | L14, "Fixed facts" bullet 3 |
| `tracker.cloud_id` | `source/briefing/SKILL.md` | L15, "Fixed facts" bullet 4 |
| `state_ref` | `source/briefing/SKILL.md` | L16, "Fixed facts" bullet 5 (Confluence page id and space) |
| `people[].chat_id` | `source/briefing/SKILL.md` | L17, "Fixed facts" bullet 6 (known Slack IDs) |
| `people[].nickname` | `source/briefing/SKILL.md` | L18, "Fixed facts" bullet 7 |
| `org.timezone` | `source/briefing/SKILL.md` | L21, "Time rules" intro line (Australia/Sydney convention, confirmed again at vault-dream L41) |
| `tracker.cloud_id`, `tracker.site_url` | `source/canvass/SKILL.md` | L48, "Fixed facts" bullet 1 |
| `user.tracker_account_id` | `source/canvass/SKILL.md` | L50, "Fixed facts" bullet 2 |
| `user.chat_user_id` (cross-check) | `source/canvass/SKILL.md` | L51, "Fixed facts" bullet 3 |
| `tracker.default_parent_epic` | `source/canvass/SKILL.md` | L52, "Fixed facts" bullet 4 |
| `tracker.project_key`, `tracker.issue_types`, `tracker.component` | `source/canvass/SKILL.md` | L55-56, "Fixed facts" bullet 5 |
| `ideas.project_key`, `ideas.issue_type`, `ideas.area_field`, `ideas.area_value` | `source/canvass/SKILL.md` | L57-58, "Fixed facts" bullet 6 |
| `kb.paths.inbox` | `source/canvass/SKILL.md` | L59, "Fixed facts" bullet 7 |
| `kb.remote.path_prefix`, `kb.remote.service` | `source/canvass/SKILL.md` | L62-63, "Fixed facts" bullet 8 |
| `ideas.area_field` (roadmap contrast) | `source/cloud-idea-scout/SKILL.md` | L23, "Fixed facts" bullet 2 |
| `ideas.labels.investigated` | `source/cloud-idea-scout/SKILL.md` | L24, "Fixed facts" bullet 3 |
| `user.email` | `source/cloud-idea-scout/SKILL.md` | L25, "Fixed facts" bullet 4 |
| `surface.id` (section name), `notify.webhooks.idea-scout` | `source/cloud-idea-scout/SKILL.md` | L26, "Fixed facts" bullet 5 |
| `kb.name`, `kb.paths.research` (Product/Cloud/Research) | `source/cloud-idea-scout/SKILL.md` | L27, "Fixed facts" bullet 6 |
| `ideas.qualifiers` (the three gate tests) | `source/cloud-idea-scout/SKILL.md` | L40-45, Step 1 body |
| `ideas.labels.wireframed` | `source/cloud-idea-wireframe/SKILL.md` | L28, "Fixed facts" bullet 3 |
| `surface.id` (section name), `notify.webhooks.idea-wireframe` | `source/cloud-idea-wireframe/SKILL.md` | L29, "Fixed facts" bullet 4 |
| `kb.local_root` | `source/cloud-idea-wireframe/SKILL.md` | L30, "Fixed facts" bullet 5 |
| `kb.paths.prototypes`, `kb.paths.screenshots` | `source/cloud-idea-wireframe/SKILL.md` | L31, "Fixed facts" bullet 6 |
| `kb.remote.service`, `kb.remote.library` | `source/cloud-idea-wireframe/SKILL.md` | L32, "Fixed facts" bullet 7 |
| `kb.name`, `kb.kind` | `source/vault-dream/SKILL.md` | L34, "Fixed facts" bullet 1 |
| `kb.remote.service` (access precedence) | `source/vault-dream/SKILL.md` | L35, "Fixed facts" bullet 2 |
| `surface.id`, `surface.home_channel_id`, `notify.webhooks.kb-dream` | `source/vault-dream/SKILL.md` | L36, "Fixed facts" bullet 3 |
| `kb.log_size_cap_kb.dream` | `source/vault-dream/SKILL.md` | L37, "Fixed facts" bullet 4 |
| `org.timezone` (TZ confirmation) | `source/vault-dream/SKILL.md` | L41, Step 0 point 1 |
| `people_confusions` | `source/vault-dream/SKILL.md` | L69, "Known errors for pass 6" |
| `known_fact_errors` | `source/vault-dream/SKILL.md` | L69, "Known errors for pass 6" (a mix of corrected figures, a wrongly-assumed process, a vendor name, and a scope claim) |
| `people_confusions` (cross-check), `known_fact_errors` (Granola misrenderings) | `source/session-log/SKILL.md` | L302 heading, paragraph L308-312, "Names - check before you write them" |
| `chat.team_id`, `chat.team_url` | `source/briefing/SKILL.md` | L14 (canvas URL carries both) |
| `chat.starter_emoji` | `source/proactive-router/SKILL.md` | L74-79, "Intent categories" table |
| `tracker.cloud_id` (audit step) | `source/cloud-idea-ticket/SKILL.md` | L133, "Fixed facts" (cloudId, with discovery fallback named inline) |
| `budgets.models.critic` (opus audit) | `source/cloud-idea-ticket/SKILL.md` | L107, Step 4 intro |
| `budgets.models.search` (haiku sub-dispatch) | `source/cloud-idea-deep-dive/SKILL.md` | L37, "Runtime strategy" bullet 2 |
| `budgets.models.critic` (wireframe critic) | `source/cloud-idea-wireframe/SKILL.md` | L92, Step 5 |
| `budgets.models.critic` (skill-eval synthesis) | `source/skill-eval/SKILL.md` | L55, Step 2 intro |

**Corrections to PLAN.md's pointers.** The plan's summary table cited two lines that do
not hold what it said:

- `people_confusions` was cited in PLAN.md as "session-log L308-315". The actual heading
  ("Names - check before you write them") starts at L302, and the Daves/Aleksandrs/Granola
  paragraph it points at runs L308-312, not to L315 - L313-315 is blank line plus the start
  of the next paragraph on ambiguous names, which does not carry the fixed facts. Corrected
  above to L302 (heading) / L308-312 (paragraph).
- The plan's YAML comment for `known_fact_errors` did not name a source at all; added the
  vault-dream L69 known-errors sentence above, since that is where the source install's actual
  corrected-fact list lives.

## Naming inside the `kb` block, and why it trips people

Two groups of keys live under `kb` and the difference is easy to mis-cite from memory:

- **Top level (`kb.<name>`)**: `kb.name`, `kb.kind`, `kb.local_root`, `kb.remote`,
  `kb.conventions_file`, `kb.types_registry`, `kb.people_file`, `kb.link_style`,
  `kb.frontmatter_required`, `kb.tag_hints`, `kb.log_size_cap_kb`, `kb.sweep_queries`.
  These describe the knowledge base itself: what it is, how to reach it, and the rules it
  keeps. There is one of each.
- **Under `kb.paths.<name>`**: `inbox`, `drafts`, `research`, `prototypes`, `screenshots`,
  `sessions`, `dreams`, `decisions`, `memory`, `voice`, `log`, `product_index`,
  `service_map`, `utility`. These are locations inside it: where a given kind of thing is
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
- **`org.timezone`** - the system clock's configured zone at onboarding time, confirmed
  once, not re-derived every run.
- **tool prefixes** (not stored in the profile; land in `state.machines`) - `ToolSearch`
  per category, per onboarding step 4.

## Adding a key

A key is added to this schema only when some skill's `## Needs` heading actually requires
it - never speculatively, never "in case a future skill wants it". Every key ships with a
default in this document (even if that default is an empty value) so a fresh profile is
never missing a key outright, with one exception: **identity keys are never defaulted.**
`user.*`, `org.name`, `state_ref`, `surface.id` and anything else that names a specific
person, organisation or document must be asked or discovered - a plausible-looking default
for an identity key is worse than a missing one, because a missing key fails loudly and a
wrong default fails silently.
