# Task

Status: cleanup instruction added; required staged validation and local commit pending

## Outcome and scope
Add a compact agent instruction to clean up task-owned temporary files and
background processes before handoff when they are no longer needed. Preserve
user files, unrelated work, deliverables, and evidence for unresolved failures.
Report retained resources so the next operator can identify them.
The user authorized this contract change. Source was clean at 3443599.
No runner changes, automatic deletion, new commands, or additional setup.

## Acceptance criteria
- [x] Contract requires cleanup of identifiable task-owned resources only.
- [x] Useful work and failure evidence are preserved; retained resources are reported.
- [x] Existing runtime cleanup and default installation remain unchanged.
- [ ] Required staged checks pass and a local commit is made through the harness.

## Checkpoint
The preceding cleanup pass is committed and published as 3443599; all five jobs
passed in https://github.com/nzzl/tiny-harness/actions/runs/37467822605.
This change is agent guidance only. No tests were added for prose; required
validation will run during commit using the existing project virtual environment.
Next: inspect the staged diff, commit through the harness, and verify Git state.
Commit output supplies final validation evidence. No push is requested for this
change; publication remains a separate step.
