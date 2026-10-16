from pathlib import Path
import hashlib,zipfile,json
r=Path(__file__).resolve().parents[1]; h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=r/"artifacts/macos-disk-auditor-v1.3.0.zip"
assert h(old)=="4dc20c4a33b57ee6a0bc76296042cd97834a5d21be6afd6d8450bda47bdf3a09"
new=r/"artifacts/macos-disk-auditor-v1.3.1.zip"; m=json.loads((r/"skill/macos-disk-auditor/manifest.json").read_text())
assert m["version"]=="1.3.1" and len(m["files"])==17
with zipfile.ZipFile(new) as z:
 assert z.testzip() is None
 names={s for s in z.namelist() if not s.endswith("/")}
 assert names=={"macos-disk-auditor/"+x for x in m["files"]}|{"macos-disk-auditor/manifest.json"}
 for n in names: assert hashlib.sha256(z.read(n)).hexdigest()==h(r/"skill"/n)
for n,v in m["files"].items():assert h(r/"skill/macos-disk-auditor"/n)==v
lines=(r/"artifacts/SHA256SUMS.txt").read_text().splitlines()
assert lines==[f"{h(old)}  {old.name}",f"{h(new)}  {new.name}"]
print(json.dumps({"ok":True,"version":"1.3.1","checked":len(m["files"]),"zip_sha256":h(new),"manifest_sha256":h(r/"skill/macos-disk-auditor/manifest.json")}))
