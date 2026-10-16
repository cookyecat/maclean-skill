#!/usr/bin/env python3
"""MacLean v0.9 native-method CANDIDATE preview. NOT executable.

Input: original validated Privacy Safe detailed triage via stdin.
Output: redacted aggregate; optional 0600 private JSON with exact method/paths.
It never calls the original cleanup executor, never invokes npm/uv cleanup,
never drops an activity guard or changes user approval state.
"""
from __future__ import annotations
import argparse,hashlib,json,os,pathlib,sys
from regenerability_policy import assess

def build(raw):
    result=assess(raw)
    original={r["id"]:r for r in raw["candidates"]}
    entries=[]
    identities=[]
    for value in result["items"]:
        source=original[value["id"]]
        rawpath=source.get("path")
        if not isinstance(rawpath,str) or not rawpath.startswith("~/"):
            raise ValueError("original detailed path required")
        identities.append((value["id"],value["kind"],rawpath))
        if value["selection"]=="BLOCKED":continue
        if value["method_id"] is None:raise ValueError("missing typed operation")
        entries.append({
            "candidate_id":value["id"],
            "exact_path":rawpath,"kind":value["kind"],
            "operation_id":value["method_id"],
            "suggested_selection":value["selection"],
            "gross_allocation_mib":value["size_mib"],
            "observed_coarse_process_family":value["coarse_activity_signal_ignored_for_eligibility"],
            "method_adapter_verified":False,
            "executability":"REQUIRES_SEPARATE_OPERATION_ADAPTER",
        })
    snapshot=hashlib.sha256(json.dumps(sorted(identities),ensure_ascii=False).encode()).hexdigest()
    return {
      "schema":"maclean-native-method-proposal-v0.9-research-only",
      "candidate_identity_sha256":snapshot,
      "user_approved":False,
      "not_an_executor_plan":True,
      "may_not_apply":True,
      "confirmed_reclaim_mib":None,
      "items":entries,
      "explanation":"Suggestions may be regenerable, but native concurrency/scope adapters and independent user approval are not ready."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--private-plan-path",type=pathlib.Path,required=True)
    opt=p.parse_args()
    dest=opt.private_plan_path
    if (dest.is_symlink() or not dest.parent.is_dir() or dest.parent.is_symlink()
        or dest.parent.stat().st_mode & 0o077 or dest.exists()):
        raise ValueError("new 0600 plan file inside existing private 0700 directory required")
    plan=build(json.load(sys.stdin))
    fd=os.open(dest,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,"w",encoding="utf8") as f:json.dump(plan,f,ensure_ascii=False,indent=2)
    print(json.dumps({"schema":plan["schema"],"candidate_count":len(plan["items"]),
        "default_count":sum(e["suggested_selection"]=="DEFAULT" for e in plan["items"]),
        "optional_count":sum(e["suggested_selection"]=="OPTIONAL" for e in plan["items"]),
        "user_approved":False,"not_an_executor_plan":True,
        "candidate_identity_sha256":plan["candidate_identity_sha256"]}))
if __name__=="__main__":main()
