# SPDX-License-Identifier: GPL-3.0-only
import unittest
from app import Court

class PaginationTests(unittest.TestCase):
    def setUp(self):
        self.court=Court();self.addCleanup(self.court.close)
    def add(self,i):
        self.court.claim(str(i),'fictional','city',str(i),'synthetic','2026-01-01T00:00:00Z','2026-01-01T00:00:00Z')
    def test_resume_after_append_has_no_duplicates(self):
        self.add(0);self.add(1)
        first=self.court.events_page(limit=1)
        self.add(2)
        rest=self.court.events_page(first['next_cursor'])
        self.assertEqual(first['events']+rest['events'],self.court.events())
        self.assertEqual(rest['next_cursor'],3)
    def test_empty_page_preserves_cursor(self):
        self.assertEqual(self.court.events_page(5),{'events':[],'next_cursor':5})
    def test_bad_limits_and_cursors_rejected(self):
        for cursor,limit in [(-1,1),(True,1),(0,0),(0,1001),(0,True)]:
            with self.assertRaises(ValueError): self.court.events_page(cursor,limit)
