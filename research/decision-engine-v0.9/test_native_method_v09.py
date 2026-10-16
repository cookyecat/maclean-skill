#!/usr/bin/env python3
"""Native plan proposal tests: no actual delete or process guard override."""
import unittest
from regenerability_policy import Refused
from native_method_proposal import build

def row(id,kind,status="REVIEW",blocks=None,size=100.0,risk="",path=None):
    return {"id":id,"kind":kind,"status":status,"safety_blocks":blocks or [],
            "size_mib":size,"rebuild_risk":risk,"path":path or "~/.cache/"+id}

def source(*rows):
    return {"read_only":True,"ai_decision_required":True,"user_approved":False,
            "scope":"known_technical_targets","policy":"privacy-safe-v1",
            "candidates":list(rows)}

class ProposalTests(unittest.TestCase):
    def test_active_npm_is_native_proposal_not_executor_plan(self):
        r=build(source(row("a","npm_cache","ACTIVE",["RELATED_PROCESS_RUNNING"])))
        self.assertEqual(len(r["items"]),1)
        self.assertEqual(r["items"][0]["operation_id"],"npm.cache.clean_all")
        self.assertEqual(r["items"][0]["executability"],"REQUIRES_SEPARATE_OPERATION_ADAPTER")
        self.assertTrue(r["not_an_executor_plan"])
        self.assertFalse(r["user_approved"])
        self.assertNotIn("schema_version",r)

    def test_profile_and_protected_not_in_proposals(self):
        r=build(source(
            row("a","npm_cache",status="PROTECTED",blocks=["MUTATION_SAFETY_BLOCK"]),
            row("b","profile_cache",risk="offline_web_apps_risk")))
        self.assertEqual(r["items"],[])

    def test_npx_removal_only_optional(self):
        r=build(source(row("a","npx_install",status="ACTIVE",blocks=["RELATED_PROCESS_RUNNING"])))
        self.assertEqual(r["items"][0]["suggested_selection"],"OPTIONAL")

    def test_plan_identity_digest_changes_when_paths_change(self):
        a=build(source(row("a","npm_cache",path="~/.npm/_cacache")))
        b=build(source(row("a","npm_cache",path="~/.cache/other")))
        self.assertNotEqual(a["candidate_identity_sha256"],b["candidate_identity_sha256"])

    def test_original_report_without_detail_path_refused(self):
        with self.assertRaises(ValueError):
            build(source(dict(row("a","npm_cache"),path=None)))

    def test_original_executable_fields_absent(self):
        plan=build(source(row("a","npm_cache")))
        self.assertNotIn("targets",plan)
        self.assertNotIn("apply",plan)
        self.assertTrue(plan["may_not_apply"])

if __name__=="__main__":unittest.main(verbosity=2)
