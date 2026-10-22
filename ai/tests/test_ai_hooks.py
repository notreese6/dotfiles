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

    def test_it_adds_its_hook_after_one_you_wired_yourself(self):
        mine = {"hooks": [{"type": "command", "command": "/usr/local/bin/mine"}]}
        self.write_settings({"hooks": {"Stop": [mine]}})

        result = self.run_tool("install")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("after 1 of your own", result.stdout)

        stop = self.settings()["hooks"]["Stop"]

        # Theirs stays first and byte-for-byte what it was; ours is added after
        # it, so both run and nothing the user put there is taken away.
        self.assertEqual(len(stop), 2)
        self.assertEqual(stop[0], mine)
        self.assertIn("notes-reminder", stop[1]["hooks"][0]["command"])

    def test_running_it_twice_beside_your_own_hook_adds_nothing_more(self):
        self.write_settings({"hooks": {"Stop": [
            {"hooks": [{"type": "command", "command": "/usr/local/bin/mine"}]}]}})

        self.run_tool("install")
        first = (self.home / ".claude" / "settings.json").read_text(encoding="utf-8")

        self.run_tool("install")
        second = (self.home / ".claude" / "settings.json").read_text(encoding="utf-8")

        self.assertEqual(first, second)
        self.assertEqual(len(self.settings()["hooks"]["Stop"]), 2)

    def test_the_flat_schema_gets_the_same_treatment(self):
        path = self.home / ".cursor" / "hooks.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"version": 1, "hooks": {"stop": [{"command": "/x/mine"}]}}),
                        encoding="utf-8")

        self.run_tool("install")

        data = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(data["version"], 1)
        self.assertEqual(data["hooks"]["stop"][0], {"command": "/x/mine"})
        self.assertEqual(len(data["hooks"]["stop"]), 2)

    def test_an_event_that_is_not_a_list_is_reported_and_left_alone(self):
        self.write_settings({"hooks": {"Stop": {"command": "/usr/local/bin/mine"}}})

        result = self.run_tool("install")

        # There is no way to add to it without replacing it, so it is reported
        # and left exactly as it was, while the other event is still wired.
        self.assertEqual(result.returncode, 1)
        self.assertIn("not a list of hooks", result.stderr)
        self.assertEqual(self.settings()["hooks"]["Stop"], {"command": "/usr/local/bin/mine"})
        self.assertIn("UserPromptSubmit", self.settings()["hooks"])

    def test_a_hooks_key_that_is_not_an_object_is_reported_rather_than_rewritten(self):
        self.write_settings({"hooks": ["nonsense"], "model": "opus"})
        before = (self.home / ".claude" / "settings.json").read_text(encoding="utf-8")

        result = self.run_tool("install")

        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot be merged into", result.stderr)
        self.assertEqual((self.home / ".claude" / "settings.json").read_text(encoding="utf-8"), before)

    def test_a_file_that_is_not_an_object_is_reported_rather_than_rewritten(self):
        path = self.home / ".claude" / "settings.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("[]", encoding="utf-8")

        result = self.run_tool("install")

        # A traceback would also exit 1, so the message is what proves it was
        # recognised and reported rather than tripped over.
        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot be merged into", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(path.read_text(encoding="utf-8"), "[]")

    def test_status_says_when_ours_sits_after_yours(self):
        self.write_settings({"hooks": {"Stop": [
            {"hooks": [{"type": "command", "command": "/usr/local/bin/mine"}]}]}})
        self.run_tool("install")

        result = self.run_tool("status")

        self.assertIn("ours, after 1 of your own", result.stdout)

    def test_status_says_when_ours_is_not_wired_because_something_else_is(self):
        self.write_settings({"hooks": {"Stop": [
            {"hooks": [{"type": "command", "command": "/usr/local/bin/mine"}]}]}})

        result = self.run_tool("status")

        self.assertIn("another command (ours not wired)", result.stdout)

    def test_only_the_agents_you_named_are_written_to(self):
        self.write_config(agents=["claude"])

        result = self.run_tool("install")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.home / ".claude" / "settings.json").is_file())

        # Creating a directory and a hooks file for a tool the person never named
        # is the surprise this setting exists to prevent.
        self.assertFalse((self.home / ".codex").exists())
        self.assertFalse((self.home / ".cursor").exists())
        self.assertIn("not configured, so left alone: codex, cursor", result.stdout)

    def test_every_agent_is_wired_when_nothing_has_been_configured(self):
        self.run_tool("install")

        self.assertTrue((self.home / ".claude" / "settings.json").is_file())
        self.assertTrue((self.home / ".codex" / "hooks.json").is_file())
        self.assertTrue((self.home / ".cursor" / "hooks.json").is_file())

    def test_an_unknown_agent_name_is_reported_and_the_rest_still_wired(self):
        self.write_config(agents=["claude", "claud"])

        result = self.run_tool("install")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("unknown agent 'claud'", result.stderr)
        self.assertTrue((self.home / ".claude" / "settings.json").is_file())

    def test_it_stops_when_no_configured_agent_can_carry_hooks(self):
        self.write_config(agents=["claud"])

        result = self.run_tool("install")

        # Doing nothing and exiting 0 would read exactly like a successful run.
        self.assertEqual(result.returncode, 1)
        self.assertIn("nothing was wired", result.stderr)
        self.assertFalse((self.home / ".claude").exists())

    def test_it_stops_when_the_agents_setting_cannot_be_read(self):
        config = self.xdg / "ai-notes" / "config.json"
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text("{ not json", encoding="utf-8")

        result = self.run_tool("install")

        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot read the agents setting", result.stderr)
        self.assertFalse((self.home / ".claude").exists())

    def test_status_reports_only_the_agents_you_named(self):
        self.write_config(agents=["codex"])

        result = self.run_tool("status")

        lines = result.stdout.splitlines()

        self.assertTrue(any(line.startswith("[*] codex") for line in lines))
        self.assertFalse(any(line.startswith("[*] claude") for line in lines))

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
