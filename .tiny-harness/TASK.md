# Task

Status: README badges verified; commit and publication pending

## Outcome and scope
Add CI status, latest version tag, and MIT license badges to the README and push
the update. Repository was clean at b6b79d7. That CI maintenance commit passed
all five GitHub checks with the Node 20 warning removed. No runtime changes.

## Acceptance criteria
- [x] Add three linked badges immediately below the README title.
- [x] Verify badge images show passing validation, v0.1.1, and MIT.
- [ ] Commit through the harness and publish the README update.

## Checkpoint
Verified all three badge images load. CI tracks master push runs; the version
badge follows tags rather than requiring a GitHub Release. The license links to
the existing MIT file. Next: required staged validation, commit, push, and confirm
GitHub CI for the published commit. Actions results provide final verification.
