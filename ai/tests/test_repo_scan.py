import subprocess
import unittest

from base import REPO_ROOT, SandboxedTestCase

SCAN = REPO_ROOT / "ai" / "bin" / "repo-scan"

# repo-scan is gitignored on purpose — it is a local-only leak gate, so a fresh
# clone does not have it. Skipping beats a suite that fails everywhere it is
# absent, and beats having no coverage at all on the machines that do run it.
skip_without_scan = unittest.skipUnless(SCAN.is_file(), "repo-scan is local-only and not present")


@skip_without_scan
class TestRepoScanWorktree(SandboxedTestCase):
    """
    Covers scanning what is about to be committed rather than what already was.
    """

    def setUp(self):
        """
        Build a throwaway repository with a clean commit behind it.

        Args:
            None

        Returns:
            None

        Raises:
            OSError: the sandbox cannot be written.
            subprocess.CalledProcessError: a git command fails.
        """

        super().setUp()

        self.work = self.home / "work"
        self.work.mkdir()
        self.git("init")
        (self.work / "clean.md").write_text("nothing to see\n", encoding="utf-8")
        self.git("add", "-A")
        self.git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "init")

    def git(self, *args):
        """
        Run one git command in the throwaway repository.

        Args:
            *args (str): arguments after `git`.

        Returns:
            subprocess.CompletedProcess: the finished run.

        Raises:
            subprocess.CalledProcessError: the command fails.
        """

        return subprocess.run(["git", "-C", str(self.work)] + list(args),
                              capture_output=True, text=True, check=True)

    def scan(self, *args):
        """
        Run repo-scan inside the throwaway repository.

        Args:
            *args (str): arguments after the command name.

        Returns:
            subprocess.CompletedProcess: the finished run.

        Raises:
            OSError: the script is missing or is not executable.
        """

        return subprocess.run(["python3", str(SCAN)] + list(args),
                              cwd=str(self.work), capture_output=True, text=True)

    def scan_merged(self, *args):
        """
        Run repo-scan with both streams sharing one pipe, preserving order.

        Reading `stdout` and `stderr` separately and joining them cannot show an
        interleaving bug at all: the join puts every stdout line ahead of every
        stderr line whatever order they were actually written in. Only one pipe
        records what a person or a `| tee` would really see.

        Args:
            *args (str): arguments after the command name.

        Returns:
            str: everything the command wrote, in the order it was written.

        Raises:
            OSError: the script is missing or is not executable.
        """

        # Explicit stdout=PIPE rather than capture_output, which cannot be
        # combined with a stderr of its own — the two together raise.
        result = subprocess.run(["python3", str(SCAN)] + list(args),
                                cwd=str(self.work), text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        return result.stdout

    def plant(self, name="pending.md"):
        """
        Write an uncommitted file carrying something a pattern matches.

        The matching text is assembled at runtime rather than written as a
        literal, so this file does not itself trip the very gate it tests —
        which it did, the first time repo-scan was pointed at the working tree.

        Args:
            name (str): file name to create in the working tree.

        Returns:
            None

        Raises:
            OSError: the file cannot be written.
        """

        bait = "pass" + "word" + ' = "' + ("hunter2" * 2) + '"'
        (self.work / name).write_text(bait + "\n", encoding="utf-8")

    def test_history_is_clean_while_the_pending_change_is_not(self):
        self.plant()

        # The whole point: the old command answered a question nobody was
        # asking, and answered it truthfully, which is what made it misleading.
        self.assertEqual(self.scan("HEAD").returncode, 0)
        self.assertEqual(self.scan("--worktree").returncode, 1)

    def test_the_finding_names_the_file_and_line(self):
        self.plant()

        result = self.scan("--worktree")

        self.assertIn("pending.md:1", result.stdout + result.stderr)

    def test_a_clean_worktree_passes(self):
        self.assertEqual(self.scan("--worktree").returncode, 0)

    def test_a_staged_file_is_scanned_too(self):
        self.plant()
        self.git("add", "-A")

        self.assertEqual(self.scan("--worktree").returncode, 1)

    def test_an_ignored_file_is_not_scanned(self):
        self.plant("secret.local")
        (self.work / ".gitignore").write_text("*.local\n", encoding="utf-8")

        # An ignored file cannot reach a commit, so flagging it would train
        # people to ignore the gate.
        self.assertEqual(self.scan("--worktree").returncode, 0)

    def test_findings_print_below_the_header_when_stdout_is_a_pipe(self):
        self.plant()

        # Must be the merged stream. Not a cosmetic complaint: stdout
        # block-buffers when it is not a tty and stderr never does, so without a
        # flush the findings overtook the header and the report read back-to-front.
        merged = self.scan_merged("--worktree")

        self.assertLess(merged.index("pattern(s)"), merged.index("[-]"))


if __name__ == "__main__":
    unittest.main()
