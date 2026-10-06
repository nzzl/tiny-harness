# Security policy

## Report a vulnerability

Use GitHub's [private vulnerability reporting form](https://github.com/nzzl/tiny-harness/security/advisories/new)
for suspected vulnerabilities. Reports are shared with repository maintainers,
rather than posted as public issues. A GitHub account is required.

Include the affected tag or commit, operating system, Python/Git versions,
reproduction steps, expected behavior, and potential impact. Use a disposable
repository and synthetic data. Do not include passwords, tokens, or private
project contents. Please keep exploit details out of public issues while the
report is being assessed.

Reports against any version are welcome. Where practical, check whether the issue
also occurs on the latest tag or `master`. Fixes are developed on `master`; older
versions do not have a separate backport commitment. Installed copies must be
updated by reviewing and merging changes; the installer does not overwrite them.

## Trust boundary

Tiny Harness is a discipline tool for trusted coding workflows, not a sandbox or
an authorization system. Checks run with your permissions and inherited
environment. Commands, dependencies, and symlinks can access external resources.
Read unfamiliar checks before executing them.

Configuration is taken from the staged tree, while the executing runner is a
working-tree file. Either can be changed, checks can be misleading, and ordinary
Git can bypass the workflow. Process cleanup covers the check's process group;
processes that leave that group can escape it. These are documented limits, not
claims of adversarial isolation. Unexpected behavior beyond these boundaries is
still worth reporting. See [README](README.md#limits-and-enforcement).
