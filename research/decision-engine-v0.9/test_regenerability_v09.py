#!/usr/bin/env python3
"""v0.9 research-only classification regression tests: no cleanup operations."""
import unittest
from regenerability_policy import classify,assess,Refused

def candidate(kind="npm_cache",id="x1",status="REVIEW",risk="",size=100.0,blocks=None,app=None):
    return {"id":id,"kind":kind,"status":status,"rebuild_risk":risk,"size_mib":size,
            "app":app,"safety_blocks":list(blocks or [])}
def report(*rows):
    return {"read_only":True,"user_approved":False,"ai_decision_required":True,
            "scope":"known_technical_targets","policy":"privacy-safe-v1",
            "candidates":list(rows)}

class RegenerabilityTests(unittest.TestCase):
    def test_npm_active_family_is_recommended_not_executable(self):
        r=classify(candidate(status="ACTIVE",blocks=["RELATED_PROCESS_RUNNING"]))
        self.assertEqual((r["selection"],r["method_id"]),("DEFAULT","npm.cache.clean_all"))
        self.assertTrue(r["coarse_activity_signal_ignored_for_eligibility"])
        self.assertFalse(r["execution_ready"])
    def test_npx_active_is_optional_precise_method(self):
        r=classify(candidate(kind="npx_install",status="ACTIVE",blocks=["RELATED_PROCESS_RUNNING"]))
        self.assertEqual((r["selection"],r["method_id"]),("OPTIONAL","npm.cache.npx.rm_exact"))
    def test_npx_empty_not_recommended(self):
        self.assertEqual(classify(candidate(kind="npx_install",size=0))["selection"],"BLOCKED")
    def test_installer_old_family_recommended(self):
        r=classify(candidate(kind="codex_runtime_installer",status="ACTIVE",blocks=["RELATED_PROCESS_RUNNING"]))
        self.assertEqual(r["selection"],"DEFAULT")
    def test_runtime_old_requires_opt_in(self):
        for kind in ("old_version","codex_daemon_old"):
            r=classify(candidate(kind=kind,status="ACTIVE",blocks=["RELATED_PROCESS_RUNNING"]))
            self.assertEqual(r["selection"],"OPTIONAL")
            self.assertFalse(r["execution_ready"])
    def test_profile_never_regenerable_default(self):
        for status in ("REVIEW","ACTIVE"):
            r=classify(candidate(kind="profile_cache",risk="offline_web_apps_risk",
                 status=status,blocks=["RELATED_PROCESS_RUNNING"] if status=="ACTIVE" else []))
            self.assertEqual(r["selection"],"BLOCKED")
    def test_protected_never_overridable(self):
        r=classify(candidate(status="PROTECTED",blocks=["MUTATION_SAFETY_BLOCK"]))
        self.assertEqual(r["selection"],"BLOCKED")
    def test_unknown_never_overridable(self):
        r=classify(candidate(status="UNKNOWN",blocks=["SIZE_UNAVAILABLE"]))
        self.assertEqual(r["selection"],"BLOCKED")
    def test_mixed_signal_cannot_be_ignored(self):
        r=classify(candidate(status="ACTIVE",blocks=["RELATED_PROCESS_RUNNING","OTHER_BLOCK"]))
        self.assertEqual(r["selection"],"BLOCKED")
    def test_unexpected_active_evidence_denied(self):
        self.assertEqual(classify(candidate(status="ACTIVE"))["selection"],"BLOCKED")
    def test_unknown_kind_denied(self):
        self.assertEqual(classify(candidate(kind="user_downloads"))["selection"],"BLOCKED")
    def test_bad_status_denied(self):
        with self.assertRaises(Refused):classify(candidate(status="SAFE"))
    def test_bad_safety_blocks_denied(self):
        with self.assertRaises(Refused):classify(dict(candidate(),safety_blocks="RELATED_PROCESS_RUNNING"))
    def test_executable_never_granted(self):
        for x in ("npm_cache","npx_install","codex_runtime_installer","old_version","profile_cache"):
            d=classify(candidate(kind=x,status="ACTIVE",blocks=["RELATED_PROCESS_RUNNING"]))
            self.assertFalse(d["execution_ready"])
            self.assertFalse(d["user_approved"])
    def test_editor_cache_can_be_recommended_with_coarse_active(self):
        r=classify(candidate(kind="app_cache",risk="editor_rebuild",status="ACTIVE",
                             blocks=["RELATED_PROCESS_RUNNING"],app="Cursor"))
        self.assertEqual(r["selection"],"DEFAULT")
    def test_logs_can_be_recommended_but_not_executed(self):
        r=classify(candidate(kind="app_log",risk="diagnostic"))
        self.assertEqual(r["selection"],"DEFAULT")
        self.assertFalse(r["execution_ready"])
    def test_typed_method_not_confused_with_legacy_path_deletion(self):
        r=classify(candidate(kind="npm_cache"))
        self.assertEqual(r["method_id"],"npm.cache.clean_all")
        self.assertFalse(r["operation_adapter_verified"])
    def test_review_is_only_legacy_preview_eligible(self):
        self.assertTrue(classify(candidate())["original_v14_path_preview_eligible"])
        self.assertFalse(classify(candidate(status="ACTIVE",blocks=["RELATED_PROCESS_RUNNING"]))["original_v14_path_preview_eligible"])
    def test_unapproved_snapshot_required(self):
        d=report(candidate());d["user_approved"]=True
        with self.assertRaises(Refused):assess(d)
    def test_duplicate_identity_rejected(self):
        with self.assertRaises(Refused):assess(report(candidate(),candidate()))
    def test_proposed_allocation_not_verified_reclaim(self):
        d=assess(report(candidate(),candidate(kind="npx_install",id="y2",size=200)))
        self.assertEqual(d["classes"]["DEFAULT"]["allocation_mib"],100)
        self.assertEqual(d["classes"]["OPTIONAL"]["allocation_mib"],200)
        self.assertIsNone(d["verified_reclaim_mib"])
        self.assertEqual(d["verified_executable_operation_count"],0)
    def test_no_promote_offline_media(self):
        self.assertEqual(classify(candidate(kind="app_cache",risk="offline_media_risk"))["selection"],"BLOCKED")
    def test_invalid_size_nan_kept(self):
        self.assertEqual(classify(candidate(size=float("nan")))["selection"],"BLOCKED")
if __name__=="__main__":unittest.main(verbosity=2)
