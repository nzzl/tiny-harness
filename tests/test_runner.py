"""Behavior tests; each fixture is an isolated disposable Git repository."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]
RUNNER = SOURCE / ".tiny-harness/run.py"


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="harness-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "repo with spaces"
        self.root.mkdir()
        self.env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                        GIT_TERMINAL_PROMPT="0")
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture Author")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "commit.gpgsign", "false")

    def run_command(self, argv):
        return subprocess.run(argv, cwd=self.root, env=self.env, text=True,
                              capture_output=True, timeout=20)

    def git(self, *args):
        result = self.run_command(["git", *args])
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def harness(self, *args):
        return self.run_command([sys.executable, str(RUNNER), *args])

    def install(self):
        result = self.harness("install", str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr)

    def configure(self, code="pass", timeout=5):
        self.install()
        self.write_checks([{"name": "behavior", "argv": [sys.executable, "-c", code],
                            "timeout_seconds": timeout}])
        self.git("add", ".tiny-harness")

    def write_checks(self, checks):
        (self.root / ".tiny-harness/checks.json").write_text(json.dumps({"checks": checks}))

    def assert_failed(self, result, text):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(text, result.stdout + result.stderr)

    def test_missing_and_empty_staged_configuration(self):
        self.assert_failed(self.harness("validate"), "missing or invalid")
        self.install()
        self.assert_failed(self.harness("validate"), "missing or invalid")
        self.git("add", ".tiny-harness")
        self.assert_failed(self.harness("validate"), "at least one required check")

    def test_malformed_and_invalid_configuration(self):
        self.install()
        path = self.root / ".tiny-harness/checks.json"
        cases = ["{", "[]", '{"checks": [], "optional": true}',
                 '{"checks": [null]}',
                 json.dumps({"checks": [{"name": "bad", "argv": [], "timeout_seconds": 1}]}),
                 json.dumps({"checks": [{"name": "bad", "argv": ["echo"], "timeout_seconds": False}]}),
                 json.dumps({"checks": [{"name": "bad", "argv": ["echo"], "timeout_seconds": float("inf")}]}),
                 json.dumps({"checks": [{"name": "same", "argv": ["echo"], "timeout_seconds": 1}] * 2})]
        for content in cases:
            with self.subTest(content=content):
                path.write_text(content)
                self.git("add", ".tiny-harness")
                self.assert_failed(self.harness("validate"), "ERROR:")

    def test_failed_check_blocks_commit_and_runs_other_checks(self):
        self.configure()
        self.write_checks([
            {"name": "fails", "argv": [sys.executable, "-c", "raise SystemExit(7)"], "timeout_seconds": 5},
            {"name": "still runs", "argv": [sys.executable, "-c", "print('second-check-evidence')"], "timeout_seconds": 5}])
        self.git("add", ".tiny-harness/checks.json")
        result = self.harness("commit", "-m", "Must fail")
        self.assert_failed(result, "exit 7")
        self.assertIn("second-check-evidence", result.stdout)
        self.assertNotEqual(self.run_command(["git", "rev-parse", "--verify", "HEAD"]).returncode, 0)

    def test_missing_executable_and_timeout(self):
        self.configure()
        for argv, timeout, evidence in [(["tiny-harness-nonexistent-command"], 5, "FAIL behavior"),
                                        ([sys.executable, "-c", "import time; time.sleep(10)"], 0.05, "timed out")]:
            with self.subTest(argv=argv):
                self.write_checks([{"name": "behavior", "argv": argv, "timeout_seconds": timeout}])
                self.git("add", ".tiny-harness/checks.json")
                self.assert_failed(self.harness("commit", "-m", "Must fail"), evidence)

    def test_unstaged_fix_cannot_mask_staged_failure(self):
        self.configure("from pathlib import Path; assert Path('value').read_text() == 'good'")
        value = self.root / "value"
        value.write_text("bad")
        self.git("add", "value")
        value.write_text("good")
        self.assert_failed(self.harness("validate"), "Required validation failed")
        self.assertEqual(value.read_text(), "good")
        self.assertEqual(self.git("show", ":value"), "bad")

    def test_untracked_dependency_is_not_in_snapshot(self):
        self.configure("from pathlib import Path; assert Path('untracked').exists()")
        (self.root / "untracked").write_text("local-only")
        self.assert_failed(self.harness("validate"), "Required validation failed")

    def test_validation_is_fresh_and_preserves_unrelated_changes(self):
        self.configure("from pathlib import Path; p = Path('generated'); assert not p.exists(); p.write_text('built')")
        for _ in range(2):
            result = self.harness("validate")
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / "generated").exists())
        (self.root / "unrelated").write_text("original")
        self.git("add", "unrelated")
        result = self.harness("commit", "-m", "Establish baseline")
        self.assertEqual(result.returncode, 0, result.stderr)
        old_head = self.git("rev-parse", "HEAD")
        (self.root / "unrelated").write_text("user edit")
        (self.root / "new").write_text("owned change")
        (self.root / "untracked").write_text("user notes")
        self.git("add", "new")
        result = self.harness("commit", "-m", "Add owned change")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("rev-parse", "HEAD^"), old_head)
        self.assertEqual(self.git("show", "HEAD:unrelated"), "original")
        self.assertEqual((self.root / "unrelated").read_text(), "user edit")
        self.assertEqual((self.root / "untracked").read_text(), "user notes")
        self.assertEqual(self.git("log", "-1", "--format=%an <%ae>"), "Fixture Author <fixture@example.invalid>")

    def test_install_preserves_existing_project_and_refuses_reinstall(self):
        files = {"AGENTS.md": "existing instructions", "CLAUDE.md": "existing agent rules",
                 "project.json": '{"existing":true}', "hooks/pre-commit": "#!/bin/sh\nexit 0\n"}
        for name, content in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        self.git("config", "core.hooksPath", "hooks")
        self.git("add", *files)
        self.git("commit", "-qm", "Existing project")
        previous = self.git("rev-parse", "HEAD")
        settings = (self.root / ".git/config").read_bytes()
        self.install()
        for name, content in files.items():
            self.assertEqual((self.root / name).read_text(), content)
        self.assertEqual((self.root / ".git/config").read_bytes(), settings)
        self.assertEqual(self.git("rev-parse", "HEAD"), previous)
        self.assertIn("Replace with", (self.root / ".tiny-harness/TASK.md").read_text())
        self.assertTrue((self.root / ".tiny-harness/LICENSE").is_file())
        self.assert_failed(self.harness("install", str(self.root)), "Refusing to replace")

    def test_install_rejects_subdirectory_and_symlink_destination(self):
        child = self.root / "child"
        child.mkdir()
        self.assert_failed(self.harness("install", str(child)), "repository root")
        (self.root / ".tiny-harness").symlink_to(self.root / "missing")
        self.assert_failed(self.harness("install", str(self.root)), "Refusing to replace")

    def test_existing_hook_runs_and_can_block_commit(self):
        self.configure()
        hooks = self.root / "custom-hooks"
        hooks.mkdir()
        hook = hooks / "pre-commit"
        hook.write_text("#!/bin/sh\necho existing-hook-evidence >&2\nexit 1\n")
        hook.chmod(0o755)
        self.git("config", "core.hooksPath", "custom-hooks")
        result = self.harness("commit", "-m", "Hook should block")
        self.assert_failed(result, "existing-hook-evidence")
        self.assertIn("Git commit failed", result.stderr)

    def test_modifying_hook_is_reported_without_rewriting_commit(self):
        self.configure()
        hook = self.root / ".git/hooks/pre-commit"
        hook.write_text("#!/bin/sh\nprintf hook-change > hook-file\ngit add hook-file\n")
        hook.chmod(0o755)
        result = self.harness("commit", "-m", "Hook changes tree")
        self.assert_failed(result, "The commit EXISTS")
        self.assertEqual(self.git("show", "HEAD:hook-file"), "hook-change")

    def test_index_change_during_validation_blocks_commit(self):
        code = "import subprocess; subprocess.run(['git', '-C', " + repr(str(self.root)) + ", 'add', 'later'], check=True)"
        self.configure(code)
        (self.root / "later").write_text("concurrent edit")
        self.assert_failed(self.harness("commit", "-m", "Must fail"), "Index or HEAD changed")

    def test_submodule_fails_instead_of_omitting_required_content(self):
        self.configure()
        self.git("commit", "-qm", "Fixture seed")
        oid = self.git("rev-parse", "HEAD")
        self.git("update-index", "--add", "--cacheinfo", "160000," + oid + ",nested")
        self.assert_failed(self.harness("validate"), "Submodules are unsupported")

    def test_unmerged_index_fails(self):
        self.configure()
        (self.root / "conflict").write_text("base")
        self.git("add", "conflict")
        self.git("commit", "-qm", "Fixture base")
        branch = self.git("branch", "--show-current")
        self.git("checkout", "-qb", "other")
        (self.root / "conflict").write_text("other")
        self.git("commit", "-qam", "Other")
        self.git("checkout", branch)
        (self.root / "conflict").write_text("main")
        self.git("commit", "-qam", "Main")
        self.assertNotEqual(self.run_command(["git", "merge", "other"]).returncode, 0)
        self.assert_failed(self.harness("validate"), "ERROR:")

    def test_installed_copy_adoption_failure_recovery_and_commit(self):
        self.install()
        installed = self.root / ".tiny-harness/run.py"
        def run(*args):
            return self.run_command([sys.executable, str(installed), *args])
        self.git("add", ".tiny-harness")
        self.assert_failed(run("commit", "-m", "Not configured"), "at least one required check")
        (self.root / "check.py").write_text("from pathlib import Path\nassert Path('answer').read_text() == '42'\n")
        (self.root / "answer").write_text("wrong")
        self.write_checks([{"name": "sample behavior", "argv": [sys.executable, "check.py"], "timeout_seconds": 5}])
        self.git("add", ".tiny-harness/checks.json", "check.py", "answer")
        self.assert_failed(run("commit", "-m", "Still broken"), "Required validation failed")
        (self.root / "answer").write_text("42")
        self.git("add", "answer")
        result = run("commit", "-m", "Make the sample meet its acceptance criterion")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("rev-list", "--count", "HEAD"), "1")
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_install_outside_repository_is_visible_failure(self):
        outside = Path(self.temporary.name) / "not-a-repo"
        outside.mkdir()
        self.assert_failed(self.harness("install", str(outside)), "not a git repository")

    def test_empty_message_does_not_create_commit(self):
        self.configure()
        self.assert_failed(self.harness("commit", "-m", "   "), "meaningful commit message")

    def test_snapshot_changes_block_commit_before_later_checks(self):
        self.configure()
        (self.root / "value").write_text("bad")
        (self.root / "link").symlink_to("value")
        (self.root / "directory").mkdir()
        (self.root / "directory/nested").write_text("original")
        self.git("add", "value", "link", "directory/nested")
        mutations = [
            "Path('value').write_text('good')",
            "Path('value').unlink()",
            "Path('value').chmod(0o755)",
            "Path('value').unlink(); Path('value').symlink_to('link')",
            "Path('link').unlink(); Path('link').symlink_to('directory/nested')",
            "Path('link').unlink(); Path('link').write_text('replacement')",
            "Path('directory').rename('moved'); Path('directory').symlink_to('moved', target_is_directory=True)",
            "Path('value').write_text('good'); raise SystemExit(7)",
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.write_checks([
                    {"name": "mutating check", "argv": [sys.executable, "-c", "from pathlib import Path; " + mutation], "timeout_seconds": 5},
                    {"name": "later check", "argv": [sys.executable, "-c", "print('later-check-ran')"], "timeout_seconds": 5},
                ])
                self.git("add", ".tiny-harness/checks.json")
                result = self.harness("commit", "-m", "Must reject a modified snapshot")
                self.assert_failed(result, "modified staged snapshot path")
                self.assertNotIn("later-check-ran", result.stdout)
                self.assertNotEqual(self.run_command(["git", "rev-parse", "--verify", "HEAD"]).returncode, 0)
                self.assertEqual(self.git("show", ":value"), "bad")
                self.assertEqual((self.root / "value").read_text(), "bad")
                self.assertEqual(os.readlink(self.root / "link"), "value")
                self.assertFalse((self.root / "directory").is_symlink())

    def test_duplicate_json_keys_block_commit_before_checks(self):
        self.install()
        failing = json.dumps({"name": "required", "argv": [sys.executable, "-c", "raise SystemExit(7)"], "timeout_seconds": 5})
        passing = json.dumps({"name": "passing", "argv": [sys.executable, "-c", "pass"], "timeout_seconds": 5})
        contents = ['{"checks": [' + failing + '], "checks": [' + passing + ']}']
        for field, value in (("name", '"replacement"'), ("argv", '["missing-tool"]'), ("timeout_seconds", '10')):
            contents.append('{"checks": [' + passing[:-1] + ', ' + json.dumps(field) + ': ' + value + '}]}')
        for content in contents:
            with self.subTest(content=content):
                (self.root / ".tiny-harness/checks.json").write_text(content)
                self.git("add", ".tiny-harness")
                result = self.harness("commit", "-m", "Must reject ambiguous configuration")
                self.assert_failed(result, "Duplicate configuration key")
                self.assertNotIn("RUN ", result.stdout)
                self.assertNotEqual(self.run_command(["git", "rev-parse", "--verify", "HEAD"]).returncode, 0)

    def test_required_suite_rejects_empty_discovery(self):
        self.install()
        (self.root / "tests").mkdir()
        shutil.copyfile(SOURCE / "tests/run.py", self.root / "tests/run.py")
        shutil.copyfile(SOURCE / ".tiny-harness/checks.json", self.root / ".tiny-harness/checks.json")
        # The original audit's accidental rename keeps a test file undiscoverable.
        (self.root / "tests/runner_tests.py").write_text("import unittest\nclass Example(unittest.TestCase):\n    def test_example(self):\n        pass\n")
        self.git("add", ".tiny-harness", "tests")
        result = self.harness("commit", "-m", "Must reject zero discovered tests")
        self.assert_failed(result, "no tests discovered")
        self.assertNotEqual(self.run_command(["git", "rev-parse", "--verify", "HEAD"]).returncode, 0)

    def test_suite_entrypoint_runs_discovered_tests_and_propagates_failures(self):
        (self.root / "tests").mkdir()
        shutil.copyfile(SOURCE / "tests/run.py", self.root / "tests/run.py")
        test = self.root / "tests/test_example.py"
        test.write_text("import unittest\nclass Example(unittest.TestCase):\n    def test_example(self):\n        self.fail('behavior-failure-evidence')\n")
        result = self.run_command([sys.executable, "-B", "tests/run.py"])
        self.assert_failed(result, "behavior-failure-evidence")
        test.write_text("import unittest\nclass Example(unittest.TestCase):\n    def test_example(self):\n        pass\n")
        result = self.run_command([sys.executable, "-B", "tests/run.py"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Ran 1 test", result.stderr)


if __name__ == "__main__":
    unittest.main()
