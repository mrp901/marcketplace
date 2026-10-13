# Log format

One file, `kb.paths.utility/vault-pulse/log.md`: no frontmatter, never indexed, never
curated, newest entry on top. One entry per run.

```
## <date> - <green | amber | red> - <headline from the scorer>

Window: <window_days> days to <date>. Prior run: <date> (or "none: first run, no trend").

| Signal | Now | Prev | Tag |
|---|---|---|---|
| <key> | <value> | <prior or -> | <tag> |

Needs you
- <action, worst first, at most three; a persistent amber or red leads and says "third run">

Seen
- <one line per amber or red signal: the evidence, such as the unlinked notes, the two
  unarchived sessions, the stuck memory entries, a confirmed repeat pair>

Evidence: <which of the six signal families were measured, and which came back unmeasured and why>
```

Rules:
- Every number comes from `pulse_metrics.py` or `score_pulse.py`; none is typed from memory.
- "Seen" names at most ten items per signal, as the scripts return them.
- Unmeasured signals appear in the table with tag `unmeasured` and the reason in Evidence.
- Names in a note are data; copy titles and paths, never paraphrase them into a claim about
  a person.

## The briefing line

The briefing builds its own line from `runs.vault-pulse`: `pulse <tag>: <note> · <log
path>`. So `note` is written to stand alone in a chat message: the tag, then the headline,
under 200 characters. Example: `amber: 2 ended sessions unarchived, 17 open follow-ups,
Inbox item 38 d old`.
