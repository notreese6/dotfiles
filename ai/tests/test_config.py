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
        self.write_config(agents=["claude", "codex"])

        self.assertEqual(airules.config_get("agents"), ["claude", "codex"])
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
        self.assertIsNone(config.notes_path)

        # No answers at all, rather than a set of hard-coded per-module fields:
        # what each module does by default is declared by the module, so a
        # config that has never been asked simply says nothing.
        self.assertEqual(config.modules, {})

    def test_flat_module_flags_are_read_under_their_new_home(self):
        # Two generations of config in one: `notes_enabled` and `misc_enabled`
        # were top-level keys before per-module answers moved under `modules`.
        # Ignoring them would read as "off" and drop whole modules out of the
        # assembled rules on the next apply, saying nothing about it.
        self.write_config(notes_enabled=True, misc_enabled=True)

        self.assertEqual(airules.Config.load().modules, {"daily-notes": True, "misc": True})

    def test_the_oldest_flat_flag_is_read_too(self):
        # `universal_enabled` was what `misc_enabled` was called before the
        # module it gates was renamed
        self.write_config(universal_enabled=True)

        self.assertIs(airules.Config.load().modules["misc"], True)

    def test_flat_module_flags_do_not_survive_a_save(self):
        self.write_config(notes_enabled=True, universal_enabled=True)

        airules.Config.load().save()
        written = json.loads(airules.config_path().read_text(encoding="utf-8"))

        # Migrated, not duplicated: leaving both shapes on disk leaves a real
        # question about which one a later reader is supposed to believe.
        self.assertEqual(written["modules"], {"daily-notes": True, "misc": True})
        for stale in ("notes_enabled", "misc_enabled", "universal_enabled"):
            self.assertNotIn(stale, written)

    def test_the_newest_key_wins_when_several_answer_one_module(self):
        # All three shapes at once, disagreeing. `modules` is current, so it
        # decides; between the two flat ones the newer name decides.
        self.write_config(universal_enabled=True, misc_enabled=False)
        self.assertIs(airules.Config.load().modules["misc"], False)

        self.write_config(modules={"misc": True})
        self.assertIs(airules.Config.load().modules["misc"], True)

    def test_a_malformed_modules_value_is_ignored_not_fatal(self):
        self.write_config(modules="not a mapping")

        # One malformed setting must not stop every agent being written, on the
        # same grounds as an unreadable `order` in a module's own declaration
        self.assertEqual(airules.Config.load().modules, {})

    def test_defaults_are_declared_once(self):
        # load() must read its fallbacks off the record's own field defaults
        # rather than repeat them. Two copies of a default only disagree on a
        # machine with no config file — the one case nobody re-tests by hand.
        declared = airules.Config(agents=list(airules.DEFAULT_AGENTS))
        loaded   = airules.Config.load()

        for name in ("agents", "modules", "local_rules_remote", "updated_at"):
            with self.subTest(field=name):
                self.assertEqual(getattr(loaded, name), getattr(declared, name))

    def test_round_trips_every_field(self):
        config = airules.Config.load()
        config.agents             = ["claude", "codex"]
        config.ai_dir             = self.home / "ai"
        config.local_rules_dir    = self.home / "ai" / "local_rules"
        config.local_rules_remote = "git@example.com:me/rules.git"
        config.modules            = {"daily-notes": True, "misc": False}
        config.notes_path         = self.home / "daily-notes"
        config.save()

        loaded = airules.Config.load()

        self.assertEqual(loaded.agents, ["claude", "codex"])
        self.assertEqual(loaded.ai_dir, self.home / "ai")
        self.assertEqual(loaded.local_rules_dir, self.home / "ai" / "local_rules")
        self.assertEqual(loaded.local_rules_remote, "git@example.com:me/rules.git")
        self.assertEqual(loaded.modules, {"daily-notes": True, "misc": False})
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
