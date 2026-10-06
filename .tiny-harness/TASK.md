# Task

Status: cleanup pass implemented; required staged validation and local commit pending

## Outcome and scope
Final small cleanup after the audit: make the installed contract's limits reference
work from adopting repositories, decide check stdin behavior from evidence, and fix
concrete problems in 614d176's Python environment guidance. Local commit only; no
push or release. Leave the verified signal cleanup unchanged.
Repository was clean at 33c1c09, which is published (CI run passed).

## Acceptance criteria
- [x] Installed contract states snapshot/environment/concurrency limits inline and
      links the upstream README section instead of an uninstalled "README".
- [x] Checks receive empty stdin; regression test fails on the previous runner
      (timed out) and passes now; README documents EOF behavior and its limits.
- [x] 614d176 guidance: activation must happen in the command that runs the harness.
- [ ] Required checks pass and the change is committed through the harness.

## Checkpoint
Stdin evidence (disposable fixtures, macOS, Python 3.10): with an idle terminal or
idle open pipe, the old runner let `read` and `input()` checks wait until timeout;
with /dev/null they end at EOF (EOF-tolerant reads pass, prompts fail immediately).
Opening /dev/tty already failed (checks have no controlling terminal). EOF-ignoring
loops still reach their timeout. No documented example relies on check stdin.
Environment evidence: harness runs without any venv; activation in an earlier
separate shell does not reach checks; same-command activation, `uv run` (0.8.22),
and `poetry run` (1.4.1) do. Conda and containers were not exercised.
Next: commit through the harness; commit output is the validation evidence.
