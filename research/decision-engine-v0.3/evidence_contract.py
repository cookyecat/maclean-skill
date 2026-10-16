#!/usr/bin/env python3
"""MacLean E1-E3 evidence contract (research-only). Never authorizes deletion.

E1 is publisher lifecycle documentation, E2 is a bounded fixture demonstration,
E3 requires current, scoped real target/workload evidence not yet implemented.
"""
from __future__ import annotations
import dataclasses
from typing import Any

PUBLISHER_CATALOG: dict[str, dict[str, Any]] = {
    "uv": {
        "url": "https://docs.astral.sh/uv/concepts/cache/",
        "claim": "Native cache prune/clean supported; direct modifications unsafe; locks protect maintenance",
        "operations": ["NATIVE_PRUNE", "NATIVE_CLEAN"],
        "important_limit": "Prune can remove centralized project environments; clean may cause re-download and rebuild",
    },
    "puppeteer": {
        "url": "https://pptr.dev/guides/installation",
        "claim": "Browser download and browser reinstall documented",
        "operations": ["BROWSER_REINSTALL", "BROWSER_CLEAR_ALL"],
        "important_limit": "Browser clear is broad; no proven exact-version usage, current-user dependency or re-download availability",
    },
    "playwright": {
        "url": "https://playwright.dev/docs/browsers",
        "claim": "Browser-client reference tracking and stale-browser garbage collection documented",
        "operations": ["MANAGED_GC"],
        "important_limit": "No proof a specific browser version is unused by this local system",
    },
}

class EvidenceError(ValueError):
    pass

@dataclasses.dataclass(frozen=True)
class Evidence:
    artifact_kind: str
    state: str
    publisher_doc_id: str | None = None
    publisher_claim_verified: bool = False
    fixture_method: str | None = None
    fixture_passed: bool = False
    fixture_isolated: bool = False
    exact_local_identity_verified: bool = False
    exact_target_use_checked: bool = False
    active_target_reference: bool | None = None
    download_recovery_verified: bool = False
    offline_dependency_excluded: bool = False
    workflow_impact_low: bool = False
    attestation_origin: str = "NONE"  # never accept AI self-attestation

    def evaluate(self) -> dict[str, Any]:
        if self.attestation_origin not in ("NONE","SYNTHETIC_TEST","INDEPENDENT_LOCAL_SENSOR"):
            raise EvidenceError("invalid attestation origin")
        if self.artifact_kind not in PUBLISHER_CATALOG:
            raise EvidenceError("unsupported artifact category")
        if self.state not in ("REVIEW", "ACTIVE", "PROTECTED", "UNKNOWN"):
            raise EvidenceError("unknown machine safety state")
        if self.fixture_passed and (not self.fixture_isolated or not self.fixture_method):
            raise EvidenceError("unisolated fixture may never be treated as evidence")
        if self.publisher_claim_verified and self.publisher_doc_id != PUBLISHER_CATALOG[self.artifact_kind]["url"]:
            raise EvidenceError("publisher evidence reference mismatch")
        if self.active_target_reference is not None and not self.exact_target_use_checked:
            raise EvidenceError("unverified exact usage signal")
        e1 = self.publisher_claim_verified and self.publisher_doc_id is not None
        e2 = e1 and self.fixture_passed and self.fixture_isolated
        e3_conditions = e2 and all((
            self.exact_local_identity_verified,
            self.exact_target_use_checked,
            self.active_target_reference is False,
            self.download_recovery_verified,
            self.offline_dependency_excluded,
            self.workflow_impact_low,
        ))
        e3 = e3_conditions and self.attestation_origin == "INDEPENDENT_LOCAL_SENSOR"
        synthetic_e3_sufficiency = e3_conditions and self.attestation_origin == "SYNTHETIC_TEST"
        veto = self.state != "REVIEW"
        missing = []
        if not e1: missing.append("PUBLISHER_LIFECYCLE_E1")
        if not e2: missing.append("BOUNDED_LOCAL_FIXTURE_E2")
        if not self.exact_local_identity_verified: missing.append("CURRENT_TARGET_IDENTITY_E3")
        if not self.exact_target_use_checked: missing.append("TARGET_REFERENCE_CHECK_E3")
        if self.active_target_reference is not False: missing.append("TARGET_NOT_IN_USE_E3")
        if not self.download_recovery_verified: missing.append("CURRENT_RECOVERY_FEASIBILITY_E3")
        if not self.offline_dependency_excluded: missing.append("OFFLINE_DEPENDENCY_E3")
        if not self.workflow_impact_low: missing.append("LOW_WORKLOAD_IMPACT_E3")
        return {
            "artifact_kind":self.artifact_kind,
            "e1_publisher":bool(e1),
            "e2_fixture":bool(e2),
            "e3_current_use_and_recovery":bool(e3),
            "synthetic_e3_counterfactual_only":bool(synthetic_e3_sufficiency),
            "machine_state_veto":veto,
            "ready_for_ai_benefit_assessment":bool(e3 and not veto),
            "missing_evidence":missing,
            "deletion_authorized":False,
            "actual_cleanup_support":False,
            "caveat":"Untrusted AI must not populate attestation fields; no production E3 sensor implemented",
        }

def from_json(item: dict) -> Evidence:
    expected={f.name for f in dataclasses.fields(Evidence)}
    if not isinstance(item,dict) or not set(item).issubset(expected):
        raise EvidenceError("invalid/extra evidence fields")
    return Evidence(**item)
