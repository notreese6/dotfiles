import os
import subprocess
import unittest
from base import SandboxedTestCase

NOTES_RULES = "## Daily notes\n\nNOTES_MARKER: pull before writing notes.\n"

TOOL_RULES = '# Using these rules\n\nTOOL_MARKER: edit the repo, never the live file.\n'

MISC = "# Misc Rules\n\nAlways be concise.\n"


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

        # AI_DIR rather than the repo's ai/, so these tests assert against
        # fixtures they control rather than against whatever the real rule
        # modules happen to say today.
        self.fake_ai = self.home / "aifix"
        (self.fake_ai / "local_rules").mkdir(parents=True)
        self.rules = self.fake_ai / "rules"
        self.write_module(self.rules, "universal.md",   TOOL_RULES,  front="order=10, required")
        self.write_module(self.rules, "misc.md",        MISC,        front="order=30, default=off, clobbers")
        # This module declares default=on, so it is selected on every run
        # here; leaving it out is now a hard failure rather than a silent skip.
        self.write_module(self.rules, "daily-notes.md", NOTES_RULES, front="order=20, default=on")

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
        env.setdefault("AI_SETUP_UNIVERSAL", "yes")
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
        text = claude_md.read_text(encoding="utf-8")

        # The tool module and the notes module, because those are the two an
        # unattended install ends up with: one has no switch, the other defaults
        # on. The misc module is off unless someone answers yes, so asserting on
        # it here would be asserting the opposite of the intended default.
        self.assertIn("TOOL_MARKER", text)
        self.assertIn("NOTES_MARKER", text)
        self.assertNotIn("End of misc.", text)

    def test_rerun_is_idempotent(self):
        self.assertEqual(self.run_install("ai").returncode, 0)

        result = self.run_install("ai")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        # The second run must not trip over its own symlinks, its own config, or
        # the backup the first run took of whatever was there before
        self.assertTrue((self.bin_dir() / "ai-rules").is_symlink())
        self.assertTrue((self.home / ".claude" / "CLAUDE.md").is_symlink())

    def test_reports_failure_when_setup_cannot_finish(self):
        # Nothing to assemble at all, so ai-rules refuses and ai-setup passes
        # that up. Emptied rather than deleted, because the modules directory is
        # globbed: a deleted module is simply not discovered, while an emptied
        # one is discovered and contributes nothing.
        for module in self.rules.glob("*.md"):
            module.write_text("", encoding="utf-8")
        for private in (self.fake_ai / "local_rules").glob("*.md"):
            private.unlink()

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

    def run_install_on_a_terminal(self, *args, answer="n\n", **overrides):
        """
        Run install.sh with a real pty on stdin, so its prompts fire.

        The confirmation is skipped when stdin is not a terminal, which every
        other test here relies on. Exercising it therefore needs an actual
        terminal rather than a pipe.

        Args:
            *args (str): arguments after the script name.
            answer (str): what to type at each prompt, newline included.
            **overrides (str): environment variables to set, or remove when None.

        Returns:
            str: everything the script wrote to the terminal, decoded.

        Raises:
            OSError: a pty cannot be allocated, or install.sh cannot be run.
        """

        import pty

        parent, child = pty.openpty()
        env = dict(os.environ)
        env["AI_DIR"]                   = str(self.fake_ai)
        env["AI_SETUP_NONINTERACTIVE"]  = "true"
        env["AI_SETUP_AGENTS"]          = "claude"
        env["AI_SETUP_LOCAL_RULES_DIR"] = str(self.fake_ai / "local_rules")
        env.setdefault("AI_SETUP_UNIVERSAL", "yes")
        env.setdefault("AI_SETUP_BACKUP_DIR", str(self.home / ".dotfiles-backup"))

        for key, value in overrides.items():
            if value is None:
                env.pop(key, None)
            else:
                env[key] = value

        proc = subprocess.Popen(
            ["./install.sh", *args], cwd=str(self.repo), env=env,
            stdin=child, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        os.close(child)
        os.write(parent, (answer * 12).encode())

        out, _ = proc.communicate(timeout=120)
        os.close(parent)

        return out.decode(errors="replace")

    def test_declining_the_prompt_keeps_the_existing_file(self):
        vimrc = self.home / ".vimrc"
        vimrc.write_text("\" my own vimrc\n", encoding="utf-8")

        output = self.run_install_on_a_terminal("vim", answer="n\n")

        # The whole point: someone with their own vimrc gets to keep it
        self.assertEqual(vimrc.read_text(encoding="utf-8"), "\" my own vimrc\n")
        self.assertFalse(vimrc.is_symlink())
        self.assertIn("kept your existing", output)

    def test_accepting_the_prompt_replaces_and_backs_up(self):
        vimrc = self.home / ".vimrc"
        vimrc.write_text("\" my own vimrc\n", encoding="utf-8")

        self.run_install_on_a_terminal("vim", answer="y\n")

        self.assertTrue(vimrc.is_symlink())

        # Saying yes still has to preserve what was there
        backups = list((self.home / ".dotfiles-backup").rglob(".vimrc"))
        self.assertEqual(len(backups), 1, backups)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "\" my own vimrc\n")

    def test_non_interactive_run_does_not_stall_waiting_for_input(self):
        (self.home / ".vimrc").write_text("\" my own vimrc\n", encoding="utf-8")

        # Provisioning and CI pipe or close stdin. A prompt there would hang the
        # run forever rather than fail, which is the worse failure.
        result = self.run_install("vim")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.home / ".vimrc").is_symlink())

    def test_yes_flag_skips_the_prompt_on_a_terminal(self):
        vimrc = self.home / ".vimrc"
        vimrc.write_text("\" my own vimrc\n", encoding="utf-8")

        # Answering n, but --yes should mean nothing is asked in the first place
        output = self.run_install_on_a_terminal("vim", "--yes", answer="n\n")

        self.assertTrue(vimrc.is_symlink())
        self.assertNotIn("kept your existing", output)

    def test_plan_names_the_targets_before_doing_anything(self):
        result = self.run_install("vim", "--dry-run")

        self.assertIn("Installing: vim", result.stdout)
        self.assertIn("--dry-run", result.stdout)

    def test_summary_counts_backups_from_both_tools(self):
        (self.home / ".vimrc").write_text("\" my vimrc\n", encoding="utf-8")
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text("# my hand-built rules\n", encoding="utf-8")

        result = self.run_install("vim", "ai")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        # ai-rules backs up in a child process, so a counter kept in install.sh's
        # own shell reports one file when two were moved
        moved = [p for p in (self.home / ".dotfiles-backup").rglob("*") if p.is_file()]
        self.assertEqual(len(moved), 2, moved)
        self.assertIn(f"{len(moved)} file(s) of yours were moved", result.stdout)

    def test_summary_says_so_when_nothing_was_replaced(self):
        result = self.run_install("vim")
        self.assertEqual(result.returncode, 0, result.stderr)

        # The old line printed the backup path unconditionally, pointing at a
        # directory that was never created
        self.assertIn("no backup was needed", result.stdout)
        self.assertFalse((self.home / ".dotfiles-backup").exists())

    def test_both_tools_share_one_timestamped_directory(self):
        (self.home / ".vimrc").write_text("\" my vimrc\n", encoding="utf-8")
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text("# my hand-built rules\n", encoding="utf-8")

        self.run_install("vim", "ai")

        root = self.home / ".dotfiles-backup"
        runs = {p.relative_to(root).parts[0] for p in root.rglob("*") if p.is_file()}

        # One install, one directory — install.sh exports it so ai-rules files
        # into the same place instead of making its own
        self.assertEqual(len(runs), 1, runs)

    def test_a_relative_backup_answer_is_anchored_under_home(self):
        (self.home / ".vimrc").write_text("\" mine\n", encoding="utf-8")

        # Snapshotted rather than asserting the repo is clean outright: a
        # previous run that exercised this bug leaves a directory behind, and a
        # test that fails on someone else's litter is a test people learn to
        # ignore. Only what THIS run creates is the test's business.
        before = {p.name for p in self.repo.iterdir()}

        # First prompt is the backup directory, second is the replace
        # confirmation. A bare word here used to become a path relative to the
        # working directory, which is the repo.
        self.run_install_on_a_terminal("vim", answer="mybackups\ny\n",
                                       AI_SETUP_BACKUP_DIR=None)

        self.assertTrue((self.home / "mybackups").is_dir())
        self.assertEqual({p.name for p in self.repo.iterdir()} - before, set())

    def test_backup_mirrors_a_nested_path_rather_than_flattening_it(self):
        # A nested source is the only thing that can tell mirroring from
        # flattening apart — ~/.vimrc is identical either way, which is why
        # every other backup test here passes with the bug present.
        clip = self.home / ".tmux" / "scripts" / "clip.sh"
        clip.parent.mkdir(parents=True)
        clip.write_text("# my clip script\n", encoding="utf-8")

        # Stops install_tmux cloning TPM from GitHub during the test
        (self.home / ".tmux" / "plugins" / "tpm").mkdir(parents=True)

        result = self.run_install("tmux")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        kept = [p for p in (self.home / ".dotfiles-backup").rglob("clip.sh") if p.is_file()]
        self.assertEqual(len(kept), 1, kept)

        # Flattening puts every backup in one directory, so two files sharing a
        # basename overwrite each other in the place you go when something broke
        self.assertTrue(str(kept[0]).endswith("/.tmux/scripts/clip.sh"), kept[0])

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
