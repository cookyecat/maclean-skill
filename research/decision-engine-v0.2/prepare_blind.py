#!/usr/bin/env python3
"""Prepare blinded, coarse real observations from a private MacLean snapshot.

Nothing is sent on network by this program. Output remains inside 0700 dir.
"""
import argparse,hashlib,json,os,pathlib

BANDS=((32,"<32 MiB"),(128,"32-128 MiB"),(512,"128-512 MiB"),(2048,"512 MiB-2 GiB"),(float('inf'),">=2 GiB"))
def canonical(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
def band(x):
 if x is None:return "unknown"
 for ceil,label in BANDS:
  if x<ceil:return label
def dump_private(p,d):
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w',encoding='utf8') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')

def select(rows):
 # Include every REVIEW plus stratified ACTIVE/PROTECTED without exposing names or exact sizes.
 chosen=[x for x in rows if x["status"]=="REVIEW"]
 for state,budget in (("ACTIVE",4),("PROTECTED",2)):
  seen=set()
  for row in rows:
   if row["status"]!=state or row["kind"] in seen: continue
   chosen.append(row);seen.add(row["kind"])
   if len(seen)>=budget:break
 return chosen

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--snapshot",type=pathlib.Path,required=True)
 ap.add_argument("--output-dir",type=pathlib.Path,required=True)
 a=ap.parse_args()
 root=a.output_dir.resolve();assert root.is_dir() and root.stat().st_mode&0o077==0
 source=json.loads(a.snapshot.read_text())
 assert source["schema"]=="real-anon-v0.2" and source["is_ground_truth"] is False
 chosen=select(source["candidates"])
 safe=[]
 for i,r in enumerate(chosen,1):
  assert r["status"] in ("REVIEW","ACTIVE","PROTECTED","UNKNOWN")
  out={
   "id":f"C{i:02d}","artifact_kind":r["kind"],
   "machine_safety_state":r["status"],
   "size_band":band(r.get("size_mib")),
   "process_signal":"category_match_not_exact_reference" if r["status"]=="ACTIVE" else "no_process_signal_confirmed" if r["status"]=="REVIEW" else "unknown",
   "rebuildability_evidence":"not_independently_verified",
   "offline_risk_cue":r.get("rebuild_risk","unspecified"),
   "safety_blocks":r.get("safety_blocks",[]),
   "available_evidence_ids":[f"obs:C{i:02d}:triage",f"obs:C{i:02d}:sizeband"]
  }
  safe.append(out)
 model_input={
   "dataset":"real-coarse-blind-v0.2",
   "is_synthetic":False,"is_gold_labeled":False,
   "source":"verified_privacy-safe-triage; identity and exact locations redacted",
   "notes":"These are coarse observations, not a complete safety investigation.",
   "evidence_limits":["no paths/pids/commands/profile IDs","process class matches need not prove exact directory use","no cache payload inspected","rebuildability not independently established"],
   "cases":safe}
 raw=json.dumps(model_input,ensure_ascii=False)
 for bad in ('/Users/','/var/folders/','~/', 'api_key','apikey','token','@'):assert bad not in raw.lower(),bad
 sha=hashlib.sha256(canonical(model_input)).hexdigest()
 dump_private(root/'blind.real-coarse.v0.2.json',model_input)
 print(json.dumps({"sample_n":len(safe),"status_counts":{s:sum(x["machine_safety_state"]==s for x in safe) for s in ("REVIEW","ACTIVE","PROTECTED")},
                   "blind_sha256":sha,"saved_private":True,"no_exact_paths":True},ensure_ascii=False))
if __name__=="__main__":main()
