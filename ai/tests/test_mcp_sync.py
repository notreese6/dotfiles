import json
import os
import subprocess
import unittest

from base import REPO_ROOT, SandboxedTestCase


# Deliberately NOT in alphabetical order once flattened (zeta, alpha, mike):
# an order-preservation test against sorted fixture names is vacuous, because
# accidental sorting reproduces the fixture. That exact mutation survived the
# first version of this file.
GROUPED = {
    "always-have": {
        "zeta":  {"type": "http", "url": "https://example.com/zeta/mcp"},
        "alpha": {"type": "http", "url": "https://example.com/alpha/mcp"},
    },
    "ci-cd": {
        "mike": {"type": "http", "url": "https://example.com/mike/mcp",
                 "headers": {"X-Token": "sekrit"}},
    },
}


class TestMcpSync(SandboxedTestCase):
    """
    End-to-end tests for the mcp-sync command, run as a real subprocess.
    """

    def setUp(self):
        """
        Point the tool at a sandboxed source and target.

        Args:
            None

        Returns:
            None

        Raises:
            OSError: the sandbox cannot be written.
        """

        super().setUp()

        self.source = self.home / "mcp-servers.json"
        self.target = self.home / "claude.json"
        self.write_source(GROUPED)

    def write_source(self, groups):
        """
        Write the grouped source file.

        Args:
            groups (dict): {group: {name: definition}}.

        Returns:
            None

        Raises:
            OSError: the file cannot be written.
        """

        self.source.write_text(json.dumps(groups, indent=2), encoding="utf-8")

    def write_target(self, servers, **other_keys):
        """
        Write a live config carrying the given servers plus unrelated keys.

        Args:
            servers (dict): the mcpServers mapping.
            **other_keys: further top-level keys, standing in for the account
                state and history Claude keeps in the same file.

        Returns:
            None

        Raises:
            OSError: the file cannot be written.
        """

        self.target.write_text(
            json.dumps({"oauthAccount": "me", "projects": {"p": 1},
                        "mcpServers": servers, **other_keys}, indent=2),
            encoding="utf-8")

    def run_cli(self, *args):
        """
        Run mcp-sync in a subprocess against the sandbox.

        Args:
            *args (str): arguments after the command name.

        Returns:
            subprocess.CompletedProcess: the finished run, output captured as
            text. A non-zero exit is returned, not raised.

        Raises:
            OSError: the script is missing or not executable.
        """

        env                    = dict(os.environ)
        env["MCP_SYNC_SOURCE"] = str(self.source)
        env["MCP_SYNC_TARGET"] = str(self.target)

        return subprocess.run(
            [str(self.repo / "ai" / "bin" / "mcp-sync")] + list(args),
            capture_output=True, text=True, env=env)

    def live_servers(self):
        """
        Read the live mcpServers back, order preserved.

        Args:
            None

        Returns:
            dict: the target file's mcpServers mapping.

        Raises:
            OSError: the target is missing.
            ValueError: the target is not JSON.
        """

        return json.loads(self.target.read_text(encoding="utf-8"))["mcpServers"]

    # ---- status --------------------------------------------------------

    def test_status_is_clean_when_live_matches_source(self):
        self.write_target({"zeta":  GROUPED["always-have"]["zeta"],
                           "alpha": GROUPED["always-have"]["alpha"],
                           "mike":  GROUPED["ci-cd"]["mike"]})

        done = self.run_cli("status")

        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("[+] live matches source", done.stdout)

    def test_status_reports_missing_drifted_and_unmanaged_by_name(self):
        self.write_target({"alpha": {"type": "http", "url": "https://example.com/CHANGED"},
                           "extra": {"type": "http", "url": "https://example.com/extra"}})

        done = self.run_cli("status")

        # Exit status is the scriptable answer; the names are the human one.
        self.assertEqual(done.returncode, 11)
        self.assertIn("missing from live: zeta", done.stdout)
        self.assertIn("drifted (live differs from source): alpha", done.stdout)
        self.assertIn("unmanaged (live only — adopt or delete): extra", done.stdout)

    def test_status_counts_order_alone_as_drift(self):
        self.write_target({"mike":  GROUPED["ci-cd"]["mike"],
                           "alpha": GROUPED["always-have"]["alpha"],
                           "zeta":  GROUPED["always-have"]["zeta"]})

        done = self.run_cli("status")

        # Same content, wrong order. The layout is the organization, so losing
        # it silently would defeat the reason the source file is grouped.
        self.assertEqual(done.returncode, 11)
        self.assertIn("live order differs", done.stdout)

    def test_status_refuses_a_flat_source_with_a_pointer_to_the_fix(self):
        self.source.write_text(json.dumps(
            {"alpha": {"type": "http", "url": "https://example.com/alpha/mcp"}}),
            encoding="utf-8")
        self.write_target({})

        done = self.run_cli("status")

        self.assertEqual(done.returncode, 12)
        self.assertIn("looks flat", done.stderr)

    def test_status_refuses_one_server_in_two_groups(self):
        self.write_source({"a": {"dup": {"url": "https://x"}},
                           "b": {"dup": {"url": "https://x"}}})
        self.write_target({})

        done = self.run_cli("status")

        self.assertEqual(done.returncode, 12)
        self.assertIn("one server, one home", done.stderr)

    # ---- apply ---------------------------------------------------------

    def test_apply_lands_the_source_order_in_the_live_file(self):
        self.write_target({"mike": GROUPED["ci-cd"]["mike"]})

        done = self.run_cli("apply")

        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(list(self.live_servers()), ["zeta", "alpha", "mike"])

    def test_apply_keeps_unmanaged_entries_and_names_them(self):
        self.write_target({"extra": {"type": "http", "url": "https://example.com/extra"}})

        done = self.run_cli("apply")

        live = self.live_servers()
        self.assertEqual(list(live), ["zeta", "alpha", "mike", "extra"])
        self.assertIn("kept unmanaged: extra", done.stdout)

    def test_apply_overwrites_a_drifted_managed_definition(self):
        self.write_target({"zeta": {"type": "http", "url": "https://example.com/WRONG"}})

        self.run_cli("apply")

        # Source of truth wins for managed names; that is the whole contract.
        self.assertEqual(self.live_servers()["zeta"], GROUPED["always-have"]["zeta"])

    def test_apply_leaves_every_other_top_level_key_alone(self):
        self.write_target({}, history=["h1"], theme="dark")

        self.run_cli("apply")

        written = json.loads(self.target.read_text(encoding="utf-8"))
        for key, value in (("oauthAccount", "me"), ("projects", {"p": 1}),
                           ("history", ["h1"]), ("theme", "dark")):
            self.assertEqual(written[key], value)

    def test_apply_backs_up_the_target_before_touching_it(self):
        self.write_target({"zeta": {"type": "http", "url": "https://example.com/WRONG"}})
        before = self.target.read_text(encoding="utf-8")

        done = self.run_cli("apply")

        backups = sorted((self.home / ".dotfiles-backup").rglob("claude.json"))
        self.assertTrue(backups, done.stdout)
        self.assertEqual(backups[-1].read_text(encoding="utf-8"), before)

    def test_apply_into_a_missing_target_creates_it(self):
        done = self.run_cli("apply")

        # A fresh machine has no ~/.claude.json yet; syncing into nothing is
        # the install-time case, not an error.
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(list(self.live_servers()), ["zeta", "alpha", "mike"])

    def test_apply_twice_reports_already_in_step_and_makes_no_backup_noise(self):
        self.write_target({})
        self.run_cli("apply")

        done = self.run_cli("apply")

        self.assertIn("already in step", done.stdout)

    # ---- adopt ---------------------------------------------------------

    def test_adopt_moves_a_live_only_server_into_the_named_group(self):
        self.write_target({"extra": {"type": "http", "url": "https://example.com/extra"}})

        done = self.run_cli("adopt", "extra", "--group", "ci-cd")

        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        groups = json.loads(self.source.read_text(encoding="utf-8"))
        self.assertIn("extra", groups["ci-cd"])

    def test_adopt_keeps_the_source_file_private(self):
        self.write_target({"extra": {"type": "http", "url": "https://example.com/extra"}})

        self.run_cli("adopt", "extra", "--group", "ci-cd")

        # The file carries credentials; an atomic replace writes a fresh inode
        # that would otherwise arrive world-readable.
        self.assertEqual(self.source.stat().st_mode & 0o777, 0o600)

    def test_adopt_refuses_an_unknown_group_and_lists_the_real_ones(self):
        self.write_target({"extra": {"type": "http", "url": "https://example.com/extra"}})

        done = self.run_cli("adopt", "extra", "--group", "nope")

        self.assertEqual(done.returncode, 12)
        self.assertIn("always-have", done.stderr)

    def test_adopt_refuses_a_name_that_is_already_managed(self):
        self.write_target({"zeta": GROUPED["always-have"]["zeta"]})

        done = self.run_cli("adopt", "zeta", "--group", "ci-cd")

        self.assertEqual(done.returncode, 12)
        self.assertIn("already managed", done.stderr)

    def test_adopt_refuses_a_name_the_live_config_does_not_hold(self):
        self.write_target({})

        done = self.run_cli("adopt", "ghost", "--group", "ci-cd")

        self.assertEqual(done.returncode, 12)
        self.assertIn("nothing to adopt", done.stderr)


if __name__ == "__main__":
    unittest.main()
