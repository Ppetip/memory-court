# SPDX-License-Identifier: GPL-3.0-only
"""Reject malformed operation envelopes before creating or reading a database."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from app import Court, demo, run


class BatchShapeTests(unittest.TestCase):
    def test_nonarray_input_never_opens_database(self):
        for value in ({}, "", None, (), iter([])):
            with self.subTest(kind=type(value).__name__), patch("app.Court") as court:
                with self.assertRaisesRegex(ValueError, "array"):
                    run(value, "must-not-open.sqlite3")
                court.assert_not_called()

    def test_invalid_late_operation_prevents_database_open(self):
        for value in (None, [], {}, {"operation":None}, {"operation":[]},
                      {"operation":"delete"}, {"operation":""}):
            with self.subTest(value=value), patch("app.Court") as court:
                with self.assertRaisesRegex(ValueError, "supported operation"):
                    run([demo()[0], value], "must-not-open.sqlite3")
                court.assert_not_called()

    def test_bad_shape_does_not_create_file_or_change_existing_history(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.sqlite3"
            with self.assertRaises(ValueError): run({}, path)
            self.assertFalse(path.exists())
            before = run([demo()[0]], path)
            with self.assertRaises(ValueError): run([demo()[2], {"operation":"unknown"}], path)
            self.assertEqual(run([], path)["events"], before["events"])

    def test_valid_batches_and_empty_arrays_preserve_behavior_and_inputs(self):
        operations = demo(); before = copy.deepcopy(operations)
        result = run(operations)
        self.assertEqual(operations, before)
        self.assertEqual([q["status"] for q in result["queries"]], ["supported", "conflict", "supported"])
        self.assertEqual(len(result["events"]), 3)
        self.assertEqual(run([])["events"], [])
        self.assertEqual(run([])["queries"], [])

    def test_argument_failure_still_rolls_back_new_events(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.sqlite3"
            original = run([demo()[0]], path)["events"]
            # Shape is valid; argument validation still occurs inside the transaction.
            with self.assertRaises(TypeError):
                run([demo()[2], {"operation":"query"}], path)
            court = Court(path)
            try: self.assertEqual(court.events(), original)
            finally: court.close()
