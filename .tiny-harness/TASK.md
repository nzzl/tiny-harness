# Task

Status: complete (final documentation commit pending validation)

## Outcome and scope
Build a small, portable agent workflow from the supplied instruction kit. Keep
the source unchanged. Produce a separate repository with atomic local commits;
publication is outside scope. Destination was absent; no pre-existing work found.

## Acceptance criteria
- [x] Contract separates constraints from preferences and supports autonomous recovery.
- [x] Staged-tree validation and commits fail visibly on missing or failed checks.
- [x] Adoption preserves existing instructions, hooks, configuration, and history.
- [x] Disposable tests exercise meaningful success and failure cases.
- [x] README explains setup, normal work, recovery, enforcement, and limits.
- [x] Source comparison, attribution, and public-release hygiene are recorded.

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

Core commit: 39e644a (validated by the runner, 17 tests passed).
README and source comparison completed; installation commands, limitations,
recovery steps, and attribution checked against the implementation. All four
source-file SHA-256 hashes match their pre-build values; source unchanged.

Final release review: reusable files contain no personal paths or credentials.
The repository intentionally uses the existing Git identity in commit metadata.
No remote or publication was requested. Linux and other Python versions remain
unverified; direct Git bypass, trusted checks, concurrent writers, modifying
hooks, dependency setup, and unsupported submodules are documented limitations.

Next: commit this documentation through the runner (validation must pass), then
confirm clean Git status. There is no remaining implementation work; publication
is a separate authorized task. The final commit ID belongs in the handoff.
