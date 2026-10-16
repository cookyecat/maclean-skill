#!/usr/bin/env python3
"""Read-only verify the deployed macos-disk-auditor files against manifest SHA-256."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import sys


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


# Authoritative release declarations: only document headings identify the
# installed version. Historical vX.Y.Z references in body text are not errors.
EXPECTED_VERSION = "1.4.0"
DECLARATION_PATTERNS = {
    "SKILL.md": r"^# macOS Disk Auditor & Safe Cleanup — v(\d+\.\d+\.\d+)\s*$",
    "README_zh.md": r"^# macOS Disk Auditor & Safe Cleanup v(\d+\.\d+\.\d+)\s*$",
    "references/execution-contract.md": r"^# Mandatory genuine Skill acceptance contract — v(\d+\.\d+\.\d+)\s*$",
}


def version_declarations(root):
    """Return release version from each authoritative document heading."""
    found, errors = {}, []
    for relative, pattern in DECLARATION_PATTERNS.items():
        try:
            lines = (root / relative).read_text(encoding="utf-8").splitlines()
            # SKILL.md carries YAML frontmatter, so title is not its first line.
            candidate = next((line for line in lines if line.startswith("# ")), "")
            match = re.fullmatch(pattern, candidate)
            found[relative] = match.group(1) if match else None
            if not match:
                errors.append(f"Invalid release heading: {relative}")
        except (OSError, UnicodeError) as exc:
            found[relative] = None
            errors.append(f"Cannot inspect release heading: {relative}: {exc}")
    return found, errors


def verify(root):
    root = Path(root).expanduser().resolve()
    manifest_path = root / 'manifest.json'
    errors = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        files = manifest['files']
        if manifest['name'] != 'macos-disk-auditor' or manifest['version'] != EXPECTED_VERSION:
            errors.append('Unexpected bundle identity/version')
        if not isinstance(files, dict) or not files:
            raise ValueError('Manifest has no files')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {'ok': False, 'root': str(root), 'errors': [f'Invalid manifest: {type(exc).__name__}: {exc}'], 'checked': 0}
    checked = 0
    for relative, expected in sorted(files.items()):
        candidate = root / relative
        if (not isinstance(relative, str) or relative.startswith('/') or
                '..' in Path(relative).parts or '\\' in relative or
                not isinstance(expected, str) or len(expected) != 64):
            errors.append('Unsafe/invalid manifest file entry')
            continue
        if candidate.is_symlink() or not candidate.is_file() or not candidate.resolve().is_relative_to(root):
            errors.append(f'Missing or unsafe file: {relative}')
            continue
        checked += 1
        if digest(candidate) != expected:
            errors.append(f'Hash mismatch: {relative}')
    included_scripts = {p.relative_to(root).as_posix() for p in (root / 'scripts').glob('*.py')}
    unexpected = included_scripts.difference(files)
    if unexpected:
        errors.extend(f'Unexpected executable script: {x}' for x in sorted(unexpected))
    declarations, declaration_errors = version_declarations(root)
    errors.extend(declaration_errors)
    for relative, declared in declarations.items():
        if declared is not None and declared != manifest["version"]:
            errors.append(f"Release version mismatch: {relative}: "
                          f"declared={declared}; manifest={manifest['version']}")
    return {'ok': not errors, 'declared_versions': declarations,
            'skill_md_sha256': digest(root / "SKILL.md") if (root / "SKILL.md").is_file() else None, 'name': manifest.get('name'), 'version': manifest.get('version'),
            'root': str(root), 'manifest_sha256': digest(manifest_path),
            'checked': checked, 'expected_files': len(files), 'errors': errors}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', default=str(Path(__file__).resolve().parent.parent))
    p.add_argument('--json', action='store_true')
    args = p.parse_args()
    result = verify(args.root)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"BUNDLE INTEGRITY: {'PASS' if result['ok'] else 'FAIL'}; "
              f"files={result['checked']}/{result.get('expected_files', '?')}; "
              f"version={result.get('version','UNKNOWN')}")
        for e in result['errors']:
            print(' - ' + e, file=sys.stderr)
    return 0 if result['ok'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
