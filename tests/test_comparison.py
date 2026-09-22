# SPDX-License-Identifier: GPL-3.0-only
import unittest
from comparison import demo, fixtures, latest_value
from app import run

class ComparisonTests(unittest.TestCase):
    def test_baseline_cannot_see_future_claim(self):
        operations,_=fixtures();events=run(operations)['events']
        self.assertEqual(latest_value(events,operations[1])['answer'],'Boston')
    def test_empty_baseline_abstains(self):
        operations,_=fixtures()
        self.assertEqual(latest_value([],operations[1]),{'status':'unknown','answer':None})
    def test_baseline_errors_match_authored_conflict_retraction_expiry(self):
        court,baseline=demo()['comparisons']
        self.assertEqual(court['matched'],4);self.assertEqual(baseline['matched'],1)
        self.assertEqual([t['actual']['answer'] for t in baseline['trials']],['Boston','Portland','Portland','Portland'])
        self.assertEqual([t['actual']['status'] for t in court['trials']],['supported','conflict','supported','unknown'])
