# Task

Status: in progress

## Outcome and scope
Add a retry limit to the fetch client. Change only `src/client.py`, its tests,
and the API documentation. No release or dependency changes.

## Acceptance criteria
- [x] Backoff helper returns increasing delays.
- [ ] Fetch stops after three failed attempts and reports the last error.
- [ ] API documentation describes the retry limit.

## Checkpoint
Decision: keep the limit as a constant until a caller needs a parameter.
Unresolved failure: `test_fetch_gives_up` fails with four attempts instead of three.
Basis: 4e0d7aa
Source: src/client.py
Source: tests/test_client.py
Source: docs/api.md
Evidence: .git/tiny-harness/logs/validate-20261029T101500Z-a1B2c3
Evidence: https://ci.example.invalid/runs/1234
Next: fix the off-by-one in the retry loop, then rerun the focused test.
