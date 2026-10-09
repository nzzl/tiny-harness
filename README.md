# Tiny Harness

[![Validate](https://github.com/nzzl/tiny-harness/actions/workflows/validate.yml/badge.svg?branch=master&event=push)](https://github.com/nzzl/tiny-harness/actions/workflows/validate.yml)
[![Version](https://img.shields.io/github/v/tag/nzzl/tiny-harness?label=version&sort=semver)](https://github.com/nzzl/tiny-harness/tags)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A small operating structure for coding agents: a contract, one task checkpoint,
explicit checks, and a command that validates before making local commits. It
works with any agent that can read files and run commands. No service, model SDK,
global agent configuration, or background process is needed.

Requires Git and Python 3.9+ on macOS or Linux. Uses only the Python standard
library. CI is configured for macOS and Linux with Python 3.9 and 3.14.
Other combinations should run the same tests before adoption.

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
validation. Replace it with the project's required checks. For a Python unittest
project, adapt [tests/run.py](tests/run.py) into a tracked check script without
overwriting existing files. That script rejects empty discovery. Configure it as:

```json
{
  "checks": [
    {
      "name": "behavior tests",
      "argv": ["python3", "tests/run.py"],
      "timeout_seconds": 120
    }
  ]
}
```

Each check needs a unique nonempty name, an argument list, and a finite positive
timeout in seconds. Duplicate JSON keys and unknown keys are rejected, including
attempted optional/skip flags. Commands run in order. Commit validation stops at
the first failed check, including a missing tool or timeout; no commit is made.
Standalone `validate` continues after ordinary failures to collect all check
results, and later successes cannot erase a failure. Changes to staged snapshot
files stop either mode immediately. Every configured check remains required for
a successful commit, and a retry runs the checks afresh.
Timeouts terminate the check's process group on supported platforms.

Use relevant, proportionate checks with observable behavior. A command returning
zero is the runner's success signal: configure the underlying test tool to reject
zero discovered tests and avoid cached no-op runs where appropriate. The harness
cannot infer that a green command actually tested anything. Add broader checks
when risk warrants them; never remove a required check merely to obtain green.

Passing checks show that their encoded expectations were satisfied, not that
those expectations are correct. Tests that capture current behavior can protect
against unintended changes, but should be identified as such when that behavior
has not been independently justified. Coverage and mutation scores help assess
tests; neither proves correctness.

For example, a cleanup check should observe that child processes stop and
temporary files disappear, rather than only checking for a “cleanup complete”
message. Where practical, demonstrate that it detects the original leak and
passes with the fix.

For pure-Python src-layout projects and Node/npm projects, start from the
[tested adoption examples](examples/README.md). These are optional configurations;
merge them with existing required checks rather than replacing those checks.

For Python dependencies, reuse the project's isolated environment and package
manager. If none exists, create a local `.venv` and exclude it from Git. Activate
it in the same shell command that runs the harness, for example
`. .venv/bin/activate && python3 .tiny-harness/run.py validate`, or run the harness
through the tool's runner, such as `uv run` or `poetry run`. Agent tools that start
a fresh shell per command do not keep an earlier activation. Keep dependencies out
of the host's system Python. Checks
should resolve `python3` and other tools through that environment's PATH; a
relative `.venv/bin/python` command cannot use the ignored environment inside the
staged snapshot. Existing uv, Poetry, Conda, or container setups can be retained.
This is an agent instruction, not a runner gate. Tiny Harness itself needs no venv
or third-party Python packages. Environment isolation does not replace the source
origin checks described in the adoption examples.

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
If nothing is staged, `commit` exits before running checks or hooks. A pending
merge with an unchanged tree still validates and commits its ancestry. Every
nonempty commit attempt validates afresh; no stale success file is trusted. After
a failed commit check, use `validate` when you want all remaining diagnostics.
Keep commits coherent. A checkpoint committed with a change can say that commit
validation is pending; the command output supplies the result. Report the new
commit ID at handoff without creating an endless bookkeeping commit loop.

## Work across multiple sessions

For a project spanning several tasks, keep unfinished requirements in an existing
backlog or a persistent feature checklist linked from `TASK.md`. Record observable
acceptance steps and their verification evidence. On resumption, reconcile the
checkpoint with Git and external results, then choose the next bounded item.
Use a relevant smoke check when implementation state is uncertain; avoid repeating
unrelated checks. A passing commit alone does not establish project completion.

See the optional [long-running-project recipe](examples/long-running/README.md)
and [feature checklist template](examples/long-running/FEATURES.md). These are
instructions, not additional runner enforcement, and are not copied by install.
Small changes can continue using the ordinary task checkpoint.

## What validation checks

The runner freezes the Git index into a tree and checks out a fresh temporary
copy using a private index. Checks and configuration come from that staged tree.
Unstaged edits, untracked files, ignored dependencies, and `.git` are absent.
Build output is discarded afterward. Partially staged work is supported: the
snapshot contains the staged versions, even when the working files differ.

The process environment and installed tools are inherited. A check must actually
read the snapshot's source for staged-source validation to hold. For example,
Python editable installs or an older installed project can redirect imports to
code outside the snapshot, allowing an unstaged repair to hide a staged failure.
The runner does not infer which source an arbitrary command imports or executes.
Use explicit dependency setup and project-source origin checks where appropriate;
see the tested [Python and Node adoption examples](examples/README.md). External
services, tools, and caches can also affect results.

After each check, the runner verifies that the snapshot's original files,
symlinks, executable bits, and directory types remain unchanged. A changed,
deleted, or unreadable staged path blocks the commit before another check can
run against repaired content. Untracked build output is allowed. Run formatters
and generators that update tracked files before staging; use read-only check
modes during validation. This guard checks state between commands; it cannot
detect a command that changes and restores a file internally or falsifies results.

Dependency installation must be explicit. Git-dependent build tools need an
adapted check; there is no Git history inside the temporary snapshot. Submodules
are rejected instead of silently omitted. Git LFS/filter-dependent checkouts,
platform-specific file semantics, and checks requiring external services are
not verified by this project's suite; test your setup before relying on it.

The runner rejects an unmerged index and detects index or HEAD changes during
validation. Use one writer per repository while validating/committing; it does
not lock out another process and a narrow check-to-commit race remains.

## Check processes and changes to validation

Each check runs in a separate process group. When it finishes, fails, or times
out, the runner kills any remaining processes in that group before inspecting
the snapshot or running another check. SIGINT (Ctrl-C), SIGTERM, and SIGHUP to
the runner also trigger check cleanup and removal of the temporary snapshot.
SIGKILL and other uncatchable termination cannot trigger cleanup. Processes that
deliberately start a new session or leave the group escape cleanup; this is not
a sandbox.

Checks are noninteractive. Their standard input is empty (`/dev/null`), and they
have no controlling terminal, so a prompt cannot read from the caller's terminal
or input. Most reads end immediately at end of input; a command that ignores it
waits until its timeout. Configure tools with their noninteractive or CI options.

Staged check configuration and its `.tiny-harness` directory cannot be symlinks.
The configuration still comes from the proposed commit, so that commit can also
change or weaken its own checks. The executing runner comes from the working
tree. Before validating a commit, the runner warns about staged changes to
`checks.json` or `run.py`, and about an executing runner different from HEAD.
Initial adoption has no previous version to compare. Warnings require no flag
or additional confirmation, and all configured checks still run normally.

Review changes to validation deliberately. The warning cannot judge whether a
change weakens a check, detect all changes to scripts invoked by checks, or stop
an agent modifying the runner or bypassing it with plain Git. Strong enforcement
requires independently controlled CI and branch protection/review rules.

## Recovery

Read the checkpoint, actual Git status/diffs, and recent history; reconcile them
before resuming. A stale checkpoint is not a reason to undo work or repeat a
commit. Run the canonical validation again when evidence is missing or stale.

- **Missing or empty configuration:** configure real checks and stage the config.
  An unstaged config is deliberately ignored.
- **Check failure or timeout:** inspect its output, repair the cause or prerequisite,
  stage the repair, and rerun. Change approach when evidence warrants it.
- **Snapshot modified:** perform the repair in your working tree, review and stage
  it, then use checks that leave staged snapshot files unchanged. Do not disable
  the guard or suppress a required check.
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

## Contributing and reporting

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, checks, and pull requests, and
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for participation expectations.
Report bugs through [issues](https://github.com/nzzl/tiny-harness/issues/new/choose).
For suspected vulnerabilities, follow [SECURITY.md](SECURITY.md).

## This repository

The contract is loaded through `AGENTS.md`; `.tiny-harness/TASK.md` records the
work. Required staged-tree checks run basic Python lint and `tests/run.py`, which
discovers behavior tests and rejects zero discovered tests. Tests use disposable
repositories, exercise failure and recovery, and invoke an installed copy without
changing your Git settings.

For development, create a virtual environment and install the pinned check tool:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
```

Ruff checks common Python errors, undefined names, and unused imports/variables;
formatting is not required. Its version is pinned in both `requirements-dev.txt`
and `ruff.toml`; update them together. A missing or mismatched tool fails visibly.
The harness runtime and installed copies still require only Git and Python's
standard library. Adopting repositories configure their own checks.

GitHub Actions runs the same canonical validation on macOS/Linux and Python
3.9/3.14 for pushes and pull requests. A separate Linux job tests the npm adoption
recipe with Node 22. Run that probe locally with `python3 tests/check_node_example.py`
when changing the Node example; it requires Node/npm but no registry access.
Python recipe regressions are part of the required behavior suite and use an
isolated editable-style import fixture without downloading packaging tools.
Merge enforcement additionally requires the repository's branch rules.

CI also reports advisory production-code review triggers: files over 300 physical
lines, functions over 50 physical lines, and McCabe complexity over 10. Tests are
excluded from these size/complexity advisories. They do not block commits or CI;
use a warning to assess readability, not automatically split code to meet a number.
Run them locally from the repository root with:

```sh
python3 tests/size_warnings.py
ruff check --no-cache --config ruff.toml --select C901 --exit-zero .tiny-harness
```

[Source notes](SOURCE-NOTES.md) describe the actual source and design reductions.
New Tiny Harness code and documentation use the [MIT license](LICENSE).
The installer carries that notice into adopted repositories. No upstream source
license is asserted or changed.
