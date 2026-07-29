import hashlib
import os
import subprocess
import unittest
from pathlib import Path
from base import SandboxedTestCase
import airules

UNIVERSAL = (
    "# Universal Rules\n\nAlways be concise.\n\n"
    + airules.NOTES_BEGIN
    + "\nNOTES SYNC: pull before writing notes.\n"
    + airules.NOTES_END
    + "\n\nEnd of universal.\n"
)

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
        (self.fake_ai / "AGENTS.md").write_text(UNIVERSAL, encoding="utf-8")
        (self.fake_ai / "local_rules" / "10-first.md").write_text("LOCAL RULE ONE\n", encoding="utf-8")
        (self.fake_ai / "local_rules" / "20-second.md").write_text("LOCAL RULE TWO\n", encoding="utf-8")

        airules.config_set("local_rules_dir", str(self.fake_ai / "local_rules"))
        airules.config_set("agents", ["claude"])
        airules.config_set("notes_enabled", False)

    def run_cli(self, *args):
        """
        Run the ai-rules script in a subprocess against the sandbox.

        Args:
            *args (str): command-line arguments passed after the script name.

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
            airules.BACKUP_SUFFIX, sorted. Empty when no backup was taken.

        Raises:
            OSError: the sandbox exists but cannot be walked.
        """

        return sorted(self.home.rglob("*" + airules.BACKUP_SUFFIX))

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
        # to mention a backup cannot be read as the notice itself. The path sits
        # mid-sentence, so it is cut at the em dash the rest of the line opens
        # with rather than run to the end.
        prefix = "[*] the rules that were there are saved at "

        return [Path(line[len(prefix):].split(" — ", 1)[0])
                for line in stdout.splitlines() if line.startswith(prefix)]

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

    def test_notes_enabled_keeps_nudge(self):
        airules.config_set("notes_enabled", True)
        self.run_cli("apply")
        self.assertIn("NOTES SYNC", (self.home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8"))

    def test_rerun_is_idempotent(self):
        self.run_cli("apply")
        first = (self.home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")

        self.run_cli("apply")
        second = (self.home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")

        self.assertEqual(first, second)
        self.assertEqual(second.count(airules.LOCAL_END), 1)

    def test_multiple_agents(self):
        airules.config_set("agents", ["claude", "codex"])
        self.run_cli("apply")
        self.assertTrue((self.home / ".claude" / "CLAUDE.md").exists())
        self.assertTrue((self.home / ".codex" / "AGENTS.md").exists())

    def test_no_local_rules_yields_no_local_block(self):
        for path in (self.fake_ai / "local_rules").glob("*.md"):
            path.unlink()

        self.run_cli("apply")
        self.assertNotIn(airules.LOCAL_END, (self.home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8"))

    def test_missing_universal_fails_clearly(self):
        (self.fake_ai / "AGENTS.md").unlink()

        result = self.run_cli("apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("AGENTS.md", result.stdout + result.stderr)

    def test_unknown_command_exits_nonzero(self):
        self.assertNotEqual(self.run_cli("bogus").returncode, 0)

    def test_string_agents_match_equivalent_list(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"

        airules.config_set("agents", ["claude"])
        self.assertEqual(self.run_cli("apply").returncode, 0)
        from_list = claude_md.read_text(encoding="utf-8")

        claude_md.unlink()

        airules.config_set("agents", "claude")
        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(claude_md.read_text(encoding="utf-8"), from_list)

    def test_string_agents_split_on_whitespace(self):
        airules.config_set("agents", "claude codex")

        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.home / ".claude" / "CLAUDE.md").exists())
        self.assertTrue((self.home / ".codex" / "AGENTS.md").exists())

    def test_unknown_agent_warns_naming_it(self):
        airules.config_set("agents", ["claud"])

        result = self.run_cli("apply")

        # Quoted so the assertion cannot pass on the "claud" inside "claude"
        self.assertIn("'claud'", result.stderr)
        for name in airules.known_agent_names():
            self.assertIn(name, result.stderr)

    def test_all_unknown_agents_exit_nonzero_and_write_nothing(self):
        airules.config_set("agents", ["claud", "codexx"])

        result = self.run_cli("apply")
        self.assertNotEqual(result.returncode, 0)

        for path in self.agent_files():
            self.assertFalse(path.exists(), "%s should not have been written" % path)

    def test_mixed_agents_write_the_valid_one_and_warn(self):
        airules.config_set("agents", ["claude", "bogus"])

        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.home / ".claude" / "CLAUDE.md").exists())
        self.assertIn("'bogus'", result.stderr)

    def test_no_known_agents_exits_3(self):
        airules.config_set("agents", ["claud", "codexx"])

        self.assertEqual(self.run_cli("apply").returncode, 3)

    def test_empty_agents_list_exits_3_and_writes_nothing(self):
        airules.config_set("agents", [])

        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 3, result.stderr)

        for path in self.agent_files():
            self.assertFalse(path.exists(), "%s should not have been written" % path)

    def test_malformed_agents_setting_is_a_config_error(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"

        for value, fragment in MALFORMED_AGENTS:
            with self.subTest(agents=value):
                airules.config_set("agents", value)

                result = self.run_cli("apply")

                self.assertEqual(result.returncode, 4, result.stderr)
                self.assertFalse(claude_md.exists(), "%r should have written nothing" % (value,))

                # The bad value and the usable names both have to be on screen
                self.assertIn(fragment, result.stderr)
                for name in airules.known_agent_names():
                    self.assertIn(name, result.stderr)

    def test_empty_universal_leaves_existing_rules_untouched(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text(PRIOR_RULES, encoding="utf-8")

        # An AGENTS.md truncated to nothing assembles into a rules file with no
        # rules in it, which must never replace the live one
        (self.fake_ai / "AGENTS.md").write_text("", encoding="utf-8")

        result = self.run_cli("apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(claude_md.read_text(encoding="utf-8"), PRIOR_RULES)
        self.assertIn("empty", result.stderr)

    def test_whitespace_only_universal_leaves_existing_rules_untouched(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text(PRIOR_RULES, encoding="utf-8")

        (self.fake_ai / "AGENTS.md").write_text("  \n\n\t\n", encoding="utf-8")

        result = self.run_cli("apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(claude_md.read_text(encoding="utf-8"), PRIOR_RULES)

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
        self.assertEqual(airules.backup_path(claude_md).read_text(encoding="utf-8"), PRIOR_RULES)
        self.assertNotEqual(claude_md.read_text(encoding="utf-8"), PRIOR_RULES)

    def test_second_apply_proceeds_and_leaves_the_first_backup_alone(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text(PRIOR_RULES, encoding="utf-8")

        self.assertEqual(self.run_cli("apply").returncode, 0)

        (self.fake_ai / "AGENTS.md").write_text(revised_universal("TWO"), encoding="utf-8")

        # The path is our own link by now, so there is nothing irreplaceable to
        # preserve and the run has no reason to stop. This is what keeps apply
        # re-runnable while the hand-built rules stay protected.
        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)

        self.assertIn("Revision TWO.", claude_md.read_text(encoding="utf-8"))
        self.assertEqual(airules.backup_path(claude_md).read_text(encoding="utf-8"), PRIOR_RULES)
        self.assertEqual(self.sandbox_backups(), [airules.backup_path(claude_md)])

    def test_a_stale_backup_cannot_block_creating_a_target_that_is_absent(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        airules.backup_path(claude_md).write_text("STALE BACKUP\n", encoding="utf-8")

        # Nothing is there to preserve, so no backup would be taken and none is
        # at risk. Refusing here would wedge the tool over a file it never reads.
        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)

        self.assertTrue(claude_md.is_symlink())
        self.assertEqual(airules.backup_path(claude_md).read_text(encoding="utf-8"), "STALE BACKUP\n")

    def test_refusal_leaves_every_target_untouched_not_just_the_blocked_one(self):
        airules.config_set("agents", ["claude", "codex"])

        targets = {
            self.home / ".claude" / "CLAUDE.md": "CLAUDE SENTINEL\n",
            self.home / ".codex"  / "AGENTS.md": "CODEX SENTINEL\n",
        }

        for path, body in targets.items():
            path.parent.mkdir(parents=True)
            path.write_text(body, encoding="utf-8")

        # Only ONE target is blocked. Without a check that runs across all of them
        # up front, whichever target is written first is already overwritten by
        # the time the blocked one is reached.
        blocked = airules.backup_path(self.home / ".codex" / "AGENTS.md")
        blocked.write_text("EARLIER BACKUP\n", encoding="utf-8")

        result = self.run_cli("apply")
        self.assertEqual(result.returncode, airules.ExitStatus.BACKUP_EXISTS, result.stderr)

        for path, body in targets.items():
            self.assertEqual(path.read_text(encoding="utf-8"), body)

        self.assertEqual(blocked.read_text(encoding="utf-8"), "EARLIER BACKUP\n")
        self.assertEqual(self.sandbox_backups(), [blocked])

    def test_refusal_names_every_blocking_backup(self):
        airules.config_set("agents", ["claude", "codex"])

        blocked = []
        for relpath in ((".claude", "CLAUDE.md"), (".codex", "AGENTS.md")):
            path = self.home.joinpath(*relpath)
            path.parent.mkdir(parents=True)
            path.write_text("SENTINEL\n", encoding="utf-8")
            backup = airules.backup_path(path)
            backup.write_text("EARLIER BACKUP\n", encoding="utf-8")
            blocked.append(backup)

        result = self.run_cli("apply")
        self.assertEqual(result.returncode, airules.ExitStatus.BACKUP_EXISTS)

        # Naming only the first would leave the user clearing one file at a time,
        # rerunning to discover the next
        for backup in blocked:
            self.assertIn(str(backup), result.stderr)

    def test_removing_the_backup_lets_the_next_apply_proceed(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text(PRIOR_RULES, encoding="utf-8")
        backup = airules.backup_path(claude_md)
        backup.write_text("EARLIER BACKUP\n", encoding="utf-8")

        self.assertEqual(self.run_cli("apply").returncode, airules.ExitStatus.BACKUP_EXISTS)

        backup.unlink()

        # Clearing it by hand is the whole documented way forward, so the run
        # after has to both link and take a fresh backup of what it replaced
        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)

        self.assertEqual(backup.read_text(encoding="utf-8"), PRIOR_RULES)
        self.assertTrue(claude_md.is_symlink())

    def test_every_target_is_a_link_to_one_assembled_file(self):
        airules.config_set("agents", ["claude", "codex", "cursor"])

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
        self.assertEqual(airules.backup_path(claude_md).read_text(encoding="utf-8"), "# TRACKED ELSEWHERE\n")
        self.assertEqual(elsewhere.read_text(encoding="utf-8"), "# TRACKED ELSEWHERE\n")

    def test_paste_notice_fires_once_and_only_for_cursor(self):
        airules.config_set("agents", ["claude", "codex", "cursor"])

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
        (self.fake_ai / "AGENTS.md").write_text(body, encoding="utf-8")

        # The rules are full of em dashes, and cron and systemd on the VMs run
        # with no locale set, where an unpinned encoding falls back to ASCII
        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)

        self.assertIn("Em dash — and a bullet •",
                      airules.assembled_path().read_text(encoding="utf-8"))

    def test_backup_notice_names_the_real_path_once_per_target(self):
        airules.config_set("agents", ["claude", "codex"])

        for relpath in ((".claude", "CLAUDE.md"), (".codex", "AGENTS.md")):
            path = self.home.joinpath(*relpath)
            path.parent.mkdir(parents=True)
            path.write_text("SENTINEL\n", encoding="utf-8")

        result = self.run_cli("apply")
        self.assertEqual(result.returncode, 0, result.stderr)

        noticed = self.backup_notices(result.stdout)

        self.assertEqual(noticed, [airules.backup_path(path) for path in self.wrote_paths(result.stdout)])
        for path in noticed:
            self.assertTrue(path.is_file(), "%s was named in a notice but does not exist" % path)

    def test_failures_before_the_write_leave_no_backup(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)

        universal = self.fake_ai / "AGENTS.md"

        # Every failure apply_rules raises before opening a target. Reaching the
        # backup step on any of them would mean a target was opened after all.
        cases = (
            ("missing universal",  lambda: universal.unlink()),
            ("empty universal",    lambda: universal.write_text("", encoding="utf-8")),
            ("no known agents",    lambda: airules.config_set("agents", ["claud", "codexx"])),
            ("bad agents setting", lambda: airules.config_set("agents", None)),
        )

        for label, break_it in cases:
            with self.subTest(case=label):
                # Restored first so each case fails for its own reason, not for
                # the damage the previous one left behind
                universal.write_text(UNIVERSAL, encoding="utf-8")
                claude_md.write_text(PRIOR_RULES, encoding="utf-8")
                airules.config_set("agents", ["claude"])

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
        airules.config_set("agents", ["claude", "codex", "cursor"])

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
            airules.BACKUP_SUFFIX, sorted. Empty when none was taken.

        Raises:
            OSError: `root` exists but cannot be walked.
        """

        return sorted(root.rglob("*" + airules.BACKUP_SUFFIX))

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

    def test_refuses_when_the_backup_is_already_there(self):
        path   = self._target()
        backup = airules.backup_path(path)
        backup.write_text("EARLIER BACKUP\n", encoding="utf-8")

        with self.assertRaises(airules.BackupExistsError) as caught:
            airules._back_up(path, self.assembled)

        self.assertEqual(caught.exception.backups, [backup])
        self.assertEqual(backup.read_text(encoding="utf-8"), "EARLIER BACKUP\n")

    def test_refuses_when_a_directory_holds_the_backup_name(self):
        path = self._target()

        # Not a file, so an is_file() check would wave it through and the write
        # would then fail partway with a bare OSError instead of this refusal
        airules.backup_path(path).mkdir()

        with self.assertRaises(airules.BackupExistsError):
            airules._back_up(path, self.assembled)

    def test_takes_the_backup_when_nothing_is_in_the_way(self):
        path   = self._target()
        backup = airules._back_up(path, self.assembled)

        self.assertEqual(backup, airules.backup_path(path))
        self.assertEqual(backup.read_text(encoding="utf-8"), "LIVE RULES\n")

    def test_skips_our_own_link_so_a_rerun_is_not_blocked(self):
        path = self.home / ".claude" / "CLAUDE.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        self.assembled.parent.mkdir(parents=True, exist_ok=True)
        self.assembled.write_text("ASSEMBLED\n", encoding="utf-8")
        path.symlink_to(self.assembled)

        # A link of ours holds a pointer, not rules. Backing it up would save
        # nothing and would then block every apply after the first.
        self.assertIsNone(airules._back_up(path, self.assembled))
        self.assertEqual(self.sandbox_backups_under(self.home), [])

    def test_backs_up_a_foreign_link_before_repointing_it(self):
        elsewhere = self.home / "dotfiles_copy.md"
        elsewhere.write_text("SOMEONE ELSE'S RULES\n", encoding="utf-8")

        path = self.home / ".claude" / "CLAUDE.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(elsewhere)

        # Not ours, so its contents are as irreplaceable as a regular file's
        backup = airules._back_up(path, self.assembled)
        self.assertEqual(backup.read_text(encoding="utf-8"), "SOMEONE ELSE'S RULES\n")


if __name__ == "__main__":
    unittest.main()
