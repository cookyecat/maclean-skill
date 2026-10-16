#!/usr/bin/env python3
"""Verify immutable v1.3.0 original source and release asset."""
from pathlib import Path
import hashlib, sys, json, zipfile, tempfile, subprocess
root=Path(__file__).resolve().parents[1]
z=root/'artifacts/macos-disk-auditor-v1.3.0.zip'
expected_zip="4dc20c4a33b57ee6a0bc76296042cd97834a5d21be6afd6d8450bda47bdf3a09"
expected_manifest="6dcdc492aad867b28e96ba25142c37c7e81f3c0e0219872d13c420dce5aafbe5"
expected_skill="64c93c23d9325101d3cf115ca8181f91317d229668d789c7f28b1a4c4c6872fe"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(z)==expected_zip, 'Original release ZIP was changed'
assert sha(root/'skill/macos-disk-auditor/manifest.json')==expected_manifest, 'Source manifest changed'
assert sha(root/'skill/macos-disk-auditor/SKILL.md')==expected_skill, 'Source skill changed'
with zipfile.ZipFile(z) as arc:
    assert arc.testzip() is None
    for name in arc.namelist():
        if name.endswith('/'):continue
        disk=root/'skill'/name
        assert disk.is_file(),f'Missing source: {name}'
        assert hashlib.sha256(arc.read(name)).hexdigest()==sha(disk),f'ZIP/source mismatch: {name}'
print(json.dumps({'ok':True,'original_zip_sha256':sha(z),'manifest_sha256':expected_manifest,'files_identical':True}))
