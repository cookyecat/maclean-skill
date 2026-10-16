#!/usr/bin/env python3
"""MacLean v0.9 — regenerability-first, operation-aware RESEARCH classifier.

A coarse RELATED_PROCESS_RUNNING status is not a global veto for vetted,
regenerable caches. It is NOT a deletion permission: every non-legacy
operation remains non-executable pending a separately tested adapter.
Unknown, path protection, privacy and offline data ALWAYS stay blocked.
"""
from __future__ import annotations
from collections import Counter
import math

# Operation registry is a declarative proposal, NEVER an executable command.
# method_id is deliberately *not* passed to the v1.4.0 path-delete executor.
ROUTES = {
    ("npm_cache", ""): ("DEFAULT", "npm.cache.clean_all",
        "npm 包下载缓存", "完整清空可重新下载，但可能影响离线 npm 操作；需要隔离验证原生清理并发安全"),
    ("uv_cache", ""): ("DEFAULT", "uv.cache.prune",
        "uv 包缓存维护", "只回收 uv 定义的无用条目，不能将整个缓存体积算作预计收益"),
    ("npx_install", ""): ("OPTIONAL", "npm.cache.npx.rm_exact",
        "npx 下载的工具环境", "运行环境可以重装，但可能影响当前命令；必须验证原生 key 与精确目录对应关系"),
    ("codex_runtime_installer", ""): ("DEFAULT", "installer.delete_scoped",
        "旧版 Codex 安装包", "可重新下载；保留原版七天年龄保护，删除前需识别是否仍被安装任务使用"),
    ("codex_daemon_old", ""): ("OPTIONAL", "runtime.remove_version",
        "旧版 Codex daemon", "属于运行组件；必须保留当前与回退版本，不能直接按普通缓存清理"),
    ("old_version", ""): ("OPTIONAL", "runtime.remove_version",
        "旧版 Cursor Agent", "属于运行组件；必须保留实际使用版本和最新回退版本"),
    ("puppeteer_cache", ""): ("OPTIONAL", "puppeteer.browsers.uninstall_build",
        "Puppeteer 浏览器下载缓存", "重新下载量较大，离线自动化可能受影响；全量 clear 不能替代单版本操作"),
    ("downloaded_runtime", ""): ("OPTIONAL", "playwright.browsers.gc_unused",
        "Playwright 浏览器下载缓存", "版本与客户端关联；未经验证不得直接清空浏览器目录"),
    ("app_cache", "editor_rebuild"): ("DEFAULT", "cache.exact_leaf",
        "编辑器可再生缓存", "可能需要重新建立索引；应用正在运行不等于该缓存不能清理"),
    ("app_log", "diagnostic"): ("DEFAULT", "log.exact_leaf",
        "诊断日志", "历史排障记录可能消失；活跃写入时需使用安全的日志轮转方式"),
    ("app_cache", "updater_redownload"): ("DEFAULT", "cache.exact_leaf",
        "应用更新缓存", "以后更新时可能重新下载"),
    ("app_update", "updater_redownload"): ("DEFAULT", "cache.exact_leaf",
        "旧版更新下载包", "以后更新时可能重新下载"),
    ("app_cache", "launcher_rebuild"): ("OPTIONAL", "cache.exact_leaf",
        "应用启动器缓存", "下次启动可能重建"),
    ("app_cache", "streaming_redownload"): ("OPTIONAL", "cache.exact_leaf",
        "在线播放缓存", "离线播放可能丢失，重新联网缓存"),
}
PROTECTED_RISKS = frozenset({
    "offline_media_risk","offline_preload_risk",
    "offline_web_apps_risk","offline_collaboration_risk"
})
SAFETY_STATES=frozenset({"REVIEW","ACTIVE","PROTECTED","UNKNOWN"})
# The only legacy ACTIVE block that policy may *reinterpret for recommendation*.
COARSE_SIGNAL="RELATED_PROCESS_RUNNING"

class Refused(ValueError):pass

def classify(row):
    if not isinstance(row,dict):raise Refused("invalid candidate record")
    status=row.get("status");kind=row.get("kind");risk=row.get("rebuild_risk") or ""
    size=row.get("size_mib");blocks=row.get("safety_blocks")
    if status not in SAFETY_STATES or not isinstance(kind,str) or not isinstance(risk,str):
        raise Refused("unsupported candidate identity/status")
    if not isinstance(blocks,list) or any(not isinstance(x,str) for x in blocks):
        raise Refused("untrusted machine blocks")
    if type(size) not in (float,int) or not math.isfinite(size) or size<0:
        return outcome(row,"KEEP","BLOCKED",None,"SIZE_NOT_VERIFIED")
    if status in ("PROTECTED","UNKNOWN") or any(x!=COARSE_SIGNAL for x in blocks):
        return outcome(row,"KEEP","BLOCKED",None,"MACHINE_OR_PRIVACY_HARD_VETO")
    if kind=="profile_cache" or risk in PROTECTED_RISKS or kind=="agent_reviewed_cache":
        return outcome(row,"KEEP","BLOCKED",None,"USER_OR_OFFLINE_DATA_PROTECTION")
    if size<=0:return outcome(row,"KEEP","BLOCKED",None,"EMPTY")
    route=ROUTES.get((kind,risk))
    if not route:return outcome(row,"KEEP","BLOCKED",None,"NOT_IN_REVIEWED_CATALOG")
    tier,operation,label,impact=route
    if status=="ACTIVE" and (not blocks or set(blocks)!={COARSE_SIGNAL}):
        return outcome(row,"KEEP","BLOCKED",None,"UNEXPECTED_ACTIVE_EVIDENCE")
    # Key simplification: a process-family match does not suppress eligibility.
    # But the action remains an unapproved *proposal*.
    eligible_original=(status=="REVIEW" and not blocks)
    return outcome(row,"RECOMMEND",tier,operation,"REGENERABLE_CATALOG_MATCH",
                   label=label,impact=impact,coarse_active=status=="ACTIVE",
                   legacy_preview_eligible=eligible_original)

def outcome(row,decision,tier,method,reason,*,label="",impact="",coarse_active=False,
            legacy_preview_eligible=False):
    return {
        "id":row.get("id"),"kind":row.get("kind"),"app":row.get("app"),
        "machine_status":row.get("status"),"size_mib":row.get("size_mib"),
        "decision":decision,"selection":tier,"method_id":method,
        "label":label,"rebuild_impact":impact,"reason_code":reason,
        "coarse_activity_signal_ignored_for_eligibility":coarse_active,
        "original_v14_path_preview_eligible":legacy_preview_eligible,
        # A recommended cache cannot turn into a new executable plan by
        # calling old v1.4 cleanup_plan with requires_quit=[].
        "operation_adapter_verified":False,
        "execution_ready":False,"user_approved":False,
    }

def assess(report):
    if (not isinstance(report,dict) or report.get("read_only") is not True
            or report.get("user_approved") is not False
            or report.get("ai_decision_required") is not True
            or report.get("scope")!="known_technical_targets"
            or report.get("policy")!="privacy-safe-v1"):
        raise Refused("not an authenticated-format original Privacy Safe triage")
    rows=report.get("candidates")
    if not isinstance(rows,list) or len(rows)>500:raise Refused("candidate count invalid")
    classifications=[classify(r) for r in rows]
    ids=[v["id"] for v in classifications]
    if any(not isinstance(x,str) or not x for x in ids) or len(ids)!=len(set(ids)):
        raise Refused("ambiguous candidate ID mapping")
    totals={t:{"count":sum(x["selection"]==t for x in classifications),
               "allocation_mib":round(sum(x["size_mib"] for x in classifications
                 if x["selection"]==t and isinstance(x["size_mib"],(float,int))),1)}
            for t in ("DEFAULT","OPTIONAL","BLOCKED")}
    gross=sum(x["size_mib"] for x in classifications if x["selection"] in ("DEFAULT","OPTIONAL"))
    return {"schema":"maclean-regenerability-v0.9","items":classifications,
            "classes":totals,"reclaimable_allocation_upper_candidate_mib":round(gross,1),
            "verified_reclaim_mib":None,
            "verified_executable_operation_count":0,
            "user_approved":False,"any_real_deletion":False,
            "note":"Candidate allocation is NOT reclaim estimate. Native ops and concurrent use not acceptance-tested."}
