#!/usr/bin/env python3
"""Bounded synthetic browser/client dependency graph, read-only scanner.

Only accepts a newly created disposable fixture root bearing a marker.
Never scans the actual Playwright/Puppeteer cache or any project directories.
The synthetic manifests below are NOT Playwright's or Puppeteer's real format.
"""
from __future__ import annotations
import json, pathlib, stat, tempfile
from contextlib import contextmanager
from operation_registry import validate_graph, safe_ident

PREFIX="maclean-v04-disposable-"
MARKER=".maclean-v04-synthetic-only"

class FixtureBoundaryError(ValueError):
    pass

def _is_private(path: pathlib.Path) -> bool:
    return (path.stat().st_mode & 0o077)==0

def _verify_root(root: pathlib.Path) -> pathlib.Path:
    if root.is_symlink() or not root.name.startswith(PREFIX):
        raise FixtureBoundaryError("refuse non-disposable fixture root")
    try:
        verified=root.resolve(strict=True)
    except OSError as e:
        raise FixtureBoundaryError("fixture root unavailable") from e
    if verified!=root and not root.as_posix().startswith("/tmp/"):
        raise FixtureBoundaryError("unexpected root alias")
    if not verified.is_dir() or not _is_private(verified):
        raise FixtureBoundaryError("synthetic fixture must be private")
    marker=verified/MARKER
    if marker.is_symlink() or not marker.is_file() or marker.read_text()!="synthetic-no-user-data\n":
        raise FixtureBoundaryError("missing exact synthetic marker")
    return verified

def _bounded_dir(root: pathlib.Path, name: str) -> pathlib.Path:
    d=root/name
    if d.is_symlink() or not d.is_dir() or d.resolve(strict=True).parent!=root:
        raise FixtureBoundaryError("invalid fixed fixture directory")
    return d

def collect(root: pathlib.Path) -> dict:
    """Only single-level directory listing under synthetic browsers and clients."""
    root=_verify_root(root)
    browsers=_bounded_dir(root,"browsers")
    clients=_bounded_dir(root,"clients")
    browser_entries=list(browsers.iterdir())
    client_entries=list(clients.iterdir())
    if len(browser_entries)>100 or len(client_entries)>100:
        raise FixtureBoundaryError("fixture entry count limit")
    installed=[]
    for p in sorted(browser_entries):
        if not safe_ident(p.name) or p.is_symlink() or not p.is_dir():
            raise FixtureBoundaryError("unknown/symlink synthetic browser entry")
        if p.resolve(strict=True).parent != browsers:
            raise FixtureBoundaryError("browser child escaped fixture")
        installed.append(p.name)
    mapping={}
    for p in sorted(client_entries):
        if (not p.name.endswith(".json") or not safe_ident(p.stem)
                or p.is_symlink() or not p.is_file()
                or p.resolve(strict=True).parent!=clients
                or p.stat().st_size>8192):
            raise FixtureBoundaryError("malformed fixture client file")
        try:
            obj=json.loads(p.read_text(encoding="utf8"))
        except (ValueError,UnicodeError) as e:
            raise FixtureBoundaryError("invalid JSON in fixture") from e
        if not isinstance(obj,dict) or set(obj)!={"client_id","requires"} or obj["client_id"]!=p.stem:
            raise FixtureBoundaryError("untrusted synthetic manifest structure")
        if not isinstance(obj["requires"],list) or any(not isinstance(x,str) for x in obj["requires"]):
            raise FixtureBoundaryError("invalid synthetic client requires")
        if not set(obj["requires"]).issubset(installed):
            raise FixtureBoundaryError("missing browser version referenced by synthetic client")
        mapping[obj["client_id"]]=obj["requires"]
    graph={"schema":"maclean-fixture-graph-v0.4","synthetic":True,
           "complete_client_universe":True,"installed_browsers":installed,"clients":mapping}
    validate_graph(graph)
    refs=set().union(*(set(v) for v in mapping.values())) if mapping else set()
    graph["synthetic_orphan_ids"]=sorted(set(installed)-refs)
    return graph

@contextmanager
def disposable_fixture():
    with tempfile.TemporaryDirectory(prefix=PREFIX) as raw:
        root=pathlib.Path(raw).resolve()
        root.chmod(0o700)
        (root/MARKER).write_text("synthetic-no-user-data\n")
        (root/"browsers").mkdir(mode=0o700)
        (root/"clients").mkdir(mode=0o700)
        for version in ("chrome-0999","chrome-1111","firefox-1542"):
            (root/"browsers"/version).mkdir(mode=0o700)
        (root/"clients"/"web-research.json").write_text(
            json.dumps({"client_id":"web-research","requires":["chrome-1111"]}))
        (root/"clients"/"qa-suite.json").write_text(
            json.dumps({"client_id":"qa-suite","requires":["chrome-1111","firefox-1542"]}))
        yield root

def demo():
    from operation_registry import assess
    with disposable_fixture() as fixture:
        graph=collect(fixture)
        # No file is removed by either research preview.
        previews={
            "targeted_orphan":assess("puppeteer.browsers.uninstall_build",graph,["chrome-0999"],target="chrome-0999"),
            "broad_clear":assess("puppeteer.browsers.clear_all",graph,["chrome-0999"]),
            "referenced_uninstall":assess("puppeteer.browsers.uninstall_build",graph,["chrome-1111"],target="chrome-1111"),
            "playwright_unused_gc":assess("playwright.browsers.gc_unused",graph,["chrome-0999"]),
        }
        return {"synthetic_only":True,"graph":graph,"previews":previews,
                "no_real_cache_read":True,"no_files_deleted":True}

if __name__=="__main__":
    print(json.dumps(demo(),ensure_ascii=False,indent=2))
