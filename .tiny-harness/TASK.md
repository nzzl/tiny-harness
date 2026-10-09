# Task

Status: test-quality guidance added; required staged validation and local commit pending

## Outcome and scope
Add approved test-quality guidance so agents ground expectations in justified
sources rather than current implementation output, investigate failing tests
before changing expectations, and, where practical, confirm that important checks
detect their intended failure. Documentation only: CONTRACT.md testing bullet
replaced with four approved bullets; two README paragraphs added under
"Configure real checks". The user authorized this change. Source was clean at
ffee0ae (v0.1.2). No runner, check, test, installer, CI, or dependency changes;
no new enforcement, thresholds, tools, or approval steps. No push, tag, or release.

## Acceptance criteria
- [x] CONTRACT.md testing bullet replaced by the four approved bullets; surrounding
      instructions unchanged.
- [x] README paragraphs inserted after "Use relevant, proportionate checks...",
      which is retained.
- [x] Required-check, missing-prerequisite, staged-source, and commit-validation
      safeguards retained; justified test corrections and "where practical"
      qualifications preserved.
- [ ] Required staged checks pass and a local commit is made through the harness.

## Checkpoint
The previous cleanup-instruction task is committed as ffee0ae and published as
v0.1.2; its pending commit note was stale. This change is prose only; no tests
were added for prose. Required validation runs during commit using the existing
project `.venv`.
Next: inspect the staged diff, commit through the harness, and verify Git state.
Publication remains a separate step.
