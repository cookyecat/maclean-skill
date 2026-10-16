#!/usr/bin/env python3
"""MacLean v0.7 synthetic-only source boundary and attestation tests."""
import copy,hashlib,json,pathlib,secrets,shutil,tempfile,unittest
from project_witness import fixture,scan,ScopeDenied,guarded_root
from fixture_attestation import FixtureWitnessIssuer,AttestationRejected,digest

SEL=["client-ALPHA"]
def att(root,issuer=None):
    i=issuer or FixtureWitnessIssuer()
    pid=digest({"synthetic_only":True,"approved_exact_targets":["chromium@1248"]})
    nonce=secrets.token_hex(16)
    record=i.issue(root,SEL,plan_digest=pid,request_nonce=nonce)
    return i,pid,nonce,record
def verify(i,pid,nonce,record,root,**kw):
    return i.verify_fresh(record,root,SEL,expected_plan_digest=pid,
                          expected_nonce=nonce,**kw)

class ProjectWitnessTests(unittest.TestCase):
    def test_selected_only_fixture_passes(self):
        with fixture() as root:
            d=scan(root,SEL)
            self.assertEqual(d["selected_clients"]["client-ALPHA"]["browser_revisions"],["chromium@1248"])
            self.assertEqual(d["unknown_unread_link_targets"],0)
            self.assertFalse(d["real_client_universe_complete"])
            self.assertFalse(d["deletion_authorized"])

    def test_unknown_external_link_does_not_stop_safe_selected_read(self):
        with fixture(True) as root:
            r=scan(root,SEL)
            self.assertEqual(r["unknown_unread_link_targets"],1)
            self.assertIn("UNKNOWN_CLIENT_REFERENCES",r["coverage_flags"])
            self.assertFalse(r["safe_to_clean"])

    def test_arbitrary_home_is_denied(self):
        with self.assertRaises(ScopeDenied):scan(pathlib.Path.home(),SEL)

    def test_duplicate_selected_ids_rejected(self):
        with fixture() as root:
            with self.assertRaises(ScopeDenied):scan(root,SEL+SEL)

    def test_unselected_client_id_denied(self):
        with fixture() as root:
            with self.assertRaises(ScopeDenied):scan(root,["../../Documents"])

    def test_missing_selected_project_denied(self):
        with fixture() as root:
            with self.assertRaises(ScopeDenied):scan(root,["client-MISSING"])

    def test_link_with_newline_denied(self):
        with fixture() as root:
            f=root/"registry"/".links"/"one"
            f.write_text(f.read_text()+"\n")
            with self.assertRaises(ScopeDenied):scan(root,SEL)

    def test_link_symlink_to_home_denied(self):
        with fixture() as root:
            f=root/"registry"/".links"/"one"
            f.unlink();f.symlink_to(pathlib.Path.home())
            with self.assertRaises(ScopeDenied):scan(root,SEL)

    def test_unselected_absolute_home_is_never_treated_as_scope_approval(self):
        with fixture() as root:
            f=root/"registry"/".links"/"one"
            f.write_text(str(pathlib.Path.home()))
            d=scan(root,SEL)
            self.assertEqual(d["unknown_unread_link_targets"],1)
            self.assertIn("SELECTED_LINK_MISSING",d["coverage_flags"])

    def test_project_parent_symlink_refused(self):
        with fixture() as root:
            p=root/"projects"/"client-ALPHA"
            shutil.rmtree(p)
            p.symlink_to(pathlib.Path.home())
            with self.assertRaises(ScopeDenied):scan(root,SEL)

    def test_node_modules_symlink_refused(self):
        with fixture() as root:
            p=root/"projects"/"client-ALPHA"/"node_modules"
            shutil.rmtree(p);p.symlink_to(pathlib.Path.home())
            with self.assertRaises(ScopeDenied):scan(root,SEL)

    def test_manifest_symlink_refused(self):
        with fixture() as root:
            f=root/"projects"/"client-ALPHA"/"node_modules"/"playwright-core"/"package.json"
            f.unlink();f.symlink_to(pathlib.Path.home())
            with self.assertRaises(ScopeDenied):scan(root,SEL)

    def test_missing_publisher_manifest_refused(self):
        with fixture() as root:
            f=root/"projects"/"client-ALPHA"/"node_modules"/"playwright-core"/"browsers.json"
            f.unlink()
            with self.assertRaises(ScopeDenied):scan(root,SEL)

    def test_invalid_browser_revision_refused(self):
        with fixture() as root:
            f=root/"projects"/"client-ALPHA"/"node_modules"/"playwright-core"/"browsers.json"
            f.write_text('{"browsers":[{"name":"chromium","revision":"../../secret"}]}')
            with self.assertRaises(ScopeDenied):scan(root,SEL)

    def test_oversized_json_refused(self):
        with fixture() as root:
            f=root/"projects"/"client-ALPHA"/"node_modules"/"playwright-core"/"browsers.json"
            f.write_text("x"*65537)
            with self.assertRaises(ScopeDenied):scan(root,SEL)

    def test_duplicate_native_links_refused(self):
        with fixture() as root:
            target=(root/"registry"/".links"/"one").read_text()
            (root/"registry"/".links"/"two").write_text(target)
            with self.assertRaises(ScopeDenied):scan(root,SEL)

    def test_registry_parent_symlink_refused(self):
        with fixture() as root:
            p=root/"registry"
            shutil.rmtree(p);p.symlink_to(pathlib.Path.home())
            with self.assertRaises(ScopeDenied):scan(root,SEL)

    def test_world_readable_fixture_refused(self):
        with fixture() as root:
            root.chmod(0o755)
            with self.assertRaises(ScopeDenied):scan(root,SEL)

class AttestationTests(unittest.TestCase):
    def test_plan_bound_fresh_fixture_cannot_authorize(self):
        with fixture(True) as root:
            i,p,n,e=att(root)
            r=verify(i,p,n,e,root)
            self.assertTrue(r["plan_digest_bound"])
            self.assertFalse(r["complete_real_e3"])
            self.assertFalse(r["deletion_authorized"])
            self.assertEqual(r["approved_cleanup_targets"],[])

    def test_wrong_plan_digest_denied(self):
        with fixture() as root:
            i,p,n,e=att(root)
            with self.assertRaises(AttestationRejected):
                verify(i,digest({"different":True}),n,e,root)

    def test_wrong_nonce_denied(self):
        with fixture() as root:
            i,p,n,e=att(root)
            with self.assertRaises(AttestationRejected):
                verify(i,p,secrets.token_hex(16),e,root)

    def test_tampered_manifest_claim_denied(self):
        with fixture() as root:
            i,p,n,e=att(root)
            e["payload"]["observation"]["real_client_universe_complete"]=True
            with self.assertRaises(AttestationRejected):verify(i,p,n,e,root)

    def test_invalid_hmac_denied(self):
        with fixture() as root:
            i,p,n,e=att(root);e["hmac_sha256"]="0"*64
            with self.assertRaises(AttestationRejected):verify(i,p,n,e,root)

    def test_replay_denied(self):
        with fixture() as root:
            i,p,n,e=att(root)
            verify(i,p,n,e,root)
            with self.assertRaises(AttestationRejected):verify(i,p,n,e,root)

    def test_expiration_denied(self):
        with fixture() as root:
            i,p,n,e=att(root)
            with self.assertRaises(AttestationRejected):
                verify(i,p,n,e,root,max_age_seconds=-1)

    def test_changed_selected_manifest_invalidates(self):
        with fixture() as root:
            i,p,n,e=att(root)
            f=root/"projects"/"client-ALPHA"/"node_modules"/"playwright-core"/"browsers.json"
            f.write_text('{"browsers":[{"name":"chromium","revision":"9999"}]}')
            with self.assertRaises(AttestationRejected):verify(i,p,n,e,root)

    def test_new_unknown_client_link_invalidates(self):
        with fixture() as root:
            i,p,n,e=att(root)
            (root/"registry"/".links"/"new").write_text("/non-authorized-project")
            with self.assertRaises(AttestationRejected):verify(i,p,n,e,root)

    def test_deleted_client_link_invalidates(self):
        with fixture() as root:
            i,p,n,e=att(root)
            (root/"registry"/".links"/"one").unlink()
            with self.assertRaises(AttestationRejected):verify(i,p,n,e,root)

    def test_other_issuer_cannot_verify(self):
        with fixture() as root:
            i,p,n,e=att(root)
            with self.assertRaises(AttestationRejected):verify(FixtureWitnessIssuer(),p,n,e,root)

    def test_nonsha_plan_rejected_before_issue(self):
        with fixture() as root:
            with self.assertRaises(AttestationRejected):
                FixtureWitnessIssuer().issue(root,SEL,plan_digest="temporary",request_nonce=secrets.token_hex(16))

    def test_no_arbitrary_model_payload_sign_method(self):
        self.assertFalse(hasattr(FixtureWitnessIssuer(),"sign_arbitrary_model_claim"))

    def test_source_does_not_mutate_fixture(self):
        with fixture(True) as root:
            path=root/"projects"/"client-ALPHA"/"node_modules"/"playwright-core"/"package.json"
            before=path.read_bytes()
            i,p,n,e=att(root);verify(i,p,n,e,root)
            self.assertEqual(path.read_bytes(),before)

if __name__=="__main__":unittest.main(verbosity=2)
