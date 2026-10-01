# Task

Status: locally verified; commit-time validation pending

## Outcome and scope
Add basic lint and CI to this repository, with advisory production size/complexity
checks. Preserve the generic standard-library harness runtime and behavioral tests.
Make a validated local commit; do not push or publish.
The repository was clean at 2695968, which completed the previous audit fixes.

## Acceptance criteria
- [x] Canonical validation requires pinned basic lint and the existing behavior suite.
- [x] CI is configured to run canonical validation on macOS/Linux and Python 3.9/3.14.
- [x] File/function size and complexity findings remain advisory, excluding tests.
- [x] Missing tools and lint errors fail; size/complexity findings do not fail.
- [x] Validate changes and document setup and remote-verification limits.

## Checkpoint
Added pinned Ruff development setup, a read-only lint check, a four-job CI matrix,
and advisory size/complexity commands. The empty-discovery regression retains the
actual required check configuration and now includes its Ruff configuration file.
Existing runtime, install behavior, and check-configuration semantics are unchanged.

Evidence: required lint and all 21 behavioral tests passed through canonical
staged-tree validation on macOS with Python 3.9.6 and 3.14.7. Disposable probes
confirmed that an undefined name fails canonical validation, oversized production
files/functions and high complexity remain nonblocking, and tests are excluded
from size advisories. Workflow YAML parsed successfully and its matrix was checked.

Next: apply the reviewed files and rerun canonical validation through the local
commit wrapper. This checkpoint accompanies that commit; read the log for its ID.
Remote CI and Linux remain unverified; no Git remote is configured. Branch
protection is unchanged. No publication is authorized.
