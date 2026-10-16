#!/usr/bin/env python3
"""Run *disposable sandbox only* uv maintenance + exact open-file detection.

This code has NO mode to select a user's real cache. It always creates its
own private TemporaryDirectory; refuses symlinked/unmarked cache directories.
A passed fixture demonstrates command scoping, NOT real-user rebuild safety.
"""
from __future__ import annotations
import json, os, pathlib, shutil, stat, subprocess, sys, tempfile, time

PREFIX="maclean-e2-disposable-"
MARKER=".maclean-synthetic-fixture-v0.3"

def guarded_cache(fixture_root: pathlib.Path, cache: pathlib.Path) -> pathlib.Path:
    root=fixture_root.resolve(strict=True)
    if root.is_symlink() or not root.name.startswith(PREFIX):
        raise ValueError("fixture root not freshly isolated")
    if not (root/MARKER).is_file():
        raise ValueError("missing sandbox marker")
    if (root.stat().st_mode & 0o077) != 0:
        raise ValueError("sandbox permissions not private")
    if cache.is_symlink() or cache.parent.resolve(strict=True) != root or cache.name != "uv-cache":
        raise ValueError("not exactly sandbox uv-cache")
    # resolve ensures no parent-component symlink and the target is under fixture
    resolved=cache.resolve(strict=True)
    if resolved.parent != root or not resolved.is_dir():
        raise ValueError("cache escaped fixture or is not a directory")
    return resolved

def safe_uv_run(root: pathlib.Path, cache: pathlib.Path, operation: str) -> dict:
    assert operation in ("prune","clean")
    path=guarded_cache(root,cache)
    uv=shutil.which("uv")
    if not uv:
        return {"operation":operation,"status":"NOT_INSTALLED","e2_pass":False}
    cmd=[uv,"--offline","--no-config","--cache-dir",str(path),"cache",operation]
    # --force and --ci are deliberately not supported.
    p=subprocess.run(cmd,cwd=str(root),env={
       "PATH":os.environ.get("PATH","/usr/bin:/bin"),
       "HOME":str(root),
       "UV_CACHE_DIR":str(path),
       "UV_NO_CACHE":"false",
       "UV_PYTHON_DOWNLOADS":"never",
       "UV_NO_PROGRESS":"1",
    },capture_output=True,text=True,timeout=15)
    return {"operation":operation,"status":"PASS" if p.returncode==0 else "FAILED",
            "return_code":p.returncode,"e2_pass":p.returncode==0,
            "offline_enforced":True,"only_disposable_fixture":True}

def check_fixture_handle(file: pathlib.Path) -> dict:
    """Check an exact file reference held by a *test child*, not all Mac apps."""
    if shutil.which("lsof") is None:
        return {"method":"lsof-scoped-test-child","supported":False}
    child_code=("import sys,time; f=open(sys.argv[1],'rb');"
                "sys.stdout.write('READY\\n');sys.stdout.flush();time.sleep(8)")
    child=subprocess.Popen([sys.executable,"-c",child_code,str(file)],
                            stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
    try:
        if child.stdout is None or child.stdout.readline().strip()!="READY":
            return {"method":"lsof-scoped-test-child","supported":False}
        p=subprocess.run(["lsof","-nP","-Fn","-p",str(child.pid)],
               capture_output=True,text=True,timeout=5)
        lines=p.stdout.splitlines()
        observed=str(file.resolve(strict=True)) in [row[1:] for row in lines if row.startswith("n")]
        return {"method":"lsof-scoped-test-child","supported":p.returncode==0,
                "exact_open_reference_detected":observed,
                "scope":"known synthetic child PID; no real-user process scan"}
    finally:
        child.terminate()
        try: child.wait(timeout=2)
        except subprocess.TimeoutExpired:
            child.kill();child.wait(timeout=2)
        if child.stdout:child.stdout.close()

def run() -> dict:
    with tempfile.TemporaryDirectory(prefix=PREFIX) as folder:
        root=pathlib.Path(folder)
        root.chmod(0o700)
        (root/MARKER).write_text("synthetic fixture, no real user data\n")
        outside=root/"outside-sentinel"
        outside.write_bytes(b"MACLEAN-SENTINEL-DO-NOT-TOUCH")
        cache=root/"uv-cache";cache.mkdir(mode=0o700)
        fixture_file=root/"known-open-file"
        fixture_file.write_bytes(b"synthetic and disposable")
        lsof=check_fixture_handle(fixture_file)
        # E2 native operations are permitted ONLY on fresh synthetic uv-cache.
        prune=safe_uv_run(root,cache,"prune")
        clean=safe_uv_run(root,cache,"clean")
        sentinel_ok=outside.read_bytes()==b"MACLEAN-SENTINEL-DO-NOT-TOUCH"
        assert sentinel_ok
        guard_rejects=[]
        for invalid in (root,fixture_file,root/"outside-sentinel"):
            try:
                guarded_cache(root,invalid)
            except (ValueError,FileNotFoundError):
                guard_rejects.append(True)
            else:guard_rejects.append(False)
        symlink=root/"symlink-to-user-home"
        symlink.symlink_to(pathlib.Path.home(),target_is_directory=True)
        try:
            guarded_cache(root,symlink); symlink_blocked=False
        except ValueError:symlink_blocked=True
        assert all(guard_rejects) and symlink_blocked
        return {"fixture_e2":bool(prune["e2_pass"] and clean["e2_pass"] and sentinel_ok),
                "uv_prune":prune,"uv_clean":clean,"exact_open_handle":lsof,
                "sandbox_sentinel_preserved":sentinel_ok,
                "invalid_targets_refused":len(guard_rejects),
                "symlink_to_home_refused":symlink_blocked,
                "real_cache_accessed":False,"real_cache_deleted":False,
                "does_not_prove_reinstall_or_current_use":True}

if __name__=="__main__":
    print(json.dumps(run(),ensure_ascii=False))
