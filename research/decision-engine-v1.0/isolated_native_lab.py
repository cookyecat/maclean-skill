#!/usr/bin/env python3
"""MacLean native adapter v1.0 research LAB ONLY.

Every mutating native command is limited to a NEW owner-private disposable
fixture created by this module. There is deliberately no user-controlled
cache-root argument or production --apply option. No network required.
"""
from __future__ import annotations
from contextlib import contextmanager
import argparse, io, json, os, pathlib, re, shutil, subprocess, tarfile, tempfile

NPX_KEY=re.compile(r"[a-f0-9]{16}\Z")
MARKER=".maclean-native-fixture-only"
class ScopeDenied(ValueError):pass

def guard(root:pathlib.Path):
    if not isinstance(root,pathlib.Path) or root.is_symlink() or not root.name.startswith("maclean-native-v10-"):
        raise ScopeDenied("not an authorized disposable fixture")
    resolved=root.resolve(strict=True)
    if (resolved.parent != pathlib.Path(tempfile.gettempdir()).resolve() or
        not resolved.is_dir() or resolved.stat().st_mode & 0o077):
        raise ScopeDenied("not an owner-private temporary root")
    marker=resolved/MARKER
    if marker.is_symlink() or not marker.is_file() or marker.read_text()!="synthetic-only\n":
        raise ScopeDenied("fixture marker missing")
    for name in ("home","npm-cache","uv-cache","logs","tmp"):
        child=resolved/name
        if child.is_symlink() or not child.is_dir() or child.resolve(strict=True).parent!=resolved:
            raise ScopeDenied("fixture path modified")
    return resolved

def env_for(root):
    root=guard(root)
    env=os.environ.copy()
    env.update({
        "HOME":str(root/"home"),"TMPDIR":str(root/"tmp"),
        "npm_config_cache":str(root/"npm-cache"),
        "npm_config_logs_dir":str(root/"logs"),
        "npm_config_userconfig":str(root/"user.npmrc"),
        "npm_config_globalconfig":str(root/"global.npmrc"),
        "npm_config_offline":"true","npm_config_ignore_scripts":"true",
        "npm_config_audit":"false","npm_config_fund":"false",
        "npm_config_update_notifier":"false","UV_CACHE_DIR":str(root/"uv-cache"),
        "NO_PROXY":"*","HTTP_PROXY":"","HTTPS_PROXY":"",
    })
    return env

def run_native(root,kind,argv):
    root=guard(root)
    if kind not in ("npm","uv"):raise ScopeDenied("unsupported executable")
    tool=shutil.which(kind)
    if not tool:raise ScopeDenied("native CLI missing")
    process=subprocess.run([tool,*argv],cwd=root,env=env_for(root),
                           stdin=subprocess.DEVNULL,capture_output=True,text=True,timeout=35)
    # Nothing from native stdout/stderr is printed to avoid leaking paths.
    return process

@contextmanager
def fixture():
    with tempfile.TemporaryDirectory(prefix="maclean-native-v10-") as d:
        root=pathlib.Path(d).resolve();root.chmod(0o700)
        for name in ("home","npm-cache","uv-cache","logs","tmp"):
            (root/name).mkdir(mode=0o700)
        for name in ("user.npmrc","global.npmrc"):(root/name).write_text("")
        (root/MARKER).write_text("synthetic-only\n")
        guard(root)
        yield root

def add_npx(root,key):
    root=guard(root)
    if not NPX_KEY.fullmatch(key):raise ScopeDenied("invalid exact npx key")
    base=root/"npm-cache"/"_npx"
    if base.is_symlink():raise ScopeDenied("npx root symlink")
    base.mkdir(exist_ok=True)
    target=base/key
    if target.exists() or target.is_symlink():raise ScopeDenied("key already exists")
    target.mkdir(mode=0o700)
    (target/"package.json").write_text('{"name":"maclean-fixture","version":"1.0.0"}')
    (target/"package-lock.json").write_text('{"name":"maclean-fixture","version":"1.0.0","lockfileVersion":3,"packages":{}}')
    return target

def native_npx_keys(root):
    p=run_native(root,"npm",["cache","npx","ls"])
    if p.returncode:raise ScopeDenied("npx list failed")
    lines=[x.strip() for x in p.stdout.splitlines() if x.strip()]
    parsed=set()
    for line in lines:
        m=re.fullmatch(r"([a-f0-9]{16}):\s+.*",line)
        if not m:raise ScopeDenied("unrecognized native npx list")
        if m.group(1) in parsed:raise ScopeDenied("duplicate key")
        parsed.add(m.group(1))
    return parsed

def native_npx_rm(root,key):
    root=guard(root)
    if not isinstance(key,str) or not NPX_KEY.fullmatch(key):
        raise ScopeDenied("invalid key; refusing wildcards/path separators")
    base=root/"npm-cache"/"_npx"
    if base.is_symlink():raise ScopeDenied("npx parent symlink")
    target=base/key
    if target.is_symlink() or not target.is_dir():
        raise ScopeDenied("npx target not regular directory")
    if key not in native_npx_keys(root):
        raise ScopeDenied("key not in native cache inventory")
    p=run_native(root,"npm",["cache","npx","rm",key])
    if p.returncode or target.exists() or target.is_symlink():
        raise ScopeDenied("native exact removal failed")
    return True

def make_tarball(root):
    root=guard(root)
    tar=root/"fixture-demo.tgz"
    content=b'{"name":"maclean-synthetic-only","version":"1.0.0"}'
    with tarfile.open(tar,"w:gz") as f:
        meta=tarfile.TarInfo("package/package.json")
        meta.size=len(content);f.addfile(meta,io.BytesIO(content))
    return tar

def npm_add(root):
    archive=make_tarball(root)
    p=run_native(root,"npm",["cache","add",str(archive)])
    if p.returncode:raise ScopeDenied("cannot seed disposable npm cache")
    return True

def npm_verify(root):
    # Mutating! Permitted only on disposable fixture, not original user cache.
    p=run_native(root,"npm",["cache","verify"])
    if p.returncode:raise ScopeDenied("native npm verify failed")
    return p.stdout

def npm_clean(root):
    # Native npm --force is limited to verified 0700 fixture, never real cache.
    p=run_native(root,"npm",["cache","clean","--force"])
    if p.returncode:raise ScopeDenied("native npm clean failed")
    return True

def uv_prune(root):
    p=run_native(root,"uv",["cache","prune"])
    if p.returncode:raise ScopeDenied("native uv prune failed")
    return p.stdout

def uv_clean(root):
    p=run_native(root,"uv",["cache","clean"])
    if p.returncode:raise ScopeDenied("native uv clean failed")
    return p.stdout

def lab():
    with fixture() as r:
        a,b="0123456789abcdef","fedcba9876543210"
        first=add_npx(r,a);second=add_npx(r,b)
        before=native_npx_keys(r)
        removed=native_npx_rm(r,a)
        after=native_npx_keys(r)
        npm_add(r)
        cacache=r/"npm-cache"/"_cacache"
        before_content=cacache.is_dir()
        npm_verify(r)
        after_verify=cacache.is_dir()
        npm_clean(r)
        after_clean=cacache.exists()
        npx_remains=second.is_dir() and b in native_npx_keys(r)
        uv_prune(r)
        # uv cache clean also executes only on our private fixture.
        uv_clean(r)
        return {
          "schema":"maclean-v1.0-isolated-native-results",
          "npm_version":run_native(r,"npm",["--version"]).stdout.strip(),
          "uv_version":run_native(r,"uv",["--version"]).stdout.strip(),
          "npx_initial_keys":len(before),"npx_exact_removed":removed,
          "npx_other_key_survived":b in after,
          "npm_cacache_seeded":before_content,
          "npm_cacache_after_verify":after_verify,
          "npm_cacache_after_clean":after_clean,
          "npm_npx_survived_cacache_clean":npx_remains,
          "uv_prune_exit_ok":True,"uv_clean_exit_ok":True,
          "outside_fixture_touched":False,
          "real_user_cache_modified":False,
          "production_operation_adapter_verified":False,
          "user_approved":False
        }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run-disposable-lab",action="store_true",required=True)
    p.parse_args()
    print(json.dumps(lab(),ensure_ascii=False))
