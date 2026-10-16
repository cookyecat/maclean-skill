#!/usr/bin/env python3
"""v1.0 method contract tests: exact targets, no deletion readiness."""
import unittest
from native_method_contract import compile_method,ContractDenied

def item(kind,path,method,tier="DEFAULT"):
    return {"kind":kind,"exact_path":path,"operation_id":method,
            "suggested_selection":tier,"method_adapter_verified":False,
            "executability":"REQUIRES_SEPARATE_OPERATION_ADAPTER"}

class ContractTests(unittest.TestCase):
    def test_exact_npm_content(self):
        x=compile_method(item("npm_cache","~/.npm/_cacache","npm.cache.clean_all"))
        self.assertEqual(x["scope"],"NPM_CONTENT_ONLY")
        self.assertFalse(x["executable"])
    def test_exact_npx_key(self):
        x=compile_method(item("npx_install","~/.npm/_npx/0123456789abcdef","npm.cache.npx.rm_exact","OPTIONAL"))
        self.assertEqual(x["scope"],"ONE_NPX_KEY")
        self.assertFalse(x["concurrent_active_npx_key_safe"])
    def test_exact_uv(self):
        x=compile_method(item("uv_cache","~/.cache/uv","uv.cache.prune"))
        self.assertEqual(x["scope"],"UV_PRUNE_UNUSED_ONLY")
    def test_npm_parent_denied(self):
        with self.assertRaises(ContractDenied):
            compile_method(item("npm_cache","~/.npm","npm.cache.clean_all"))
    def test_npx_parent_denied(self):
        with self.assertRaises(ContractDenied):
            compile_method(item("npx_install","~/.npm/_npx","npm.cache.npx.rm_exact"))
    def test_npx_traversal_denied(self):
        with self.assertRaises(ContractDenied):
            compile_method(item("npx_install","~/.npm/_npx/../../.ssh","npm.cache.npx.rm_exact"))
    def test_mismatched_method_denied(self):
        with self.assertRaises(ContractDenied):
            compile_method(item("npm_cache","~/.npm/_cacache","npm.cache.npx.rm_exact"))
    def test_unvetted_profile_denied(self):
        with self.assertRaises(ContractDenied):
            compile_method(item("profile_cache","~/Library/Application Support/Chrome","npm.cache.clean_all"))
    def test_unverified_claim_denied(self):
        e=item("npm_cache","~/.npm/_cacache","npm.cache.clean_all")
        e["method_adapter_verified"]=True
        with self.assertRaises(ContractDenied):compile_method(e)
    def test_not_selected_denied(self):
        with self.assertRaises(ContractDenied):
            compile_method(item("uv_cache","~/.cache/uv","uv.cache.prune","BLOCKED"))
    def test_relative_other_uv_denied(self):
        with self.assertRaises(ContractDenied):
            compile_method(item("uv_cache","~/.cache/other","uv.cache.prune"))
    def test_every_result_is_unapproved(self):
        for arg in [item("npm_cache","~/.npm/_cacache","npm.cache.clean_all"),
                    item("npx_install","~/.npm/_npx/0123456789abcdef","npm.cache.npx.rm_exact"),
                    item("uv_cache","~/.cache/uv","uv.cache.prune")]:
            e=compile_method(arg)
            self.assertFalse(e["production_method_approved"])
            self.assertFalse(e["user_approved"])
            self.assertIsNone(e["estimated_physical_reclaim_mib"])
if __name__=="__main__":unittest.main(verbosity=2)
