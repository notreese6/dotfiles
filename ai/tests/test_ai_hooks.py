import json
import subprocess
import unittest

from base import REPO_ROOT, SandboxedTestCase

TOOL = REPO_ROOT / "ai" / "bin" / "ai-hooks"


class TestAiHooks(SandboxedTestCase):
    """
    Covers wiring hooks into files the user also owns.
    """

    def run_tool(self, *args):
        """
        Run ai-hooks against the sandboxed HOME.

        Args:
            *args (str): arguments after the command name.

        Returns:
            subprocess.CompletedProcess: the finished run.

        Raises:
            OSError: the tool is missing or is not executable.
        """

        import os

        return subprocess.run(["python3", str(TOOL)] + list(args),
                              capture_output=True, text=True, env=dict(os.environ))

    def settings(self):
        """
        Read the sandboxed Claude settings file.

        Args:
            None

        Returns:
            dict: its contents, or {} when absent.

        Raises:
            ValueError: it exists but is not valid JSON.
        """

        path = self.home / ".claude" / "settings.json"

        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}

    def write_settings(self, data):
        """
        Seed the sandboxed Claude settings file.

        Args:
            data (dict): contents to write.

        Returns:
            None

        Raises:
            OSError: it cannot be written.
        """

        path = self.home / ".claude" / "settings.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def test_it_wires_both_hooks_into_a_fresh_machine(self):
        result = self.run_tool("install")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("UserPromptSubmit", self.settings()["hooks"])
        self.assertIn("Stop", self.settings()["hooks"])

    def test_running_it_twice_changes_nothing(self):
        self.run_tool("install")
        first = (self.home / ".claude" / "settings.json").read_text(encoding="utf-8")

        self.run_tool("install")
        second = (self.home / ".claude" / "settings.json").read_text(encoding="utf-8")

        # An installer people re-run has to be safe to re-run. Appending a second
        # copy would fire the hook twice and be invisible until it did.
        self.assertEqual(first, second)

    def test_it_leaves_the_rest_of_your_settings_alone(self):
        self.write_settings({"model": "opus", "theme": "dark-ansi",
                             "enabledPlugins": {"something": True}})

        self.run_tool("install")
        after = self.settings()

        # This file is the user's, not ours — it carries the model, the theme and
        # the plugin list. Installing a hook must not cost them any of it.
        self.assertEqual(after["model"], "opus")
        self.assertEqual(after["theme"], "dark-ansi")
        self.assertEqual(after["enabledPlugins"], {"something": True})

    def test_it_refuses_to_replace_a_hook_you_wired_yourself(self):
        self.write_settings({"hooks": {"Stop": [
            {"hooks": [{"type": "command", "command": "/usr/local/bin/mine"}]}]}})

        result = self.run_tool("install")

        self.assertEqual(result.returncode, 1)
        self.assertIn("already runs something else", result.stderr)

        # Untouched, not appended to: firing both would be a surprise, and
        # replacing it takes away something put there on purpose.
        wired = self.settings()["hooks"]["Stop"][0]["hooks"][0]["command"]
        self.assertEqual(wired, "/usr/local/bin/mine")

    def test_a_malformed_file_is_reported_rather_than_rewritten(self):
        path = self.home / ".claude" / "settings.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{ not json", encoding="utf-8")

        result = self.run_tool("install")

        # Rewriting a file we cannot parse means discarding whatever it held,
        # which is the clobber this tool exists to avoid.
        self.assertEqual(result.returncode, 1)
        self.assertIn("not valid JSON", result.stderr)
        self.assertEqual(path.read_text(encoding="utf-8"), "{ not json")

    def test_cursor_gets_the_schema_version_it_requires(self):
        self.run_tool("install")

        cursor = json.loads((self.home / ".cursor" / "hooks.json").read_text(encoding="utf-8"))

        # Cursor rejects a hooks file with no version, so a file we create from
        # nothing has to carry one or the hooks silently never load.
        self.assertEqual(cursor["version"], 1)

    def test_each_agent_gets_its_own_event_name(self):
        self.run_tool("install")

        claude = self.settings()["hooks"]
        cursor = json.loads((self.home / ".cursor" / "hooks.json").read_text(encoding="utf-8"))["hooks"]

        # Claude and Codex use PascalCase, Cursor camelCase. Wiring one name
        # everywhere would leave whichever disagrees silently unhooked.
        self.assertIn("UserPromptSubmit", claude)
        self.assertIn("beforeSubmitPrompt", cursor)

    def test_the_date_hook_is_told_which_shape_to_emit(self):
        self.run_tool("install")

        claude = self.settings()["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
        cursor = json.loads(
            (self.home / ".cursor" / "hooks.json").read_text(encoding="utf-8")
        )["hooks"]["beforeSubmitPrompt"][0]["command"]

        # The two agents disagree on how a hook returns text, so one script
        # serves both only if it is told which of them is asking.
        self.assertIn("--format=claude", claude)
        self.assertIn("--format=cursor", cursor)

    def test_dry_run_writes_nothing(self):
        result = self.run_tool("install", "--dry-run")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.home / ".claude" / "settings.json").exists())

    def test_status_reports_without_changing_anything(self):
        result = self.run_tool("status")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.home / ".claude" / "settings.json").exists())


if __name__ == "__main__":
    unittest.main()
