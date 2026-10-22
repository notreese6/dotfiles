"""
Git operations for keeping the daily-notes directory in step across machines.

Separate from airules.py, which is about assembling rules: the only thing the
two share is the Config record. Every git command in this system goes through
_git() here, so there is one place that decides how git is invoked.

Two rules shape everything below:

- Never block the user's work. A missing remote, an unreachable host or a
  rejected push still leaves the note committed locally. Losing a note to a
  network problem is worse than a stale remote.
- Never resolve a conflict. The notes are prose written by a person; a machine
  picking a winner silently destroys one side's writing. Abort, name the files,
  and let a person decide.
"""

import os
import subprocess
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

# Kept inside .git/ so it is never a file the user sees in their notes, never
# shows up in `git status`, and cannot be committed by accident.
LOCK_RELPATH = ".git/ai-sync.lock"

# What `git diff --name-only` reports for a file left conflicted by a failed
# merge or rebase. Named because "U" alone at a call site says nothing.
DIFF_FILTER_UNMERGED = "U"


class NotesError(RuntimeError):
    """
    Base for every failure this module raises, so a caller can catch one class.

    Attributes:
        None beyond RuntimeError's.
    """


class NotARepoError(NotesError):
    """
    The notes directory is not a git repository.

    Raised rather than initialising one: making a repo out of a directory of
    someone's work is their decision, not a side effect of running a sync.

    Attributes:
        path (pathlib.Path): the directory that is not a repository.
    """

    def __init__(self, path):
        """
        Name the directory and say that nothing was created.

        Args:
            path (str or pathlib.Path): the directory that is not a repository.

        Returns:
            None

        Raises:
            None
        """

        self.path = Path(path)

        super().__init__(f"{self.path} is not a git repository, and nothing was created")


class LockHeld(NotesError):
    """
    Another sync is already running against the same notes directory.

    Attributes:
        path (pathlib.Path): the lock directory that already exists.
        pid (str): the process id recorded in it, or "" when it could not be
            read — a lock with an unreadable owner still counts as held.
    """

    def __init__(self, path, pid):
        """
        Name the lock and, where known, what holds it.

        Args:
            path (str or pathlib.Path): the lock directory.
            pid (str): the recorded process id, or "" when unknown.

        Returns:
            None

        Raises:
            None
        """

        self.path = Path(path)
        self.pid  = pid

        held_by = f" (held by pid {pid})" if pid else ""

        super().__init__(f"another sync is already running{held_by}: {self.path}")


class ConflictError(NotesError):
    """
    A pull hit a real conflict, and the rebase was aborted.

    The working tree is exactly as it was before the pull: nothing was merged,
    nothing was resolved, nothing was lost. A person decides which side wins.

    Attributes:
        paths (list): [str] the conflicted files, repo-relative, sorted.
        has_stashed_work (bool): True when the conflicting local edits were put
            on the stash rather than left in the file. That happens when the
            rebase succeeded and re-applying the autostash is what conflicted —
            the file is back to the remote's version and the reader's own text
            is only in the stash, which is not where they will look for it.
    """

    def __init__(self, paths, has_stashed_work=False):
        """
        Name the conflicted files and say the tree was left alone.

        Args:
            paths (iterable of str): repo-relative paths git reported as
                unmerged. May be empty when git reported a conflict without
                naming files, which is still a conflict.
            has_stashed_work (bool): whether the local edits ended up on the
                stash instead of in the file.

        Returns:
            None

        Raises:
            None
        """

        self.paths            = sorted(paths)
        self.has_stashed_work = has_stashed_work

        named = ", ".join(self.paths) if self.paths else "an unnamed file"
        where = ("; your uncommitted edits are on the stash" if has_stashed_work
                 else "; the rebase was aborted and nothing was changed")

        super().__init__(f"conflict in {named}{where}")


class RepoState(Enum):
    """
    What a notes directory looks like relative to the configured remote.

    Computed without touching anything, so a caller can report the situation
    and let the owner act. The member values are auto-assigned and never
    stored, so a member only ever matches itself.

    Members:
        ABSENT: the directory does not exist, or exists and is empty.
        NOT_A_REPO: it holds files but is not a git repository.
        NO_REMOTE: it is a repository with no `origin`.
        REMOTE_DIFFERS: it is a repository whose `origin` is not the configured
            remote.
        READY: it is a repository whose `origin` matches, or whose `origin`
            matches the absence of a configured remote.
    """

    ABSENT         = auto()
    NOT_A_REPO     = auto()
    NO_REMOTE      = auto()
    REMOTE_DIFFERS = auto()
    READY          = auto()


def _git(notes_dir, *args, should_check=True):
    """
    Run one git command in the notes directory.

    Every git invocation in this system goes through here, so there is one
    place that decides the working directory, the encoding and whether output
    is captured.

    Args:
        notes_dir (str or pathlib.Path): the repository to run in.
        *args (str): the git arguments, e.g. "status", "--porcelain".
        should_check (bool): True raises on a non-zero exit; False hands the
            result back so the caller can inspect `returncode`. False is for
            the commands whose failure is an expected outcome — a push with no
            network, a rebase that hit a conflict.

    Returns:
        subprocess.CompletedProcess: with `stdout` and `stderr` as text.

    Raises:
        subprocess.CalledProcessError: `should_check` was True and git exited
            non-zero.
        OSError: git is not installed, or `notes_dir` cannot be entered.
    """

    # Pinned to utf-8 rather than the locale default: under LC_ALL=C that
    # default is ASCII, and note filenames and commit subjects carry em dashes.
    return subprocess.run(
        ["git", "-C", str(notes_dir), *args],
        capture_output=True, text=True, encoding="utf-8", check=should_check,
    )


def is_repo(notes_dir):
    """
    Say whether a directory is a git repository.

    Args:
        notes_dir (str or pathlib.Path): the candidate directory.

    Returns:
        bool: True when it holds a `.git` directory. False when it does not, or
        when the directory itself is absent.

    Raises:
        None
    """

    return (Path(notes_dir) / ".git").is_dir()


def remote_url(notes_dir, name="origin"):
    """
    Read a remote's URL.

    Args:
        notes_dir (str or pathlib.Path): the repository.
        name (str): the remote to look up. Defaults to "origin".

    Returns:
        str: the URL, or "" when the remote is not configured or the directory
        is not a repository.

    Raises:
        OSError: git is not installed.
    """

    if not is_repo(notes_dir):
        return ""

    result = _git(notes_dir, "remote", "get-url", name, should_check=False)

    return result.stdout.strip() if result.returncode == 0 else ""


def is_empty_dir(path):
    """
    Say whether a path is absent or an empty directory.

    Args:
        path (str or pathlib.Path): the candidate directory.

    Returns:
        bool: True when it does not exist or holds nothing at all. False when
        it holds anything, including hidden entries.

    Raises:
        OSError: it exists but cannot be listed.
    """

    path = Path(path)
    if not path.exists():
        return True

    return path.is_dir() and not any(path.iterdir())


def notes_repo_state(notes_dir, remote):
    """
    Work out what a notes directory looks like, without changing anything.

    Pure by design: a caller reports the result and lets the owner act, so
    "nothing happened" is structurally true rather than a promise.

    Args:
        notes_dir (str or pathlib.Path): the configured notes directory.
        remote (str): the configured remote, or "" when there is none.

    Returns:
        RepoState: which case holds. See RepoState for the meaning of each.

    Raises:
        OSError: the directory exists but cannot be listed, or git is missing.
    """

    if is_empty_dir(notes_dir):
        return RepoState.ABSENT

    if not is_repo(notes_dir):
        return RepoState.NOT_A_REPO

    configured = remote_url(notes_dir)

    # No remote on either side is a coherent local-only setup, not a mismatch.
    if not configured:
        return RepoState.NO_REMOTE if remote else RepoState.READY

    if remote and configured != remote:
        return RepoState.REMOTE_DIFFERS

    return RepoState.READY


class lock:
    """
    Serialize sync runs against one notes directory.

    A context manager over `os.mkdir`, which is atomic on every filesystem this
    runs on. Deliberately not `flock`: macOS does not have the flock(1) utility
    and the fcntl semantics differ across the two platforms, whereas "make a
    directory, fail if it exists" behaves identically everywhere.

    Two agents on one machine can finish work at the same moment, and git has
    no interest in being driven concurrently — an interleaved `add` and `rebase`
    against one repository produces states neither caller expected.

    Args:
        notes_dir (str or pathlib.Path): the repository to lock.

    Returns:
        None

    Raises:
        None
    """

    def __init__(self, notes_dir):
        """
        Record where the lock will live.

        Args:
            notes_dir (str or pathlib.Path): the repository to lock.

        Returns:
            None

        Raises:
            None
        """

        self.path = Path(notes_dir) / LOCK_RELPATH

    def __enter__(self):
        """
        Take the lock, or report who already holds it.

        Returns:
            lock: self, so `with lock(d) as held:` has something to bind.

        Args:
            None

        Raises:
            LockHeld: the lock directory already exists.
            OSError: the lock cannot be created for any other reason — a
                read-only filesystem, a missing .git directory.
        """

        try:
            os.mkdir(self.path)
        except FileExistsError:
            raise LockHeld(self.path, self._holder()) from None

        # Written after the mkdir, never before: the directory is the lock, and
        # this is only so a stuck one can be traced to a process.
        (self.path / "pid").write_text(f"{os.getpid()}\n", encoding="utf-8")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Release the lock, including when the body raised.

        Args:
            exc_type (type or None): the exception class, if one is propagating.
            exc_value (BaseException or None): the exception itself.
            traceback (types.TracebackType or None): its traceback.

        Returns:
            bool: False always, so an exception in the body keeps propagating.
            Swallowing it here would turn a conflict into a silent success.

        Raises:
            None
        """

        # Best-effort: a lock we cannot remove is a problem, but raising here
        # would replace whatever real error the body was already reporting.
        try:
            (self.path / "pid").unlink()
        except OSError:
            pass

        try:
            self.path.rmdir()
        except OSError:
            pass

        return False

    def _holder(self):
        """
        Read the process id recorded in an existing lock.

        Args:
            None

        Returns:
            str: the recorded pid, or "" when it cannot be read. A lock whose
            owner is unknown still counts as held — an unreadable pid is a
            reason to be more careful, not less.

        Raises:
            None
        """

        try:
            return (self.path / "pid").read_text(encoding="utf-8").strip()
        except OSError:
            return ""


def has_upstream(notes_dir):
    """
    Say whether the current branch tracks a remote branch.

    Args:
        notes_dir (str or pathlib.Path): the repository.

    Returns:
        bool: True when `@{u}` resolves. False on a branch that was never
        pushed, or in a repository with no remote at all.

    Raises:
        OSError: git is not installed.
    """

    return _git(notes_dir, "rev-parse", "--abbrev-ref", "@{u}", should_check=False).returncode == 0


def has_unpushed(notes_dir):
    """
    Say whether this clone holds commits the remote does not.

    Args:
        notes_dir (str or pathlib.Path): the repository.

    Returns:
        bool: True when there is at least one commit ahead of the upstream.
        False when it is level, or when there is no upstream to compare with —
        a branch nobody has pushed has nothing to be ahead *of*.

    Raises:
        OSError: git is not installed.
    """

    # Redundant with the returncode check below — with no upstream, `@{u}` does
    # not resolve and git exits 128, so that check alone would already yield
    # False. Kept because it states the intent: there is nothing to be ahead of.
    # Change one and the other still holds; remove both and this returns True on
    # a repo with no remote, which would make the CLI claim it pushed.
    if not has_upstream(notes_dir):
        return False

    result = _git(notes_dir, "rev-list", "--count", "@{u}..HEAD", should_check=False)

    return result.returncode == 0 and result.stdout.strip() not in ("", "0")


def incoming_delta(notes_dir):
    """
    Fetch, then report what the remote has that this clone does not.

    The point of this is the agent nudge: before writing a note, a caller needs
    to know whether the file it is about to write changed elsewhere, so it can
    re-read and reconcile rather than overwrite.

    Args:
        notes_dir (str or pathlib.Path): the repository.

    Returns:
        tuple: (paths, subjects) — [str] repo-relative files that differ, and
        [str] commit subjects, both oldest first. ("", "") is not returned;
        two empty lists mean already current, or nothing to compare against.

    Raises:
        OSError: git is not installed.
    """

    if not has_upstream(notes_dir):
        return ([], [])

    # Failure here is offline, which is not an error: the delta is then simply
    # whatever was already fetched, and the caller carries on working locally.
    _git(notes_dir, "fetch", "--quiet", should_check=False)

    paths    = _git(notes_dir, "diff", "--name-only", "HEAD..@{u}", should_check=False)
    subjects = _git(notes_dir, "log", "--format=%s", "HEAD..@{u}", should_check=False)

    return (
        [line for line in paths.stdout.splitlines() if line.strip()],
        [line for line in reversed(subjects.stdout.splitlines()) if line.strip()],
    )


def conflicted_paths(notes_dir):
    """
    List the files git currently reports as unmerged.

    Args:
        notes_dir (str or pathlib.Path): the repository.

    Returns:
        list: [str] repo-relative paths, sorted. Empty when nothing is
        conflicted.

    Raises:
        OSError: git is not installed.
    """

    result = _git(notes_dir, "diff", "--name-only", f"--diff-filter={DIFF_FILTER_UNMERGED}",
                  should_check=False)

    return sorted(line for line in result.stdout.splitlines() if line.strip())


@dataclass(frozen=True)
class SyncStatus:
    """
    Everything a caller needs to know about a notes setup, gathered once.

    Frozen because it describes the setup as it was read: nothing acts on this
    record, so nothing should be able to edit it and hand it on as fact.

    Args:
        notes_dir (pathlib.Path): the configured notes directory.
        does_exist (bool): whether that directory is there at all.
        state (RepoState): how it stands relative to the configured remote.
        configured_remote (str): the remote the config names, or "".
        actual_remote (str): the remote the repository names, or "".
        has_upstream (bool): whether the branch tracks a remote branch.
        unpushed (int): commits this clone holds that the remote does not, as of
            the last fetch. 0 when there is no upstream.
        uncommitted (int): files changed but not committed.
        last_commit (str): subject and date of the newest commit, or "" when
            there are none.
        note_count (int): how many `.md` files are under the directory, so an
            empty setup is distinguishable from a working one.
        branch (str): the checked-out branch, or "" on a detached HEAD. Empty is
            the interesting case: there is then no branch to push, which no
            other field in this record would reveal.

    Returns:
        None

    Raises:
        None
    """

    notes_dir:         Path
    does_exist:        bool
    state:             RepoState
    configured_remote: str  = ""
    actual_remote:     str  = ""
    has_upstream:      bool = False
    unpushed:          int  = 0
    uncommitted:       int  = 0
    last_commit:       str  = ""
    note_count:        int  = 0
    branch:            str  = ""

    @property
    def is_ready_to_sync(self):
        """
        Whether a sync would actually reach a remote.

        Args:
            None

        Returns:
            bool: True only when the directory is a repository whose remote
            matches the config and whose branch has an upstream. Local-only is
            deliberately not "ready": the notes work, but nothing syncs.

        Raises:
            None
        """

        return self.state is RepoState.READY and self.has_upstream


def status(notes_dir, remote):
    """
    Read the whole notes setup without changing or fetching anything.

    No fetch: a status command that hangs on a slow network is one nobody runs,
    and the counts being "as of the last fetch" is worth saying rather than
    worth waiting for.

    Args:
        notes_dir (str or pathlib.Path or None): the configured directory, or
            None when nothing is configured.
        remote (str): the configured remote, or "".

    Returns:
        SyncStatus: the setup as read.

    Raises:
        OSError: the directory exists but cannot be listed, or git is missing.
    """

    if notes_dir is None:
        return SyncStatus(notes_dir=Path(""), does_exist=False, state=RepoState.ABSENT)

    notes_dir = Path(notes_dir)
    if not notes_dir.is_dir():
        return SyncStatus(notes_dir=notes_dir, does_exist=False, state=RepoState.ABSENT,
                          configured_remote=remote)

    notes = sum(1 for _ in notes_dir.rglob("*.md"))
    state = notes_repo_state(notes_dir, remote)

    if not is_repo(notes_dir):
        return SyncStatus(notes_dir=notes_dir, does_exist=True, state=state,
                          configured_remote=remote, note_count=notes)

    ahead  = _git(notes_dir, "rev-list", "--count", "@{u}..HEAD", should_check=False)
    dirty  = _git(notes_dir, "status", "--porcelain", should_check=False)
    latest = _git(notes_dir, "log", "-1", "--format=%ad  %s", "--date=format:%Y-%m-%d %H:%M",
                  should_check=False)

    # Non-zero on a detached HEAD, which is the whole point of asking: there is
    # then no branch to push and nothing else in this report would say so.
    head = _git(notes_dir, "symbolic-ref", "--short", "-q", "HEAD", should_check=False)

    return SyncStatus(
        notes_dir         = notes_dir,
        does_exist        = True,
        state             = state,
        configured_remote = remote,
        actual_remote     = remote_url(notes_dir),
        has_upstream      = has_upstream(notes_dir),
        unpushed          = int(ahead.stdout.strip() or 0) if ahead.returncode == 0 else 0,
        uncommitted       = len([l for l in dirty.stdout.splitlines() if l.strip()]),
        last_commit       = latest.stdout.strip() if latest.returncode == 0 else "",
        note_count        = notes,
        branch            = head.stdout.strip() if head.returncode == 0 else "",
    )


def pull(notes_dir):
    """
    Bring in remote work, refusing to resolve anything.

    Rebase rather than merge so the history stays a straight line — a notes
    repo read by a person benefits from that far more than from merge commits
    recording which machine wrote when. `--autostash` so an edit in progress
    does not block the pull and is put back afterwards.

    Args:
        notes_dir (str or pathlib.Path): the repository.

    Returns:
        tuple: (paths, subjects) — what came in, as incoming_delta() reports it,
        computed before the pull so the caller can see what changed. Two empty
        lists mean there was nothing to bring in.

    Raises:
        ConflictError: the rebase hit a real conflict. It is aborted first, so
            the working tree is left exactly as it was.
        NotARepoError: `notes_dir` is not a git repository.
        OSError: git is not installed.
    """

    if not is_repo(notes_dir):
        raise NotARepoError(notes_dir)

    delta = incoming_delta(notes_dir)

    if not has_upstream(notes_dir):
        return delta

    stashes_before = _stash_count(notes_dir)

    result = _git(notes_dir, "pull", "--rebase", "--autostash", "--quiet", should_check=False)

    # Checked regardless of the exit code. `git pull --rebase --autostash` exits
    # ZERO when the rebase itself succeeds but re-applying the autostash
    # conflicts — it prints "Applying autostash resulted in conflicts" and
    # leaves markers in the working tree. Trusting the status code there let
    # `git add -A` stage those markers as content and push them to the remote,
    # while every line of output said the sync had worked.
    paths = conflicted_paths(notes_dir)

    if result.returncode == 0 and not paths:
        return delta

    # Only one of these two can be in progress, and each ignores its own failure:
    # whichever did not happen has nothing to abort, and saying so would bury
    # the real outcome.
    _git(notes_dir, "rebase", "--abort", should_check=False)

    # An autostash conflict leaves no rebase to abort, so the markers are still
    # in the tree. They are safe to discard ONLY because the pull put the local
    # edits in a stash first — checked, not assumed, because resetting without
    # one would destroy uncommitted work.
    was_stashed = bool(paths) and _stash_count(notes_dir) > stashes_before
    if was_stashed:
        _git(notes_dir, "reset", "--hard", "HEAD", should_check=False)

    # A pull can fail without conflicting — no network, a rejected fetch. Those
    # are not this function's problem: the caller works locally and tries later.
    if not paths and "conflict" not in (result.stderr + result.stdout).lower():
        return delta

    raise ConflictError(paths, has_stashed_work=was_stashed)


def _stash_count(notes_dir):
    """
    Count the entries on the stash.

    Used to tell a stash this pull created from one that was already there: the
    difference is what makes discarding a conflicted working tree safe.

    Args:
        notes_dir (str or pathlib.Path): the repository.

    Returns:
        int: how many stash entries exist. 0 when there are none, or when the
        stash ref does not exist at all.

    Raises:
        OSError: git is not installed.
    """

    result = _git(notes_dir, "stash", "list", should_check=False)

    return len([line for line in result.stdout.splitlines() if line.strip()])


def commit_all(notes_dir, message):
    """
    Stage everything and commit, unless there is nothing to commit.

    Args:
        notes_dir (str or pathlib.Path): the repository.
        message (str): the commit message. Used verbatim.

    Returns:
        bool: True when a commit was made, False when the tree was already
        clean. False is the ordinary case for a sync run after a sync run, so
        it is a return value rather than an exception.

    Raises:
        NotARepoError: `notes_dir` is not a git repository.
        subprocess.CalledProcessError: the add or the commit failed.
        OSError: git is not installed.
    """

    if not is_repo(notes_dir):
        raise NotARepoError(notes_dir)

    # -A rather than `.` so this does not depend on the working directory. They
    # happen to be identical here — _git pins the cwd to the repo root with -C,
    # and since git 2.0 `add .` stages deletions too — but the guarantee should
    # come from the flag rather than from that coincidence holding.
    _git(notes_dir, "add", "-A")

    # --quiet makes this exit non-zero when there IS something staged, so a
    # zero return means nothing to do. Checking the index directly beats
    # parsing `status`, which changes format with configuration.
    if _git(notes_dir, "diff", "--cached", "--quiet", should_check=False).returncode == 0:
        return False

    _git(notes_dir, "commit", "--quiet", "--message", message)

    return True


def push(notes_dir):
    """
    Push, retrying once behind a pull, and treating failure as tolerable.

    Args:
        notes_dir (str or pathlib.Path): the repository.

    Returns:
        bool: True when the push landed. False when there is no upstream to
        push to, or when it failed and is worth trying again later. False is
        not an error: the commit is already local, and refusing to finish would
        block work over a network problem.

    Raises:
        ConflictError: the retry's pull hit a real conflict.
        NotARepoError: `notes_dir` is not a git repository.
        OSError: git is not installed.
    """

    if not is_repo(notes_dir):
        raise NotARepoError(notes_dir)

    if not has_upstream(notes_dir):
        return False

    if _git(notes_dir, "push", "--quiet", should_check=False).returncode == 0:
        return True

    # The ordinary cause is someone else pushing first, which a rebase fixes.
    # pull() raises on a real conflict, which is the right outcome: a rejected
    # push hiding a conflict must not look like "offline, try later".
    pull(notes_dir)

    return _git(notes_dir, "push", "--quiet", should_check=False).returncode == 0
