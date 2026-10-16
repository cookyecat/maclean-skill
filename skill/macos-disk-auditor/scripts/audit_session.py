#!/usr/bin/env python3
"""Verified privacy-first read-only audit with owner-private report checkpoints."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import platform
import stat
import subprocess
import sys
import uuid
from verify_bundle import digest, verify

SCOPES=('home','library','triage','path','developer')
def now():return datetime.now(timezone.utc).isoformat(timespec='seconds')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--scope',choices=SCOPES,required=True)
    ap.add_argument('--root',type=Path,help='Exact known cache leaf for --scope path')
    ap.add_argument('--project-root',type=Path,help='User-selected developer project for --scope developer')
    ap.add_argument('--details',action='store_true',help='Explicit local-only detailed report')
    ap.add_argument('--user-selected-cache',action='store_true',help='Exact user-selected app cache leaf with explicit scope authorization')
    ap.add_argument('--output-dir',type=Path,required=True)
    ap.add_argument('--timeout',type=int,default=180)
    ap.add_argument('--depth',type=int,choices=(1,2,3),default=1)
    ap.add_argument('--top',type=int,default=25)
    ap.add_argument('--du-timeout',type=int,default=45)
    a=ap.parse_args()
    if not(5<=a.timeout<=3600 and 5<=a.du_timeout<=180 and 1<=a.top<=50):
        ap.error('Invalid timeout/top')
    if a.scope=='path' and a.root is None:ap.error('--root required for path')
    if a.scope=='developer' and a.project_root is None:ap.error('--project-root required for developer')
    bundle=Path(__file__).resolve().parent.parent
    v=verify(bundle)
    if not v['ok']:
        print('BLOCKED: manifest integrity failed',file=sys.stderr)
        return 3
    directory=a.output_dir.expanduser().absolute()
    if directory.is_symlink():ap.error('report directory may not be symlink')
    directory.mkdir(parents=True,mode=0o700,exist_ok=True)
    if not directory.is_dir() or directory.is_symlink() or directory.stat().st_uid!=os.geteuid() or directory.stat().st_mode & 0o077:
        ap.error('report directory must be owned by caller and mode 0700')
    if a.scope=='triage':
        script=bundle/'scripts/triage_home.py'
        command=[sys.executable,str(script),'--json']
        if a.project_root:command+=['--project-root',str(a.project_root)]
    else:
        script=bundle/'scripts/audit_disk.py'
        command=[sys.executable,str(script),'--scope',a.scope,'--json','--depth',str(a.depth),
                 '--top',str(a.top),'--du-timeout',str(a.du_timeout),'--skip-root-total']
        if a.scope=='home':command+=['--root',str(Path.home())]
        if a.scope=='library':command+=['--root',str(Path.home()/'Library')]
        if a.scope=='path':command+=['--root',str(a.root)]
        if a.project_root:command+=['--project-root',str(a.project_root)]
        if a.user_selected_cache:command+=['--user-selected-cache']
    if a.details:command.append('--details')
    started=now();status='failed';payload=None;error=None;exit_code=None
    try:
        p=subprocess.run(command,capture_output=True,text=True,timeout=a.timeout)
        exit_code=p.returncode
        try:payload=json.loads(p.stdout)
        except json.JSONDecodeError:error='Invalid JSON from verified audit script'
        if exit_code==0 and payload is not None:
            status='ok' if payload.get('complete_within_policy',True) else 'partial'
        elif exit_code==4 and payload is not None:status='partial'
        else:error=error or f'Bundled script refused or failed: exit={exit_code}'
    except subprocess.TimeoutExpired:
        status='timeout';error='Audit exceeded bounded timeout'
    report={'skill':'macos-disk-auditor','version':'1.4.0',
            'bundle_manifest_sha256':v['manifest_sha256'],
            'bundle_integrity_checked_files':v['checked'],
            'executed_script':script.relative_to(bundle).as_posix(),
            'executed_script_sha256':digest(script),
            'scope':a.scope,'read_only_audit':True,
            'target_files_modified':False,'platform':platform.system(),
            'start_utc':started,'finish_utc':now(),'status':status,
            'script_exit_code':exit_code,'error':error,'result':payload}
    # Intentionally no hostname, login, or absolute audited paths by default.
    if a.details:
        report['audited_path']=str(a.root or a.project_root or Path.home())
    dest=directory/f'audit-{a.scope}-{uuid.uuid4().hex[:10]}.json'
    fd=os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as f:
        json.dump(report,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(json.dumps({'status':status,'report_path':str(dest),'scope':a.scope,
                      'executed_script':report['executed_script'],
                      'script_exit_code':exit_code,'bundle_integrity':'PASS'},ensure_ascii=False))
    return 0 if status=='ok' else 4

if __name__=='__main__':
    raise SystemExit(main())
