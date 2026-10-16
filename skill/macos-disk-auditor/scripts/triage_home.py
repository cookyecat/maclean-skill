#!/usr/bin/env python3
"""Privacy-first read-only evidence for AI assessment; never decides deletion eligibility."""
import argparse
import json
from pathlib import Path
from privacy_policy import POLICY_ID, EXCLUDED_CLASSES, discover, public_id, app_catalog_entry
from cleanup_plan import disk_kib, resolve_target, running

GUARD_BY_KIND = {'npm_cache':'Npm','npx_install':'Npm','uv_cache':'Uv',
                 'puppeteer_cache':'Puppeteer','downloaded_runtime':'Playwright',
                 'codex_runtime_installer':'Codex','codex_daemon_old':'Codex',
                 'old_version':'Cursor','cargo_target':'Cargo'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--json', action='store_true')
    p.add_argument('--details', action='store_true', help='Explicit local-only detailed paths and PIDs')
    p.add_argument('--project-root', type=Path, help='Explicitly selected developer project')
    a = p.parse_args()
    home = Path.home()
    found = discover(home, project_root=a.project_root)
    candidates = []
    for index,(path,kind,group) in enumerate(found,1):
        meta=app_catalog_entry(path.relative_to(home).as_posix())
        guard=meta['guard'] if meta else GUARD_BY_KIND[kind]
        row = {'id':public_id(kind,index), 'kind':kind, 'group':group,
               'ai_assessment':'REQUIRED', 'approved':False,
               'status':'REVIEW', 'size_mib':None, 'safety_blocks':[]}
        if meta:
            row.update({'app':meta['app'],'rebuild_risk':meta['risk']})
            if kind=='profile_cache': row['review_flags']=['OFFLINE_DATA_MAY_NOT_REDOWNLOAD']
        if a.details:
            row['path'] = '~/' + path.relative_to(home).as_posix()
        try:
            row['size_mib'] = round(disk_kib(path)/1024, 1)
        except (ValueError,OSError):
            row['status'] = 'UNKNOWN'
            row['safety_blocks'].append('SIZE_UNAVAILABLE')
        try:
            # Path authorization is a *negative safety veto*, never a decision
            # that this candidate ought to be deleted.
            ent = {'path':'~/' + path.relative_to(home).as_posix(), 'kind':kind,
                   'reason':'Synthetic review placeholder; AI must assess independently',
                   'requires_quit':[guard]}
            resolve_target(ent,home)
        except (ValueError,OSError):
            row['status'] = 'PROTECTED'
            row['safety_blocks'].append('MUTATION_SAFETY_BLOCK')
        if row['status']=='REVIEW':
            try:
                matched=running([guard],path)
                if matched:
                    row['status']='ACTIVE'
                    row['safety_blocks'].append('RELATED_PROCESS_RUNNING')
                    if a.details:
                        row['matching_pids']=sorted(set().union(*matched.values()))
            except (ValueError,OSError):
                row['status']='UNKNOWN'
                row['safety_blocks'].append('PROCESS_AUDIT_UNAVAILABLE')
        candidates.append(row)
    report={'policy':POLICY_ID,'scope':'known_technical_targets',
            'privacy_exclusions':list(EXCLUDED_CLASSES),
            'excluded_actual_count':None,'complete_within_policy':True,
            'read_only':True,'user_approved':False,
            'ai_decision_required':True,
            'note':'Machine safety signals are not deletion recommendations or approvals.',
            'candidates':candidates}
    if a.json:
        print(json.dumps(report,ensure_ascii=False,indent=2))
    else:
        print('PRIVACY-SAFE TRIAGE | AI review required | no cleanup approved')
        for x in candidates:
            print(f"{x['id']} {x['kind']} {x['size_mib']} MiB {x['status']}")
    return 0

if __name__=='__main__':
    raise SystemExit(main())
