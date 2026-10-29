#!/usr/bin/env python3
"""Print a bounded, read-only navigation brief from TASK.md and Git state."""
import argparse
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys


TASK_PATH = ".tiny-harness/TASK.md"
LIST_CAP = 8
LINE_CHARS = 200
HEADER = (
    "Context brief: navigation aid only. It does not replace .tiny-harness/CONTRACT.md or TASK.md.",
    "Read both in full. They govern scope, acceptance criteria, decisions, and failures.",
)
CAVEAT = (
    "Caveat: a basis commit does not record uncommitted contents seen when notes were written.",
    '"Unchanged" means only that Git shows no difference from that commit, not that a note is correct.',
)
FIELD = re.compile(r"^\s*(Basis|Source|Evidence|Next):\s*(.*?)\s*$")
UNCHECKED = re.compile(r"^\s*[-*]\s+\[ \]\s+(.*?)\s*$")
URL = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")


def git(root, *args):
    """Return (exit code, stdout, stderr); never raise for a nonzero exit."""
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    try:
        result = subprocess.run(["git", "--no-optional-locks", "--literal-pathspecs", *args],
                                cwd=root, env=env, stdin=subprocess.DEVNULL,
                                capture_output=True, text=True, errors="replace")
    except OSError as error:
        return 127, "", str(error)
    return result.returncode, result.stdout, result.stderr


def first_line(text):
    lines = text.strip().splitlines()
    return lines[0] if lines else "no message"


def parse_task(text):
    task = {"sections": [], "unchecked": [], "Basis": [], "Source": [], "Evidence": [], "Next": []}
    for number, line in enumerate(text.splitlines(), 1):
        unchecked, field = UNCHECKED.match(line), FIELD.match(line)
        if line.startswith("## "):
            task["sections"].append((line[3:].strip(), number))
        elif unchecked:
            task["unchecked"].append((unchecked.group(1), number))
        elif field:
            name, value = field.groups()
            task[name].append((value.strip("`").strip(), number))
    return task


def resolve_basis(root, values):
    """Return (commit or None, description of the basis state)."""
    distinct = {value for value, _ in values if value}
    if not distinct:
        return None, "unknown (no basis recorded)"
    if len(distinct) > 1:
        return None, "unknown (multiple different Basis lines)"
    value = distinct.pop()
    if git(root, "rev-parse", "--verify", "--quiet", "HEAD")[0] != 0:
        return None, "unknown (no HEAD)"
    code, out, err = git(root, "rev-parse", "--verify", "--quiet", value + "^{commit}")
    if code == 1:
        return None, "unknown (basis not found: shallow clone, gc, or typo)"
    if code != 0:
        return None, "unknown (git error: " + first_line(err) + ")"
    commit = out.strip()
    code, _, err = git(root, "merge-base", "--is-ancestor", commit, "HEAD")
    if code == 0:
        count = git(root, "rev-list", "--count", commit + "..HEAD")[1].strip() or "unknown"
        return commit, value + " (ancestor of HEAD, " + count + " commits behind)"
    if code == 1:
        return commit, (value + " (basis is not an ancestor of HEAD: diverged or rewritten history;"
                        " results are content differences only)")
    return commit, value + " (ancestry unknown, git error: " + first_line(err) + ")"


def repository_relative(path):
    parts = PurePosixPath(path).parts
    return bool(parts) and not path.startswith(("/", "\\")) and ".." not in parts


def compare(root, basis, path, git=git):
    """Classify a referenced path as changed, unchanged, or unknown relative to basis."""
    if not repository_relative(path):
        return "unknown (not a repository-relative path)"
    layers = (("committed", (basis, "HEAD")), ("staged", ("--cached", "HEAD")), ("unstaged", ()))
    changed, errors = [], []
    for name, revisions in layers:
        code, _, err = git(root, "diff", "--quiet", *revisions, "--", path)
        if code == 1:
            changed.append(name)
        elif code != 0:
            errors.append(name + ": " + first_line(err))
    if changed:
        note = "; git error on " + ", ".join(errors) if errors else ""
        return "changed (" + "/".join(changed) + ")" + note
    if errors:
        return "unknown (git error: " + "; ".join(errors) + ")"
    tracked = False
    for revision in (basis, "HEAD"):
        code, out, err = git(root, "ls-tree", "--name-only", revision, "--", path)
        if code != 0:
            return "unknown (git error: " + first_line(err) + ")"
        tracked = tracked or bool(out.strip())
    code, out, err = git(root, "ls-files", "--others", "--directory", "--", path)
    if code != 0:
        return "unknown (git error: " + first_line(err) + ")"
    if out.strip():
        return "unknown (untracked files; not comparable to basis)"
    if tracked:
        return "unchanged relative to recorded basis"
    if os.path.lexists(root / path):
        return "unknown (untracked; not comparable to basis)"
    return "unknown (absent from basis, HEAD, index, and working tree)"


def evidence(root, item):
    if URL.match(item):
        return "not checked (URL)"
    try:
        status = (root / item).stat()
    except FileNotFoundError:
        return "missing"
    except OSError as error:
        return "unknown (stat error: " + str(error) + ")"
    if os.path.isdir(root / item):
        return "present (directory)"
    return "present, " + str(status.st_size) + " bytes"


def capped(title, items, more):
    """List items under a title, naming where to find any omitted ones."""
    lines = [title + " (" + str(len(items)) + "):"]
    lines += ["  " + item for item in items[:LIST_CAP]]
    if len(items) > LIST_CAP:
        lines.append("  [" + str(len(items) - LIST_CAP) + " more " + more + "]")
    return lines


def git_lines(root):
    code, out, _ = git(root, "symbolic-ref", "--quiet", "--short", "HEAD")
    branch = out.strip() if code == 0 else "detached or unknown"
    code, out, _ = git(root, "log", "-1", "--format=%h %s")
    lines = ["Git: branch " + branch + "; HEAD " + (out.strip() if code == 0 else "none")]
    for title, args in (("Staged", ("diff", "--cached", "--name-status")),
                        ("Unstaged", ("diff", "--name-status")),
                        ("Untracked", ("ls-files", "--others", "--exclude-standard"))):
        code, out, err = git(root, *args)
        if code != 0:
            lines.append(title + ": unknown (git error: " + first_line(err) + ")")
        else:
            items = [line.replace("\t", " ") for line in out.splitlines()]
            lines += capped(title, items, "in git status")
    return lines


def render(root, task):
    lines = git_lines(root)
    lines.append("TASK.md sections:")
    lines += ["  " + title + ": TASK.md:" + str(number) for title, number in task["sections"]]
    unchecked = task["unchecked"]
    omitted = unchecked[LIST_CAP:]
    location = "TASK.md:" + str(omitted[0][1]) if omitted else ""
    lines += capped("Unchecked criteria", [text + " (TASK.md:" + str(number) + ")"
                                           for text, number in unchecked],
                    "unchecked criteria from " + location)
    basis, state = resolve_basis(root, task["Basis"])
    lines.append("Basis: " + state)
    # Without a usable basis, every source inherits the basis's "unknown" reason.
    sources = [path + ": " + (compare(root, basis, path) if basis else state)
               for path, _ in task["Source"]]
    lines += capped("Sources", sources, "sources in TASK.md")
    lines += capped("Evidence", [item + ": " + evidence(root, item) for item, _ in task["Evidence"]],
                    "evidence items in TASK.md")
    lines += ["Next: " + text + " (TASK.md:" + str(number) + ")" for text, number in task["Next"]]
    return lines


def size(lines):
    return sum(len(line.encode("utf-8")) + 1 for line in lines)


def footer(max_lines, max_bytes):
    return ("[brief truncated to fit " + str(max_lines) + " lines and " + str(max_bytes)
            + " bytes. Read TASK.md and git status directly.]")


def minimum(max_lines, max_bytes):
    required = [*HEADER, *CAVEAT, footer(max_lines, max_bytes)]
    return len(required), size(required)


def bound(body, max_lines, max_bytes):
    """Keep the header and caveat, then add body lines in order while they fit."""
    body = [line if len(line) <= LINE_CHARS else line[:LINE_CHARS - 1] + "…" for line in body]
    output = [*HEADER, *CAVEAT]
    if len(output) + len(body) <= max_lines and size(output + body) <= max_bytes:
        return output + body
    notice = footer(max_lines, max_bytes)
    for line in body:
        if len(output) + 2 > max_lines or size(output + [line, notice]) > max_bytes:
            break
        output.append(line)
    return output + [notice]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-lines", type=int, default=60)
    parser.add_argument("--max-bytes", type=int, default=6000)
    args = parser.parse_args()
    lines, octets = minimum(args.max_lines, args.max_bytes)
    if args.max_lines < lines or args.max_bytes < octets:
        parser.error("budget too small: the header, caveat, and truncation notice need "
                     + str(lines) + " lines and " + str(octets) + " bytes")
    code, out, err = git(Path.cwd(), "rev-parse", "--show-toplevel")
    if code != 0:
        print("ERROR: not a Git repository: " + first_line(err), file=sys.stderr)
        return 1
    root = Path(out.strip())
    try:
        text = (root / TASK_PATH).read_text(encoding="utf-8", errors="replace")
    except OSError as error:
        print("ERROR: cannot read " + TASK_PATH + ": " + str(error), file=sys.stderr)
        return 1
    output = bound(render(root, parse_task(text)), args.max_lines, args.max_bytes)
    sys.stdout.buffer.write("".join(line + "\n" for line in output).encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
