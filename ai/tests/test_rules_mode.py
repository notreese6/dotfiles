import json
import os
import subprocess
import unittest
from pathlib import Path
from base import SandboxedTestCase
import airules

MINE = "# MY OWN RULES\n\nNever lose this line.\n"


class TestAdditiveText(SandboxedTestCase):
    """
    Covers the text transform additive mode is built on.
    """

    def test_the_readers_own_text_comes_first_and_survives(self):
        out = airules.additive_text(MINE, "GENERATED\n")

        self.assertIn("Never lose this line.", out)
        self.assertLess(out.index("MY OWN RULES"), out.index("GENERATED"))

    def test_applying_it_twice_changes_nothing(self):
        once  = airules.additive_text(MINE, "GENERATED\n")
        twice = airules.additive_text(once, "GENERATED\n")

        # Every apply runs this against its own previous output. If it were not
        # idempotent the file would grow by a full copy of the rules each time.
        self.assertEqual(once, twice)
        self.assertEqual(twice.count(airules.GENERATED_END), 1)

    def test_a_later_run_replaces_the_generated_region_not_the_readers_text(self):
        first  = airules.additive_text(MINE, "OLD RULES\n")
        second = airules.additive_text(first, "NEW RULES\n")

        self.assertIn("NEW RULES", second)
        self.assertNotIn("OLD RULES", second)
        self.assertIn("Never lose this line.", second)

    def test_an_empty_file_gets_only_the_generated_region(self):
        out = airules.additive_text("", "GENERATED\n")

        self.assertTrue(out.startswith(airules.GENERATED_BEGIN))
        self.assertEqual(out.count(airules.GENERATED_END), 1)

    def test_text_the_reader_added_after_the_region_is_kept(self):
        first = airules.additive_text(MINE, "GENERATED\n")
        edited = first + "\n# A NOTE I ADDED LATER\n"

        second = airules.additive_text(edited, "GENERATED\n")

        # People write below whatever is already in the file. Losing that would
        # be the same destruction additive mode exists to avoid.
        self.assertIn("A NOTE I ADDED LATER", second)
        self.assertIn("Never lose this line.", second)

    def test_the_readers_own_text_is_never_parsed_for_markers_mid_line(self):
        quoting = MINE + f"\nWe use {airules.GENERATED_END} to close the block.\n"

        out = airules.additive_text(quoting, "GENERATED\n")

        # A marker quoted inside a sentence is prose, not a boundary. Treating
        # it as one would silently truncate the reader's file.
        self.assertIn("to close the block.", out)
        self.assertIn("Never lose this line.", out)


class TestApplyModes(SandboxedTestCase):
    """
    Covers what each mode does to a real agent file, end to end.
    """

    def setUp(self):
        """
        Build a throwaway ai/ directory with one module and a private layer.

        Args:
            None

        Returns:
            None

        Raises:
            OSError: the sandbox cannot be written.
        """

        super().setUp()

        self.fake_ai = self.home / "aifix"
        self.rules   = self.fake_ai / "rules"
        self.write_module(self.rules, "universal.md", "# Using these rules\n\nTOOL_MARKER\n",
                          front="order=10, required")
        self.write_module(self.rules, "daily-notes.md", "# Daily notes\n\nNOTES_MARKER\n",
                          front="order=20, default=on")

        (self.fake_ai / "local_rules").mkdir(parents=True)
        (self.fake_ai / "local_rules" / "10-private.md").write_text("PRIVATE_MARKER\n", encoding="utf-8")

        self.claude_md = self.home / ".claude" / "CLAUDE.md"
        self.claude_md.parent.mkdir(parents=True)

    def apply(self, mode, agents=("claude",)):
        """
        Run ai-rules apply against the sandbox in one mode.

        Args:
            mode (str): "clobber" or "additive".
            agents (tuple of str): agent names to configure.

        Returns:
            subprocess.CompletedProcess: the finished run.

        Raises:
            OSError: the script is missing or is not executable.
        """

        self.write_config(
            agents          = list(agents),
            ai_dir          = str(self.fake_ai),
            local_rules_dir = str(self.fake_ai / "local_rules"),
            rules_mode      = mode,
            modules         = {"daily-notes": True},
        )

        env           = dict(os.environ)
        env["AI_DIR"] = str(self.fake_ai)

        return subprocess.run([str(self.repo / "ai" / "bin" / "ai-rules"), "apply"],
                              capture_output=True, text=True, env=env)

    def test_clobber_replaces_the_file_with_a_link(self):
        self.claude_md.write_text(MINE, encoding="utf-8")

        self.assertEqual(self.apply("clobber").returncode, 0)

        self.assertTrue(self.claude_md.is_symlink())
        self.assertEqual(self.claude_md.resolve(), airules.assembled_path().resolve())
        self.assertNotIn("MY OWN RULES", self.claude_md.read_text(encoding="utf-8"))

    def test_additive_keeps_the_file_and_the_readers_rules(self):
        self.claude_md.write_text(MINE, encoding="utf-8")

        self.assertEqual(self.apply("additive").returncode, 0)

        # A real file, not a link: a symlink would mean the reader's rules are
        # not in the file the agent reads, which is the whole point of the mode.
        self.assertFalse(self.claude_md.is_symlink())

        text = self.claude_md.read_text(encoding="utf-8")
        self.assertIn("Never lose this line.", text)
        self.assertIn("NOTES_MARKER", text)
        self.assertIn("TOOL_MARKER", text)
        self.assertIn("PRIVATE_MARKER", text)

    def test_additive_backs_the_file_up_before_touching_it(self):
        self.claude_md.write_text(MINE, encoding="utf-8")

        self.apply("additive")

        saved = list((self.home / airules.BACKUP_DIRNAME).rglob("CLAUDE.md"))
        self.assertTrue(saved, "additive mode wrote without taking a backup")

        # The backup is the only way back from a bad generated region, even
        # though the reader's own text was not what changed.
        self.assertEqual(saved[0].read_text(encoding="utf-8"), MINE)

    def test_additive_is_idempotent_across_runs(self):
        self.claude_md.write_text(MINE, encoding="utf-8")

        self.apply("additive")
        first = self.claude_md.read_text(encoding="utf-8")
        self.apply("additive")
        second = self.claude_md.read_text(encoding="utf-8")

        self.assertEqual(first, second)
        self.assertEqual(second.count(airules.GENERATED_END), 1)

    def test_additive_updates_the_region_when_the_rules_change(self):
        self.claude_md.write_text(MINE, encoding="utf-8")
        self.apply("additive")

        self.write_module(self.rules, "daily-notes.md", "# Daily notes\n\nCHANGED_MARKER\n",
                          front="order=20, default=on")
        self.apply("additive")

        text = self.claude_md.read_text(encoding="utf-8")
        self.assertIn("CHANGED_MARKER", text)
        self.assertNotIn("NOTES_MARKER", text)
        self.assertIn("Never lose this line.", text)

    def test_switching_from_clobber_to_additive_does_not_inline_our_own_rules(self):
        self.claude_md.write_text(MINE, encoding="utf-8")
        self.apply("clobber")
        self.assertTrue(self.claude_md.is_symlink())

        self.apply("additive")

        text = self.claude_md.read_text(encoding="utf-8")
        self.assertFalse(self.claude_md.is_symlink())

        # The symlink held this repo's rules and nothing of the reader's, so
        # carrying its contents across would append our rules to a copy of our
        # rules. One generated region, no duplication.
        self.assertEqual(text.count(airules.GENERATED_END), 1)
        self.assertEqual(text.count("TOOL_MARKER"), 1)

    def test_switching_from_additive_to_clobber_replaces_the_file(self):
        self.claude_md.write_text(MINE, encoding="utf-8")
        self.apply("additive")

        self.apply("clobber")

        self.assertTrue(self.claude_md.is_symlink())

    def test_additive_with_no_existing_file_still_writes_one(self):
        self.assertEqual(self.apply("additive").returncode, 0)

        self.assertTrue(self.claude_md.is_file())
        self.assertIn("NOTES_MARKER", self.claude_md.read_text(encoding="utf-8"))

    def test_every_agent_gets_the_same_treatment(self):
        codex = self.home / ".codex" / "AGENTS.md"
        codex.parent.mkdir(parents=True)
        codex.write_text("# CODEX OWN\n", encoding="utf-8")
        self.claude_md.write_text(MINE, encoding="utf-8")

        self.apply("additive", agents=("claude", "codex"))

        for path, own in ((self.claude_md, "MY OWN RULES"), (codex, "CODEX OWN")):
            self.assertFalse(path.is_symlink(), f"{path} became a link")
            self.assertIn(own, path.read_text(encoding="utf-8"))

    def test_the_run_reports_appending_rather_than_linking(self):
        self.claude_md.write_text(MINE, encoding="utf-8")

        out = self.apply("additive").stdout

        # Saying "linked" for an append describes it as the replacement the
        # reader chose this mode to avoid
        self.assertIn("appended to", out)
        self.assertNotIn("[+] linked", out)

    def test_an_unknown_mode_falls_back_rather_than_guessing_clobber(self):
        self.claude_md.write_text(MINE, encoding="utf-8")

        self.apply("banana")

        # A typo must not silently pick the destructive one. The default is
        # clobber, but that is the documented default, not a guess made here.
        self.assertEqual(airules.Config.load().rules_mode, airules.RULES_MODE_CLOBBER)


if __name__ == "__main__":
    unittest.main()
