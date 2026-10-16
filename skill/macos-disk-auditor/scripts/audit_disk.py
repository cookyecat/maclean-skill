#!/usr/bin/env python3
"""Privacy-safe macOS disk allocation; never recursively traverse Home/Library parents."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from privacy_policy import POLICY_ID, EXCLUDED_CLASSES, PolicyDenied, authorize_scan, discover, public_id


def measure_one(path, timeout):
    # du only on an exact authorized technical leaf, not its parent.
    try:
        p = subprocess.run(['du', '-sk', str(path)], capture_output=True, text=True,
                           timeout=timeout or None)
    except (subprocess.TimeoutExpired, OSError):
        return None, 'MEASURE_ERROR'
    if p.returncode or not p.stdout.strip():
        return None, 'MEASURE_ERROR'
    first = p.stdout.splitlines()[0].split(None, 1)
    if not first or not first[0].isdigit():
        return None, 'MEASURE_ERROR'
    # du stderr may indicate partial traversal; never silently accept it.
    if p.stderr.strip():
        return None, 'MEASURE_ERROR'
    return int(first[0]), None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path.home() / 'Library')
    p.add_argument('--scope', choices=('home', 'library', 'path', 'developer'))
    p.add_argument('--project-root', type=Path, help='Explicitly user-selected developer project root')
    p.add_argument('--user-selected-cache', action='store_true', help='User explicitly selected exact Library/Caches/<app> leaf')
    p.add_argument('--depth', type=int, default=1)   # compatibility; not used to recurse
    p.add_argument('--top', type=int, default=25)
    p.add_argument('--min-mib', type=float, default=0)
    p.add_argument('--json', action='store_true')
    p.add_argument('--details', action='store_true', help='Explicit local-only detailed path report')
    p.add_argument('--skip-root-total', action='store_true')
    p.add_argument('--du-timeout', type=int, default=45)
    a = p.parse_args()
    if not (1 <= a.depth <= 3 and 1 <= a.top <= 50 and a.min_mib >= 0 and 0 <= a.du_timeout <= 3600):
        p.error('invalid depth/top/min-mib/du-timeout')
    home = Path.home().absolute()
    root = a.root.expanduser().absolute()
    if a.scope is None:
        if root == home:
            a.scope = 'home'
        elif root == home / 'Library':
            a.scope = 'library'
        else:
            a.scope = 'path'
    try:
        if a.scope in ('home', 'library'):
            expected = home if a.scope == 'home' else home / 'Library'
            if root != expected:
                raise PolicyDenied('scope root must be HOME or HOME/Library')
            targets = discover(home, group=a.scope)
        elif a.scope == 'developer':
            if a.project_root is None:
                raise PolicyDenied('developer scope requires explicit --project-root')
            targets = discover(home, group='developer', project_root=a.project_root)
        else:
            kind, group = authorize_scan(home, root, project_root=a.project_root, user_selected_cache=a.user_selected_cache)
            targets = [(root, kind, group)] if root.is_dir() else []
    except PolicyDenied as exc:
        p.error('PRIVACY_SCOPE_DENIED: ' + str(exc))
    started = time.monotonic()
    candidates = []
    warnings = []
    for idx, (path, kind, group) in enumerate(targets, 1):
        try:
            authorize_scan(home, path, project_root=a.project_root, user_selected_cache=a.user_selected_cache)
            kib, error = measure_one(path, a.du_timeout)
        except PolicyDenied:
            kib, error = None, 'POLICY_DENIED'
        item = {'id': public_id(kind, idx), 'kind': kind, 'measurement':
                'UNKNOWN_ERROR' if error else 'MEASURED', 'size_kib': kib,
                'size_mib': round(kib/1024, 1) if kib is not None else None}
        if a.details:
            item['path'] = '~/' + path.relative_to(home).as_posix()
        candidates.append(item)
        if error:
            warnings.append({'id': item['id'], 'code': error})
    free = shutil.disk_usage(home)
    result = {'policy': POLICY_ID, 'coverage_profile': a.scope,
              'complete_within_policy': not warnings,
              'complete': not warnings, 'home_total_measured': False,
              'root_kib': None, 'root_total_skipped': True,
              'privacy_exclusions': list(EXCLUDED_CLASSES),
              'excluded_actual_count': None,  # intentionally not enumerated
              'candidate_count': len(candidates), 'candidates': candidates[:a.top],
              'display_truncated': len(candidates) > a.top,
              'warnings': warnings, 'elapsed_seconds': round(time.monotonic()-started, 2),
              'disk': {'total_gib': round(free.total/2**30, 2),
                       'used_gib': round(free.used/2**30, 2),
                       'free_gib': round(free.free/2**30, 2)}}
    if a.details:
        result['root'] = '~/' + root.relative_to(home).as_posix() if root != home else '~'
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print('PRIVACY-SAFE MACOS AUDIT | scope=' + a.scope)
        print('Only explicitly allowlisted technical leaves were measured; Home total NOT measured')
        for item in result['candidates']:
            print(f"{item['id']} {item['kind']} {item['size_mib']} MiB [{item['measurement']}]")
    return 0 if not warnings else 4

if __name__ == '__main__':
    raise SystemExit(main())
