# Lens: reality

What the codebase actually does today where this idea lands, and what that makes cheap or
expensive. The user can't read the code in the moment; this lens reads it for them and
says what an engineer would say in the first five minutes of the conversation.

## Inputs

The known packet, then `codebase: search` and `codebase: read` against
`profile.codebase.path`, at most `budgets.idea-spar.code_reads` file reads, each search a
`budgets.models.search`-tier subagent returning paths, line ranges and a two-line summary.

`profile.codebase.access: none`, or the category unresolved: say "couldn't check the
code" in the verdict and stop. Never describe how the code probably works.

## What to find

1. **Where it lands.** The entry points the idea touches: the screen, endpoint, job or
   table. Path and line for each.
2. **What already exists.** Data, components or jobs the idea could reuse. This is usually
   the most valuable finding: "the per-account breakdown is already computed for the export
   job" turns a big idea into a small one.
3. **What makes it expensive.** The data isn't stored at the needed grain, it's computed in
   a nightly batch, two services own it, there is no permission model for it.
4. **What it would break or change.** Callers, reports or customers depending on the
   current behaviour.
5. **What only an engineer can answer.** Name the question and, if the code shows it,
   whoever owns that area (from commit history or a CODEOWNERS-style file, never guessed).

## Shape

The output contract in `SKILL.md`. Every finding's source is a `path:line` (or a range);
a claim about the code with no path is cut. The verdict is a cost call in plain words
("smaller than it looks", "bigger than it looks", "blocked on X") with the reason.

Do not paste code. One identifier or field name in backticks is fine when it is the point.

## Worked example (fictional, against `profiles/example.md`)

> **Verdict** - Smaller than it looks: drift is already calculated, just never surfaced.
>
> - `RouteVarianceJob` computes plan-vs-booked drift per load every 15 minutes and writes it
>   to `load_variance` · `src/jobs/route_variance.py:40-88` · **so what:** the alert is a
>   consumer of existing data, not new analytics; scope drops by the calculation work.
> - There is no notification service; the only outbound path is the weekly email digest ·
>   `src/notify/digest.py:12` · **so what:** "both channels" means building in-app
>   notifications from scratch; email-only is the cheap first cut.
>
> **Checked, no bearing** - `dispatch_ui/plan_view` (read-only, unaffected).
> **Would change my mind** - if `load_variance` is pruned daily (couldn't tell from the code;
> ask the job's owner).
