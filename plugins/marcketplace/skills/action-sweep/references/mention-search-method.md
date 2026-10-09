# The tracker-mention search method

**Hard-won knowledge - do not rediscover this the slow way.** A full-text tracker search
for "comment mentions me" (`comment ~ "<user name>"` or equivalent JQL) does **not**
reliably return results. This was confirmed by direct testing against the reference
instance, not assumed. Never fall back to it, even as a "quick check" - it silently
misses real mentions, which is worse than finding nothing, because it looks like it
worked.

Use this method instead, every run:

1. `tracker: search issues (JQL)` for issues the user is assignee or reporter on **and**
   still watches: `(assignee = currentUser() OR reporter = currentUser()) AND watcher =
   currentUser() AND updated >= <cursor>` (or the cold-start window - see
   `gather-procedure.md`), fields `summary, status, comment`, comment bodies in the
   tracker's structured format (Jira: ADF, `responseContentFormat: adf`), never markdown.
2. For each issue returned, scan its comments for a tag: the user's name in a mention,
   matched two ways, either hit counts. (a) A mention node whose account id is
   `user.tracker_account_id`. The markdown format strips that id - the node renders as
   `<custom data-type="mention" data-id="id-0">@<user.name></custom>`, a placeholder,
   not the account - which is why step 1 asks for the structured format. (b) The literal
   string `@<user.name>` (or the `@` text of any node (a) matched, the tracker's own
   spelling) in the comment text, which catches a tag typed as plain text that never
   became a mention node and carries no id anywhere. A comment with neither is not a
   tag, even on the user's own ticket; don't widen to untagged comments. A tag is a find
   on its own: never drop one because it reads as "in passing" or has no question
   mark; whether it needs anything is the user's judgement, not the sweep's. The one
   exception: drop it when the comment's whole text, mentions and punctuation aside, is
   a bare "cc" or "fyi" (any case). Anything more ("fyi, done") surfaces; when in doubt,
   surface.
3. For each tag, check whether the user has since **specifically addressed that
   comment** - a reply that responds to its content, not just any later comment on
   the same issue. A chronologically later comment about a different point in the same
   thread does not count as addressing it. If it is genuinely unclear whether it has been
   addressed, treat it as unaddressed - that is the safer failure, since an unaddressed
   mention becomes a visible item rather than a silently dropped one.
4. Group matching comments by issue. One issue can carry a mix - some mentions
   addressed, some not. Carry that mix forward rather than collapsing the whole issue to
   one bucket: an addressed commitment on an issue can produce a draft ticket while a
   separate unaddressed tag on the *same* issue still gets its own `to-do` line. A tag
   is always `to-do`, even when it implies a ticket (the line can say so); the "more
   concrete action" rule in `sizing-and-routing.md` never pulls a tag elsewhere.

**Deliberate scope, not an accident:** only tags on issues the user is assignee or
reporter on and still watches surface. Watched-only issues are out, and so is an
assigned or reported issue the user has unwatched - an unwatch is a deliberate opt-out.
A tag outside that scope never surfaces; don't quietly widen the search to catch it.
