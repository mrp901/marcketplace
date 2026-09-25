# Example profile - Northwind Logistics

This file is two things at once, deliberately:

1. **The bootstrap skeleton.** Onboarding (`plugins/marcketplace/shared/onboarding.md`)
   copies this shape when it creates a brand new profile document for someone - filling
   in their real answers over these fictional ones.
2. **The eval fixture.** Every ported skill's evals run against this exact profile, so its
   values need to be plausible, complete and stable rather than realistic-sounding filler.

**A real profile never lives in this repository.** It lives in a cloud-connector document
the user owns - a Confluence page or a SharePoint/OneDrive file - per
`plugins/marcketplace/shared/onboarding.md`. This file is fictional throughout: Northwind
Logistics is not a real company, Freight Ops is not a real product, and every id, person
and URL below is invented for this purpose. Every key here matches
`plugins/marcketplace/shared/profile-schema.md` exactly - see "Verify before you finish"
in that porting run's report for the mechanical check.

```yaml
profile_version: 1
state_ref: confluence:8f2e4a91-example-cloud-id/990111222

org:
  name: Northwind Logistics
  product_scope: Freight Ops
  product_tag: "[Freight]"
  modules_context: Freight Ops is the load-planning and dock-scheduling product for mid-size carriers.
  timezone: Australia/Sydney

user:
  name: Priya Kanth
  email: priya.kanth@northwindlogistics.example
  chat_user_id: W1EXAMPLEUSR1
  tracker_account_id: 5f3a2b:99887766-1122-3344-5566-778899aabbcc

tools:
  chat: {service: slack}
  email: {service: outlook}
  calendar: {service: outlook}
  tracker: {service: jira}
  ideas: {service: jira_product_discovery}
  wiki: {service: confluence}
  notetaker: {service: granola, tested: false}
  kb: {service: sharepoint}
  codebase: {service: device_bridge}
  web: {service: websearch}

chat:
  team_id: TEXAMPLE001
  team_url: https://northwindlogistics.slack.com
  starter_emoji: [envelope, ticket, book, star]
  include_saved_items: true

calendar:
  day_window: "00:00-23:59 local"

briefing:
  expected_runs:
    proactive-router: 2
    action-sweep: 8
    idea-scout: 8
    idea-wireframe: 8
    kb-dream: 8
    skill-health-check: 8

tracker:
  cloud_id: 8f2e4a91-3c7d-4b2e-9a11-example000fc
  site_url: https://northwindlogistics.atlassian.net
  project_key: FLT
  issue_types: {story: 20001, epic: 20000, bug: 20002}
  component: {name: Platform, id: 30010}
  default_parent_epic: FLT-401
  ticket_template: standard
  parked_prefix: "[PARKED]"
  my_work_jql: "assignee = currentUser() OR reporter = currentUser() OR watcher = currentUser()"

ideas:
  project_key: FIG
  issue_type: {name: Idea, id: 20372}
  area_field: "cf[20067]"
  area_value: "Freight Ops"
  roadmap_field: "cf[20054]"
  labels: {investigated: investigated, wireframed: wireframed}
  qualifiers: [summary_has_product_tag, area_field_has_area_value, assignee_is_me]
  parked_roadmap_values: ["Someday", "Parking lot"]

notetaker:
  lookback_days: 7
  prep_lines: true

kb:
  name: Northwind Ops Vault
  kind: obsidian_okf
  local_root: ""
  remote: {service: sharepoint, library: "Northwind Ops Vault", path_prefix: "Vault/Northwind Ops"}
  conventions_file: CLAUDE.md
  types_registry: References/okf-conventions.md
  people_file: Org/people-and-org.md
  link_style: relative_markdown
  link_pass: surface
  draft_stale_days: 30
  frontmatter_required: [type, title, description, tags, status, generated]
  tag_hints: [freight, ops, discovery]
  paths:
    inbox: Inbox/
    research: Product/FreightOps/Research/
    prototypes: Product/FreightOps/Prototypes/
    screenshots: References/Images and Screenshots/Screenshots/
    sessions: Sessions/
    dreams: Dreams/
    decisions: Decisions/
    memory: Memory/
    voice: Voice/
    log: log.md
    product_index: Product/FreightOps/index.md
    service_map: Product/service-map.md
    utility: .utility/
  log_size_cap_kb: {writers: 20, dream: 40}
  sweep_queries: ["freight ops dashboard", "dock scheduling", "competitor brief"]

codebase:
  path: ~/dev/freight-ops
  access: device_bridge

surface:
  kind: slack_canvas
  id: FEXAMPLECANVAS1
  url: https://northwindlogistics.slack.com/docs/TEXAMPLE001/FEXAMPLECANVAS1
  home_channel_id: CEXAMPLEHOME01

notify:
  mode: webhook
  fallback_channel_id: CEXAMPLEHOME01
  mention_form: markdown_link
  webhooks:
    briefing: https://hooks.example-chat.invalid/triggers/TEXAMPLE001/00000001/briefingexample
  proof_of_life: {}

people:
  - {name: Priya Kanth, nickname: Priya, chat_id: W1EXAMPLEUSR1, email: priya.kanth@northwindlogistics.example, role: Product Manager, decision_maker: true}
  - {name: Tomasz Wieckowski, nickname: Tomasz, chat_id: W2EXAMPLEUSR2, email: tomasz.w@northwindlogistics.example, role: Engineering Lead, decision_maker: true}
  - {name: Ana Beltrao, nickname: Ana, chat_id: W3EXAMPLEUSR3, email: ana.beltrao@northwindlogistics.example, role: Designer, decision_maker: false}
  - {name: Owen Fairclough, nickname: Owen, chat_id: W4EXAMPLEUSR4, email: owen.fairclough@northwindlogistics.example, role: Support Lead, decision_maker: false}

people_confusions:
  - "Two people named Ana on the Ops team; this profile's Ana Beltrao is Design, not Ana Souza in Support."

known_fact_errors:
  - "Dock-scheduling module does not yet support multi-yard allocation - reintroduced by mistake once, corrected 2026-08-02."

voice:
  guide_path: Voice/
  registers: [teammate_chat, exec_update, customer_facing, ticket_prose]
  calibration_refs: [FIG-118, FIG-131]
  calibrated_at: ""
  sample_counts: {}

budgets:
  briefing: {connector_calls: 3, notetaker_calls: 1, surface_reads: 1, surface_writes: 1}
  proactive-router: {searches: 5, thread_reads: 6, dispatches: 3}
  action-sweep: {canvas_guard: 5, cold_start_days: 7, targeted_search_per_todo: 1, thread_reads: 6}
  idea-scout: {web_searches: 4, kb_notes: 3, note_words: 800}
  idea-deep-dive: {loop_budget: 8, circle_caps: {kb: 2, people: 2, code: 3, web: 4}, depth_cap: 3}
  idea-wireframe: {pngs: 5, competitor_pngs: 2, md_reads: 5, html_lines: 300, critic_rounds: 1}
  kb-dream: {incremental_reads: 25, sessions_incremental: 5, sessions_full: 10, reviews: monthly}
  skill-health-check: {kb_reads: 15}
  models: {worker: sonnet, search: haiku, critic: opus}
```

## Keys a real user must answer on first run

Onboarding asks a single batched question, per skill, only for the keys that skill's
`## Needs` requires and that discovery could not fill in. Across the whole plugin, these
are the keys onboarding classifies `ask` (see `profile-schema.md`'s "Key-by-key table")
and that a real first run will actually prompt for:

- `org.name`, `org.product_scope`, `org.product_tag`, `org.modules_context`
- `user.name`
- `tracker.project_key`, `tracker.default_parent_epic`
- `ideas.project_key`, `ideas.area_value`
- `kb.name`, `kb.kind`, `kb.people_file`, `kb.link_style`
- `surface.id` (and its URL)
- `notify.mode` (and `notify.fallback_channel_id` if webhook delivery is ever unreachable)
- `people` (at least the decision-makers)

Everything else is either discovered automatically (chat/tracker identity, cloud ids,
issue-type ids, timezone, tool prefixes) or ships with the default shown above.
