import json
import os
import subprocess
import unittest
from pathlib import Path
from base import SandboxedTestCase
import airules

NOTES_RULES = "## Daily notes\n\nNOTES_MARKER: pull before writing notes.\n"

TOOL_RULES = '# Using these rules\n\nTOOL_MARKER: edit the repo, never the live file.\n'

MISC = "# Misc Rules\n\nAlways be concise.\n"


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
        self.rules = self.fake_ai / "rules"
        self.write_module(self.rules, "universal.md",   TOOL_RULES,  front="order=10, required")
        self.write_module(self.rules, "misc.md",        MISC,        front="order=30, default=off, clobbers")
        # This module declares default=on, so it is selected on every run
        # here; leaving it out is now a hard failure rather than a silent skip.
        self.write_module(self.rules, "daily-notes.md", NOTES_RULES, front="order=20, default=on")
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
        env.setdefault("AI_SETUP_UNIVERSAL", "yes")
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

    def module_answer(self, stem):
        """
        Read one module's stored answer out of the sandboxed config.

        Args:
            stem (str): the module stem, e.g. "daily-notes".

        Returns:
            bool or None: the stored answer, or None when the module has no
            entry — which is what a question never asked leaves behind.

        Raises:
            ValueError: the config file is not valid JSON.
        """

        return (airules.config_get(airules.CONFIG_KEY_MODULES, {}) or {}).get(stem)

    def test_writes_config_and_assembles(self):
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stderr)

        self.assertEqual(airules.config_get("agents"), ["claude"])
        self.assertIs(self.module_answer("daily-notes"), True)
        self.assertIn("LOCAL RULE ONE", self.claude_rules())

    def test_leaves_the_agent_path_a_link_to_the_assembled_file(self):
        self.assertEqual(self.run_setup().returncode, 0)

        claude_md = self.home / ".claude" / "CLAUDE.md"
        self.assertTrue(claude_md.is_symlink())
        self.assertEqual(claude_md.resolve(), airules.assembled_path().resolve())

    def test_defaults_notes_path_outside_tcc(self):
        self.run_setup(AI_SETUP_MODULE_DAILY_NOTES="yes")
        self.assertEqual(airules.config_get("notes_path"), str(self.home / "daily-notes"))

    def test_notes_path_is_not_asked_when_notes_are_off(self):
        self.run_setup(AI_SETUP_MODULE_DAILY_NOTES="no",
                       AI_SETUP_NOTES_PATH=str(self.home / "somewhere"))

        # Turning notes off has to skip the follow-up entirely: a setting nothing
        # will read should not be recorded from a question never asked
        self.assertIs(self.module_answer("daily-notes"), False)
        self.assertEqual(airules.config_get("notes_path", None), None)

    def test_notes_are_enabled_by_default(self):
        self.run_setup(AI_SETUP_MODULE_DAILY_NOTES=None)

        # A fresh machine keeps notes rather than having to opt in
        self.assertIs(self.module_answer("daily-notes"), True)

    def test_enabling_notes_asks_for_the_path(self):
        self.run_setup(AI_SETUP_MODULE_DAILY_NOTES="yes",
                       AI_SETUP_NOTES_PATH=str(self.home / "somewhere"))

        self.assertIs(self.module_answer("daily-notes"), True)
        self.assertEqual(airules.config_get("notes_path"), str(self.home / "somewhere"))

    def test_warns_when_notes_path_is_tcc_protected(self):
        result = self.run_setup(AI_SETUP_MODULE_DAILY_NOTES="yes",
                                AI_SETUP_NOTES_PATH=str(self.home / "Documents" / "daily-notes"))

        output = result.stdout + result.stderr
        self.assertIn("Documents", output)
        self.assertRegex(output.lower(), r"warn|restrict")

    def test_warns_when_notes_path_is_in_icloud(self):
        icloud = self.home / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "notes"
        result = self.run_setup(AI_SETUP_MODULE_DAILY_NOTES="yes", AI_SETUP_NOTES_PATH=str(icloud))

        # iCloud is TCC-gated the same way but is not one of the three folder
        # names, so it needs its own check rather than falling out of the list
        self.assertRegex((result.stdout + result.stderr).lower(), r"warn|restrict")

    def test_accepts_a_notes_path_outside_the_home_directory(self):
        result = self.run_setup(AI_SETUP_MODULE_DAILY_NOTES="yes", AI_SETUP_NOTES_PATH="/srv/notes")
        self.assertEqual(result.returncode, 0, result.stderr)

        # relative_to() raises for a path outside HOME. Left unhandled that ends
        # the run in a traceback rather than accepting a perfectly good path.
        self.assertEqual(airules.config_get("notes_path"), "/srv/notes")
        self.assertNotRegex((result.stdout + result.stderr).lower(), r"warn|restrict")

    def test_rerun_changes_value(self):
        self.run_setup(AI_SETUP_AGENTS="claude")
        self.run_setup(AI_SETUP_AGENTS="claude codex")

        self.assertEqual(airules.config_get("agents"), ["claude", "codex"])

    def test_a_module_that_clobbers_names_the_files_first(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text("mine\n", encoding="utf-8")

        output = self.run_setup().stdout

        # misc.md declares `clobbers`, so the files it would replace have to be
        # on screen before the question, not described after the answer
        self.assertIn("clobbers these files", output)
        self.assertIn("~/.claude/CLAUDE.md", output)

    def test_no_clobber_warning_when_no_module_declares_one(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text("mine\n", encoding="utf-8")

        # Same file present, but nothing left that replaces it. A warning shown
        # anyway is a warning people learn to scroll past.
        (self.rules / "misc.md").unlink()
        self.set_modules(misc=False)

        self.assertNotIn("clobbers these files", self.run_setup().stdout)

    def test_a_module_dropped_into_the_repo_is_picked_up_with_no_code_change(self):
        self.write_module(self.rules, "security.md",
                          "# Security practice\n\nSECURITY_MARKER: never commit a token.\n",
                          front="order=25, default=on")

        self.assertEqual(self.run_setup().returncode, 0)

        # The whole point of discovery: a file is the entire change. No constant,
        # no config key, no prompt written by hand.
        self.assertIs(self.module_answer("security"), True)
        self.assertIn("SECURITY_MARKER", self.claude_rules())

    def test_a_dropped_in_module_is_asked_about_in_its_declared_position(self):
        self.write_module(self.rules, "security.md", "# Security practice\n\nR\n",
                          front="order=25, default=on")
        self.run_setup()

        asked = list(airules.config_get(airules.CONFIG_KEY_MODULES, {}))

        # Answers are stored in the order the questions were asked, so this is
        # also the assertion that the questions themselves came in module order
        self.assertEqual(asked, ["daily-notes", "security", "misc"])

    def test_a_module_removed_from_the_repo_drops_out_of_the_config(self):
        self.run_setup()
        self.assertIn("misc", airules.config_get(airules.CONFIG_KEY_MODULES, {}))

        (self.rules / "misc.md").unlink()
        self.assertEqual(self.run_setup().returncode, 0)

        # Otherwise the config keeps an answer to a question nobody asks any
        # more, and the next reader cannot tell it is dead
        self.assertNotIn("misc", airules.config_get(airules.CONFIG_KEY_MODULES, {}))

    def test_rerun_keeps_the_notes_answer_when_the_prompt_is_unanswered(self):
        self.run_setup(AI_SETUP_MODULE_DAILY_NOTES="yes")

        # No override: the prompt is pre-filled from the config, so a bare enter
        # re-chooses yes rather than silently turning sync off
        self.run_setup(AI_SETUP_MODULE_DAILY_NOTES=None)

        self.assertIs(self.module_answer("daily-notes"), True)

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

    def test_backup_dir_defaults_to_the_shared_root(self):
        self.run_setup()

        # Same default install.sh uses, so the two agree with no configuration
        self.assertEqual(airules.config_get("backup_dir"), str(self.home / airules.BACKUP_DIRNAME))

    def test_backup_dir_is_configurable(self):
        self.run_setup(AI_SETUP_BACKUP_DIR=str(self.home / "elsewhere"))

        self.assertEqual(airules.config_get("backup_dir"), str(self.home / "elsewhere"))

    def test_a_configured_backup_dir_is_where_backups_land(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True)
        claude_md.write_text("# hand built\n", encoding="utf-8")

        elsewhere = self.home / "elsewhere"
        self.run_setup(AI_SETUP_BACKUP_DIR=str(elsewhere))

        # Configuring it has to actually move the backups, not just record a path
        kept = [p for p in elsewhere.rglob("*") if p.is_file()]
        self.assertEqual(len(kept), 1, kept)
        self.assertEqual(kept[0].read_text(encoding="utf-8"), "# hand built\n")

    def test_pressing_enter_keeps_the_configured_backup_dir(self):
        self.run_setup(AI_SETUP_BACKUP_DIR=str(self.home / "elsewhere"))

        # No override this time: every prompt is pre-filled from the config, so a
        # bare enter re-chooses what is already set rather than resetting it
        self.run_setup(AI_SETUP_BACKUP_DIR=None)

        self.assertEqual(airules.config_get("backup_dir"), str(self.home / "elsewhere"))

    def test_warns_when_the_remote_is_http(self):
        result = self.run_setup(AI_SETUP_LOCAL_RULES_REMOTE="https://example.com/me/rules.git")

        # install.sh runs this with no terminal, so a credential prompt there
        # does not ask — it fails. Worth saying at the moment it is configured.
        self.assertIn("http(s) remote", result.stdout + result.stderr)

    def test_no_warning_for_an_ssh_remote(self):
        origin = self.home / "origin"
        origin.mkdir()
        (origin / "10-rule.md").write_text("REMOTE RULE\n", encoding="utf-8")
        self._git_init(origin)

        result = self.run_setup(AI_SETUP_LOCAL_RULES_REMOTE=str(origin))

        self.assertNotIn("http(s) remote", result.stdout + result.stderr)

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

    def test_the_private_layer_defaults_outside_the_repo_tree(self):
        self.assertEqual(self.run_setup(AI_SETUP_LOCAL_RULES_DIR=None).returncode, 0)

        configured = Path(airules.config_get("local_rules_dir"))

        # Nesting a private repo inside a tracked directory of this one is what
        # let the shipped .gitignore placeholder into the clone, where it
        # ignored every rule the clone existed to carry
        self.assertEqual(configured, airules.default_local_rules_dir())
        self.assertNotIn(str(self.fake_ai), str(configured))

    def test_a_clone_outside_the_repo_can_track_its_own_rules(self):
        origin = self.home / "origin"
        origin.mkdir()
        (origin / "50-from-remote.md").write_text("REMOTE RULE\n", encoding="utf-8")
        self._git_init(origin)

        # The placeholder that ships the in-repo directory. It must not end up
        # inside the clone: `*` plus `!.gitignore` there ignores every rule file.
        (self.fake_ai / "local_rules").mkdir(parents=True, exist_ok=True)
        (self.fake_ai / "local_rules" / ".gitignore").write_text("*\n!.gitignore\n", encoding="utf-8")

        self.assertEqual(self.run_setup(AI_SETUP_LOCAL_RULES_REMOTE=str(origin),
                                        AI_SETUP_LOCAL_RULES_DIR=None).returncode, 0)

        cloned = airules.default_local_rules_dir()
        self.assertIn("REMOTE RULE", self.claude_rules())

        # The real regression: add a rule to the cloned repo and it must be
        # trackable. With the placeholder inside, git reported it as ignored.
        (cloned / "60-mine.md").write_text("MY RULE\n", encoding="utf-8")
        ignored = subprocess.run(["git", "check-ignore", "60-mine.md"],
                                 cwd=cloned, capture_output=True, text=True)
        self.assertNotEqual(ignored.returncode, 0,
                            "the cloned private repo cannot track its own rules")

    def test_a_remote_that_yields_no_rules_says_so(self):
        origin = self.home / "origin"
        origin.mkdir()

        # Exactly what a repo created through a web UI ships, and exactly what
        # the real private remote held: a boilerplate README and nothing else.
        (origin / "README.md").write_text("# rules\n\nTo push, run git push.\n", encoding="utf-8")
        self._git_init(origin)

        result = self.run_setup(AI_SETUP_LOCAL_RULES_REMOTE=str(origin),
                                AI_SETUP_LOCAL_RULES_DIR=None)

        # Not a failure — a private repo is legitimately empty the day it is
        # made — but the run otherwise reports success with no private layer at
        # all, which is indistinguishable from a working setup.
        self.assertEqual(result.returncode, 0)
        self.assertIn("produced no rules", result.stderr)
        self.assertIn("README.md is skipped", result.stderr)
        self.assertNotIn("### LOCAL", self.claude_rules())

    def test_a_remote_that_yields_rules_says_nothing(self):
        origin = self.home / "origin"
        origin.mkdir()
        (origin / "50-real.md").write_text("REMOTE RULE\n", encoding="utf-8")
        self._git_init(origin)

        result = self.run_setup(AI_SETUP_LOCAL_RULES_REMOTE=str(origin),
                                AI_SETUP_LOCAL_RULES_DIR=None)

        # A warning that fires on the happy path is a warning people learn to
        # scroll past, which costs the one case it exists for
        self.assertNotIn("produced no rules", result.stderr)

    def test_no_empty_remote_warning_when_no_remote_is_configured(self):
        empty = self.home / "no_private_rules"
        empty.mkdir()

        result = self.run_setup(AI_SETUP_LOCAL_RULES_REMOTE="",
                                AI_SETUP_LOCAL_RULES_DIR=str(empty))

        # Having no private layer is the normal state for anyone who never set
        # a remote. Complaining about it every run is noise, and noise is how a
        # warning that matters gets scrolled past.
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("produced no rules", result.stderr)

    def test_rules_left_in_the_repo_directory_are_reported_not_ignored(self):
        stray = self.fake_ai / "local_rules"
        stray.mkdir(parents=True, exist_ok=True)
        (stray / "10-old.md").write_text("STRANDED RULE\n", encoding="utf-8")

        result = self.run_setup(AI_SETUP_LOCAL_RULES_DIR=None)

        # Anyone who followed the older instructions has rules here that now
        # reach no agent. Silently not applying them looks exactly like
        # applying them.
        self.assertIn("nothing reads", result.stderr)
        self.assertIn("10-old.md", result.stderr)
        self.assertNotIn("STRANDED RULE", self.claude_rules())

    def test_no_stranded_warning_when_the_repo_directory_is_the_configured_one(self):
        stray = self.fake_ai / "local_rules"
        stray.mkdir(parents=True, exist_ok=True)
        (stray / "10-old.md").write_text("STILL READ\n", encoding="utf-8")

        result = self.run_setup(AI_SETUP_LOCAL_RULES_DIR=str(stray))

        self.assertNotIn("nothing reads", result.stderr)
        self.assertIn("STILL READ", self.claude_rules())

    def test_no_stranded_warning_for_the_placeholder_alone(self):
        stray = self.fake_ai / "local_rules"
        stray.mkdir(parents=True, exist_ok=True)
        for rule in stray.glob("*.md"):
            rule.unlink()
        (stray / ".gitignore").write_text("*\n!.gitignore\n", encoding="utf-8")

        # The shipped placeholder is not a rule, so an untouched clone must not
        # warn about it on every single run
        self.assertNotIn("nothing reads", self.run_setup(AI_SETUP_LOCAL_RULES_DIR=None).stderr)

    def notes_tree(self, path):
        """
        Capture a directory's full contents, for a did-nothing assertion.

        Args:
            path (pathlib.Path): the directory. Need not exist.

        Returns:
            dict: {str: str} every file's path relative to `path`, mapped to
            its bytes as a hex digest. `.git` is included deliberately: the
            claim under test is that no repository was created.

        Raises:
            OSError: a file cannot be read.
        """

        import hashlib

        if not path.exists():
            return {}

        return {
            str(p.relative_to(path)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(path.rglob("*")) if p.is_file()
        }

    def test_notes_directory_with_content_but_no_repo_is_reported_not_created(self):
        notes = self.home / "daily-notes"
        notes.mkdir()
        (notes / "2026-01-01.md").write_text("a note\n", encoding="utf-8")
        before = self.notes_tree(notes)

        result = self.run_setup(AI_SETUP_NOTES_PATH=str(notes),
                                AI_SETUP_NOTES_REMOTE="ssh://git@example.com/me/notes.git")

        self.assertIn("is not a git repository", result.stderr)
        self.assertIn("will make it one", result.stderr)

        # The exact commands, with real paths substituted — a reader should not
        # have to translate a placeholder to act on this
        self.assertIn(f"git -C {notes} init", result.stderr)
        self.assertIn("remote add origin ssh://git@example.com/me/notes.git", result.stderr)

        # The actual claim: nothing was created. Asserting the message alone
        # would pass even if it had silently run the commands it printed.
        self.assertEqual(self.notes_tree(notes), before)
        self.assertFalse((notes / ".git").exists())

    def test_a_notes_repo_with_no_remote_is_reported_not_wired_up(self):
        notes = self.home / "daily-notes"
        notes.mkdir()
        subprocess.run(["git", "init", "--quiet", str(notes)], check=True)
        before = self.notes_tree(notes)

        result = self.run_setup(AI_SETUP_NOTES_PATH=str(notes),
                                AI_SETUP_NOTES_REMOTE="ssh://git@example.com/me/notes.git")

        self.assertIn("no remote", result.stderr)
        self.assertIn(f"git -C {notes} remote add origin", result.stderr)
        self.assertEqual(self.notes_tree(notes), before)

    def test_a_notes_repo_pointing_elsewhere_is_reported_not_repointed(self):
        notes = self.home / "daily-notes"
        subprocess.run(["git", "init", "--quiet", str(notes)], check=True)
        subprocess.run(["git", "-C", str(notes), "remote", "add", "origin",
                        "ssh://git@example.com/me/OTHER.git"], check=True)

        result = self.run_setup(AI_SETUP_NOTES_PATH=str(notes),
                                AI_SETUP_NOTES_REMOTE="ssh://git@example.com/me/notes.git")

        # Both URLs shown so the reader can see which one is wrong. Repointing
        # someone's repo is how work gets pushed where it was never meant to go.
        self.assertIn("OTHER.git", result.stderr)
        self.assertIn("me/notes.git", result.stderr)
        self.assertIn("nothing was altered", result.stderr)

        current = subprocess.run(["git", "-C", str(notes), "remote", "get-url", "origin"],
                                 capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(current, "ssh://git@example.com/me/OTHER.git")

    def test_an_empty_notes_directory_with_a_remote_is_cloned(self):
        origin = self.home / "notes-origin"
        origin.mkdir()
        (origin / "2026-01-01.md").write_text("from the remote\n", encoding="utf-8")
        self._git_init(origin)

        notes = self.home / "daily-notes"

        self.assertEqual(self.run_setup(AI_SETUP_NOTES_PATH=str(notes),
                                        AI_SETUP_NOTES_REMOTE=str(origin)).returncode, 0)

        # Fetching a repo the owner already made is not creating one, and it is
        # the same thing the private-rules layer already does
        self.assertTrue((notes / ".git").is_dir())
        self.assertTrue((notes / "2026-01-01.md").is_file())

    def test_an_empty_notes_directory_with_no_remote_says_nothing_will_sync(self):
        notes = self.home / "daily-notes"
        notes.mkdir()

        result = self.run_setup(AI_SETUP_NOTES_PATH=str(notes), AI_SETUP_NOTES_REMOTE="")

        self.assertIn("nothing will sync", result.stderr)
        self.assertEqual(self.notes_tree(notes), {})

    def test_a_ready_notes_repo_is_reported_silently(self):
        origin = self.home / "notes-origin"
        origin.mkdir()
        (origin / "2026-01-01.md").write_text("note\n", encoding="utf-8")
        self._git_init(origin)

        notes = self.home / "daily-notes"
        subprocess.run(["git", "clone", "--quiet", str(origin), str(notes)], check=True)

        result = self.run_setup(AI_SETUP_NOTES_PATH=str(notes), AI_SETUP_NOTES_REMOTE=str(origin))

        # A message on every run for a setup that is already correct is noise,
        # and noise is how the messages that matter get scrolled past
        self.assertNotIn("nothing will sync", result.stderr)
        self.assertNotIn("not a git repository", result.stderr)
        self.assertNotIn("nothing was altered", result.stderr)

    def test_the_notes_remote_is_recorded_and_asked_after_the_path(self):
        self.run_setup(AI_SETUP_NOTES_PATH=str(self.home / "n"),
                       AI_SETUP_NOTES_REMOTE="ssh://git@example.com/me/notes.git")

        self.assertEqual(airules.config_get("notes_remote"), "ssh://git@example.com/me/notes.git")

    def test_no_notes_repo_report_when_the_notes_module_is_off(self):
        notes = self.home / "daily-notes"
        notes.mkdir()
        (notes / "2026-01-01.md").write_text("a note\n", encoding="utf-8")

        # Written into the config directly, and NOT passed as an env answer.
        # Turning the module off skips the question that would set it, so a
        # test relying on the prompt would leave notes_path unset — and then
        # pass whether or not the module check works at all.
        self.write_config(notes_path=str(notes))

        result = self.run_setup(AI_SETUP_MODULE_DAILY_NOTES="no")

        # Notes are off, so their repository is none of setup's business
        self.assertNotIn("is not a git repository", result.stderr)
        self.assertNotIn("nothing will sync", result.stderr)

    def test_an_unreachable_notes_remote_does_not_lose_the_answers(self):
        result = self.run_setup(AI_SETUP_NOTES_PATH=str(self.home / "n"),
                                AI_SETUP_NOTES_REMOTE="ssh://git@example.invalid/me/notes.git")

        # The answers are work the user just did. A clone that cannot reach its
        # host must not throw them away and make them retype the lot.
        self.assertEqual(airules.config_get("notes_remote"),
                         "ssh://git@example.invalid/me/notes.git")
        self.assertIn("could not clone", result.stderr)

    def test_an_unreachable_notes_remote_still_installs_the_rules(self):
        result = self.run_setup(AI_SETUP_NOTES_PATH=str(self.home / "n"),
                                AI_SETUP_NOTES_REMOTE="ssh://git@example.invalid/me/notes.git")

        # The notes layer and the rules layer have nothing to do with each
        # other. A notes host being down must not leave the agents unconfigured.
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(airules.assembled_path().is_file())
        self.assertTrue((self.home / ".claude" / "CLAUDE.md").is_symlink())

    def test_an_unreachable_notes_remote_reports_rather_than_tracebacks(self):
        result = self.run_setup(AI_SETUP_NOTES_PATH=str(self.home / "n"),
                                AI_SETUP_NOTES_REMOTE="ssh://git@example.invalid/me/notes.git")

        # A traceback tells the reader nothing they can act on and looks like
        # the tool broke rather than the network
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("notes will not sync", result.stderr)

    def test_a_failed_local_rules_clone_also_keeps_the_answers(self):
        result = self.run_setup(AI_SETUP_LOCAL_RULES_REMOTE="ssh://git@example.invalid/me/r.git",
                                AI_SETUP_LOCAL_RULES_DIR=str(self.home / "bare"))

        self.assertEqual(result.returncode, airules.ExitStatus.CLONE_FAILED)
        self.assertEqual(airules.config_get("local_rules_remote"),
                         "ssh://git@example.invalid/me/r.git")

        # Pointed at where they were kept, so the reader knows re-running is an
        # edit rather than starting over
        self.assertIn(str(airules.config_path()), result.stderr)

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
