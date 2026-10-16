#!/usr/bin/env python3
"""v0.8: safety, classification, batch toggle, no-apply regressions."""
from __future__ import annotations
from pathlib import Path
from unittest.mock import patch
import json,os,sys,tempfile,types,unittest
from pragmatic_policy import assess,decide,PolicyError
from preview_batch import create_preview,PreviewDenied,catalog_fingerprint

def row(id="uv_cache-001",kind="uv_cache",status="REVIEW",size=200.0,risk="",
        app=None,path="~/.cache/uv",blocks=None):
    return {"id":id,"kind":kind,"status":status,"size_mib":size,
            "rebuild_risk":risk,"app":app,"group":"home",
            "safety_blocks":blocks or [],"path":path}

def triage(rows):
    return {"scope":"known_technical_targets","policy":"privacy-safe-v1",
            "read_only":True,"user_approved":False,"ai_decision_required":True,
            "candidates":rows}

class PolicyTests(unittest.TestCase):
    def test_uv_default_when_quiet(self):
        r=decide(row())
        self.assertEqual((r["decision"],r["selection"]),("RECOMMEND","DEFAULT"))
        self.assertTrue(r["default_checked"])

    def test_npm_download_cache_default(self):
        self.assertEqual(decide(row(kind="npm_cache"))["selection"],"DEFAULT")

    def test_cursor_diagnostic_log_default(self):
        self.assertEqual(decide(row(kind="app_log",risk="diagnostic"))["selection"],"DEFAULT")

    def test_updater_exact_catalog_default(self):
        for kind in ("app_update","app_cache"):
            self.assertEqual(decide(row(kind=kind,risk="updater_redownload"))["selection"],"DEFAULT")

    def test_editor_cacheddata_default(self):
        self.assertEqual(decide(row(kind="app_cache",risk="editor_rebuild"))["selection"],"DEFAULT")

    def test_puppeteer_browser_runtime_opt_in(self):
        self.assertEqual(decide(row(kind="puppeteer_cache"))["selection"],"OPTIONAL")

    def test_streaming_cache_opt_in(self):
        self.assertEqual(decide(row(kind="app_cache",risk="streaming_redownload"))["selection"],"OPTIONAL")

    def test_old_runtime_fallback_opt_in(self):
        for kind in ("old_version","codex_daemon_old","downloaded_runtime","npx_install"):
            self.assertEqual(decide(row(kind=kind))["selection"],"OPTIONAL")

    def test_profile_never_selectable(self):
        r=decide(row(kind="profile_cache",risk="offline_collaboration_risk"))
        self.assertEqual(r["selection"],"BLOCKED")
        self.assertFalse(r["user_may_opt_in"])

    def test_offline_media_never_selectable(self):
        r=decide(row(kind="app_cache",risk="offline_media_risk"))
        self.assertEqual(r["decision"],"KEEP")

    def test_unknown_non_catalog_never_selectable(self):
        self.assertEqual(decide(row(kind="home_documents"))["selection"],"BLOCKED")

    def test_active_veto_dominates_default(self):
        r=decide(row(status="ACTIVE"))
        self.assertEqual((r["decision"],r["selection"]),("DEFER","BLOCKED"))

    def test_protected_and_unknown_hard_veto(self):
        for state in ("PROTECTED","UNKNOWN"):
            self.assertEqual(decide(row(status=state))["selection"],"BLOCKED")

    def test_safety_block_veto_even_review(self):
        self.assertEqual(decide(row(blocks=["RELATED_PROCESS_RUNNING"]))["selection"],"BLOCKED")

    def test_missing_size_cannot_default(self):
        self.assertEqual(decide(row(size=None))["selection"],"BLOCKED")

    def test_zero_size_not_recommended(self):
        self.assertEqual(decide(row(size=0))["selection"],"BLOCKED")

    def test_invalid_state_is_error(self):
        with self.assertRaises(PolicyError):decide(row(status="SAFE_TO_DELETE"))

    def test_ai_reviewed_unknown_cache_not_in_default(self):
        self.assertEqual(decide(row(kind="agent_reviewed_cache"))["selection"],"BLOCKED")

    def test_duplicate_ids_rejected(self):
        with self.assertRaises(PolicyError):assess(triage([row(),row()]))

    def test_preapproved_or_nonreadonly_report_rejected(self):
        d=triage([row()]);d["user_approved"]=True
        with self.assertRaises(PolicyError):assess(d)
        d["user_approved"]=False;d["read_only"]=False
        with self.assertRaises(PolicyError):assess(d)

    def test_class_totals_reflect_activity(self):
        r=assess(triage([row(),row(id="b",kind="puppeteer_cache"),
                         row(id="c",status="ACTIVE")]))
        self.assertEqual(r["totals"],{"DEFAULT":1,"OPTIONAL":1,"BLOCKED":1})
        self.assertEqual(r["allocation_mib_by_class"]["DEFAULT"],200.0)
        self.assertFalse(r["batch_approved"])

class PlanTests(unittest.TestCase):
    def setUp(self):
        self.ctx=tempfile.TemporaryDirectory(prefix="maclean-v08-unit-")
        self.addCleanup(self.ctx.cleanup)
        self.dir=Path(self.ctx.name);self.dir.chmod(0o700)
        self.default=row()
        self.optional=row(id="puppeteer_cache-002",kind="puppeteer_cache",
                          path="~/.cache/puppeteer",size=420.0)
        self.protected=row(id="profile_cache-003",kind="profile_cache",
                           status="PROTECTED",size=10.0,
                           risk="offline_collaboration_risk",path="~/Library/secret")
        self.rows=[self.default,self.optional,self.protected]
        self.resolve=types.ModuleType("cleanup_plan")
        self.resolve.resolve_target=lambda e,h: h/str(e["path"])[2:]
        self.resolve.running=lambda guards,target: {}
        self.privacy=types.ModuleType("privacy_policy")
        self.privacy.app_catalog_entry=lambda rel: None
        self.triage=types.ModuleType("triage_home")
        self.triage.GUARD_BY_KIND={"uv_cache":"Uv","puppeteer_cache":"Puppeteer","profile_cache":"Chrome"}
        self.mods=patch.dict(sys.modules,{"cleanup_plan":self.resolve,"privacy_policy":self.privacy,"triage_home":self.triage})
        self.mods.start()
        self.addCleanup(self.mods.stop)
        self.orig=patch("preview_batch.capture_original",return_value=(self.dir,triage(self.rows)))
        self.orig.start()
        self.addCleanup(self.orig.stop)
        self.subprocess=patch("preview_batch.subprocess.run",
            return_value=types.SimpleNamespace(returncode=0,stdout="PREVIEW ONLY; NO FILES MODIFIED."))
        self.subprocess.start()
        self.addCleanup(self.subprocess.stop)

    def runpreview(self,extra=None,excluded=None):
        return create_preview(self.dir,self.dir,extra or [],excluded or [],
                              catalog_fingerprint(triage(self.rows)))

    def test_default_plan_is_unapproved_and_exact(self):
        result=self.runpreview()
        self.assertEqual(result["selected_count"],1)
        p=json.loads((self.dir/"pending-unapproved-plan.json").read_text())
        self.assertEqual(p["schema_version"],2)
        self.assertIs(p["user_approved"],False)
        self.assertEqual(p["targets"][0]["path"],"~/.cache/uv")
        self.assertEqual(p["targets"][0]["requires_quit"],["Uv"])
        self.assertFalse(result["any_deletion_performed"])

    def test_manual_opt_in_adds_exact_optional_only(self):
        result=self.runpreview(extra=["puppeteer_cache-002"])
        self.assertEqual(result["selected_count"],2)
        p=json.loads((self.dir/"pending-unapproved-plan.json").read_text())
        self.assertEqual(len(p["targets"]),2)

    def test_uncheck_default_leaves_no_plan(self):
        result=self.runpreview(excluded=["uv_cache-001"])
        self.assertEqual(result["selected_count"],0)
        self.assertIsNone(result["pending_plan_sha256"])
        self.assertFalse((self.dir/"pending-unapproved-plan.json").exists())

    def test_cannot_opt_in_protected(self):
        with self.assertRaises(PreviewDenied):self.runpreview(extra=["profile_cache-003"])

    def test_cannot_opt_in_default_using_optional_flag(self):
        with self.assertRaises(PreviewDenied):self.runpreview(extra=["uv_cache-001"])

    def test_cannot_uncheck_optional_as_default(self):
        with self.assertRaises(PreviewDenied):self.runpreview(excluded=["puppeteer_cache-002"])

    def test_unknown_id_denied(self):
        with self.assertRaises(PreviewDenied):self.runpreview(extra=["not-a-real-id"])

    def test_duplicate_id_denied(self):
        with self.assertRaises(PreviewDenied):self.runpreview(extra=["puppeteer_cache-002"]*2)

    def test_process_becomes_active_excludes_target(self):
        self.resolve.running=lambda guards,target: {"Uv":{99}} if "uv" in str(target) else {}
        result=self.runpreview()
        self.assertEqual(result["selected_count"],0)
        self.assertEqual(result["deferred_at_second_check"],["uv_cache-001"])

    def test_optional_without_previous_catalog_identity_refused(self):
        with self.assertRaises(PreviewDenied):
            create_preview(self.dir,self.dir,["puppeteer_cache-002"],[],None)

    def test_changed_catalog_mapping_refused_even_same_id(self):
        old=catalog_fingerprint(triage(self.rows))
        self.rows[1]["path"]="~/.cache/changed-option"
        with self.assertRaises(PreviewDenied):
            create_preview(self.dir,self.dir,["puppeteer_cache-002"],[],old)

    def test_review_digest_is_present_with_default_suggestion(self):
        result=self.runpreview()
        self.assertEqual(len(result["candidate_identity_sha256"]),64)

    def test_original_executor_refusal_stops_publication(self):
        with patch("preview_batch.subprocess.run",return_value=types.SimpleNamespace(returncode=2,stdout="ERROR")):
            with self.assertRaises(PreviewDenied):self.runpreview()

    def test_preview_private_mode(self):
        self.runpreview()
        self.assertEqual((self.dir/"pending-unapproved-plan.json").stat().st_mode & 0o777,0o600)
        self.assertEqual((self.dir/"redacted-review.json").stat().st_mode & 0o777,0o600)

    def test_unsafe_output_dir_permissions_rejected(self):
        self.dir.chmod(0o755)
        with self.assertRaises(PreviewDenied):self.runpreview()

if __name__=="__main__":unittest.main(verbosity=2)
