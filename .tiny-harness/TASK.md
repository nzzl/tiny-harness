# Task

Status: Python environment guidance prepared; validation and publication pending

## Outcome and scope
Make isolated Python environments the default instruction when dependencies are
needed. Reuse existing tooling; create a local ignored .venv only when needed.
Keep this in the contract and documentation, without adding runner enforcement
or requiring an environment for standard-library-only use of Tiny Harness.
The user authorized this update. Repository was clean at 2aa8a18.

## Acceptance criteria
- [x] Contract defaults to an existing isolated environment or local .venv.
- [x] Existing package managers/containers remain supported by the guidance.
- [x] README and Python example explain PATH and the staged-snapshot boundary.
- [x] No runner logic, check configuration, or new runtime dependencies.
- [ ] Required staged checks pass; commit, push, and inspect GitHub CI.

## Checkpoint
Reconciled the preceding task: 2aa8a18 is published and all five jobs passed in
https://github.com/nzzl/tiny-harness/actions/runs/37462732186.
This change is instructions and documentation only; no new tests for prose.
No project .venv existed at the start. Use an ignored local .venv for the pinned
development checks. Next: inspect the staged diff, commit through the harness,
push, and verify the resulting Actions run. Commit output and GitHub CI provide
final evidence for the pending steps; check those before repeating publication.
