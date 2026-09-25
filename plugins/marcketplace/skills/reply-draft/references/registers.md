# Register selection

Picked once per dispatch, from the thread's audience and channel - never from the
`email` or `chat-reply` category alone, since a teammate DM and a customer email can
arrive through either.

| Thread looks like | Register |
|---|---|
| A chat thread with an internal colleague, no external participant on the thread | `teammate_chat` |
| An email or chat thread with anyone outside the org (a customer, a vendor, a partner) | `customer_facing` |
| An email thread with a named executive, or addressed to a leadership distribution list | `exec_update` |
| Anything that reads as ticket or tracker prose quoted into the thread (a ticket comment forwarded as an email) | `ticket_prose` |

If a thread genuinely mixes audiences (an internal colleague CC'd on a customer thread),
pick by who the reply is actually addressed to, not who else is copied - the register
matches the primary recipient the reply is going to.

Load only the one register note this thread calls for, per `voice.md`'s handler usage
rule - never all four, never the full avoid-list plus every register note when one
register note and the shared avoid-list will do.
