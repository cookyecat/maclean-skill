#!/usr/bin/env python3
"""Publisher-method audit regressions. Synthetic only; no cleanup API."""
import unittest
from audit_strategy_v03 import audit

def case(id,kind,state="REVIEW",level="E3_SYNTHETIC"):
 return {"id":id,"artifact_kind":kind,"machine_safety_state":state,"evidence_level":level}
def pred(id,decision="RECOMMEND",method="NATIVE_PRUNE"):
 return {"id":id,"decision":decision,"cleanup_strategy":method}
def judge(c,p):
 return audit({"is_synthetic":True,"dataset":"evidence-ladder-synthetic-v0.3","cases":c},
              {"predictions":p})
class StrategyTests(unittest.TestCase):
 def test_uv_prune_fixture_but_no_delete_permission(self):
  r=judge([case("a","uv")],[pred("a")])
  self.assertEqual(r["method_or_evidence_issues"],[])
  self.assertFalse(r["deletion_authorized"])
 def test_browser_clean_scope_not_verified(self):
  for k in ("puppeteer","playwright"):
   r=judge([case("b",k)],[pred("b",method="NATIVE_CLEAN")])
   self.assertEqual(len(r["method_or_evidence_issues"]),1)
 def test_puppeteer_exact_path_has_no_verified_adapter(self):
  r=judge([case("b","puppeteer")],[pred("b",method="EXACT_PATH")])
  self.assertEqual(r["method_or_evidence_issues"][0]["status"],"UNVERIFIED")
 def test_active_class_remains_independent_veto(self):
  r=judge([case("a","uv",state="ACTIVE")],[pred("a")])
  self.assertEqual(r["violations_of_active_or_protected"],["a"])
 def test_e1_only_cannot_be_recommended(self):
  r=judge([case("a","uv",level="E1")],[pred("a")])
  self.assertTrue(any(e["issue"]=="RECOMMEND_WITHOUT_SYNTHETIC_E3" for e in r["method_or_evidence_issues"]))
 def test_nonrecommendation_cannot_specify_method(self):
  r=judge([case("a","uv")],[pred("a",decision="KEEP",method="NATIVE_PRUNE")])
  self.assertTrue(any(e["issue"]=="NONRECOMMEND_METHOD_MUST_BE_NONE" for e in r["method_or_evidence_issues"]))
 def test_none_does_not_authorize(self):
  r=judge([case("a","uv")],[pred("a",decision="KEEP",method="NONE")])
  self.assertEqual(r["method_or_evidence_issues"],[])
  self.assertFalse(r["deletion_authorized"])
if __name__=="__main__":unittest.main(verbosity=2)
