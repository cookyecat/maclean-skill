#!/usr/bin/env python3
"""MacLean v0.5: privacy-minimal native read-only CLI capability probe.

No npx, npm install, curl, browser download, uninstall, cache clear or user-cache
arguments. A missing preinstalled native CLI is recorded as NOT_AVAILABLE;
there is no package-install fallback or fake E2 success.
"""
from __future__ import annotations
import importlib.util, json, os, pathlib, shutil, subprocess, sys, tempfile

def run_bounded(args: list[str], cwd: pathlib.Path, env: dict[str,str]) -> dict:
    try:
        p=subprocess.run(args,cwd=cwd,env=env,capture_output=True,text=True,timeout=12,
                         stdin=subprocess.DEVNULL)
        # Deliberately discard raw output, which could contain paths.
        return {"completed":True,"exit_code":p.returncode,
                "stdout_present":bool(p.stdout.strip()),
                "raw_output_suppressed":True,"valid":p.returncode==0}
    except subprocess.TimeoutExpired:
        return {"completed":False,"timeout":True,"valid":False}
    except OSError as e:
        return {"completed":False,"error_class":type(e).__name__,"valid":False}

def probe() -> dict:
    with tempfile.TemporaryDirectory(prefix="maclean-v05-native-probe-") as d:
        base=pathlib.Path(d).resolve()
        base.chmod(0o700)
        for name in ("home","browsers","npm-cache","puppeteer-cache"):
            (base/name).mkdir(mode=0o700)
        env={"HOME":str(base/"home"),"PATH":os.environ.get("PATH","/usr/bin:/bin"),
             "PLAYWRIGHT_BROWSERS_PATH":str(base/"browsers"),
             "PUPPETEER_CACHE_DIR":str(base/"puppeteer-cache"),
             "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD":"1",
             "PUPPETEER_SKIP_DOWNLOAD":"true",
             "npm_config_offline":"true","npm_config_ignore_scripts":"true",
             "npm_config_cache":str(base/"npm-cache"),
             "NO_PROXY":"*","HTTP_PROXY":"","HTTPS_PROXY":"",
             "UV_NO_PROGRESS":"1"}
        availability={name:bool(shutil.which(name)) for name in
                      ("uv","lsof","node","npm","npx","playwright","puppeteer")}
        availability["python_playwright_module"] = importlib.util.find_spec("playwright") is not None
        measurements={}
        # Only installed native CLI; NEVER invoke npx as that can auto-install.
        pw=shutil.which("playwright")
        if pw:
            measurements["playwright_install_list"]=run_bounded([pw,"install","--list"],base,env)
        elif availability["python_playwright_module"]:
            measurements["playwright_install_list"]=run_bounded([sys.executable,"-m","playwright","install","--list"],base,env)
        else:
            measurements["playwright_install_list"]={"status":"NOT_AVAILABLE",
                                                      "not_tested":True,"installed_version_verified":False}
        # Puppeteer main CLI is not automatically equivalent to @puppeteer/browsers;
        # a stand-alone 'puppeteer' executable is never assumed to support 'list'.
        measurements["puppeteer_browsers_list"]={
            "status":"NOT_AVAILABLE_OR_NO_VERIFIED_STANDALONE_BROWSER_CLI",
            "not_tested":True,
            "rationale":"Do not invoke npx or read real cache just to discover CLI capabilities"}
        if shutil.which("uv"):
            measurements["uv_version"]=run_bounded([shutil.which("uv"),"--version"],base,env)
            measurements["uv_cache_dir_isolated"]=run_bounded([shutil.which("uv"),"--cache-dir",
                            str(base/"home"/"uv-test-cache"),"cache","dir"],base,env)
        return {
            "schema":"maclean-native-cli-capabilities-v0.5",
            "scope":"isolated private home and browser caches",
            "installed":availability,"native_readonly_results":measurements,
            "real_user_cache_accessed":False,"npx_executed":False,
            "package_downloaded":False,"real_user_cache_cleaned":False,
            "e2_browser_native_verified":False,
            "e3_host_usage_verified":False,
            "note":"NOT_AVAILABLE is an important negative finding, never silently substitute a simulated CLI."
        }

if __name__=="__main__":
    print(json.dumps(probe(),ensure_ascii=False))
