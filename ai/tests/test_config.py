import json
import os
import unittest
from base import SandboxedTestCase
import airules


class TestConfig(SandboxedTestCase):
    """
    Covers config_path resolution and the config read/write round-trip.
    """

    def test_config_path_follows_xdg(self):
        self.assertEqual(
            airules.config_path(),
            self.xdg / "ai-notes" / "config.json",
        )

    def test_config_path_falls_back_to_home_when_xdg_unset(self):
        os.environ.pop("XDG_CONFIG_HOME", None)
        self.assertEqual(
            airules.config_path(),
            self.home / ".config" / "ai-notes" / "config.json",
        )

    def test_read_returns_empty_dict_when_file_absent(self):
        self.assertEqual(airules.config_read(), {})

    def test_missing_key_returns_default(self):
        self.assertEqual(airules.config_get("nope", "DEFLT"), "DEFLT")

    def test_set_then_get_roundtrip(self):
        airules.config_set("agents", "claude codex")
        self.assertEqual(airules.config_get("agents"), "claude codex")

    def test_update_overwrites_in_place(self):
        airules.config_set("agents", "claude codex")
        airules.config_set("agents", "claude")
        self.assertEqual(airules.config_get("agents"), "claude")

    def test_other_keys_preserved(self):
        airules.config_set("notes_path", "/tmp/n")
        airules.config_set("agents", "claude")
        airules.config_set("notes_path", "/tmp/other")
        self.assertEqual(airules.config_get("agents"), "claude")
        self.assertEqual(airules.config_get("notes_path"), "/tmp/other")

    def test_types_survive_the_roundtrip(self):
        airules.config_set("notes_enabled", False)
        airules.config_set("agents", ["claude", "codex"])
        self.assertIs(airules.config_get("notes_enabled"), False)
        self.assertEqual(airules.config_get("agents"), ["claude", "codex"])

    def test_file_is_valid_readable_json(self):
        airules.config_set("notes_remote", "git@github.com:me/x.git")
        data = json.loads(airules.config_path().read_text(encoding="utf-8"))
        self.assertEqual(data["notes_remote"], "git@github.com:me/x.git")

    def test_corrupt_config_raises_rather_than_silently_resetting(self):
        path = airules.config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{not json", encoding="utf-8")
        with self.assertRaises(ValueError):
            airules.config_read()

    def test_failed_write_leaves_no_temp_file(self):
        airules.config_set("agents", "claude")
        with self.assertRaises(TypeError):
            airules.config_set("bad", object())
        leftovers = list(airules.config_path().parent.glob("*.tmp"))
        self.assertEqual(leftovers, [])
        self.assertEqual(airules.config_get("agents"), "claude")

    def test_sandbox_is_not_real_home(self):
        parents = airules.config_path().parents
        self.assertIn(self.home, parents)
        self.assertNotIn(self.real_home, parents)


if __name__ == "__main__":
    unittest.main()
