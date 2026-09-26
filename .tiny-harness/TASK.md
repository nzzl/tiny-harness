# Task

Status: fixes verified; commit-time validation pending

## Outcome and scope
Fix the three confirmed pre-publication audit findings. Preserve the existing
repository and source kit. Make a validated local commit; do not push or publish.
The repository was clean at 9bef864 when work resumed. That documentation commit
completed the earlier build despite its checkpoint still saying it was pending.

## Acceptance criteria
- [x] Reject changed/deleted/replaced staged snapshot paths before committing.
- [x] Preserve support for untracked build output and existing recovery behavior.
- [x] Reject duplicate JSON object keys before any check runs.
- [x] Make this repository's required suite fail when no tests are discovered.
- [x] Add behavioral regressions and update configuration/recovery documentation.
- [x] Pass the canonical staged-tree check and original independent audit probes.

## Checkpoint
Baseline: 39e644a and 9bef864 contain the original implementation and documentation.
The source kit remains read-only; its four file hashes were verified unchanged
at the end of the original build. The audit added no release-repository changes.

Fixes: capture snapshot content/type/executable-bit signatures before checks and
compare after each command, including symlinks and parent directories. Stop on a
change; generated untracked output remains allowed. Reject duplicate JSON keys
at all object depths. A small project-specific unittest entry point rejects
empty discovery and propagates test failures. No generic test-framework parser,
hook replacement, external dependency, or background service was introduced.

Evidence: 21 tests passed through canonical staged-tree validation, including regressions for
all three findings; snapshot cases cover content, deletion, permissions, symlinks,
parent-directory replacement, and a mutation by a failed check. The existing
untracked-output, unrelated-edit, hook, timeout, and installation tests still pass.
All three original independent audit probes pass against the proposed staged
files in disposable repositories. The probe assertions were unchanged; only the
clone fixture was updated to apply the staged patch before testing. Staged
whitespace and local documentation-link checks also pass.

Remaining limits: checks are trusted commands. Snapshot state is compared between
commands, so an internal change-and-restore is not detected. Direct Git bypass,
modifying hooks, concurrent writers, explicit dependency setup, and unsupported
submodules remain documented. Linux and other Python versions remain unverified.

No code fixes remain. This checkpoint accompanies the local fix commit; the
runner must rerun required validation before creating it. Read the Git log for
the resulting commit identity and reconcile this checkpoint on resumption.
Publication remains explicitly unauthorized.
