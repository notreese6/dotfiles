import os
import subprocess
import unittest
from pathlib import Path
from test_notesync import NotesRepoTestCase, git
import airules


class TestDailyNotesSyncCli(NotesRepoTestCase):
    """
    End-to-end tests for daily-notes-sync, run as a real subprocess.

    Inherits the origin-plus-two-clones fixture, so every case here is two
    machines sharing one notes repo — which is the only situation this command
    exists for.
    """

    def setUp(self):
        """
        Point the sandboxed config at clone 'one' as the notes directory.

        Args:
            None

        Returns:
            None

        Raises:
            OSError: the sandbox cannot be written.
        """

        super().setUp()

        self.write_config(notes_path=str(self.one), notes_remote=str(self.origin))

    def run_sync(self, *args, **overrides):
        """
        Run daily-notes-sync in a subprocess against the sandbox.

        Args:
            *args (str): command-line arguments after the script name.
            **overrides (str): environment variables to set for this run.

        Returns:
            subprocess.CompletedProcess: the finished run, output captured as
            text. A non-zero exit is returned, not raised.

        Raises:
            OSError: the script is missing or is not executable.
        """

        env = dict(os.environ)
        env.update(overrides)

        return subprocess.run(
            [str(self.repo / "ai" / "bin" / "daily-notes-sync"), *args],
            capture_output=True, text=True, env=env,
        )

    def test_pull_reports_what_another_machine_pushed(self):
        self.commit_push(self.two, "2026-01-02/project.md", "theirs\n", message="add day two")

        result = self.run_sync("pull")

        self.assertEqual(result.returncode, 0, result.stderr)

        # The reason `pull` exists as its own command: an agent about to write
        # this file needs to see that it changed elsewhere first.
        self.assertIn("2026-01-02/project.md", result.stdout)
        self.assertIn("add day two", result.stdout)

    def test_pull_says_so_when_there_is_nothing_to_bring_in(self):
        result = self.run_sync("pull")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("already current", result.stdout)

    def test_pull_commits_nothing(self):
        self.write(self.one, "2026-01-03/wip.md", "half-written\n")
        before = git(self.one, "rev-parse", "HEAD").strip()

        self.assertEqual(self.run_sync("pull").returncode, 0)

        # `pull` is the freshness check an agent runs *before* writing. Having
        # it commit would sweep a half-written note into history.
        self.assertEqual(git(self.one, "rev-parse", "HEAD").strip(), before)

        # -uall because the plain --porcelain collapses an untracked directory
        # to one entry, which would pass this whether or not the file survived
        self.assertIn("2026-01-03/wip.md", git(self.one, "status", "--porcelain", "-uall"))

    def test_a_bare_invocation_commits_and_pushes(self):
        self.write(self.one, "2026-01-04/project.md", "written today\n")

        result = self.run_sync()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("pushed", result.stdout)

        git(self.two, "pull", "--quiet")
        self.assertTrue((self.two / "2026-01-04/project.md").is_file())

    def test_the_default_commit_message_carries_a_timestamp(self):
        self.write(self.one, "2026-01-04/project.md", "written today\n")
        self.run_sync()

        subject = git(self.one, "log", "--format=%s", "-1").strip()

        self.assertTrue(subject.startswith("notes: "), subject)

    def test_an_explicit_message_is_used_verbatim(self):
        self.write(self.one, "2026-01-04/project.md", "written today\n")
        self.run_sync("sync", "--message", "logged the migration")

        self.assertEqual(git(self.one, "log", "--format=%s", "-1").strip(), "logged the migration")

    def test_a_clean_tree_says_so_and_still_succeeds(self):
        result = self.run_sync()

        # Running a sync twice is the ordinary case, not an error
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("nothing to commit", result.stdout)

    def test_a_run_with_nothing_to_send_does_not_claim_it_pushed(self):
        result = self.run_sync()

        # `git push` exits 0 with "Everything up-to-date", so reporting on its
        # status alone would say "pushed" on a run that sent nothing. Output
        # nobody can trust is output nobody reads.
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("nothing to push", result.stdout)
        self.assertNotIn("[+] pushed", result.stdout)

    def test_a_commit_stranded_by_an_earlier_offline_run_is_pushed_later(self):
        # First run: written and committed while the remote was unreachable
        git(self.one, "remote", "set-url", "origin", str(self.home / "nowhere.git"))
        self.write(self.one, "2026-01-09/offline.md", "written on a plane\n")
        self.assertEqual(self.run_sync().returncode, 0)

        # Second run: back online, and nothing new has been written since. This
        # is why "nothing to push" cannot simply be inferred from "nothing to
        # commit" — the earlier note is still waiting to go out.
        git(self.one, "remote", "set-url", "origin", str(self.origin))
        result = self.run_sync()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("nothing to commit", result.stdout)
        self.assertIn("[+] pushed", result.stdout)

        git(self.two, "pull", "--quiet")
        self.assertTrue((self.two / "2026-01-09/offline.md").is_file())


class TestStatus(NotesRepoTestCase):
    """
    Covers the read-only status report.
    """

    def setUp(self):
        """
        Point the sandboxed config at clone 'one'.

        Args:
            None

        Returns:
            None

        Raises:
            OSError: the sandbox cannot be written.
        """

        super().setUp()

        self.write_config(notes_path=str(self.one), notes_remote=str(self.origin))

    def run_status(self, **overrides):
        """
        Run `daily-notes-sync status` against the sandbox.

        Args:
            **overrides (str): environment variables for this run.

        Returns:
            subprocess.CompletedProcess: the finished run.

        Raises:
            OSError: the script is missing or is not executable.
        """

        env = dict(os.environ)
        env.update(overrides)

        return subprocess.run([str(self.repo / "ai" / "bin" / "daily-notes-sync"), "status"],
                              capture_output=True, text=True, env=env)

    def test_a_working_setup_reports_ready(self):
        result = self.run_status()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(self.one), result.stdout)
        self.assertIn("ready", result.stdout)

    def test_it_changes_nothing(self):
        before = self.tree_state(self.one)
        head   = git(self.one, "rev-parse", "HEAD").strip()

        self.run_status()

        # A status command that commits, fetches or writes is one you cannot run
        # to find out what is going on
        self.assertEqual(self.tree_state(self.one), before)
        self.assertEqual(git(self.one, "rev-parse", "HEAD").strip(), head)

    def test_status_does_not_fetch(self):
        before = git(self.one, "rev-parse", "origin/main").strip()
        self.commit_push(self.two, "2026-01-10/theirs.md", "theirs\n")

        self.run_status()

        # A fetch would move the remote-tracking ref. It is left alone on
        # purpose: a status command that makes a network call hangs on a slow
        # or unreachable remote, and one that hangs is one nobody runs — which
        # is why the report says its counts are as of the last fetch.
        self.assertEqual(git(self.one, "rev-parse", "origin/main").strip(), before)
        self.assertIn("as of the last fetch", self.run_status().stdout)

    def test_a_local_only_setup_is_reported_as_working_not_broken(self):
        git(self.one, "remote", "remove", "origin")
        self.write_config(notes_remote="")

        result = self.run_status()

        # Local-only is a coherent way to use this. Reporting it as an error is
        # what makes an agent decide notes are broken and stop logging.
        self.assertEqual(result.returncode, 0)
        self.assertIn("local only", result.stdout)
        self.assertNotIn("not syncing", result.stdout + result.stderr)

    def test_a_directory_that_is_not_a_repo_says_what_to_run(self):
        plain = self.home / "plain-notes"
        (plain / "2026-01-01").mkdir(parents=True)
        (plain / "2026-01-01" / "note.md").write_text("a note\n", encoding="utf-8")
        self.write_config(notes_path=str(plain))

        result = self.run_status()
        out    = result.stdout + result.stderr

        self.assertEqual(result.returncode, 0)
        self.assertIn("not a repository", out)
        self.assertIn(f"git -C {plain} init", out)

        # The notes are still counted: "not a repository" and "no notes" are
        # different problems and only one of them is about git
        self.assertIn("1 markdown file", out)
        self.assertFalse((plain / ".git").exists())

    def test_a_mismatched_remote_is_reported_rather_than_hidden(self):
        git(self.one, "remote", "set-url", "origin", "ssh://git@example.com/me/OTHER.git")

        result = self.run_status()
        out    = result.stdout + result.stderr

        self.assertIn("OTHER.git", out)
        self.assertIn("they disagree", out)

    def test_status_exits_zero_even_when_nothing_is_set_up(self):
        self.write_config(notes_path=None)

        # Non-zero would make this unusable as a check: a caller could not tell
        # "the setup is incomplete" from "the command itself failed"
        self.assertEqual(self.run_status().returncode, 0)

    def test_unpushed_work_is_reported(self):
        self.write(self.one, "2026-01-09/mine.md", "mine\n")
        git(self.one, "add", "-A")
        git(self.one, "commit", "--quiet", "-m", "mine")

        out = self.run_status().stdout

        self.assertIn("1 commit(s)", out)


class TestDailyNotesSyncFailures(NotesRepoTestCase):
    """
    Covers each way the command declines to act, and what it exits with.
    """

    def setUp(self):
        """
        Point the sandboxed config at clone 'one'.

        Args:
            None

        Returns:
            None

        Raises:
            OSError: the sandbox cannot be written.
        """

        super().setUp()

        self.write_config(notes_path=str(self.one), notes_remote=str(self.origin))

    def run_sync(self, *args, **overrides):
        """
        Run daily-notes-sync in a subprocess against the sandbox.

        Args:
            *args (str): command-line arguments after the script name.
            **overrides (str): environment variables for this run.

        Returns:
            subprocess.CompletedProcess: the finished run.

        Raises:
            OSError: the script is missing or is not executable.
        """

        env = dict(os.environ)
        env.update(overrides)

        return subprocess.run(
            [str(self.repo / "ai" / "bin" / "daily-notes-sync"), *args],
            capture_output=True, text=True, env=env,
        )

    def test_a_conflict_exits_with_its_own_status_and_changes_nothing(self):
        self.commit_push(self.two, "2026-01-01/project.md", "# day one\n\ntheirs\n")
        self.write(self.one, "2026-01-01/project.md", "# day one\n\nmine\n")
        git(self.one, "add", "-A")
        git(self.one, "commit", "--quiet", "-m", "mine")

        before = self.tree_state(self.one)
        result = self.run_sync()

        self.assertEqual(result.returncode, airules.ExitStatus.SYNC_CONFLICT)
        self.assertIn("2026-01-01/project.md", result.stderr)

        # Said in the output, because the natural fear on reading "conflict" is
        # that something was already mangled, and the next move depends on it
        # not having been
        self.assertIn("was not changed", result.stderr)
        self.assertEqual(self.tree_state(self.one), before)

    def test_an_autostash_conflict_does_not_push_markers(self):
        # End to end, the exact failure seen on a real machine: two sessions
        # minutes apart, sync reported "[+] pushed", and a literal
        # "<<<<<<< Updated upstream" block reached the remote.
        self.commit_push(self.two, "2026-01-01/project.md", "# day one\n\ntheirs\n")
        self.write(self.one, "2026-01-01/project.md", "# day one\n\nmine, still editing\n")

        result = self.run_sync()

        self.assertEqual(result.returncode, airules.ExitStatus.SYNC_CONFLICT)
        self.assertNotIn("pushed", result.stdout)

        git(self.one, "fetch", "--quiet")
        on_remote = git(self.one, "show", "origin/main:2026-01-01/project.md")
        self.assertNotIn("<<<<<<<", on_remote)
        self.assertNotIn("mine, still editing", on_remote)

    def test_the_conflict_message_says_where_the_stashed_work_went(self):
        self.commit_push(self.two, "2026-01-01/project.md", "# day one\n\ntheirs\n")
        self.write(self.one, "2026-01-01/project.md", "# day one\n\nmine, still editing\n")

        err = self.run_sync().stderr

        # The file now holds the remote's version, so "your working tree was not
        # changed" would be a lie about the file they are about to open — and
        # nobody looks on the stash unless told to.
        self.assertIn("stash", err)
        self.assertNotIn("your working tree was not changed", err)

    def test_a_held_lock_exits_with_its_own_status(self):
        lock = self.one / ".git" / "ai-sync.lock"
        lock.mkdir()
        (lock / "pid").write_text("4242\n", encoding="utf-8")

        result = self.run_sync()

        self.assertEqual(result.returncode, airules.ExitStatus.SYNC_LOCKED)
        self.assertIn("4242", result.stderr)

    def test_a_directory_that_is_not_a_repo_is_refused_and_left_alone(self):
        plain = self.home / "plain-notes"
        plain.mkdir()
        (plain / "note.md").write_text("mine\n", encoding="utf-8")
        self.write_config(notes_path=str(plain))

        result = self.run_sync()

        self.assertEqual(result.returncode, airules.ExitStatus.NOT_A_REPO)

        # Creating a repo out of someone's notes is their decision, so the
        # command names the exact thing to run and does none of it
        self.assertIn("will not make one", result.stderr)
        self.assertIn("git -C", result.stderr)
        self.assertFalse((plain / ".git").exists())

    def test_no_configured_notes_path_is_refused(self):
        self.write_config(notes_path=None)

        result = self.run_sync()

        self.assertEqual(result.returncode, airules.ExitStatus.NOT_A_REPO)
        self.assertIn("ai-setup", result.stderr)

    def test_an_unreachable_remote_still_commits_and_exits_zero(self):
        git(self.one, "remote", "set-url", "origin", str(self.home / "nowhere.git"))
        self.write(self.one, "2026-01-05/offline.md", "written on a plane\n")

        result = self.run_sync()

        # The note is recorded; only its delivery is pending. Exiting non-zero
        # here would fail an agent's whole turn over a wifi drop.
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("safe locally", result.stderr)
        self.assertIn("offline.md", git(self.one, "show", "--stat", "--format=", "HEAD"))

    def test_the_lock_is_released_after_a_conflict(self):
        self.commit_push(self.two, "2026-01-01/project.md", "# day one\n\ntheirs\n")
        self.write(self.one, "2026-01-01/project.md", "# day one\n\nmine\n")
        git(self.one, "add", "-A")
        git(self.one, "commit", "--quiet", "-m", "mine")

        self.assertEqual(self.run_sync().returncode, airules.ExitStatus.SYNC_CONFLICT)

        # A lock surviving a failed run wedges every later sync, and a conflict
        # is exactly when someone will be re-running the command repeatedly
        self.assertFalse((self.one / ".git" / "ai-sync.lock").exists())


if __name__ == "__main__":
    unittest.main()
