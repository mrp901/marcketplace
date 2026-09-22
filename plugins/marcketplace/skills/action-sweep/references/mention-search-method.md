# The tracker-mention search method

**Hard-won knowledge - do not rediscover this the slow way.** A full-text tracker search
for "comment mentions me" (`comment ~ "<user name>"` or equivalent JQL) does **not**
reliably return results. This was confirmed by direct testing against the reference
instance, not assumed. Never fall back to it, even as a "quick check" - it silently
misses real mentions, which is worse than finding nothing, because it looks like it
worked.

Use this method instead, every run:

1. `tracker: search issues (JQL)` for issues where the user is assignee, watcher, or
   reporter, `updated >= <cursor>` (or the cold-start window - see
   `gather-procedure.md`), fields `summary, status, comment`.
2. For each issue returned, scan its comments for the mention marker carrying the user's
   `user.tracker_account_id`, or the literal form of their name.
3. For each matching comment, check whether the user has since **specifically addressed
   that question** - a reply that responds to its content, not just any later comment on
   the same issue. A chronologically later comment about a different point in the same
   thread does not count as addressing it. If it is genuinely unclear whether it has been
   addressed, treat it as unaddressed - that is the safer failure, since an unaddressed
   mention becomes a visible item rather than a silently dropped one.
4. Group matching comments by issue. One issue can carry a mix - some mentions
   addressed, some not. Carry that mix forward rather than collapsing the whole issue to
   one bucket: an addressed commitment on an issue can produce a draft ticket while a
   separate unaddressed mention on the *same* issue still needs to surface - either as
   its own "needs your reply" line (if nothing else is in motion for that issue) or as an
   open-question note on the draft the addressed commitment already produced (if
   something is).

**Known limitation, stated plainly, not silently worked around:** this only catches
mentions on issues the user already has some relationship to (assignee, watcher,
reporter). A mention on an issue with none of those three never surfaces. If this ever
turns out to matter, say so in the run's output rather than quietly widening the search.
