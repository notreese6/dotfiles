import unittest
from base import SandboxedTestCase
import airules

UNIVERSAL = "# Universal Rules\n\nAlways be concise.\n\nEnd of universal.\n"
NOTES     = "## Daily notes\n\nNOTES SYNC: pull before writing notes.\n"

# Markers of their own, so these exercise strip_block itself rather than
# whichever production constants happen to exist today.
MARK_BEGIN = "<!-- test-block:start -->"
MARK_END   = "<!-- test-block:end -->"


def _converge(universal, local_text, rounds=4, notes_enabled=False):
    """
    Apply assemble() repeatedly, feeding each result back in as the universal.

    Args:
        universal (str): starting universal rules text.
        local_text (str): local rules, passed unchanged to every round.
        rounds (int): how many times to apply assemble(). Must be >= 1.
        notes_enabled (bool): passed straight through to assemble().

    Returns:
        list: [str] the output of each round, in order, so a caller can compare
        later rounds against the first.

    Raises:
        None
    """

    outs = []
    text = universal

    for _ in range(rounds):
        text = airules.assemble(text + (NOTES if notes_enabled else ""), local_text)
        outs.append(text)

    return outs


class TestAssemble(SandboxedTestCase):
    """
    Covers marker stripping, local-rules reading, and rules assembly.
    """

    def _local_dir(self, **files):
        """
        Create a local-rules directory under the sandboxed HOME.

        Args:
            **files: {str: str} mapping file name to file body. Written into the
                directory as-is; names need not end in `.md`.

        Returns:
            pathlib.Path: the directory holding the written files.

        Raises:
            OSError: the directory or one of the files cannot be written.
        """

        d = self.home / "local_rules"
        d.mkdir(parents=True, exist_ok=True)
        for name, body in files.items():
            # Pinned so a non-ASCII fixture body still writes under LC_ALL=C.
            (d / name).write_text(body, encoding="utf-8")
        return d

    def _rules_dir(self, **files):
        """
        Create a rules-module directory under the sandboxed HOME.

        Args:
            **files: {str: str} module filename to body.

        Returns:
            pathlib.Path: the directory holding the written modules.

        Raises:
            OSError: the directory or one of the files cannot be written.
        """

        d = self.home / "rules"
        d.mkdir(parents=True, exist_ok=True)
        for name, body in files.items():
            (d / name).write_text(body, encoding="utf-8")
        return d

    def test_strip_marked_block_removes_block_and_markers(self):
        out = airules.strip_block(UNIVERSAL, MARK_BEGIN, MARK_END, should_repeat=True)
        self.assertNotIn("NOTES SYNC", out)
        self.assertNotIn(MARK_BEGIN, out)
        self.assertNotIn(MARK_END, out)
        self.assertIn("Always be concise.", out)
        self.assertIn("End of universal.", out)

    def test_strip_marked_block_is_noop_without_markers(self):
        out = airules.strip_block("plain\n", MARK_BEGIN, MARK_END, should_repeat=True)
        self.assertEqual(out, "plain\n")

    def test_strip_marked_block_removes_every_region(self):
        text = (
            "HEAD\n\n"
            + MARK_BEGIN + "\nFIRST NUDGE\n" + MARK_END + "\n"
            + "MIDDLE\n\n"
            + MARK_BEGIN + "\nSECOND NUDGE\n" + MARK_END + "\n"
            + "TAIL\n"
        )

        out = airules.strip_block(text, MARK_BEGIN, MARK_END, should_repeat=True)
        self.assertEqual(out, "HEAD\n\nMIDDLE\n\nTAIL\n")
        self.assertNotIn("FIRST NUDGE", out)
        self.assertNotIn("SECOND NUDGE", out)
        self.assertNotIn(MARK_BEGIN, out)
        self.assertNotIn(MARK_END, out)

    def test_strip_marked_block_ignores_markers_quoted_mid_line(self):
        text = "See " + MARK_BEGIN + " and " + MARK_END + " above.\n"
        self.assertEqual(airules.strip_block(text, MARK_BEGIN, MARK_END, should_repeat=True), text)

    def test_strip_local_ignores_markers_quoted_mid_line(self):
        text = "See " + airules.LOCAL_BEGIN + " and " + airules.LOCAL_END + " above.\n"
        self.assertEqual(airules.strip_block(text, airules.LOCAL_BEGIN, airules.LOCAL_END, should_use_last_end=True), text)

    def test_strip_local_closes_on_the_last_end_marker(self):
        text = (
            airules.LOCAL_BEGIN + "\n\nquoted:\n"
            + airules.LOCAL_END + "\n\n"
            + airules.LOCAL_END + "\nTAIL\n"
        )

        out = airules.strip_block(text, airules.LOCAL_BEGIN, airules.LOCAL_END, should_use_last_end=True)
        self.assertEqual(out, "TAIL\n")
        self.assertNotIn(airules.LOCAL_END, out)

    def test_strip_marked_block_unterminated_block_runs_to_end(self):
        text = "KEEP ME\n\n" + MARK_BEGIN + "\nDANGLING NOTES\ntrailing junk\n"

        out = airules.strip_block(text, MARK_BEGIN, MARK_END, should_repeat=True)
        self.assertEqual(out, "KEEP ME\n\n")
        self.assertNotIn(MARK_BEGIN, out)
        self.assertNotIn("DANGLING NOTES", out)
        self.assertNotIn("trailing junk", out)

    def test_strip_local_unterminated_block_runs_to_end(self):
        text = "KEEP ME\n\n" + airules.LOCAL_BEGIN + "\nDANGLING LOCAL\ntrailing junk\n"

        out = airules.strip_block(text, airules.LOCAL_BEGIN, airules.LOCAL_END, should_use_last_end=True)
        self.assertEqual(out, "KEEP ME\n\n")
        self.assertNotIn(airules.LOCAL_BEGIN, out)
        self.assertNotIn("DANGLING LOCAL", out)
        self.assertNotIn("trailing junk", out)

    def test_read_local_rules_sorted(self):
        d   = self._local_dir(**{"20-second.md": "TWO\n", "10-first.md": "ONE\n"})
        out = airules.read_local_rules(d)
        self.assertLess(out.index("ONE"), out.index("TWO"))

    def test_read_local_rules_empty_when_absent(self):
        self.assertEqual(airules.read_local_rules(self.home / "nope"), "")

    def test_read_local_rules_reads_only_markdown(self):
        d = self._local_dir(**{
            "10-real.md":   "REAL RULE\n",
            "notes.txt":    "NOT A RULE\n",
            "20-old.md~":   "EDITOR BACKUP\n",
            ".DS_Store":    "\x00\x01binary junk\n",
        })

        out = airules.read_local_rules(d)

        # Anything but *.md is someone else's file. Concatenating a stray note or
        # an editor backup would put it in every agent's rules, and a binary one
        # would fail the read outright.
        self.assertIn("REAL RULE", out)
        self.assertNotIn("NOT A RULE", out)
        self.assertNotIn("EDITOR BACKUP", out)
        self.assertNotIn("binary junk", out)

    def test_read_local_rules_skips_a_readme(self):
        d = self._local_dir(**{
            "10-real.md": "REAL RULE\n",
            "README.md":  "# my-rules\n\nTo push to this repo, run git push.\n",
            "readme.md":  "lowercase variant\n",
        })

        out = airules.read_local_rules(d)

        # A repo created through a web UI ships a boilerplate README. It is
        # markdown, so without this it lands in the rules and the agent reads
        # "to push to this repo, run git push" as an instruction.
        self.assertIn("REAL RULE", out)
        self.assertNotIn("git push", out)
        self.assertNotIn("lowercase variant", out)

    def test_read_local_rules_round_trips_non_ascii(self):
        body = "Rule — with an em dash\n"
        d    = self._local_dir(**{"10-dash.md": body})

        # assertIn rather than assertEqual: the text is wrapped in markers
        # naming its file now, so equality would be asserting the wrapper
        # rather than the encoding this test exists for.
        self.assertIn("Rule — with an em dash", airules.read_local_rules(d))

    def test_the_private_layer_honours_declared_order(self):
        d = self._local_dir(**{
            "10-first.md":  "FIRST RULE\n",
            "aardvark.md":  "<!-- ai-rules: order=1 -->\n\nAARDVARK RULE\n",
        })

        out = airules.read_local_rules(d)

        # Without this, ordering a private layer means renaming files. The
        # `10-`/`20-` prefix convention still works as the tie-break.
        self.assertLess(out.index("AARDVARK RULE"), out.index("FIRST RULE"))

    def test_the_private_layer_strips_its_front_matter(self):
        d = self._local_dir(**{"10-one.md": "<!-- ai-rules: order=3 -->\n\nPRIVATE RULE\n"})

        out = airules.read_local_rules(d)

        # It leaked verbatim into every agent's rules before, and the order it
        # declared was ignored — a declaration that did nothing but add noise
        self.assertIn("PRIVATE RULE", out)
        self.assertNotIn("ai-rules:", out)

    def test_the_private_layer_names_the_file_each_rule_came_from(self):
        d = self._local_dir(**{"10-one.md": "ONE\n", "20-two.md": "TWO\n"})

        out = airules.read_local_rules(d)

        # Several private files used to concatenate into one undifferentiated
        # blob, so a rule could not be traced back to the file to edit
        self.assertIn(airules.MODULE_END_TEMPLATE.format(name="10-one.md"), out)
        self.assertIn(airules.MODULE_END_TEMPLATE.format(name="20-two.md"), out)

    def test_a_private_file_declaring_nothing_still_applies(self):
        d = self._local_dir(**{"10-plain.md": "PLAIN PRIVATE RULE\n"})

        # The opposite of a shareable module, which is off unless it says
        # otherwise. A private file is there because someone put it there.
        self.assertIn("PLAIN PRIVATE RULE", airules.read_local_rules(d))

    def test_a_private_file_can_be_shelved_without_deleting_it(self):
        d = self._local_dir(**{
            "10-live.md":    "LIVE RULE\n",
            "20-shelved.md": "<!-- ai-rules: default=off -->\n\nSHELVED RULE\n",
        })

        out = airules.read_local_rules(d)

        # `default=off` has to mean something here, or it is a declaration that
        # silently does nothing — which is what it did before.
        self.assertIn("LIVE RULE", out)
        self.assertNotIn("SHELVED RULE", out)

    def test_assemble_without_local_has_no_local_block(self):
        out = airules.assemble(UNIVERSAL, "   \n")
        self.assertNotIn(airules.LOCAL_BEGIN, out)
        self.assertNotIn(airules.LOCAL_END, out)

    def test_modules_sort_by_declared_order_not_by_filename(self):
        d = self.home / "rules"
        self.write_module(d, "zzz.md", "FIRST RULE\n", front="order=10")
        self.write_module(d, "aaa.md", "SECOND RULE\n", front="order=20")

        out = airules.read_modules(airules.discover_modules(d))

        # Alphabetically aaa precedes zzz. Declared order has to beat that, or
        # the tool's own rules could not be pinned to the top of the document.
        self.assertLess(out.index("FIRST RULE"), out.index("SECOND RULE"))

    def test_modules_with_equal_order_fall_back_to_the_filename(self):
        d = self.home / "rules"
        self.write_module(d, "bbb.md", "BEE RULE\n", front="order=40")
        self.write_module(d, "aaa.md", "AYE RULE\n", front="order=40")

        out = airules.read_modules(airules.discover_modules(d))

        # A tie must not be broken by whatever order the filesystem hands back,
        # or the assembled file would differ between machines for no reason
        self.assertLess(out.index("AYE RULE"), out.index("BEE RULE"))

    def test_a_module_declaring_nothing_still_works(self):
        d = self.home / "rules"
        self.write_module(d, "plain.md", "# Plain\n\nPLAIN RULE\n")

        module, = airules.discover_modules(d)

        # Dropping in a file with no declaration is the simplest thing someone
        # can do, so it has to work: asked about, off unless you say yes.
        self.assertEqual(module.stem, "plain")
        self.assertEqual(module.order, airules.DEFAULT_MODULE_ORDER)
        self.assertFalse(module.is_required)
        self.assertFalse(module.is_on_by_default)
        self.assertEqual(module.title, "Plain")

    def test_a_readme_in_the_rules_directory_is_not_a_module(self):
        d = self.home / "rules"
        self.write_module(d, "real.md",  "REAL RULE\n")
        self.write_module(d, "README.md", "To push to this repo, run git push.\n")

        stems = [m.stem for m in airules.discover_modules(d)]

        # Load-bearing now that this directory is globbed rather than listed: a
        # boilerplate README would otherwise be read to every agent as rules.
        self.assertEqual(stems, ["real"])

    def test_discovery_of_a_missing_directory_is_empty_not_fatal(self):
        self.assertEqual(airules.discover_modules(self.home / "nope"), ())

    def test_front_matter_is_not_carried_into_the_output(self):
        d = self.home / "rules"
        self.write_module(d, "one.md", "# One\n\nRULE BODY\n", front="order=10, default=on")

        out = airules.read_modules(airules.discover_modules(d))

        # It is metadata about the module, not an instruction to an agent
        self.assertIn("RULE BODY", out)
        self.assertNotIn("ai-rules:", out)
        self.assertNotIn("order=10", out)

    def test_each_module_is_wrapped_in_markers_naming_its_file(self):
        d = self.home / "rules"
        self.write_module(d, "one.md", "RULE ONE\n", front="order=10")

        out = airules.read_modules(airules.discover_modules(d))

        # The assembled document is the only thing an agent reads, so it has to
        # say which source file each chunk came from and that editing it there
        # is pointless
        self.assertIn("one.md", out)
        self.assertIn("DO NOT TOUCH", out)
        self.assertIn(airules.MODULE_END_TEMPLATE.format(name="one.md"), out)

    def test_a_selected_module_with_no_file_is_fatal(self):
        d = self.home / "rules"
        self.write_module(d, "gone.md", "RULE\n", front="order=10")

        modules = airules.discover_modules(d)
        (d / "gone.md").unlink()

        # Selecting a module and finding no file is a broken install, not a
        # preference. Skipping it would drop a whole discipline out of every
        # agent's rules and still report success — which is how a failed rename
        # once left the notes module one apply away from vanishing.
        with self.assertRaises(airules.MissingModuleError) as caught:
            airules.read_modules(modules)

        # The message has to name the module and the directory, because the
        # whole point is that the reader can act without re-deriving anything
        self.assertEqual(caught.exception.name, "gone.md")
        self.assertIn("gone.md", str(caught.exception))
        self.assertIn(str(d), str(caught.exception))

    def test_selection_falls_back_to_what_each_module_declares(self):
        d = self.home / "rules"
        self.write_module(d, "req.md", "REQ\n",  front="order=10, required")
        self.write_module(d, "on.md",  "ON\n",   front="order=20, default=on")
        self.write_module(d, "off.md", "OFF\n",  front="order=30, default=off")

        modules = airules.discover_modules(d)

        # No answers at all is a fresh clone. What it gets is exactly what the
        # modules declare, which is how a module added to the repo takes effect
        # without anyone editing a config first.
        self.assertEqual([m.stem for m in airules.selected_modules(modules, {})], ["req", "on"])

    def test_a_stored_answer_overrides_a_declared_default(self):
        d = self.home / "rules"
        self.write_module(d, "on.md",  "ON\n",  front="order=10, default=on")
        self.write_module(d, "off.md", "OFF\n", front="order=20, default=off")

        modules = airules.discover_modules(d)
        chosen  = airules.selected_modules(modules, {"on": False, "off": True})

        self.assertEqual([m.stem for m in chosen], ["off"])

    def test_a_required_module_cannot_be_switched_off(self):
        d = self.home / "rules"
        self.write_module(d, "req.md", "REQ\n", front="order=10, required")

        modules = airules.discover_modules(d)

        # A stored "no" for a required module is a config that should not exist,
        # but it must not be able to remove the rules that explain the system
        self.assertEqual([m.stem for m in airules.selected_modules(modules, {"req": False})], ["req"])

    def test_required_modules_are_never_asked_about(self):
        d = self.home / "rules"
        self.write_module(d, "req.md", "REQ\n", front="order=10, required")
        self.write_module(d, "opt.md", "OPT\n", front="order=20, default=on")

        modules = airules.discover_modules(d)

        # Asking a question whose only valid answer is yes trains someone to
        # stop reading the questions that matter
        self.assertEqual([m.stem for m in airules.optional_modules(modules)], ["opt"])

    def test_front_matter_parses_flags_values_and_quoted_commas(self):
        front = airules.parse_front_matter(
            '<!-- ai-rules: order=30, default=off, clobbers, prompt="Take these, all of them" -->\n# T\n')

        self.assertEqual(front["order"], "30")
        self.assertEqual(front["default"], "off")
        self.assertIs(front["clobbers"], True)

        # The comma inside the quotes is content. Without that the prompt would
        # be truncated at the comma and the rest read as a bogus key.
        self.assertEqual(front["prompt"], "Take these, all of them")

    def test_a_file_with_no_declaration_parses_as_no_declaration(self):
        self.assertEqual(airules.parse_front_matter("# Title\n\nBody.\n"), {})

    def test_an_unreadable_order_falls_back_instead_of_raising(self):
        d = self.home / "rules"
        self.write_module(d, "bad.md", "RULE\n", front="order=banana")

        module, = airules.discover_modules(d)

        # A typo in a comment must not stop every agent being written. The
        # module still assembles; it just sorts where an undeclared one would.
        self.assertEqual(module.order, airules.DEFAULT_MODULE_ORDER)

    def test_a_declared_prompt_beats_the_one_built_from_the_title(self):
        d = self.home / "rules"
        self.write_module(d, "a.md", "# Global instructions\n\nR\n", front='prompt="Inherit the lot"')
        self.write_module(d, "b.md", "# Daily notes\n\nR\n")

        declared, derived = airules.discover_modules(d)

        # "Include the Global instructions rules" is what the derived form gives
        # for a module whose heading is not a noun phrase, which is why a module
        # can override it
        self.assertEqual(declared.prompt, "Inherit the lot")
        self.assertEqual(derived.prompt, "Include the Daily notes rules")

    def test_assemble_is_idempotent(self):
        once  = airules.assemble(UNIVERSAL, "LOCAL ONE\n")
        twice = airules.assemble(once, "LOCAL ONE\n")
        self.assertEqual(once, twice)
        self.assertEqual(twice.count(airules.LOCAL_END), 1)

    def test_reassembly_replaces_stale_local_block(self):
        once  = airules.assemble(UNIVERSAL, "OLD RULE\n")
        twice = airules.assemble(once, "NEW RULE\n")
        self.assertIn("NEW RULE", twice)
        self.assertNotIn("OLD RULE", twice)
        self.assertEqual(twice.count(airules.LOCAL_END), 1)

    def test_assemble_converges_when_local_quotes_local_end_inline(self):
        local = "Our docs quote the " + airules.LOCAL_END + " marker inline.\n"
        outs  = _converge(UNIVERSAL, local)

        for later in outs[1:]:
            self.assertEqual(outs[0], later)

        # Exactly one marker owns a line of its own: the generated one. The
        # quoted copy sits mid-sentence and stays put.
        self.assertEqual(outs[0].count("\n" + airules.LOCAL_END + "\n"), 1)
        self.assertEqual(outs[0].count(airules.LOCAL_END), 2)
        self.assertIn("Our docs quote", outs[-1])

    def test_assemble_converges_when_local_quotes_local_end_on_own_line(self):
        local = "Example:\n\n```\n" + airules.LOCAL_END + "\n```\n"
        outs  = _converge(UNIVERSAL, local)

        for later in outs[1:]:
            self.assertEqual(outs[0], later)

        self.assertEqual(outs[0].count(airules.LOCAL_END), 2)
        self.assertIn("Example:", outs[-1])

    def test_assemble_converges_when_local_quotes_notes_markers(self):
        local = (
            "Our docs quote " + MARK_BEGIN
            + " and " + MARK_END + " inline.\n"
        )
        outs = _converge(UNIVERSAL, local)

        for later in outs[1:]:
            self.assertEqual(outs[0], later)

        self.assertEqual(outs[0].count("\n" + airules.LOCAL_END + "\n"), 1)
        self.assertIn("Our docs quote", outs[-1])
        self.assertNotIn("NOTES SYNC", outs[-1])

    def test_local_block_spacing_is_symmetric(self):
        out      = airules.assemble(UNIVERSAL, "LOCAL ONE\n")
        expected = airules.LOCAL_BEGIN + "\n\nLOCAL ONE\n\n" + airules.LOCAL_END + "\n"

        self.assertTrue(out.endswith(expected))

    def test_single_trailing_newline(self):
        out = airules.assemble(UNIVERSAL, "LOCAL\n")
        self.assertTrue(out.endswith("\n"))
        self.assertFalse(out.endswith("\n\n"))


if __name__ == "__main__":
    unittest.main()
