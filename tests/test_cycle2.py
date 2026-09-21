import unittest
from app import Court

class SourceTests(unittest.TestCase):
    def setUp(self):
        self.c = Court()
        for id, source in [('a','bad'),('b','bad'),('c','good')]:
            self.c.claim(id,id,'color','blue',source,'2026-01-01T00:00:00Z','2026-01-01T00:00:00Z')
    def tearDown(self): self.c.close()
    def test_source_retraction_preserves_history(self):
        self.c.revoke_source('bad','2026-01-02T00:00:00Z','incorrect import')
        self.assertEqual(self.c.query('a','color','2026-01-01T12:00:00Z')['answer'],'blue')
        for id in ('a','b'):self.assertIsNone(self.c.query(id,'color','2026-01-03T00:00:00Z')['answer'])
        self.assertEqual(self.c.query('c','color','2026-01-03T00:00:00Z')['answer'],'blue')
    def test_revoked_source_cannot_add_claims(self):
        self.c.revoke_source('bad','2026-01-02T00:00:00Z','wrong')
        with self.assertRaises(ValueError):self.c.claim('d','d','color','red','bad','2026-01-03T00:00:00Z','2026-01-03T00:00:00Z')
        self.assertEqual(len(self.c.events()),4)
    def test_unknown_source_rejected_atomically(self):
        with self.assertRaises(ValueError):self.c.revoke_source('absent','2026-01-02T00:00:00Z','wrong')
        self.assertEqual(len(self.c.events()),3)
