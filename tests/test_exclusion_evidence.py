# SPDX-License-Identifier: GPL-3.0-only
import unittest
from app import Court, stamp

T1 = "2026-01-01T00:00:00Z"
T2 = "2026-01-02T00:00:00Z"
T3 = "2026-01-03T00:00:00Z"


class ExclusionEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.court = Court()
        self.addCleanup(self.court.close)
        self.court.claim("one", "fictional", "city", "Boston", "form", T1, T1)

    def query(self, **kwargs):
        return self.court.query("fictional", "city", T1, explain=True, **kwargs)

    def test_exclusions_reference_both_visible_event_types_in_sequence_order(self):
        self.court.revoke_source("form", T2, "form withdrawn")
        self.court.retract("one", T2, "wrong city")
        entry = self.query(known_at=T2)["excluded"][0]
        self.assertEqual(entry["reasons"], ["retracted", "source_revoked"])
        self.assertEqual(entry["event_evidence"], [
            {"sequence": 2, "kind": "revoke_source", "recorded_at": stamp(T2), "reason": "form withdrawn"},
            {"sequence": 3, "kind": "retract", "recorded_at": stamp(T2), "reason": "wrong city"}])

    def test_knowledge_cutoff_hides_later_events_even_when_claim_is_excluded(self):
        self.court.retract("one", T2, "first correction")
        self.court.revoke_source("form", T3, "later discovery")
        self.assertEqual(self.query()["excluded"], [])
        early = self.query(known_at=T2)["excluded"][0]
        self.assertEqual(early["reasons"], ["retracted"])
        self.assertEqual([e["reason"] for e in early["event_evidence"]], ["first correction"])
        self.assertEqual(len(self.query(known_at=T3)["excluded"][0]["event_evidence"]), 2)

    def test_unrelated_entity_events_and_payload_fields_are_not_disclosed(self):
        self.court.claim("other", "unrelated", "city", "Portland", "other-form", T1, T1)
        self.court.retract("other", T2, "unrelated reason")
        self.court.retract("one", T2, "relevant reason")
        entry = self.query(known_at=T2)["excluded"][0]
        self.assertEqual([e["reason"] for e in entry["event_evidence"]], ["relevant reason"])
        self.assertEqual(set(entry["event_evidence"][0]), {"sequence", "kind", "recorded_at", "reason"})

    def test_repeated_exclusion_events_remain_distinct_without_writes(self):
        self.court.retract("one", T2, "first")
        self.court.retract("one", T3, "second")
        before = self.court.events()
        first = self.query(known_at=T3)
        self.assertEqual([e["sequence"] for e in first["excluded"][0]["event_evidence"]], [2, 3])
        first["excluded"][0]["event_evidence"][0]["reason"] = "modified output"
        self.assertEqual(self.query(known_at=T3)["excluded"][0]["event_evidence"][0]["reason"], "first")
        self.assertEqual(self.court.events(), before)

    def test_plain_query_preserves_answer_and_does_not_include_explanations(self):
        self.court.retract("one", T2, "withdrawn")
        plain = self.court.query("fictional", "city", T1, known_at=T2)
        explained = self.query(known_at=T2)
        self.assertNotIn("excluded", plain)
        self.assertEqual({k: v for k, v in explained.items() if k != "excluded"}, plain)
