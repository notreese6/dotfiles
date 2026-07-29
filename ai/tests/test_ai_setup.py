import json
import os
import subprocess
import unittest
from base import SandboxedTestCase
import airules

UNIVERSAL = "# Universal Rules\n\nAlways be concise.\n"


class TestAiSetup(SandboxedTestCase):
    """
    Covers the ai-setup CLI: prompts, config keys, the TCC guard, and the
    ai-rules run it finishes with.
    """

    def setUp(self):
        """
        Stand up a sandboxed ai/ directory for setup to read.

        Args:
            None

        Returns:
            None

        Raises:
            OSError: the fixture files cannot be written.
        """

        super().setUp()

        self.fake_ai = self.home / "aifix"
        (self.fake_ai / "local_rules").mkdir(parents=True)
        (self.fake_ai / "AGENTS.md").write_text(UNIVERSAL, encoding="utf-8")
        (self.fake_ai / "local_rules" / "10-first.md").write_text("LOCAL RULE ONE\n", encoding="utf-8")

        # The real ai/bin holds both scripts; setup shells out to its sibling
        (self.fake_ai / "bin").mkdir()
        for name in ("ai-rules", "ai-setup"):
            (self.fake_ai / "bin" / name).symlink_to(self.repo / "ai" / "bin" / name)

    def run_setup(self, *args, **overrides):
        """
        Run ai-setup in a subprocess against the sandbox.

        Args:
            *args (str): command-line arguments passed after the script name.
            **overrides (str): environment variables to set or replace. A value
                of None removes the variable instead.

        Returns:
            subprocess.CompletedProcess: the finished run, with `returncode`,
            `stdout`, and `stderr` captured as text. A non-zero exit is
            returned, not raised.

        Raises:
            OSError: the script is missing or is not executable.
        """

        env = dict(os.environ)
        env["AI_DIR"]                     = str(self.fake_ai)
        env["AI_SETUP_NONINTERACTIVE"]    = "true"
        env["AI_SETUP_LOCAL_RULES_DIR"]   = str(self.fake_ai / "local_rules")
        env.setdefault("AI_SETUP_AGENTS", "claude")

        for key, value in overrides.items():
            if value is None:
                env.pop(key, None)
            else:
                env[key] = value

        return subprocess.run(
            [str(self.repo / "ai" / "bin" / "ai-setup"), *args],
            capture_output=True, text=True, env=env,
        )

    def claude_rules(self):
        """
        Read what Claude Code would see after a setup run.

        Args:
            None

        Returns:
            str: the contents reached through the agent's rules path, following
            the symlink apply leaves there.

        Raises:
            OSError: the path does not exist or cannot be read.
        """

        return (self.home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")

    def test_writes_config_and_assembles(self):
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stderr)

        self.assertEqual(airules.config_get("agents"), ["claude"])
        self.assertIs(airules.config_get("notes_enabled"), False)
        self.assertIn("LOCAL RULE ONE", self.claude_rules())

    def test_leaves_the_agent_path_a_link_to_the_assembled_file(self):
        self.assertEqual(self.run_setup().returncode, 0)

        claude_md = self.home / ".claude" / "CLAUDE.md"
        self.assertTrue(claude_md.is_symlink())
        self.assertEqual(claude_md.resolve(), airules.assembled_path().resolve())

    def test_defaults_notes_path_outside_tcc(self):
        self.run_setup()
        self.assertEqual(airules.config_get("notes_path"), str(self.home / "daily-notes"))

    def test_warns_when_notes_path_is_tcc_protected(self):
        result = self.run_setup(AI_SETUP_NOTES_PATH=str(self.home / "Documents" / "daily-notes"))

        output = result.stdout + result.stderr
        self.assertIn("Documents", output)
        self.assertRegex(output.lower(), r"warn|restrict")

    def test_warns_when_notes_path_is_in_icloud(self):
        icloud = self.home / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "notes"
        result = self.run_setup(AI_SETUP_NOTES_PATH=str(icloud))

        # iCloud is TCC-gated the same way but is not one of the three folder
        # names, so it needs its own check rather than falling out of the list
        self.assertRegex((result.stdout + result.stderr).lower(), r"warn|restrict")

    def test_accepts_a_notes_path_outside_the_home_directory(self):
        result = self.run_setup(AI_SETUP_NOTES_PATH="/srv/notes")
        self.assertEqual(result.returncode, 0, result.stderr)

        # relative_to() raises for a path outside HOME. Left unhandled that ends
        # the run in a traceback rather than accepting a perfectly good path.
        self.assertEqual(airules.config_get("notes_path"), "/srv/notes")
        self.assertNotRegex((result.stdout + result.stderr).lower(), r"warn|restrict")

    def test_rerun_changes_value(self):
        self.run_setup(AI_SETUP_AGENTS="claude")
        self.run_setup(AI_SETUP_AGENTS="claude codex")

        self.assertEqual(airules.config_get("agents"), ["claude", "codex"])

    def test_rerun_preserves_notes_enabled(self):
        self.run_setup()
        self.write_config(notes_enabled=True)
        self.run_setup()

        self.assertIs(airules.config_get("notes_enabled"), True)

    def test_records_updated_at(self):
        self.run_setup()

        stamp = airules.config_get("updated_at")
        self.assertTrue(stamp)

        # Pinned to a real UTC instant rather than any truthy string, so a stamp
        # that silently stops being written or well-formed is caught
        self.assertRegex(stamp, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    def test_records_where_it_read_the_rules_from(self):
        self.run_setup()

        self.assertEqual(airules.config_get("ai_dir"), str(self.fake_ai))
        self.assertEqual(airules.config_get("local_rules_dir"), str(self.fake_ai / "local_rules"))

    def test_config_is_valid_json_after_a_run(self):
        self.run_setup()

        data = json.loads(airules.config_path().read_text(encoding="utf-8"))
        self.assertEqual(data["agents"], ["claude"])

    def test_dry_run_writes_nothing(self):
        result = self.run_setup("--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)

        # Reports what it would do and touches neither the config nor any agent
        self.assertFalse(airules.config_path().exists())
        self.assertFalse((self.home / ".claude" / "CLAUDE.md").exists())
        self.assertIn("claude", result.stdout)

    def test_dry_run_does_not_disturb_an_existing_config(self):
        self.run_setup(AI_SETUP_AGENTS="claude")
        before = airules.config_path().read_text(encoding="utf-8")

        self.run_setup("--dry-run", AI_SETUP_AGENTS="claude codex cursor")

        self.assertEqual(airules.config_path().read_text(encoding="utf-8"), before)

    def test_reports_the_failure_when_apply_refuses(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text("HAND BUILT\n", encoding="utf-8")
        airules.backup_path(claude_md).write_text("EARLIER BACKUP\n", encoding="utf-8")

        result = self.run_setup()

        # apply refuses rather than destroy the backup, and setup has to pass
        # that up instead of reporting a setup that did not finish as success
        self.assertEqual(result.returncode, airules.ExitStatus.BACKUP_EXISTS)
        self.assertEqual(claude_md.read_text(encoding="utf-8"), "HAND BUILT\n")

    def test_unknown_argument_is_rejected(self):
        result = self.run_setup("--nope")

        # argparse owns usage errors and exits 2
        self.assertEqual(result.returncode, 2)
        self.assertIn("usage", result.stderr.lower())

    def test_clones_the_local_rules_remote_when_the_directory_is_bare(self):
        origin = self.home / "origin"
        origin.mkdir()
        (origin / "50-from-remote.md").write_text("REMOTE RULE\n", encoding="utf-8")
        self._git_init(origin)

        # A directory holding only the tracked .gitignore that ships the empty
        # dir still counts as bare — git clone refuses a non-empty target, so
        # treating it as occupied would make the remote unusable by default.
        local_dir = self.home / "bare_rules"
        local_dir.mkdir()
        (local_dir / ".gitignore").write_text("*\n!.gitignore\n", encoding="utf-8")

        result = self.run_setup(
            AI_SETUP_LOCAL_RULES_REMOTE=str(origin),
            AI_SETUP_LOCAL_RULES_DIR=str(local_dir),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("REMOTE RULE", self.claude_rules())

    def test_does_not_clone_over_existing_local_rules(self):
        origin = self.home / "origin"
        origin.mkdir()
        (origin / "50-from-remote.md").write_text("REMOTE RULE\n", encoding="utf-8")
        self._git_init(origin)

        result = self.run_setup(AI_SETUP_LOCAL_RULES_REMOTE=str(origin))
        self.assertEqual(result.returncode, 0, result.stderr)

        # The sandbox's local_rules already holds a rule. Cloning over it would
        # discard rules that exist nowhere else.
        self.assertIn("LOCAL RULE ONE", self.claude_rules())
        self.assertNotIn("REMOTE RULE", self.claude_rules())

    def test_reports_a_clone_that_fails_instead_of_a_traceback(self):
        local_dir = self.home / "bare_rules"
        local_dir.mkdir()

        result = self.run_setup(
            AI_SETUP_LOCAL_RULES_REMOTE=str(self.home / "no_such_repo"),
            AI_SETUP_LOCAL_RULES_DIR=str(local_dir),
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("[-]", result.stderr)

    def _git_init(self, path):
        """
        Turn a directory into a committed git repository.

        Args:
            path (pathlib.Path): directory holding the files to commit.

        Returns:
            None

        Raises:
            subprocess.CalledProcessError: a git command fails.
        """

        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")

        for command in (["init", "-q"], ["add", "-A"], ["commit", "-qm", "seed"]):
            subprocess.run(["git", "-C", str(path), *command], check=True,
                           capture_output=True, env=env)


if __name__ == "__main__":
    unittest.main()
