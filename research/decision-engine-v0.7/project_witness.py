#!/usr/bin/env python3
"""v0.7: EXACTLY-SELECTED fixture project metadata witness, never real Home."""
import hashlib,json,pathlib,re,tempfile
from contextlib import contextmanager
PREFIX="maclean-v07-fixture-"
ID=re.compile(r"client-[A-Za-z0-9_-]{1,32}\Z")
class ScopeDenied(ValueError):pass

def guarded_root(root):
    if not isinstance(root,pathlib.Path) or root.is_symlink() or not root.name.startswith(PREFIX):
        raise ScopeDenied("not a v0.7 synthetic fixture")
    real=root.resolve(strict=True)
    allowed={pathlib.Path(tempfile.gettempdir()).resolve(),pathlib.Path("/private/tmp")}
    if real.parent not in allowed or not real.is_dir() or real.stat().st_mode&0o077:
        raise ScopeDenied("not owner-private temporary root")
    m=real/".v07-synthetic-only"
    if m.is_symlink() or not m.is_file() or m.read_text()!="synthetic\n":
        raise ScopeDenied("invalid fixture marker")
    return real

def child(parent,name):
    p=parent/name
    if p.is_symlink() or not p.is_dir() or p.resolve(strict=True).parent!=parent:
        raise ScopeDenied("symlinked or missing client directory")
    return p

def bounded_json(folder,name):
    p=folder/name
    if p.is_symlink() or not p.is_file() or p.stat().st_size>65536:
        raise ScopeDenied("bad manifest path or excessive size")
    raw=p.read_bytes()
    if len(raw)>65536:raise ScopeDenied("excessive manifest data")
    try:data=json.loads(raw)
    except (ValueError,UnicodeError):raise ScopeDenied("bad manifest") from None
    if not isinstance(data,dict):raise ScopeDenied("bad publisher metadata")
    return data,hashlib.sha256(raw).hexdigest()

def scan(root,selected):
    root=guarded_root(root)
    if (not isinstance(selected,list) or not 1<=len(selected)<=16
            or len(set(selected))!=len(selected)
            or any(not isinstance(x,str) or not ID.fullmatch(x) for x in selected)):
        raise ScopeDenied("invalid exact client allowlist")
    projects=child(root,"projects")
    links=child(child(root,"registry"),".links")
    wanted={}
    for cid in selected:
        folder=child(child(child(projects,cid),"node_modules"),"playwright-core")
        wanted[str(folder)]=cid
    entries=list(links.iterdir())
    if len(entries)>32:raise ScopeDenied("too many client references")
    observed=set();unknown_count=0
    for f in entries:
        if (not re.fullmatch("[A-Za-z0-9_-]{1,48}",f.name)
                or f.is_symlink() or not f.is_file() or f.stat().st_size>512):
            raise ScopeDenied("untrusted link-file identity")
        raw=f.read_text()
        if any(x in raw for x in ("\n","\r","\x00")):
            raise ScopeDenied("malformed link-content")
        # Raw unknown target is NEVER stat'ed or resolved.
        cid=wanted.get(raw)
        if cid is None:unknown_count+=1;continue
        if cid in observed:raise ScopeDenied("duplicate client reference")
        observed.add(cid)
    refs={}
    for location,cid in sorted(wanted.items()):
        path=pathlib.Path(location)
        pkg,ph=bounded_json(path,"package.json")
        browsers,bh=bounded_json(path,"browsers.json")
        if not isinstance(pkg.get("version"),str) or not pkg["version"]:
            raise ScopeDenied("invalid package version")
        desc=browsers.get("browsers")
        if not isinstance(desc,list) or len(desc)>30:
            raise ScopeDenied("invalid browser manifest list")
        versions=[]
        for d in desc:
            if (not isinstance(d,dict)
                    or not isinstance(d.get("name"),str)
                    or not isinstance(d.get("revision"),str)
                    or not re.fullmatch("[A-Za-z0-9_-]{1,48}",d["name"])
                    or not re.fullmatch("[A-Za-z0-9_.-]{1,48}",d["revision"])):
                raise ScopeDenied("invalid browser descriptor")
            versions.append(d["name"]+"@"+d["revision"])
        refs[cid]={"present_in_native_links":cid in observed,
                   "package_version":pkg["version"],
                   "browser_revisions":sorted(set(versions)),
                   "package_sha256":ph,"browsers_sha256":bh}
    return {"schema":"maclean-project-witness-v0.7","fixture_only":True,
            "selected_client_ids":sorted(selected),"selected_client_count":len(selected),
            "selected_clients":refs,"total_link_entries":len(entries),
            "unknown_unread_link_targets":unknown_count,
            "coverage":"PARTIAL_REAL_HOST_UNPROVEN",
            "coverage_flags":(["UNKNOWN_CLIENT_REFERENCES"] if unknown_count else [])
                            +(["SELECTED_LINK_MISSING"] if len(observed)<len(selected) else [])
                            +["REAL_HOST_CLIENT_UNIVERSE_NOT_ENUMERATED"],
            "real_client_universe_complete":False,
            "unknown_link_target_dereferenced":False,
            "safe_to_clean":False,"deletion_authorized":False}
@contextmanager
def fixture(unselected=False):
    with tempfile.TemporaryDirectory(prefix=PREFIX) as d:
        root=pathlib.Path(d).resolve();root.chmod(0o700)
        (root/".v07-synthetic-only").write_text("synthetic\n")
        links=root/"registry"/".links";links.mkdir(parents=True)
        p=root/"projects"/"client-ALPHA"/"node_modules"/"playwright-core"
        p.mkdir(parents=True)
        (p/"package.json").write_text('{"name":"playwright-core","version":"1.64.1"}')
        (p/"browsers.json").write_text('{"browsers":[{"name":"chromium","revision":"1248"}]}')
        (links/"one").write_text(str(p))
        if unselected:(links/"other").write_text(str(pathlib.Path.home()/"another-unselected-project"))
        yield root
if __name__=="__main__":
    with fixture(True) as root:print(json.dumps(scan(root,["client-ALPHA"])))
