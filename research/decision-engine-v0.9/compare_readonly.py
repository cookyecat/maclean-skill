#!/usr/bin/env python3
"""MacLean v0.9 real verified read-only audit and safe experiment comparison.

No apply, no cleanup or runtime-stop. Process family signals only affect
recommendation eligibility, NOT original v1.4 executor deletion permission.
"""
from __future__ import annotations
import argparse,hashlib,json,os,pathlib,subprocess,sys
from regenerability_policy import assess,Refused

class TrialDenied(ValueError):pass

def run_readonly_verified(root):
    scripts=root.resolve(strict=True)/"scripts"
    v=subprocess.run([sys.executable,str(scripts/"verify_bundle.py"),"--json"],
                     capture_output=True,text=True,timeout=35)
    if v.returncode:raise TrialDenied("original bundle verification failed")
    evidence=json.loads(v.stdout)
    if evidence.get("ok") is not True or evidence.get("version")!="1.4.0":
        raise TrialDenied("requires exact verified v1.4.0")
    p=subprocess.run([sys.executable,str(scripts/"triage_home.py"),"--json","--details"],
                     capture_output=True,text=True,timeout=180)
    if p.returncode:raise TrialDenied("Privacy Safe triage failed")
    data=json.loads(p.stdout)
    if not data.get("complete_within_policy") or data.get("scope")!="known_technical_targets":
        raise TrialDenied("incomplete or expanded audit scope")
    return data

def private_write(root,name,data):
    f=root/name
    fd=os.open(f,os.O_EXCL|os.O_CREAT|os.O_WRONLY|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,"w") as file:json.dump(data,file,ensure_ascii=False,indent=2)

def evaluate(skill_root,output_dir):
    if output_dir.is_symlink() or not output_dir.is_dir() or output_dir.stat().st_mode & 0o077:
        raise TrialDenied("requires owner-only existing output directory")
    data=run_readonly_verified(skill_root)
    val=assess(data)
    considered=[x for x in val["items"] if x["selection"] in ("DEFAULT","OPTIONAL")]
    coarse=[x for x in considered if x["coarse_activity_signal_ignored_for_eligibility"]]
    old=[x for x in considered if x["original_v14_path_preview_eligible"]]
    methods={}
    for x in considered:
        d=methods.setdefault(x["method_id"],{"count":0,"candidate_allocation_mib":0})
        d["count"]+=1;d["candidate_allocation_mib"]+=x["size_mib"]
    for v in methods.values():v["candidate_allocation_mib"]=round(v["candidate_allocation_mib"],1)
    identities=sorted((c["id"],c["kind"],c["path"]) for c in data["candidates"])
    identity=hashlib.sha256(json.dumps(identities,sort_keys=True).encode()).hexdigest()
    receipt={
      "schema":"maclean-v09-compare-redacted","total_candidates":len(val["items"]),
      "candidate_identity_sha256":identity,"classes":val["classes"],
      "method_suggestions":methods,
      "ignored_coarse_activity_candidates":len(coarse),
      "ignored_coarse_activity_allocation_mib":round(sum(x["size_mib"] for x in coarse),1),
      "original_guarded_preview_eligible_count":len(old),
      "original_guarded_preview_eligible_mib":round(sum(x["size_mib"] for x in old),1),
      "items":val["items"],"new_native_adapters_implemented":0,
      "actual_reclaim_mib":None,"user_approved":False,"cleanup_performed":False,
      "no_executable_plan_for_coarse_active":True,
      "warning":"Recommendations are not executable operations. No new native adapter or process-bypass plan."}
    private_write(output_dir,"redacted-v09-comparison.json",receipt)
    return {k:v for k,v in receipt.items() if k!="items"}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--skill-root",required=True,type=pathlib.Path)
    p.add_argument("--output-dir",required=True,type=pathlib.Path)
    a=p.parse_args()
    try:print(json.dumps(evaluate(a.skill_root,a.output_dir),ensure_ascii=False))
    except (TrialDenied,Refused,ValueError,OSError,subprocess.TimeoutExpired,json.JSONDecodeError) as e:
        print("REFUSED",type(e).__name__,str(e)[:120],file=sys.stderr);sys.exit(2)
