# Task

Status: pilot implemented and tested. Required staged validation and local commit pending.

## Outcome and scope
Add an optional context-brief pilot under `examples/context-brief/`: example
checkpoint fields (Basis, Source, Evidence, Next), a documented log-saving
recipe, and a read-only `brief.py`, with tests and a link from
`examples/README.md`. The user authorized steps 1 to 3 of the revised plan.
Source was clean at 34fcab1 (v0.1.3). No change to `run.py`, `CONTRACT.md`,
`checks.json`, the installed TASK template, or the installer. No agent
evaluation, push, tag, or publication. Agent benefit stays untested.

## Acceptance criteria
- [x] `brief.py` reports changed, unchanged relative to the recorded basis, or
      unknown for each referenced file. It separates Git differences from Git
      errors. It reports missing or invalid bases, unborn HEAD, diverged
      history, untracked files, and paths outside the repository.
- [x] Output always starts with the navigation-aid header and caveat, and fits
      the line and byte limits (including multibyte text). Budgets too small
      for the header, caveat, and truncation notice are rejected.
- [x] `brief.py` writes nothing: the index and working tree are unchanged.
- [x] The log recipe runs in a subshell, never overwrites a log, reports setup
      failure clearly, and returns the exact validation status.
- [ ] Required staged checks pass and a local commit is made with `run.py commit`.

## Checkpoint
Evidence: `tests/test_context_brief.py` has 15 tests. They pass on Python 3.14.7
(project `.venv`) and on Python 3.10, in a disposable repository. Python 3.9 is
not installed locally, so CI covers it after a push. The recipe tests run the
README code block itself, with a stand-in runner that exits 7.
Controlled fault: when `compare` always returned "unchanged", five tests failed.
The fault is reverted.
Manual observation: with the real runner and a failing check in a scratch
fixture, the recipe returned 1, the same as a direct `validate`. A second run in
the same second made a new 0600 log, and the first log stayed unchanged. The
fixture is deleted.
Two test expectations were wrong at first and were corrected with reasons:
`git rm` leaves no unstaged difference, and the 60-line default budget does not
truncate the capped fixture output.
Not tested: any benefit to agents. That needs the separately approved evaluation.
Next: stage the named files, inspect the staged diff, and commit with `run.py commit`.
