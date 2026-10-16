#!/usr/bin/env python3
"""MacLean v0.6 - disposable-only browser identity and client reference evidence.

Never accepts a user cache path. Requires pinned CLI package tree already held
inside a private maclean-v05-native-e2.* Mac test directory. Only native
read-only Playwright list is invoked against a freshly created disposable cache.
All raw paths and metadata remain local; output is aggregate and anonymized.
"""
from __future__ import annotations
import contextlib, hashlib, json, os, pathlib, shutil, stat, subprocess, tempfile

def bounded_root(path:pathlib.Path) -> pathlib.Path:
    if path.is_symlink() or not path.name.startswith("maclean-v05-native-e2."):
        raise ValueError("not pinned disposable package root")
    q=path.resolve(strict=True)
    if q.parent != pathlib.Path("/private/tmp") or q.stat().st_mode & 0o077:
        raise ValueError("unsafe package-root ownership or scope")
    for name,want in (("playwright-core","1.64.1"),("@puppeteer/browsers","3.2.5")):
        file=q/"pkg/node_modules"/name/"package.json"
        if file.is_symlink() or not file.is_file():
            raise ValueError("missing pinned package")
        if json.loads(file.read_text())["version"]!=want:
            raise ValueError("mismatched pinned package")
    return q

def bounded_file(root:pathlib.Path, relative:str) -> dict:
    """Lstat every synthetic component; simple synthetic mode is NOT browser authenticity."""
    # Never even lstat a user-supplied root; this function is fixture-only.
    allowed_parents={pathlib.Path("/private/tmp"),pathlib.Path(tempfile.gettempdir()).resolve()}
    outer=(root.parent if root.name=="browser-cache" else root)
    valid=(outer.name.startswith("maclean-v06-") and outer.parent in allowed_parents
           and (root==outer or (outer.name.startswith("maclean-v06-trust-fixture-")
                                and root.parent==outer and root.name=="browser-cache")))
    if (not valid or root.is_symlink() or outer.is_symlink() or not root.is_dir()
            or not outer.is_dir() or root.stat().st_mode & 0o077
            or outer.stat().st_mode & 0o077):
        return {"status":"OUTSIDE_DISPOSABLE_FIXTURE_DENIED"}
    if not relative or len(relative)>240:return {"status":"INVALID_RELATIVE"}
    parts=pathlib.PurePosixPath(relative).parts
    if any(part in (".","..","") for part in parts) or relative.startswith("/"):
        return {"status":"INVALID_RELATIVE"}
    cur=root
    for piece in parts:
        cur=cur/piece
        try: st=cur.lstat()
        except FileNotFoundError:return {"status":"MISSING"}
        if stat.S_ISLNK(st.st_mode):return {"status":"SYMLINK_DENIED"}
    if not stat.S_ISREG(st.st_mode):return {"status":"NOT_REGULAR"}
    if st.st_mode & 0o111 == 0:return {"status":"NOT_EXECUTABLE"}
    # Avoid confusing a fixture stub with an authenticated browser.
    return {"status":"EXECUTABLE_MODE_ONLY","authentic_browser":False,
            "safe_to_delete":False}

def run_lab(package_root:pathlib.Path) -> dict:
    package=bounded_root(package_root)
    with tempfile.TemporaryDirectory(prefix="maclean-v06-trust-fixture-") as tmp:
        root=pathlib.Path(tmp).resolve()
        root.chmod(0o700)
        reg=root/"browser-cache"
        reg.mkdir(mode=0o700)
        links=reg/".links"
        links.mkdir(mode=0o700)
        cli=package/"pkg/node_modules/playwright-core/cli.js"
        original_manifest=package/"pkg/node_modules/playwright-core/browsers.json"
        client=root/"test-client"
        client.mkdir(mode=0o700)
        # Copy only the known, pinned PUBLISHER metadata from previous isolated package.
        shutil.copyfile(original_manifest,client/"browsers.json")
        shutil.copyfile(package/"pkg/node_modules/playwright-core/package.json",client/"package.json")
        (links/"fixture-client").write_text(str(client))
        (reg/"chromium-1248").mkdir(mode=0o700)
        # This fixture is intentionally phony; no Chrome browser was downloaded.
        env={"PATH":os.environ.get("PATH","/usr/bin:/bin"),
             "HOME":str(root),"PLAYWRIGHT_BROWSERS_PATH":str(reg),
             "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD":"1","PUPPETEER_SKIP_DOWNLOAD":"true",
             "NO_PROXY":"*","HTTP_PROXY":"","HTTPS_PROXY":""}
        result=subprocess.run([shutil.which("node"),str(cli),"install","--list"],
                 cwd=root,env=env,stdin=subprocess.DEVNULL,
                 capture_output=True,text=True,timeout=15)
        raw=result.stdout+result.stderr
        # Real CLI can traverse .links->client/browsers.json! Keep all paths private.
        exposed_metadata_path=str(client) in raw
        relative="chromium-1248/chrome-mac/Chromium.app/Contents/MacOS/Chromium"
        absent=bounded_file(reg,relative)
        synthetic_bin=reg/"browser-mode-fixture"
        synthetic_bin.write_bytes(b"synthetic-not-real-browser")
        not_executable=bounded_file(reg,"browser-mode-fixture")
        synthetic_bin.chmod(0o700)
        mode_executable=bounded_file(reg,"browser-mode-fixture")
        symlink=reg/"browser-symlink"
        symlink.symlink_to(synthetic_bin)
        denied=bounded_file(reg,"browser-symlink")
        malformed=bounded_file(reg,"../test-client/browsers.json")
        # Source-level client reference census: explicitly limited to known fixture.
        links_entries=list(links.iterdir())
        census=[]
        for link in links_entries:
            if link.is_symlink() or not link.is_file() or link.stat().st_size>1024:
                raise ValueError("untrusted fixture link")
            destination=pathlib.Path(link.read_text())
            if destination!=client:
                raise ValueError("link outside known synthetic client")
            b=destination/"browsers.json"
            if b.is_symlink() or not b.is_file() or b.stat().st_size>64_000:
                raise ValueError("client metadata unavailable")
            parsed=json.loads(b.read_text())
            census.append({"client_reference_present":True,
                           "publisher_browser_manifest":isinstance(parsed.get("browsers"),list)})
        return {
            "schema":"maclean-v06-disposable-e2",
            "pinned_playwright_core":"1.64.1",
            "native_list_exit_code":result.returncode,
            "native_list_prints_client_path":exposed_metadata_path,
            "native_list_contains_chromium":("chromium" in result.stdout.lower()),
            "link_metadata_client_count":len(census),
            "links_are_plaintext_absolute_client_paths":True,
            "sandboxed_source_manifest_read":all(x["publisher_browser_manifest"] for x in census),
            "phony_browser_file":absent["status"],
            "synthetic_not_executable":not_executable["status"],
            "synthetic_mode_executable":mode_executable["status"],
            "symbolic_link":denied["status"],
            "path_escape":malformed["status"],
            "real_browser_integrity_verified":False,
            "real_client_universe_complete":False,
            "real_cache_read":False,"real_cache_deleted":False,
            "native_cleanup_executed":False,
            "deletion_authorized":False
        }

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--package-root",type=pathlib.Path,required=True)
    args=p.parse_args();print(json.dumps(run_lab(args.package_root),ensure_ascii=False))
