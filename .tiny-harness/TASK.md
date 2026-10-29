# Task

Status: fsmonitor repair implemented and tested. Required staged validation and local commit pending.

## Outcome and scope
Fix the remaining review finding in the optional context-brief pilot (after
commit f913840). `brief.py` inherited `core.fsmonitor` configuration. A primed
fsmonitor hook that reported no changed paths ran during the brief, created a
file, and hid an unstaged modification. Bounded repair: the shared `git()`
wrapper in `brief.py`, one regression test, one README sentence, and this file.
No change to `run.py`, `CONTRACT.md`, `checks.json`, the installed template, the
installer, or repository or global Git configuration. No push, tag,
publication, or agent evaluation.

## Acceptance criteria
- [x] Every Git subprocess in `brief.py` runs with `-c core.fsmonitor=false`.
      `--no-optional-locks`, `--literal-pathspecs`, `--no-ext-diff`,
      `--no-textconv`, basis validation, and comparison semantics stay the same.
- [x] A regression test primes a real fsmonitor hook that hides a change, then
      shows that the brief never runs the hook. The source is reported as
      changed (unstaged), it appears in the unstaged list, and `.git/config` and
      the index stay unchanged.
- [ ] Required staged checks pass and a local commit is made with `run.py commit`.

## Checkpoint
Evidence: `test_fsmonitor_hook_is_never_invoked` asserts that its fixture works.
Plain `git diff --quiet` must report no difference, and the hook must have run
during priming. Otherwise the test fails, so a setup problem cannot skip it.
Before the fix, the test failed with "brief invoked the fsmonitor hook". A
manual scratch reproduction also showed "unchanged relative to recorded basis"
and an empty unstaged list. After the fix, all 22 brief tests pass on Python
3.14.7 (project `.venv`) and Python 3.10, and ruff passes. Python 3.9 is not
installed locally, so CI covers it after a push.
Limit: the test covers a hook-based fsmonitor (protocol 2). The built-in daemon
(`core.fsmonitor=true`) is turned off by the same override but is not tested.
Next: stage the named files, inspect the staged diff, and commit with `run.py commit`.
