#!/usr/bin/env python3
"""MacLean v0.5: reproducible NATIVE Puppeteer + Playwright read-only E2 lab.

Requires caller-installed pinned CLI packages in a fresh, 0700 temp root.
Never invokes install/uninstall/clear, npx, browser download or user's real cache.
Publishes only aggregate test facts. Fake 'installed' build intentionally lacks binary.
"""
from __future__ import annotations
import argparse,json,os,pathlib,re,shutil,stat,subprocess,sys

PINNED={"@puppeteer/browsers":"3.2.5","playwright-core":"1.64.1"}

def assert_lab_root(root:pathlib.Path):
    if root.is_symlink() or not root.name.startswith("maclean-v05-native-e2."):
        raise ValueError("not a v0.5 disposable package root")
    resolved=root.resolve(strict=True)
    if resolved.parent.as_posix() not in ("/private/tmp","/tmp") or not resolved.is_dir():
        raise ValueError("root outside exact disposable Mac temp scope")
    if resolved.stat().st_mode & 0o077:raise ValueError("temp root not mode 0700")
    for package,want in PINNED.items():
        p=resolved/"pkg/node_modules"/package/"package.json"
        if p.is_symlink() or not p.is_file() or json.loads(p.read_text())["version"]!=want:
            raise ValueError("pinned native CLI unavailable or mismatched")
    return resolved

def invoke(node,script,args,root,cache):
    env={"HOME":str(root/"home"),"PATH":os.environ.get("PATH","/usr/bin:/bin"),
         "PUPPETEER_CACHE_DIR":str(cache),"PLAYWRIGHT_BROWSERS_PATH":str(cache),
         "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD":"1","PUPPETEER_SKIP_DOWNLOAD":"true",
         "npm_config_cache":str(root/"npm-cache"),"npm_config_offline":"true",
         "npm_config_ignore_scripts":"true","NO_PROXY":"*","HTTP_PROXY":"",
         "HTTPS_PROXY":"","NODE_OPTIONS":""}
    p=subprocess.run([node,str(script),*args],cwd=root/"pkg",env=env,
       capture_output=True,text=True,timeout=20,stdin=subprocess.DEVNULL)
    return p.returncode,p.stdout,p.stderr

def lab(root:pathlib.Path)->dict:
    root=assert_lab_root(root)
    node=shutil.which("node")
    if not node:raise RuntimeError("Node unavailable")
    pp=root/"pkg/node_modules/@puppeteer/browsers/lib/main-cli.js"
    pw=root/"pkg/node_modules/playwright-core/cli.js"
    if pp.is_symlink() or pw.is_symlink() or not(pp.is_file() and pw.is_file()):
        raise ValueError("native CLI missing or symlinked")
    cache=root/"v05-browser-test-cache"
    if cache.exists():raise ValueError("refuse overwrite of existing fixture")
    cache.mkdir(mode=0o700)
    # This filename is 100% invented and may not correspond to real Chrome.
    fake=cache/"chrome"/"mac_arm-999.0.0.0"
    fake.mkdir(parents=True,mode=0o700)
    (cache/"chrome").chmod(0o700)
    try:
        pp_help=invoke(node,pp,["list","--help"],root,cache)
        pp_list=invoke(node,pp,["list","--path",str(cache)],root,cache)
        has_fictional_build=("chrome@999.0.0.0" in pp_list[1])
        # Find CLI-returned binary path in *known synthetic fixture*.
        reported_binary=None
        for line in pp_list[1].splitlines():
            prefix=str(fake)+"/"
            if "chrome@999.0.0.0" in line and prefix in line:
                relative=line.split(prefix,1)[1]
                candidate=fake/relative
                if not candidate.is_relative_to(fake):
                    raise ValueError("unexpected browser path")
                reported_binary=candidate
                break
        native_list_has_no_binary=bool(reported_binary is not None and not reported_binary.is_file())
        pw_unprepared=invoke(node,pw,["install","--list"],root,cache)
        # Playwright's official list depends on .links; we create only in the sandbox.
        (cache/".links").mkdir(mode=0o700)
        pw_prepared=invoke(node,pw,["install","--list"],root,cache)
        pw_dry=invoke(node,pw,["install","--dry-run"],root,cache)
        no_browser_binary_created=not reported_binary or not reported_binary.exists()
        return {
          "schema":"maclean-native-e2-v0.5",
          "pinned_native_packages":PINNED,
          "puppeteer_list_help_supports_path":pp_help[0]==0 and "--path" in pp_help[1],
          "puppeteer_list_rc":pp_list[0],
          "puppeteer_lists_synthetic_empty_build":has_fictional_build,
          "puppeteer_reported_executable_missing":native_list_has_no_binary,
          "playwright_list_without_links_rc":pw_unprepared[0],
          "playwright_list_with_empty_links_rc":pw_prepared[0],
          "playwright_install_dry_run_rc":pw_dry[0],
          "playwright_dry_run_only":True,
          "fixture_binary_created":not no_browser_binary_created,
          "publisher_native_list_guarantees_binary_exists":False,
          "real_user_cache_accessed":False,
          "real_user_cache_deleted":False,"npx_executed":False,
          "browser_downloaded":False,"native_cleanup_command_executed":False,
          "e3_host_recovery_proven":False,
          "finding":"Puppeteer list may index folder names even when executable is absent"
        }
    finally:
        # Temp fixture directory is intentionally left in the dedicated isolated
        # temp root for inspection; no cleanup command is invoked on any user path.
        pass

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--lab-root",required=True,type=pathlib.Path)
    a=ap.parse_args()
    print(json.dumps(lab(a.lab_root),ensure_ascii=False))
