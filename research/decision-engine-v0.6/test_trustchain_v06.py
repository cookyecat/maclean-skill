#!/usr/bin/env python3
"""MacLean v0.6: reproducible identity/envelope/privacy regressions (no cleanup)."""
from __future__ import annotations
import copy,datetime as dt,json,os,pathlib,tempfile,unittest
from evidence_envelope import seal,verify,fixture_example,InvalidEvidence
from native_e2_fixture import bounded_file,run_lab
UTC=dt.timezone.utc
SOURCE="synthetic.playwright-native"
SUBJECT="ABCD1234"

def sample_body():
    return {"binary":"EXEC_MODE_ONLY","clients":"PARTIAL_SYNTHETIC",
            "activity":"NOT_OBSERVED_SHALLOW","coverage_complete":False,
            "publisher_listed":True,"observed_in_real_cache":False}

def ctx(body=None):
    key=os.urandom(32);now=dt.datetime.now(UTC)
    record=seal(key=key,source=SOURCE,subject=SUBJECT,
                body=body or sample_body(),issued_at=now,nonce=os.urandom(16).hex())
    return key,now,record

def check(key,now,record,**kwargs):
    return verify(record,key=key,expected_source=SOURCE,expected_subject=SUBJECT,
                  now=now,**kwargs)

class TrustTests(unittest.TestCase):
    def test_fixture_example_has_no_authorization(self):
        result=fixture_example()
        self.assertEqual(result["integrity_check"],"PASS")
        self.assertFalse(result["deletion_authorized"])
        self.assertFalse(result["e3_fully_proven"])

    def test_unobserved_file_not_safe(self):
        k,n,r=ctx()
        verdict=check(k,n,r)
        self.assertEqual(verdict["decision_hint"],"KEEP")
        self.assertFalse(verdict["recommended_for_cleanup"])

    def test_positive_reference_defers(self):
        body=sample_body();body["activity"]="POSITIVE_OPEN_REFERENCE"
        k,n,r=ctx(body)
        self.assertEqual(check(k,n,r)["decision_hint"],"DEFER")

    def test_unknown_reference_keeps(self):
        body=sample_body();body["activity"]="UNKNOWN"
        k,n,r=ctx(body)
        self.assertEqual(check(k,n,r)["decision_hint"],"KEEP")

    def test_modified_report_rejected(self):
        k,n,r=ctx();modified=copy.deepcopy(r)
        modified["payload"]["body"]["publisher_listed"]=False
        with self.assertRaises(InvalidEvidence):check(k,n,modified)

    def test_forged_tag_rejected(self):
        k,n,r=ctx();r["hmac_sha256"]="0"*64
        with self.assertRaises(InvalidEvidence):check(k,n,r)

    def test_different_key_rejected(self):
        k,n,r=ctx()
        with self.assertRaises(InvalidEvidence):check(os.urandom(32),n,r)

    def test_replay_nonce_rejected(self):
        k,n,r=ctx();seen=set()
        check(k,n,r,used_nonces=seen)
        with self.assertRaises(InvalidEvidence):check(k,n,r,used_nonces=seen)

    def test_old_evidence_rejected(self):
        k,n,r=ctx()
        with self.assertRaises(InvalidEvidence):
            check(k,n+dt.timedelta(minutes=5),r)

    def test_future_evidence_rejected(self):
        k,n,r=ctx()
        with self.assertRaises(InvalidEvidence):
            check(k,n-dt.timedelta(minutes=5),r)

    def test_source_mismatch_rejected(self):
        k,n,r=ctx()
        with self.assertRaises(InvalidEvidence):
            verify(r,key=k,now=n,expected_source="synthetic.puppeteer-native",
                   expected_subject=SUBJECT)

    def test_subject_mismatch_rejected(self):
        k,n,r=ctx()
        with self.assertRaises(InvalidEvidence):
            verify(r,key=k,now=n,expected_source=SOURCE,expected_subject="ZZZZ9999")

    def test_unlisted_extra_payload_field_rejected(self):
        k,n,r=ctx();r["payload"]["raw_path"]="/Users/nobody/secret"
        with self.assertRaises(InvalidEvidence):check(k,n,r)

    def test_unlisted_extra_evidence_field_rejected(self):
        b=sample_body();b["executable_command"]="rm -rf"
        with self.assertRaises(InvalidEvidence):ctx(b)

    def test_synthetic_cannot_claim_real_e3(self):
        b=sample_body();b["observed_in_real_cache"]=True
        with self.assertRaises(InvalidEvidence):ctx(b)

    def test_client_coverage_completeness_unavailable(self):
        b=sample_body();b["coverage_complete"]=True
        with self.assertRaises(InvalidEvidence):ctx(b)

    def test_ai_provenance_forbidden(self):
        k=os.urandom(32);n=dt.datetime.now(UTC)
        with self.assertRaises(InvalidEvidence):
            seal(key=k,source="llm.self-reported-e3",subject=SUBJECT,
                 body=sample_body(),issued_at=n,nonce=os.urandom(16).hex())

    def test_weak_key_rejected(self):
        with self.assertRaises(InvalidEvidence):
            seal(key=b"x"*8,source=SOURCE,subject=SUBJECT,
                 body=sample_body(),issued_at=dt.datetime.now(UTC),nonce="a"*32)

    def test_invalid_subject_rejected(self):
        with self.assertRaises(InvalidEvidence):
            seal(key=os.urandom(32),source=SOURCE,subject="~/Documents",
                 body=sample_body(),issued_at=dt.datetime.now(UTC),nonce="a"*32)

    def test_invalid_nonce_rejected(self):
        with self.assertRaises(InvalidEvidence):
            seal(key=os.urandom(32),source=SOURCE,subject=SUBJECT,
                 body=sample_body(),issued_at=dt.datetime.now(UTC),nonce="UNSAFE")

    def test_naive_datetime_rejected(self):
        with self.assertRaises(InvalidEvidence):
            seal(key=os.urandom(32),source=SOURCE,subject=SUBJECT,
                 body=sample_body(),issued_at=dt.datetime.now(),nonce="a"*32)

    def test_unapproved_real_binary_claim_rejected(self):
        b=sample_body();b["binary"]="VERIFIED_BROWSER"
        with self.assertRaises(InvalidEvidence):ctx(b)

    def test_real_catalog_sensor_cannot_claim_binary(self):
        b=sample_body();k=os.urandom(32);n=dt.datetime.now(UTC)
        with self.assertRaises(InvalidEvidence):
            seal(key=k,source="real.catalog-leaf-open-reference",subject=SUBJECT,
                 body=b,issued_at=n,nonce="a"*32)

    def test_only_disposable_binary_fixture_states(self):
        with tempfile.TemporaryDirectory(prefix="maclean-v06-test-") as temp:
            root=pathlib.Path(temp).resolve();f=root/"browser.bin"
            self.assertEqual(bounded_file(root,"browser.bin")["status"],"MISSING")
            f.write_bytes(b"fake executable bytes")
            self.assertEqual(bounded_file(root,"browser.bin")["status"],"NOT_EXECUTABLE")
            f.chmod(0o700)
            outcome=bounded_file(root,"browser.bin")
            self.assertEqual(outcome["status"],"EXECUTABLE_MODE_ONLY")
            self.assertFalse(outcome["authentic_browser"])
            self.assertFalse(outcome["safe_to_delete"])

    def test_symlink_escape_denied(self):
        with tempfile.TemporaryDirectory(prefix="maclean-v06-test-") as temp:
            root=pathlib.Path(temp).resolve()
            (root/"link").symlink_to(pathlib.Path.home(),target_is_directory=True)
            self.assertEqual(bounded_file(root,"link/whatever")["status"],"SYMLINK_DENIED")

    def test_parent_path_escape_denied(self):
        with tempfile.TemporaryDirectory(prefix="maclean-v06-test-") as temp:
            root=pathlib.Path(temp).resolve()
            self.assertEqual(bounded_file(root,"../outside")["status"],"INVALID_RELATIVE")
            self.assertEqual(bounded_file(root,"/etc/passwd")["status"],"INVALID_RELATIVE")

    def test_native_cli_pinned_isolation_if_available(self):
        marker=pathlib.Path("/tmp/maclean-v05-native-latest-path.txt")
        if not marker.is_file():self.skipTest("pinned on-Mac CLI lab unavailable in CI")
        pkg=pathlib.Path(marker.read_text().strip())
        outcome=run_lab(pkg)
        self.assertEqual(outcome["native_list_exit_code"],0)
        self.assertTrue(outcome["native_list_prints_client_path"])
        self.assertTrue(outcome["native_list_contains_chromium"])
        self.assertEqual(outcome["link_metadata_client_count"],1)
        self.assertEqual(outcome["phony_browser_file"],"MISSING")
        self.assertEqual(outcome["symbolic_link"],"SYMLINK_DENIED")
        self.assertFalse(outcome["real_browser_integrity_verified"])
        self.assertFalse(outcome["deletion_authorized"])

if __name__=="__main__":unittest.main(verbosity=2)
