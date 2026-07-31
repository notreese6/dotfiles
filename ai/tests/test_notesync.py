import os
import subprocess
import unittest
from pathlib import Path
from base import SandboxedTestCase
import notesync


def git(cwd, *args):
    """
    Run a git command in a test fixture, failing the test if it errors.

    Args:
        cwd (pathlib.Path): the directory to run in.
        *args (str): git arguments.

    Returns:
        str: captured standard output.

    Raises:
        subprocess.CalledProcessError: git exited non-zero.
    """

    # Identity pinned per-invocation so these never depend on, or touch, the
    # real user's git config.
    return subprocess.run(
        ["git", "-C", str(cwd), "-c", "user.email=t@t", "-c", "user.name=t",
         "-c", "commit.gpgsign=false", *args],
        capture_output=True, text=True, check=True,
    ).stdout


class NotesRepoTestCase(SandboxedTestCase):
    """
    An origin plus two clones, standing in for two machines sharing a notes repo.
    """

    def setUp(self):
        """
        Build a bare origin and two working clones under the sandboxed HOME.

        Real git repositories rather than mocks: this module exists to drive
        git correctly, so a mock would only assert that it calls the commands
        this implementation happens to call.

        Args:
            None

        Returns:
            None

        Raises:
            subprocess.CalledProcessError: a git command failed.
            OSError: the sandbox cannot be written.
        """

        super().setUp()

        seed = self.home / "seed"
        seed.mkdir()
        (seed / "2026-01-01").mkdir()
        (seed / "2026-01-01" / "project.md").write_text("# day one\n\nfirst note\n", encoding="utf-8")
        git(seed, "init", "--quiet", "--initial-branch=main")
        git(seed, "add", "-A")
        git(seed, "commit", "--quiet", "-m", "seed")

        self.origin = self.home / "origin.git"
        subprocess.run(["git", "clone", "--quiet", "--bare", str(seed), str(self.origin)], check=True)

        self.one = self.clone("one")
        self.two = self.clone("two")

    def clone(self, name):
        """
        Clone the origin into the sandbox, standing in for one machine.

        Args:
            name (str): directory name under the sandboxed HOME.

        Returns:
            pathlib.Path: the working clone.

        Raises:
            subprocess.CalledProcessError: the clone failed.
        """

        path = self.home / name
        subprocess.run(["git", "clone", "--quiet", str(self.origin), str(path)], check=True)
        git(path, "config", "user.email", "t@t")
        git(path, "config", "user.name", "t")

        return path

    def write(self, repo, relpath, text):
        """
        Write a note file inside a clone.

        Args:
            repo (pathlib.Path): the clone.
            relpath (str): path under it.
            text (str): file contents.

        Returns:
            pathlib.Path: the file written.

        Raises:
            OSError: the file cannot be written.
        """

        path = repo / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

        return path

    def commit_push(self, repo, relpath, text, message="note"):
        """
        Write, commit and push one file from a clone.

        Args:
            repo (pathlib.Path): the clone.
            relpath (str): path under it.
            text (str): file contents.
            message (str): commit message.

        Returns:
            None

        Raises:
            subprocess.CalledProcessError: a git command failed.
        """

        self.write(repo, relpath, text)
        git(repo, "add", "-A")
        git(repo, "commit", "--quiet", "-m", message)
        git(repo, "push", "--quiet")

    def tree_state(self, repo):
        """
        Capture every tracked and untracked file's contents, for comparison.

        Args:
            repo (pathlib.Path): the clone.

        Returns:
            dict: {str: str} path relative to `repo` mapped to its text. Skips
            everything under `.git`, which changes for reasons this is not
            asserting about.

        Raises:
            OSError: a file cannot be read.
        """

        state = {}
        for path in sorted(repo.rglob("*")):
            if ".git" in path.parts or not path.is_file():
                continue
            state[str(path.relative_to(repo))] = path.read_text(encoding="utf-8")

        return state


class TestLock(NotesRepoTestCase):
    """
    Covers the mkdir lock that serializes concurrent syncs.
    """

    def test_a_second_acquire_reports_the_holder(self):
        with notesync.lock(self.one):
            with self.assertRaises(notesync.LockHeld) as caught:
                with notesync.lock(self.one):
                    self.fail("the second acquire should not have succeeded")

        # The pid is what makes a stuck lock traceable to a process, which is
        # the only way out of one that was never released
        self.assertEqual(caught.exception.pid, str(os.getpid()))

    def test_the_lock_is_released_when_the_body_raises(self):
        with self.assertRaises(ValueError):
            with notesync.lock(self.one):
                raise ValueError("something went wrong mid-sync")

        # A lock that outlives its run wedges every later sync on the machine,
        # and a crash is exactly when that would happen
        with notesync.lock(self.one):
            pass

    def test_two_directories_lock_independently(self):
        with notesync.lock(self.one):
            with notesync.lock(self.two):
                pass

    def test_the_lock_lives_inside_git_so_it_is_never_committed(self):
        with notesync.lock(self.one):
            self.assertTrue((self.one / notesync.LOCK_RELPATH).is_dir())

            # Anything outside .git/ would show up in `git status`, get swept
            # into `git add -A` by the sync itself, and land in the repo
            self.assertEqual(git(self.one, "status", "--porcelain").strip(), "")


class TestIncomingDelta(NotesRepoTestCase):
    """
    Covers reporting what the remote has that this clone does not.
    """

    def test_reports_the_files_and_subjects_another_machine_pushed(self):
        self.commit_push(self.two, "2026-01-02/project.md", "second note\n", message="add day two")

        paths, subjects = notesync.incoming_delta(self.one)

        self.assertEqual(paths, ["2026-01-02/project.md"])
        self.assertEqual(subjects, ["add day two"])

    def test_reports_nothing_when_already_current(self):
        self.assertEqual(notesync.incoming_delta(self.one), ([], []))

    def test_reports_nothing_when_there_is_no_upstream(self):
        solo = self.home / "solo"
        solo.mkdir()
        git(solo, "init", "--quiet", "--initial-branch=main")

        # A repo nobody has pushed yet is a normal state, not a failure
        self.assertEqual(notesync.incoming_delta(solo), ([], []))

    def test_subjects_come_back_oldest_first(self):
        self.commit_push(self.two, "a.md", "a\n", message="first")
        self.commit_push(self.two, "b.md", "b\n", message="second")

        _, subjects = notesync.incoming_delta(self.one)

        # Reading order. `git log` gives newest first, which reads backwards
        # when the point is "here is what happened while you were away".
        self.assertEqual(subjects, ["first", "second"])


class TestPull(NotesRepoTestCase):
    """
    Covers bringing in remote work, and refusing to resolve a conflict.
    """

    def test_fast_forwards_and_reports_what_came_in(self):
        self.commit_push(self.two, "2026-01-02/project.md", "second note\n", message="day two")

        paths, subjects = notesync.pull(self.one)

        self.assertEqual(paths, ["2026-01-02/project.md"])
        self.assertEqual(subjects, ["day two"])
        self.assertEqual((self.one / "2026-01-02/project.md").read_text(encoding="utf-8"),
                         "second note\n")

    def test_a_local_edit_survives_the_pull(self):
        self.commit_push(self.two, "2026-01-02/other.md", "theirs\n")
        self.write(self.one, "2026-01-03/mine.md", "work in progress\n")

        notesync.pull(self.one)

        # --autostash: an edit in progress must not block a pull, and must not
        # be lost to one either
        self.assertEqual((self.one / "2026-01-03/mine.md").read_text(encoding="utf-8"),
                         "work in progress\n")

    def test_a_real_conflict_raises_and_names_the_file(self):
        self.commit_push(self.two, "2026-01-01/project.md", "# day one\n\ntheirs\n")

        self.write(self.one, "2026-01-01/project.md", "# day one\n\nmine\n")
        git(self.one, "add", "-A")
        git(self.one, "commit", "--quiet", "-m", "mine")

        with self.assertRaises(notesync.ConflictError) as caught:
            notesync.pull(self.one)

        self.assertIn("2026-01-01/project.md", caught.exception.paths)
        self.assertIn("2026-01-01/project.md", str(caught.exception))

    def test_a_conflict_leaves_the_working_tree_byte_identical(self):
        self.commit_push(self.two, "2026-01-01/project.md", "# day one\n\ntheirs\n")

        self.write(self.one, "2026-01-01/project.md", "# day one\n\nmine\n")
        git(self.one, "add", "-A")
        git(self.one, "commit", "--quiet", "-m", "mine")

        before = self.tree_state(self.one)

        with self.assertRaises(notesync.ConflictError):
            notesync.pull(self.one)

        # The actual claim this module makes. Raising is not enough: a rebase
        # left half-applied writes conflict markers into the user's prose, and
        # an agent that then "reconciles" would be editing git's scribble.
        self.assertEqual(self.tree_state(self.one), before)
        self.assertNotIn("<<<<<<<", (self.one / "2026-01-01/project.md").read_text(encoding="utf-8"))

    def test_a_conflict_leaves_no_rebase_in_progress(self):
        self.commit_push(self.two, "2026-01-01/project.md", "# day one\n\ntheirs\n")
        self.write(self.one, "2026-01-01/project.md", "# day one\n\nmine\n")
        git(self.one, "add", "-A")
        git(self.one, "commit", "--quiet", "-m", "mine")

        with self.assertRaises(notesync.ConflictError):
            notesync.pull(self.one)

        # A repo stuck mid-rebase refuses almost every later command, so the
        # next sync would fail for a reason unrelated to what actually happened
        self.assertFalse((self.one / ".git" / "rebase-merge").exists())
        self.assertFalse((self.one / ".git" / "rebase-apply").exists())
        git(self.one, "status")

    def test_offline_is_not_a_conflict(self):
        git(self.one, "remote", "set-url", "origin", str(self.home / "nowhere.git"))

        # No network is the ordinary case on a laptop, and it must not look
        # like two people editing the same note
        self.assertEqual(notesync.pull(self.one), ([], []))

    def test_a_directory_that_is_not_a_repo_is_refused(self):
        plain = self.home / "plain"
        plain.mkdir()
        (plain / "note.md").write_text("mine\n", encoding="utf-8")

        with self.assertRaises(notesync.NotARepoError):
            notesync.pull(plain)

        # Nothing created: making a repo out of someone's notes is their call
        self.assertFalse((plain / ".git").exists())


class TestCommitAndPush(NotesRepoTestCase):
    """
    Covers committing local work and getting it to the remote.
    """

    def test_commits_new_and_changed_files(self):
        self.write(self.one, "2026-01-04/project.md", "fresh\n")
        self.write(self.one, "2026-01-01/project.md", "# day one\n\nedited\n")

        self.assertTrue(notesync.commit_all(self.one, "logged"))
        self.assertEqual(git(self.one, "status", "--porcelain").strip(), "")
        self.assertIn("logged", git(self.one, "log", "--format=%s", "-1"))

    def test_a_clean_tree_makes_no_commit(self):
        before = git(self.one, "rev-parse", "HEAD").strip()

        # A sync after a sync is the ordinary case, so this is a return value
        # rather than an exception — and an empty commit per run would bury the
        # real ones in noise
        self.assertFalse(notesync.commit_all(self.one, "nothing to do"))
        self.assertEqual(git(self.one, "rev-parse", "HEAD").strip(), before)

    def test_commits_a_deletion_too(self):
        (self.one / "2026-01-01" / "project.md").unlink()

        # `add -A` rather than `add .`: a note deleted on one machine has to
        # stop existing on the others, or it comes back on the next sync
        self.assertTrue(notesync.commit_all(self.one, "removed"))
        self.assertEqual(git(self.one, "status", "--porcelain").strip(), "")

    def test_push_lands_on_the_remote(self):
        self.write(self.one, "2026-01-04/project.md", "fresh\n")
        notesync.commit_all(self.one, "logged")

        self.assertTrue(notesync.push(self.one))

        git(self.two, "pull", "--quiet")
        self.assertTrue((self.two / "2026-01-04/project.md").is_file())

    def test_push_retries_once_behind_a_pull(self):
        self.commit_push(self.two, "2026-01-05/theirs.md", "theirs\n")

        self.write(self.one, "2026-01-05/mine.md", "mine\n")
        notesync.commit_all(self.one, "mine")

        # The first push is rejected because the other machine got there first.
        # That is the common case with two machines, not an error.
        self.assertTrue(notesync.push(self.one))

        git(self.two, "pull", "--quiet")
        self.assertTrue((self.two / "2026-01-05/mine.md").is_file())
        self.assertTrue((self.two / "2026-01-05/theirs.md").is_file())

    def test_an_unreachable_remote_leaves_the_commit_in_place(self):
        self.write(self.one, "2026-01-06/project.md", "written offline\n")
        notesync.commit_all(self.one, "offline note")
        git(self.one, "remote", "set-url", "origin", str(self.home / "nowhere.git"))

        # False, not an exception: the note is committed, and refusing to
        # finish would block someone's work over a network problem
        self.assertFalse(notesync.push(self.one))
        self.assertIn("offline note", git(self.one, "log", "--format=%s", "-1"))

    def test_push_with_no_upstream_is_not_an_error(self):
        solo = self.home / "solo"
        solo.mkdir()
        git(solo, "init", "--quiet", "--initial-branch=main")
        (solo / "note.md").write_text("mine\n", encoding="utf-8")
        git(solo, "add", "-A")
        git(solo, "commit", "--quiet", "-m", "first")

        self.assertFalse(notesync.push(solo))

    def test_a_conflicting_push_reports_the_conflict_rather_than_offline(self):
        self.commit_push(self.two, "2026-01-01/project.md", "# day one\n\ntheirs\n")

        self.write(self.one, "2026-01-01/project.md", "# day one\n\nmine\n")
        notesync.commit_all(self.one, "mine")

        # The retry's pull conflicts. Returning False here would report a
        # genuine conflict as "offline, try later" and it would never surface.
        with self.assertRaises(notesync.ConflictError):
            notesync.push(self.one)


class TestHasUnpushed(NotesRepoTestCase):
    """
    Covers knowing whether anything is waiting to go out.
    """

    def test_false_on_a_clone_that_is_level_with_its_remote(self):
        self.assertFalse(notesync.has_unpushed(self.one))

    def test_true_after_a_local_commit(self):
        self.write(self.one, "2026-01-07/project.md", "mine\n")
        notesync.commit_all(self.one, "mine")

        self.assertTrue(notesync.has_unpushed(self.one))

    def test_false_again_once_it_is_pushed(self):
        self.write(self.one, "2026-01-07/project.md", "mine\n")
        notesync.commit_all(self.one, "mine")
        notesync.push(self.one)

        self.assertFalse(notesync.has_unpushed(self.one))

    def test_false_with_no_upstream_to_be_ahead_of(self):
        solo = self.home / "solo"
        solo.mkdir()
        git(solo, "init", "--quiet", "--initial-branch=main")
        (solo / "note.md").write_text("mine\n", encoding="utf-8")
        git(solo, "add", "-A")
        git(solo, "commit", "--quiet", "-m", "first")

        # A branch nobody has pushed has nothing to be ahead *of*; saying True
        # here would make the CLI claim it pushed a repo with no remote
        self.assertFalse(notesync.has_unpushed(solo))

    def test_incoming_work_does_not_count_as_unpushed(self):
        self.commit_push(self.two, "2026-01-08/theirs.md", "theirs\n")

        # Behind is not ahead. Confusing the two makes the CLI push on a run
        # whose only news was someone else's.
        self.assertFalse(notesync.has_unpushed(self.one))


class TestRepoState(NotesRepoTestCase):
    """
    Covers the pure state check ai-setup reports from.
    """

    def test_absent_and_empty_both_read_as_absent(self):
        self.assertIs(notesync.notes_repo_state(self.home / "nope", ""), notesync.RepoState.ABSENT)

        empty = self.home / "empty"
        empty.mkdir()
        self.assertIs(notesync.notes_repo_state(empty, ""), notesync.RepoState.ABSENT)

    def test_content_without_a_repo(self):
        plain = self.home / "plain"
        plain.mkdir()
        (plain / "note.md").write_text("mine\n", encoding="utf-8")

        self.assertIs(notesync.notes_repo_state(plain, ""), notesync.RepoState.NOT_A_REPO)

    def test_a_repo_with_no_remote_but_one_configured(self):
        solo = self.home / "solo"
        solo.mkdir()
        git(solo, "init", "--quiet", "--initial-branch=main")

        self.assertIs(notesync.notes_repo_state(solo, "ssh://git@example.com/me/n.git"),
                      notesync.RepoState.NO_REMOTE)

    def test_a_repo_with_no_remote_and_none_configured_is_ready(self):
        solo = self.home / "solo"
        solo.mkdir()
        git(solo, "init", "--quiet", "--initial-branch=main")

        # Local-only notes are a coherent setup, not a half-finished one
        self.assertIs(notesync.notes_repo_state(solo, ""), notesync.RepoState.READY)

    def test_a_remote_that_does_not_match_the_config(self):
        self.assertIs(notesync.notes_repo_state(self.one, "ssh://git@example.com/me/other.git"),
                      notesync.RepoState.REMOTE_DIFFERS)

    def test_a_matching_remote_is_ready(self):
        self.assertIs(notesync.notes_repo_state(self.one, str(self.origin)),
                      notesync.RepoState.READY)

    def test_the_state_check_changes_nothing(self):
        plain = self.home / "plain"
        plain.mkdir()
        (plain / "note.md").write_text("mine\n", encoding="utf-8")
        before = self.tree_state(plain)

        for remote in ("", str(self.origin)):
            notesync.notes_repo_state(plain, remote)

        # The whole point of it being pure: ai-setup reports from this, and
        # "it did nothing" has to be structurally true rather than a promise
        self.assertEqual(self.tree_state(plain), before)
        self.assertFalse((plain / ".git").exists())
