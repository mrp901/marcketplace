# vault-pulse - design rationale (for editors; not loaded at runtime)

## 2026-10-13 new skill (1.8.0)

**Why it exists.** The user runs `session-log` constantly and rarely opens the knowledge
base. Every skill that touches it measures hygiene (conformance, links, curation); none
measured whether it was compounding, and every silent failure so far was found by an
audit: the SessionEnd hook broken until 7 Oct, about six sessions never captured, 39
voice-ledger pairs unpromoted for nine days, the monthly voice review failing unattended,
and a gap in dream runs nobody was told about. The ask was a way to know the system is
still compounding without checking it.

**Decisions, and what they cost.**
- **A separate routine, not a `kb-dream` step.** A check that lives in the thing it checks
  fails with it. The cost is one more schedule to set up.
- **Behaviour, not hygiene.** Reuse (inbound links from real notes), consultation (tool calls
  that read the knowledge base) and repeat corrections are the compounding signals;
  conformance stays `kb-dream`'s.
- **Deterministic first.** Two stdlib scripts produce every number; the model's only job is
  to adjudicate at most five repeat-correction candidates and to write the entry. A model
  asked to "assess the vault" would drift toward a pleasing answer, which is the failure
  `skill-health-check` was written to avoid.
- **One definition of substantive.** The capture audit calls `../../scripts/pending_sessions.py`'s
  own `assess`, so the pulse and the sweep cannot disagree about which sessions count. The
  first version counted every large transcript and flagged 14 sessions, most of them
  scheduled routines nobody typed into; with the shared test it flagged 2.
- **Never green when blind.** A signal that cannot be measured is `unmeasured`, and two of
  them make the verdict amber. An absent reading must not look like a good one.
- **No post, no board line.** `notify.md` gives the briefing the only voice. The pulse
  records to `state.runs` and the briefing repeats an amber or red verdict on every
  briefing until the next run clears it. A red board line would have needed a new category
  and a handler; the briefing already reaches the user without one.
- **Watched by the briefing.** `vault-pulse` goes in `briefing.expected_runs` (9 days for a
  weekly run), so a pulse that stops is named overdue. The pulse in turn reads the
  briefing's and `kb-dream`'s heartbeats, so each watches the other.

**First reading, 2026-10-13 (the vault it was built for).** Amber: 2 ended substantive
sessions with no archive copy, 17 open follow-ups, an Inbox item 38 days old. Green:
reuse 64% (48 of 75 matured notes linked), consultation 78% (14 of 18 sessions), no memory
entries stuck at `fold_status: none`, every ledger item marked. These are a baseline, not a
trend; the thresholds are principled defaults, not fitted to this result.

**Known limits.** Inbound links are a proxy for use. The consultation count credits a lookup
anywhere in a session, not only before the first write. The repeat-correction overlap test
suggests pairs by title and misses a repeat worded differently. `signals.md` lists each.

**Rejected.** Reading the vault's own session notes with a model to judge "usefulness":
subjective, expensive, and the part most likely to flatter itself. A dashboard note in the
bundle: it would be one more thing to open, which is the problem being solved.
