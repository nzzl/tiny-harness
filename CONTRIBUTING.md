# Contributing to Tiny Harness

Bug reports, fixes, and small improvements are welcome. For a larger feature,
open an issue first so we can agree whether it belongs in a tiny harness.

## Development

Use Git and Python 3.9+ on macOS or Linux. From your checkout:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
```

Read [AGENTS.md](AGENTS.md) and the [contract](.tiny-harness/CONTRACT.md).
Keep changes focused, preserve unrelated work, and update the task checkpoint.
Prefer the standard library and existing patterns. Avoid adding approval steps,
services, dependencies, or quality gates without a concrete need.

## Checks and commits

Add behavior tests for bugs and meaningful behavior changes. Documentation edits
do not need new tests. Stage only your intended files and inspect the diff, then:

```sh
git diff --cached --check
python3 .tiny-harness/run.py commit -m "Describe the change"
```

Validation reads the staged versions, so stage repairs before retrying. The commit
command runs required checks and respects existing hooks. Use
`python3 .tiny-harness/run.py validate` for diagnostics without committing. Keep the virtual
environment active so Python and Ruff are available inside the temporary snapshot.
Never weaken a check just to make it pass.

If changing the Node example, also run `python3 tests/check_node_example.py`
with Node 22 and npm available. This fixture uses a local dependency and needs
no package registry access. CI runs the Python checks on macOS/Linux with Python
3.9/3.14, plus this Node example on Linux.

## Pull requests

Open a pull request against `master`. Explain the problem, the resulting behavior,
and what you checked. Mention relevant limits or untested platforms. AI-assisted
contributions are welcome; the contributor remains responsible for reviewing the
diff and verifying its behavior.

Report ordinary bugs through [issues](https://github.com/nzzl/tiny-harness/issues).
Use [private vulnerability reporting](SECURITY.md) for suspected security issues.
Follow the [code of conduct](CODE_OF_CONDUCT.md). Contributions use the existing
[MIT license](LICENSE). Keep the root and `.tiny-harness/LICENSE` notices identical;
the latter is copied into adopting repositories.
