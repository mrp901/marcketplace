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

The workflow runs the same two checks the wave gate runs locally: `scrub_check.py plugins/`
and `line_budget.py --all`. It does not run `claude plugin validate`, which needs the CLI.
