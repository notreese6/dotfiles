import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ai" / "lib"))

import airules

_ENV_KEYS = ("HOME", "XDG_CONFIG_HOME")


def _restore_env(saved):
    """
    Restore environment variables to a previously captured state.

    A key whose saved value is None was absent originally and is removed rather
    than set to an empty string, so callers cannot tell the sandbox ever ran.

    Args:
        saved (dict): {str: str or None} mapping env var name to its original
            value, where None means the variable was not set.

    Returns:
        None

    Raises:
        None
    """

    for key, value in saved.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


class SandboxedTestCase(unittest.TestCase):
    """
    Base test case that redirects HOME into a throwaway directory.

    Every test inheriting from this runs against a temp HOME and
    XDG_CONFIG_HOME, so nothing under test can read or overwrite the real
    ~/.claude/CLAUDE.md and ~/.codex/AGENTS.md.

    Attributes set for subclasses:
        repo (pathlib.Path): repository root.
        real_home (pathlib.Path): the user's actual home, for assertions only.
        home (pathlib.Path): the sandboxed HOME.
        xdg (pathlib.Path): the sandboxed XDG_CONFIG_HOME, deliberately not
            home/".config" so tests can tell the two config_path branches apart.
    """

    def setUp(self):
        """
        Point HOME and XDG_CONFIG_HOME at a fresh temp directory.

        Restoration and temp-directory removal are registered via addCleanup, so
        they still run if a subclass overrides tearDown without calling super()
        or if setUp itself fails partway.

        Args:
            None

        Returns:
            None

        Raises:
            OSError: the temp directory cannot be created.
        """

        self.repo      = REPO_ROOT
        self.real_home = Path(os.path.expanduser("~"))

        # Registered as cleanups rather than in tearDown so a subclass that
        # overrides tearDown without calling super() cannot leak the sandboxed
        # HOME into the real environment.
        self.addCleanup(_restore_env, {k: os.environ.get(k) for k in _ENV_KEYS})
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

        # xdg is deliberately not home/".config" so tests can tell the XDG
        # branch of config_path() apart from the fallback branch.
        self.home = Path(self._tmp.name)
        self.xdg  = self.home / "xdg"

        os.environ["HOME"]            = str(self.home)
        os.environ["XDG_CONFIG_HOME"] = str(self.xdg)

    def backup_of(self, target):
        """
        Find where a displaced file was filed, without knowing the timestamp.

        Backups land in `~/.dotfiles-backup/<timestamp>/<path under home>`, and
        a test cannot predict the timestamp, so the tree is searched for the
        mirrored path instead.

        Args:
            target (pathlib.Path): the file that was replaced.

        Returns:
            pathlib.Path: the single backup of `target`. Points at a
            non-existent path when none was taken, so a caller asserting on its
            contents fails with a missing file rather than silently passing.

        Raises:
            AssertionError: more than one backup of `target` exists, which would
                make any assertion about "the" backup ambiguous.
        """

        root  = self.home / airules.BACKUP_DIRNAME
        found = sorted(root.glob(f"*/{target.relative_to(self.home)}")) if root.is_dir() else []

        assert len(found) < 2, f"expected at most one backup of {target}, found {found}"

        return found[0] if found else root / "never-taken" / target.name

    def write_config(self, **settings):
        """
        Put settings straight into the sandboxed config file.

        A fixture, not an API a shipped tool should reach for: airules.Config is
        the only supported way to write this file, so that `updated_at` cannot
        go stale. This bypasses it on purpose, which is what lets a test set up
        states Config cannot represent — a malformed `agents`, or a value that
        will not serialize.

        Args:
            **settings: keys to write, merged over whatever is already in the
                file rather than replacing it. Values may be any JSON type, and
                deliberately may be invalid, so error paths can be exercised.

        Returns:
            None

        Raises:
            OSError: the config file or its directory cannot be written.
            TypeError: a value is not JSON-serializable. Left to propagate, so a
                test can assert on it.
            ValueError: the existing config file is not valid JSON.
        """

        data = airules.config_read()
        data.update(settings)

        airules._config_write(data)
