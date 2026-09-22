# Reaping transient drafts

`kb-conventions.md`'s "Transient drafts" section places this obligation on `kb-dream`
explicitly: `reply-draft` and `action-sweep` (and any future handler with a `draft` first-
pass mode) write working artefacts under `kb.paths.drafts` expecting this pass to clear
them. A port of this skill without it is incomplete.

## Scope

Every file under `kb.paths.drafts`, every dream (incremental and full alike - drafts are
cheap to list and the folder is small by design, so this is not scope-gated the way the
main curation passes are).

## Reap when

- **Superseded.** The draft's own `supersedes_on` (kb-conventions.md's required field on
  every draft) names an event - the reply being sent, the ticket being filed - and real
  state shows that event happened (the sent-mail check, the tracker key existing). Reap
  it.
- **Stale.** The draft has sat untouched past `profile.kb.draft_stale_days` (default 30, a conservative
  default - flagged in `HISTORY.md` as the value this port assumed where the schema and
  the source contract are both silent on a number). Reap it even if `supersedes_on`'s
  event hasn't happened - a draft nobody acted on for a month is not still pending, it's
  abandoned.

## How to reap

Never delete. Move the file to the recycle location under `kb.paths.utility`
(`<utility>/dream-recycle/<YYYY-MM-DD>/<original-name>`), same mechanic as any other
supersession in `curation-passes.md`. One `log.md` line per reap, bold verb
`**Deprecation**`, naming the original path, the recycle path, and which condition
(superseded or stale) triggered it. Drafts are explicitly excluded from indexing per
`kb-conventions.md`, so no `index.md` line is removed or added for a reap - there was
never one to begin with.

## Reporting

One row in the dream note's "What I curated" table per reap, or one summary line
("N stale drafts reaped") when there are several in one run rather than a row each.
