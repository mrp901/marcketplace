# Closing a list

A list closes on the user's word, never on this skill's count of ticked rows: the user may
have done half the items themselves, or decided some no longer matter. "All items on that
list are done" closes it; silence does not.

## On the user's word

In one write batch, per `../../../shared/kb-conventions.md`. A list is a transient draft,
so there is no index line to update; once closed, `kb-dream` reaps it on its next pass.

1. **A banner** directly under the list's title: `> **Done - <D Mon YYYY>, ~<HH:MM>.**`
   then whose word closed it, a link to the session note that covered the work (when one
   exists) and "Kept as the record of the <window>; nothing here is still open." The list
   body is left as it was; it is the record of what the plan said.
2. **`status`** to the kb's own retired value, read from `kb.conventions_file` (for
   example `deprecated`). Where the kb defines none, leave `status` alone and rely on the
   banner. This is the one place this skill moves a status, and only because the user said
   so.
3. **`generated`** to this skill and now, since the content changed.
4. **A log line**: `**Deprecation**` - the list, "marked done on <user>'s word". Where the
   kb defines no retired status and `status` was left alone, the verb is `**Update**`.

## Partly done

When the user stops with items open, do not close. Offer to note which items were done
in a short banner instead, and leave `status` as it is; `kb-dream` reaps an abandoned list once it is past
`stale_after`.

## Then

Offer `session-log` for the working session. Where a session note is written, link it
from the list's banner; linking it from the rest of the kb is `session-log`'s job.
