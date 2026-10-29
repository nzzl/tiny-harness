"""Behavior tests for the optional context-brief pilot in disposable repositories."""
import importlib.util
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]
EXAMPLE = SOURCE / "examples/context-brief"
BRIEF = EXAMPLE / "brief.py"
SPEC = importlib.util.spec_from_file_location("context_brief", BRIEF)
brief = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(brief)


class ContextBriefTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="brief-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "repo with spaces"
        self.root.mkdir()
        self.env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                        GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0")
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture Author")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        (self.root / ".tiny-harness").mkdir()

    def git(self, *args):
        result = subprocess.run(["git", *args], cwd=self.root, env=self.env, text=True,
                                capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def write(self, path, text):
        (self.root / path).parent.mkdir(parents=True, exist_ok=True)
        (self.root / path).write_text(text, encoding="utf-8")

    def commit(self, path, text, message="Change"):
        self.write(path, text)
        self.git("add", path)
        self.git("commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    def task(self, *lines):
        self.write(".tiny-harness/TASK.md", "\n".join(["# Task", "## Checkpoint", *lines]) + "\n")

    def run_brief(self, *args, expect=0):
        result = subprocess.run([sys.executable, str(BRIEF), *args], cwd=self.root, env=self.env,
                                capture_output=True, timeout=20)
        self.assertEqual(result.returncode, expect, result.stderr.decode())
        return result

    def output(self, *args):
        return self.run_brief(*args).stdout.decode("utf-8")

    def source_result(self, output, path):
        match = re.search(r"^  " + re.escape(path) + r": (.*)$", output, re.MULTILINE)
        self.assertIsNotNone(match, output)
        return match.group(1)

    def test_each_change_layer_is_reported_separately(self):
        names = ("committed.txt", "staged.txt", "unstaged.txt", "partial.txt", "same.txt")
        for name in names:
            self.write(name, "original\n")
        self.git("add", ".")
        self.git("commit", "-qm", "Initial")
        basis = self.git("rev-parse", "HEAD")
        self.commit("committed.txt", "committed\n")
        self.write("staged.txt", "staged\n")
        self.write("partial.txt", "staged part\n")
        self.git("add", "staged.txt", "partial.txt")
        self.write("unstaged.txt", "unstaged\n")
        self.write("partial.txt", "unstaged part\n")
        self.task("Basis: `" + basis + "`", *("Source: " + name for name in names))
        output = self.output()
        self.assertEqual(self.source_result(output, "committed.txt"), "changed (committed)")
        self.assertEqual(self.source_result(output, "staged.txt"), "changed (staged)")
        self.assertEqual(self.source_result(output, "unstaged.txt"), "changed (unstaged)")
        self.assertEqual(self.source_result(output, "partial.txt"), "changed (staged/unstaged)")
        self.assertEqual(self.source_result(output, "same.txt"), "unchanged relative to recorded basis")
        self.assertIn("1 commits behind", output)
        self.assertNotIn("verified", output.lower())

    def layered_changes(self):
        """Commit a basis, then change one file in each comparison layer."""
        for name in ("committed.txt", "staged.txt", "unstaged.txt", "same.txt"):
            self.write(name, "original\n")
        self.git("add", ".")
        self.git("commit", "-qm", "Initial")
        basis = self.git("rev-parse", "HEAD")
        self.commit("committed.txt", "committed\n")
        self.write("staged.txt", "staged\n")
        self.git("add", "staged.txt")
        self.write("unstaged.txt", "unstaged\n")
        self.task("Basis: " + basis, *("Source: " + name for name in
                                       ("committed.txt", "staged.txt", "unstaged.txt", "same.txt")))

    def assert_layers_reported(self, output):
        self.assertEqual(self.source_result(output, "committed.txt"), "changed (committed)")
        self.assertEqual(self.source_result(output, "staged.txt"), "changed (staged)")
        self.assertEqual(self.source_result(output, "unstaged.txt"), "changed (unstaged)")
        self.assertEqual(self.source_result(output, "same.txt"), "unchanged relative to recorded basis")

    def helper(self, name, body):
        """Write an executable outside the repository that leaves a marker when run."""
        marker = Path(self.temporary.name) / (name + "-ran")
        script = Path(self.temporary.name) / name
        script.write_text("#!/bin/sh\ntouch " + "'" + str(marker) + "'\n" + body)
        script.chmod(0o755)
        return script, marker

    def test_external_diff_helpers_are_never_invoked(self):
        self.layered_changes()
        # A trusted helper that reports "no difference" would otherwise hide every change.
        script, marker = self.helper("external-diff", "exit 0\n")
        self.git("config", "diff.external", str(script))
        self.git("config", "diff.trustExitCode", "true")
        self.git("config", "diff.helper.command", str(script))
        self.git("config", "diff.helper.trustExitCode", "true")
        self.write(".git/info/attributes", "*.txt diff=helper\n")
        self.assert_layers_reported(self.output())
        self.assertFalse(marker.exists(), "brief invoked an external diff helper")

    def test_text_conversion_is_never_invoked(self):
        self.layered_changes()
        # Identical converted text for every file would otherwise hide every change.
        script, marker = self.helper("textconv", "echo same\n")
        self.git("config", "diff.convert.textconv", str(script))
        self.write(".git/info/attributes", "*.txt diff=convert\n")
        self.assert_layers_reported(self.output())
        self.assertFalse(marker.exists(), "brief invoked a text conversion helper")

    def test_fsmonitor_hook_is_never_invoked(self):
        basis = self.commit("file.txt", "original\n")
        # Hook protocol 2: print a token and a NUL, then changed paths; none means "nothing changed".
        script, marker = self.helper("fsmonitor", "printf 'token-fixed\\0'\n")
        self.git("config", "core.fsmonitor", str(script))
        self.git("config", "core.fsmonitorHookVersion", "2")
        self.git("update-index", "--fsmonitor")
        priming = {key: value for key, value in self.env.items() if key != "GIT_OPTIONAL_LOCKS"}
        for _ in range(2):
            subprocess.run(["git", "status", "--porcelain"], cwd=self.root, env=priming,
                           check=True, capture_output=True, timeout=20)
        self.write("file.txt", "modified without staging\n")
        hidden = subprocess.run(["git", "diff", "--quiet", "--", "file.txt"], cwd=self.root,
                                env=self.env, capture_output=True, timeout=20)
        self.assertEqual(hidden.returncode, 0, "fixture setup failed: fsmonitor did not hide the change")
        self.assertTrue(marker.exists(), "fixture setup failed: fsmonitor hook did not run")
        marker.unlink()
        self.task("Basis: " + basis, "Source: file.txt")
        config, index = self.root / ".git/config", self.root / ".git/index"
        before = (config.read_bytes(), index.read_bytes(), index.stat().st_mtime_ns)
        output = self.output()
        self.assertFalse(marker.exists(), "brief invoked the fsmonitor hook")
        self.assertEqual(self.source_result(output, "file.txt"), "changed (unstaged)")
        self.assertIn("Unstaged (1):\n  M file.txt\n", output)
        self.assertEqual((config.read_bytes(), index.read_bytes(), index.stat().st_mtime_ns), before)

    def test_fixed_basis_still_reports_later_committed_changes(self):
        basis = self.commit("file.txt", "checkpoint\n")
        self.commit("file.txt", "changed after checkpoint\n")
        self.task("Basis: " + basis, "Source: file.txt")
        output = self.output()
        self.assertEqual(self.source_result(output, "file.txt"), "changed (committed)")
        self.assertIn("1 commits behind", output)

    def test_moving_references_and_expressions_are_rejected(self):
        first = self.commit("file.txt", "one\n")
        self.commit("file.txt", "two\n")
        self.git("branch", "feature")
        self.git("tag", "v1")
        branch = self.git("symbolic-ref", "--short", "HEAD")
        for value in ("HEAD", branch, "feature", "v1", "@", "HEAD~1", first[:7] + "^{commit}",
                      first + "~0", "refs/heads/feature"):
            with self.subTest(value=value):
                self.task("Basis: " + value, "Source: file.txt")
                output = self.output()
                expected = "unknown (Basis must be a fixed commit hash, not a reference or expression)"
                self.assertIn("Basis: " + expected, output)
                self.assertEqual(self.source_result(output, "file.txt"), expected)

    def test_hex_named_reference_is_not_treated_as_a_commit_hash(self):
        self.commit("file.txt", "one\n")
        # A branch whose name looks like a hash is still a moving reference.
        self.git("branch", "deadbeef")
        self.task("Basis: deadbeef", "Source: file.txt")
        output = self.output()
        self.assertIn("Basis: unknown (deadbeef resolves through a reference, not as a commit hash)",
                      output)

    def test_full_and_abbreviated_hashes_resolve_and_others_are_unavailable(self):
        basis = self.commit("file.txt", "one\n")
        self.commit("file.txt", "two\n")
        blob = self.git("rev-parse", "HEAD:file.txt")
        for value in (basis, basis[:7], basis[:12].upper()):
            with self.subTest(value=value):
                self.task("Basis: " + value, "Source: file.txt")
                output = self.output()
                self.assertIn("Basis: " + value + " (ancestor of HEAD, 1 commits behind)", output)
                self.assertEqual(self.source_result(output, "file.txt"), "changed (committed)")
        for value in ("0123456789abcdef0123456789abcdef01234567", blob):
            with self.subTest(value=value):
                self.task("Basis: " + value, "Source: file.txt")
                output = self.output()
                self.assertIn("Basis: unknown (basis not found", output)
                self.assertTrue(self.source_result(output, "file.txt").startswith(
                    "unknown (basis not found"), output)

    def test_deleted_and_added_files_count_as_changed(self):
        basis = self.commit("old.txt", "old\n")
        self.git("rm", "-q", "old.txt")
        self.write("new.txt", "new\n")
        self.git("add", "new.txt")
        self.task("Basis: " + basis, "Source: old.txt", "Source: new.txt")
        output = self.output()
        # git rm removes the file from index and working tree alike, so they still match.
        self.assertEqual(self.source_result(output, "old.txt"), "changed (staged)")
        self.assertEqual(self.source_result(output, "new.txt"), "changed (staged)")

    def test_unusable_bases_make_every_source_unknown(self):
        def check(basis_lines, expected):
            self.task(*basis_lines, "Source: file.txt")
            output = self.output()
            self.assertIn("Basis: " + expected, output)
            self.assertTrue(self.source_result(output, "file.txt").startswith(expected), output)
        self.write("file.txt", "x\n")
        check(["Basis: abc1234"], "unknown (no HEAD)")
        first = self.commit("file.txt", "x\n")
        second = self.commit("file.txt", "y\n")
        check([], "unknown (no basis recorded)")
        check(["Basis: 0123456789abcdef0123456789abcdef01234567"], "unknown (basis not found")
        check(["Basis: " + first, "Basis: " + second], "unknown (multiple different Basis lines)")

    def test_diverged_basis_is_labeled_as_content_comparison(self):
        self.commit("file.txt", "base\n")
        default = self.git("symbolic-ref", "--short", "HEAD")
        self.git("switch", "-qc", "side")
        side = self.commit("file.txt", "side\n")
        self.git("switch", "-q", default)
        self.commit("other.txt", "main\n")
        self.task("Basis: " + side, "Source: file.txt", "Source: other.txt")
        output = self.output()
        self.assertIn("not an ancestor of HEAD", output)
        self.assertEqual(self.source_result(output, "file.txt"), "changed (committed)")
        self.assertEqual(self.source_result(output, "other.txt"), "changed (committed)")

    def test_untracked_absent_and_outside_paths_are_unknown(self):
        basis = self.commit("dir/tracked.txt", "tracked\n")
        self.write("loose.txt", "untracked\n")
        self.write("dir/extra.txt", "untracked in tracked directory\n")
        self.write(".gitignore", "ignored.log\n")
        self.write("ignored.log", "ignored\n")
        sources = ("loose.txt", "dir", "ignored.log", "nowhere.txt", "../outside.txt", "/etc/hosts")
        self.task("Basis: " + basis, *("Source: " + path for path in sources))
        output = self.output()
        for path in ("loose.txt", "ignored.log"):
            self.assertEqual(self.source_result(output, path),
                             "unknown (untracked files; not comparable to basis)")
        self.assertEqual(self.source_result(output, "dir"),
                         "unknown (untracked files; not comparable to basis)")
        self.assertEqual(self.source_result(output, "nowhere.txt"),
                         "unknown (absent from basis, HEAD, index, and working tree)")
        for path in ("../outside.txt", "/etc/hosts"):
            self.assertEqual(self.source_result(output, path), "unknown (not a repository-relative path)")

    def test_git_errors_are_not_reported_as_differences(self):
        def failing(_root, *args):
            return 128, "", "fatal: simulated failure\nmore detail"
        self.assertEqual(brief.compare(self.root, "abc", "file.txt", git=failing),
                         "unknown (git error: committed: fatal: simulated failure; "
                         "staged: fatal: simulated failure; unstaged: fatal: simulated failure)")

        def partly_failing(_root, *args):
            return (1, "", "") if "--cached" in args else (128, "", "fatal: broken")
        self.assertEqual(brief.compare(self.root, "abc", "file.txt", git=partly_failing),
                         "changed (staged); git error on committed: fatal: broken, unstaged: fatal: broken")

    def test_output_fits_limits_with_multibyte_text(self):
        criteria = ["- [ ] Ünïcode criterion " + str(number) + " " + "ü€" * 150 for number in range(300)]
        basis = self.commit("file.txt", "x\n")
        self.task("Basis: " + basis, *criteria, "Next: " + "→" * 500)
        for max_lines, max_bytes in ((60, 6000), (12, 1500), (7, 700), (200, 100000)):
            with self.subTest(max_lines=max_lines, max_bytes=max_bytes):
                raw = self.run_brief("--max-lines", str(max_lines), "--max-bytes", str(max_bytes)).stdout
                lines = raw.decode("utf-8").splitlines()
                self.assertLessEqual(len(raw), max_bytes)
                self.assertLessEqual(len(lines), max_lines)
                self.assertTrue(all(len(line) <= brief.LINE_CHARS for line in lines))
                self.assertEqual(lines[:4], [*brief.HEADER, *brief.CAVEAT])
        lines = self.output("--max-lines", "12", "--max-bytes", "1500").splitlines()
        self.assertEqual(lines[-1], "[brief truncated to fit 12 lines and 1500 bytes. "
                                    "Read TASK.md and git status directly.]")
        full = self.output("--max-lines", "200", "--max-bytes", "100000")
        self.assertNotIn("[brief truncated", full)
        self.assertIn("Unchecked criteria (300):", full)
        # Criteria start at TASK.md line 4, so the ninth (first omitted) is on line 12.
        self.assertIn("[292 more unchecked criteria from TASK.md:12]", full)

    def test_budget_too_small_is_rejected(self):
        self.task("Basis: " + self.commit("file.txt", "x\n"))
        lines, octets = brief.minimum(4, 500)
        self.assertEqual(lines, 5)
        self.run_brief("--max-lines", "4", expect=2)
        self.run_brief("--max-bytes", str(octets - 1), expect=2)
        raw = self.run_brief("--max-lines", "5", "--max-bytes", str(brief.minimum(5, 400)[1])).stdout
        self.assertLessEqual(len(raw.decode("utf-8").splitlines()), 5)

    def test_evidence_uses_stat_without_reading(self):
        self.commit("file.txt", "x\n")
        log = self.root / ".git/tiny-harness/logs/validate-1"
        log.parent.mkdir(parents=True)
        with log.open("wb") as stream:
            stream.truncate(2**30)
        log.chmod(0)
        self.addCleanup(log.chmod, 0o600)
        self.task("Evidence: .git/tiny-harness/logs/validate-1", "Evidence: missing.log",
                  "Evidence: https://ci.example.invalid/run/1")
        output = self.output()
        self.assertIn(".git/tiny-harness/logs/validate-1: present, 1073741824 bytes", output)
        self.assertIn("missing.log: missing", output)
        self.assertIn("https://ci.example.invalid/run/1: not checked (URL)", output)

    def test_brief_does_not_change_repository_state(self):
        basis = self.commit("file.txt", "x\n")
        self.write("file.txt", "dirty\n")
        self.write("untracked.txt", "new\n")
        self.task("Basis: " + basis, "Source: file.txt", "Source: untracked.txt")
        index = self.root / ".git/index"
        os.utime(index, (1, 1))  # An index refresh would replace this old timestamp.

        def state():
            return (index.read_bytes(), index.stat().st_mtime_ns,
                    sorted(str(path) for path in self.root.rglob("*")))
        before = state()
        self.output()
        self.assertEqual(state(), before)
        status = self.git("status", "--porcelain")
        self.output()
        self.assertEqual(self.git("status", "--porcelain"), status)

    def test_outside_repository_and_unreadable_task_fail_visibly(self):
        outside = Path(self.temporary.name) / "not-a-repo"
        outside.mkdir()
        result = subprocess.run([sys.executable, str(BRIEF)], cwd=outside, env=self.env,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 1)
        self.assertIn("not a Git repository", result.stderr)
        self.assertIn("cannot read", self.run_brief(expect=1).stderr.decode())

    def test_example_checkpoint_parses_into_documented_fields(self):
        task = brief.parse_task((EXAMPLE / "TASK.example.md").read_text(encoding="utf-8"))
        self.assertEqual([value for value, _ in task["Basis"]], ["4e0d7aa"])
        self.assertEqual([value for value, _ in task["Source"]],
                         ["src/client.py", "tests/test_client.py", "docs/api.md"])
        self.assertEqual(len(task["Evidence"]), 2)
        self.assertEqual(len(task["unchecked"]), 2)
        self.assertEqual([title for title, _ in task["sections"]],
                         ["Outcome and scope", "Acceptance criteria", "Checkpoint"])
        self.assertTrue(task["Next"][0][0].startswith("fix the off-by-one"))


class LogRecipeTests(unittest.TestCase):
    """Run the documented shell recipe exactly as the README shows it."""

    shell_argv = ["sh", "-c"]

    def setUp(self):
        text = (EXAMPLE / "README.md").read_text(encoding="utf-8")
        blocks = [block for block in re.findall(r"```sh\n(.*?)```", text, re.DOTALL)
                  if "tiny-harness/logs" in block]
        self.assertEqual(len(blocks), 1)
        self.recipe = blocks[0]
        self.temporary = tempfile.TemporaryDirectory(prefix="recipe-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "repo"
        self.root.mkdir()
        self.env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        subprocess.run(["git", "init", "-q"], cwd=self.root, env=self.env, check=True)
        # A stand-in runner with a distinctive status shows the exact value survives.
        (self.root / ".tiny-harness").mkdir()
        (self.root / ".tiny-harness/run.py").write_text(
            "import sys\nprint('RUN fixture')\nprint('noise\\n' * 50, end='')\n"
            "print('FAIL fixture (exit 7)')\nsys.exit(7)\n")

    def shell(self, script, cwd=None):
        return subprocess.run(self.shell_argv + [script], cwd=cwd or self.root, env=self.env,
                              capture_output=True, text=True, timeout=20)

    def logs(self):
        return sorted((self.root / ".git/tiny-harness/logs").iterdir())

    def test_status_is_returned_and_logs_are_never_overwritten(self):
        first = self.shell(self.recipe)
        self.assertEqual(first.returncode, 7, first.stderr)
        self.assertIn("validate exit 7; log:", first.stdout)
        self.assertIn("FAIL fixture (exit 7)", first.stdout)
        self.assertNotIn("noise", first.stdout)
        [log] = self.logs()
        content = log.read_bytes()
        self.assertIn(b"noise", content)
        second = self.shell(self.recipe)
        self.assertEqual(second.returncode, 7)
        self.assertEqual(len(self.logs()), 2)
        self.assertEqual(log.read_bytes(), content)

    def test_caller_shell_continues_and_keeps_its_options(self):
        # The recipe's `set +e` must stay inside its subshell; every caller option survives.
        result = self.shell("set -u\ncaller_options=$-\n" + self.recipe + "\necho \"after $?\"\n"
                            "[ \"$caller_options\" = \"$-\" ] && case $- in *u*) echo kept;; esac\n")
        self.assertIn("after 7", result.stdout)
        self.assertIn("kept", result.stdout)

    def test_setup_failure_is_reported_without_running_validation(self):
        outside = Path(self.temporary.name) / "not-a-repo"
        outside.mkdir()
        (outside / ".tiny-harness").mkdir()
        marker = outside / "ran"
        (outside / ".tiny-harness/run.py").write_text("open(" + repr(str(marker)) + ", 'w').close()\n")
        result = self.shell(self.recipe, cwd=outside)
        self.assertEqual(result.returncode, 125)
        self.assertIn("Log setup failed. Validation did not run.", result.stderr)
        self.assertFalse(marker.exists())


class ZshLogRecipeTests(LogRecipeTests):
    """Repeat the recipe tests in zsh, where `status` is a read-only variable."""

    # -f skips startup files, so the caller's zsh configuration cannot affect the result.
    shell_argv = ["zsh", "-f", "-c"]

    def setUp(self):
        if shutil.which("zsh") is None:
            self.skipTest("zsh is not installed; zsh compatibility of the log recipe is NOT verified")
        super().setUp()


if __name__ == "__main__":
    unittest.main()
