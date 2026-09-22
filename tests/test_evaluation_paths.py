# SPDX-License-Identifier: GPL-3.0-only
import unittest
from app import Court

class ExclusionTests(unittest.TestCase):
    def setUp(self):self.c=Court();self.addCleanup(self.c.close)
    def claim(self,id,start,end=None):self.c.claim(id,'fictional','city','Boston','source','2026-01-01T00:00:00Z',start,end)
    def test_expired_and_future_validity_are_explained(self):
        self.claim('expired','2026-01-01T00:00:00Z','2026-01-02T00:00:00Z');self.claim('future','2026-01-03T00:00:00Z')
        r=self.c.query('fictional','city','2026-01-02T00:00:00Z',explain=True)
        self.assertEqual(r['excluded'],[{'id':'expired','reasons':['expired']},{'id':'future','reasons':['not_yet_valid']}])
        self.assertIsNone(r['answer'])
    def test_retraction_and_revocation_both_explained_without_rewriting_history(self):
        self.claim('old','2026-01-01T00:00:00Z');self.c.retract('old','2026-01-02T00:00:00Z','test');self.c.revoke_source('source','2026-01-02T00:00:00Z','test')
        r=self.c.query('fictional','city','2026-01-02T00:00:00Z',True)
        self.assertEqual(r['excluded'][0]['reasons'],['retracted','source_revoked'])
        self.assertEqual(self.c.query('fictional','city','2026-01-01T00:00:00Z',True)['excluded'],[])
    def test_explanation_is_opt_in_and_boolean(self):
        self.assertNotIn('excluded',self.c.query('fictional','city','2026-01-01T00:00:00Z'))
        with self.assertRaises(ValueError):self.c.query('fictional','city','2026-01-01T00:00:00Z',1)
