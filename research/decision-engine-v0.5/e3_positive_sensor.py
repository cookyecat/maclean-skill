#!/usr/bin/env python3
"""MacLean v0.5: independent E3 *positive-reference* sensor (READ ONLY).

Only two exact technical cache leaves already allowed by MacLean's privacy
policy, or a disposable synthetic fixture. Never reads file content, enumerates
Home/Library, or returns PIDs, file names, commands, profile IDs or paths.

It can positively observe an open reference. NO observation is NOT proof a
cache is unused, even if lsof exits successfully.
"""
from __future__ import annotations
import argparse,datetime,json,os,pathlib,shutil,subprocess,sys,tempfile,time

CATALOG={
  "puppeteer":".cache/puppeteer",
  "playwright":"Library/Caches/ms-playwright",
}
ALLOWED_STATES=("ABSENT","OPEN_REFERENCE_OBSERVED","NOT_OBSERVED_IN_SHALLOW_SCAN",
                "INCONCLUSIVE","DENIED")

def path_safe(home: pathlib.Path, leaf: pathlib.Path, *, synthetic=False) -> bool:
    """Reject symlink chains and any root other than exact known leaf."""
    if home.is_symlink() or leaf.is_symlink(): return False
    if not synthetic and leaf not in [home/v for v in CATALOG.values()]:return False
    try:parts=leaf.relative_to(home).parts
    except ValueError:return False
    cur=home
    for part in parts:
        if part in (".","..","") or cur.is_symlink():return False
        cur=cur/part
        if cur.is_symlink():return False
    return True

def lsof_positive(root:pathlib.Path, *, timeout=12) -> dict:
    native=shutil.which("lsof")
    if not native:return {"state":"INCONCLUSIVE","reason":"LSOF_UNAVAILABLE"}
    try:
        # +d is only direct children, NOT +D recursive descent.
        p=subprocess.run([native,"-nP","-Fpn","+d",str(root)],
                          capture_output=True,text=True,timeout=timeout,
                          stdin=subprocess.DEVNULL)
    except (OSError,subprocess.TimeoutExpired) as e:
        return {"state":"INCONCLUSIVE","reason":type(e).__name__}
    # Parse response ONLY in memory; never emit process metadata or filenames.
    observed=0
    for line in p.stdout.splitlines():
        if not line.startswith("n"):continue
        opened=line[1:]
        if opened==str(root) or opened.startswith(str(root)+os.sep):
            observed+=1
    if observed:
        return {"state":"OPEN_REFERENCE_OBSERVED","observed_open_entries":min(observed,999),
                "reference_scope":"root_or_direct_children_only","negative_proof":False}
    # lsof may report zero exits or access limited; neither proves non-use.
    return {"state":"NOT_OBSERVED_IN_SHALLOW_SCAN" if p.returncode in (0,1) else "INCONCLUSIVE",
            "observed_open_entries":0,"reference_scope":"root_or_direct_children_only",
            "negative_proof":False,
            "permission_or_visibility_not_guaranteed":True}

def inspect_real_known_leaves() -> dict:
    home=pathlib.Path.home().absolute()
    results={}
    for category,relative in CATALOG.items():
        leaf=home/relative
        if not path_safe(home,leaf):
            results[category]={"state":"DENIED","reason":"PATH_SCOPE_OR_SYMLINK"}
        elif not leaf.exists():
            results[category]={"state":"ABSENT","reason":"NO_APPROVED_CACHE_ROOT"}
        elif not leaf.is_dir():
            results[category]={"state":"INCONCLUSIVE","reason":"NOT_DIRECTORY"}
        else:
            results[category]=lsof_positive(leaf)
    assert all(x["state"] in ALLOWED_STATES for x in results.values())
    return {
       "schema":"maclean-e3-positive-observation-v0.5",
       "observation_time_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
       "policy":"two_maclean_exact_known_technical_cache_leaves_only",
       "results":results,
       "content_read":False,"paths_enumerated":False,"personal_profiles_scanned":False,
       "any_real_file_modified":False,"services_stopped":False,
       "e3_positive_reference_only":True,"e3_complete_usage_proof":False,
       "execution_authorized":False}

def synthetic_positive_control():
    # Own process and freshly generated synthetic file; NEVER stop real service.
    with tempfile.TemporaryDirectory(prefix="maclean-v05-e3-sandbox-") as d:
        root=pathlib.Path(d).resolve()
        root.chmod(0o700)
        f=root/"fixture-open-handle"
        f.write_bytes(b"fixture-data-no-user-data")
        child=subprocess.Popen([sys.executable,"-c",
           "import sys,time;fp=open(sys.argv[1],'rb');print('READY',flush=True);time.sleep(12)",
           str(f)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
        try:
            ready=child.stdout.readline().strip() if child.stdout else ""
            if ready!="READY":return {"state":"INCONCLUSIVE","control_succeeded":False}
            found=lsof_positive(root)
            return {"state":found["state"],
                    "control_succeeded":found["state"]=="OPEN_REFERENCE_OBSERVED",
                    "only_disposable_child":True,"any_real_file_modified":False}
        finally:
            child.terminate()
            try:child.wait(timeout=3)
            except subprocess.TimeoutExpired:child.kill();child.wait(timeout=3)
            if child.stdout:child.stdout.close()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("fixture","real-known-leaves"),required=True)
    args=p.parse_args()
    x=synthetic_positive_control() if args.mode=="fixture" else inspect_real_known_leaves()
    print(json.dumps(x,ensure_ascii=False))

if __name__=="__main__":
    main()
