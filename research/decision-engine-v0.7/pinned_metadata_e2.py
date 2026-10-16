#!/usr/bin/env python3
"""Use PREVIOUSLY PINNED official Playwright metadata in private synthetic fixture.

Does not inspect any real project/browser cache, install npm dependencies,
invoke npx, download browsers or run cleanup commands.
"""
from __future__ import annotations
import argparse,json,pathlib,shutil,tempfile
from project_witness import fixture,scan,ScopeDenied

def isolated_publisher_root(path:pathlib.Path)->pathlib.Path:
    if not path.is_dir() or path.is_symlink() or not path.name.startswith("maclean-v05-native-e2."):
        raise ScopeDenied("must use existing isolated pinned package fixture")
    real=path.resolve(strict=True)
    if real.parent not in (pathlib.Path("/private/tmp"),pathlib.Path(tempfile.gettempdir()).resolve()):
        raise ScopeDenied("pinned package prefix outside private temp")
    if real.stat().st_mode & 0o077:
        raise ScopeDenied("package root not owner-private")
    source=real/"pkg"/"node_modules"/"playwright-core"
    for name in ("package.json","browsers.json"):
        f=source/name
        if f.is_symlink() or not f.is_file() or f.stat().st_size>65536:
            raise ScopeDenied("publisher manifest unavailable")
    if json.loads((source/"package.json").read_text()).get("version")!="1.64.1":
        raise ScopeDenied("unexpected publisher version")
    return source

def probe(package_root:pathlib.Path)->dict:
    source=isolated_publisher_root(package_root)
    with fixture(unselected=True) as root:
        target=root/"projects"/"client-ALPHA"/"node_modules"/"playwright-core"
        for name in ("package.json","browsers.json"):
            shutil.copyfile(source/name,target/name)
        result=scan(root,["client-ALPHA"])
        return {
           "experiment":"v0.7 pinned publisher metadata mapped into synthetic project",
           "publisher":"playwright-core","version":"1.64.1",
           "reference_count":len(result["selected_clients"]["client-ALPHA"]["browser_revisions"]),
           "selected_client_count":result["selected_client_count"],
           "unselected_link_count":result["unknown_unread_link_targets"],
           "completeness":result["coverage"],
           "user_project_scanned":False,"real_cache_scanned":False,
           "browser_downloaded":False,"cleanup_executed":False,
           "deletion_authorized":False}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--pinned-root",required=True,type=pathlib.Path)
    print(json.dumps(probe(p.parse_args().pinned_root)))
