# SPDX-License-Identifier: GPL-3.0-only
import unittest
from app import Court, run

T1='2026-01-01T00:00:00Z'
T2='2026-01-02T00:00:00Z'
T3='2026-01-03T00:00:00Z'
class KnowledgeTimeTests(unittest.TestCase):
    def setUp(self):
        self.c=Court();self.addCleanup(self.c.close)
        self.c.claim('late','fictional','city','Boston','form',T2,T1,T3)

    def test_late_claim_does_not_leak_into_original_view(self):
        original=self.c.query('fictional','city',T1,explain=True)
        self.assertEqual(original['status'],'unknown');self.assertEqual(original['excluded'],[])
        self.assertNotIn('known_at',original)
        hindsight=self.c.query('fictional','city',T1,known_at=T2)
        self.assertEqual(hindsight['answer'],'Boston')

    def test_later_retraction_changes_hindsight_only(self):
        self.c.retract('late',T3,'incorrect source')
        self.assertEqual(self.c.query('fictional','city',T2,known_at=T2)['answer'],'Boston')
        result=self.c.query('fictional','city',T2,True,known_at=T3)
        self.assertEqual(result['status'],'unknown')
        self.assertEqual(len(result['excluded']),1)
        self.assertEqual(result['excluded'][0]['id'],'late')
        self.assertEqual(result['excluded'][0]['reasons'],['retracted'])

    def test_validity_uses_effective_time_not_knowledge_time(self):
        self.assertEqual(self.c.query('fictional','city',T3,known_at=T2)['status'],'unknown')
        with self.assertRaises(ValueError):self.c.query('fictional','city',T1,known_at='2026-01-02')

    def test_operation_adapter_accepts_knowledge_time(self):
        result=run([{'operation':'query','entity':'fictional','attribute':'city','as_of':T1,'known_at':T2}])
        self.assertTrue(result['queries'][0]['known_at'].startswith('2026-01-02'))
