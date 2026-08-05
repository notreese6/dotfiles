import sys
import unittest
from pathlib import Path

from base import REPO_ROOT, SandboxedTestCase

sys.path.insert(0, str(REPO_ROOT / "ai" / "lib"))
import airules


class TestSkillDelivery(SandboxedTestCase):
    """
    Covers linking this repo's skills into each agent's skills directory.
    """

    def setUp(self):
        """
        Build a throwaway `ai/skills/` holding one well-formed skill.

        Args:
            None

        Returns:
            None

        Raises:
            OSError: the sandbox cannot be written.
        """

        super().setUp()

        self.ai = self.home / "ai"
        self.make_skill("demo-skill")

        self.roots = {
            airules.RulesRoot.HOME:       self.home,
            airules.RulesRoot.CONFIG_DIR: self.xdg,
        }
        self.claude = airules.SUPPORTED_AGENTS["claude"]

    def make_skill(self, name, body="probe\n"):
        """
        Create a skill directory in the throwaway repo.

        Args:
            name (str): the skill's directory name.
            body (str): text after the frontmatter.

        Returns:
            pathlib.Path: the skill directory.

        Raises:
            OSError: it cannot be written.
        """

        directory = self.ai / "skills" / name
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: probe\n---\n{body}", encoding="utf-8")

        return directory

    def agent_dir(self):
        """
        The sandboxed skills directory for the claude agent.

        Args:
            None

        Returns:
            pathlib.Path: the directory, which may not exist yet.

        Raises:
            None
        """

        return self.claude.skills_path(self.roots)

    def test_a_shipped_skill_is_linked_not_copied(self):
        linked, conflicts = airules.link_skills(self.claude, self.roots, airules.skill_sources(self.ai))

        self.assertEqual(linked, ["demo-skill"])
        self.assertEqual(conflicts, [])

        # A symlink rather than a copy is the whole point: three copies is the
        # drift this repo exists to prevent, and it had already happened once.
        self.assertTrue((self.agent_dir() / "demo-skill").is_symlink())

    def test_a_directory_without_a_skill_file_is_not_a_skill(self):
        (self.ai / "skills" / "half-written").mkdir(parents=True)

        linked, _ = airules.link_skills(self.claude, self.roots, airules.skill_sources(self.ai))

        # Linking one mid-write would put a broken skill in front of every agent.
        self.assertNotIn("half-written", linked)

    def test_skills_the_user_installed_are_left_alone(self):
        theirs = self.agent_dir() / "users-own"
        theirs.mkdir(parents=True)
        (theirs / "SKILL.md").write_text("mine\n", encoding="utf-8")

        airules.link_skills(self.claude, self.roots, airules.skill_sources(self.ai))

        # A working machine has over a hundred of these. Managing only the names
        # this repo ships is what makes the whole thing safe to run.
        self.assertEqual((theirs / "SKILL.md").read_text(encoding="utf-8"), "mine\n")

    def test_a_name_already_taken_is_reported_not_clobbered(self):
        taken = self.agent_dir() / "demo-skill"
        taken.mkdir(parents=True)
        (taken / "SKILL.md").write_text("NOT OURS\n", encoding="utf-8")

        linked, conflicts = airules.link_skills(self.claude, self.roots, airules.skill_sources(self.ai))

        self.assertEqual([name for name, _ in conflicts], ["demo-skill"])
        self.assertNotIn("demo-skill", linked)
        self.assertEqual((taken / "SKILL.md").read_text(encoding="utf-8"), "NOT OURS\n")

    def test_running_twice_changes_nothing(self):
        first, _  = airules.link_skills(self.claude, self.roots, airules.skill_sources(self.ai))
        second, _ = airules.link_skills(self.claude, self.roots, airules.skill_sources(self.ai))

        self.assertEqual(first, second)
        self.assertTrue((self.agent_dir() / "demo-skill").is_symlink())

    def test_a_stale_link_is_repointed_rather_than_called_a_conflict(self):
        elsewhere = self.home / "moved" / "demo-skill"
        elsewhere.mkdir(parents=True)
        self.agent_dir().mkdir(parents=True, exist_ok=True)
        (self.agent_dir() / "demo-skill").symlink_to(elsewhere, target_is_directory=True)

        linked, conflicts = airules.link_skills(self.claude, self.roots, airules.skill_sources(self.ai))

        # The repo moving is ordinary. Treating an outdated link of our own as
        # someone else's file would strand every agent on the old location.
        self.assertEqual(conflicts, [])
        self.assertEqual(linked, ["demo-skill"])
        self.assertEqual((self.agent_dir() / "demo-skill").resolve(),
                         (self.ai / "skills" / "demo-skill").resolve())

    def test_an_agent_with_no_skills_support_is_skipped_quietly(self):
        agent = airules.SupportedAgent(name="paper", root=airules.RulesRoot.HOME,
                                       relpath=("notes.txt",))

        self.assertEqual(airules.link_skills(agent, self.roots, airules.skill_sources(self.ai)), ([], []))

    def test_the_private_layer_ships_skills_too(self):
        private = self.home / "private" / "skills" / "local-only"
        private.mkdir(parents=True)
        (private / "SKILL.md").write_text("---\nname: local-only\ndescription: p\n---\n",
                                          encoding="utf-8")

        sources   = airules.skill_sources(self.ai, self.home / "private")
        linked, _ = airules.link_skills(self.claude, self.roots, sources)

        # The private layer lives outside the repo and is never committed, so its
        # skills cannot be merged on disk — they have to be collected separately
        # and delivered the same way.
        self.assertEqual(linked, ["demo-skill", "local-only"])

    def test_the_shared_repo_wins_a_name_clash_with_the_private_layer(self):
        private = self.home / "private" / "skills" / "demo-skill"
        private.mkdir(parents=True)
        (private / "SKILL.md").write_text("SHADOW\n", encoding="utf-8")

        sources = airules.skill_sources(self.ai, self.home / "private")

        # Shadowing a reviewed, travelling skill with something machine-local is
        # the harder failure to notice, so precedence follows argument order and
        # the repo is passed first.
        self.assertEqual([s.parent.parent for s in sources], [self.ai])

    def test_an_absent_private_layer_is_simply_no_skills(self):
        self.assertEqual(airules.skill_sources(self.ai, None),
                         airules.skill_sources(self.ai))
        self.assertEqual(airules.skill_sources(self.ai, self.home / "nope"),
                         airules.skill_sources(self.ai))

    def test_cursor_takes_skills_from_home_though_its_rules_do_not(self):
        cursor = airules.SUPPORTED_AGENTS["cursor"]

        # Cursor reads its rules out of a settings box, so its rules text is
        # parked beside the config — but it discovers skills on disk like the
        # others. Resolving both against one root would misplace one of them.
        self.assertEqual(cursor.rules_path(self.roots).parent, self.xdg)
        self.assertEqual(cursor.skills_path(self.roots), self.home / ".cursor" / "skills")


class TestOneAgentTable(SandboxedTestCase):
    """
    Covers the single agent definition every tool reads.
    """

    def test_every_agent_is_described_in_exactly_one_place(self):
        for agent in airules.SUPPORTED_AGENTS.values():
            # Rules, skills and hooks for one agent all come off one record. A
            # second table somewhere else is how they drift when one moves.
            self.assertTrue(agent.relpath)
            self.assertTrue(agent.skills_relpath)
            self.assertTrue(agent.hooks_relpath)

    def test_each_agent_translates_the_canonical_event_names(self):
        for agent in airules.SUPPORTED_AGENTS.values():
            for canonical in ("prompt_submit", "stop"):
                self.assertTrue(agent.native_event(canonical),
                                f"{agent.name} has no name for {canonical}")

    def test_an_unknown_event_is_empty_rather_than_an_error(self):
        agent = airules.SUPPORTED_AGENTS["claude"]

        # An agent with no equivalent for an event simply does not get that hook
        # wired, which must not be a crash for every other agent in the run.
        self.assertEqual(agent.native_event("no-such-event"), "")

    def test_adding_an_agent_needs_no_change_outside_the_table(self):
        added = airules.SupportedAgent(
            name="probe", root=airules.RulesRoot.HOME, relpath=("probe.md",),
            skills_relpath=(".probe", "skills"),
            hooks_relpath=(".probe", "hooks.json"), hooks_schema=airules.HOOKS_FLAT,
            hook_events=(("stop", "onStop"),))

        # Everything a caller needs comes off the record itself, so a new agent
        # is a row rather than a branch in each tool.
        roots = {airules.RulesRoot.HOME: self.home, airules.RulesRoot.CONFIG_DIR: self.xdg}
        self.assertEqual(added.hooks_path(roots), self.home / ".probe" / "hooks.json")
        self.assertEqual(added.skills_path(roots), self.home / ".probe" / "skills")
        self.assertEqual(added.native_event("stop"), "onStop")


if __name__ == "__main__":
    unittest.main()
