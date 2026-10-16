#!/usr/bin/env python3
"""Fail-closed synthetic Playwright .links guard; never follows real host links.

Input may only be an owner-private maclean-v06-* disposable root created in the
OS temp directory. Link targets are checked lexically against an explicit small
fixture allowlist BEFORE any target-directory or manifest read.
"""
from __future__ import annotations
import json, pathlib, re, stat, tempfile

class LinkDenied(ValueError):
    pass

def root_ok(root:pathlib.Path)->pathlib.Path:
    allowed={pathlib.Path("/private/tmp"),pathlib.Path(tempfile.gettempdir()).resolve()}
    if (root.is_symlink() or not root.name.startswith("maclean-v06-")
            or root.parent not in allowed or not root.is_dir()
            or root.stat().st_mode & 0o077):
        raise LinkDenied("not owner-private disposable fixture")
    return root.resolve(strict=True)

def scan_fixture_links(root:pathlib.Path, *, expected_clients:set[str]) -> dict:
    root=root_ok(root)
    if (not isinstance(expected_clients,set) or not expected_clients
            or len(expected_clients)>16
            or any(not re.fullmatch(r"client-[A-Za-z0-9_-]{1,24}",x) for x in expected_clients)):
        raise LinkDenied("invalid explicit fixture client allowlist")
    browser_root=root/"browser-cache"
    clients=root/"clients"
    # Reject parent symlinks BEFORE any child stat(), is_dir() or manifest read.
    if browser_root.is_symlink() or clients.is_symlink():
        raise LinkDenied("fixture parent symlink forbidden")
    if not browser_root.is_dir() or not clients.is_dir():
        raise LinkDenied("fixture parents not directories")
    links=browser_root/".links"
    if links.is_symlink() or not links.is_dir() or links.resolve(strict=True).parent!=browser_root:
        raise LinkDenied("fixture links layout invalid")
    entries=sorted(links.iterdir())
    if not entries or len(entries)>32:raise LinkDenied("no or excessive links")
    seen=set()
    manifests=[]
    for link in entries:
        if (not re.fullmatch(r"[A-Za-z0-9_-]{1,32}",link.name)
                or link.is_symlink() or not link.is_file()
                or link.stat().st_size>512):
            raise LinkDenied("unexpected link file")
        raw=link.read_text(encoding="utf8")
        if "\x00" in raw or "\n" in raw or "\r" in raw:
            raise LinkDenied("link contains control characters")
        path=pathlib.Path(raw)
        # String comparison only. Do NOT resolve/stat an untrusted linked path.
        if path.parent!=clients or path.name not in expected_clients:
            raise LinkDenied("client outside explicit fixture allowlist")
        if path in seen:raise LinkDenied("duplicate client link")
        seen.add(path)
        if path.is_symlink() or not path.is_dir() or path.resolve(strict=True)!=path:
            raise LinkDenied("client path is not a confined directory")
        required={}
        for filename in ("package.json","browsers.json"):
            f=path/filename
            if f.is_symlink() or not f.is_file() or f.stat().st_size>64_000:
                raise LinkDenied("client manifest missing or unsafe")
            try: required[filename]=json.loads(f.read_text(encoding="utf8"))
            except (ValueError,UnicodeError):raise LinkDenied("unparseable client manifest") from None
        if (not isinstance(required["package.json"],dict)
                or not isinstance(required["package.json"].get("version"),str)
                or not isinstance(required["browsers.json"],dict)
                or not isinstance(required["browsers.json"].get("browsers"),list)):
            raise LinkDenied("unexpected publisher metadata structure")
        manifests.append(len(required["browsers.json"]["browsers"]))
    return {
        "schema":"maclean-v06-links-fixture-only",
        "client_links_verified":len(manifests),
        "browser_descriptor_counts":manifests,
        "full_host_client_universe_proven":False,
        "raw_client_locations_exposed":False,
        "real_project_metadata_read":False,
        "deletion_authorized":False
    }
