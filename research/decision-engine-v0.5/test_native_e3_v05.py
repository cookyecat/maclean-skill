#!/usr/bin/env python3
"""MacLean v0.5 safety regressions. No real cache deletion or project inspection."""
from __future__ import annotations
import copy,datetime,os,pathlib,tempfile,unittest
from unittest.mock import patch
from e3_failclosed_gate import assess_report,classify_one,GateError
from e3_positive_sensor import path_safe,synthetic_positive_control,ALLOWED_STATES
from native_capability_probe import probe as native_probe

def rec(state="NOT_OBSERVED_IN_SHALLOW_SCAN"):
    return {
      "schema":"maclean-e3-positive-observation-v0.5",
      "observation_time_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "results":{"puppeteer":{"state":state},"playwright":{"state":"ABSENT"}},
      "content_read":False,"personal_profiles_scanned":False,
      "direct_leaf_child_metadata_may_be_enumerated_by_lsof":True,
      "any_real_file_modified":False,"services_stopped":False,
    }

class EvidenceV05Tests(unittest.TestCase):
    def test_absence_of_lsof_reference_never_recommends(self):
        x=assess_report(rec())
        p=x["categories"]["puppeteer"]
        self.assertEqual(p["decision_hint"],"KEEP")
        self.assertFalse(p["safe_to_delete_inferred"])
        self.assertFalse(p["no_future_dependency_proven"])
        self.assertEqual(x["all_default_cleanup_recommendations"],[])

    def test_positive_open_reference_defers(self):
        x=assess_report(rec("OPEN_REFERENCE_OBSERVED"))
        self.assertEqual(x["categories"]["puppeteer"]["decision_hint"],"DEFER")
        self.assertFalse(x["native_operation_authorized"])

    def test_absent_root_not_cleanup_suggestion(self):
        x=assess_report(rec("ABSENT"))
        self.assertEqual(x["categories"]["puppeteer"]["decision_hint"],"KEEP")

    def test_denied_root_not_cleanup_suggestion(self):
        x=assess_report(rec("DENIED"))
        self.assertEqual(x["categories"]["puppeteer"]["decision_hint"],"KEEP")

    def test_unknown_lsof_errors_fail_closed(self):
        x=assess_report(rec("INCONCLUSIVE"))
        self.assertEqual(x["categories"]["puppeteer"]["decision_hint"],"KEEP")

    def test_sensor_timestamp_stale(self):
        x=rec()
        x["observation_time_utc"]=(datetime.datetime.now(datetime.timezone.utc)-
                                   datetime.timedelta(minutes=10)).isoformat()
        v=assess_report(x)
        self.assertTrue(v["stale"])
        self.assertEqual(v["categories"]["puppeteer"]["reason"],"STALE_READ_ONLY_SENSOR_RESULT")

    def test_future_timestamp_invalidated(self):
        x=rec("OPEN_REFERENCE_OBSERVED")
        x["observation_time_utc"]=(datetime.datetime.now(datetime.timezone.utc)+
                                    datetime.timedelta(hours=2)).isoformat()
        self.assertTrue(assess_report(x)["stale"])

    def test_sensor_without_timezone_rejected(self):
        x=rec();x["observation_time_utc"]="2026-10-17T12:00:00"
        with self.assertRaises(GateError):assess_report(x)

    def test_false_privacy_scope_claim_rejected(self):
        x=rec();x["personal_profiles_scanned"]=True
        with self.assertRaises(GateError):assess_report(x)

    def test_unknown_scope_disclosure_rejected(self):
        x=rec();x.pop("direct_leaf_child_metadata_may_be_enumerated_by_lsof")
        with self.assertRaises(GateError):assess_report(x)

    def test_modified_user_data_rejected(self):
        x=rec();x["any_real_file_modified"]=True
        with self.assertRaises(GateError):assess_report(x)

    def test_stopped_service_rejected(self):
        x=rec();x["services_stopped"]=True
        with self.assertRaises(GateError):assess_report(x)

    def test_extra_scanner_targets_rejected(self):
        x=rec();x["results"]["private_profile"]={"state":"ABSENT"}
        with self.assertRaises(GateError):assess_report(x)

    def test_unknown_sensor_state_rejected(self):
        x=rec();x["results"]["puppeteer"]["state"]="UNUSED_SAFE"
        with self.assertRaises(GateError):assess_report(x)

    def test_path_guard_disallows_generic_home(self):
        home=pathlib.Path.home().absolute()
        self.assertFalse(path_safe(home,home))
        self.assertFalse(path_safe(home,home/"Documents"))
        self.assertFalse(path_safe(home,home/"Library/Application Support/Google/Chrome/Default"))

    def test_path_guard_allows_only_two_fixed_catalog_leaves(self):
        home=pathlib.Path.home().absolute()
        self.assertTrue(path_safe(home,home/".cache/puppeteer"))
        self.assertTrue(path_safe(home,home/"Library/Caches/ms-playwright"))

    def test_symlinked_exact_leaf_denied(self):
        with tempfile.TemporaryDirectory(prefix="maclean-v05-test-home-") as t:
            h=pathlib.Path(t);(h/".cache").mkdir()
            (h/".cache"/"puppeteer").symlink_to(pathlib.Path.home(),target_is_directory=True)
            self.assertFalse(path_safe(h,h/".cache"/"puppeteer"))

    def test_disposable_positive_reference_real_lsof(self):
        result=synthetic_positive_control()
        if result["state"]=="INCONCLUSIVE":self.skipTest("lsof not available")
        self.assertTrue(result["control_succeeded"],result)
        self.assertEqual(result["state"],"OPEN_REFERENCE_OBSERVED")
        self.assertFalse(result["any_real_file_modified"])

    def test_native_probe_does_not_use_npx(self):
        p=native_probe()
        self.assertFalse(p["npx_executed"])
        self.assertFalse(p["package_downloaded"])
        self.assertFalse(p["real_user_cache_cleaned"])
        self.assertFalse(p["e2_browser_native_verified"])

    def test_sensor_reports_never_approve(self):
        for state in ALLOWED_STATES:
            x=assess_report(rec(state))
            self.assertFalse(x["native_operation_authorized"])
            self.assertFalse(x["user_batch_approval_authorized"])
            self.assertEqual(x["all_default_cleanup_recommendations"],[])

if __name__=="__main__":
    unittest.main(verbosity=2)
