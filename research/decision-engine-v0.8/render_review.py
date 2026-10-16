#!/usr/bin/env python3
"""v0.8 readable review of a PRIVATE, redacted preview. NO APPLY."""
from __future__ import annotations
import argparse,json,pathlib
LABELS={"DEFAULT":"默认推荐","OPTIONAL":"可选清理","BLOCKED":"自动保留 / 暂缓"}
def render(report):
    if not isinstance(report,dict) or report.get("schema")!="maclean-pragmatic-batch-v0.8" or report.get("user_approved") is not False:
        raise ValueError("not an unapproved pragmatic MacLean preview")
    lines=["MacLean 智能清理 · 只读建议",
           "用户不用懂技术，AI 能判断得准，程序能删得安全。",
           "",
           f"候选：{report['total_candidates']} 项；默认推荐：{report['catalog_classes'].get('DEFAULT',0)} 项；"
           f"可选：{report['catalog_classes'].get('OPTIONAL',0)} 项；"
           f"自动保留：{report['catalog_classes'].get('BLOCKED',0)} 项",
           f"默认推荐估算：{report['estimated_mib_by_class'].get('DEFAULT',0):.1f} MiB；"
           f"可选项目总计：{report['estimated_mib_by_class'].get('OPTIONAL',0):.1f} MiB",
           "(以上为 du 分配空间，不是预计 APFS 净增量)",
           ""]
    for tier in ("DEFAULT","OPTIONAL","BLOCKED"):
        selected=[r for r in report["items"] if r["selection"]==tier]
        lines.append("【"+LABELS[tier]+"】")
        if not selected:lines.append("（无）")
        if tier!="BLOCKED":
            for r in selected:
                tick="[x]" if r["id"] in report["selected_ids"] else "[ ]"
                app=r.get("app") or r["kind"]
                lines.append(f"{tick} {r['id']} · {app} · {r['size_mib']:.1f} MiB")
                lines.append("    "+r["reason"])
        else:
            summary={}
            for r in selected:
                k=r["machine_status"]
                summary[k]=summary.get(k,0)+1
            lines.append("已自动排除 "+", ".join(f"{k} {v} 项" for k,v in sorted(summary.items())))
            lines.append("包含正在使用的技术组件、受保护目标及证据不足的缓存。")
        lines.append("")
    lines+=["本次当前勾选："+str(report["selected_count"])+" 项，"
             +f"{report['selected_measured_mib']:.1f} MiB",
             "状态：未批准 · 未删除 · 仍需原版执行器 dry-run 和独立人工批准。",
             "可取消默认项或勾选可选项，系统会重新审计并生成一份新的精确计划。",
             "普通用户无需理解路径；技术明细仅保存在本机受保护的计划文件中。"]
    return "\n".join(lines)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--private-review",type=pathlib.Path,required=True)
    args=p.parse_args()
    if args.private_review.is_symlink() or args.private_review.stat().st_mode&0o077:
        raise SystemExit("REFUSED: private review file must be owner-only")
    print(render(json.loads(args.private_review.read_text())))
