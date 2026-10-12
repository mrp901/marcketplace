# Ticket draft formats

An issue can produce either shape below, and a single source issue can carry unaddressed
questions into whichever shape it produces - see "Open questions" in each.

## A. New ticket

A commitment ("I'll make this ticket") with no ticket yet, or an unaddressed mention with
no ticket already in motion for it:

```markdown
### Draft - <short title>  `[ROUTE: small | larger | larger+defined]`

**Source:** [KEY](url) - {who asked what, and what the reply committed to}

**Issue type:** Story | Bug | ...
**Priority:** Low | Medium | High
**Components:** {tracker.component.name}

#### User Story
As a <user>, I want <capability>, so that <outcome>.

#### UI
<mockup reference, or "None - description only">

#### Acceptance Criteria
**AC1**: ...

#### Open questions
<only other people's unaddressed mentions on the same source issue that this draft
doesn't resolve - quote who asked what, so it can be answered inline or on the ticket.
Omit this subsection entirely if there are none, and always when there is no source
issue. The drafter's own doubts never go here - see the ground rules.>
```

If the ticket should sit parked until some future trigger, add a
`> [!NOTE] Park this ticket` callout above the draft naming the trigger condition, and
prefix the title with `tracker.parked_prefix`.

## B. Modification

New information for an existing ticket, not a new one (a confirmation, a scope addition,
a still-open sub-question on an issue already in motion):

```markdown
> [!WARNING] Modify ONLY
> This is a modification to <source ticket>, not a new ticket.

## Draft - <short title>

**Source:** [KEY](url) - {context}

### What to add to <KEY>
- {each addition, confirmation, or scope note as its own bullet}
- {include any reference data - hex values, naming decisions, etc. - inline}

#### Open questions
<as above - only other people's unaddressed mentions on the same issue this
modification doesn't resolve. Omit if there are none.>
```

## Ground rules for both shapes

- **Never overwrite an existing ticket's description or acceptance criteria.** New
  information is always additive, delivered as a comment - this is the second hard stop's
  companion rule: even a confirmed push never rewrites what's already there.
- Sizing and routing (shape A only) is decided per `sizing-and-routing.md`, never guessed.
- **The drafter's own guesses never reach the tracker.** A question the drafter raised
  itself - a design choice, a scope edge, an assumed field value - is not an unaddressed
  mention. It goes in the draft's own `## Open questions` (`draft-format.md`), outside
  the Ticket block, so the user settles it before the push tick. Either the Ticket block
  resolves it (an AC that states the choice, or names who makes it), or it stays a
  question to the user; `push` files the Ticket block as it stands, so a question left
  inside it is filed too.

  Bad - a line ticked with no source issue, the drafter's doubt inside the Ticket block:

  ```markdown
  #### Open questions
  - Should long carrier names on the FLT dock-slot chart wrap, or truncate?
  ```

  Good - the Ticket block omits the subsection; the doubt sits in the draft's own section:

  ```markdown
  ## Open questions
  - Wrap or truncate long carrier names? AC1 assumes truncate; say before pushing.
  ```
