# SPDX-License-Identifier: GPL-3.0-only
import tempfile
from pathlib import Path
import unittest
from app import Court, run

T = '2026-01-01T00:00:00Z'


def claim(id):
    return {'operation':'claim','id':id,'entity':'fictional','attribute':'city','value':'Boston',
            'source':'form','recorded_at':T,'valid_from':T}


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.court = Court(); self.addCleanup(self.court.close)

    def add(self, id):
        data = claim(id); data.pop('operation'); self.court.claim(**data)

    def test_pages_hold_boundary_across_append_and_preserve_equal_time_order(self):
        for id in ('one','two','three'): self.add(id)
        first = self.court.events_snapshot(limit=1)
        self.add('later')
        second = self.court.events_snapshot(first['next_cursor'], 1, first['through_sequence'])
        third = self.court.events_snapshot(second['next_cursor'], 1, first['through_sequence'])
        self.assertEqual([p['events'][0]['sequence'] for p in (first,second,third)], [1,2,3])
        self.assertEqual([p['has_more'] for p in (first,second,third)], [True,True,False])
        self.assertEqual(len(self.court.events_snapshot()['events']), 4)
        self.assertEqual(len(self.court.events_page()['events']), 4)

    def test_empty_and_exhausted_pages_keep_cursor_without_advancing_boundary(self):
        first = self.court.events_snapshot()
        self.assertEqual(first, {'events':[],'next_cursor':0,'through_sequence':0,'has_more':False})
        self.add('one')
        self.assertEqual(self.court.events_snapshot(0, 1, 0), first)
        self.assertEqual(self.court.events_snapshot(1, 1, 1),
                         {'events':[],'next_cursor':1,'through_sequence':1,'has_more':False})

    def test_invalid_cursors_limits_and_future_boundaries_do_not_write(self):
        self.add('one'); before = self.court.events(); changes = self.court.db.total_changes
        for kwargs in ({'after_sequence':True},{'after_sequence':-1},{'after_sequence':2},
                       {'limit':False},{'limit':0},{'limit':1001},{'through_sequence':True},
                       {'through_sequence':-1},{'through_sequence':2},{'after_sequence':1,'through_sequence':0}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.court.events_snapshot(**kwargs)
        self.assertEqual(self.court.events(), before)
        self.assertEqual(self.court.db.total_changes, changes)

    def test_snapshots_include_audit_events_and_return_detached_data_without_writes(self):
        self.add('one'); self.court.retract('one', T, 'withdrawn')
        self.court.revoke_source('form', T, 'source withdrawn')
        before = self.court.events(); changes = self.court.db.total_changes
        page = self.court.events_snapshot()
        self.assertEqual([e['kind'] for e in page['events']], ['claim','retract','revoke_source'])
        page['events'][0]['payload']['value'] = 'changed output'
        self.assertEqual(self.court.events_snapshot()['events'], before)
        self.assertEqual(self.court.db.total_changes, changes)

    def test_batch_history_sees_pending_claims_and_keeps_requested_boundary(self):
        result = run([claim('one'), {'operation':'history','limit':1}, claim('two'),
                      {'operation':'history','after_sequence':1,'through_sequence':1}])
        self.assertEqual(result['history_pages'][0]['through_sequence'], 1)
        self.assertEqual(result['history_pages'][1]['events'], [])
        self.assertEqual(len(result['events']), 2)
        self.assertNotIn('history_pages', run([claim('one')]))

    def test_failed_history_request_rolls_back_prior_batch_writes(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder)/'synthetic.sqlite3')
            run([claim('existing')], path)
            with self.assertRaises(ValueError):
                run([claim('new'), {'operation':'history','through_sequence':99}], path)
            court = Court(path)
            try:
                self.assertEqual([e['payload']['id'] for e in court.events()], ['existing'])
            finally:
                court.close()
