#!/usr/bin/env python3
"""Synthetic regression tests: independent gate and quality scoring, no deletion."""
import copy
import json
from pathlib import Path
import unittest
from evaluate import InputError, evaluate, preflight_violation

ROOT=Path(__file__).parent


def read(name, key):
    return json.loads((ROOT/name).read_text(encoding="utf-8"))[key]


class TestDecisionEvaluator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases=read("cases.synthetic.json", "cases")
        cls.correct=read("predictions.illustrative.json", "predictions")
        cls.unsafe=read("predictions.redteam.json", "predictions")

    def test_case_fixture_count_and_no_private_paths(self):
        self.assertEqual(20,len(self.cases))
        for c in self.cases:
            self.assertNotIn("path",c)
            self.assertEqual("synthetic_scenario_not_real_mac_evidence",c["provenance"])

    def test_manual_exemplar_is_self_consistent_not_model_performance(self):
        result=evaluate(self.cases,self.correct)
        self.assertEqual("PASS",result["release_quality_gate"])
        self.assertEqual(0,result["critical_false_recommendations"])
        self.assertEqual(0,result["gate_violations"])
        self.assertEqual(1.0,result["three_state_accuracy"])
        self.assertFalse(result["automated_deletion_supported"])

    def test_redteam_catches_dangerous_recommendations(self):
        result=evaluate(self.cases,self.unsafe)
        self.assertEqual("FAIL",result["release_quality_gate"])
        self.assertEqual(4,result["critical_false_recommendations"])
        self.assertGreaterEqual(result["gate_violations"],5)

    def test_missing_evidence_does_not_count_as_valid(self):
        prediction=copy.deepcopy(self.correct[0])
        prediction["evidence_ids"]=["made-up-document"]
        violations=preflight_violation(self.cases[0],prediction)
        self.assertIn("UNKNOWN_EVIDENCE_REFERENCE",violations)

    def test_active_and_protected_never_bypass_gate(self):
        idx={c["id"]:c for c in self.cases}
        for cid in ["npm-live","codex-current","cursor-current","symlink-bypass"]:
            p=copy.deepcopy(self.correct[0])
            p["id"]=cid
            p["decision"]="RECOMMEND"
            self.assertIn("UNSAFE_SAFETY_STATE",preflight_violation(idx[cid],p))

    def test_offline_profile_cannot_be_recommended(self):
        idx={c["id"]:c for c in self.cases}
        for cid in ["feishu-offline","chrome-service-worker"]:
            p=copy.deepcopy(self.correct[0])
            p["id"]=cid
            self.assertIn("OFFLINE_DEPENDENCY",preflight_violation(idx[cid],p))

    def test_native_cleanup_method_is_required_for_native_app(self):
        p=copy.deepcopy(self.correct[0])
        p["cleanup_strategy"]="EXACT_PATH"
        self.assertIn("IGNORED_NATIVE_CLEANUP_METHOD",preflight_violation(self.cases[0],p))

    def test_duplicate_or_missing_prediction_fails(self):
        with self.assertRaises(InputError):
            evaluate(self.cases,self.correct[:-1])
        with self.assertRaises(InputError):
            evaluate(self.cases,self.correct+[self.correct[-1]])

    def test_reason_is_required(self):
        bad=copy.deepcopy(self.correct)
        bad[0]["reason"]="short"
        with self.assertRaises(InputError):
            evaluate(self.cases,bad)

    def test_case_missing_provenance_fails(self):
        bad=copy.deepcopy(self.cases)
        bad[0]["evidence_ids"]=[]
        with self.assertRaises(InputError):
            evaluate(bad,self.correct)


if __name__=="__main__":
    unittest.main()
