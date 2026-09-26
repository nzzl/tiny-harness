# Tiny Harness

A small operating structure for coding agents: a contract, one task checkpoint,
explicit checks, and a command that validates before making local commits. It
works with any agent that can read files and run commands. No service, model SDK,
global agent configuration, or background process is needed.

Requires Git and Python 3.9+ on macOS or Linux. Uses only the Python standard
library. Automated verification currently covers macOS with Python 3.10; other
supported combinations should run the same tests before adoption.

## Install into an existing repository

From the destination repository's root, run the copy from your Tiny Harness checkout:

```sh
python3 /path/to/tiny-harness/.tiny-harness/run.py install .
```

This adds only `.tiny-harness/`: `CONTRACT.md`, `TASK.md`, `checks.json`, `run.py`,
and `LICENSE`. It preserves existing agent instructions, hooks, Git configuration,
project files, and history. It does not stage or commit anything. It refuses an
existing `.tiny-harness` directory, file, or symlink; upgrades require reviewing
and merging changes deliberately. An interrupted partial installation also
requires inspection, not an overwrite retry.

Read existing instructions and add a reference to `.tiny-harness/CONTRACT.md`
where appropriate; do not replace an existing `AGENTS.md` or `CLAUDE.md`. Resolve
conflicting instructions using the project's authority rules before work. For
agents that do not automatically load `AGENTS.md`, put this in their startup
instructions or opening message:

> Read the repository instructions, `.tiny-harness/CONTRACT.md`, and
> `.tiny-harness/TASK.md` before working. Follow the contract within the task's
> authorization, and use its validation-and-commit command for local commits.

## Configure real checks

The installed configuration starts with an empty `checks` list, which **fails**
validation. Replace it with the project's required checks. For example, a Python
project with actual tests under `tests/` could use:

```json
{
  "checks": [
    {
      "name": "behavior tests",
      "argv": ["python3", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "timeout_seconds": 120
    }
  ]
}
```

Each check needs a unique nonempty name, an argument list, and a finite positive
timeout in seconds. Unknown keys are rejected, including attempted optional/skip
flags. Commands run in order; a failure remains a failure even when later checks
pass. Every configured check runs every time. A missing tool or timeout fails.
Timeouts terminate the check's process group on supported platforms.

Use relevant, proportionate checks with observable behavior. A command returning
zero is the runner's success signal: configure the underlying test tool to reject
zero discovered tests and avoid cached no-op runs where appropriate. The harness
cannot infer that a green command actually tested anything. Add broader checks
when risk warrants them; never remove a required check merely to obtain green.

Arguments do not undergo shell expansion. Use an explicit shell command only
when necessary. Keep setup reproducible: a required check can invoke a tracked
script that installs locked dependencies and runs tests. Missing prerequisites
must fail visibly. Do not commit credentials or personal environment paths.

## Normal work

1. Read instructions and `TASK.md`; inspect status, diffs, and recent commits.
   Record the outcome, scope, acceptance criteria, and existing changes.
2. Implement and investigate failures autonomously within authorization. Update
   the checkpoint at milestones with evidence and a concrete next action.
3. Stage only intended files or hunks and review the staged diff:

   ```sh
   git add path/to/owned-change .tiny-harness/TASK.md
   git diff --cached --check
   git diff --cached
   python3 .tiny-harness/run.py commit -m "Explain why this coherent change is needed"
   ```

   On first adoption, deliberately stage the new `.tiny-harness` files too.
   The command validates and then makes one ordinary Git commit, using existing
   identity, signing settings, and hooks. No automatic staging or history rewriting.

Use `python3 .tiny-harness/run.py validate` for validation without committing.
The commit command always validates again; it does not trust a stale success file.
Keep commits coherent. A checkpoint committed with a change can say that commit
validation is pending; the command output supplies the result. Report the new
commit ID at handoff without creating an endless bookkeeping commit loop.

## What validation checks

The runner freezes the Git index into a tree and checks out a fresh temporary
copy using a private index. Checks and configuration come from that staged tree.
Unstaged edits, untracked files, ignored dependencies, and `.git` are absent.
Build output is discarded afterward. Partially staged work is supported: an
unstaged repair cannot hide a failing staged version. Checks see the same staged
content on every fresh run, although external tools/caches can still affect them.

Dependency installation must be explicit. Git-dependent build tools need an
adapted check; there is no Git history inside the temporary snapshot. Submodules
are rejected instead of silently omitted. Git LFS/filter-dependent checkouts,
platform-specific file semantics, and checks requiring external services are
not verified by this project's suite; test your setup before relying on it.

The runner rejects an unmerged index and detects index or HEAD changes during
validation. Use one writer per repository while validating/committing; it does
not lock out another process and a narrow check-to-commit race remains.

## Recovery

Read the checkpoint, actual Git status/diffs, and recent history; reconcile them
before resuming. A stale checkpoint is not a reason to undo work or repeat a
commit. Run the canonical validation again when evidence is missing or stale.

- **Missing or empty configuration:** configure real checks and stage the config.
  An unstaged config is deliberately ignored.
- **Check failure or timeout:** inspect its output, repair the cause or prerequisite,
  stage the repair, and rerun. Change approach when evidence warrants it.
- **Index/HEAD changed:** inspect competing changes, coordinate the writer, and
  rerun against the intended staged tree. Do not reset someone else's work.
- **Hook/signing/identity failure:** diagnose the existing Git setup. Do not
  bypass hooks or fabricate an identity. Retry after resolving the prerequisite.
- **Hook changed the commit tree:** the command reports failure, but the commit
  already exists. Inspect history and make a new validated corrective commit;
  do not amend or erase the existing commit.
- **Blocked:** record the exact error, attempted recovery, and smallest missing
  input/access. Continue independent work; ask only for the genuine blocker.

## Limits and enforcement

Markdown governs scope, deliberate staging, preservation, test quality, and
honest checkpoints by instruction. The runner enforces configuration validity
and check exit status **only when invoked**. Plain `git commit`, a changed runner,
or deliberately misleading checks can bypass this workflow. Existing hooks may
modify the commit; the runner detects a differing final tree afterward and
reports failure, but cannot undo an already-created commit safely.

Checks are trusted executable project code running with your permissions and
environment; the temporary directory is isolation for reproducibility, not a
security sandbox. Symlinks and commands can access external files. Inspect a
repository before running its checks. No daemon, universal hook, remote CI gate,
test-quality oracle, or authorization engine is installed. If a project needs
server-side enforcement, configure its existing CI/branch rules separately.

## This repository

The contract is loaded through `AGENTS.md`; `.tiny-harness/TASK.md` records the
build. `.tiny-harness/checks.json` runs `tests/test_runner.py` through the canonical
entry point. Tests use disposable repositories, exercise failure and recovery,
and invoke an installed copy without changing your Git settings.

[Source notes](SOURCE-NOTES.md) describe the actual source and design reductions.
New Tiny Harness code and documentation use the [MIT license](.tiny-harness/LICENSE).
The installer carries that notice into adopted repositories. No upstream source
license is asserted or changed.
