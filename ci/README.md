# CI

`validate.yml` is the GitHub Actions workflow for this repo. It lives here rather than in
`.github/workflows/` because the automation that builds this repo authenticates with a
token that has no `workflow` scope, so it cannot create or update files under
`.github/workflows/`.

To enable CI, copy it into place and push from your own machine:

```
mkdir -p .github/workflows
cp ci/validate.yml .github/workflows/validate.yml
git add .github/workflows/validate.yml && git commit -m "ci: enable validation workflow"
git push
```

The workflow runs the checks the wave gate runs locally: `scrub_check.py plugins/`,
`line_budget.py --all` and `check_refs.py`, then installs a pinned Claude Code release and
runs `claude plugin validate --strict .` and `claude plugin test plugins/marcketplace`. The
tests need no credentials. Type-checking the hooks module stays a local step (see
`tsconfig.mods.json`), because the declarations it needs are written only when an
interactive session loads the plugin.

`scrub_check.py` loads the organisation-specific denylist from the `SCRUB_DENYLIST`
repository secret (paste the contents of your local `scrub_denylist.local.txt` into it).
Without the secret the check still runs, on its built-in shape patterns only, and says so
in its first line of output.
