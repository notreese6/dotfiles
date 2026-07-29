import os
import subprocess
import unittest
from base import SandboxedTestCase

UNIVERSAL = "# Universal Rules\n\nAlways be concise.\n"


class TestInstallAiTarget(SandboxedTestCase):
    """
    Covers the `ai` target in install.sh, run as the real script.
    """

    def setUp(self):
        """
        Give install.sh an ai/ directory to read that is not the repo's own.

        Args:
            None

        Returns:
            None

        Raises:
            OSError: the fixture files cannot be written.
        """

        super().setUp()

        # AI_DIR rather than the repo's ai/, so these tests do not depend on
        # ai/AGENTS.md, which Task 6 has not authored yet.
        self.fake_ai = self.home / "aifix"
        (self.fake_ai / "local_rules").mkdir(parents=True)
        (self.fake_ai / "AGENTS.md").write_text(UNIVERSAL, encoding="utf-8")

        (self.fake_ai / "bin").mkdir()
        for name in ("ai-rules", "ai-setup"):
            (self.fake_ai / "bin" / name).symlink_to(self.repo / "ai" / "bin" / name)

    def run_install(self, *args, **extra_env):
        """
        Run install.sh against the sandboxed HOME.

        Args:
            *args (str): arguments after the script name, e.g. "ai", "--dry-run".
            **extra_env (str): environment variables to set or replace.

        Returns:
            subprocess.CompletedProcess: the finished run, output captured as
            text. A non-zero exit is returned, not raised.

        Raises:
            OSError: install.sh is missing or is not executable.
        """

        env = dict(os.environ)
        env["AI_DIR"]                   = str(self.fake_ai)
        env["AI_SETUP_NONINTERACTIVE"]  = "true"
        env["AI_SETUP_AGENTS"]          = "claude"
        env["AI_SETUP_LOCAL_RULES_DIR"] = str(self.fake_ai / "local_rules")
        env.update(extra_env)

        return subprocess.run(
            ["./install.sh", *args],
            cwd=str(self.repo), capture_output=True, text=True, env=env,
        )

    def bin_dir(self):
        """
        Locate the sandboxed directory install.sh links the tools into.

        Args:
            None

        Returns:
            pathlib.Path: `~/.local/bin` under the sandboxed HOME. Not
            guaranteed to exist.

        Raises:
            None
        """

        return self.home / ".local" / "bin"

    def test_dry_run_creates_nothing(self):
        result = self.run_install("ai", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)

        self.assertIn("ai-rules", result.stdout)
        self.assertFalse((self.bin_dir() / "ai-rules").exists())
        self.assertFalse((self.home / ".claude" / "CLAUDE.md").exists())

    def test_install_creates_symlinks(self):
        result = self.run_install("ai")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        for name in ("ai-rules", "ai-setup"):
            link = self.bin_dir() / name
            self.assertTrue(link.is_symlink(), f"{name} was not linked")
            self.assertEqual(link.resolve(), (self.repo / "ai" / "bin" / name).resolve())

    def test_install_runs_setup_through_to_assembled_rules(self):
        result = self.run_install("ai")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        # Linking the tools is only half the target: the point of running
        # ai-setup is that a fresh machine ends up with rules actually in place
        claude_md = self.home / ".claude" / "CLAUDE.md"
        self.assertTrue(claude_md.is_symlink())
        self.assertIn("Always be concise.", claude_md.read_text(encoding="utf-8"))

    def test_rerun_is_idempotent(self):
        self.assertEqual(self.run_install("ai").returncode, 0)

        result = self.run_install("ai")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        # The second run must not trip over its own symlinks, its own config, or
        # the backup the first run took of whatever was there before
        self.assertTrue((self.bin_dir() / "ai-rules").is_symlink())
        self.assertTrue((self.home / ".claude" / "CLAUDE.md").is_symlink())

    def test_reports_failure_when_setup_cannot_finish(self):
        # No AGENTS.md to assemble from, so ai-rules refuses and ai-setup passes
        # that up.
        (self.fake_ai / "AGENTS.md").unlink()

        result = self.run_install("ai")

        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)

        # The exit status alone is `set -e` doing its job and would hold with no
        # handling at all. What has to be asserted is the summary line, because
        # errexit ends the run silently — leaving ai-setup's last message
        # looking like one more note rather than the reason nothing installed.
        self.assertIn("ai-setup did not finish", result.stderr)

    def test_a_working_setup_prints_no_failure_summary(self):
        result = self.run_install("ai")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        # Guards the other direction: a summary printed unconditionally would
        # tell every successful install that nothing was written
        self.assertNotIn("did not finish", result.stderr)

    def test_default_run_includes_the_ai_target(self):
        result = self.run_install("--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)

        # With no target named, install.sh runs every known one; ai has to be in
        # that list or a fresh clone silently skips the rules entirely
        self.assertIn("ai-rules", result.stdout)

    def test_unknown_target_still_rejected(self):
        result = self.run_install("bogus")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("bogus", result.stdout + result.stderr)

    def test_help_lists_ai_as_a_known_target(self):
        result = self.run_install("bogus")

        # The rejection names what IS valid, so the list has to stay in step
        # with the dispatcher rather than drifting behind it
        self.assertIn("ai", result.stdout + result.stderr)

    def test_never_touches_the_real_home(self):
        before = self._real_bin_entries()

        self.run_install("ai")

        # These tests run a real installer as a subprocess. If the sandboxed HOME
        # ever stopped being exported, this is what notices before it has linked
        # tools into the developer's own ~/.local/bin.
        self.assertEqual(self._real_bin_entries(), before)

    def _real_bin_entries(self):
        """
        List what is currently in the REAL home's ~/.local/bin.

        Read-only, and reports an absent directory as empty rather than creating
        it, so calling this can never bring the real directory into being.

        Args:
            None

        Returns:
            set: {str} the entry names, or an empty set when the directory does
            not exist.

        Raises:
            OSError: the directory exists but cannot be listed.
        """

        real = self.real_home / ".local" / "bin"

        return {entry.name for entry in real.iterdir()} if real.is_dir() else set()


if __name__ == "__main__":
    unittest.main()
