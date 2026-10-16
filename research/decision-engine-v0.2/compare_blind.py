#!/usr/bin/env python3
"""Compare two blinded provider results; does not claim accuracy without human gold."""
import argparse,hashlib,json,os,pathlib,sys
STATES=("RECOMMEND","DEFER","KEEP")
def hash_data(x):
 return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def private_write(f,x):
 fd=os.open(f,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as out:json.dump(x,out,ensure_ascii=False,indent=2);out.write('\n')
def compare(blind,results):
 cases=blind["cases"];ids=[c["id"] for c in cases];assert len(ids)==len(set(ids))
 fp=hash_data(blind)
 ps={}
 for name,r in results.items():
  assert r["meta"]["blind_sha256"]==fp,"MISMATCHED_FROZEN_INPUT"
  pred=r["predictions"]
  assert len(pred)==len(ids) and {x["id"] for x in pred}==set(ids)
  ps[name]={p["id"]:p for p in pred}
 names=list(results)
 a,b=names
 counter={x:{y:0 for y in STATES} for x in STATES}
 violations={a:[],b:[]}
 changes=[]
 for c in cases:
  cid=c["id"]
  x,y=ps[a][cid],ps[b][cid]
  counter[x["decision"]][y["decision"]]+=1
  if x["decision"]!=y["decision"]:changes.append(cid)
  for name,p in ((a,x),(b,y)):
   unsafe=(p["decision"]=="RECOMMEND" and
           (c["machine_safety_state"]!="REVIEW" or
            c["rebuildability_evidence"]=="not_independently_verified"))
   if unsafe:violations[name].append(cid)
 raw_agreement=sum(counter[s][s] for s in STATES)/len(cases)
 rates={name:{s:sum(p["decision"]==s for p in ps[name].values()) for s in STATES} for name in names}
 exp=sum((rates[a][s]/len(ids))*(rates[b][s]/len(ids)) for s in STATES)
 kappa=(raw_agreement-exp)/(1-exp) if exp<1 else None
 return {
  "research_only":True,"human_gold_available":False,"accuracy_not_computable":True,
  "blind_sha256":fp,"n":len(cases),"providers":names,
  "state_counts":rates,"agreement_ratio":round(raw_agreement,3),
  "cohen_kappa":round(kappa,3) if kappa is not None else None,
  "cross_tab":counter,"disagreements":changes,
  "unsubstantiated_recommendations":violations,
  "qualifier":"Not human-verified. A machine status plus unverified reconstructability cannot ground a deletion recommendation.",
  "model_latencies_s":{name:results[name]["meta"].get("duration_s") for name in names}
 }
def main():
 a=argparse.ArgumentParser()
 for k in ("blind","minimax","deepseek","output"):a.add_argument("--"+k,type=pathlib.Path,required=True)
 args=a.parse_args()
 blind=json.loads(args.blind.read_text())
 out=compare(blind,{k:json.loads(getattr(args,k).read_text()) for k in ("minimax","deepseek")})
 assert args.output.parent.stat().st_mode&0o077==0
 private_write(args.output,out)
 print(json.dumps(out,ensure_ascii=False))
if __name__=="__main__":main()
