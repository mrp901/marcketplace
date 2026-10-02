# Skill ecosystem flow

A high-level picture of how the marcketplace skills run, read top to bottom by cadence:
the overnight scheduled runs, then the board and your ticks, then the handlers the hub
dispatches on those ticks, then the things you run yourself, then the weekly jobs, then
the feedback loops. Skill names below are the repo skills in
`plugins/marcketplace/skills/`.

Since 1.1.0 there is one tick rule on the whole board: **a tick means "yes, do it"**. The
Router acts on every tick; the Briefing only closes lines and reports. Nothing on the
board is an FYI, and nothing ever sends a message on your behalf.

Solid arrows are a write or a direct hand-off. Dotted arrows mean the hand-off waits for
a later run: a tick reaching the hub on its next scheduled run, or something one run
leaves for another to pick up. The overnight skills are separate scheduled routines, not
a chain; the order shown is the conventional one, and each runs on whatever cron you gave
it.

Three hand-offs wrap from a later band back to an earlier one and aren't drawn as
arrows, to keep the diagram acyclic:

- **Your tick → `proactive-router`.** The hub reads the board fresh on its next run,
  including whatever you ticked, edited, deleted or added.
- **A decision log → your next spar.** `idea-spar` `decide` writes each ticked decision to
  the idea's decision log, which the next session on that idea reads as known context.
- **`session-log`'s notes → `kb-dream`.** Dream reads recent `Sessions/` notes as one of
  its inputs on its next run.

```mermaid
flowchart TB
    subgraph overnight["Overnight, each on its own schedule"]
        direction TB
        router["proactive-router\n(the hub: sweep, then act on every tick)"]
        dream["kb-dream"]
        sparwatch["idea-spar\n(Next watch)"]
        sweep["action-sweep"]
        briefing["briefing\n(close, report, post)"]
    end

    board(["The board: Today · To-do · For you · Ideas · Closed"])
    tick(["You tick, edit, delete or add a line"])
    message(["The briefing message\n(Runs block, FYIs, health)"])

    router --> board
    dream --> board
    sparwatch -->|"forks only"| board
    sparwatch -.->|"pack link via runs"| message
    sweep --> board
    briefing --> board
    briefing --> message
    board --> tick

    subgraph handlers["Dispatched by the hub, on a tick"]
        direction TB
        replydraft["reply-draft\n(email, chat-reply)"]
        kbnote["kb-note"]
        ideaticket["idea-ticket\n(draft → file)"]
        sweeptargeted["action-sweep\n(targeted / meeting → push)"]
        spardecide["idea-spar\n(decide)"]
        dreamsettle["kb-dream\n(settle)"]
        inline["inline: investigate,\npromote, to-do"]
    end

    router -.-> replydraft
    router -.-> kbnote
    router -.-> ideaticket
    router -.-> sweeptargeted
    router -.-> spardecide
    router -.-> dreamsettle
    router -.-> inline

    subgraph manual["Your day, direct or hook-driven"]
        direction TB
        sessionlog["session-log"]
        ideaticketdirect["idea-ticket\n(direct)"]
        sparsession["idea-spar\n(session: challenge, reality,\nmarket, sketch, pack it)"]
        skilleval["skill-eval\n(manual only)"]
    end

    sessionhook(["SessionEnd / SessionStart hooks"])
    sessionhook --> sessionlog
    roadmap(["You move an idea into Next"])
    roadmap -.-> sparwatch

    subgraph weekly["Weekly band, each on its own schedule"]
        direction TB
        healthcheck["skill-health-check"]
    end

    healthcheck -->|"red score only"| board
    healthcheck -.->|"amber, green"| message

    subgraph feedback["Feedback loops"]
        direction TB
        decisionlog(["idea decision logs"])
        outcomes(["state.outcomes"])
    end

    spardecide -.-> decisionlog
    decisionlog -.-> sparsession
    decisionlog -.-> sparwatch
    tick -.->|"ticked shc: line,\nqueued"| skilleval
    skilleval -.-> outcomes
    outcomes -.-> briefing
```

## Legend

- **Bands, top to bottom**: the overnight schedules → the board, your tick and the one
  message → handlers the hub dispatches → things you run yourself or that a hook kicks
  off → the weekly jobs → the loops that feed back into the system.
- **Solid arrow**: a write, or a hand-off within the same run.
- **Dotted arrow**: a hand-off picked up on a later scheduled run rather than acted on
  immediately.
- The **board** node stands in for the shared surface (one chat canvas by default) and
  its five sections. The **message** node is the one post the plugin sends; every other
  skill's run lands in its Runs block from `state.runs`. The tracker, the knowledge base
  and the state document aren't drawn as nodes; every skill that touches them is
  described in `README.md` and each skill's own `SKILL.md`.

## What a tick does, by line

| Line | Tag | On tick |
|---|---|---|
| A swept candidate (email, ticket, note, summary, to-do) | `pr:` | dispatched to its handler, or an inline action |
| A find from the action sweep | `sweep:` | drafted (first tick), then pushed (second tick on the fresh line) |
| An overdue item | `rb:` | `inline:investigate` |
| A tracker-feed claim the live issue contradicts | `feed:` | `inline:investigate` |
| A term to add to the glossary | `term:` | `inline:promote`; the line is removed, never logged |
| A curation task | `dream:` | `kb-dream` `settle` |
| A red health score | `shc:` | queued; you run `skill-eval` |
| An option under an idea's decision | `<key>/d…` | `idea-spar` `decide` records it in the idea's decision log |
| Your own To-do | (none) | done; briefing closes it |

## Known gaps

- **`idea-spar`'s Next watch only sees moves.** An idea created straight into Next, or
  first seen by the watch already in Next, is seeded rather than briefed. Spar on it
  directly.
- **The migration is one-way and runs once.** The first `briefing` run under 1.1.0
  rewrites the board into the five-section layout; every other skill waits for it. A
  board that can't be read as either layout stops briefing with a fallback post rather
  than a guess (`skills/briefing/references/migration.md`).
- **The eval cases for dispatching handlers grade the hub's payload, not the handler.**
  The new `proactive-router` cases accept either a completed dispatch or a documented
  "could not resolve a tool category" sub-line, because the mock servers cover chat and
  the state document only.
