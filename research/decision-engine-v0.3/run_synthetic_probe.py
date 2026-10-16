#!/usr/bin/env python3
"""Synthetic evidence-ladder provider probe. Never scans/deletes files.

Only an invented E0-E3 research fixture is sent over HTTPS to the explicitly
configured MiniMax / DeepSeek provider. Raw replies remain on local disk (0600).
"""
import argparse, hashlib, json, os, pathlib, re, sys, time, urllib.parse, urllib.request, urllib.error

def config(path):
    rows={}
    for raw in path.read_text(errors='replace').splitlines():
        if raw.lstrip().startswith('#') or '=' not in raw: continue
        k,v=raw.split('=',1);k=k.strip().removeprefix('export ').strip()
        if re.fullmatch('[A-Z0-9_]+',k): rows[k]=v.strip().strip('"').strip("'")
    return rows

def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def private_file(path, data):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:
        json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')

SYSTEM="""You are an independent research analyst assessing macOS cache observations.
No tools; no commands; no assumptions about user identity or exact paths.
For each case choose RECOMMEND, DEFER, or KEEP. Synthetic E3 checks are assumed to have been independently established ONLY in this hypothetical scenario, not on a real Mac.
RECOMMEND only when trustworthy evidence proves safe reconstructability,
low impact, no live dependency, and worthwhile gain. REVIEW is NOT a recommendation.
ACTIVE and PROTECTED are independent hard vetoes. If evidence is insufficient, KEEP; if only timing/process status is blocking, DEFER. When synthetic E3 supplies all needed evidence and no block, consider RECOMMEND rather than automatically KEEP. Never invent evidence.
Only cite exact IDs from each case's available_evidence_ids.
For a RECOMMEND choose strategy NATIVE_PRUNE / NATIVE_CLEAN / EXACT_PATH;
otherwise choose NONE. Strategies are research proposals, NOT executable commands.
Return a JSON object with predictions array, each entry with fields
id, decision, cleanup_strategy, reason, evidence_ids, confidence.
Cover every case exactly once, with no other text."""

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--provider',required=True,choices=['minimax','deepseek'])
    p.add_argument('--blind',required=True,type=pathlib.Path)
    p.add_argument('--env-file',required=True,type=pathlib.Path)
    p.add_argument('--output-dir',required=True,type=pathlib.Path)
    a=p.parse_args()
    blind=json.loads(a.blind.read_text())
    cases=blind['cases']
    assert len(cases)==9 and blind['dataset']=='evidence-ladder-synthetic-v0.3' and blind['is_synthetic'] is True
    raw=json.dumps(blind,ensure_ascii=False)
    assert all(t not in raw for t in ('/Users/','/var/folders/','~/','API_KEY','sk-'))
    assert a.output_dir.is_dir() and a.output_dir.stat().st_mode&0o077==0
    d=config(a.env_file)
    if a.provider=='minimax':
        key,base,model=(d.get(k) for k in ('RAOS_LLM_API_KEY','RAOS_LLM_BASE_URL','RAOS_LLM_MODEL'))
    else:
        key,base,model=(d.get(k) for k in ('RAOS_DEEPSEEK_API_KEY','RAOS_DEEPSEEK_BASE_URL','RAOS_DEEPSEEK_MODEL'))
    assert key and base and model
    assert urllib.parse.urlparse(base).hostname in ('api.minimax.cn','api.deepseek.com')
    url=base.rstrip('/')+'/chat/completions'
    payload={
        'model':model,
        'messages':[{'role':'system','content':SYSTEM},
                    {'role':'user','content':'Independently assess all 9 cases; JSON only:\n'+raw}],
        'response_format':{'type':'json_object'},
        'stream':False,'max_tokens':11000
    }
    if a.provider=='minimax':
        payload['reasoning_effort']='max'
    else:
        payload['thinking']={'type':'enabled'}
    request=urllib.request.Request(url,data=json.dumps(payload).encode(),
          headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},
          method='POST')
    start=time.monotonic()
    try:
        with urllib.request.urlopen(request,timeout=260) as response:
            body=json.load(response)
    except urllib.error.HTTPError as error:
        print(json.dumps({'provider':a.provider,'status':'HTTP_ERROR',
                          'http_code':error.code,'response_suppressed':True}))
        return 4
    except Exception as error:
        print(json.dumps({'provider':a.provider,'status':'NETWORK_ERROR',
                          'error_class':type(error).__name__}))
        return 5
    try:
        answer=body['choices'][0]['message']['content']
        assert isinstance(answer,str)
        if answer.strip().startswith(chr(96)*3):
            answer=answer.strip().split('\n',1)[-1]
            answer=answer.rsplit(chr(96)*3,1)[0]
        predictions=json.loads(answer)['predictions']
        ids=[c['id'] for c in cases]
        assert len(predictions)==len(ids) and {p['id'] for p in predictions}==set(ids)
        allowed={c['id']:set(c['available_evidence_ids']) for c in cases}
        for pred in predictions:
            assert pred['decision'] in ('RECOMMEND','DEFER','KEEP')
            assert pred['cleanup_strategy'] in ('NATIVE_PRUNE','NATIVE_CLEAN','EXACT_PATH','NONE')
            assert set(pred['evidence_ids']).issubset(allowed[pred['id']])
            assert len(pred.get('reason',''))>=10
    except Exception as error:
        private_file(a.output_dir/f'invalid_{a.provider}.json',{'body':body,'error_class':type(error).__name__})
        print(json.dumps({'provider':a.provider,'status':'OUTPUT_INVALID',
                          'error_class':type(error).__name__,'raw_response_private':True}))
        return 3
    u=body.get('usage') or {}
    meta={'provider':a.provider,'model':model,'duration_s':round(time.monotonic()-start,1),
          'thinking_mode':'max' if a.provider=='minimax' else 'enabled',
          'blind_sha256':digest(blind),'count':len(predictions),
          'token_usage':{k:u[k] for k in ('prompt_tokens','completion_tokens','total_tokens') if k in u}}
    private_file(a.output_dir/f'predictions_{a.provider}.json',{'predictions':predictions,'meta':meta})
    print(json.dumps({'provider':a.provider,'status':'OK','n':len(predictions),
        'duration_s':meta['duration_s'],'blind_sha256':meta['blind_sha256'],
        'counts':{state:sum(q['decision']==state for q in predictions) for state in ('RECOMMEND','DEFER','KEEP')}}))
    return 0

if __name__=='__main__':
    sys.exit(main())
