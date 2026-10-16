#!/usr/bin/env python3
"""v0.7 experimental executor-owned sensor, NOT a production attestation.

The issuer signs only fresh results from its own fixture reader, never an
arbitrary LLM-authored dictionary. Re-verification rescans a permitted fixture
and rejects stale evidence or changed references. Same-user ephemeral HMAC is
NOT a production trust boundary against local adversaries.
"""
from __future__ import annotations
from datetime import datetime,timezone
import hashlib,hmac,json,re,secrets
from project_witness import scan

class AttestationRejected(ValueError):pass
def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(x):return hashlib.sha256(canonical(x)).hexdigest()
def plan_id_valid(x):return isinstance(x,str) and bool(re.fullmatch("[a-f0-9]{64}",x))
def time_now():return datetime.now(timezone.utc)
def _stamp(key,body):
    return hmac.new(key,canonical(body),hashlib.sha256).hexdigest()

class FixtureWitnessIssuer:
    """Caller owns secret and nonce set. No arbitrary-observation signing API."""
    def __init__(self):
        self.__key=secrets.token_bytes(32)
        self.__used=set()
    def issue(self, root, selected, *, plan_digest, request_nonce):
        if not plan_id_valid(plan_digest) or not re.fullmatch("[a-f0-9]{32}",request_nonce):
            raise AttestationRejected("invalid plan binding or nonce")
        observed=scan(root,selected) # Direct local read, not user/model text.
        if not observed["fixture_only"] or observed["real_client_universe_complete"]:
            raise AttestationRejected("unexpected real E3 authority")
        body={"schema":"maclean-v07-fixture-attestation",
              "observation":observed,
              "observation_sha256":digest(observed),
              "plan_digest":plan_digest,"nonce":request_nonce,
              "issued_at":time_now().isoformat()}
        return {"payload":body,"hmac_sha256":_stamp(self.__key,body)}
    def verify_fresh(self, envelope,root,selected,*,expected_plan_digest,
                     expected_nonce,max_age_seconds=30):
        if (not isinstance(envelope,dict) or set(envelope)!={"payload","hmac_sha256"}
                or not isinstance(envelope["payload"],dict)):
            raise AttestationRejected("invalid envelope")
        b=envelope["payload"]
        if (set(b)!={"schema","observation","observation_sha256","plan_digest","nonce","issued_at"}
                or b["schema"]!="maclean-v07-fixture-attestation"
                or b["plan_digest"]!=expected_plan_digest or b["nonce"]!=expected_nonce
                or not plan_id_valid(expected_plan_digest)
                or not re.fullmatch("[a-f0-9]{32}",expected_nonce)):
            raise AttestationRejected("mismatched scope/plan/nonce")
        try:submitted=bytes.fromhex(envelope["hmac_sha256"])
        except (TypeError,ValueError):raise AttestationRejected("invalid tag") from None
        if len(submitted)!=32 or not hmac.compare_digest(submitted,bytes.fromhex(_stamp(self.__key,b))):
            raise AttestationRejected("tampered observation")
        try:issued=datetime.fromisoformat(b["issued_at"])
        except (TypeError,ValueError):raise AttestationRejected("bad timestamp") from None
        if issued.tzinfo is None:raise AttestationRejected("naive timestamp")
        age=(time_now()-issued.astimezone(timezone.utc)).total_seconds()
        if age<0 or age>max_age_seconds:raise AttestationRejected("stale/future observation")
        if b["nonce"] in self.__used:raise AttestationRejected("replayed snapshot")
        current=scan(root,selected)
        if (digest(current)!=b["observation_sha256"]
                or current!=b["observation"]):
            raise AttestationRejected("TOCTOU: live project/link state changed")
        self.__used.add(b["nonce"])
        return {"schema":"maclean-v07-verification","integrity":"PASS",
                "fresh_and_no_local_drift":True,
                "plan_digest_bound":True,"challenge_bound":True,
                "selected_client_ids":sorted(selected),
                "coverage":"PARTIAL_REAL_HOST_UNPROVEN",
                "complete_real_e3":False,
                "approved_cleanup_targets":[],
                "deletion_authorized":False,
                "production_cryptographic_trust_boundary":False,
                "note":"Same-user fixture HMAC is a research demonstration, not independently secured executor signing."}
if __name__=="__main__":
    from project_witness import fixture
    with fixture(unselected=True) as root:
        issuer=FixtureWitnessIssuer()
        pid=digest({"plan":"synthetic-only"})
        nonce=secrets.token_hex(16)
        record=issuer.issue(root,["client-ALPHA"],plan_digest=pid,request_nonce=nonce)
        print(json.dumps(issuer.verify_fresh(record,root,["client-ALPHA"],
                                              expected_plan_digest=pid,expected_nonce=nonce)))
