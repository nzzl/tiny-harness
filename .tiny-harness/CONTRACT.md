# Agent operating contract

## Mandatory constraints

- Read applicable repository instructions, this contract, and TASK.md before work.
  Inspect actual code and Git status/diffs before choosing a solution. Follow the
  user's authorized scope; distinguish existing work from your changes.
- Record the outcome, boundaries, observable acceptance criteria, and existing
  changes in TASK.md. Keep one compact checkpoint: decisions, evidence, unresolved
  failures, and next action. Never mark an incomplete task or check as passed.
- Implement, test, diagnose, repair, and make local commits autonomously within
  the authorized task. Ask only for missing information that blocks progress or
  consequential actions outside existing authorization (for example publication,
  destructive data changes, or new external commitments). Routine failures are
  problems to investigate, not approval gates.
- Preserve unrelated edits, existing instructions, hooks, and Git history. Stage
  named files or selected hunks; inspect the staged diff. Include only work you
  own or are explicitly authorized to include. Never reset, clean, force-push,
  amend, or otherwise discard/rewrite work to get unstuck.
- Configure real, relevant checks in checks.json. Use behavior-focused tests
  proportional to risk; do not add tests that merely restate implementation.
  Never weaken or remove a required check to make a failure disappear. A missing
  prerequisite is a failure to resolve or report, never a silent skip.
- Commit with `python3 .tiny-harness/run.py commit -m "Reason for this change"`.
  This validates the staged tree afresh, stopping at the first failed check;
  an empty commit exits before checks. For all ordinary check results, use
  `python3 .tiny-harness/run.py validate`. Do not bypass failed
  checks or existing hooks. Keep commits small, coherent, and meaningful.
- On failure, inspect the error and relevant state, identify a cause, make a
  targeted repair, and rerun. Change approach when evidence contradicts it. If
  blocked by unavailable access, a prerequisite, or an unresolved decision,
  record exact evidence and the smallest needed intervention; do independent work.
- On resumption, read TASK.md, Git status, staged/unstaged diffs, and recent log.
  Reconcile the checkpoint with actual files before proceeding. Do not repeat an
  external action or create duplicate commits merely because the record is stale.
- Before handoff, update the checkpoint and report completed work, check results,
  commit identifiers, remaining failures/limitations, and next action if any.

## Preferences (adapt with a reason)

Prefer the smallest direct solution, few dependencies, concise documentation, and
existing project conventions. Record meaningful assumptions and tradeoffs in
TASK.md; a separate design document is rarely needed. Stop when acceptance
criteria and relevant checks pass. Extra polish is a new scope decision.

## Enforcement boundary

These instructions depend on the agent reading and following them. The runner
rejects missing/malformed/empty check configuration and unsuccessful checks;
its commit command validates first. It does not judge test quality, task truth,
authorization, or deliberate staging. Plain Git bypasses it. Existing hooks run
normally and may reject a commit. See README for snapshot and concurrency limits.
