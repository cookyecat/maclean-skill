#!/usr/bin/env python3
"""MacLean v0.4 synthetic-only negative and bounded-scope regression tests."""
import copy
import json
import pathlib
import tempfile
import unittest

from operation_registry import assess, ContractError, REGISTRY, validate_graph
from synthetic_dependency_graph import (
    collect, disposable_fixture, FixtureBoundaryError, MARKER, PREFIX,
)

class TestOperationContracts(unittest.TestCase):
    def graph(self, family="puppeteer"):
        with disposable_fixture() as root:
            return collect(root,app_family=family)

    def test_scoped_unused_browser_exact_but_never_authorized(self):
        g=self.graph()
        r=assess("puppeteer.browsers.uninstall_build",g,["chrome-0999"],target="chrome-0999")
        self.assertEqual(r["synthetic_effect_ids"],["chrome-0999"])
        self.assertTrue(r["exact_scope_matches_approved"])
        self.assertFalse(r["deletion_authorized"])
        self.assertFalse(r["production_eligible"])
        self.assertIn("NATIVE_METHOD_NOT_BOUNDED_FIXTURE_VERIFIED",r["flags"])

    def test_broad_clear_exceeds_narrow_approval(self):
        r=assess("puppeteer.browsers.clear_all",self.graph(),["chrome-0999"])
        self.assertEqual(r["synthetic_effect_size"],3)
        self.assertIn("EXACT_APPROVED_SET_MISMATCH",r["flags"])
        self.assertIn("SYNTHETIC_CLIENT_STILL_REFERENCES_TARGET",r["flags"])

    def test_playwright_uninstall_all_touches_live_fixture_clients(self):
        r=assess("playwright.browsers.uninstall_all",self.graph("playwright"),["chrome-0999"])
        self.assertIn("EXACT_APPROVED_SET_MISMATCH",r["flags"])
        self.assertIn("SYNTHETIC_CLIENT_STILL_REFERENCES_TARGET",r["flags"])

    def test_playwright_gc_dynamic_scope_undetermined(self):
        r=assess("playwright.browsers.gc_unused",self.graph("playwright"),["chrome-0999"])
        self.assertIsNone(r["synthetic_effect_size"])
        self.assertIn("EFFECT_SCOPE_UNPROVEN",r["flags"])

    def test_client_uninstall_scope_can_only_reference_installed(self):
        r=assess("playwright.browsers.uninstall_client",self.graph("playwright"),
                 ["chrome-1111","firefox-1542"],client="qa-suite")
        self.assertTrue(r["exact_scope_matches_approved"])
        self.assertIn("SYNTHETIC_CLIENT_STILL_REFERENCES_TARGET",r["flags"])

    def test_unknown_client_fails_scope(self):
        r=assess("playwright.browsers.uninstall_client",self.graph("playwright"),["chrome-0999"],
                 client="invisible-client")
        self.assertFalse(r["method_scope_decidable_in_fixture"])
        self.assertIn("CLIENT_NOT_EXACTLY_IDENTIFIED",r["flags"])

    def test_cross_app_fails_even_if_methods_seem_similar(self):
        for op in ("uv.cache.prune","playwright.browsers.gc_unused"):
            with self.assertRaises(ContractError):
                assess(op,self.graph(),["chrome-0999"])

    def test_unknown_method_fails(self):
        with self.assertRaises(ContractError):
            assess("generic.native.clean",self.graph(),["chrome-0999"])

    def test_duplicate_or_uninstalled_approval_denied(self):
        for ids in (["chrome-0999","chrome-0999"],["unrecognized-9999"]):
            with self.assertRaises(ContractError):
                assess("puppeteer.browsers.uninstall_build",self.graph(),ids,target="chrome-0999")

    def test_activity_and_protection_veto_synthetic_preview(self):
        g=self.graph()
        for kwargs,flag in (
            ({"active_targets":["chrome-0999"]},"ACTIVE_TARGET_VETO"),
            ({"protected_targets":["chrome-0999"]},"PROTECTED_TARGET_VETO")):
            r=assess("puppeteer.browsers.uninstall_build",g,["chrome-0999"],
                     target="chrome-0999",**kwargs)
            self.assertIn(flag,r["flags"])
            self.assertFalse(r["production_eligible"])

    def test_approval_cannot_include_referenced_extra(self):
        r=assess("puppeteer.browsers.uninstall_build",self.graph(),
                 ["chrome-0999","chrome-1111"],target="chrome-0999")
        self.assertIn("EXACT_APPROVED_SET_MISMATCH",r["flags"])

    def test_fixture_graph_reference_mapping(self):
        g=self.graph()
        self.assertEqual(g["synthetic_orphan_ids"],["chrome-0999"])
        self.assertEqual(set(g["clients"]["qa-suite"]),{"chrome-1111","firefox-1542"})
        self.assertEqual(g["app_family"],"puppeteer")

    def test_symlink_browser_entry_denied(self):
        with disposable_fixture() as root:
            (root/"browsers"/"evil-link").symlink_to(pathlib.Path.home(),target_is_directory=True)
            with self.assertRaises(FixtureBoundaryError):
                collect(root)

    def test_symlink_client_manifest_denied(self):
        with disposable_fixture() as root:
            target=root/"clients"/"qa-suite.json"
            target.unlink()
            target.symlink_to(root/"clients"/"web-research.json")
            with self.assertRaises(FixtureBoundaryError):
                collect(root)

    def test_missing_browser_build_reference_denied(self):
        with disposable_fixture() as root:
            f=root/"clients"/"qa-suite.json"
            f.write_text(json.dumps({"client_id":"qa-suite","requires":["not-installed"]}))
            with self.assertRaises(FixtureBoundaryError):
                collect(root)

    def test_invalid_manifest_shape_denied(self):
        with disposable_fixture() as root:
            f=root/"clients"/"qa-suite.json"
            f.write_text('{"client_id":"qa-suite","requires":["chrome-1111"],"private_path":"hidden"}')
            with self.assertRaises(FixtureBoundaryError):
                collect(root)

    def test_missing_fixture_marker_denied(self):
        with disposable_fixture() as root:
            (root/MARKER).unlink()
            with self.assertRaises(FixtureBoundaryError):
                collect(root)

    def test_open_real_directory_denied(self):
        with self.assertRaises(FixtureBoundaryError):
            collect(pathlib.Path.home())

    def test_world_readable_fixture_denied(self):
        with disposable_fixture() as root:
            root.chmod(0o755)
            with self.assertRaises(FixtureBoundaryError):
                collect(root)

    def test_bounded_entry_count_denied(self):
        with disposable_fixture() as root:
            for n in range(101):
                (root/"browsers"/f"extra-{n}").mkdir()
            with self.assertRaises(FixtureBoundaryError):
                collect(root)

    def test_incomplete_client_universe_denied(self):
        g=self.graph()
        g["complete_client_universe"]=False
        with self.assertRaises(ContractError):
            assess("puppeteer.browsers.clear_all",g,["chrome-0999"])

    def test_assessment_is_nonmutating(self):
        with disposable_fixture() as root:
            before=sorted(x.name for x in (root/"browsers").iterdir())
            g=collect(root)
            for _ in range(4):
                assess("puppeteer.browsers.clear_all",g,["chrome-0999"])
            after=sorted(x.name for x in (root/"browsers").iterdir())
            self.assertEqual(before,after)

    def test_no_host_usage_or_deletion_method_exposed(self):
        for o in REGISTRY.values():
            self.assertTrue(o.publisher_doc_url.startswith("https://"))
            self.assertIsNotNone(o.scope)
        g=self.graph()
        p=assess("puppeteer.browsers.uninstall_build",g,["chrome-0999"],target="chrome-0999")
        self.assertFalse(p["production_eligible"])
        self.assertNotIn("command",p)
        self.assertNotIn("apply",p)

if __name__=="__main__":
    unittest.main(verbosity=2)
