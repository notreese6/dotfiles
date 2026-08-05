import os
import subprocess
import unittest
from base import SandboxedTestCase
import airules

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
        self.write_module(self.rules, "misc.md",        MISC,        front="order=30, default=off")
        # This module declares default=on, so it is selected on every run
        # here; leaving it out is now a hard failure rather than a silent skip.
        self.write_module(self.rules, "daily-notes.md", NOTES_RULES, front="order=20, default=on")

        (self.fake_ai / "bin").mkdir()
        for name in ("ai-rules", "ai-setup", "daily-notes-sync"):
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

        for name in ("ai-rules", "ai-setup", "daily-notes-sync"):
            link = self.bin_dir() / name
            self.assertTrue(link.is_symlink(), f"{name} was not linked")
            self.assertEqual(link.resolve(), (self.repo / "ai" / "bin" / name).resolve())

    def test_the_linked_sync_tool_actually_runs(self):
        self.assertEqual(self.run_install("ai").returncode, 0)

        # A symlink that exists but points at something unexecutable is a link
        # in name only, and the failure would not show until someone needed it
        result = subprocess.run([str(self.bin_dir() / "daily-notes-sync"), "--help"],
                                capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("daily-notes", result.stdout)

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

    def test_each_target_is_asked_about_and_names_what_it_replaces(self):
        (self.home / ".vimrc").write_text('" my own vimrc\n', encoding="utf-8")

        # Bare run, so every target is asked about. "n" to all of them, so
        # nothing here can touch a file.
        out = self.run_install_on_a_terminal(answer="n\n" * 8)

        for target in ("tmux", "vim", "bash", "ai"):
            self.assertIn(f"? {target} [", out, f"{target} was never asked about")

        # Named before the question, not after the answer. The point is to
        # decide knowing what it costs.
        self.assertIn("~/.vimrc", out)
        self.assertLess(out.index("~/.vimrc"), out.index("? vim ["))

    def test_declining_a_target_leaves_its_files_completely_alone(self):
        vimrc = self.home / ".vimrc"
        vimrc.write_text('" my own vimrc\n', encoding="utf-8")

        self.run_install_on_a_terminal(answer="n\n" * 8)

        self.assertFalse(vimrc.is_symlink())
        self.assertEqual(vimrc.read_text(encoding="utf-8"), '" my own vimrc\n')

    def test_a_declined_target_is_remembered_and_defaults_to_no(self):
        self.run_install_on_a_terminal(answer="n\n" * 8)

        self.assertIs(airules.Config.load().targets.get("vim"), False)

        # A re-run must not quietly re-ask as though the answer were yes: the
        # bracket capital is the only thing telling you what enter will do.
        out = self.run_install_on_a_terminal(answer="\n" * 8)
        self.assertIn("? vim [y/N]", out)

    def test_naming_a_target_skips_the_question_entirely(self):
        # `./install.sh vim` has already said which one you want. Asking again
        # is a question with one sensible answer, and those teach people to
        # stop reading the ones that matter.
        out = self.run_install_on_a_terminal("vim", answer="\n" * 4)

        self.assertNotIn("? vim [", out)
        self.assertTrue((self.home / ".vimrc").is_symlink())

    def test_one_target_answer_does_not_leak_into_the_next(self):
        for name in (".tmux.conf", ".vimrc", ".bashrc"):
            (self.home / name).write_text(f"# my {name}\n", encoding="utf-8")

        # no to the AUTORUN machine-role question, then:
        # yes to tmux, no to vim, yes to bash, yes to ai
        self.run_install_on_a_terminal(answer="n\ny\nn\ny\ny\n" + "\n" * 6)

        self.assertTrue((self.home / ".tmux.conf").is_symlink())
        self.assertFalse((self.home / ".vimrc").is_symlink())
        self.assertTrue((self.home / ".bashrc").is_symlink())

    def test_accepting_a_target_does_not_ask_again_per_file(self):
        (self.home / ".bashrc").write_text("# my bashrc\n", encoding="utf-8")

        out = self.run_install_on_a_terminal(answer="y\n" * 8)

        # The target question already named this exact file. A second prompt
        # that always follows the first is one people learn to mash through —
        # and it shifted every later answer onto the wrong target.
        self.assertNotIn("replace " + str(self.home / ".bashrc"), out)
        self.assertTrue((self.home / ".bashrc").is_symlink())

    def test_a_replaced_file_still_reaches_the_backup(self):
        (self.home / ".bashrc").write_text("# irreplaceable\n", encoding="utf-8")

        self.run_install_on_a_terminal(answer="y\n" * 8)

        saved = [p for p in (self.home / ".dotfiles-backup").rglob(".bashrc")]
        self.assertTrue(saved, "the replaced bashrc was not backed up")
        self.assertEqual(saved[0].read_text(encoding="utf-8"), "# irreplaceable\n")

    def test_the_file_list_a_target_announces_is_the_list_it_installs(self):
        out = self.run_install_on_a_terminal("bash", answer="\n" * 4)

        # Both come from links_for(), so a file added to one is added to the
        # other. Asserting it here is what stops that ever being two lists.
        for name in (".bashrc", ".bash_profile"):
            self.assertTrue((self.home / name).is_symlink(), f"{name} was not installed")

    def test_a_stored_no_is_honoured_when_nobody_is_there_to_ask(self):
        vimrc = self.home / ".vimrc"
        vimrc.write_text('" my own vimrc\n', encoding="utf-8")

        self.run_install_on_a_terminal(answer="n\n" * 8)
        self.assertIs(airules.Config.load().targets.get("vim"), False)

        # The unattended re-run is the dangerous one: provisioning, a cron, or
        # anyone piping into this. Forgetting the stored answer there would
        # install over a file the user has already explicitly refused.
        self.run_install()

        self.assertFalse(vimrc.is_symlink())
        self.assertEqual(vimrc.read_text(encoding="utf-8"), '" my own vimrc\n')

    def test_a_stored_yes_still_installs_when_nobody_is_there_to_ask(self):
        self.run_install_on_a_terminal(answer="y\n" * 8)
        self.assertIs(airules.Config.load().targets.get("vim"), True)

        (self.home / ".vimrc").unlink()
        self.run_install()

        # The stored answer has to work both ways, or "remembered" would just
        # mean "disabled forever"
        self.assertTrue((self.home / ".vimrc").is_symlink())

    def test_files_we_already_own_are_not_listed_as_replacements(self):
        self.run_install_on_a_terminal(answer="y\n" * 8)
        self.assertTrue((self.home / ".bashrc").is_symlink())

        out = self.run_install_on_a_terminal(answer="y\n" * 8)

        # Second run: everything is already our symlink, so nothing is at risk.
        # Listing them anyway makes the warning fire on every routine re-run,
        # and a warning that always fires is one nobody reads.
        self.assertNotIn("replaces these", out)

    def test_a_broken_symlink_of_the_users_is_still_announced(self):
        vimrc = self.home / ".vimrc"
        vimrc.symlink_to(self.home / "somewhere-that-does-not-exist")

        out = self.run_install_on_a_terminal(answer="n\n" * 8)

        # -e is false for a dangling link, so a check on -e alone would miss it.
        # It is still something of theirs pointing somewhere they chose, and
        # replacing it unannounced is the same loss as replacing a real file.
        self.assertIn("~/.vimrc", out)
        self.assertLess(out.index("~/.vimrc"), out.index("? vim ["))

    def test_an_already_installed_target_says_so_rather_than_nothing_is_there(self):
        # Install it, so every destination is our own symlink.
        self.run_install_on_a_terminal("vim", answer="\n" * 4)
        self.assertTrue((self.home / ".vimrc").is_symlink())

        out = self.run_install_on_a_terminal(answer="n\n" * 8)

        # "nothing of yours is there to replace" reads as "the file does not
        # exist", which is flatly wrong about a working symlink — and it is the
        # steady state, so it is the message seen most often.
        self.assertIn("already installed from this repo", out)
        self.assertNotIn("no vim config", out)

    def test_a_target_with_nothing_installed_does_not_claim_it_is_installed(self):
        out = self.run_install_on_a_terminal(answer="n\n" * 8)

        self.assertIn("nothing of yours would be replaced", out)
        self.assertNotIn("already installed from this repo", out)

    def test_a_partly_installed_target_claims_neither(self):
        # tmux owns three files. Install them, then remove one, which is the
        # mixed state: some ours, some absent, none of them theirs.
        self.run_install_on_a_terminal("tmux", answer="\n" * 4)
        (self.home / ".tmux" / "scripts" / "clip.sh").unlink()

        out = self.run_install_on_a_terminal(answer="n\n" * 8)

        # Saying "you have no tmux config" here would be untrue, and saying
        # "already installed" would be too. Both claims are about presence; the
        # question the reader has is what they lose, and the answer is nothing.
        self.assertIn("nothing of yours would be replaced", out)

    def test_an_already_ours_link_is_recognised_through_a_symlinked_repo_path(self):
        import os

        # A repo reached by a symlinked path spells its own files differently
        # from what readlink reports — on macOS /var vs /private/var does this
        # to every temp directory. Compared as raw strings, files we installed
        # ourselves come back as "these are YOURS and get replaced".
        alias = self.home / "repo-alias"
        os.symlink(self.repo, alias)

        self.run_install_on_a_terminal("vim", answer="\n" * 4)
        vimrc = self.home / ".vimrc"
        vimrc.unlink()
        vimrc.symlink_to(alias / "vim" / "vimrc")

        out = self.run_install_on_a_terminal(answer="n\n" * 8)

        self.assertNotIn("~/.vimrc", out)
        self.assertIn("already installed from this repo", out)

    def test_everything_at_risk_is_listed_before_the_first_question(self):
        for name, body in ((".vimrc", '" mine\n'), (".bashrc", "# mine\n")):
            (self.home / name).write_text(body, encoding="utf-8")

        out = self.run_install_on_a_terminal(answer="n\n" * 8)

        # The per-target lists come at each decision; this is the whole picture,
        # which is what you want before answering the first one.
        head = out[:out.index("? tmux")]
        self.assertIn("would be replaced if you say yes to everything", head)
        self.assertIn("~/.vimrc", head)
        self.assertIn("~/.bashrc", head)

    def test_the_agent_rules_files_are_mentioned_up_front_too(self):
        out = self.run_install_on_a_terminal(answer="n\n" * 8)

        # They are not in any target's link list — the ai target links three
        # commands and ai-setup writes these — so an up-front list built only
        # from those lists would omit the file that matters most.
        head = out[:out.index("? tmux")]
        self.assertIn("CLAUDE.md", head)
        self.assertIn("append", head)

    def test_the_ai_target_says_what_the_three_commands_do(self):
        out = self.run_install_on_a_terminal(answer="n\n" * 8)

        # "AI rules tooling" says nothing a reader can decide on
        self.assertIn("ai-rules", out)
        self.assertIn("daily-notes-sync", out)
        self.assertIn("your AI agents read", out)

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

        self.assertIn("Targets: vim", result.stdout)
        self.assertIn("--dry-run", result.stdout)

    def test_the_header_says_whose_config_this_is(self):
        result = self.run_install("--dry-run")

        # Someone cloning this needs to know before the first prompt that these
        # are notreese's own preferences, not a neutral setup script. "Installing
        # tmux" reads as installing the program; it does neither.
        self.assertIn("notreese's dotfiles", result.stdout)
        self.assertIn("YOURS", result.stdout)

    def test_the_prompt_says_replace_rather_than_install(self):
        out = self.run_install_on_a_terminal(answer="n\n" * 8)

        for target in ("tmux", "vim", "bash"):
            self.assertIn(f"replace your {target} config with this repo's", out)

        # And the ai target is described by what it installs, since "AI rules
        # tooling" is not something a reader can decide on. Asserted by naming
        # the commands rather than counting them — the count changed the first
        # time a fifth was added and broke this test for no reason.
        for command in ("ai-rules", "ai-setup", "daily-notes-sync", "ai-hooks"):
            self.assertIn(command, out)

    def test_personal_targets_are_off_unless_asked_for(self):
        out = self.run_install_on_a_terminal(answer="\n" * 8)

        # Enter at every prompt must leave someone else's machine as it was.
        # These are notreese's preferences; the default cannot be to take them.
        for target in ("tmux", "vim", "bash"):
            self.assertIn(f"? {target} [y/N]", out)
        self.assertIn("? ai [Y/n]", out)

    def test_the_tmux_hint_is_not_shown_when_tmux_was_declined(self):
        out = self.run_install_on_a_terminal(answer="n\n" * 8)

        # A next step for something just declined reads as though it happened
        self.assertNotIn("prefix + I", out)

    def test_the_tmux_hint_is_shown_when_tmux_was_installed(self):
        out = self.run_install_on_a_terminal("tmux", answer="\n" * 4)

        self.assertIn("prefix + I", out)

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

        # Prompt order: the backup directory first (it is asked at the top of the
        # script), then the AUTORUN machine-role question, then the replace
        # confirmation. A bare word for the backup used to become a path relative
        # to the working directory, i.e. the repo.
        self.run_install_on_a_terminal("vim", answer="mybackups\nn\ny\n",
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
