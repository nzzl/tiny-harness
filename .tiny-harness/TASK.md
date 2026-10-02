# Task

Status: CI maintenance prepared; validation pending

## Outcome and scope
Resolve the setup-node Node 20 runtime deprecation warning. The user authorized
fixing this release follow-up. Repository was clean at 8d06eb7, and v0.1.1 was
already published after all five CI jobs passed. Preserve that release tag.

## Acceptance criteria
- [x] Pin setup-node to a verified release that declares the Node 24 action runtime.
- [x] Keep example tests on Node 22 and disable automatic package-manager caching.
- [ ] Required local checks pass before committing.
- [ ] Push the maintenance commit; all five GitHub jobs pass without the Node 20 warning.

## Checkpoint
Verified official setup-node v7.0.0 and v7 both resolve to
820762786026740c76f36085b0efc47a31fe5020; its action.yml declares node24.
Reviewed release changes. Automatic caching is explicitly disabled to preserve
the existing fixture setup. No harness code or example runtime changes.
Next: commit through the harness, push, then inspect CI results and annotations
for that exact commit. The Actions run supplies final external verification.
