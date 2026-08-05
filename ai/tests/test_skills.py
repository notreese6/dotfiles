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


class TestShippedSkillsAreLoadable(unittest.TestCase):
    """
    Covers the frontmatter every skill this repo ships has to carry.
    """

    def shipped(self):
        """
        List the skills in this repo, as (directory name, SKILL.md text).

        Args:
            None

        Returns:
            list: [(str, str)] one pair per skill directory holding a SKILL.md,
            sorted by name. Empty only if the repo ships no skills.

        Raises:
            OSError: a SKILL.md exists but cannot be read.
        """

        root = REPO_ROOT / "ai" / "skills"

        return sorted((p.parent.name, p.read_text(encoding="utf-8"))
                      for p in root.glob("*/SKILL.md"))

    def test_every_shipped_skill_declares_a_name_matching_its_directory(self):
        for name, text in self.shipped():
            with self.subTest(skill=name):
                # link_skills only checks that a SKILL.md exists, so a skill
                # whose frontmatter is malformed or misnamed links cleanly and
                # then never loads — the failure is silence, in the one
                # mechanism whose whole job is to load on demand.
                self.assertTrue(text.startswith("---\n"), "no frontmatter block")
                self.assertIn(f"\nname: {name}\n", text)

    def test_every_shipped_skill_describes_when_to_use_it(self):
        for name, text in self.shipped():
            with self.subTest(skill=name):
                front = text.split("---", 2)[1]
                after = front.split("description:", 1)

                # The description is the only thing an agent reads when deciding
                # whether to load a skill. An empty one is a skill that ships,
                # links, and is never chosen.
                self.assertEqual(len(after), 2, "no description")
                self.assertGreater(len(after[1].strip()), 40, "description too thin to match on")


class TestSkillsFollowTheirModule(SandboxedTestCase):
    """
    Covers a skill being dropped when the module that owns it is switched off.
    """

    def modules(self):
        """
        Build a throwaway ai/rules/ holding one optional module.

        Args:
            None

        Returns:
            list: [airules.Module] the discovered modules.

        Raises:
            OSError: the sandbox cannot be written.
        """

        rules = self.home / "ai" / "rules"
        rules.mkdir(parents=True, exist_ok=True)
        (rules / "notes.md").write_text(
            "<!-- ai-rules: order=20, default=on -->\n\n# Notes\n", encoding="utf-8")

        return airules.discover_modules(rules)

    def skill(self, name, owner=""):
        """
        Create a skill that optionally names an owning module.

        Args:
            name (str): the skill's directory name.
            owner (str): the module stem to declare, or "" to declare none.

        Returns:
            pathlib.Path: the skill directory.

        Raises:
            OSError: it cannot be written.
        """

        directory = self.home / "ai" / "skills" / name
        directory.mkdir(parents=True, exist_ok=True)
        declared = f"module: {owner}\n" if owner else ""
        (directory / "SKILL.md").write_text(
            f"---\nname: {name}\n{declared}description: probe\n---\n", encoding="utf-8")

        return directory

    def test_a_skill_is_dropped_when_its_module_is_switched_off(self):
        owned  = self.skill("notes-helper", owner="notes")
        kept   = self.skill("unowned")

        selected = airules.selected_skills([owned, kept], self.modules(), {"notes": False})

        # Saying no to a subject has to mean no to all of it. Before this, the
        # answer reached only the rules text, so the skill stayed linked and the
        # decline looked honoured while it was not.
        self.assertEqual(selected, [kept])

    def test_a_skill_is_kept_when_its_module_is_on(self):
        owned = self.skill("notes-helper", owner="notes")

        self.assertEqual(airules.selected_skills([owned], self.modules(), {"notes": True}), [owned])

    def test_an_unanswered_module_falls_back_to_its_own_default(self):
        owned = self.skill("notes-helper", owner="notes")

        # default=on, and a config that has never been asked must not silently
        # drop a skill the module itself says should be there.
        self.assertEqual(airules.selected_skills([owned], self.modules(), {}), [owned])

    def test_a_skill_naming_a_module_that_does_not_exist_is_kept(self):
        stale = self.skill("orphan", owner="no-such-module")

        # Removing guidance over a stale name in one file would be silent. The
        # assembly is where a missing module is a hard error; this is not.
        self.assertEqual(airules.selected_skills([stale], self.modules(), {}), [stale])

    def test_the_private_layer_is_unconditional_because_nothing_asks_about_it(self):
        private = self.skill("local-only")

        self.assertEqual(airules.skill_module(private), "")
        self.assertEqual(airules.selected_skills([private], self.modules(), {"notes": False}),
                         [private])

    def test_a_module_line_in_the_prose_is_not_a_declaration(self):
        directory = self.skill("prosey")
        (directory / "SKILL.md").write_text(
            "---\nname: prosey\ndescription: p\n---\n\nmodule: notes\n", encoding="utf-8")

        # Only the frontmatter declares. A skill explaining modules in its body
        # must not accidentally opt itself out of delivery.
        self.assertEqual(airules.skill_module(directory), "")

    def test_a_link_is_removed_once_its_module_goes_off(self):
        owned = self.skill("notes-helper", owner="notes")
        roots = {airules.RulesRoot.HOME: self.home, airules.RulesRoot.CONFIG_DIR: self.xdg}
        claude = airules.SUPPORTED_AGENTS["claude"]
        airules.link_skills(claude, roots, [owned])

        removed = airules.unlink_skills(claude, roots, [owned])

        # Filtering what gets linked is only half of it: a link made while the
        # module was on survives, so the skill stays in front of the agent and
        # the answer still looks ignored. Only visible on the second run.
        self.assertEqual(removed, ["notes-helper"])
        self.assertFalse((claude.skills_path(roots) / "notes-helper").exists())

    def test_a_real_directory_under_our_name_is_never_removed(self):
        owned  = self.skill("notes-helper", owner="notes")
        roots  = {airules.RulesRoot.HOME: self.home, airules.RulesRoot.CONFIG_DIR: self.xdg}
        claude = airules.SUPPORTED_AGENTS["claude"]

        theirs = claude.skills_path(roots) / "notes-helper"
        theirs.mkdir(parents=True)
        (theirs / "SKILL.md").write_text("MINE\n", encoding="utf-8")

        # Their own skill happens to share the name. Deleting it over a config
        # answer would destroy work this tool never created -- the one thing
        # that must not follow from turning a module off.
        self.assertEqual(airules.unlink_skills(claude, roots, [owned]), [])
        self.assertEqual((theirs / "SKILL.md").read_text(encoding="utf-8"), "MINE\n")

    def test_a_link_pointing_somewhere_else_is_left_alone(self):
        owned     = self.skill("notes-helper", owner="notes")
        elsewhere = self.home / "someone-elses" / "notes-helper"
        elsewhere.mkdir(parents=True)

        roots  = {airules.RulesRoot.HOME: self.home, airules.RulesRoot.CONFIG_DIR: self.xdg}
        claude = airules.SUPPORTED_AGENTS["claude"]
        claude.skills_path(roots).mkdir(parents=True, exist_ok=True)
        (claude.skills_path(roots) / "notes-helper").symlink_to(elsewhere, target_is_directory=True)

        # A symlink is not automatically ours. Same identity check link_skills
        # makes, so we can only ever take away what we put there.
        self.assertEqual(airules.unlink_skills(claude, roots, [owned]), [])
        self.assertTrue((claude.skills_path(roots) / "notes-helper").is_symlink())

    def test_removing_what_was_never_linked_is_not_an_error(self):
        owned  = self.skill("notes-helper", owner="notes")
        roots  = {airules.RulesRoot.HOME: self.home, airules.RulesRoot.CONFIG_DIR: self.xdg}

        self.assertEqual(airules.unlink_skills(airules.SUPPORTED_AGENTS["claude"], roots, [owned]), [])

    def test_the_hook_and_the_library_agree_on_the_notes_module_stem(self):
        text = (REPO_ROOT / "ai" / "hooks" / "notes-reminder").read_text(encoding="utf-8")

        # The hook duplicates the stem rather than importing it, to keep a
        # 2600-line import off every Stop event. This is what stops the two
        # drifting, which is the only thing sharing the constant would buy.
        self.assertIn(f'NOTES_MODULE_STEM = "{airules.NOTES_MODULE_STEM}"', text)


if __name__ == "__main__":
    unittest.main()
