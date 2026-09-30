# proactive-router sweep harness (subagent runs, no API spend)

Local stand-in for `claude plugin eval` on the `21..25-sweep-real-w*` cases: a Claude Code subagent follows the live SKILL.md against a deterministic mock, and Haiku subagents judge the writes.

- `build_worlds.py` - builds the five eval cases and `evals/sweep-real-labels.json` from `inputs_fict.json` + `inputs_chatreply.json` (fictional Northwind world; no real data).
- `mock_tools.py --run <dir> --world wN <tool> ...` - serves the world's Slack/Confluence fixtures and logs every call to `<dir>/mock_calls.jsonl`.
- `grade.py packet <dir> wN` - writes `judge_packet.md` for the judges.
- `grade.py score <dir> wN <rep> ../baseline --judges j1.json j2.json j3.json` - majority vote + code checks into `results.jsonl` and `traces/`.

Per world: one runner subagent (`model: sonnet`) with the brief below, then `packet`, three judge subagents (`model: haiku`) each told to read the packet and write only the JSON verdicts to `judge_K.json`, then `score`. Rebuild the report with the claude-api skill's `build-report-lite.mjs <absolute path to this flow dir>`.

Runner brief (fill `<RUN>` and `<W>`): load `plugins/marcketplace/skills/proactive-router/SKILL.md`, invoked as `/marcketplace:proactive-router profile=confluence:8f2e4a91-example-cloud-id/889000111 unattended`, now = 2026-09-22 08:45 Australia/Sydney. The `chat` and `wiki` tools are `python mock_tools.py --run <RUN> --world <W> <tool>` (search_public_and_private, read_thread, read_context, read_canvas, update_canvas --file, get_page, update_page --file). Hard rules: no mcp__ tools, no WebFetch/WebSearch, no subagents, never read `evals/` or this folder except to write payloads under `<RUN>/payloads/`, don't open mock_tools.py.
