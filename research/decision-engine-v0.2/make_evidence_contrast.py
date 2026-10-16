#!/usr/bin/env python3
"""Make a *synthetic* evidence-enrichment counterfactual from a blind cache sample.

NEVER represents new facts about the user's Mac. All additions are hypothetical,
except the public Puppeteer re-download documentation identified by URL.
"""
import argparse,json,os,pathlib,hashlib
def hash_data(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--blind',type=pathlib.Path,required=True);p.add_argument('--output-dir',type=pathlib.Path,required=True)
 a=p.parse_args();src=json.loads(a.blind.read_text())
 assert src['dataset']=='real-coarse-blind-v0.2' and len(src['cases'])==12
 contrast=json.loads(json.dumps(src))
 contrast['dataset']='counterfactual-evidence-supplement-v0.2'
 contrast['is_synthetic']=True
 contrast['is_gold_labeled']=False
 contrast['source']='SYNTHETIC evidence counterfactuals; NOT actual additional Mac observations'
 contrast['notes']='Adds hypothetical verified rebuildability, time and network availability to test sensitivity. Not evidence that real Mac is safe.'
 for case in contrast['cases']:
  kind,state=case['artifact_kind'],case['machine_safety_state']
  case['lab_assumptions_not_real']=[]
  if case['id']=='C01' and kind=='puppeteer_cache' and state=='REVIEW':
   case['rebuildability_evidence']='PUBLIC_DOC_AND_HYPOTHETICAL_REDOWNLOAD_CONDITIONS'
   case['lab_assumptions_not_real']=[
      'Official Puppeteer installation documents browser download and reinstall',
      'Hypothetical: download source is accessible, no offline use and no current automation dependency',
      'Hypothetical: user values recovering this space now'
   ]
   case['available_evidence_ids']+=['public:puppeteer-install-doc','scenario:network-and-workflow-assumption']
   case['public_source']='https://pptr.dev/guides/installation'
  elif state=='ACTIVE':
   case['rebuildability_evidence']='HYPOTHETICAL_REGENERABLE_BUT_CURRENTLY_ACTIVE'
   case['lab_assumptions_not_real']=[
     'Hypothetical: this is reconstructable at some later time',
     'Original real status is still ACTIVE; no override of activity veto']
   case['available_evidence_ids']+=['scenario:rebuild-assumption']
  elif state=='PROTECTED':
   case['lab_assumptions_not_real']=['Hypothetical rebuildability never overrides PROTECTED status']
  else:
   case['lab_assumptions_not_real']=['No new reliable rebuildability evidence; remain uncertain']
 path=a.output_dir/'contrast.synthetic.v0.2.json'
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as stream:json.dump(contrast,stream,indent=2,ensure_ascii=False);stream.write('\n')
 print(json.dumps({'synthetic':True,'cases':len(contrast['cases']),
                   'contrast_sha256':hash_data(contrast),'public_source_count':1,
                   'user_machine_new_facts_claimed':False}))
if __name__=='__main__':main()
