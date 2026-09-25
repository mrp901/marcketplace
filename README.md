# marcketplace

A private Claude Code marketplace carrying one plugin: a product manager's operating
system, built so it survives changing jobs. Every organisation-specific fact lives in a
profile document rather than in the skills, so the same plugin works at the next company
by filling in a new profile.

Private, single-user, not published anywhere.

## Install

```
/plugin marketplace add mrp901/marcketplace
/plugin install marcketplace@marcketplace
```

To pin it so it survives a fresh machine, add to `~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "marcketplace": { "source": { "source": "github", "repo": "mrp901/marcketplace" } }
  },
  "enabledPlugins": ["marcketplace@marcketplace"]
}
```

Update with `/plugin marketplace update marcketplace`.

## First run

Run any skill interactively once. It will ask where the profile should live, create the
profile and state documents, and print the argument suffix to paste into your routines.
It asks only for what it cannot discover, and only for the keys that skill actually needs.

`profiles/example.md` is the template, filled in for a fictional organisation. It doubles
as the eval fixture.

## The skills

| Skill | What it does | How it runs |
|---|---|---|
| `briefing` | Calendar, chat and tracker snapshot; the reporter that closes finished lines, reports what every skill did, and posts the one message | Schedule |
| `proactive-router` | The hub. Sweeps reactions and saved items, classifies them, and acts on every tick on the board | Schedule |
| `reply-draft` | Drafts an email or chat reply in your voice. Never sends | Handler |
| `kb-note` | Captures one decision or reference note into the knowledge base | Handler |
| `action-sweep` | Sweeps canvases, mentions, assigned tickets, meeting actions and your own chat commitments into one line each | Schedule, and a handler |
| `idea-ticket` | Writes an ideas-board ticket in your voice, audited before you see it | Direct, and a handler |
| `idea-scout` | First-pass discovery on one qualifying idea; records your decisions; watches the roadmap | Schedule, and a handler |
| `idea-deep-dive` | Resolves an idea's open questions across four sources | Schedule |
| `idea-wireframe` | One annotated wireframe for an investigated idea; reworks it on your say-so | Schedule, and a handler |
| `session-log` | Writes a working session up as a durable note | Direct, plus hooks |
| `kb-dream` | Curates the knowledge base, consolidates memory, reviews the learning loop | Schedule, and a handler |
| `skill-eval` | Turns feedback on one run into an amended skill | Direct only |
| `skill-health-check` | Scores recent skill output against real evidence | Direct or schedule |

Every skill takes `profile=<ref>` and, when scheduled, `unattended`:

```
Run /marcketplace:briefing profile=confluence:<cloudId>/<pageId> unattended
```

## How the parts fit together

**The board** is one shared canvas with five sections: Today, To-do, For you, Ideas and
Closed. It holds only things that need you. **Every tick means "yes, do it."** Edit a line
and then tick it to have it done your way. Edit without ticking and nothing happens yet.
Delete a line and it is never proposed again. Add a line anywhere and it is a new request.
To-do is the one exception: it is your own list, and a tick there means done. A choice is
a question with one checkbox per option; tick one.

**The hub** reads every line, works out what you ticked, edited, deleted or added, and
acts on it: dispatching a handler, performing a small inline action, or resolving a
choice. Handlers run in their own context and report back; they never write to the board
themselves. The briefing closes what has finished and reports what every skill did, so
the same news never reaches you twice.

**Nothing irreversible happens without a tick, and nothing ever sends a message on your
behalf.** A handler that reaches an external write stops and asks for a second, specific
tick on a fresh line. A prior tick on a different item is never authorisation for this
one. A drafted reply is always yours to paste and send.

**The loop learns.** Ticks, edits and deletions accumulate into a tally. Three ticks on a
category with no handler proposes one. Three deletions of the same pattern stops it being
proposed. Nothing is ever mapped or executed without your tick.

**Voice compounds.** Drafting skills load a register built from your own writing, check
themselves against a list of model tells, and record what they wrote. When you edit a
draft, that difference feeds back on the next review.

Contributors: see `PORTING.md`. Scheduling is yours to set up; skills never self-schedule.

For a top-to-bottom picture of how the skills hand off to each other over a day, see
`docs/skill-flow.md`.

## Repository layout

```
plugins/marcketplace/
  skills/<skill>/SKILL.md     the procedure, under 150 lines, always loaded
  skills/<skill>/references/  the detail, loaded on demand
  skills/<skill>/HISTORY.md   why it is the way it is; never loaded at runtime
  shared/                     the eleven contracts every skill depends on
  scripts/                    the checks that gate every change
profiles/example.md           the template and eval fixture
ci/validate.yml               copy into .github/workflows/ to enable, see ci/README.md
```

`HISTORY.md` files are worth reading before changing a skill. Most of the rules in this
plugin exist because something went wrong once, and the history says what.

## Checks

```
claude plugin validate .
python3 plugins/marcketplace/scripts/scrub_check.py plugins/
python3 plugins/marcketplace/scripts/line_budget.py --all
python3 plugins/marcketplace/scripts/check_refs.py
```

The first validates the manifests. The second fails if any organisation-specific literal
reaches the plugin, which is what keeps it portable. The third enforces the line cap that
keeps the always-loaded part of each skill small. The fourth checks that every path a skill
points at resolves from the file it is written in, which is the easiest thing here to get
wrong by exactly one directory level.
