import hashlib
import os
import subprocess
import unittest
from pathlib import Path
from base import SandboxedTestCase
import airules

TOOL_RULES = '# Using these rules\n\nTOOL_MARKER: edit the repo, never the live file.\n'

MISC = "# Misc Rules\n\nAlways be concise.\n\nEnd of misc.\n"

# The notes rules are their own module under ai/rules/, rather than a section
# embedded in someone else's file.
NOTES_RULES = "## Daily notes\n\nNOTES SYNC: pull before writing notes.\n"

# Stands in for a live, hand-built rules file that predates any `apply` run
PRIOR_RULES = "# Hand-built rules\n\nIrreplaceable. No backup exists.\n"

# The `agents` values a hand-edited config plausibly ends up holding, each with
# the fragment the error must quote back so the bad value is identifiable
MALFORMED_AGENTS = (
    (None,               "None"),
    (5,                  "5"),
    ({"claude": True},   "claude"),
    (["claude", 5],      "5"),
)


def revised_universal(marker):
    """
    Build a universal rules text no other revision can be mistaken for.

    Args:
        marker (str): text unique to this revision, e.g. "TWO".

    Returns:
        str: a complete universal rules document carrying `marker`.

    Raises:
        None
    """

    return f"# Universal Rules\n\nRevision {marker}.\n"


def file_fingerprint(path):
    """
    Capture enough of a file's state to notice any rewrite of it.

    Args:
        path (pathlib.Path): file to fingerprint. Need not exist.

    Returns:
        tuple: (True, size, mtime_ns, sha256 hex digest) for an existing file,
        or (False, None, None, None) when it is absent. Two calls comparing
        equal mean the file was not created, removed, or rewritten in between.

    Raises:
        OSError: the file exists but cannot be read.
    """

    if not path.is_file():
        return (False, None, None, None)

    info = path.stat()

    return (True, info.st_size, info.st_mtime_ns, hashlib.sha256(path.read_bytes()).hexdigest())


class TestAiRulesCli(SandboxedTestCase):
    """
    End-to-end tests for the ai-rules command, run as a real subprocess.
    """

    def setUp(self):
        """
        Build a throwaway ai/ directory and point the config at it.

        The universal rules, the local rules, and every config key the CLI reads
        live under the sandboxed HOME, so the command never sees the real ones.

        Args:
            None

        Returns:
            None

        Raises:
            OSError: the sandbox directories or files cannot be created.
        """

        super().setUp()

        self.fake_ai = self.home / "aifix"
        (self.fake_ai / "local_rules").mkdir(parents=True)
        self.rules = self.fake_ai / "rules"
        self.write_module(self.rules, "universal.md",   TOOL_RULES,  front="order=10, required")
        self.write_module(self.rules, "misc.md",        MISC,        front="order=30, default=off, clobbers")
        (self.fake_ai / "local_rules" / "10-first.md").write_text("LOCAL RULE ONE\n", encoding="utf-8")
        (self.fake_ai / "local_rules" / "20-second.md").write_text("LOCAL RULE TWO\n", encoding="utf-8")

        self.write_module(self.rules, "daily-notes.md", NOTES_RULES, front="order=20, default=on")

        self.write_config(
            local_rules_dir = str(self.fake_ai / "local_rules"),
            agents          = ["claude"],
        )
        self.set_modules(daily_notes=False, misc=True)

    def run_cli(self, *args, **overrides):
        """
        Run the ai-rules script in a subprocess against the sandbox.

        Args:
            *args (str): command-line arguments passed after the script name.
            **overrides (str): environment variables to set for this run.

        Returns:
            subprocess.CompletedProcess: the finished run, with `returncode`,
            `stdout`, and `stderr` captured as text. A non-zero exit is
            returned, not raised.

        Raises:
            OSError: the script is missing or is not executable.
        """

        # Inherits the sandboxed HOME and XDG_CONFIG_HOME that setUp exported,
        # so the child process resolves the same config and targets we do.
        env           = dict(os.environ)
        env["AI_DIR"] = str(self.fake_ai)
        env.update(overrides)

        return subprocess.run(
            [str(self.repo / "ai" / "bin" / "ai-rules")] + list(args),
            capture_output=True, text=True, env=env,
        )

    def agent_files(self):
        """
        List every per-agent target path, whether or not it exists.

        Args:
            None

        Returns:
            list: [pathlib.Path] one path per name in airules.SUPPORTED_AGENTS,
            resolved against the sandboxed HOME and XDG_CONFIG_HOME.

        Raises:
            None
        """

        resolved = airules.agent_targets(airules.known_agent_names())

        return [target.path for target in resolved.targets]

    def wrote_paths(self, stdout):
        """
        Pull the target paths back out of the CLI's `[+] linked <path>` lines.

        Args:
            stdout (str): the CLI's captured standard output.

        Returns:
            list: [pathlib.Path] one path per success line, in the order
            printed. Empty when the run reported linking nothing.

        Raises:
            None
        """

        # Matching the [+] success tag as well keeps this from picking up a path
        # out of an informational or warning line that happens to say "linked".
        prefix = "[+] linked "

        return [Path(line[len(prefix):]) for line in stdout.splitlines() if line.startswith(prefix)]

    def sandbox_backups(self):
        """
        List every backup file anywhere under the sandboxed HOME.

        Sweeping the whole sandbox rather than checking one expected name is
        what catches a backup that accumulates under a second name, or lands
        somewhere no per-target check would look.

        Args:
            None

        Returns:
            list: [pathlib.Path] every path under the sandbox whose name ends in
            the backup root, sorted. Empty when no backup was taken.

        Raises:
            OSError: the sandbox exists but cannot be walked.
        """

        root = self.home / airules.BACKUP_DIRNAME

        return sorted(p for p in root.rglob("*") if p.is_file()) if root.is_dir() else []

    def backup_notices(self, stdout):
        """
        Pull the backup paths back out of the CLI's informational notices.

        Args:
            stdout (str): the CLI's captured standard output.

        Returns:
            list: [pathlib.Path] one path per notice line, in the order printed.
            Empty when the run reported taking no backup.

        Raises:
            None
        """

        # The [*] tag is matched too, so a success or warning line that happens
        # to mention a backup cannot be read as the notice itself.
        prefix = "[*] what was there is saved at "

        return [Path(line[len(prefix):]) for line in stdout.splitlines() if line.startswith(prefix)]

    def real_agent_entries(self):
        """
        List the top-level names inside the REAL home's agent directories.

        Read-only, and a directory that is absent is reported as empty rather
        than created, so calling this can never bring the real ~/.claude into
        being.

        Args:
            None

        Returns:
            set: {(str, str)} a (directory name, entry name) pair for every
            entry directly inside the real ~/.claude and ~/.codex.

        Raises:
            OSError: one of those directories exists but cannot be listed.
        """

        entries = set()

        for name in (".claude", ".codex"):
            directory = self.real_home / name
            if not directory.is_dir():
                continue

            for child in directory.iterdir():
                entries.add((name, child.name))

        return entries

    def test_apply_writes_claude_target(self):
        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)

        text = (self.home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("Always be concise.", text)
        self.assertIn("LOCAL RULE ONE", text)
        self.assertIn("LOCAL RULE TWO", text)
        self.assertNotIn("NOTES SYNC", text)

    def test_bare_invocation_is_a_usage_error_and_writes_nothing(self):
        result = self.run_cli()

        self.assertEqual(result.returncode, 2)
        self.assertIn("usage:", result.stdout + result.stderr)
        self.assertIn("required", result.stdout + result.stderr)
        self.assertFalse((self.home / ".claude" / "CLAUDE.md").exists())

    def test_bare_invocation_does_not_back_anything_up(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True, exist_ok=True)
        claude_md.write_text(PRIOR_RULES, encoding="utf-8")

        self.assertEqual(self.run_cli().returncode, 2)
        self.assertEqual(claude_md.read_text(encoding="utf-8"), PRIOR_RULES)
        self.assertEqual(self.sandbox_backups(), [])

    def test_enabling_the_notes_module_includes_it(self):
        self.set_modules(daily_notes=True)
        self.run_cli("apply")

        text = (self.home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("NOTES SYNC", text)
        self.assertEqual(text.count("NOTES SYNC"), 1)

    def test_notes_disabled_leaves_the_layer_out(self):
        self.set_modules(daily_notes=False)
        self.run_cli("apply")

        # The layer is skipped rather than stripped after the fact, so no
        # markers are left behind either
        text = (self.home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertNotIn("NOTES SYNC", text)

    def test_notes_layer_is_independent_of_the_universal_file(self):
        # The whole point of the split: someone can take the notes rules without
        # the rest of one person's universal opinions
        (self.rules / "misc.md").write_text("# Only this\n\nNothing else.\n", encoding="utf-8")
        self.set_modules(daily_notes=True)
        self.run_cli("apply")

        text = (self.home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("NOTES SYNC", text)
        self.assertIn("Nothing else.", text)

    def test_rerun_is_idempotent(self):
        self.run_cli("apply")
        first = (self.home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")

        self.run_cli("apply")
        second = (self.home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")

        self.assertEqual(first, second)
        self.assertEqual(second.count(airules.LOCAL_END), 1)

    def test_multiple_agents(self):
        self.write_config(agents=["claude", "codex"])
        self.run_cli("apply")
        self.assertTrue((self.home / ".claude" / "CLAUDE.md").exists())
        self.assertTrue((self.home / ".codex" / "AGENTS.md").exists())

    def test_no_local_rules_yields_no_local_block(self):
        for path in (self.fake_ai / "local_rules").glob("*.md"):
            path.unlink()

        self.run_cli("apply")
        self.assertNotIn(airules.LOCAL_END, (self.home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8"))

    def test_no_rules_at_all_fails_clearly(self):
        (self.rules / "misc.md").unlink()
        for stale in (self.fake_ai / "local_rules").glob("*.md"):
            stale.unlink()

        result = self.run_cli("apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("rules", result.stdout + result.stderr)

    def test_unknown_command_exits_nonzero(self):
        self.assertNotEqual(self.run_cli("bogus").returncode, 0)

    def test_string_agents_match_equivalent_list(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"

        self.write_config(agents=["claude"])
        self.assertEqual(self.run_cli("apply").returncode, 0)
        from_list = claude_md.read_text(encoding="utf-8")

        claude_md.unlink()

        self.write_config(agents="claude")
        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(claude_md.read_text(encoding="utf-8"), from_list)

    def test_string_agents_split_on_whitespace(self):
        self.write_config(agents="claude codex")

        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.home / ".claude" / "CLAUDE.md").exists())
        self.assertTrue((self.home / ".codex" / "AGENTS.md").exists())

    def test_unknown_agent_warns_naming_it(self):
        self.write_config(agents=["claud"])

        result = self.run_cli("apply")

        # Quoted so the assertion cannot pass on the "claud" inside "claude"
        self.assertIn("'claud'", result.stderr)
        for name in airules.known_agent_names():
            self.assertIn(name, result.stderr)

    def test_all_unknown_agents_exit_nonzero_and_write_nothing(self):
        self.write_config(agents=["claud", "codexx"])

        result = self.run_cli("apply")
        self.assertNotEqual(result.returncode, 0)

        for path in self.agent_files():
            self.assertFalse(path.exists(), "%s should not have been written" % path)

    def test_mixed_agents_write_the_valid_one_and_warn(self):
        self.write_config(agents=["claude", "bogus"])

        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.home / ".claude" / "CLAUDE.md").exists())
        self.assertIn("'bogus'", result.stderr)

    def test_no_known_agents_exits_3(self):
        self.write_config(agents=["claud", "codexx"])

        self.assertEqual(self.run_cli("apply").returncode, 3)

    def test_empty_agents_list_exits_3_and_writes_nothing(self):
        self.write_config(agents=[])

        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 3, result.stderr)

        for path in self.agent_files():
            self.assertFalse(path.exists(), "%s should not have been written" % path)

    def test_malformed_agents_setting_is_a_config_error(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"

        for value, fragment in MALFORMED_AGENTS:
            with self.subTest(agents=value):
                self.write_config(agents=value)

                result = self.run_cli("apply")

                self.assertEqual(result.returncode, 4, result.stderr)
                self.assertFalse(claude_md.exists(), "%r should have written nothing" % (value,))

                # The bad value and the usable names both have to be on screen
                self.assertIn(fragment, result.stderr)
                for name in airules.known_agent_names():
                    self.assertIn(name, result.stderr)

    def test_empty_modules_leave_existing_rules_untouched(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text(PRIOR_RULES, encoding="utf-8")

        # A module truncated to nothing assembles into a rules file with no rules
        # in it, which must never replace the live one
        for module in (self.rules).glob("*.md"):
            module.write_text("", encoding="utf-8")
        for stale in (self.fake_ai / "local_rules").glob("*.md"):
            stale.unlink()

        result = self.run_cli("apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(claude_md.read_text(encoding="utf-8"), PRIOR_RULES)
        self.assertIn("no rules selected or found", result.stderr)

    def test_whitespace_only_modules_leave_existing_rules_untouched(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text(PRIOR_RULES, encoding="utf-8")

        # Every layer blanked, not just the module: the private layer counts as
        # rules too, so leaving it would make this pass for the wrong reason
        for module in (self.rules).glob("*.md"):
            module.write_text("  \n\n\t\n", encoding="utf-8")
        for stale in (self.fake_ai / "local_rules").glob("*.md"):
            stale.write_text("  \n", encoding="utf-8")

        result = self.run_cli("apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(claude_md.read_text(encoding="utf-8"), PRIOR_RULES)

    def test_every_module_combination_assembles_exactly_what_is_enabled(self):
        # The full matrix, because "add a rule and it shows up" is only true for
        # the modules this machine has switched on. A rule written into a module
        # that is off is saved and then never reaches any agent, which looks
        # exactly like success from the writer's side.
        (self.rules / "misc.md").write_text("MISC_MARKER\n", encoding="utf-8")
        (self.rules / "daily-notes.md").write_text("NOTES_MARKER\n", encoding="utf-8")
        for stale in (self.fake_ai / "local_rules").glob("*.md"):
            stale.unlink()
        (self.fake_ai / "local_rules" / "10-p.md").write_text("LOCAL_MARKER\n", encoding="utf-8")

        claude_md = self.home / ".claude" / "CLAUDE.md"

        for misc in (True, False):
            for notes in (True, False):
                with self.subTest(misc=misc, notes=notes):
                    self.set_modules(misc=misc, daily_notes=notes)
                    self.assertEqual(self.run_cli("apply").returncode, 0)

                    text = claude_md.read_text(encoding="utf-8")
                    self.assertEqual("MISC_MARKER" in text, misc)
                    self.assertEqual("NOTES_MARKER" in text, notes)

                    # Two layers have no switch, and they are the two a reader
                    # can therefore always count on: the private rules, and the
                    # tool's own rules about editing the source rather than the
                    # generated file. Neither flag can turn either off.
                    self.assertIn("LOCAL_MARKER", text)
                    self.assertIn("TOOL_MARKER", text)

    def test_the_private_layer_defaults_beside_the_config(self):
        # No local_rules_dir at all, which is a config ai-setup has not written
        # yet — apply still has to know where the private layer lives, and it
        # must not be inside the repo tree.
        self.write_config(local_rules_dir=None)

        default = airules.default_local_rules_dir()
        default.mkdir(parents=True, exist_ok=True)
        (default / "10-default-place.md").write_text("DEFAULT PLACE RULE\n", encoding="utf-8")

        self.assertEqual(self.run_cli("apply").returncode, 0)

        text = (self.home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("DEFAULT PLACE RULE", text)

        # And the in-repo directory is not what it fell back to
        self.assertNotIn("LOCAL RULE ONE", text)

    def test_a_selected_module_with_no_file_stops_the_run(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text(PRIOR_RULES, encoding="utf-8")

        self.set_modules(daily_notes=True)
        (self.rules / "daily-notes.md").unlink()

        result = self.run_cli("apply")

        # A distinct status, not just nonzero: the caller has to be able to tell
        # a broken install from an empty one without parsing the message. And
        # nobody reads the message — that is the whole reason this stops rather
        # than warning, so the exit status is what has to carry it.
        self.assertEqual(result.returncode, airules.ExitStatus.MISSING_MODULE)
        self.assertIn("daily-notes.md", result.stderr)

        # Nothing written and nothing displaced. Assembling without the module
        # would have replaced these rules with a copy silently missing it.
        self.assertEqual(claude_md.read_text(encoding="utf-8"), PRIOR_RULES)
        self.assertEqual(self.sandbox_backups(), [])

    def test_the_missing_module_message_says_how_to_get_unstuck(self):
        self.set_modules(daily_notes=True)
        (self.rules / "daily-notes.md").unlink()

        stderr = self.run_cli("apply").stderr

        # Both ways out, because either can be the right one: the file was lost
        # by accident, or the module genuinely is not wanted on this machine
        self.assertIn(str(self.fake_ai / "rules"), stderr)
        self.assertIn("Restore", stderr)
        self.assertIn("config", stderr)

    def test_a_module_turned_off_may_be_absent_without_complaint(self):
        # The mirror of the test above, and the reason it checks a *selected*
        # module: a fork that does not want the notes discipline deletes the
        # file and turns the flag off, and that has to keep working.
        self.set_modules(daily_notes=False)
        (self.rules / "daily-notes.md").unlink()

        self.assertEqual(self.run_cli("apply").returncode, 0)

    def test_a_rule_added_to_a_disabled_module_never_reaches_the_agent(self):
        self.set_modules(misc=False, daily_notes=True)

        # Writing the rule succeeds; that is the trap. Only the assembly says
        # whether an agent will ever see it.
        (self.rules / "misc.md").write_text("BRAND_NEW_RULE\n", encoding="utf-8")
        self.assertEqual(self.run_cli("apply").returncode, 0)

        self.assertNotIn("BRAND_NEW_RULE",
                         (self.home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8"))

    def test_the_private_layer_reaches_the_agent_with_every_module_off(self):
        self.set_modules(misc=False, daily_notes=False)
        (self.fake_ai / "local_rules" / "50-new.md").write_text("PRIVATE_ADDITION\n", encoding="utf-8")

        self.assertEqual(self.run_cli("apply").returncode, 0)

        # Which is what makes local_rules the safe answer when someone asks for
        # a rule and the module it belongs in is switched off
        self.assertIn("PRIVATE_ADDITION",
                      (self.home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8"))

    def test_reports_the_directory_the_rules_came_from(self):
        result = self.run_cli("apply")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(self.fake_ai), result.stdout)

    def test_first_apply_creates_no_backup(self):
        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)

        # Nothing existed to preserve, so an empty .bak would be a lie
        self.assertEqual(self.sandbox_backups(), [])
        self.assertEqual(self.backup_notices(result.stdout), [])

    def test_backup_holds_the_hand_built_rules_it_replaced(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text(PRIOR_RULES, encoding="utf-8")

        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)

        # The live file the very first apply overwrites is the one with no copy
        # anywhere else, so it is the one the backup has to be holding
        self.assertEqual(self.backup_of(claude_md).read_text(encoding="utf-8"), PRIOR_RULES)
        self.assertNotEqual(claude_md.read_text(encoding="utf-8"), PRIOR_RULES)

    def test_second_apply_proceeds_and_leaves_the_first_backup_alone(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text(PRIOR_RULES, encoding="utf-8")

        self.assertEqual(self.run_cli("apply").returncode, 0)

        (self.rules / "misc.md").write_text(revised_universal("TWO"), encoding="utf-8")

        # The path is our own link by now, so there is nothing irreplaceable to
        # preserve and the run has no reason to stop. This is what keeps apply
        # re-runnable while the hand-built rules stay protected.
        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)

        self.assertIn("Revision TWO.", claude_md.read_text(encoding="utf-8"))
        self.assertEqual(self.backup_of(claude_md).read_text(encoding="utf-8"), PRIOR_RULES)
        self.assertEqual(self.sandbox_backups(), [self.backup_of(claude_md)])

    def test_every_target_is_a_link_to_one_assembled_file(self):
        self.write_config(agents=["claude", "codex", "cursor"])

        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)

        assembled = airules.assembled_path()
        self.assertTrue(assembled.is_file())

        wrote = self.wrote_paths(result.stdout)
        self.assertEqual(len(wrote), 3)

        # Links, not copies: one file holds the rules and the agent paths point
        # at it, so they cannot drift and the local rules land on disk once.
        for path in wrote:
            self.assertTrue(path.is_symlink(), f"{path} is not a symlink")
            self.assertEqual(path.resolve(), assembled.resolve())

    def test_a_foreign_link_is_repointed_and_its_contents_kept(self):
        elsewhere = self.home / "some_repo" / "claude.md"
        elsewhere.parent.mkdir(parents=True)
        elsewhere.write_text("# TRACKED ELSEWHERE\n", encoding="utf-8")

        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.symlink_to(elsewhere)

        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)

        # Repointed at ours, and what it used to reach is preserved, because a
        # link we did not make is as irreplaceable as a regular file
        self.assertEqual(claude_md.resolve(), airules.assembled_path().resolve())
        self.assertEqual(self.backup_of(claude_md).read_text(encoding="utf-8"), "# TRACKED ELSEWHERE\n")
        self.assertEqual(elsewhere.read_text(encoding="utf-8"), "# TRACKED ELSEWHERE\n")

    def test_paste_notice_fires_once_and_only_for_cursor(self):
        self.write_config(agents=["claude", "codex", "cursor"])

        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)

        notices = [line for line in result.stdout.splitlines() if "Cursor > Settings" in line]

        # One agent reads its rules out of a settings UI. Telling the other two
        # to paste theirs in would send the user to a screen that ignores them.
        self.assertEqual(len(notices), 1, result.stdout)
        self.assertIn(str(self.xdg / "ai-notes" / "cursor-user-rules.txt"), notices[0])

    def test_non_ascii_rules_survive_an_ascii_locale_run(self):
        # All three are needed to actually get an ASCII default. LC_ALL=C alone
        # still yields UTF-8: macOS turns UTF-8 mode on by default, and Linux
        # coerces the C locale to C.UTF-8 (PEP 538). Without these the test runs
        # green against an unpinned encoding and proves nothing.
        for name, value in (("LC_ALL", "C"), ("PYTHONUTF8", "0"), ("PYTHONCOERCECLOCALE", "0")):
            os.environ[name] = value
            self.addCleanup(os.environ.pop, name, None)

        body = "# Universal\n\nEm dash — and a bullet •\n"
        (self.rules / "misc.md").write_text(body, encoding="utf-8")

        # The rules are full of em dashes, and cron and systemd on the VMs run
        # with no locale set, where an unpinned encoding falls back to ASCII
        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)

        self.assertIn("Em dash — and a bullet •",
                      airules.assembled_path().read_text(encoding="utf-8"))

    def test_backups_land_in_the_shared_dotfiles_backup_directory(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text(PRIOR_RULES, encoding="utf-8")

        self.assertEqual(self.run_cli("apply").returncode, 0)

        # One place to look, the same one install.sh uses. Nothing beside the
        # rules file — a `.bak` sibling is exactly what people fail to find.
        backups = self.sandbox_backups()
        self.assertEqual(len(backups), 1, backups)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), PRIOR_RULES)
        self.assertIn(airules.BACKUP_DIRNAME, str(backups[0]))
        self.assertFalse((claude_md.parent / "CLAUDE.md.bak").exists())

    def test_backup_mirrors_the_path_it_came_from(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text(PRIOR_RULES, encoding="utf-8")

        self.run_cli("apply")

        # Mirrored rather than flattened to the basename, so it is obvious where
        # the file came from and two same-named files cannot collide in here
        self.assertTrue(str(self.sandbox_backups()[0]).endswith("/.claude/CLAUDE.md"))

    def test_two_runs_that_both_back_up_do_not_collide(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text(PRIOR_RULES, encoding="utf-8")

        self.assertEqual(self.run_cli("apply").returncode, 0)

        # Put a hand-written file back, so the next run has something to preserve
        claude_md.unlink()
        claude_md.write_text("# second hand-built file\n", encoding="utf-8")

        # A fixed `.bak` name would have to choose between them, which is the
        # whole reason the old code refused to run. Separate directories cannot.
        self.assertEqual(self.run_cli("apply", **{"DOTFILES_BACKUP_DIR": str(self.home / airules.BACKUP_DIRNAME / "second")}).returncode, 0)

        bodies = sorted(b.read_text(encoding="utf-8") for b in self.sandbox_backups())
        self.assertEqual(bodies, sorted([PRIOR_RULES, "# second hand-built file\n"]))

    def test_honours_an_exported_backup_directory(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text(PRIOR_RULES, encoding="utf-8")

        shared = self.home / airules.BACKUP_DIRNAME / "20260101-000000"
        self.assertEqual(self.run_cli("apply", **{"DOTFILES_BACKUP_DIR": str(shared)}).returncode, 0)

        # install.sh exports its own directory so one install run collects both
        # its backups and ours under a single timestamp
        self.assertEqual((shared / ".claude" / "CLAUDE.md").read_text(encoding="utf-8"), PRIOR_RULES)

    def test_backup_notice_names_the_real_path_once_per_target(self):
        self.write_config(agents=["claude", "codex"])

        for relpath in ((".claude", "CLAUDE.md"), (".codex", "AGENTS.md")):
            path = self.home.joinpath(*relpath)
            path.parent.mkdir(parents=True)
            path.write_text("SENTINEL\n", encoding="utf-8")

        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)

        noticed = self.backup_notices(result.stdout)

        self.assertEqual(noticed, [self.backup_of(path) for path in self.wrote_paths(result.stdout)])
        for path in noticed:
            self.assertTrue(path.is_file(), "%s was named in a notice but does not exist" % path)

    def test_failures_before_the_write_leave_no_backup(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)

        modules = self.rules
        locals_ = self.fake_ai / "local_rules"

        def blank_every_layer():
            """Leave every module and every private file present but empty."""
            for path in list(modules.glob("*.md")) + list(locals_.glob("*.md")):
                path.write_text("", encoding="utf-8")

        def strip_private_and_blank_modules():
            """Leave no private rules and no module text, so nothing assembles."""
            blank_every_layer()
            for stale in locals_.glob("*.md"):
                stale.unlink()

        # Every failure apply_rules raises before opening a target. Reaching the
        # backup step on any of them would mean a target was opened after all.
        cases = (
            ("no layers at all",     strip_private_and_blank_modules),
            ("all layers empty",     blank_every_layer),
            ("selected module gone", lambda: (modules / "daily-notes.md").unlink()),
            ("no known agents",      lambda: self.write_config(agents=["claud", "codexx"])),
            ("bad agents setting",   lambda: self.write_config(agents=None)),
        )

        for label, break_it in cases:
            with self.subTest(case=label):
                # Restored first so each case fails for its own reason, not for
                # the damage the previous one left behind
                self.write_module(modules, "universal.md",   TOOL_RULES,  front="order=10, required")
                self.write_module(modules, "daily-notes.md", NOTES_RULES, front="order=20, default=on")
                self.write_module(modules, "misc.md",        MISC,        front="order=30, default=off")
                (locals_ / "10-first.md").write_text("LOCAL RULE ONE\n", encoding="utf-8")
                claude_md.write_text(PRIOR_RULES, encoding="utf-8")
                self.write_config(agents=["claude"])
                self.set_modules(daily_notes=True, misc=True)


                break_it()

                result = self.run_cli("apply")

                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertEqual(claude_md.read_text(encoding="utf-8"), PRIOR_RULES)
                self.assertEqual(self.sandbox_backups(), [])

    def test_never_touches_real_home(self):
        real_targets   = [self.real_home / ".claude" / "CLAUDE.md",
                          self.real_home / ".codex" / "AGENTS.md"]
        before_files   = {path: file_fingerprint(path) for path in real_targets}
        before_entries = self.real_agent_entries()

        # Every RulesRoot a supported agent resolves against — HOME and the
        # config directory — has to land inside the sandbox, so all three run
        self.write_config(agents=["claude", "codex", "cursor"])

        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)

        wrote = self.wrote_paths(result.stdout)
        self.assertEqual(len(wrote), 3, "expected one wrote line per agent:\n%s" % result.stdout)

        for path in wrote:
            # commonpath, not a string prefix: a sibling directory named like
            # the sandbox with a suffix must not be able to pass as inside it
            shared = Path(os.path.commonpath([str(path), str(self.home)]))

            self.assertEqual(shared, self.home, "%s is outside the sandbox" % path)
            self.assertTrue(path.is_file(), "%s was reported written but does not exist" % path)

        # Nothing new appeared beside the real rules files, and the real rules
        # files themselves were not rewritten
        self.assertEqual(self.real_agent_entries() - before_entries, set())
        for path in real_targets:
            self.assertEqual(file_fingerprint(path), before_files[path], "%s changed" % path)


class TestResolvedPaths(SandboxedTestCase):
    """
    Covers the literal path each supported agent resolves to.
    """

    def test_each_agent_resolves_to_its_documented_path(self):
        resolved = airules.agent_targets(["claude", "codex", "cursor"])

        # Spelled out rather than rebuilt from SUPPORTED_AGENTS, which would
        # move with any edit to the table and confirm nothing. A dropped comma
        # in a one-element relpath, for one, turns the filename into a directory
        # per character and only a literal path catches it.
        self.assertEqual(
            [target.path for target in resolved.targets],
            [
                self.home / ".claude" / "CLAUDE.md",
                self.home / ".codex"  / "AGENTS.md",
                self.xdg  / "ai-notes" / "cursor-user-rules.txt",
            ],
        )

    def test_assembled_file_sits_beside_the_config(self):
        self.assertEqual(airules.assembled_path(), self.xdg / "ai-notes" / "rules.md")


class TestBackupGuard(SandboxedTestCase):
    """
    Covers _back_up's own refusal and its two skips, which apply_rules'
    pre-flight normally reaches first and so cannot exercise.
    """

    @property
    def into(self):
        """
        The backup directory this class's direct _back_up calls file into.

        Args:
            None

        Returns:
            pathlib.Path: a fixed directory under the sandboxed HOME, so a test
            can predict where a backup landed without knowing a timestamp.

        Raises:
            None
        """

        return self.home / airules.BACKUP_DIRNAME / "test-run"

    @property
    def assembled(self):
        """
        The assembled rules file this sandbox's agent paths point at.

        Args:
            None

        Returns:
            pathlib.Path: the sandboxed assembled_path(). Not guaranteed to
            exist — a test that needs it present writes it itself.

        Raises:
            None
        """

        return airules.assembled_path()

    def sandbox_backups_under(self, root):
        """
        List every backup file anywhere under a directory.

        Args:
            root (pathlib.Path): directory to sweep.

        Returns:
            list: [pathlib.Path] every path below `root` whose name ends in
            the backup root, sorted. Empty when none was taken.

        Raises:
            OSError: `root` exists but cannot be walked.
        """

        backups = root / airules.BACKUP_DIRNAME

        return sorted(p for p in backups.rglob("*") if p.is_file()) if backups.is_dir() else []

    def _target(self, body="LIVE RULES\n"):
        """
        Write a rules file to back up, under the sandboxed HOME.

        Args:
            body (str): contents to give the file.

        Returns:
            pathlib.Path: the file that was written.

        Raises:
            OSError: the file or its directory cannot be written.
        """

        path = self.home / ".claude" / "CLAUDE.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")

        return path

    def test_takes_the_backup_when_nothing_is_in_the_way(self):
        path   = self._target()
        backup = airules._back_up(path, self.assembled, self.into)

        self.assertEqual(backup, airules.backup_path(path, self.into))
        self.assertEqual(backup.read_text(encoding="utf-8"), "LIVE RULES\n")

    def test_skips_our_own_link_so_a_rerun_is_not_blocked(self):
        path = self.home / ".claude" / "CLAUDE.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        self.assembled.parent.mkdir(parents=True, exist_ok=True)
        self.assembled.write_text("ASSEMBLED\n", encoding="utf-8")
        path.symlink_to(self.assembled)

        # A link of ours holds a pointer, not rules. Backing it up would save
        # nothing and would then block every apply after the first.
        self.assertIsNone(airules._back_up(path, self.assembled, self.into))
        self.assertEqual(self.sandbox_backups_under(self.home), [])

    def test_backs_up_a_foreign_link_before_repointing_it(self):
        elsewhere = self.home / "dotfiles_copy.md"
        elsewhere.write_text("SOMEONE ELSE'S RULES\n", encoding="utf-8")

        path = self.home / ".claude" / "CLAUDE.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(elsewhere)

        # Not ours, so its contents are as irreplaceable as a regular file's
        backup = airules._back_up(path, self.assembled, self.into)
        self.assertEqual(backup.read_text(encoding="utf-8"), "SOMEONE ELSE'S RULES\n")


if __name__ == "__main__":
    unittest.main()
