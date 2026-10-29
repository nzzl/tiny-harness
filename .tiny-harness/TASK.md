# Task

Status: implemented and tested locally. Staged validation and local commit pending.

## Outcome and scope
Update the documentation to match what Tiny Harness has been shown to do and what
the 2026-10-29 evaluations found. Fix the context-brief log recipe, which fails in
zsh because `status` is a read-only zsh variable.

In scope:
- README positioning and adoption guidance.
- A new evaluation note under `docs/`.
- Context-brief pilot wording in `examples/context-brief/README.md` and
  `examples/README.md`.
- The recipe variable rename.
- Recipe tests under sh and zsh.
- This file.

Out of scope: `CONTRACT.md`, `run.py`, the installer, the installed template, and
`checks.json`. No new features, no change to the pilot design, and no rerun of
agent evaluations. No push, tag, or release. The evaluation records are read-only
sources.

## Acceptance criteria
- [x] The README describes a validation-before-commit utility. It keeps the
      enforcement boundary and makes no claim about accuracy, discipline, or
      time or token savings. It includes adoption guidance and the distinction
      from CI.
- [x] The evaluation note gives the version, the runtime, the three scenarios,
      a results table, the overhead, and the limitations, and the README links
      to it. It contains no private material.
- [x] The context brief stays optional and experimental, with the observed
      result stated.
- [x] The recipe uses `validation_exit_code`. The tests run the recipe under sh
      and zsh, covering exit status, unique logs, setup failure, and caller
      options. A missing zsh is reported, not hidden.
- [x] The original recipe fails under zsh and the fixed one passes, both shown
      in disposable fixtures.
- [ ] Required staged checks pass, and the local commit is made with `run.py commit`.

## Checkpoint
Evidence: in a scratch fixture with zsh 5.9 and macOS `sh`, the original recipe
returned 7 under sh. Under zsh it printed "read-only variable: status" and
returned 1. After the variable was renamed to `validation_exit_code`, all six
`LogRecipeTests` and `ZshLogRecipeTests` passed under the project `.venv`
(Python 3.14.7) with zsh 5.9. In a scratch copy with the original recipe
restored, both zsh tests that need validation's exit status failed: the result
was 1, not 7, with "read-only variable: status". The sh tests still passed.
The figures in the evaluation note match the saved `grades.json` totals
(116.8 s, 19 calls, 10,737 tokens; 230.8 s, 38 calls, 20,956 tokens).
Limit: when zsh is missing, the zsh tests skip with a reason that says zsh is
not verified. Linux CI runners may not include zsh, so CI there may cover only
sh. The skip path was not exercised locally, because zsh is installed.
Next: stage the named files, inspect the staged diff, and commit with
`run.py commit`. The result of commit validation comes from the command output.
