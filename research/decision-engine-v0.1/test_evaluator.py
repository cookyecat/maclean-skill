#!/usr/bin/env python3
"""Offline decision evaluator adversarial regression. No filesystem cleanup."""
from __future__ import annotations
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import evaluate
from make_blind_input import redact_cases

ROOT = Path(__file__).resolve().parent
FIX = ROOT / "fixtures"

def read(name):
    return json.loads((FIX / name).read_text(encoding="utf-8"))

class TestResearchEvaluator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = read("cases.synthetic.v0.1.json")["cases"]
        cls.oracle = read("predictions.oracle-control.json")["predictions"]
        cls.eager = read("predictions.overeager-control.json")["predictions"]
        cls.timid = read("predictions.timid-control.json")["predictions"]

    def test_oracle_calibration_only(self):
        r = evaluate.evaluate(self.cases, self.oracle)
        self.assertEqual(r["release_quality_gate"], "PASS")
        self.assertEqual(r["dataset_size"], 18)
        self.assertEqual(r["critical_false_recommendations"], 0)
        self.assertEqual(r["gate_violations"], 0)
        self.assertEqual(r["recommend_recall"], 1.0)

    def test_overeager_detected(self):
        r = evaluate.evaluate(self.cases, self.eager)
        self.assertEqual(r["release_quality_gate"], "FAIL")
        self.assertGreater(r["critical_false_recommendations"], 0)
        self.assertGreater(r["gate_violations"], 0)

    def test_all_keep_does_not_game_gate(self):
        r = evaluate.evaluate(self.cases, self.timid)
        self.assertEqual(r["release_quality_gate"], "FAIL")
        self.assertEqual(r["recommend_recall"], 0)
        self.assertEqual(r["critical_false_recommendations"], 0)

    def test_fabricated_evidence_id_is_flagged(self):
        p = copy.deepcopy(self.oracle)
        p[0]["evidence_ids"].append("imaginary-evidence")
        r = evaluate.evaluate(self.cases, p)
        self.assertEqual(r["release_quality_gate"], "FAIL")
        self.assertTrue(any(
            "UNKNOWN_EVIDENCE_REFERENCE" in d["gate_violations"]
            for d in r["disagreements_and_gate_flags"]))

    def test_native_strategy_missing_is_flagged(self):
        p = copy.deepcopy(self.oracle)
        p[0]["cleanup_strategy"] = "EXACT_PATH"
        r = evaluate.evaluate(self.cases, p)
        self.assertEqual(r["release_quality_gate"], "FAIL")
        self.assertGreater(r["gate_violations"], 0)

    def test_unsupported_native_method_is_flagged(self):
        p = copy.deepcopy(self.oracle)
        p[8]["cleanup_strategy"] = "NATIVE_CLEAN"
        r = evaluate.evaluate(self.cases, p)
        self.assertEqual(r["release_quality_gate"], "FAIL")
        self.assertTrue(any(
            "NATIVE_STRATEGY_UNAVAILABLE" in d["gate_violations"]
            for d in r["disagreements_and_gate_flags"]))

    def test_single_false_positive_blocks_pass(self):
        p = copy.deepcopy(self.oracle)
        p[7]["decision"] = "RECOMMEND"
        p[7]["cleanup_strategy"] = "EXACT_PATH"
        r = evaluate.evaluate(self.cases, p)
        self.assertEqual(r["critical_false_recommendations"], 1)
        self.assertEqual(r["release_quality_gate"], "FAIL")

    def test_bad_prediction_ids_fail_closed(self):
        p = copy.deepcopy(self.oracle)
        p[0]["id"] = p[1]["id"]
        with self.assertRaises(evaluate.InputError):
            evaluate.evaluate(self.cases, p)

    def test_unknown_case_evidence_ids_fail_schema(self):
        c = copy.deepcopy(self.cases)
        c[0]["evidence_ids"] = []
        with self.assertRaises(evaluate.InputError):
            evaluate.evaluate(c, self.oracle)

    def test_blind_export_hides_gold(self):
        d = redact_cases(read("cases.synthetic.v0.1.json"))
        self.assertEqual(len(d["cases"]), 18)
        serialized = json.dumps(d)
        self.assertNotIn("human_expected", serialized)
        self.assertNotIn("acceptable_strategies", serialized)
        self.assertNotIn("label_rationale", serialized)
        self.assertNotIn("RECOMMEND\"}", serialized)

    def test_cli_exit_codes(self):
        good = subprocess.run([sys.executable, str(ROOT/"evaluate.py"),
            "--cases", str(FIX/"cases.synthetic.v0.1.json"),
            "--predictions", str(FIX/"predictions.oracle-control.json")],
            capture_output=True,text=True)
        bad = subprocess.run([sys.executable, str(ROOT/"evaluate.py"),
            "--cases", str(FIX/"cases.synthetic.v0.1.json"),
            "--predictions", str(FIX/"predictions.overeager-control.json")],
            capture_output=True,text=True)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(bad.returncode, 3, bad.stderr)

    def test_private_report_permissions_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(prefix="maclean-eval-test-") as t:
            out = Path(t)/"out.json"
            args=[sys.executable, str(ROOT/"evaluate.py"),
                "--cases",str(FIX/"cases.synthetic.v0.1.json"),
                "--predictions",str(FIX/"predictions.oracle-control.json"),
                "--output",str(out)]
            first = subprocess.run(args,capture_output=True,text=True)
            second = subprocess.run(args,capture_output=True,text=True)
            self.assertEqual(first.returncode,0,first.stderr)
            self.assertEqual(out.stat().st_mode & 0o777,0o600)
            self.assertEqual(second.returncode,2)
            self.assertIn("refuse overwrite",second.stderr)

if __name__=="__main__":
    unittest.main(verbosity=2)
