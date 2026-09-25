# Write-up

Whichever way the run ends, this is the whole write-up: note, surface, notify.

## The note

Update the idea's existing note in place if one exists; never create a second note for the
same idea. No existing note -> create
`kb.paths.research/<idea-key>-<slug>.md` following `kb.conventions_file`'s frontmatter and
section conventions plus the two fields below, and every rule in `../../../shared/kb-conventions.md`
(frontmatter contract, the type registry's single authority, link style, index and log
maintenance).

- Frontmatter carries `deep_dive_status: complete | stuck | loop-limit` (this run's end
  state) so a later run can detect a resume.
- **Resolved findings** - a section (new, or appended to if it exists from a prior run):
  every resolved question's answer, in prose, with its citation - this is where an answer
  actually lives, not just the log line that references it.
- **Open questions** - refreshed: resolved items removed (they are in Resolved findings now);
  every question still in the queue is kept here regardless of whether it has been attempted
  yet - untried (including an incidental spawn never reached before the run ended), PENDING
  (shown with what it is waiting on), or stuck (flagged with its missing input - normally one
  question, but a depth-cap cascade produces a whole chain of stuck items; list every one of
  them, not just the leaf). Empty in a **complete** run.
- **Decisions for you** - its own section, separate from Open questions, untouched.
- **Run state** - the queue as it stands at the end of the run: remaining question IDs,
  chain-depth, which circles each has already exhausted, PENDING/blocked-on relationships.
  This is what makes the note the actual resume point, not just a status line.
- **Deep-dive log** - loops used vs. budget, each question resolved with which circle
  answered it and how many searches that attempt used (including the sweep's own counts, all
  four), any spawned-question lineage ("Q4 - spawned by Q2, blocking; resolved via code, 2
  searches"), and status this run ended on.

## The board

Write only inside the idea's block under Ideas (`../../../shared/surface-protocol.md`'s
Ideas block grammar). `chat: read canvas` first for current addressing; write the block
header `- <key> · <title> · note` if no block exists yet. Settle this skill's own existing
`<key>/q…` lines first per "Settle before you append" (never act on a tick; the hub
dispatches it), then append this run's lines in the same write. Only an actionable end
state gets lines; a clean **complete** run with nothing in Decisions for you writes nothing.

- **complete**, with items in Decisions for you: one option group per fork, at most two
  open groups per idea across this skill and `idea-scout` combined (a third waits in the
  note until one is decided):
  ```
  - <the fork, as a question>
    - [ ] (<key>/q1a) <option>
    - [ ] (<key>/q1b) <option>
  ```
- **stuck**: one line per stuck item (a depth-cap cascade gets one line per item in the
  chain, root to leaf):
  `- [ ] (<key>/q<n>) <the question, what was checked> · edit this line with your answer and tick`
- **loop-limit reached**: one line:
  `- [ ] (<key>/q-paused) <how many questions remain> · edit this line with a steer, or tick to continue from the note next run`

Every line carries category `idea-decision`. A tick dispatches `idea-scout`'s `decide`
mode, which appends the answer to this note's Decisions section and clears the question
from Open questions and Run state, so the next resume does not re-ask it.

Never tick or delete a line written by another run (this skill's own earlier pass,
`idea-scout` or `idea-wireframe`); closing is briefing's and acting is the hub's.

## Run record

No webhook and no post. Write `state.runs.idea-deep-dive`: `status` (`ok` for complete,
`partial` for stuck or loop-limit), `note` one line (`<key>: 3 resolved, 1 stuck on
<what>`), `ref` the note path. The briefing's Runs block carries it to the user.
