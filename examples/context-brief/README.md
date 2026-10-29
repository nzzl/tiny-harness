# Context brief (pilot)

This optional pilot helps an agent resume work with less rereading. It adds
three things: optional checkpoint fields, a recipe that saves long check output,
and a read-only script that prints a short brief. The installer does not copy
this example. It does not change the contract, the TASK template, the runner,
or validation.

No evaluation shows that this pilot helps agents. The tests show only that the
script reports what it claims. Use it as an experiment. If it does not help,
remove it.

## The problem it addresses

The contract tells the agent to reconcile notes with Git on resumption. A
checkpoint does not usually record which commit it describes or which files the
next step depends on. The agent must then read every change since an unknown
point. Also, at the end of a session, long check output is gone.

## Adopt

Copy `brief.py` into the project, for example to `tools/brief.py`. Do not
overwrite an existing file. Add one line to the project's own agent instructions:

> On resumption, after reading the contract and TASK.md, you can run
> `python3 tools/brief.py` for a short summary of changed sources and evidence.

## Checkpoint fields

Add these lines anywhere in `.tiny-harness/TASK.md`. All of them are optional.
See [TASK.example.md](TASK.example.md).

```
Basis: <hash of the commit the notes were last reconciled against>
Source: <repository-relative path that the next step depends on>
Evidence: <log path or URL>
Next: <one concrete action>
```

Repeat `Source:` and `Evidence:` for each item. List only the files that the
next step depends on. A directory is allowed.

`Basis:` must be a commit hash. To get it, run this command after you reconcile
the notes with the files:

```sh
git rev-parse HEAD
```

Record the printed hash, for example `Basis: 4e0d7aa9c1...`. Do not record the
word `HEAD`, a branch name, a tag, or an expression such as `HEAD~1`. Each new
commit moves those names. The brief then compares against the wrong commit and
hides changes. For this reason, the brief rejects them. A full hash or an unambiguous
abbreviation works. After the next reconciliation, record the new hash.

A basis commit does not record uncommitted contents. If the notes describe
uncommitted work, "unchanged relative to recorded basis" says nothing about that
work. Commit first or keep the uncommitted details in the notes.

## Run the brief

Run the script from inside the repository. It needs Python 3.9 or later and Git.

```sh
python3 tools/brief.py
python3 tools/brief.py --max-lines 40 --max-bytes 4000
```

The default limits are 60 lines and 6000 bytes, counted in UTF-8. The script cuts
each line at 200 characters. It rejects limits that are too small for its header,
caveat, and truncation notice. Exit status 0 means that the script printed a
brief. Status 1 means that the directory is not a Git repository or that TASK.md
cannot be read. Status 2 means a usage error.

The brief always starts with a header that says it is a navigation aid. It gives
the TASK.md line of each section, but it does not repeat scope or decisions. It
lists unchecked criteria, staged, unstaged, and untracked files, the basis
state, each source, each evidence item, and `Next:`. A list longer than eight
items ends with a marker that names the count and where to find the rest. Text
from TASK.md appears as written.

Each source gets one of these results:

- `changed (committed/staged/unstaged)`: Git shows a difference from the basis
  in at least one of these layers. Additions and deletions count.
- `unchanged relative to recorded basis`: Git shows no difference in any layer.
  This does not mean that a note about the file is correct.
- `unknown (...)`: the script cannot compare, and the reason names the cause.
  The basis problems are: none, more than one, not a commit hash, a hash that
  resolves through a reference, not found, or no HEAD. The other causes are a
  Git error, an untracked path, an absent path, or a path outside the repository.

If the basis is not an ancestor of HEAD, the brief says so. The results are then
content differences only. Evidence paths get only a size from the file system.
The script does not open them, and it does not check URLs.

The script uses `git --no-optional-locks` and writes no files. Its diff commands
use `--no-ext-diff` and `--no-textconv`, and all its Git commands use
`-c core.fsmonitor=false`. Configured diff helpers, text conversion programs,
and fsmonitor hooks do not run and cannot change a result. It does not edit
TASK.md. It is not a check, and it runs on the working tree, not on the staged
snapshot. Required checks still run in full at each commit.

## Save long check output

Use this recipe instead of pasting long output into notes. Run it from the
repository root. It runs in a subshell, so it does not change your shell
configuration. It returns the exact exit status of validation.

```sh
(
  set +e
  dir="$(git rev-parse --git-path tiny-harness/logs)" && mkdir -p "$dir" &&
    log="$(mktemp "$dir/validate-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")" ||
    { echo "Log setup failed. Validation did not run." >&2; exit 125; }
  python3 .tiny-harness/run.py validate >"$log" 2>&1
  status=$?
  echo "validate exit $status; log: $log"
  grep -nE '^(RUN|PASS|FAIL|ERROR|WARNING)' "$log" | tail -n 40
  exit "$status"
)
```

The recipe has these properties:

- `mktemp` makes a new file each time, so earlier logs stay unchanged.
- Logs go under the Git directory, so Git never stages them and the staged
  snapshot never contains them.
- If setup fails, the recipe prints a message and returns 125 without running
  validation.
- The `grep` line shows the result lines of the runner.

Record the log path in an `Evidence:` line, with the few lines that matter. For a
commit, replace `validate` with `commit -m "..."` in the runner command.

Warning: logs can contain secrets that checks print. Logs are local and a fresh
clone does not have them. Use a CI link for evidence that must last. If you no
longer need old logs, delete them from the printed directory.

## Remove

Delete the copied script, the instruction line, and any fields you added to
TASK.md. Nothing else depends on them.
