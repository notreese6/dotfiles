import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "ai" / "lib"))

_ENV_KEYS = ("HOME", "XDG_CONFIG_HOME")


def _restore_env(saved):
    """Restore environment variables to a previously captured state.

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
    """Base test case that redirects HOME into a throwaway directory.

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
        """Point HOME and XDG_CONFIG_HOME at a fresh temp directory.

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
