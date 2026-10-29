# Task

Status: review repair implemented and tested. Required staged validation and local commit pending.

## Outcome and scope
Fix two review findings in the optional context-brief pilot (commit 75a543e).
First, `brief.py` inherited external-diff and text-conversion configuration, so
a configured helper ran, wrote files, and reported a changed source as
unchanged. Second, `Basis:` accepted moving references such as `HEAD`, so later
commits moved the baseline and hid changes. Bounded repair only: `brief.py`, its
tests, and the example README. No change to `run.py`, `CONTRACT.md`,
`checks.json`, the installed template, the installer, Git configuration, or the
pilot architecture. No push, tag, publication, or agent evaluation.

## Acceptance criteria
- [x] All `brief.py` diff commands pass `--no-ext-diff --no-textconv`.
      Changed, unchanged, and unknown results and error reporting stay the same.
- [x] `Basis:` must be a hexadecimal commit hash (4 to 64 digits). `HEAD`,
      branch and tag names, `@`, and revision expressions are rejected with an
      explicit unknown state. A hex-named branch that wins resolution is
      rejected. Full and unambiguous abbreviated hashes work. Unavailable and
      non-commit hashes give "basis not found".
- [x] The example README shows `git rev-parse HEAD` and says to record the
      printed hash, not the word `HEAD`. The uncommitted-contents caveat stays.
- [ ] Required staged checks pass and a local commit is made with `run.py commit`.

## Checkpoint
Evidence: six new tests in `tests/test_context_brief.py` failed on the unfixed
code (12 failures, counting subtests). The external diff helper and the text
conversion each hid all three changed layers. Every moving reference was
accepted as a basis. After the fix, all 21 tests pass on Python 3.14.7 (project
`.venv`) and on Python 3.10, and ruff passes. Python 3.9 is not installed
locally, so CI covers it after a push.
Three existing tests recorded `Basis: HEAD`. They now record real hashes.
Open finding, not in this scope and not tested: worktree diffs can still start
a configured `core.fsmonitor` hook. That hook tells Git which files changed, so
a faulty hook can run code and hide unstaged changes. This needs its own
decision.
Next: stage the named files, inspect the staged diff, and commit with `run.py commit`.
