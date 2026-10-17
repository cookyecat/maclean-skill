#!/usr/bin/env python3
"""Verify v1.4.0 source and historical v1.3.x release archives separately.

The repository may update its source tree before a new installation ZIP ships.
Do NOT compare the latest source manifest to a historical archive.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

EXPECTED_ZIPS = {
    "macos-disk-auditor-v1.3.0.zip": "4dc20c4a33b57ee6a0bc76296042cd97834a5d21be6afd6d8450bda47bdf3a09",
    "macos-disk-auditor-v1.3.1.zip": "7ec47c0d0afe5b60aa200359885b59658fa9d0504af340ef83757ccc0d0512f5",
}
VERSION = "1.4.0"
N_FILES = 17


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate(root: Path, source_dir: Path) -> dict:
    source = source_dir / "manifest.json"
    manifest = json.loads(source.read_bytes())
    assert manifest["version"] == VERSION
    assert manifest["hash_algorithm"] == "sha256"
    assert len(manifest["files"]) == N_FILES
    for relative, expected_sha in manifest["files"].items():
        file = source_dir / relative
        assert file.is_file() and not file.is_symlink(), relative
        assert digest(file.read_bytes()) == expected_sha, relative

    # Compare the exact source tree, excluding Python build output produced by
    # the separate CI syntax compilation step.
    actual = {
        p.relative_to(source_dir).as_posix()
        for p in source_dir.rglob("*")
        if p.is_file() and not p.is_symlink()
        and "__pycache__" not in p.relative_to(source_dir).parts
        and p.suffix != ".pyc"
    }
    assert actual == set(manifest["files"]) | {"manifest.json"}

    artifacts = root / "artifacts"
    expected_lines = [f"{sha}  {filename}" for filename, sha in EXPECTED_ZIPS.items()]
    assert (artifacts / "SHA256SUMS.txt").read_text().splitlines() == expected_lines

    zipped = {}
    for filename, expected_sha in EXPECTED_ZIPS.items():
        archive = artifacts / filename
        assert digest(archive.read_bytes()) == expected_sha, filename
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None, filename
            bundle_name = "macos-disk-auditor/manifest.json"
            embedded = json.loads(z.read(bundle_name))
            expected_version = filename.removeprefix("macos-disk-auditor-v").removesuffix(".zip")
            assert embedded["version"] == expected_version, filename
            assert len(embedded["files"]) == N_FILES, filename
            file_names = {name for name in z.namelist() if not name.endswith("/")}
            assert file_names == {
                "macos-disk-auditor/" + p
                for p in embedded["files"]
            } | {bundle_name}, filename
            for rel, signature in embedded["files"].items():
                assert digest(z.read("macos-disk-auditor/" + rel)) == signature, (filename, rel)
        zipped[filename] = expected_sha

    return {
        "ok": True,
        "source_version": manifest["version"],
        "source_file_count": len(manifest["files"]),
        "historical_archives": sorted(zipped),
        "source_manifest_sha256": digest(source.read_bytes()),
        "note": "Source-only v1.4.0 sync; historic v1.3.x ZIP archives are unchanged.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source-dir", type=Path, default=None)
    args = parser.parse_args()
    folder = args.source_dir or (args.repository_root / "skill/macos-disk-auditor")
    print(json.dumps(validate(args.repository_root, folder), sort_keys=True))
