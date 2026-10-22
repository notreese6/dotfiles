import json
import subprocess
import unittest
from datetime import date

from base import REPO_ROOT, SandboxedTestCase

HOOK = REPO_ROOT / "ai" / "hooks" / "notes-reminder"


class TestNotesReminder(SandboxedTestCase):
    """
    Covers the Stop hook that asks whether today's work has been written down.
    """

    def setUp(self):
        """
        Point the hook at a sandboxed config, state directory and notes tree.

        Args:
            None

        Returns:
            None

        Raises:
            OSError: the sandbox cannot be written.
        """

        super().setUp()

        self.notes = self.home / "notes"
        self.state = self.home / "state"
        self.notes.mkdir()

        (self.xdg / "ai-notes").mkdir(parents=True)
        (self.xdg / "ai-notes" / "config.json").write_text(
            json.dumps({"notes_path": str(self.notes)}), encoding="utf-8")

    def fire(self, **payload):
        """
        Run the hook with a payload and return what it decided.

        Args:
            **payload: the hook input, e.g. session_id="s1".

        Returns:
            dict: the parsed decision, or {} when the hook stayed silent.

        Raises:
            AssertionError: the hook exited non-zero, which it never may — a
                hook that fails a turn over a note is worse than the problem.
        """

        result = subprocess.run(
            ["python3", str(HOOK)],
            input=json.dumps(payload), capture_output=True, text=True,
            env={**self.env(), "NOTES_REMINDER_STATE_DIR": str(self.state)})

        self.assertEqual(result.returncode, 0, result.stderr)

        return json.loads(result.stdout) if result.stdout.strip() else {}

    def env(self):
        """
        The environment the hook should run under.

        Args:
            None

        Returns:
            dict: a copy of the current environment, already pointed at the
            sandboxed HOME and XDG_CONFIG_HOME by the base class.

        Raises:
            None
        """

        import os

        return dict(os.environ)

    def write_todays_note(self):
        """
        Create a note for today, as a session that logged its work would.

        Args:
            None

        Returns:
            None

        Raises:
            OSError: it cannot be written.
        """

        day = self.notes / date.today().isoformat()
        day.mkdir(parents=True, exist_ok=True)
        (day / "dotfiles.md").write_text("# logged\n", encoding="utf-8")

    def test_it_asks_when_nothing_has_been_written_today(self):
        self.assertEqual(self.fire(session_id="s1").get("decision"), "block")

    def test_it_asks_only_once_per_session(self):
        self.fire(session_id="s1")

        # Stop fires at the end of every turn. Asking each time is how the prose
        # version of this rule became wallpaper in the first place.
        self.assertEqual(self.fire(session_id="s1"), {})

    def test_a_new_session_is_asked_again(self):
        self.fire(session_id="s1")

        self.assertEqual(self.fire(session_id="s2").get("decision"), "block")

    def test_it_stays_quiet_once_today_has_a_note(self):
        self.write_todays_note()

        self.assertEqual(self.fire(session_id="s1"), {})

    def test_it_does_not_block_itself_into_a_loop(self):
        # Set once the hook has already blocked. Blocking again from here is
        # exactly how a Stop hook never lets a turn finish.
        self.assertEqual(self.fire(session_id="s1", stop_hook_active=True), {})

    def test_an_unconfigured_machine_is_not_nagged(self):
        (self.xdg / "ai-notes" / "config.json").unlink()

        self.assertEqual(self.fire(session_id="s1"), {})

    def test_a_broken_config_is_silent_rather_than_fatal(self):
        (self.xdg / "ai-notes" / "config.json").write_text("{not json", encoding="utf-8")

        # Raising here would break every turn on that machine until someone
        # noticed the config, which is a far worse failure than a missed note.
        self.assertEqual(self.fire(session_id="s1"), {})

    def write_config(self, **extra):
        """
        Rewrite the sandboxed config with the notes path plus any extra keys.

        Args:
            **extra: additional top-level config keys, e.g. `modules`.

        Returns:
            None

        Raises:
            OSError: the config cannot be written.
        """

        (self.xdg / "ai-notes" / "config.json").write_text(
            json.dumps({"notes_path": str(self.notes), **extra}), encoding="utf-8")

    def test_declining_the_notes_module_stops_the_nagging(self):
        self.write_config(modules={"daily-notes": False})

        # Turning the module off does not clear notes_path, so reading the path
        # alone kept this hook asking about a subject that had just been
        # declined -- the one place the answer was visibly ignored.
        self.assertEqual(self.fire(session_id="s1"), {})

    def test_the_module_being_on_is_unaffected(self):
        self.write_config(modules={"daily-notes": True})

        self.assertIn("decision", self.fire(session_id="s1"))

    def test_a_config_with_no_modules_map_still_asks(self):
        # Predates the modules map, or was written by hand. Absent is not "off",
        # and treating it as off would silently retire the reminder on every
        # machine whose config has not been rewritten since.
        self.assertIn("decision", self.fire(session_id="s1"))

    def test_an_empty_payload_still_works(self):
        # Nothing guarantees a payload carries a session id, and falling over on
        # an empty one would take the hook out on whichever agent omits it.
        self.assertEqual(self.fire().get("decision"), "block")


if __name__ == "__main__":
    unittest.main()
