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
    ("npm_cache",""):("npm 可再下载的软件包缓存","后续 npm 任务可能重新下载依赖；离线环境下可能无法立即恢复"),
    ("uv_cache",""):("uv 包与构建缓存","后续 uv 任务可能重新下载或编译，离线工作可能受影响"),
    ("codex_runtime_installer",""):("已过期的 Codex 运行时安装文件","可能需要重新下载安装文件；原版执行器强制至少保留最近七天的安装产物"),
    ("app_log","diagnostic"):("应用诊断日志","历史故障排查记录将消失；应用运行后可能重新产生日志"),
    ("app_update","updater_redownload"):("旧版应用更新下载包","下次应用更新可能需要重新下载更新包"),
    ("app_cache","updater_redownload"):("应用更新器缓存","下一次更新时可能需要重新下载安装包"),
    ("app_cache","editor_rebuild"):("编辑器可重建的缓存数据","重新启动时编辑器可能重建缓存或索引，短期变慢"),
}
OPTIONAL: dict[tuple[str,str],tuple[str,str]] = {
    ("npx_install",""):("npx 下载的命令运行环境","下次执行命令可能重新安装依赖，离线工具可能无法启动"),
    ("puppeteer_cache",""):("Puppeteer 浏览器下载缓存","以后可能需要重新下载较大的浏览器版本；离线自动化可能受影响"),
    ("downloaded_runtime",""):("Playwright 浏览器下载缓存","浏览器版本可能与项目绑定，恢复可能需要大量下载"),
    ("cargo_target",""):("Rust 项目构建产物","重新编译可能耗时；原版 Git 仓库安全校验必须通过"),
    ("codex_daemon_old",""):("旧版 Codex daemon","回退时可能需要重新下载；原版执行器保护当前及最新两个版本"),
    ("old_version",""):("旧版 Cursor Agent","可能减少版本回退能力；原版执行器保护最新版本"),
    ("app_cache","launcher_rebuild"):("应用启动器缓存","应用下次启动可能重建缓存，短期变慢"),
    ("app_cache","streaming_redownload"):("在线播放缓存","媒体需要重新缓存，已缓存的离线播放内容可能不可用"),
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
