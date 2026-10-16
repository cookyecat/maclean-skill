#!/usr/bin/env python3
"""MacLean native v1.0 isolated scope and true npm/uv negative regressions."""
import json, os, pathlib, shutil, tempfile, unittest
from unittest.mock import patch
from isolated_native_lab import (fixture, guard, run_native, add_npx,
    native_npx_keys, native_npx_rm, npm_add, npm_verify, npm_clean,
    uv_prune, uv_clean, ScopeDenied, lab)
from synthetic_runtime_race import run as race_run

def tools_available():
    return bool(shutil.which("npm") and shutil.which("uv"))

class NativeSandboxTests(unittest.TestCase):
    def test_user_home_denied(self):
        with self.assertRaises(ScopeDenied): guard(pathlib.Path.home())

    def test_missing_marker_denied(self):
        with fixture() as r:
            (r/".maclean-native-fixture-only").unlink()
            with self.assertRaises(ScopeDenied):guard(r)

    def test_world_readable_root_denied(self):
        with fixture() as r:
            r.chmod(0o755)
            with self.assertRaises(ScopeDenied):guard(r)

    def test_symlinked_fixture_path_denied(self):
        with fixture() as r:
            src=r/"uv-cache"
            src.rmdir()
            src.symlink_to(pathlib.Path.home(),target_is_directory=True)
            with self.assertRaises(ScopeDenied):guard(r)

    def test_symlinked_cacache_denied(self):
        with fixture() as r:
            (r/"npm-cache"/"_cacache").symlink_to(pathlib.Path.home(),target_is_directory=True)
            with self.assertRaises(ScopeDenied):guard(r)

    def test_symlinked_npx_root_denied(self):
        with fixture() as r:
            (r/"npm-cache"/"_npx").symlink_to(pathlib.Path.home(),target_is_directory=True)
            with self.assertRaises(ScopeDenied):guard(r)

    def test_symlinked_user_config_denied(self):
        with fixture() as r:
            f=r/"user.npmrc"
            f.unlink();f.symlink_to(pathlib.Path.home())
            with self.assertRaises(ScopeDenied):guard(r)

    def test_unknown_native_command_denied_before_launch(self):
        with fixture() as r:
            for method,args in (("npm",["exec","evil"]),
                ("npm",["cache","clean","--cache","/tmp"]),
                ("uv",["cache","clean","--force"]),
                ("npm",["cache","npx","rm","--all"])):
                with self.assertRaises(ScopeDenied):run_native(r,method,args)

    def test_npx_path_traversal_denied(self):
        with fixture() as r:
            for key in ("../../etc","abcdef","0123456789abcdef/../foo","*"):
                with self.assertRaises(ScopeDenied):add_npx(r,key)
                with self.assertRaises(ScopeDenied):native_npx_rm(r,key)

    def test_exact_npx_native_removal_preserves_sibling(self):
        if not tools_available():self.skipTest("native npm/uv not available")
        with fixture() as r:
            k1="0123456789abcdef";k2="fedcba9876543210"
            p1=add_npx(r,k1);p2=add_npx(r,k2)
            self.assertEqual(native_npx_keys(r),{k1,k2})
            self.assertTrue(native_npx_rm(r,k1))
            self.assertFalse(p1.exists())
            self.assertTrue(p2.is_dir())
            self.assertEqual(native_npx_keys(r),{k2})

    def test_absent_npx_native_key_denied(self):
        if not tools_available():self.skipTest("native npm/uv not available")
        with fixture() as r:
            with self.assertRaises(ScopeDenied):native_npx_rm(r,"0123456789abcdef")

    def test_native_npm_verify_vs_full_clean(self):
        if not tools_available():self.skipTest("native npm/uv not available")
        with fixture() as r:
            add_npx(r,"0123456789abcdef")
            npm_add(r)
            path=r/"npm-cache"/"_cacache"
            self.assertTrue(path.is_dir())
            npm_verify(r)
            self.assertTrue(path.is_dir())
            npm_clean(r)
            self.assertFalse(path.exists())
            self.assertEqual(native_npx_keys(r),{"0123456789abcdef"})

    def test_native_uv_prune_and_clean_in_isolated_cache(self):
        if not tools_available():self.skipTest("native npm/uv not available")
        with fixture() as r:
            uv_prune(r)
            uv_clean(r)
            self.assertFalse((r/"uv-cache").is_symlink())

    def test_outside_sentinel_preserved(self):
        if not tools_available():self.skipTest("native npm/uv not available")
        with tempfile.TemporaryDirectory(prefix="maclean-v10-outside-") as d:
            outside=pathlib.Path(d)/"do-not-touch"
            outside.write_text("kept")
            with fixture() as r:
                npm_add(r);npm_clean(r);uv_prune(r);uv_clean(r)
            self.assertEqual(outside.read_text(),"kept")

    def test_real_native_combined_lab(self):
        if not tools_available():self.skipTest("native npm/uv not available")
        v=lab()
        self.assertTrue(v["npx_exact_removed"])
        self.assertTrue(v["npx_other_key_survived"])
        self.assertTrue(v["npm_npx_survived_cacache_clean"])
        self.assertFalse(v["npm_cacache_after_clean"])
        self.assertFalse(v["real_user_cache_modified"])
        self.assertFalse(v["production_operation_adapter_verified"])

    def test_runtime_race_is_not_concurrency_safe(self):
        if not tools_available():self.skipTest("native npm/uv not available")
        v=race_run()
        self.assertTrue(v["counterexample_confirmed"])
        self.assertFalse(v["real_cache_touched"])
        self.assertFalse(v["late_file_read_succeeded"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
