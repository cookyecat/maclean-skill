#!/usr/bin/env python3
"""Create a private, minimized, read-only real MacLean triage snapshot.

No private paths/PIDs/commands/file payloads. Never mutates audited user files.
Only the vetted original triage script and manifest verifier are executed.
"""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib, subprocess, sys, tempfile
from datetime import datetime, timezone

ALLOWED = {"kind", "group", "status", "size_mib", "safety_blocks", "app", "rebuild_risk", "review_flags"}
STATUS = {"REVIEW", "ACTIVE", "PROTECTED", "UNKNOWN"}
KIND = {"npm_cache", "npx_install", "uv_cache", "puppeteer_cache", "downloaded_runtime",
"codex_runtime_installer", "codex_daemon_old", "old_version", "cargo_target",
"app_cache", "app_log", "app_update", "profile_cache", "agent_reviewed_cache"}
TRIAGE_FIELDS = {"policy", "scope", "privacy_exclusions", "excluded_actual_count",
"complete_within_policy", "read_only", "user_approved", "ai_decision_required", "note", "candidates"}
def canonical(x): return json.dumps(x, ensure_ascii=False, separators=(",",":"), sort_keys=True).encode()
def sha(x): return hashlib.sha256(canonical(x)).hexdigest()
def private_write(path, record):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,"w",encoding="utf-8") as f: json.dump(record,f,ensure_ascii=False,indent=2);f.write("\n")
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--skill-root",type=pathlib.Path,required=True)
    a.add_argument("--output-dir",type=pathlib.Path,required=True)
    opts=a.parse_args()
    root=opts.skill_root.resolve(strict=True)
    scripts=root/"scripts"
    verify=subprocess.run([sys.executable,str(scripts/"verify_bundle.py"),"--json"],text=True,capture_output=True,timeout=20)
    assert verify.returncode==0, "bundle hash verifier refused"
    verification=json.loads(verify.stdout)
    assert verification["ok"] and verification["version"]=="1.4.0"
    triage=subprocess.run([sys.executable,str(scripts/"triage_home.py"),"--json"],text=True,capture_output=True,timeout=180)
    assert triage.returncode==0, "triage script failed"
    data=json.loads(triage.stdout)
    assert set(data).issubset(TRIAGE_FIELDS), "unexpected triage output fields"
    assert data["read_only"] and data["user_approved"] is False
    candidates=[]
    for i,row in enumerate(data["candidates"],1):
        assert set(row).issubset(ALLOWED|{"id","ai_assessment","approved"}), "extra field forbidden"
        assert row["status"] in STATUS and row["kind"] in KIND
        assert "path" not in row and "matching_pids" not in row
        r={k:row[k] for k in ALLOWED if k in row}
        r["id"]=f"R{i:03d}"
        r["available_evidence_ids"]=[f"maclean-triage:{i:03d}:state", f"maclean-triage:{i:03d}:size"]
        r["evidence_quality"]="machine_status_and_allocation_only"
        r["rebuildability"]="UNVERIFIED" # never infer PROVEN from a cache label
        candidates.append(r)
    assert candidates, "no candidates"
    snapshot={"schema":"real-anon-v0.2","source":"verified_privacy_safe_triage",
              "bundle_sha256":verification["manifest_sha256"],
              "observed_at_utc":datetime.now(timezone.utc).isoformat(),
              "redaction":"no raw path, host, uid, pid, command, filename or profile ID",
              "is_ground_truth":False,
              "candidates":candidates}
    # Strict structural validation before writing or submitting to any model.
    private_dir=opts.output_dir.resolve()
    if private_dir.is_symlink():raise ValueError("output directory symlink")
    private_dir.mkdir(mode=0o700,parents=True,exist_ok=True)
    assert private_dir.stat().st_mode&0o077==0, "private dir must be 0700"
    private_write(private_dir/"snapshot.real-anon.json",snapshot)
    source_digest=sha(snapshot)
    def stat(items):
        return {"n":len(items),"mib":round(sum(x.get("size_mib") or 0 for x in items),1)}
    by_status={s:stat([x for x in candidates if x["status"]==s]) for s in sorted(STATUS)}
    print(json.dumps({"snapshot_sha256":source_digest,"candidates":len(candidates),
                      "summary_by_state":by_status,
                      "path_exposed":False,
                      "bundle_integrity":"PASS",
                      "saved_private":True},ensure_ascii=False))
if __name__=="__main__":main()
