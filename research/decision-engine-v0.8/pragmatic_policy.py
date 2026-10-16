#!/usr/bin/env python3
"""Pragmatic MacLean v0.8: risk-calibrated, CATALOG-ONLY recommendation policy.

Input is trusted read-only MacLean triage output, NOT arbitrary AI claims.
Class DEFAULT = recommended and checked; OPTIONAL = recommended but unchecked;
KEEP/DEFER = not selectable. Hard activity/privacy veto always wins.
This module neither scans files nor supplies an apply/delete operation.
"""
from __future__ import annotations
from collections import Counter
from typing import Any

AUTO: dict[tuple[str,str],tuple[str,str]] = {
    ("npm_cache",""):("npm package content cache","Packages are downloaded again when required; offline/npm tasks may be slower"),
    ("uv_cache",""):("uv package/build cache","Later uv commands may re-download or rebuild; offline work could be affected"),
    ("codex_runtime_installer",""):("stale Codex runtime installer","Installer files may be downloaded again; original executor still enforces age >= 7 days"),
    ("app_log","diagnostic"):("application diagnostic logs","Clearing logs removes older debugging history; the app may create new logs"),
    ("app_update","updater_redownload"):("old application update download","The application may need to download the updater again"),
    ("app_cache","updater_redownload"):("application updater cache","Future application updates may download packages again"),
    ("app_cache","editor_rebuild"):("editor UI/cache data","Editor may rebuild/index on restart and temporarily use more resources"),
}
OPTIONAL: dict[tuple[str,str],tuple[str,str]] = {
    ("npx_install",""):("downloaded npx execution packages","Commands may require a fresh install; offline tools may not start"),
    ("puppeteer_cache",""):("Puppeteer browser download cache","Browser revisions may need large downloads; active or offline automation may fail"),
    ("downloaded_runtime",""):("Playwright browser download cache","Browser binaries may be version-coupled; restoring may require large downloads"),
    ("cargo_target",""):("Rust compiled project output","Rebuilding can be expensive; project root must satisfy the original Git safety gate"),
    ("codex_daemon_old",""):("older Codex daemon release","Fallback may require re-download; original executor preserves current + two newest builds"),
    ("old_version",""):("older Cursor Agent build","Fallback capability may be lost; original executor preserves newest builds"),
    ("app_cache","launcher_rebuild"):("application launcher cache","Launcher may rebuild the data and start more slowly"),
    ("app_cache","streaming_redownload"):("streaming playback cache","Media will need re-download, offline playback may no longer work"),
}
PRESERVE_RISKS={
    "offline_media_risk","offline_preload_risk",
    "offline_web_apps_risk","offline_collaboration_risk",
}
VALID_STATUS={"REVIEW","ACTIVE","PROTECTED","UNKNOWN"}

class PolicyError(ValueError):
    pass

def decide(row:dict[str,Any])->dict[str,Any]:
    if not isinstance(row,dict):
        raise PolicyError("non-object triage record")
    state=row.get("status")
    if state not in VALID_STATUS:
        raise PolicyError("unrecognized safety state")
    size=row.get("size_mib")
    if type(size) not in (float,int) or size<0 or size>1e12:
        return _result(row,"KEEP","BLOCKED","Missing/invalid measured allocation; no deletion recommendation")
    kind=row.get("kind")
    risk=row.get("rebuild_risk","")
    if not isinstance(kind,str) or not isinstance(risk,str):
        raise PolicyError("kind/risk must be strings")
    if state=="ACTIVE":
        return _result(row,"DEFER","BLOCKED","Application or relevant process is active; automatically excluded")
    if state in ("PROTECTED","UNKNOWN"):
        return _result(row,"KEEP","BLOCKED","Privacy, identity, or safety state is unresolved")
    if row.get("safety_blocks"):
        return _result(row,"KEEP","BLOCKED","Machine safety veto present even though status says REVIEW")
    if kind=="profile_cache" or risk in PRESERVE_RISKS:
        return _result(row,"KEEP","BLOCKED","Offline/profile data may be irrecoverable or privacy-sensitive")
    if kind=="agent_reviewed_cache":
        return _result(row,"KEEP","BLOCKED","User-selected unknown cache requires distinct detailed assessment")
    key=(kind,risk)
    # Avoid promoting an app cache merely because another app has same type.
    rule=AUTO.get(key)
    if rule:
        # Nothing useful reclaimed from 0-sized cache; no artificial evidence barrier.
        if size<=0:
            return _result(row,"KEEP","BLOCKED","Empty candidate; no recovery value")
        return _result(row,"RECOMMEND","DEFAULT",f"{rule[0]}; {rule[1]}",impact=rule[1])
    rule=OPTIONAL.get(key)
    if rule:
        if size<=0:return _result(row,"KEEP","BLOCKED","Empty candidate; no recovery value")
        return _result(row,"RECOMMEND","OPTIONAL",f"{rule[0]}; {rule[1]}",impact=rule[1])
    return _result(row,"KEEP","BLOCKED","No vetted default/optional catalog semantics for this cache")

def _result(row,decision,selection,reason,*,impact=""):
    return {
        "id":row.get("id"),"kind":row.get("kind"),
        "group":row.get("group"),
        "app":row.get("app"),
        "machine_status":row.get("status"),
        "decision":decision,"selection":selection,
        "default_checked":selection=="DEFAULT",
        "user_may_opt_in":selection=="OPTIONAL",
        "size_mib":row.get("size_mib"),
        "reason":reason,"rebuild_impact":impact,
        "exact_target_required":selection in ("DEFAULT","OPTIONAL"),
        "plan_approved":False,
    }

def assess(report:dict)->dict:
    if not isinstance(report,dict) or report.get("read_only") is not True:
        raise PolicyError("must receive original read-only triage record")
    if report.get("user_approved") is not False or report.get("ai_decision_required") is not True:
        raise PolicyError("input is not a nonapproved triage snapshot")
    rows=report.get("candidates")
    if not isinstance(rows,list) or len(rows)>500:
        raise PolicyError("invalid or excessive candidate count")
    out=[decide(row) for row in rows]
    ids=[row["id"] for row in out]
    if any(not isinstance(x,str) or not x or len(x)>100 for x in ids) or len(ids)!=len(set(ids)):
        raise PolicyError("ambiguous candidate IDs")
    counts=Counter(r["selection"] for r in out)
    amount={key:round(sum(r["size_mib"] for r in out if r["selection"]==key and isinstance(r["size_mib"],(float,int))),1)
            for key in ("DEFAULT","OPTIONAL","BLOCKED")}
    return {"schema":"maclean-pragmatic-decision-v0.8",
            "policy":"known semantic catalog + original hard veto, no universal E3 requirement",
            "items":out,"totals":dict(counts),
            "allocation_mib_by_class":amount,"no_cleaning_performed":True,
            "batch_approved":False,
            "note":"Recommended measured allocation is NOT guaranteed APFS free-space gain"}
