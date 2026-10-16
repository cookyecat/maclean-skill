#!/usr/bin/env python3
"""Disposable npx run-time interruption test; never touches real user caches."""
import json, subprocess, sys
from isolated_native_lab import fixture, add_npx, native_npx_rm

def run():
    with fixture() as root:
        key = "1234567890abcdef"
        target = add_npx(root, key)
        (target / "later.js").write_text("fixture")
        snippet = ("import pathlib,sys\n"
                   "p=pathlib.Path(sys.argv[1])\n"
                   "print('READY',flush=True)\n"
                   "sys.stdin.readline()\n"
                   "print('FOUND' if (p/'later.js').exists() else 'MISSING',flush=True)\n")
        child = subprocess.Popen([sys.executable,"-c",snippet,str(target)],
                   cwd=root,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                   stderr=subprocess.DEVNULL,text=True)
        try:
            if child.stdout.readline().strip() != "READY":
                raise RuntimeError("synthetic child not ready")
            ok = native_npx_rm(root,key)
            child.stdin.write("\n")
            child.stdin.flush()
            result = child.stdout.readline().strip()
            child.wait(timeout=5)
            return {"native_npx_rm_succeeded":ok,
                    "late_file_read_succeeded":result=="FOUND",
                    "counterexample_confirmed":ok and result=="MISSING",
                    "real_user_process_stopped":False,
                    "real_cache_touched":False}
        finally:
            if child.poll() is None:
                child.terminate()
                try:child.wait(timeout=3)
                except subprocess.TimeoutExpired:child.kill();child.wait(timeout=3)
            child.stdin.close()
            child.stdout.close()

if __name__ == "__main__":
    print(json.dumps(run()))
