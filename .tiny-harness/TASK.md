# Task

Status: in progress

## Outcome and scope
Build a small, portable agent workflow from the supplied instruction kit. Keep
the source unchanged. Produce a separate repository with atomic local commits;
publication is outside scope. Destination was absent; no pre-existing work found.

## Acceptance criteria
- [x] Contract separates constraints from preferences and supports autonomous recovery.
- [x] Staged-tree validation and commits fail visibly on missing or failed checks.
- [x] Adoption preserves existing instructions, hooks, configuration, and history.
- [x] Disposable tests exercise meaningful success and failure cases.
- [ ] README explains setup, normal work, recovery, enforcement, and limits.
- [ ] Source comparison, attribution, and public-release hygiene are recorded.

## Checkpoint
Source inspection complete: four Markdown files and their referenced global
workflow skill; no executable harness, hooks, task tracker, or license notice.
Source file hashes recorded externally for a final unchanged check.

Retain source-first inspection, fresh evidence, behavior tests, proportionality,
and atomic commits. Replace phase approvals/operator-only commits with scoped
autonomy. Use one Python standard-library runner, explicit JSON checks, and one
task record. Validate an isolated copy of the index to preserve unrelated edits.
No hook replacement; commit wrapper is opt-in, not tamper-proof enforcement.

Verification: canonical staged-tree validation passed all 17 behavior tests,
including installed-copy adoption, failed-check recovery, hook preservation,
and commits that preserve unrelated work. Staged whitespace check passed.

Next: make the core commit through the runner; finish and verify public-facing
documentation and source preservation. Commit validation will rerun afresh.
