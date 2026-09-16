import sqlite3
import tempfile
import unittest
from pathlib import Path
from app import Court, demo, run, stamp


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.c = Court()

    def tearDown(self):
        self.c.close()

    def add(self, id="one", value="Boston", start="2026-01-01T00:00:00Z", end=None):
        self.c.claim(id, "person", "city", value, "synthetic", start, start, end)

    def test_conflict_abstains(self):
        self.add()
        self.add("two", "Portland")
        result = self.c.query("person", "city", "2026-01-02T00:00:00Z")
        self.assertEqual(result["status"], "conflict")
        self.assertIsNone(result["answer"])

    def test_retraction_not_retroactive(self):
        self.add()
        self.c.retract("one", "2026-01-03T00:00:00Z", "error")
        self.assertEqual(self.c.query("person", "city", "2026-01-02T00:00:00Z")["answer"], "Boston")
        self.assertIsNone(self.c.query("person", "city", "2026-01-04T00:00:00Z")["answer"])

    def test_expiry_exclusive(self):
        self.add(end="2026-01-02T00:00:00Z")
        self.assertEqual(self.c.query("person", "city", "2026-01-02T00:00:00Z")["status"], "unknown")

    def test_future_claim_hidden(self):
        self.add(start="2026-02-01T00:00:00Z")
        self.assertEqual(self.c.query("person", "city", "2026-01-01T00:00:00Z")["status"], "unknown")

    def test_event_mutation_rejected(self):
        self.add()
        with self.assertRaises(sqlite3.IntegrityError):
            self.c.db.execute("DELETE FROM events")

    def test_unknown_retraction(self):
        with self.assertRaises(ValueError):
            self.c.retract("absent", "2026-01-01T00:00:00Z", "error")

    def test_no_naive_time(self):
        with self.assertRaises(ValueError):
            stamp("2026-01-01")

    def test_duplicate_id_rejected(self):
        self.add()
        with self.assertRaises(ValueError):
            self.add()

    def test_demo_resolution(self):
        self.assertEqual([q["status"] for q in run(demo())["queries"]], ["supported", "conflict", "supported"])

    def test_out_of_order_append_rejected(self):
        self.add(start="2026-02-01T00:00:00Z")
        with self.assertRaises(ValueError):
            self.add("old")

    def test_timezone_normalization(self):
        self.assertEqual(stamp("2026-01-01T01:00:00+01:00"), stamp("2026-01-01T00:00:00Z"))

    def test_database_persists(self):
        with tempfile.TemporaryDirectory() as d:
            path = str(Path(d) / "memory.db")
            run(demo(), path)
            court = Court(path)
            try:
                self.assertEqual(court.query("fictional-customer", "shipping_city", "2026-01-04T00:00:00Z")["answer"], "Portland")
            finally:
                court.close()


if __name__ == "__main__":
    unittest.main()
