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

    def test_types_survive_the_roundtrip(self):
        self.write_config(notes_enabled=False, agents=["claude", "codex"])

        self.assertIs(airules.config_get("notes_enabled"), False)
        self.assertEqual(airules.config_get("agents"), ["claude", "codex"])

    def test_file_is_valid_readable_json(self):
        airules.Config.load().save()

        data = json.loads(airules.config_path().read_text(encoding="utf-8"))
        self.assertEqual(data["agents"], ["claude"])

    def test_corrupt_config_raises_rather_than_silently_resetting(self):
        path = airules.config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{not json", encoding="utf-8")

        # Both entry points, because resetting a hand-edited config to defaults
        # on a stray character would discard settings with no way to get them back
        with self.assertRaises(ValueError):
            airules.config_read()

        with self.assertRaises(ValueError):
            airules.Config.load()

    def test_failed_save_leaves_no_temp_file_and_no_damage(self):
        self.write_config(agents=["claude"])

        config = airules.Config.load()
        config.extra["bad"] = object()

        with self.assertRaises(TypeError):
            config.save()

        # The scratch file is a sibling of the target, so a failed write that
        # left one behind would put junk in the user's config directory
        self.assertEqual(list(airules.config_path().parent.glob("*.tmp")), [])
        self.assertEqual(airules.config_get("agents"), ["claude"])

    def test_config_set_is_gone(self):
        # One writer only. A second one silently stops updated_at from meaning
        # what it says, which is exactly how it went stale before.
        self.assertFalse(hasattr(airules, "config_set"))

    def test_write_config_fixture_merges_rather_than_replacing(self):
        self.write_config(agents=["claude"])
        self.write_config(notes_path="/srv/notes")

        # Guards the fixture's own contract. Every test that seeds across more
        # than one call depends on it, and a helper that quietly started
        # replacing would drop the earlier keys and leave those tests passing
        # against defaults instead of what they set.
        self.assertEqual(airules.config_get("agents"), ["claude"])
        self.assertEqual(airules.config_get("notes_path"), "/srv/notes")

    def test_sandbox_is_not_real_home(self):
        parents = airules.config_path().parents
        self.assertIn(self.home, parents)
        self.assertNotIn(self.real_home, parents)


class TestConfigRecord(SandboxedTestCase):
    """
    Covers the Config record: load, save, round-tripping, and describe().
    """

    def test_absent_file_loads_usable_defaults(self):
        config = airules.Config.load()

        # A machine with no config yet has to be able to assemble anyway
        self.assertEqual(config.agents, ["claude"])
        self.assertIs(config.notes_enabled, False)
        self.assertIsNone(config.notes_path)

    def test_round_trips_every_field(self):
        config = airules.Config.load()
        config.agents             = ["claude", "codex"]
        config.ai_dir             = self.home / "ai"
        config.local_rules_dir    = self.home / "ai" / "local_rules"
        config.local_rules_remote = "git@example.com:me/rules.git"
        config.notes_enabled      = True
        config.notes_path         = self.home / "daily-notes"
        config.save()

        loaded = airules.Config.load()

        self.assertEqual(loaded.agents, ["claude", "codex"])
        self.assertEqual(loaded.ai_dir, self.home / "ai")
        self.assertEqual(loaded.local_rules_dir, self.home / "ai" / "local_rules")
        self.assertEqual(loaded.local_rules_remote, "git@example.com:me/rules.git")
        self.assertIs(loaded.notes_enabled, True)
        self.assertEqual(loaded.notes_path, self.home / "daily-notes")

    def test_paths_come_back_as_paths(self):
        config           = airules.Config.load()
        config.notes_path = self.home / "daily-notes"
        config.save()

        # Stored as a string in JSON, so a caller doing notes_path / "x" would
        # break if load() handed the raw string back
        self.assertIsInstance(airules.Config.load().notes_path, type(self.home))

    def test_save_stamps_updated_at(self):
        airules.Config.load().save()

        self.assertRegex(airules.config_get("updated_at"), r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    def test_unknown_keys_survive_a_save(self):
        self.write_config(some_future_setting={"nested": [1, 2]})

        airules.Config.load().save()

        # An older tool saving must not drop a newer tool's settings, which is
        # the failure mode of building the file from known fields alone
        self.assertEqual(airules.config_get("some_future_setting"), {"nested": [1, 2]})
        self.assertEqual(airules.Config.load().extra["some_future_setting"], {"nested": [1, 2]})

    def test_agents_written_as_a_string_load_as_a_list(self):
        self.write_config(agents="claude codex")

        self.assertEqual(airules.Config.load().agents, ["claude", "codex"])

    def test_malformed_agents_raises(self):
        self.write_config(agents=5)

        with self.assertRaises(airules.BadAgentsError):
            airules.Config.load()

    def test_agents_list_holding_a_non_string_raises(self):
        self.write_config(agents=["claude", 7])

        with self.assertRaises(airules.BadAgentsError):
            airules.Config.load()

    def test_a_misspelled_field_raises_rather_than_defaulting(self):
        config = airules.Config.load()

        # The whole reason this is a record and not a bag of string keys:
        # config_get("noets_path") would hand back "" and read as configured
        with self.assertRaises(AttributeError):
            config.noets_path

    def test_describe_covers_every_setting_and_aligns(self):
        config            = airules.Config.load()
        config.notes_path = self.home / "daily-notes"

        lines = config.describe()

        self.assertTrue(any("notes path:" in line for line in lines))
        self.assertTrue(any("agents:" in line for line in lines))

        # Values line up in a column, so the block scans as a table. Measured as
        # the first non-space after the colon; splitting on ": " instead would
        # move with the label length and pass no matter how ragged the output.
        columns = set()
        for line in lines:
            after = line[line.index(":") + 1:]
            columns.add(len(line) - len(after) + (len(after) - len(after.lstrip())))

        self.assertEqual(len(columns), 1, lines)

    def test_describe_shows_unset_values_as_none_not_blank(self):
        lines = airules.Config.load().describe()

        # A blank right-hand side reads as a setting that failed to print
        self.assertTrue(any("(none)" in line for line in lines))

    def test_unset_paths_are_left_out_rather_than_written_null(self):
        airules.Config.load().save()

        data = json.loads(airules.config_path().read_text(encoding="utf-8"))

        self.assertNotIn("notes_path", data)
        self.assertIsNone(airules.Config.load().notes_path)


if __name__ == "__main__":
    unittest.main()
