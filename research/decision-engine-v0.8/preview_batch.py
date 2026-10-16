#!/usr/bin/env python3
"""MacLean v0.8 read-only ONE-BATCH suggestion and optional-item selector.

Loads the VERIFIED original skill, reruns ORIGINAL privacy-safe detailed triage
locally, applies only the catalog rules in pragmatic_policy, and asks the
ORIGINAL cleanup_plan.py to PREVIEW an unapproved exact-target plan.

There is intentionally NO --apply, no user_approved=True, no deletion method.
All exact paths remain private in a 0700 folder with 0600 report/plan files.
"""
from __future__ import annotations
import argparse,hashlib,importlib,json,os,pathlib,stat,subprocess,sys

from pragmatic_policy import assess,PolicyError

class PreviewDenied(ValueError):pass
def write_private(parent,name,obj):
    target=parent/name
    fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,"w",encoding="utf8") as f:
        json.dump(obj,f,ensure_ascii=False,indent=2)
        f.write("\n")
    return target

def capture_original(skill_root:pathlib.Path):
    root=skill_root.resolve(strict=True)
    scripts=root/"scripts"
    result=subprocess.run([sys.executable,str(scripts/"verify_bundle.py"),"--json"],
                          capture_output=True,text=True,timeout=25)
    if result.returncode:raise PreviewDenied("original release integrity verifier failed")
    verification=json.loads(result.stdout)
    if verification.get("ok") is not True or verification.get("version")!="1.4.0":
        raise PreviewDenied("requires exact verified v1.4.0 bundle")
    triage=subprocess.run([sys.executable,str(scripts/"triage_home.py"),"--json","--details"],
                          capture_output=True,text=True,timeout=220)
    if triage.returncode:
        raise PreviewDenied("original read-only triage returned an error")
    observed=json.loads(triage.stdout)
    if observed.get("scope")!="known_technical_targets" or observed.get("policy")!="privacy-safe-v1":
        raise PreviewDenied("unsupported scanner scope")
    # Do not print raw observations (they can contain paths and PIDs).
    return scripts,observed

def catalog_fingerprint(triage):
    """Opaque binding of candidate IDs to exact catalog kinds/paths; no paths printed."""
    identity=[]
    for x in triage.get("candidates",[]):
        if not isinstance(x.get("id"),str) or not isinstance(x.get("path"),str) or not isinstance(x.get("kind"),str):
            raise PreviewDenied("missing candidate identity field")
        identity.append([x["id"],x["kind"],x["path"]])
    identity.sort()
    raw=json.dumps(identity,separators=(",",":"),ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def create_preview(skill_root:pathlib.Path,output_dir:pathlib.Path,extra_ids:list[str],
                   excluded_defaults:list[str]|None=None,expected_catalog_sha256:str|None=None):
    # Caller-controlled private destination is itself not a cleanup target.
    if output_dir.is_symlink() or not output_dir.is_dir() or output_dir.stat().st_mode&0o077:
        raise PreviewDenied("output_dir must already exist with owner-only mode 0700")
    scripts,triage=capture_original(skill_root)
    decisions=assess(triage)
    observed_catalog_sha256=catalog_fingerprint(triage)
    # Selection IDs are ordinal, NOT stable identities. Always bind post-scan
    # user changes to exactly the previously reviewed ID->path association.
    if (extra_ids or excluded_defaults) and (not isinstance(expected_catalog_sha256,str)
         or observed_catalog_sha256!=expected_catalog_sha256):
        raise PreviewDenied("candidate identities changed or previous-review digest missing; rescan and review")
    byid={row["id"]:row for row in decisions["items"]}
    original={row["id"]:row for row in triage["candidates"]}
    excluded_defaults=excluded_defaults or []
    if len(extra_ids)!=len(set(extra_ids)) or len(excluded_defaults)!=len(set(excluded_defaults)):
        raise PreviewDenied("duplicate selection IDs")
    if any(cid not in byid or byid[cid]["selection"]!="OPTIONAL" for cid in extra_ids):
        raise PreviewDenied("only exact current OPTIONAL IDs may be manually checked")
    if any(cid not in byid or byid[cid]["selection"]!="DEFAULT" for cid in excluded_defaults):
        raise PreviewDenied("only exact current DEFAULT IDs may be unchecked")
    selected_ids=({r["id"] for r in decisions["items"] if r["selection"]=="DEFAULT"}
                  -set(excluded_defaults))|set(extra_ids)

    # Import only the independently hash-verified original executor and catalog.
    sys.path.insert(0,str(scripts))
    from cleanup_plan import resolve_target,running
    from privacy_policy import app_catalog_entry
    from triage_home import GUARD_BY_KIND

    targets=[]
    deferred_by_fresh_check=[]
    for row in decisions["items"]:
        if row["id"] not in selected_ids:continue
        source=original[row["id"]]
        path=source.get("path")
        if (not isinstance(path,str) or not path.startswith("~/")
                or source.get("status")!="REVIEW"
                or row["selection"] not in ("DEFAULT","OPTIONAL")):
            raise PreviewDenied("selected target missing exact read-only verified path")
        rel=path[2:]
        meta=app_catalog_entry(rel)
        guard=meta["guard"] if meta else GUARD_BY_KIND.get(row["kind"])
        if not guard:raise PreviewDenied("unknown activity guard")
        target={"path":path,"kind":row["kind"],
                "reason":row["reason"],"requires_quit":[guard]}
        verified_path=resolve_target(target,pathlib.Path.home())
        # Recheck process when building plan, in addition to executor apply recheck.
        if running([guard],verified_path):
            deferred_by_fresh_check.append(row["id"])
            continue
        targets.append(target)
    if len(targets)>80:raise PreviewDenied("original plan target count exceeded")
    plan=None
    preview_result=None
    if targets:
        plan={"schema_version":2,"user_approved":False,"targets":targets}
        plan_path=write_private(output_dir,"pending-unapproved-plan.json",plan)
        validated=subprocess.run([sys.executable,str(scripts/"cleanup_plan.py"),
                     "--plan",str(plan_path)],capture_output=True,text=True,timeout=120)
        # Never leak the executor raw output, which includes the exact paths.
        if validated.returncode or "PREVIEW ONLY; NO FILES MODIFIED." not in validated.stdout:
            raise PreviewDenied("original cleanup preview rejected draft plan")
        preview_result="ORIGINAL_EXECUTOR_PREVIEW_PASS"
    # Snapshot contains no private paths/PIDs; exact path list stays in local plan.
    safe_items=[dict(r) for r in decisions["items"]]
    for row in safe_items:
        if row["id"] in deferred_by_fresh_check:
            row["decision"]="DEFER"
            row["selection"]="BLOCKED"
            row["default_checked"]=False
            row["user_may_opt_in"]=False
            row["reason"]="Process became active during preflight; excluded"
    output={
       "schema":"maclean-pragmatic-batch-v0.8",
       "candidate_identity_sha256":observed_catalog_sha256,
       "privacy":"redacted display; exact paths only in local unapproved plan",
       "total_candidates":len(safe_items),
       "catalog_classes":decisions["totals"],
       "estimated_mib_by_class":decisions["allocation_mib_by_class"],
       "items":safe_items,
       "selected_ids":sorted(selected_ids-set(deferred_by_fresh_check)),
       "selected_count":len(targets),
       "selected_measured_mib":round(sum(byid[cid]["size_mib"]
                             for cid in selected_ids-set(deferred_by_fresh_check)),1),
       "deferred_at_second_check":sorted(deferred_by_fresh_check),
       "original_executor_dry_run":preview_result,
       "user_approved":False,
       "any_deletion_performed":False,
       "tip":"Recommendation is not approval. User may uncheck defaults or check optional items; create a NEW exact plan before consenting."
    }
    write_private(output_dir,"redacted-review.json",output)
    plan_sha256=hashlib.sha256((output_dir/"pending-unapproved-plan.json").read_bytes()).hexdigest() if plan else None
    # stdout includes only summary, never private IDs/pids/paths
    return {k:output[k] for k in ("total_candidates","catalog_classes",
            "estimated_mib_by_class","selected_count","selected_measured_mib",
            "deferred_at_second_check","original_executor_dry_run","user_approved","any_deletion_performed","candidate_identity_sha256")
           }|{"pending_plan_sha256":plan_sha256,
              "private_local_files":True,"no_apply_supported":True}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--skill-root",type=pathlib.Path,required=True)
    p.add_argument("--private-output-dir",type=pathlib.Path,required=True)
    p.add_argument("--include-optional",action="append",default=[],metavar="CANDIDATE_ID")
    p.add_argument("--exclude-default",action="append",default=[],metavar="CANDIDATE_ID")
    p.add_argument("--expected-catalog-sha256",default=None,metavar="HASH")
    args=p.parse_args()
    print(json.dumps(create_preview(args.skill_root,args.private_output_dir,args.include_optional,
                                    args.exclude_default,args.expected_catalog_sha256),ensure_ascii=False))
if __name__=="__main__":
    try:main()
    except (ValueError,OSError,PolicyError,subprocess.TimeoutExpired,json.JSONDecodeError) as e:
        print("REFUSED:",type(e).__name__,str(e)[:140],file=sys.stderr)
        sys.exit(2)
