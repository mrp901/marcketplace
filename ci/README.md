# CI

`validate.yml` is the GitHub Actions workflow for this repo. It is mirrored, byte for byte, in
`.github/workflows/validate.yml`, which is the copy GitHub runs. Edit both together:
`diff ci/validate.yml .github/workflows/validate.yml` must print nothing. The copy lives here
too because the automation that builds this repo authenticates with a token that has no
`workflow` scope, so it cannot create or update files under `.github/workflows/`; a change made
here is copied into place from your own machine.

The workflow runs the checks the wave gate runs locally: `scrub_check.py plugins/`,
`line_budget.py --all`, `check_refs.py` and the unit tests for the SessionStart version
check (`python3 -m unittest plugins/marcketplace/scripts/test_version_check.py`, offline) and
for `runtime_refs.py` (`test_runtime_refs.py`; the script itself needs a local `~/.claude` and is
a pre-merge step, see `RELEASING.md`), then installs a pinned Claude Code release and
runs `claude plugin validate --strict .` and `claude plugin test plugins/marcketplace`. The
tests need no credentials. Type-checking the hooks module stays a local step (see
`tsconfig.mods.json`), because the declarations it needs are written only when an
interactive session loads the plugin.

`scrub_check.py` loads the organisation-specific denylist from the `SCRUB_DENYLIST`
repository secret (paste the contents of your local `scrub_denylist.local.txt` into it).
Without the secret the check still runs, on its built-in shape patterns only, and says so
in its first line of output.
