# Working an item

One item at a time, in the order the user picks. Each lesson below was paid for on a real
run; the reason is kept with the rule.

## Before acting

- **Re-check it is still open.** A list is a snapshot, and the day moves under it. Read
  the item's source again before doing anything: a ticket question the list calls open may
  have been answered an hour ago. Act on what is true now, and say what moved.
- **Find what the item's words mean before asking.** "Run the spec bootstrapping" is
  shorthand for a process the user has run before. Search `kb.paths.sessions` and the kb
  for an earlier run first, then the repository the item points at for a skill or process
  document of that name. Ask only when neither settles it.
- **Settle scope once, then work.** Where an item fans out (three merges touching a
  dozen screens), propose the scope with a recommendation and wait. A choice the user makes here
  ("parent plus three, but separately") governs the rest of the item.

## Doing it

- **Follow the process the item names, by its own files.** When the work belongs to a
  process with its own instructions - a repository's authoring skill, its git working
  agreement, its templates - read those files by path and follow them, in their order,
  with their gates. Do not substitute a general approach, and do not dispatch a
  marcketplace handler; that is the hub's job.
- **Work isolated.** Where the item changes a repository whose working copy is on another
  branch, use a separate worktree off a fresh default branch, never the user's checkout.
- **Delegate noisy reading.** A broad code or history sweep goes to a subagent that
  returns findings with evidence; spot-check its key claims before relying on them.
- **Ask one decision at a time, with a recommendation.** Use the interactive question tool
  where one exists. Ask business decisions only; a fact the code, the tracker or the kb can
  answer is looked up, not asked.
- **Read the answer, not the option label.** A user who picks "raise a bug" and writes
  "not a bug, a story under FLT-1201" wants the story. One who answers a recommendation with
  a question ("current plus trailing 12, no?") has confirmed it.

## External writes

- Show the exact text, the destination and the fields first; wait for an explicit yes
  for that write alone.
- Match the destination's house format: read two or three siblings under the same parent
  before drafting a ticket, and reuse their sections and summary prefix.
- Write what the user asked, as they asked it. A requested attribution ("say Claude
  thinks it's a bug") goes in verbatim.
- Where a tool cannot do part of the ask (attach a file, set a field), say so plainly and
  leave it as a named step for the user, never silently drop it.
- A message to a person is drafted, never sent.

## After each item

Report in a few lines: what was done, each write with its link or id, anything the user
still has to do by hand, and what is left open.
