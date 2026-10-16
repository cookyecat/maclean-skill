#!/usr/bin/env python3
"""Fixture-only native executor v1.1 regression tests."""
import json, pathlib, shutil, tempfile, unittest
from unittest.mock import patch
import native_executor as ex

class V11(unittest.TestCase):
    def setUp(self):
        self.ctx=tempfile.TemporaryDirectory(prefix="maclean-v11-test-")
        self.addCleanup(self.ctx.cleanup)
        self.home=pathlib.Path(self.ctx.name).resolve()
        self.home.chmod(0o700)
        self.cache=self.home/".npm"/"_cacache"
        self.cache.mkdir(parents=True)
        (self.cache/"sentinel").write_text("fixture only")
        self.npx=self.home/".npm"/"_npx"/"0123456789abcdef"
        self.npx.mkdir(parents=True)
        self.rows=[
            {"id":"npm1","kind":"npm_cache","path":"~/.npm/_cacache",
             "status":"ACTIVE","size_mib":20.0,
             "safety_blocks":["RELATED_PROCESS_RUNNING"]},
            {"id":"npx1","kind":"npx_install","path":"~/.npm/_npx/0123456789abcdef",
             "status":"REVIEW","size_mib":5.0,"safety_blocks":[]}
        ]
        self.plan=self.home/"draft.json"
        self.approval=self.home/"approval.json"
        def resolve(info,home):
            if info["path"] not in {self.rows[0]["path"],self.rows[1]["path"]}:
                raise ex.Denied("not fixture path")
            return home/info["path"][2:]
        def target_type(path):
            st=path.lstat()
            return (st.st_dev,st.st_ino)
        self.real_original=ex.original
        for ctx in (patch.object(ex,"original",return_value=(self.home,resolve,target_type)),
                    patch.object(ex,"fresh_triage",side_effect=lambda _:self.rows),
                    patch.object(ex.pathlib.Path,"home",return_value=self.home)):
            ctx.start()
            self.addCleanup(ctx.stop)
    def build(self):
        ex.draft(self.home,self.plan)
        return json.loads(self.plan.read_text())
    def approve(self,ids):
        value={"schema":"maclean-v1.1-exact-approval",
               "plan_sha256":ex.sha(self.plan.read_bytes()),
               "selected_ids":ids,"approved":True}
        self.approval.write_text(json.dumps(value))
        self.approval.chmod(0o600)

    def test_draft_unapproved(self):
        p=self.build()
        self.assertFalse(p["user_approved"])
        self.assertEqual(len(p["targets"]),2)
        self.assertTrue(p["targets"][1]["preview_only"])
    def test_preview_no_delete(self):
        self.build()
        x=ex.preview(self.home,self.plan,["npm1"])
        self.assertFalse(x["real_execution_performed"])
        self.assertTrue((self.cache/"sentinel").exists())
    def test_npx_preview_only(self):
        self.build()
        self.assertEqual(ex.preview(self.home,self.plan,["npx1"])["blocked_from_execution"],["npx1"])
    def test_duplicate_select_refused(self):
        self.build()
        with self.assertRaises(ex.Denied): ex.preview(self.home,self.plan,["npm1","npm1"])
    def test_inode_changed_refused(self):
        self.build()
        shutil.rmtree(self.cache)
        self.cache.mkdir()
        with self.assertRaises(ex.Denied): ex.preview(self.home,self.plan,["npm1"])
    def test_protected_on_rescan_refused(self):
        self.build()
        self.rows[0]["status"]="PROTECTED"
        self.rows[0]["safety_blocks"]=["PRIVATE_DATA"]
        with self.assertRaises(ex.Denied): ex.preview(self.home,self.plan,["npm1"])
    def test_draft_npx_flag_tamper_rejected(self):
        x=self.build()
        x["targets"][1]["preview_only"]=False
        self.plan.write_text(json.dumps(x))
        with self.assertRaises(ex.Denied): ex.parse_plan(self.plan)
    def test_missing_approval_blocks_apply(self):
        self.build()
        with self.assertRaises(ex.Denied):
            ex.apply(self.home,self.plan,["npm1"],self.approval)
        self.assertTrue(self.cache.exists())
    def test_wrong_approval_digest_blocks_apply(self):
        self.build();self.approve(["npm1"])
        x=json.loads(self.approval.read_text());x["plan_sha256"]="0"*64
        self.approval.write_text(json.dumps(x))
        with self.assertRaises(ex.Denied):
            ex.apply(self.home,self.plan,["npm1"],self.approval)
    def test_npx_apply_unconditionally_blocked(self):
        self.build();self.approve(["npx1"])
        with self.assertRaises(ex.Denied):
            ex.apply(self.home,self.plan,["npx1"],self.approval)
        self.assertTrue(self.npx.exists())
    def test_terminal_absence_blocks_apply(self):
        self.build();self.approve(["npm1"])
        with patch.object(ex.sys.stdin,"isatty",return_value=False):
            with self.assertRaises(ex.Denied):
                ex.apply(self.home,self.plan,["npm1"],self.approval)
    def test_fixture_npm_native_apply(self):
        if not shutil.which("npm"):self.skipTest("npm unavailable")
        self.build();self.approve(["npm1"])
        with patch.object(ex,"human_confirm",return_value=None):
            x=ex.apply(self.home,self.plan,["npm1"],self.approval)
        self.assertEqual(x["success_count"],1)
        self.assertFalse(self.cache.exists())
        self.assertTrue(self.npx.exists())
    def test_original_verifier_cannot_be_forged(self):
        with tempfile.TemporaryDirectory(prefix="fake-skill-") as folder:
            p=pathlib.Path(folder);(p/"scripts").mkdir()
            (p/"scripts"/"verify_bundle.py").write_text("print('ok')")
            with self.assertRaises(ex.Denied):
                self.real_original(p)

    def test_expired_draft_denied(self):
        from datetime import datetime,timezone,timedelta
        doc=self.build()
        doc["created_at_utc"]=(datetime.now(timezone.utc)-timedelta(hours=5)).isoformat()
        self.plan.write_text(json.dumps(doc))
        with self.assertRaises(ex.Denied):
            ex.preview(self.home,self.plan,["npm1"])

    def test_replaced_symlink_denied(self):
        self.build()
        shutil.rmtree(self.cache)
        self.cache.symlink_to(self.home,target_is_directory=True)
        with self.assertRaises(ex.Denied):
            ex.preview(self.home,self.plan,["npm1"])

    def test_selection_approval_mismatch_denied(self):
        self.build();self.approve(["npx1"])
        with self.assertRaises(ex.Denied):
            ex.apply(self.home,self.plan,["npm1"],self.approval)
        self.assertTrue(self.cache.exists())

    def test_denied_false_approval(self):
        self.build();self.approve(["npm1"])
        d=json.loads(self.approval.read_text());d["approved"]=False
        self.approval.write_text(json.dumps(d))
        with self.assertRaises(ex.Denied):
            ex.apply(self.home,self.plan,["npm1"],self.approval)

    def test_native_env_overrides_hostile_npm_cache(self):
        with tempfile.TemporaryDirectory(prefix="env-test-") as directory:
            context=pathlib.Path(directory).resolve();context.chmod(0o700)
            with patch.dict(ex.os.environ,{"npm_config_cache":"/tmp/hostile",
                                         "NPM_CONFIG_GLOBALCONFIG":"/tmp/hostile"}):
                environment=ex.native_env(context,"npm.cache.clean_all",self.cache)
            self.assertEqual(environment["NPM_CONFIG_CACHE"],str(self.home/".npm"))
            self.assertNotEqual(environment["NPM_CONFIG_GLOBALCONFIG"],"/tmp/hostile")
            self.assertNotEqual(environment["NPM_CONFIG_USERCONFIG"],environment["NPM_CONFIG_GLOBALCONFIG"])

    def test_unknown_target_method_refused(self):
        self.build()
        x=json.loads(self.plan.read_text())
        x["targets"][0]["operation"]="shell.rm"
        self.plan.write_text(json.dumps(x))
        with self.assertRaises(ex.Denied):ex.parse_plan(self.plan)

if __name__=="__main__": unittest.main(verbosity=2)
