import unittest
from base import SandboxedTestCase
import airules

UNIVERSAL = (
    "# Universal Rules\n\nAlways be concise.\n\n"
    + airules.NOTES_BEGIN
    + "\nNOTES SYNC: pull before writing notes.\n"
    + airules.NOTES_END
    + "\n\nEnd of universal.\n"
)


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
        text = airules.assemble(text, local_text, notes_enabled=notes_enabled)
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

    def test_strip_notes_removes_block_and_markers(self):
        out = airules.strip_block(UNIVERSAL, airules.NOTES_BEGIN, airules.NOTES_END, should_repeat=True)
        self.assertNotIn("NOTES SYNC", out)
        self.assertNotIn(airules.NOTES_BEGIN, out)
        self.assertNotIn(airules.NOTES_END, out)
        self.assertIn("Always be concise.", out)
        self.assertIn("End of universal.", out)

    def test_strip_notes_is_noop_without_markers(self):
        out = airules.strip_block("plain\n", airules.NOTES_BEGIN, airules.NOTES_END, should_repeat=True)
        self.assertEqual(out, "plain\n")

    def test_strip_notes_removes_every_region(self):
        text = (
            "HEAD\n\n"
            + airules.NOTES_BEGIN + "\nFIRST NUDGE\n" + airules.NOTES_END + "\n"
            + "MIDDLE\n\n"
            + airules.NOTES_BEGIN + "\nSECOND NUDGE\n" + airules.NOTES_END + "\n"
            + "TAIL\n"
        )

        out = airules.strip_block(text, airules.NOTES_BEGIN, airules.NOTES_END, should_repeat=True)
        self.assertEqual(out, "HEAD\n\nMIDDLE\n\nTAIL\n")
        self.assertNotIn("FIRST NUDGE", out)
        self.assertNotIn("SECOND NUDGE", out)
        self.assertNotIn(airules.NOTES_BEGIN, out)
        self.assertNotIn(airules.NOTES_END, out)

    def test_strip_notes_ignores_markers_quoted_mid_line(self):
        text = "See " + airules.NOTES_BEGIN + " and " + airules.NOTES_END + " above.\n"
        self.assertEqual(airules.strip_block(text, airules.NOTES_BEGIN, airules.NOTES_END, should_repeat=True), text)

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

    def test_strip_notes_unterminated_block_runs_to_end(self):
        text = "KEEP ME\n\n" + airules.NOTES_BEGIN + "\nDANGLING NOTES\ntrailing junk\n"

        out = airules.strip_block(text, airules.NOTES_BEGIN, airules.NOTES_END, should_repeat=True)
        self.assertEqual(out, "KEEP ME\n\n")
        self.assertNotIn(airules.NOTES_BEGIN, out)
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

    def test_read_local_rules_round_trips_non_ascii(self):
        body = "Rule — with an em dash\n"
        d    = self._local_dir(**{"10-dash.md": body})

        self.assertEqual(airules.read_local_rules(d), body)

    def test_assemble_notes_disabled_strips_block(self):
        out = airules.assemble(UNIVERSAL, "LOCAL ONE\n", notes_enabled=False)
        self.assertNotIn("NOTES SYNC", out)
        self.assertIn("LOCAL ONE", out)
        self.assertIn(airules.LOCAL_BEGIN, out)
        self.assertIn(airules.LOCAL_END, out)

    def test_assemble_notes_enabled_keeps_block(self):
        out = airules.assemble(UNIVERSAL, "", notes_enabled=True)
        self.assertIn("NOTES SYNC", out)

    def test_assemble_without_local_has_no_local_block(self):
        out = airules.assemble(UNIVERSAL, "   \n", notes_enabled=False)
        self.assertNotIn(airules.LOCAL_BEGIN, out)
        self.assertNotIn(airules.LOCAL_END, out)

    def test_assemble_is_idempotent(self):
        once  = airules.assemble(UNIVERSAL, "LOCAL ONE\n", notes_enabled=False)
        twice = airules.assemble(once, "LOCAL ONE\n", notes_enabled=False)
        self.assertEqual(once, twice)
        self.assertEqual(twice.count(airules.LOCAL_END), 1)

    def test_reassembly_replaces_stale_local_block(self):
        once  = airules.assemble(UNIVERSAL, "OLD RULE\n", notes_enabled=False)
        twice = airules.assemble(once, "NEW RULE\n", notes_enabled=False)
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
            "Our docs quote " + airules.NOTES_BEGIN
            + " and " + airules.NOTES_END + " inline.\n"
        )
        outs = _converge(UNIVERSAL, local)

        for later in outs[1:]:
            self.assertEqual(outs[0], later)

        self.assertEqual(outs[0].count("\n" + airules.LOCAL_END + "\n"), 1)
        self.assertIn("Our docs quote", outs[-1])
        self.assertNotIn("NOTES SYNC", outs[-1])

    def test_local_block_spacing_is_symmetric(self):
        out      = airules.assemble(UNIVERSAL, "LOCAL ONE\n", notes_enabled=False)
        expected = airules.LOCAL_BEGIN + "\n\nLOCAL ONE\n\n" + airules.LOCAL_END + "\n"

        self.assertTrue(out.endswith(expected))

    def test_single_trailing_newline(self):
        out = airules.assemble(UNIVERSAL, "LOCAL\n", notes_enabled=False)
        self.assertTrue(out.endswith("\n"))
        self.assertFalse(out.endswith("\n\n"))


if __name__ == "__main__":
    unittest.main()
