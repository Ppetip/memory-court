# SPDX-License-Identifier: GPL-3.0-only
import tempfile
import unittest
from pathlib import Path
from app import Court, run

T1='2026-01-01T00:00:00Z'
T2='2026-01-02T00:00:00Z'
class BatchAtomicityTests(unittest.TestCase):
    def claim(self,id,time):return {'operation':'claim','id':id,'entity':'fictional','attribute':'city','value':'Boston','source':'form','recorded_at':time,'valid_from':time}
    def test_failed_batch_preserves_existing_database_exactly(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=str(Path(tmp)/'memory.sqlite3')
            before=run([self.claim('old',T1)],path)['events']
            for failing in [{'operation':'retract','id':'missing','recorded_at':T2,'reason':'test'}, {'operation':'unknown'}, {'operation':'query'}]:
                with self.subTest(failing=failing),self.assertRaises((ValueError,TypeError)):
                    run([self.claim('new',T2),failing],path)
                court=Court(path)
                try:self.assertEqual(court.events(),before)
                finally:court.close()
    def test_successful_batch_commits_all_and_queries_see_pending_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=str(Path(tmp)/'memory.sqlite3')
            result=run([self.claim('old',T1),{'operation':'query','entity':'fictional','attribute':'city','as_of':T1}],path)
            self.assertEqual(result['queries'][0]['answer'],'Boston')
            court=Court(path)
            try:self.assertEqual(court.events(),result['events'])
            finally:court.close()
    def test_failed_direct_append_does_not_poison_next_transaction(self):
        court=Court();self.addCleanup(court.close)
        with self.assertRaises(ValueError):court.retract('missing',T1,'test')
        self.assertFalse(court.db.in_transaction)
        op=self.claim('new',T1);op.pop('operation');court.claim(**op)
        self.assertEqual(len(court.events()),1);self.assertFalse(court.db.in_transaction)
