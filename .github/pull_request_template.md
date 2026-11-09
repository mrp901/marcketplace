## Summary

<!-- What changes, and why. -->

## Version

<!-- New version in plugin.json and CHANGELOG, or "none". -->

## Runtime checklist

Answer each with checked (how), not affected (why), or gap (named). See `RELEASING.md`.

- [ ] 1. Cloud routines still run from a fresh clone with connectors only:
- [ ] 2. Synced copy: anything local that needs the new version (say "update and restart after merge" if so):
- [ ] 3. Outside the repo: `runtime_refs.py` run, every hit fixed or named:
- [ ] 4. Profile and state: defaults, migrations or aliases, mixed-version writes:
- [ ] 5. Existing content: notes, lines or state made under an older contract:
- [ ] 6. Rollback: what a revert leaves that the old version misreads:

## Repo checks run

- [ ] `claude plugin validate --strict .`
- [ ] `claude plugin test plugins/marcketplace`
- [ ] `python3 plugins/marcketplace/scripts/scrub_check.py plugins/` (0 FAIL)
- [ ] `python3 plugins/marcketplace/scripts/line_budget.py --all`
- [ ] `python3 plugins/marcketplace/scripts/check_refs.py`
- [ ] Unit tests: `test_version_check.py`, `test_kb_health_score.py`, `test_runtime_refs.py`

## After merge

<!-- Update the plugin and restart, first scheduled run to watch, anything else. Or "none". -->
