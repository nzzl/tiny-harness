# Task

Status: termination cleanup fixed; required staged validation and local commit pending

## Outcome and scope
Fix audit finding F1: SIGTERM and SIGHUP must unwind active validation, stop the
check process group, and remove the temporary snapshot. Preserve conventional
signal exit codes and existing SIGINT behavior. No new dependencies or operator
steps. Leave the lower-priority installed README link and stdin behavior unchanged.
Source checkout was clean at 614d176; runtime matches the audited 2aa8a18.

## Acceptance criteria
- [x] Regression reproduces leaked processes in validate and commit before the fix.
- [x] SIGTERM to runner/group, SIGHUP, and SIGINT clean up in both commands.
- [x] Interrupted validation leaves HEAD and index unchanged and never reports success.
- [x] README states supported signals and the uncatchable-termination limitation.
- [ ] Required staged checks pass and change is committed through the harness.

## Checkpoint
The preceding environment-guidance change 614d176 is published; all five jobs
passed in https://github.com/nzzl/tiny-harness/actions/runs/37464956254.
In a disposable clone, SIGTERM regression failed before the fix in both commands
because surviving processes held output pipes open. Regression cleanup removed
its processes and snapshots. With the fix, four tests covering eight cases pass
on Python 3.14.7. Ruff, complexity, and size checks pass without warnings.
Next: run required staged checks through the commit command and inspect Git state.
Commit output is the final validation evidence. Publication is not part of this
local fix; do not repeat or infer publication from this checkpoint.
