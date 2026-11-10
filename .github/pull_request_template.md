## Summary

<!-- What changes, and why. -->

## Version

<!-- New version in plugin.json and CHANGELOG, or "none". -->

## Runtime checklist

Answer each with checked (how), not affected (why), or gap (named). See `RELEASING.md`.

- [ ] 1. Cloud routines still run from a fresh clone with connectors only:
- [ ] 2. Synced copy: anything local that needs the new version (say "update and restart after merge" if so):
- [ ] 3. Outside the repo: `runtime_refs.py` run (`python3`, or `python` on Windows), every hit fixed or named:
- [ ] 4. Profile and state: defaults, migrations or aliases; how an older version writes this document (whole-document replace or key merge) and that it keeps keys it does not know:
- [ ] 5. Existing content: does any new or changed rule (clock, prune, lock, counter, matcher) act on notes, board lines or state that already exist? The oldest real example you ran it against, and what it does to it (especially anything it deletes or counts):
- [ ] 6. Rollback: what a revert leaves that the old version misreads:

## Repo checks run

- [ ] `claude plugin validate --strict .`
- [ ] `claude plugin test plugins/marcketplace`
- [ ] `python3 plugins/marcketplace/scripts/scrub_check.py . --require-denylist` (0 FAIL; paste the `denylist: <path> (N patterns)` line, a run with none loaded exits 2 and is not a pass)
- [ ] `python3 plugins/marcketplace/scripts/line_budget.py --all`
- [ ] `python3 plugins/marcketplace/scripts/check_refs.py`
- [ ] Unit tests: `test_version_check.py`, `test_kb_health_score.py`, `test_runtime_refs.py`, `test_scrub_check.py`

## After merge

<!-- Update the plugin and restart, first scheduled run to watch, anything else. Or "none". -->
