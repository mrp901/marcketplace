# Onboarding

Every skill runs this procedure at the start of every invocation, before doing anything
else. It is the same six numbered steps for every skill; a skill follows them verbatim
rather than reimplementing any part of them.

## Step 0 - Mode

Look for the literal token `unattended` in the invocation arguments. If present, this run
asks no questions, ever - every "ask" branch below becomes a fast-fail instead. Absence of
the token means interactive mode. **Never infer unattended from context** (a quiet
terminal, a scheduled-looking prompt, no human replying) - only the literal token counts.
A routine prompt that forgot to include it is an interactive run that happens to have no
one watching, and it will hang waiting on a question exactly as it should.

## Step 1 - Locate the profile

Resolve the profile reference in this order, first match wins:

1. A `profile=` argument in the invocation.
2. The `MARCKETPLACE_PROFILE` environment variable.
3. The pointer file at `~/.claude/marcketplace/profile.ref`.
4. Interactive only: ask once.

Ref formats: `confluence:<cloudId>/<pageId>`, `sharepoint:<drive>/<path>`,
`gdrive:<fileId>` (untested - offer it but mark it so).

**Bootstrap** (interactive only, when none of the four resolves to an existing document):

1. Ask whether the profile should live in Confluence or SharePoint.
2. `ToolSearch` that service.
3. Create the profile document from the `profiles/example.md` skeleton, with the answers
   gathered in this bootstrap flow filled in, and an empty sibling state document created
   from `state-schema.md`'s shape (`state_version`, `installed_version`, `profile_ref` set,
   every other key empty or its documented default).
4. Write the pointer file at `~/.claude/marcketplace/profile.ref` with the new profile's
   ref.
5. Print exactly this line so the user can paste it into a routine prompt, with the real
   ref substituted:

   ```
   profile=<ref> unattended
   ```

## Step 2 - Read profile and state

Read the profile document **by id, never by search** - onboarding step 1 resolved an
exact reference, and re-discovering it by search risks landing on the wrong document.
Read the sibling state document via the profile's `state_ref`; if it does not exist yet,
create it (this only happens outside the bootstrap flow if a profile was hand-edited to
remove `state_ref` or point at a missing document - treat that as a fast-fail-worthy
condition in unattended mode, or ask in interactive mode before creating one silently).

## Step 3 - Diff Needs against the profile

Compare this skill's `## Needs` heading against what the profile actually has. For every
key or tool category still missing:

1. **Discover first.** Run the applicable discovery procedure from
   `profile-schema.md`'s "Discovery procedures" section. A key that discovery resolves is
   written back (step 6) and does not need to be asked.
2. **Still missing, interactive** - ask, in **one batched question covering every missing
   key for this skill**, never a drip of one question at a time. List every key still
   needed in that single message.
3. **Still missing, unattended** - fast-fail (see below).

## Step 4 - Tool discovery

For each tool category this skill needs: if `profile.tools.<category>.service` names a
service, `ToolSearch` with `+<service> <verb>` (the verb from `tool-capabilities.md`) to
find and cache the concrete tool prefix in `state.machines[<machine_id>].tools`. If no
service is set, `ToolSearch` by capability keyword instead (the category name plus the
verb) and offer what comes back: a service this plugin has been tested against is offered
plainly; anything else is offered marked `(untested)` with `tested: false` recorded
alongside it. One re-resolution is allowed if the cached prefix fails at call time;
a second failure is a fast-fail.

## Step 5 - Voice check

Only for skills that list `voice` in their `## Needs`. If `profile.voice.calibrated_at` is
empty:

- **Interactive** - run the calibration procedure in `voice.md` before continuing.
- **Unattended** - proceed anyway, but prefix the drafted output with `voice: uncalibrated`
  so the user knows not to trust the register.

## Step 6 - Write back

Write the profile only if something changed in it this run (a discovered or asked key was
filled in) - otherwise leave it untouched, since the profile is low-frequency by design
(see `state-schema.md`'s "Why two documents"). Always write `state.machines` (this run's
tool resolutions) and `state.runs[<skill>]` (this run's outcome), whether or not anything
else changed.

## Fast-fail

When a required key or category is still missing after discovery, in unattended mode:

1. Write one line under `# Plugin notices` on the surface:

   ```
   - <date> <skill>: fast-fail · missing <keys> · run /marcketplace:<skill> interactively once
   ```

2. Set `state.runs[<skill>].status = fast-fail`.
3. Stop. Do nothing else this run.

**Never guess an identity key.** A missing `user.*`, `org.name` or similar identity value
is always a fast-fail or an interactive ask - it is never inferred, defaulted or left
blank and proceeded past.

A skill whose surface cannot be resolved (no `surface.id`, or the surface itself is
unreachable) has nowhere to write that notice line. In that case it writes to
`state.runs[<skill>]` and to its own session output only, and stops the same way.

## For skill authors

Every `SKILL.md`'s `## Needs` heading lists:

- **Profile keys**, as dotted paths (e.g. `tracker.project_key`, `kb.paths.inbox`).
- **Tool categories** the skill calls (e.g. `chat`, `tracker`, `kb`).
- Any of the above that are genuinely optional for this skill marked `(optional)` -
  onboarding does not ask or fast-fail on a missing optional key, it simply proceeds
  without it.

Every `SKILL.md` also carries this one line, verbatim, pointing back here:

> Resolve profile, state and tools per `../../shared/onboarding.md` before doing anything else.
