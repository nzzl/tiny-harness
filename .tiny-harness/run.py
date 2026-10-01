#!/usr/bin/env python3
"""Tiny Harness: validate the staged tree, commit it, or install without overwrites."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import sys
import tempfile


TASK = """# Task

Status: ready

## Outcome and scope
Replace with the authorized outcome and boundaries before implementation.

## Acceptance criteria
- [ ] Replace with observable success criteria.

## Checkpoint
Record existing changes, decisions, checks and results, failures, and next action.
Update before a handoff or interruption and at meaningful milestones.
"""


class Failure(Exception):
    pass


def git(root, *args, env=None):
    result = subprocess.run(["git", "-C", str(root), *args], env=env,
                            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise Failure(result.stderr.strip() or "Git command failed: " + " ".join(args))
    return result.stdout.strip()


def repository(path):
    return Path(git(path, "rev-parse", "--show-toplevel")).resolve()


def head(root):
    result = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
                            text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else None


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate configuration key: " + repr(key))
        result[key] = value
    return result


def configuration(snapshot):
    path = snapshot / ".tiny-harness/checks.json"
    try:
        config = json.loads(path.read_text(), object_pairs_hook=unique_object)
    except (OSError, ValueError) as error:
        raise Failure("Required staged configuration is missing or invalid: " + str(error))
    if not isinstance(config, dict) or set(config) != {"checks"}:
        raise Failure("Configuration must contain only 'checks'.")
    checks = config["checks"]
    if not isinstance(checks, list) or not checks:
        raise Failure("Configure at least one required check; empty configuration is not success.")
    names = set()
    for check in checks:
        if not isinstance(check, dict) or set(check) != {"name", "argv", "timeout_seconds"}:
            raise Failure("Each check needs name, argv, and timeout_seconds (no unknown keys).")
        name, argv, timeout = check["name"], check["argv"], check["timeout_seconds"]
        if not isinstance(name, str) or not name.strip() or name in names:
            raise Failure("Check names must be nonempty and unique.")
        names.add(name)
        if not isinstance(argv, list) or not argv or any(not isinstance(a, str) for a in argv) or not argv[0]:
            raise Failure("Check argv must be a nonempty list of strings with an executable.")
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
            raise Failure("Check timeout_seconds must be a finite positive number.")
    return checks


def run_check(check, snapshot):
    print("RUN " + check["name"] + ": " + json.dumps(check["argv"]), flush=True)
    try:
        process = subprocess.Popen(check["argv"], cwd=snapshot, start_new_session=True)
    except OSError as error:
        print("FAIL " + check["name"] + ": " + str(error), flush=True)
        return False
    try:
        code = process.wait(timeout=check["timeout_seconds"])
    except (subprocess.TimeoutExpired, KeyboardInterrupt) as error:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
        if isinstance(error, KeyboardInterrupt):
            raise
        print("FAIL " + check["name"] + ": timed out", flush=True)
        return False
    print(("PASS " if code == 0 else "FAIL ") + check["name"] + " (exit " + str(code) + ")", flush=True)
    return code == 0


def unchanged(root, tree, previous_head):
    if git(root, "write-tree") != tree or head(root) != previous_head:
        raise Failure("Index or HEAD changed during validation; inspect changes and run again.")


def snapshot_signature(path):
    """Record content, file kind, and executable bit without following symlinks."""
    try:
        mode = path.lstat().st_mode
        content = None
        if stat.S_ISLNK(mode):
            content = os.readlink(path)
        elif stat.S_ISREG(mode):
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            content = digest.digest()
        return stat.S_IFMT(mode), mode & stat.S_IXUSR, content
    except OSError:
        return None


def snapshot_baseline(snapshot):
    # At checkout time these are staged paths and their parent directories only.
    # Retaining this list lets checks add untracked build output afterward.
    baseline = {}
    for path in [snapshot, *snapshot.rglob("*")]:
        signature = snapshot_signature(path)
        if signature is None:
            raise Failure("Cannot inspect staged snapshot path: " + str(path.relative_to(snapshot)))
        baseline[path] = signature
    return baseline


def snapshot_unchanged(snapshot, baseline, check):
    for path, signature in baseline.items():
        if snapshot_signature(path) != signature:
            raise Failure("Check " + repr(check["name"]) + " modified staged snapshot path "
                          + repr(str(path.relative_to(snapshot))) + "; no commit was made. "
                          "Run repairs before staging, then validate again.")


def validate(root, *, fail_fast=False):
    tree, previous_head = git(root, "write-tree"), head(root)
    print("Validating staged tree " + tree, flush=True)
    with tempfile.TemporaryDirectory(prefix="tiny-harness-") as directory:
        temporary = Path(directory)
        snapshot = temporary / "snapshot"
        snapshot.mkdir()
        env = dict(os.environ, GIT_INDEX_FILE=str(temporary / "index"))
        git(root, "read-tree", tree, env=env)
        entries = git(root, "ls-files", "--stage", env=env)
        if any(line.startswith("160000 ") for line in entries.splitlines()):
            raise Failure("Submodules are unsupported; required contents cannot be silently omitted.")
        git(root, "checkout-index", "--all", "--prefix=" + str(snapshot) + os.sep, env=env)
        baseline = snapshot_baseline(snapshot)
        checks = configuration(snapshot)
        results = []
        for check in checks:
            results.append(run_check(check, snapshot))
            snapshot_unchanged(snapshot, baseline, check)
            if fail_fast and not results[-1]:
                print("Stopping after the first failed check; run validate for all check results.", flush=True)
                break
        unchanged(root, tree, previous_head)
        if not all(results):
            raise Failure("Required validation failed; no commit was made.")
    print("PASS all " + str(len(checks)) + " required checks for staged tree " + tree, flush=True)
    return tree, previous_head


def commit(root, message):
    if not message.strip():
        raise Failure("A meaningful commit message is required.")
    staged = subprocess.run(["git", "-C", str(root), "diff", "--cached", "--quiet"],
                            text=True, capture_output=True)
    if staged.returncode not in (0, 1):
        raise Failure(staged.stderr.strip() or "Cannot inspect staged changes.")
    # A pending merge can record meaningful ancestry without changing the tree.
    if staged.returncode == 0 and not (root / git(root, "rev-parse", "--git-path", "MERGE_HEAD")).is_file():
        raise Failure("Nothing staged to commit; stage intended changes before committing.")
    tree, previous_head = validate(root, fail_fast=True)
    unchanged(root, tree, previous_head)
    result = subprocess.run(["git", "-C", str(root), "commit", "-m", message])
    if result.returncode:
        raise Failure("Git commit failed (including any existing hooks); diagnose and retry without bypassing checks.")
    if git(root, "rev-parse", "HEAD^{tree}") != tree:
        raise Failure("Commit tree differs from the validated tree (possibly a modifying hook). "
                      "The commit EXISTS; inspect it and correct with a new validated commit. Do not rewrite history.")
    print("Committed validated tree: " + git(root, "rev-parse", "HEAD"), flush=True)


def install(path):
    root = repository(path)
    if root != path.resolve():
        raise Failure("Install target must be the repository root.")
    target = root / ".tiny-harness"
    if os.path.lexists(target):
        raise Failure("Refusing to replace existing .tiny-harness; review and merge updates manually.")
    source = Path(__file__).resolve().parent
    # Prepare completely before adding the directory; no existing project files are edited.
    with tempfile.TemporaryDirectory(prefix="tiny-harness-install-") as directory:
        staged = Path(directory) / ".tiny-harness"
        staged.mkdir()
        for name in ("run.py", "CONTRACT.md", "LICENSE"):
            shutil.copyfile(source / name, staged / name)
        (staged / "TASK.md").write_text(TASK)
        (staged / "checks.json").write_text('{"checks": []}\n')
        shutil.copytree(staged, target)
    print("Installed " + str(target), flush=True)
    print("Configure .tiny-harness/checks.json and TASK.md, then stage them deliberately.\n"
          "Load .tiny-harness/CONTRACT.md in the agent, or add a reference to existing instructions.\n"
          "No instructions, hooks, Git settings, or project configuration were replaced.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate", help="run required checks on a fresh copy of the index")
    committing = commands.add_parser("commit", help="validate, then commit using existing Git identity and hooks")
    committing.add_argument("-m", "--message", required=True)
    installing = commands.add_parser("install", help="add the harness to an existing Git repository")
    installing.add_argument("target", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "install":
            install(args.target)
        else:
            root = repository(Path.cwd())
            if args.command == "validate":
                validate(root)
            else:
                commit(root, args.message)
    except (Failure, OSError) as error:
        print("ERROR: " + str(error), file=sys.stderr, flush=True)
        return 1
    except KeyboardInterrupt:
        print("ERROR: interrupted; validation is incomplete. Inspect task and Git state before resuming.", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
