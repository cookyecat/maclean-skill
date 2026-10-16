#!/usr/bin/env python3
"""MacLean native executor v1.1 (experimental, separate from original v1.4).

Preview is read-only; execution requires an EXTERNAL, explicit approval file
bound to the EXACT draft bytes, a live human TTY confirmation, and fresh
per-target validation. ChatGPT never creates an approval record.

Only npm content cache clean and uv prune may be live-executed in this version.
npx key deletion remains preview-only because native rm can break active tools.
This tool is not installed as MacLean's production executor.
"""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib, re, shutil, stat, subprocess, sys, tempfile, time
from datetime import datetime,timezone

SHA256_ORIGINAL={
    "verify_bundle.py":"6502e18edeb9b29c36e965fd3933b5a2b1b9ac9fe8b9bd56d58a99b3d68aecda",
    "cleanup_plan.py":"7aded28f2f4d002eb54a5fc8f0076148f7455c8b4f558950573f4fc4de6c89fb",
    "privacy_policy.py":"ffd6ed993ec28d3ccff0dad34636c1c0fbd7a7991e3c87871419f08ca74dc384",
    "triage_home.py":"af0ef5a5759f8147e33ae451f5b1be1fec410776ce6876c73760e3a07a8f2ccc",
}
OPERATIONS={
    "npm.cache.clean_all":("npm_cache","~/.npm/_cacache","npm"),
    "uv.cache.prune":("uv_cache","~/.cache/uv","uv"),
}
NPX_PREFIX="~/.npm/_npx/"
HEX_KEY=re.compile(r"[a-f0-9]{16}\Z")
SCHEMA="maclean-native-executor-v1.1-draft"
class Denied(ValueError):pass

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def canonical(x)->bytes:return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()
def stop(msg):raise Denied(msg)
def private_file(path:pathlib.Path, allow_missing=False):
    if path.is_symlink():stop("symlinked file")
    if not path.exists():
        if allow_missing:return
        stop("file unavailable")
    mode=path.stat().st_mode
    if not stat.S_ISREG(mode) or mode&0o077:stop("file must be ordinary owner-only (0600)")
def private_dir(path:pathlib.Path):
    if path.is_symlink() or not path.is_dir() or path.stat().st_mode & 0o077:
        stop("directory must be owner-only (0700)")
def write_private(path, data):
    private_dir(path.parent)
    if path.exists() or path.is_symlink():stop("refuse overwrite existing report or plan")
    fd=os.open(path,os.O_EXCL|os.O_CREAT|os.O_WRONLY|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,"wb") as f:
        f.write(data)
        f.flush();os.fsync(f.fileno())

def original(skill_root:pathlib.Path):
    # Verify known original program bytes BEFORE running any original script.
    root=skill_root.resolve(strict=True)
    if root.is_symlink():stop("original skill root symlink")
    scripts=root/"scripts"
    if scripts.is_symlink() or not scripts.is_dir():stop("missing scripts")
    for name,digest in SHA256_ORIGINAL.items():
        f=scripts/name
        if f.is_symlink() or not f.is_file() or sha(f.read_bytes())!=digest:
            stop("original pinned file integrity mismatch: "+name)
    v=subprocess.run([sys.executable,str(scripts/"verify_bundle.py"),"--json"],
             stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,timeout=40)
    if v.returncode:stop("original manifest integrity verifier failed")
    metadata=json.loads(v.stdout)
    if metadata.get("ok") is not True or metadata.get("version")!="1.4.0":
        stop("unsupported original Skill bundle")
    sys.path.insert(0,str(scripts))
    from cleanup_plan import resolve_target,check_target_type
    return scripts,resolve_target,check_target_type

def fresh_triage(scripts):
    v=subprocess.run([sys.executable,str(scripts/"triage_home.py"),"--json","--details"],
           stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,timeout=200)
    if v.returncode:stop("original Privacy Safe triage failed")
    data=json.loads(v.stdout)
    if (data.get("read_only") is not True or data.get("complete_within_policy") is not True
            or data.get("scope")!="known_technical_targets"
            or data.get("policy")!="privacy-safe-v1"
            or data.get("user_approved") is not False):
        stop("triage incomplete or privacy scope changed")
    rows=data.get("candidates")
    if not isinstance(rows,list) or len(rows)>500:stop("candidate list malformed")
    return rows

def allowed(row, *, preview_npx=True):
    if not isinstance(row,dict):stop("malformed candidate")
    kind,path=row.get("kind"),row.get("path")
    if not isinstance(kind,str) or not isinstance(path,str):stop("missing candidate identity")
    if kind=="npm_cache" and path=="~/.npm/_cacache":
        method="npm.cache.clean_all";selection="DEFAULT";risk="May interrupt ongoing npm downloads; packages can be fetched again"
    elif kind=="uv_cache" and path=="~/.cache/uv":
        method="uv.cache.prune";selection="DEFAULT";risk="Native prune removes unused items; reclaimed space may be small"
    elif kind=="npx_install" and path.startswith(NPX_PREFIX) and HEX_KEY.fullmatch(path[len(NPX_PREFIX):]):
        method="npm.cache.npx.rm_exact";selection="OPTIONAL";risk="Exact cached runnable may be needed by a running command"
    else:return None
    state=row.get("status");block=row.get("safety_blocks")
    if state not in ("ACTIVE","REVIEW") or not isinstance(block,list):return None
    if block and (state!="ACTIVE" or set(block)!={"RELATED_PROCESS_RUNNING"}):return None
    size=row.get("size_mib")
    if type(size) not in (int,float) or not (0<size<1e11):return None
    return {"id":row.get("id"),"path":path,"kind":kind,"operation":method,
            "tier":selection,"risk":risk,"size_mib":round(size,2),
            "status_at_draft":state,"preview_only":method=="npm.cache.npx.rm_exact"}

def check_paths(entry, resolve_target, check_target_type, home):
    kind=entry["kind"];path=entry["path"];op=entry["operation"]
    if op in OPERATIONS:
        expected_kind,expected_path,guard=OPERATIONS[op]
        if kind!=expected_kind or path!=expected_path:stop("method/target mismatch")
    elif op=="npm.cache.npx.rm_exact":
        if kind!="npx_install" or not path.startswith(NPX_PREFIX) or not HEX_KEY.fullmatch(path[len(NPX_PREFIX):]):
            stop("invalid precise npx key")
        guard="Npm"
    else:stop("unrecognized native operation")
    original_entry={"path":path,"kind":kind,"reason":"Native cache operation, rebuildable content, exact reviewed scope",
                    "requires_quit":[guard]}
    target=resolve_target(original_entry,home)
    if target.is_symlink():stop("target is symlink")
    if target.exists():check_target_type(target)
    return target

def snapshot(rows):return {r.get("id"):r for r in rows if isinstance(r,dict)}
def snapshot_id(entries):
    return sha(canonical([[e["id"],e["kind"],e["path"],e["operation"]] for e in entries]))

def draft(skill_root:pathlib.Path, dest:pathlib.Path):
    if os.geteuid()==0:stop("root not allowed")
    scripts,resolve,check_type=original(skill_root)
    rows=fresh_triage(scripts)
    choices=[]
    for row in rows:
        entry=allowed(row)
        if entry is None:continue
        if not isinstance(entry["id"],str) or not entry["id"]:stop("bad candidate id")
        check_paths(entry,resolve,check_type,pathlib.Path.home())
        choices.append(entry)
    if len({e["id"] for e in choices})!=len(choices):stop("duplicate candidate id")
    if not choices:stop("no supported native candidates")
    plan={"schema":SCHEMA,"created_at_utc":datetime.now(timezone.utc).isoformat(),
          "original_bundle_version":"1.4.0",
          "selected_identity_sha256":snapshot_id(choices),
          "user_approved":False,"targets":choices}
    write_private(dest,canonical(plan)+b"\n")
    return {"plan_sha256":sha(dest.read_bytes()),
            "candidate_count":len(choices),
            "default_count":sum(x["tier"]=="DEFAULT" for x in choices),
            "optional_count":sum(x["tier"]=="OPTIONAL" for x in choices),
            "gross_default_allocation_mib":round(sum(x["size_mib"] for x in choices if x["tier"]=="DEFAULT"),1),
            "gross_optional_allocation_mib":round(sum(x["size_mib"] for x in choices if x["tier"]=="OPTIONAL"),1),
            "native_methods":sorted({x["operation"] for x in choices}),
            "user_approved":False,"real_cache_changed":False,
            "note":"Exact one-batch choices are NOT yet approved or ready for apply"}

def parse_plan(planpath):
    private_file(planpath)
    raw=planpath.read_bytes()
    data=json.loads(raw)
    if (not isinstance(data,dict) or data.get("schema")!=SCHEMA
        or data.get("user_approved") is not False
        or set(data)!={"schema","created_at_utc","original_bundle_version",
                         "selected_identity_sha256","user_approved","targets"}
        or data["original_bundle_version"]!="1.4.0"):
        stop("invalid original unapproved native draft")
    items=data["targets"]
    if not isinstance(items,list) or not 1<=len(items)<=80 or any(not isinstance(x,dict) for x in items):
        stop("invalid native target count")
    allowed_keys={"id","path","kind","operation","tier","risk","size_mib","status_at_draft","preview_only"}
    if any(set(x)!=allowed_keys for x in items):stop("unexpected target fields")
    if data["selected_identity_sha256"]!=snapshot_id(items):
        stop("draft internal target identity mismatch")
    if len({x["id"] for x in items})!=len(items):
        stop("duplicate native target identity")
    return data,sha(raw)

def choose(plan,keys):
    by={x["id"]:x for x in plan["targets"]}
    if not isinstance(keys,list) or not keys or len(keys)>80 or len(set(keys))!=len(keys):
        stop("need 1-80 distinct selected candidate ids")
    if any(x not in by for x in keys):stop("candidate not in original approved-for-review set")
    return [by[x] for x in keys]

def compare_live(entries,rows,resolve,check_type,home):
    now=snapshot(rows)
    original_ids=[r.get("id") for r in rows]
    if len(set(original_ids))!=len(original_ids):stop("ambiguous live IDs")
    for e in entries:
        if e["id"] not in now:stop("selected candidate no longer exists")
        fresh=allowed(now[e["id"]])
        if fresh is None or fresh["path"]!=e["path"] or fresh["kind"]!=e["kind"] or fresh["operation"]!=e["operation"]:
            stop("selected target identity, risk or method changed; require new review")
        if now[e["id"]]["status"] not in ("ACTIVE","REVIEW"):stop("new safety block")
        target=check_paths(e,resolve,check_type,home)
        if not target.exists():stop("approved target became absent")
    return True

def native_env(context:pathlib.Path,op,path):
    private_dir(context)
    env={k:v for k,v in os.environ.items() if not k.casefold().startswith(("npm_config_","uv_"))}
    env["NODE_OPTIONS"]=""
    env.update({"NPM_CONFIG_USERCONFIG":str(context/"empty.npmrc"),
                "NPM_CONFIG_GLOBALCONFIG":str(context/"empty.npmrc"),
                "NPM_CONFIG_LOGS_DIR":str(context/"logs"),
                "NPM_CONFIG_IGNORE_SCRIPTS":"true","NPM_CONFIG_UPDATE_NOTIFIER":"false",
                "NPM_CONFIG_OFFLINE":"true","NPM_CONFIG_AUDIT":"false",
                "UV_NO_CONFIG":"1","UV_OFFLINE":"1"})
    if op=="npm.cache.clean_all":
        env["NPM_CONFIG_CACHE"]=str(path.parent)
    elif op=="uv.cache.prune":
        env["UV_CACHE_DIR"]=str(path)
    else:stop("real native operation not cleared for this executor")
    return env

def execute_native(op,path,context):
    if op not in ("npm.cache.clean_all","uv.cache.prune"):
        stop("this operation is preview-only pending exact-task safety validation")
    tool="npm" if op=="npm.cache.clean_all" else "uv"
    resolved=shutil.which(tool)
    if not resolved:stop("required native tool not installed")
    env=native_env(context,op,path)
    args=[resolved,"cache","clean","--force"] if tool=="npm" else [resolved,"cache","prune"]
    # No shell, no argv from untrusted plan or arbitrary path field.
    p=subprocess.run(args,env=env,cwd=context,stdin=subprocess.DEVNULL,
                     capture_output=True,text=True,timeout=180)
    if p.returncode:stop("native operation failed; stdout/stderr kept private")
    return True

def approved_file(approval:pathlib.Path,digest,selected):
    private_file(approval)
    obj=json.loads(approval.read_bytes())
    if (not isinstance(obj,dict) or set(obj)!={"schema","plan_sha256","selected_ids","approved"}
            or obj["schema"]!="maclean-v1.1-exact-approval"
            or obj["approved"] is not True or obj["plan_sha256"]!=digest
            or obj["selected_ids"]!=selected):
        stop("no exact human batch approval")
    return True

def human_confirm(digest,selected):
    if not sys.stdin.isatty():stop("physical interactive terminal required")
    print("Final batch:",len(selected),"items. Re-download and active task impact possible.")
    print("Plan SHA-256:",digest)
    print("Type DELETE "+digest[:8]+" to authorize this exact batch:",flush=True)
    if input().strip()!="DELETE "+digest[:8]:stop("terminal confirmation mismatch")

def preview(skill_root,planpath,chosen):
    plan,digest=parse_plan(planpath)
    entries=choose(plan,chosen)
    scripts,resolve,check_type=original(skill_root)
    live=fresh_triage(scripts)
    compare_live(entries,live,resolve,check_type,pathlib.Path.home())
    return {"schema":"maclean-v1.1-preview-result",
            "plan_sha256":digest,"selected_ids":chosen,
            "selected_count":len(entries),"gross_allocated_mib":round(sum(e["size_mib"] for e in entries),1),
            "blocked_from_execution":[e["id"] for e in entries if e["preview_only"]],
            "all_real_paths_validated":True,"approval_present":False,
            "real_execution_performed":False,"estimated_net_reclaim_mib":None}

def apply(skill_root,planpath,chosen,approval):
    # NEVER called for user's real cache during research/this task.
    plan,digest=parse_plan(planpath)
    entries=choose(plan,chosen)
    if any(e["preview_only"] for e in entries):
        stop("npx key deletion is preview-only: native command may break running tasks")
    approved_file(approval,digest,chosen)
    scripts,resolve,check_type=original(skill_root)
    live=fresh_triage(scripts)
    compare_live(entries,live,resolve,check_type,pathlib.Path.home())
    human_confirm(digest,chosen)
    with tempfile.TemporaryDirectory(prefix="maclean-v11-native-config-") as directory:
        context=pathlib.Path(directory).resolve();context.chmod(0o700)
        (context/"empty.npmrc").write_text("");(context/"empty.npmrc").chmod(0o600)
        (context/"logs").mkdir(mode=0o700)
        before=shutil.disk_usage(pathlib.Path.home()).free
        receipts=[]
        # Sequential per-target revalidation; stop immediately on error.
        for e in entries:
            live=fresh_triage(scripts)
            compare_live([e],live,resolve,check_type,pathlib.Path.home())
            target=check_paths(e,resolve,check_type,pathlib.Path.home())
            st=target.lstat()
            execute_native(e["operation"],target,context)
            # Persist only type and identity; no false precise reclaim claim.
            receipts.append({"id":e["id"],"method":e["operation"],"preflight_inode":st.st_ino,
                             "native_command_returned_success":True})
        after=shutil.disk_usage(pathlib.Path.home()).free
        return {"schema":"maclean-v1.1-apply-receipt","success_count":len(receipts),
                "net_apfs_free_bytes_delta":after-before,
                "warning":"APFS delta includes concurrent writes; may differ from deleted allocation"}

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--skill-root",type=pathlib.Path,required=True)
    group=cli.add_mutually_exclusive_group(required=True)
    group.add_argument("--create-draft",type=pathlib.Path)
    group.add_argument("--plan",type=pathlib.Path)
    cli.add_argument("--select",action="append",default=[])
    cli.add_argument("--apply",action="store_true")
    cli.add_argument("--approval",type=pathlib.Path)
    a=cli.parse_args()
    if a.create_draft:
        if a.apply or a.approval or a.select:stop("draft generation cannot apply or approve")
        result=draft(a.skill_root,a.create_draft)
    else:
        if not a.select:stop("select exact candidates from unapproved draft first")
        if a.apply:
            if not a.approval:stop("apply requires separate plan digest-bound approval")
            result=apply(a.skill_root,a.plan,a.select,a.approval)
        else:
            if a.approval:stop("approval cannot appear in preview mode")
            result=preview(a.skill_root,a.plan,a.select)
    print(json.dumps(result,ensure_ascii=False))
if __name__=="__main__":
    try:main()
    except (Denied,OSError,ValueError,json.JSONDecodeError,subprocess.TimeoutExpired) as e:
        print("REFUSED",type(e).__name__,str(e)[:110],file=sys.stderr)
        raise SystemExit(2)
