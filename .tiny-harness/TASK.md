# Task

Status: guidance and installation verified; staged checks and publication pending

## Outcome and scope
Add an optional persistent feature checklist and resumption/verification recipe.
Strengthen the contract and installed task template without adding runtime gates,
new dependencies, extra installed files, or a mandatory backlog for small changes.
The user authorized implementation and publication of this guidance.
The repository was clean at 475a91d.

## Acceptance criteria
- [x] Optional guide and template retain unfinished project requirements across tasks.
- [x] Contract covers evidence-based resumption, relevant user-visible verification,
      and distinguishing task completion from overall project completion.
- [x] Installed task template records verification evidence and pending external steps.
- [x] Documentation links and a disposable five-file install are verified.
- [ ] Required checks pass, changes are committed and pushed, and CI passes.

## Checkpoint
Reconciled the prior stale community checkpoint: 475a91d is published, all five
jobs in https://github.com/nzzl/tiny-harness/actions/runs/37431317348 passed, and
the GitHub community profile reports 100%. That work is complete; do not repeat it.

Current changes are instructions, examples, and the task-template string only;
runner execution and check configuration remain unchanged (verified by comparing
parsed code with only the TASK string excluded). A disposable installation confirms
exactly five files, the updated handoff template, and no installed backlog. Local
documentation links resolve. No new tests for prose.
Next: commit through the harness, push, and inspect CI for the resulting commit. Commit output and its GitHub Actions run
provide the final verification evidence for these pending steps. On resumption,
check those sources before repeating publication or assuming failure.
