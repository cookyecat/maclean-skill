#!/usr/bin/env python3
"""MacLean v1.0 typed *plan validation*, not an executor.

Accept only exact known npm/uv cache identities from prior v0.9 research.
Returns a non-executable method record. It does not read real filesystem paths,
invoke npm/uv, modify v1.4 executor or grant approval.
"""
from __future__ import annotations
import re

KIND_METHOD={
    "npm_cache":"npm.cache.clean_all",
    "npx_install":"npm.cache.npx.rm_exact",
    "uv_cache":"uv.cache.prune",
}
HEX16=re.compile(r"[a-f0-9]{16}\Z")

class ContractDenied(ValueError):pass

def compile_method(item):
    if not isinstance(item,dict):raise ContractDenied("candidate must be object")
    kind=item.get("kind")
    if kind not in KIND_METHOD:raise ContractDenied("not a supported native-cache class")
    method=item.get("operation_id")
    if method!=KIND_METHOD[kind]:
        raise ContractDenied("method/kind mismatch")
    path=item.get("exact_path")
    if not isinstance(path,str):raise ContractDenied("missing exact identity")
    if kind=="npm_cache":
        if path!="~/.npm/_cacache":raise ContractDenied("npm parent/alternate cache outside contract")
        scope="NPM_CONTENT_ONLY"
    elif kind=="uv_cache":
        if path!="~/.cache/uv":raise ContractDenied("uv cache root outside contract")
        scope="UV_PRUNE_UNUSED_ONLY"
    else:
        prefix="~/.npm/_npx/"
        if not path.startswith(prefix) or not HEX16.fullmatch(path[len(prefix):]):
            raise ContractDenied("not one exact npx cache key")
        scope="ONE_NPX_KEY"
    if item.get("suggested_selection") not in ("DEFAULT","OPTIONAL"):
        raise ContractDenied("not an eligible selection")
    if item.get("method_adapter_verified") is not False or item.get("executability")!="REQUIRES_SEPARATE_OPERATION_ADAPTER":
        raise ContractDenied("refuse records that self-claim native method readiness")
    return {
      "schema":"maclean-v1.0-native-method-contract-research",
      "kind":kind,"method":method,"scope":scope,
      "exact_relative_identity":path,
      "estimated_physical_reclaim_mib":None,
      "sandbox_native_semantics_tested":True,
      "concurrent_active_npx_key_safe":False,
      "production_method_approved":False,
      "user_approved":False,
      "executable":False,
    }
