#!/usr/bin/env python3
"""MacLean research v0.2 offline regression; no network or actual cache mutation."""
from __future__ import annotations
import json, unittest
from prepare_blind import select, band
from compare_blind import compare, hash_data

def fakecases():
    rows=[]
    for i in range(6):
        rows.append({"id":f"RAW{i}", "kind":f"review_kind_{i}", "status":"REVIEW", "size_mib":10+i})
    for i in range(4):
        rows.append({"id":f"RAW{i+6}", "kind":f"active_kind_{i}", "status":"ACTIVE", "size_mib":20+i})
    for i in range(2):
        rows.append({"id":f"RAW{i+10}", "kind":f"protected_kind_{i}", "status":"PROTECTED","size_mib":10})
    return rows

def model_input():
    cases=[]
    for i,x in enumerate(fakecases(),1):
        cases.append({"id":f"C{i:02d}","machine_safety_state":x["status"],
            "rebuildability_evidence":"not_independently_verified"})
    return {"cases":cases,"dataset":"real-coarse-blind-v0.2"}

class TestBlindV02(unittest.TestCase):
    def test_selection_size_and_strata(self):
        chosen=select(fakecases())
        self.assertEqual(len(chosen),12)
        self.assertEqual([x["status"] for x in chosen].count("REVIEW"),6)
        self.assertEqual([x["status"] for x in chosen].count("ACTIVE"),4)
        self.assertEqual([x["status"] for x in chosen].count("PROTECTED"),2)

    def test_numeric_buckets_no_exact_values(self):
        self.assertEqual(band(10),"<32 MiB")
        self.assertEqual(band(64),"32-128 MiB")
        self.assertEqual(band(256),"128-512 MiB")
        self.assertEqual(band(1024),"512 MiB-2 GiB")
        self.assertEqual(band(4096),">=2 GiB")
        self.assertEqual(band(None),"unknown")

    def test_all_keep_agrees_but_no_gold_accuracy(self):
        b=model_input()
        pred=[{"id":c["id"],"decision":"KEEP"} for c in b["cases"]]
        results={name:{"predictions":pred,"meta":{"blind_sha256":hash_data(b),"duration_s":1}}
                 for name in ("minimax","deepseek")}
        r=compare(b,results)
        self.assertEqual(r["agreement_ratio"],1)
        self.assertIsNone(r["cohen_kappa"])
        self.assertTrue(r["accuracy_not_computable"])
        self.assertEqual(r["unsubstantiated_recommendations"],{"minimax":[],"deepseek":[]})

    def test_hard_veto_and_unknown_rebuild_detected(self):
        b=model_input()
        a=[{"id":c["id"],"decision":"KEEP"} for c in b["cases"]]
        a[0]["decision"]="RECOMMEND"
        a[6]["decision"]="RECOMMEND" # ACTIVE; independent safety veto
        x={"predictions":a,"meta":{"blind_sha256":hash_data(b),"duration_s":1}}
        y={"predictions":[{"id":c["id"],"decision":"KEEP"} for c in b["cases"]],
           "meta":{"blind_sha256":hash_data(b),"duration_s":1}}
        r=compare(b,{"minimax":x,"deepseek":y})
        self.assertEqual(len(r["unsubstantiated_recommendations"]["minimax"]),2)
        self.assertIn("C07",r["unsubstantiated_recommendations"]["minimax"])
        self.assertEqual(len(r["disagreements"]),2)

    def test_snapshot_digest_guard(self):
        b=model_input()
        pred=[{"id":c["id"],"decision":"KEEP"} for c in b["cases"]]
        with self.assertRaises(AssertionError):
            compare(b,{"a":{"predictions":pred,"meta":{"blind_sha256":"wrong"}},
                       "b":{"predictions":pred,"meta":{"blind_sha256":hash_data(b)}}})

if __name__=="__main__":unittest.main(verbosity=2)
