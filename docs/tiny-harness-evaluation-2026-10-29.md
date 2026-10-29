# Tiny Harness evaluation, 2026-10-29

Two small evaluations compared Claude Code sessions with and without parts of
Tiny Harness. In these trials Tiny Harness showed no benefit. The trials do not
show that Tiny Harness is useless, and they do not show that it doubles usage in
general. This note explains what was measured and what limits the result.

The project's own test suite shows that the runner and the recipes behave as
documented. These evaluations asked a different question: does an agent
produce better work with the harness? The tests answer only the first question.

## Setup

- **Tiny Harness:** commit `febe44c`, three commits after `v0.1.3`. Used
  unchanged.
- **Agent:** Claude Code 2.1.312 in headless mode (`claude -p`), using model
  `claude-opus-5-5` at effort `high`. The account was a subscription login, not
  an API key.
- **Same in every session:** model, effort, tools (Bash, Read, Edit, Write,
  Glob, Grep), and permission mode.
- **Isolation:** user settings, MCP servers, session persistence, and
  auto-memory were turned off. Every session started in a fresh disposable
  repository with no remote, and had a 15-minute limit.
- **Configurations:**
  - **A, baseline:** Claude Code alone. The project instructions point to the
    README for the test command. The repository has no harness files and no
    contract text.
  - **B, harness:** A plus the installed `.tiny-harness/` directory, the
    recommended startup paragraph, and a configured check. The context-brief
    pilot was not included.
- **Same in both configurations:** prompts, code, tests, documented test
  commands, and handoff information.
- **Order:** A then B for scenarios 1 and 3, B then A for scenario 2.

Scenarios:

1. **Bug fix.** A business-day calculation returns a holiday when the holiday
   follows a weekend or a second holiday. The task asks for a fix, regression
   tests, and boundary cases.
2. **Resume.** A handoff note says amounts are float dollars. A later commit by
   another contributor changed them to integer cents. The task is to finish the
   work and keep the contributor's change.
3. **Commit scope.** The task authorizes the commit of one staged hunk. The same
   file also has an unstaged draft. The repository also has an unstaged README
   edit and an untracked failing test, and neither may be committed. The test
   suite therefore fails in the working tree but passes on the staged tree.

## Results

Each scenario ran once per configuration, so there are six sessions in total.
"Passed" means that the session passed every hidden behavior check, every
requirement check, every preservation check, and every commit-scope check.

| Scenario | Configuration | Result | Elapsed | Tool calls | Output tokens |
|---|---|---|---|---|---|
| 1 Bug fix | A baseline | passed | 40.9 s | 7 | 3,739 |
| 1 Bug fix | B harness | passed | 72.8 s | 11 | 6,601 |
| 2 Resume | B harness | passed | 110.0 s | 16 | 9,780 |
| 2 Resume | A baseline | passed | 49.5 s | 6 | 4,712 |
| 3 Commit scope | A baseline | passed | 26.4 s | 6 | 2,286 |
| 3 Commit scope | B harness | passed | 48.0 s | 11 | 4,575 |
| **Total** | A baseline | 3 of 3 | 116.8 s | 19 | 10,737 |
| **Total** | B harness | 3 of 3 | 230.8 s | 38 | 20,956 |

In every session, both configurations made exactly one commit and kept history.
Without the harness, the baseline also handled every situation that the
scenarios tested:

- It checked the later commit before it trusted the handoff note.
- It staged only named files.
- In scenario 3, it ran the tests on an export of the index, not on the working
  tree.

The harness sessions used `run.py commit`, which validated the staged tree. They
also updated `TASK.md` and showed tests failing before the fix more
consistently. The harness sessions also removed their temporary files. Two
baseline sessions left one temporary file or directory each.

**Overhead.** In these sessions, the harness configuration took about twice the
elapsed time, twice the tool calls, and twice the output tokens. The harness
sessions did three kinds of extra work: they read the contract and checkpoint,
they wrote checkpoint updates, and they ran the extra test demonstrations that
the contract asks for. This split was not measured. The re-validation by `run.py commit` cost almost nothing, because the
fixture test suites ran in milliseconds. The sessions used a subscription, so
the token counts measure usage. They do not show any additional charge.

No difference in correctness was measured. The harness did not prevent a
mistake that the baseline made, and it did not cause a mistake in code or
commits.

## Corrections and limitations

- **Grading corrections.** The automatic grader failed three sessions on test
  preservation: one baseline session and two harness sessions. In each, the
  agent had moved `tests/test_cli.py` into a helper and kept the same inputs and
  expected outputs. The original test files, rerun unchanged against each
  committed result, passed. After this inspection, these sessions were graded as
  passes. The pre-launch grader checks covered deleted tests, not refactored
  tests.
- **Early checkpoint claims.** All three harness checkpoints were committed with
  the status "done", including the claim that the commit had been made, before
  commit validation had run. The final results passed, but these claims came
  before their evidence. The README allows a checkpoint to say that validation
  is pending, and the agents did not use that option.
- **Weaker isolation.** All six sessions could reach the same scratch directory,
  which also contained the trial workspaces. Transcript review found no session
  that accessed another session's workspace, but the isolation was weaker than
  intended.
- **Sample size and fixtures.** Each configuration and scenario ran only once.
  The fixtures were small and easy for this model at this effort level. The
  longest session took 110 seconds. The same model family wrote the scenarios.
- **Generalization.** These results do not show how the harness affects longer
  or multi-session work, weaker models, lower effort, slow or flaky test suites,
  or agents that commit with `git add -A`.

## Context-brief pilot

A separate set of six sessions tested the optional
[context-brief pilot](../examples/context-brief/README.md). These sessions used
the same runtime and model. All three configurations included the core harness:

- the core harness only;
- the core harness, the checkpoint fields, and the log recipe;
- the full brief, which adds the brief script to those.

Two scenarios were tested: a stale checkpoint, and a long validation log that
hid a real failure. All six sessions passed. The full-brief agents were offered
the brief, but neither ran it. Offering the brief therefore showed no benefit.
The effect of actually running the brief remains untested.

The evaluation also found that the log recipe failed in zsh, because `status` is
a read-only zsh variable. The recipe now uses `validation_exit_code`, and its
regression tests run it under `sh` and zsh.
