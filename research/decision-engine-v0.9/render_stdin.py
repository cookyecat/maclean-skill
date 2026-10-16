#!/usr/bin/env python3
"""v0.9 stdin-only report renderer. Pipe verified v1.4 triage JSON locally.
No filesystem traversal, subprocesses, deletion, or approval capability.
"""
import json,sys
from regenerability_policy import assess

def main():
    data=json.load(sys.stdin)
    result=assess(data)
    totals=result["classes"]
    print("MacLean v0.9 | 再生性优先 / 研究预览 / 无删除")
    for name in ("DEFAULT","OPTIONAL","BLOCKED"):
        value=totals[name]
        print(f"{name:8} {value['count']:2} 项 {value['allocation_mib']:10.1f} MiB")
    print("本轮粗粒度进程信号不再阻断推荐：",sum(x["coarse_activity_signal_ignored_for_eligibility"] for x in result["items"]),"项")
    print("原 v1.4 路径预览仍可能验收：",sum(x["original_v14_path_preview_eligible"] for x in result["items"]),"项")
    print("新的原生删除适配器：0；实际回收空间：未知；用户批准：否")
    by={}
    for x in result["items"]:
        if x["method_id"] is None:continue
        item=by.setdefault(x["method_id"],[0,0.0])
        item[0]+=1;item[1]+=x["size_mib"]
    print("建议操作类别（不等于已验证清理命令）：")
    for k,(count,size) in sorted(by.items(),key=lambda r:r[1][1],reverse=True):
        print(f"  {k}  {count} 项 {size:.1f} MiB")
if __name__=="__main__":main()
