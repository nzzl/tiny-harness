# Task

Status: locally verified; commit-time validation pending

## Outcome and scope
Remove two measured development delays: validating empty commits and running
remaining checks after a commit check has already failed. Preserve exhaustive
standalone validation, staged-snapshot protection, and existing hooks.
The repository was clean at 2911e76. Make a local validated commit; do not publish.

## Acceptance criteria
- [x] Empty commits stop before checks/hooks, including an unborn repository.
- [x] Pending merges with unchanged content still validate and commit ancestry.
- [x] Failed, missing, and timed-out commit checks prevent later checks and commits.
- [x] Successful retries run every required check afresh.
- [x] Standalone validation still collects ordinary failures and later results.
- [x] Required lint/tests pass and measured delays improve.

## Checkpoint
Prepared early staged-change detection, commit-only fail-fast validation, focused
behavioral regressions, and matching workflow documentation. Pending merges are
exempt from the empty-content shortcut because they can record meaningful ancestry.

Evidence: required lint and all 25 behavioral tests passed through canonical
staged-tree validation on macOS with Python 3.9.6 and 3.14.7. Tests cover failed,
missing, and timed-out checks; fresh successful retries; exhaustive standalone
validation; empty initial/existing commits; unchanged-tree merges; and existing
snapshot, staging, installation, and hook guarantees.

Three serial before/after timing trials in disposable repository copies measured
median empty-commit latency of 6.636s -> 0.054s and first-check lint failure latency
of 6.352s -> 0.113s. These are local measurements, not portable timing guarantees.

Next: apply the reviewed files and commit through the harness, which reruns all
required checks. This checkpoint accompanies that commit; read the log for its ID.
Remote CI has not run; no remote is configured. No publication is authorized.
