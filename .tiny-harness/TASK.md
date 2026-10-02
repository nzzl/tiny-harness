# Task

Status: locally verified; validated commit pending

## Outcome and scope
Fix check process leakage and reject symlinked configuration. Make changes to
validation visible with an advisory warning, without adding approval flags.
The user authorized this follow-up after review. Preserve unrelated work.
The repository was clean at e50d85e; v0.1.0 was already published after CI passed.

## Acceptance criteria
- [x] Same-group children are stopped after success, failure, timeout, and interruption.
- [x] Configuration file/directory symlinks are rejected.
- [x] Changes to staged checks/runner or the executing runner produce warnings.
- [x] Normal changes remain quiet; warnings neither skip checks nor demand approval.
- [x] Relevant regression tests and required lint/behavior checks pass.

## Checkpoint
Implemented cleanup, configuration boundary checks, advisory commit warnings,
and documentation. All 38 tests and required lint passed locally on Python 3.10.14.
No production size or complexity warnings; runner is 276 lines. No new dependencies
or permission flags. Tests cover passing/failing/timed-out/interrupted children,
file/directory symlinks, normal commits, and staged/executing-runner warnings.
Next: commit through the harness, which reruns required checks on the staged tree.
Publication and tagging are outside this follow-up's scope.
