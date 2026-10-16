#!/usr/bin/env python3
"""Research v0.4: typed app-specific cleanup operation contracts (NO EXECUTOR).

No subprocess, no deleting, no scanning a user's machine, no apply support.
Distinguishes documented publisher operation scope from locally demonstrated
behavior and from current target-usage evidence.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
from typing import Literal

Scope = Literal["SCOPED_BUILD", "CACHE_ALL", "UNUSED_DYNAMIC", "BROWSERS_ALL",
                "CLIENT_SET", "UNVERIFIED_DYNAMIC"]

@dataclass(frozen=True)
class Operation:
    op_id: str
    application: str
    scope: Scope
    publisher_doc_url: str
    publisher_semantics: str
    local_native_fixture_verified: bool
    version: int = 1

REGISTRY: dict[str, Operation] = {
    "uv.cache.prune": Operation(
        "uv.cache.prune", "uv", "UNUSED_DYNAMIC",
        "https://docs.astral.sh/uv/concepts/cache/",
        "Prunes uv-defined unused entries; may include centralized environments",
        True),  # isolated fixture ONLY (v0.3)
    "uv.cache.clean_all": Operation(
        "uv.cache.clean_all", "uv", "CACHE_ALL",
        "https://docs.astral.sh/uv/concepts/cache/",
        "Clears ALL uv cache entries in the selected cache root",
        True),  # isolated fixture ONLY (v0.3)
    "puppeteer.browsers.uninstall_build": Operation(
        "puppeteer.browsers.uninstall_build", "puppeteer", "SCOPED_BUILD",
        "https://pptr.dev/browsers-api",
        "Publisher uninstall API accepts a selected browser/build; CLI equivalence unverified",
        False),
    "puppeteer.browsers.clear_all": Operation(
        "puppeteer.browsers.clear_all", "puppeteer", "BROWSERS_ALL",
        "https://pptr.dev/browsers-api",
        "CLI clear removes all installed browsers in its cache",
        False),
    "playwright.browsers.uninstall_client": Operation(
        "playwright.browsers.uninstall_client", "playwright", "CLIENT_SET",
        "https://playwright.dev/docs/browsers",
        "CLI uninstall removes browsers for the selected Playwright installation",
        False),
    "playwright.browsers.uninstall_all": Operation(
        "playwright.browsers.uninstall_all", "playwright", "BROWSERS_ALL",
        "https://playwright.dev/docs/browsers",
        "CLI uninstall --all removes browsers from other Playwright installations",
        False),
    "playwright.browsers.gc_unused": Operation(
        "playwright.browsers.gc_unused", "playwright", "UNVERIFIED_DYNAMIC",
        "https://playwright.dev/docs/browsers",
        "Automatic version-client reference-aware stale browser GC",
        False),
}

class ContractError(ValueError):
    pass

def safe_ident(s: str) -> bool:
    if not isinstance(s,str) or not s or len(s)>90:
        return False
    return all(c.isalnum() or c in "._-" for c in s) and s[0].isalnum()

def validate_graph(graph: dict) -> None:
    if not isinstance(graph,dict) or graph.get("schema")!="maclean-fixture-graph-v0.4":
        raise ContractError("only synthetic fixture graph schema supported")
    if graph.get("synthetic") is not True or graph.get("complete_client_universe") is not True:
        raise ContractError("synthetic graph with explicitly complete fixture client universe required")
    family=graph.get("app_family")
    if family not in ("puppeteer","playwright"):
        raise ContractError("fixture graph owner must be explicit")
    installed=graph.get("installed_browsers")
    clients=graph.get("clients")
    if not isinstance(installed,list) or not isinstance(clients,dict):
        raise ContractError("malformed graph")
    if len(installed)!=len(set(installed)) or len(installed)>100 or any(not safe_ident(s) for s in installed):
        raise ContractError("invalid installed browser identifiers")
    if len(clients)>100 or any(not safe_ident(s) for s in clients):
        raise ContractError("invalid client identifiers")
    for refs in clients.values():
        if not isinstance(refs,list) or len(refs)!=len(set(refs)):
            raise ContractError("client reference list invalid")
        if any(not safe_ident(s) for s in refs):
            raise ContractError("client dependency identity invalid")
        if any(s not in installed for s in refs):
            raise ContractError("client refers to unavailable fixture browser build")
    computed_unused=sorted(set(installed)-set().union(*(set(v) for v in clients.values())))
    if "synthetic_orphan_ids" in graph and graph["synthetic_orphan_ids"] != computed_unused:
        raise ContractError("forged synthetic orphan IDs")

def graph_fingerprint(graph: dict) -> str:
    """Deterministic synthetic graph digest; NOT an authentication signature."""
    validate_graph(graph)
    significant={k:graph[k] for k in ("schema","synthetic","complete_client_universe",
                                      "app_family","installed_browsers","clients")}
    blob=json.dumps(significant,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(blob).hexdigest()


def simulated_scope(operation: Operation, graph: dict, requested: set[str],
                    *, target: str | None = None, client: str | None = None) -> tuple[set[str] | None, list[str]]:
    """Only computes a synthetic potential effect set. None means unknowable."""
    installed=set(graph["installed_browsers"])
    refs={k:set(v) for k,v in graph["clients"].items()}
    warnings=[]
    if operation.scope == "SCOPED_BUILD":
        if not target or target not in installed:
            warnings.append("BUILD_NOT_EXACTLY_IDENTIFIED")
            return None,warnings
        return {target},warnings
    if operation.scope in ("CACHE_ALL","BROWSERS_ALL"):
        return installed,warnings
    if operation.scope == "CLIENT_SET":
        if not client or client not in refs:
            warnings.append("CLIENT_NOT_EXACTLY_IDENTIFIED")
            return None,warnings
        return refs[client],warnings
    if operation.scope == "UNUSED_DYNAMIC":
        warnings.append("NATIVE_PRUNE_SCOPE_DIFFERENT_FROM_SYNTHETIC_BROWSER_GRAPH")
        return None,warnings
    warnings.append("AUTO_GC_HAS_NO_FIXED_TARGET_SET")
    return None,warnings

def assess(operation_id: str, graph: dict, approved_targets: list[str],
           *, target: str | None = None, client: str | None = None,
           active_targets: list[str] | None = None,
           protected_targets: list[str] | None = None) -> dict:
    """Conservative research preview. NEVER returns executable plan or authorization."""
    validate_graph(graph)
    if operation_id not in REGISTRY:raise ContractError("unregistered app operation")
    op=REGISTRY[operation_id]
    if op.application != graph["app_family"]:
        raise ContractError("cross-application cleanup method not allowed for fixture graph")
    allow=set(approved_targets)
    installed=set(graph["installed_browsers"])
    if not isinstance(approved_targets,list) or not approved_targets:
        raise ContractError("nonempty approved target list required")
    if len(allow)!=len(approved_targets) or not allow.issubset(installed):
        raise ContractError("approval set invalid or not entirely installed")
    active=set(active_targets or [])
    protected=set(protected_targets or [])
    if not (active|protected).issubset(installed):
        raise ContractError("activity/protection evidence contains unknown target")
    effect,flags=simulated_scope(op,graph,allow,target=target,client=client)
    if effect is None:
        flags.append("EFFECT_SCOPE_UNPROVEN")
    else:
        if effect != allow:
            flags.append("EXACT_APPROVED_SET_MISMATCH")
        if effect & active:
            flags.append("ACTIVE_TARGET_VETO")
        if effect & protected:
            flags.append("PROTECTED_TARGET_VETO")
        still_referenced=set().union(*[set(x) for x in graph["clients"].values()]) if graph["clients"] else set()
        if effect & still_referenced:
            flags.append("SYNTHETIC_CLIENT_STILL_REFERENCES_TARGET")
    if not op.local_native_fixture_verified:
        flags.append("NATIVE_METHOD_NOT_BOUNDED_FIXTURE_VERIFIED")
    flags.append("REAL_USER_E3_ATTESTATION_MISSING")
    flags.append("NO_PRODUCTION_ADAPTER")
    # Do not turn synthetic fixture scope equality into permission.
    return {
        "operation_id":op.op_id,"publisher_documented":True,
        "graph_fingerprint":graph_fingerprint(graph),
        "requested_approved_ids":sorted(allow),
        "target_argument":target,"client_argument":client,
        "scope_semantics":op.scope,
        "synthetic_effect_size":len(effect) if effect is not None else None,
        "synthetic_effect_ids":sorted(effect) if effect is not None else None,
        "exact_scope_matches_approved":effect == allow if effect is not None else False,
        "flags":sorted(set(flags)),
        "method_scope_decidable_in_fixture":effect is not None,
        "research_only":True,"deletion_authorized":False,
        "production_eligible":False,
        "qualification":"Synthetic fixture client universe is not evidence about real host clients",
    }

def revalidate_synthetic_preview(previous: dict, current_graph: dict,
                                 *, active_targets: list[str] | None = None,
                                 protected_targets: list[str] | None = None) -> dict:
    """Re-evaluate research preview against fresh fixture graph; never apply."""
    validate_graph(current_graph)
    required=("operation_id","requested_approved_ids","graph_fingerprint",
              "target_argument","client_argument")
    if any(k not in previous for k in required) or previous.get("research_only") is not True:
        raise ContractError("untrusted or incomplete research preview")
    current=assess(previous["operation_id"],current_graph,previous["requested_approved_ids"],
                   target=previous["target_argument"],client=previous["client_argument"],
                   active_targets=active_targets,protected_targets=protected_targets)
    drift=current["graph_fingerprint"] != previous["graph_fingerprint"]
    flags=set(current["flags"])
    if drift:
        flags.add("GRAPH_CHANGED_REVIEW_REQUIRED")
    if current["synthetic_effect_ids"] != previous.get("synthetic_effect_ids"):
        flags.add("TOUCHED_SET_CHANGED_REVIEW_REQUIRED")
    current["flags"]=sorted(flags)
    current["snapshot_changed"]=drift
    current["deletion_authorized"]=False
    current["production_eligible"]=False
    return current
