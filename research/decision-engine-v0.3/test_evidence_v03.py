#!/usr/bin/env python3
"""Only synthetic/isolated evidence-provenance tests; no real cache scans."""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import tempfile, unittest
from evidence_contract import Evidence, EvidenceError, PUBLISHER_CATALOG, from_json
from sandbox_uv_e2 import PREFIX, MARKER, guarded_cache, run

def example(kind="uv",state="REVIEW"):
    return Evidence(artifact_kind=kind,state=state)

def publisher(e):
    return replace(e,publisher_claim_verified=True,
                   publisher_doc_id=PUBLISHER_CATALOG[e.artifact_kind]["url"])

def fixture(e):
    return replace(e,fixture_passed=True,fixture_isolated=True,
                   fixture_method="NATIVE_PRUNE" if e.artifact_kind=="uv" else "SYNTHETIC_LOCAL_METHOD")

def e3_flags(e,origin="SYNTHETIC_TEST"):
    return replace(e,exact_local_identity_verified=True,
      exact_target_use_checked=True,active_target_reference=False,
      download_recovery_verified=True,offline_dependency_excluded=True,
      workflow_impact_low=True,attestation_origin=origin)

class EvidenceContractTests(unittest.TestCase):
    def test_e0_is_not_a_recommendation(self):
        e=example().evaluate()
        self.assertFalse(e["e1_publisher"])
        self.assertFalse(e["ready_for_ai_benefit_assessment"])
        self.assertIn("CURRENT_RECOVERY_FEASIBILITY_E3",e["missing_evidence"])
        self.assertFalse(e["deletion_authorized"])

    def test_official_document_is_e1_not_e3(self):
        result=publisher(example()).evaluate()
        self.assertTrue(result["e1_publisher"])
        self.assertFalse(result["e2_fixture"])
        self.assertFalse(result["e3_current_use_and_recovery"])

    def test_bounded_fixture_is_e2_not_real_e3(self):
        e=fixture(publisher(example())).evaluate()
        self.assertTrue(e["e2_fixture"])
        self.assertFalse(e["e3_current_use_and_recovery"])

    def test_synthetic_e3_never_escalates_to_live_e3(self):
        e=e3_flags(fixture(publisher(example()))).evaluate()
        self.assertTrue(e["synthetic_e3_counterfactual_only"])
        self.assertFalse(e["ready_for_ai_benefit_assessment"])
        self.assertFalse(e["deletion_authorized"])

    def test_live_e3_still_does_not_authorize_delete(self):
        # Simulates independent sensor data; not a real attestation.
        e=e3_flags(fixture(publisher(example())),origin="INDEPENDENT_LOCAL_SENSOR").evaluate()
        self.assertTrue(e["ready_for_ai_benefit_assessment"])
        self.assertFalse(e["deletion_authorized"])
        self.assertFalse(e["actual_cleanup_support"])

    def test_active_and_protected_remain_vetoed(self):
        for state in ("ACTIVE","PROTECTED","UNKNOWN"):
            e=e3_flags(fixture(publisher(example(state=state))),
                       origin="INDEPENDENT_LOCAL_SENSOR").evaluate()
            self.assertTrue(e["machine_state_veto"])
            self.assertFalse(e["ready_for_ai_benefit_assessment"])

    def test_bad_publisher_citation_fail_closed(self):
        with self.assertRaises(EvidenceError):
            replace(example(),publisher_claim_verified=True,publisher_doc_id="https://example.com").evaluate()

    def test_unisolated_fixture_fail_closed(self):
        with self.assertRaises(EvidenceError):
            replace(publisher(example()),fixture_passed=True,
                    fixture_method="NATIVE_CLEAN",fixture_isolated=False).evaluate()

    def test_exact_file_reference_without_verification_fail_closed(self):
        with self.assertRaises(EvidenceError):
            replace(example(),active_target_reference=False).evaluate()

    def test_out_of_catalog_or_unknown_state_fails(self):
        for e in (example("browser_profile"),example(state="NOT_A_STATE"),
                  replace(example(),attestation_origin="AI_SAYS_TRUE")):
            with self.assertRaises(EvidenceError):e.evaluate()

    def test_unknown_input_fields_rejected(self):
        with self.assertRaises(EvidenceError):
            from_json({"artifact_kind":"uv","state":"REVIEW",
                       "model_claim":"cleanable"})
    def test_non_uv_catalog_document_support(self):
        for app in ("puppeteer","playwright"):
            e=publisher(example(app)).evaluate()
            self.assertTrue(e["e1_publisher"])
            self.assertFalse(e["ready_for_ai_benefit_assessment"])

    def test_disposable_root_guard_rejects_forged_paths(self):
        with tempfile.TemporaryDirectory(prefix=PREFIX) as td:
            root=Path(td);root.chmod(0o700)
            cache=root/"uv-cache";cache.mkdir()
            with self.assertRaises(ValueError):
                guarded_cache(root,cache)
            (root/MARKER).write_text("only fixture")
            self.assertEqual(guarded_cache(root,cache),cache.resolve())
            wrong=root/"other";wrong.mkdir()
            with self.assertRaises(ValueError):
                guarded_cache(root,wrong)

    def test_fixture_native_operations_and_lsof(self):
        r=run()
        if r["uv_prune"]["status"]=="NOT_INSTALLED":
            self.skipTest("uv unavailable in this environment")
        self.assertTrue(r["fixture_e2"],r)
        self.assertTrue(r["sandbox_sentinel_preserved"])
        self.assertTrue(r["symlink_to_home_refused"])
        self.assertEqual(r["invalid_targets_refused"],3)
        self.assertFalse(r["real_cache_accessed"])
        self.assertFalse(r["real_cache_deleted"])
        if r["exact_open_handle"].get("supported"):
            self.assertTrue(r["exact_open_handle"]["exact_open_reference_detected"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
