#!/usr/bin/env python3
"""MacLean v0.5 E3 evidence classification (research only, fail-closed).

Sources: bounded lsof positive-reference sensor, publisher native E2 results.
This checks observation sufficiency, not truth of untrusted self-reported claims.
It never outputs an executable cleanup plan or grants approval.
"""
from __future__ import annotations
from datetime import datetime,timezone
from typing import Any

class GateError(ValueError):
    pass

RESULTS=("ABSENT","OPEN_REFERENCE_OBSERVED","NOT_OBSERVED_IN_SHALLOW_SCAN",
         "INCONCLUSIVE","DENIED")
def classify_one(kind:str, observation:dict) -> dict[str,Any]:
    if kind not in ("puppeteer","playwright") or not isinstance(observation,dict):
        raise GateError("unsupported or invalid target evidence")
    state=observation.get("state")
    if state not in RESULTS:raise GateError("unrecognized sensor output")
    # Positive observation is valuable: veto removal.
    # Negative evidence is insufficient even if lsof returned 0 or 1.
    if state=="OPEN_REFERENCE_OBSERVED":
        decision="DEFER"
        detail="Exact root/direct-child open handle observed, live-use veto"
        level="E3_POSITIVE_OPEN_REFERENCE_ONLY"
    elif state=="ABSENT":
        decision="KEEP"
        detail="No cache root exists under this exact catalog location"
        level="E0_ABSENT"
    else:
        decision="KEEP"
        detail="No reliable proof of unused and recoverable cache; fail closed"
        level="E3_INSUFFICIENT_NEGATIVE"
    return {
       "artifact":kind,"machine_status":state,
       "decision_hint":decision,"reason":detail,
       "evidence_level":level,
       "safe_to_delete_inferred":False,
       "no_future_dependency_proven":False,
       "e3_full_attestation":False,
       "native_cleanup_allowed":False,
       "user_approval_requested":False
    }

def assess_report(record:dict)->dict[str,Any]:
    if not isinstance(record,dict) or record.get("schema")!="maclean-e3-positive-observation-v0.5":
        raise GateError("unrecognized evidence schema")
    if record.get("any_real_file_modified") is not False or record.get("services_stopped") is not False:
        raise GateError("sensor was not demonstrably read-only")
    if record.get("content_read") is not False or record.get("personal_profiles_scanned") is not False:
        raise GateError("privacy boundary violated")
    if record.get("direct_leaf_child_metadata_may_be_enumerated_by_lsof") is not True:
        raise GateError("incomplete scope disclosure")
    rows=record.get("results")
    if not isinstance(rows,dict) or set(rows)!={"puppeteer","playwright"}:
        raise GateError("unexpected sensor targets")
    try:
        observed=datetime.fromisoformat(record["observation_time_utc"])
    except (ValueError,KeyError,TypeError) as e:
        raise GateError("bad sensor timestamp") from e
    if observed.tzinfo is None:raise GateError("timestamp must be timezone-aware")
    age=(datetime.now(timezone.utc)-observed).total_seconds()
    stale=(age<0 or age>60)
    evaluated={kind:classify_one(kind,val) for kind,val in rows.items()}
    if stale:
        for item in evaluated.values():
            item["decision_hint"]="KEEP"
            item["reason"]="STALE_READ_ONLY_SENSOR_RESULT"
    return {
       "research_only":True,"sensor_age_seconds":round(age,1),
       "stale":stale,"categories":evaluated,
       "all_default_cleanup_recommendations":[],
       "native_operation_authorized":False,
       "user_batch_approval_authorized":False,
       "source_authentication":"NOT_CRYPTOGRAPHICALLY_ATTESTED",
       "limitation":"No observed handle is not no dependency. Timestamp freshness alone does not prevent TOCTOU."
    }
