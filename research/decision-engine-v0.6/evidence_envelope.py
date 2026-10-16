#!/usr/bin/env python3
"""MacLean v0.6 independent evidence-envelope prototype (NO EXECUTION).

HMAC protects research records from accidental/unauthorized modification and
enables freshness/replay checks only if a separate trusted process holds the
secret. It does NOT prove that an LLM-supplied claim is true or authorize deletion.
Pure stdlib, no real file scanner and no native mutation.
"""
from __future__ import annotations
import datetime as dt
import hashlib, hmac, json, re
from typing import Any

SOURCES=frozenset({"synthetic.playwright-native","synthetic.puppeteer-native",
                   "synthetic.open-reference","real.catalog-leaf-open-reference"})
BINARY=frozenset({"NOT_CHECKED","NOT_PRESENT","NONEXECUTABLE","SYMLINK_DENIED","EXEC_MODE_ONLY"})
CLIENTS=frozenset({"UNKNOWN","PARTIAL_SYNTHETIC","PARTIAL_REAL"})
ACTIVITY=frozenset({"POSITIVE_OPEN_REFERENCE","NOT_OBSERVED_SHALLOW","UNKNOWN"})
FIELDS=frozenset({"schema","source","subject","issued_at","nonce","body"})
BODY_FIELDS=frozenset({"binary","clients","activity","coverage_complete","publisher_listed","observed_in_real_cache"})

class InvalidEvidence(ValueError):
    pass

def canonical(doc:dict)->bytes:
    return json.dumps(doc,sort_keys=True,ensure_ascii=False,
                      separators=(",",":"),allow_nan=False).encode("utf8")

def validate_payload(body:dict, source:str, subject:str)->None:
    if source not in SOURCES:raise InvalidEvidence("unexpected evidence source")
    if not re.fullmatch(r"[A-Z0-9]{8,20}",subject):
        raise InvalidEvidence("subject must be opaque identifier")
    if not isinstance(body,dict) or set(body)!=BODY_FIELDS:
        raise InvalidEvidence("invalid evidence schema")
    if body["binary"] not in BINARY or body["clients"] not in CLIENTS or body["activity"] not in ACTIVITY:
        raise InvalidEvidence("unrecognized evidence type")
    if type(body["coverage_complete"]) is not bool or type(body["publisher_listed"]) is not bool or type(body["observed_in_real_cache"]) is not bool:
        raise InvalidEvidence("boolean fields invalid")
    if body["coverage_complete"]:
        raise InvalidEvidence("no complete actual client universe is implemented")
    if source.startswith("synthetic.") and body["observed_in_real_cache"]:
        raise InvalidEvidence("synthetic cannot claim real cache observation")
    if source=="real.catalog-leaf-open-reference" and body["binary"]!="NOT_CHECKED":
        raise InvalidEvidence("shallow sensor cannot attest binary integrity")

def seal(*, key:bytes, source:str, subject:str, body:dict, issued_at:dt.datetime,
         nonce:str)->dict:
    if not isinstance(key,bytes) or len(key)<32:
        raise InvalidEvidence("research HMAC secret requires 256 bits")
    if issued_at.tzinfo is None:raise InvalidEvidence("timestamp without timezone")
    if not re.fullmatch("[0-9a-f]{32}",nonce):
        raise InvalidEvidence("invalid 128-bit nonce")
    validate_payload(body,source,subject)
    obj={"schema":"maclean-research-envelope-v0.6","source":source,
         "subject":subject,"issued_at":issued_at.astimezone(dt.timezone.utc).isoformat(),
         "nonce":nonce,"body":body}
    tag=hmac.new(key,canonical(obj),hashlib.sha256).hexdigest()
    return {"payload":obj,"hmac_sha256":tag}

def verify(envelope:dict,*,key:bytes,expected_source:str,expected_subject:str,
           now:dt.datetime,used_nonces:set[str]|None=None,max_age_seconds:int=30)->dict:
    if not isinstance(envelope,dict) or set(envelope)!={"payload","hmac_sha256"}:
        raise InvalidEvidence("unrecognized sealed record")
    obj=envelope["payload"]
    if not isinstance(obj,dict) or set(obj)!=FIELDS or obj.get("schema")!="maclean-research-envelope-v0.6":
        raise InvalidEvidence("invalid evidence envelope")
    if obj["source"]!=expected_source or obj["subject"]!=expected_subject:
        raise InvalidEvidence("unexpected evidence origin or subject")
    validate_payload(obj["body"],obj["source"],obj["subject"])
    try: got=bytes.fromhex(envelope["hmac_sha256"])
    except (TypeError,ValueError):raise InvalidEvidence("invalid integrity tag") from None
    if len(got)!=32 or len(key)<32:
        raise InvalidEvidence("invalid integrity parameters")
    expected=hmac.new(key,canonical(obj),hashlib.sha256).digest()
    if not hmac.compare_digest(got,expected):
        raise InvalidEvidence("evidence changed after signing")
    try:issued=dt.datetime.fromisoformat(obj["issued_at"])
    except (ValueError,TypeError):raise InvalidEvidence("invalid issuance timestamp") from None
    if issued.tzinfo is None or now.tzinfo is None:
        raise InvalidEvidence("timezone missing")
    age=(now.astimezone(dt.timezone.utc)-issued.astimezone(dt.timezone.utc)).total_seconds()
    if age<0 or age>max_age_seconds:
        raise InvalidEvidence("stale or future evidence")
    if used_nonces is not None:
        if obj["nonce"] in used_nonces:raise InvalidEvidence("replayed evidence")
        used_nonces.add(obj["nonce"])
    body=obj["body"]
    # Strictly asymmetric; only positive observed open references are actionable vetoes.
    hint="DEFER" if body["activity"]=="POSITIVE_OPEN_REFERENCE" else "KEEP"
    return {
        "integrity_check":"PASS","fresh_within_seconds":max_age_seconds,
        "source_identity_is_cryptographically_authenticated":False,
        "real_host_client_coverage_complete":False,
        "source":obj["source"],"opaque_subject":obj["subject"],
        "decision_hint":hint,"e3_fully_proven":False,
        "recommended_for_cleanup":False,"executable_plan":False,
        "deletion_authorized":False,
        "limitation":"Research HMAC demonstrates sealed transport only, not trustworthy source capture or no-use proof",
    }

def fixture_example()->dict[str,Any]:
    import os
    key=os.urandom(32)
    now=dt.datetime.now(dt.timezone.utc)
    body={"binary":"EXEC_MODE_ONLY","clients":"PARTIAL_SYNTHETIC",
          "activity":"NOT_OBSERVED_SHALLOW","coverage_complete":False,
          "publisher_listed":True,"observed_in_real_cache":False}
    evidence=seal(key=key,source="synthetic.playwright-native",
                  subject="ABCD1234",body=body,issued_at=now,nonce=os.urandom(16).hex())
    return verify(evidence,key=key,expected_source="synthetic.playwright-native",
                  expected_subject="ABCD1234",now=now)

if __name__=="__main__":
    print(json.dumps(fixture_example(),ensure_ascii=False))
