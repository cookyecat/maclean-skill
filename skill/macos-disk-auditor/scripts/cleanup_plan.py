#!/usr/bin/env python3
"""Conservative, user-approved macOS Home cleanup. Default is read-only.

v1.1 supports narrow, explicitly classified Home cache/build targets while
retaining v1 Library targets. NO sudo, no automatic cleanup, no shell deletion.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
from privacy_policy import protected_cleanup_target, PolicyDenied, app_catalog_entry

LIBRARY_KINDS = {"cache", "log", "updater", "downloaded_runtime", "preload", "old_version", "agent_reviewed_cache", "app_cache", "app_log", "app_update", "profile_cache"}
HOME_KINDS = {"npm_cache", "npx_install", "uv_cache", "puppeteer_cache",
              "codex_runtime_installer", "codex_daemon_old", "cargo_target"}
KINDS = LIBRARY_KINDS | HOME_KINDS
GUARDS = {
    "Cursor": r"/Applications/Cursor\.app/|Cursor Helper(?:\s*\(|\b)|/cursor-agent(?:\s|$)|/cursor-agent-worker(?:\s|$)",
    "VS Code": r"/Applications/Visual Studio Code\.app/|Code Helper\s*\(",
    "Chrome": r"/Applications/Google Chrome\.app/",
    "Playwright": r"/ms-playwright/(?:chromium|firefox|webkit)|chromium_headless_shell|chrome-headless-shell",
    "Puppeteer": r"/\.cache/puppeteer/|puppeteer(?:-core)?/|chrome-headless-shell",
    "Feishu": r"/Applications/(?:Lark|Feishu|飞书)\.app/",
    "Steam": r"/Applications/Steam\.app/|/steam_osx(?:\s|$)",
    "BambuStudio": r"/Applications/(?:BambuStudio|Bambu Studio)\.app/",
    "NetEase": r"/Applications/(?:NeteaseMusic|NetEase Music|网易云音乐)\.app/",
    "Xmind": r"/Applications/[Xx][Mm]ind\.app/",
    "BaiduNetdisk": r"/Applications/(?:BaiduNetdisk|百度网盘)\.app/",
    "Youku": r"/Applications/(?:Youku|优酷)\.app/",
    "TencentVideo": r"/Applications/(?:TencentVideo|腾讯视频)\.app/",
    "Xueersi": r"/Applications/(?:学而思|Xes)\.app/",
    "Npm": r"(?:/npm-cli\.js|/npx-cli\.js|\bnpm (?:install|ci|exec|cache)|\bnpx\s)",
    "Uv": r"(?:^|[/\s])uv (?:run|pip|sync|cache|venv|build|tool)\b",
    "Codex": r"(?:/codex(?:\s|$)|/app-server-daemon/|codex-app-server|/Codex\.app/)",
    "Cargo": r"(?:^|[/\s])(?:cargo|rustc|maturin)\s|(?:/target/(?:debug|release)/)",
}
BLOCK_PARTS = {
    ".git", "keychains", "messages", "mail", "photos", "db_storage", "nt_db",
    "snapshots", "history", "bookmarks", "cookies", "indexeddb", "local storage",
    "settings.json", "state.vscdb", "state.vscdb.backup", "user data", "system data",
    "mobile documents", "cloudstorage", "session", "sessions", "workspacestorage",
    "thread_history_1.sqlite", "logs_2.sqlite", "state_5.sqlite", "storage.json",
}
BAD_BASENAMES = {
    "application support", "containers", "group containers", "library", "caches",
    "user", "users", "documents", "globalstorage", "default", "versions",
    "plugins", "extensions", "browser", "userdata", "data", "worktrees",
}
NAMES_TO_KEEP = {".git", "pyvenv.cfg", "cargo.toml", "cargo.lock", "package.json"}
SPECIFIC_GUARDS = {
    "old_version": {"Cursor"}, "downloaded_runtime": {"Playwright"},
    "npm_cache": {"Npm"}, "npx_install": {"Npm"},
    "uv_cache": {"Uv"}, "puppeteer_cache": {"Puppeteer"},
    "codex_runtime_installer": {"Codex"}, "codex_daemon_old": {"Codex"},
    "cargo_target": {"Cargo"},
}


def reject(msg):
    raise ValueError(msg)


def run(argv, **kw):
    return subprocess.run(argv, text=True, capture_output=True, **kw)


def read_plan(path):
    obj = json.loads(path.expanduser().read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or obj.get("schema_version") not in (1, 2, 3):
        reject("Plan needs schema_version 1, 2 or 3")
    if type(obj.get("user_approved")) is not bool:
        reject("Plan requires an explicit user_approved boolean")
    if not isinstance(obj.get("targets"), list) or not 1 <= len(obj["targets"]) <= 80:
        reject("Plan requires 1–80 individually reviewed targets")
    return obj


def parse_literal(raw, home):
    if not isinstance(raw, str) or not raw.startswith("~/"):
        reject("Use an exact ~/... literal path; absolute paths and arbitrary roots are forbidden")
    tail = raw[2:]
    if (not tail or tail.startswith("/") or "//" in tail or any(ch in raw for ch in "*?[]\r\n\0")):
        reject(f"Non-literal path: {raw}")
    parts = tail.split("/")
    if any(p in ("", ".", "..") for p in parts) or any("\\" in p for p in parts):
        reject(f"Traversal or invalid path: {raw}")
    if home.is_symlink():
        reject("HOME is symlinked; manual review required")
    path = home
    for part in parts:
        path = path / part
        if path.is_symlink():
            reject(f"Symlink component forbidden: {path}")
    if not path.resolve().is_relative_to(home.resolve()):
        reject(f"Outside HOME: {raw}")
    return path, parts


def validate_library(kind, path, parts, guards):
    if len(parts) < 3 or parts[0] != "Library":
        reject("Library cleanup targets require a narrow ~/Library/... leaf")
    rel = parts[1:]
    lower = [p.casefold() for p in rel]
    if rel[-1].casefold() in BAD_BASENAMES or any(p in BLOCK_PARTS for p in lower):
        reject("Protected or overly broad Library state: " + str(path))
    name = rel[-1].casefold()
    if kind == "cache" and not ("cache" in name or name == "appcache"):
        reject("Library cache target must be a cache-named leaf")
    if kind == "log" and not (name.startswith("log") or name.endswith(".log")):
        reject("Library log target must be a log-named leaf")
    if kind == "updater" and not ("updat" in name or name.endswith((".dmg", ".zip"))):
        reject("Library updater target must be an updater or update archive leaf")
    if kind == "downloaded_runtime" and parts != ["Library", "Caches", "ms-playwright"]:
        reject("Recognized library downloaded_runtime is ~/Library/Caches/ms-playwright only")
    if kind == "preload" and name != "preload":
        reject("Library preload target must be a preload leaf")
    if kind == "agent_reviewed_cache":
        # AI selects the exact cache target and explains why. The executor
        # only enforces technical guardrails, NOT algorithmic reclaimability.
        if len(parts) != 3 or parts[:2] != ["Library", "Caches"] or not name or name in BAD_BASENAMES:
            reject("AI-reviewed cache must be one exact Library/Caches/<app> leaf")
    if kind in ('app_cache','app_log','app_update','profile_cache'):
        meta=app_catalog_entry('/'.join(parts))
        if meta is None or meta['kind'] != kind:
            reject('Application cleanup target must match exact catalog entry')
        if meta['guard'] not in guards:
            reject('Missing catalog app activity guard')
    if kind == "old_version":
        prefix = ["Library", "Application Support", "Cursor", "User", "globalStorage",
                  "anysphere.cursor-agent-worker", "agent-cli", ".local", "share", "cursor-agent", "versions"]
        if parts[:-1] != prefix or not re.fullmatch(r"20\d\d\.\d\d\.\d\d[-_][A-Za-z0-9-]+", parts[-1]):
            reject("old_version requires an exact, dated Cursor Agent build within its versions folder")
    if kind not in LIBRARY_KINDS:
        reject("Non-Library kind inside Library")


def git_repo_check(path):
    project = path.parent
    if not (project / "Cargo.toml").is_file():
        reject(f"Cargo.toml missing beside target: {project}")
    chk = run(["git", "-C", str(project), "rev-parse", "--show-toplevel"])
    if chk.returncode or Path(chk.stdout.strip()).resolve() != project.resolve():
        reject("Cargo target must be directly inside an existing Git checkout/worktree root")
    chk = run(["git", "-C", str(project), "check-ignore", "--quiet", "--no-index", "target"])
    if chk.returncode != 0:
        reject("Cargo target must be ignored by git before cleanup")
    tracked = run(["git", "-C", str(project), "ls-files", "--cached", "--", "target"])
    if tracked.returncode or tracked.stdout.strip():
        reject("Cargo target contains tracked paths; cannot delete")
    status = run(["git", "-C", str(project), "status", "--porcelain=v1", "--untracked-files=normal"])
    if status.returncode or status.stdout.strip():
        reject("Git checkout has changes/untracked files; require clean worktree before cleaning build output")
    if path.exists() and not any((path / x).exists() for x in ("debug", "release", ".rustc_info.json")):
        reject("target lacks recognizable Cargo build structure")


def validate_home_kind(kind, path, parts):
    name = parts[-1]
    if kind == "npm_cache" and parts == [".npm", "_cacache"]:
        return
    if kind == "npx_install" and len(parts) == 3 and parts[:2] == [".npm", "_npx"] and re.fullmatch(r"[0-9a-f]{8,40}", name):
        return
    if kind == "uv_cache" and parts == [".cache", "uv"]:
        return
    if kind == "puppeteer_cache" and parts == [".cache", "puppeteer"]:
        return
    if kind == "codex_runtime_installer" and len(parts) == 3 and parts[:2] == [".cache", "codex-runtimes"] and re.fullmatch(r"codex-runtime-install-[A-Za-z0-9_-]{4,40}", name):
        # Newly created installers might be mid-install; keep anything < 7 days old.
        if path.exists() and __import__("time").time() - path.stat().st_mtime < 7 * 86400:
            reject("Codex runtime installer directory is newer than 7 days")
        return
    if kind == "codex_daemon_old" and len(parts) == 5 and parts[:4] == [".codex", "packages", "app-server-daemon", "releases"] and re.fullmatch(r"\d+\.\d+\.\d+(?:-[A-Za-z0-9._-]+)?", name):
        current = path.parent.parent / "current"
        if not current.is_symlink():
            reject("Cannot identify current Codex daemon; no versions may be removed")
        if path == current.resolve():
            reject("Never remove current Codex daemon")
        builds = sorted((p for p in path.parent.iterdir() if p.is_dir() and not p.is_symlink()),
                        key=lambda p: (version_sort_key(p.name), p.name), reverse=True)
        if path in builds[:2]:
            reject("Preserving two newest Codex daemon builds for current/fallback safety")
        return
    if kind == "cargo_target" and len(parts) >= 4 and name == "target":
        # Reviewable project roots only: ~/Developer/<project>/target or ~/... registered Codex worktree.
        acceptable = (parts[0] == "Developer" and len(parts) <= 8) or (
            len(parts) == 5 and parts[:2] == [".codex", "worktrees"])
        if not acceptable:
            reject("Cargo targets allowed only in reviewed Developer or Codex worktree project roots")
        git_repo_check(path)
        return
    reject(f"No allowlisted Home cleanup rule for {kind}: {path}")


def version_sort_key(name):
    nums = re.match(r"^(\d+)\.(\d+)\.(\d+)", name)
    return tuple(map(int, nums.groups())) if nums else (0, 0, 0)


def resolve_target(entry, home):
    if not isinstance(entry, dict):
        reject("Plan target must be an object")
    raw, kind = entry.get("path"), entry.get("kind")
    reason, guards = entry.get("reason"), entry.get("requires_quit")
    if kind not in KINDS:
        reject(f"Unsupported kind: {kind}")
    if not isinstance(reason, str) or len(reason.strip()) < 12:
        reject("Each target needs a detailed explanation (at least 12 characters)")
    if not isinstance(guards, list) or not guards or any(g not in GUARDS for g in guards):
        reject(f"Specify nonempty known requires_quit guards for {raw}")
    if kind in SPECIFIC_GUARDS and not SPECIFIC_GUARDS[kind].issubset(set(guards)):
        reject(f"Missing required process guard(s) for {kind}: {SPECIFIC_GUARDS[kind]}")
    path, parts = parse_literal(raw, home)
    protected_cleanup_target(home, path)  # hard privacy veto, independent of AI approval
    if kind in LIBRARY_KINDS:
        validate_library(kind, path, parts, guards)
    else:
        validate_home_kind(kind, path, parts)
    if kind == "old_version" and path.parent.is_dir():
        builds = sorted((p for p in path.parent.iterdir() if p.is_dir() and not p.is_symlink()
                        and re.fullmatch(r"20\d\d\.\d\d\.\d\d[-_][A-Za-z0-9-]+", p.name)),
                        key=lambda p: p.name, reverse=True)
        if path in builds[:2]:
            reject("Never delete two newest dated Cursor Agent builds")
    return path


def disk_kib(path):
    p = run(["du", "-sk", str(path)])
    if p.returncode or not p.stdout:
        reject(f"Cannot measure {path}: {p.stderr.strip()}")
    return int(p.stdout.split()[0])


def running(guards, target=None):
    p = run(["ps", "-axo", "pid=,command="])
    if p.returncode:
        reject("Cannot inspect processes; refusing cleanup")
    matches = {}
    for row in p.stdout.splitlines():
        bits = row.strip().split(None, 1)
        if len(bits) != 2 or not bits[0].isdigit():
            continue
        pid, cmd = int(bits[0]), bits[1]
        if pid in (os.getpid(), os.getppid()):
            continue
        if target is not None and str(target) in cmd:
            matches.setdefault("target in process command", set()).add(pid)
        for name in guards:
            if re.search(GUARDS[name], cmd, flags=re.IGNORECASE):
                matches.setdefault(name, set()).add(pid)
    return matches


def check_target_type(path):
    mode = path.lstat().st_mode
    if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
        reject(f"Only ordinary files/directories are supported: {path}")
    return (path.lstat().st_dev, path.lstat().st_ino)


def terminal_confirm():
    # Read directly from the controlling TTY, NOT stdin (could contain script source).
    fd = os.open("/dev/tty", os.O_RDWR | os.O_NOCTTY)
    try:
        os.write(fd, b"Type DELETE to permanently delete the EXACT approved targets: ")
        answer = bytearray()
        while len(answer) < 64:
            part = os.read(fd, 64-len(answer))
            if not part:
                break
            answer.extend(part)
            if b"\n" in part or b"\r" in part:
                break
        return answer.decode(errors="replace").strip() == "DELETE"
    finally:
        os.close(fd)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--plan", required=True, type=Path)
    cli.add_argument("--apply", action="store_true")
    args = cli.parse_args()
    if os.geteuid() == 0:
        reject("Do not use sudo/root")
    home = Path.home()
    data = read_plan(args.plan)
    if data["schema_version"] == 1 and any(not x.get("path", "").startswith("~/Library/") for x in data["targets"]):
        reject("v1 plans may only target ~/Library; use schema_version: 2 for Home targets")
    selected = [(e, resolve_target(e, home)) for e in data["targets"]]
    paths = [str(p) for _, p in selected]
    if len(set(paths)) != len(paths):
        reject("Duplicate target in plan")
    if any(e["kind"] == "agent_reviewed_cache" for e, _ in selected):
        if data["schema_version"] != 3:
            reject("AI-reviewed cache requires schema v3")
        for e, _ in selected:
            if e["kind"] != "agent_reviewed_cache":
                continue
            analysis = e.get("ai_analysis")
            conditions = e.get("conditions")
            if not isinstance(analysis, str) or len(analysis.strip()) < 25 or not isinstance(conditions, list) or not conditions or not all(isinstance(c, str) and c.strip() for c in conditions):
                reject("AI-reviewed target requires written AI analysis and explicit conditions")
    for i, left in enumerate(paths):
        for right in paths[i+1:]:
            if left.startswith(right + os.sep) or right.startswith(left + os.sep):
                reject("Nested paths may not appear in the same plan")
    print("macOS HOME cleanup | " + ("APPLY" if args.apply else "PREVIEW / READ-ONLY"), flush=True)
    print(f"Home: {home}\nPlan user_approved: {data['user_approved']}")
    present, total = [], 0
    for entry, path in selected:
        if not path.exists() and not path.is_symlink():
            print("[ABSENT] " + entry["path"])
            continue
        identity = check_target_type(path)
        size = disk_kib(path)
        present.append((entry, path, size, identity))
        total += size
        print(f"[{size/1024:9.1f} MiB] {entry['kind']:23} {entry['path']}\n    {entry['reason']}")
    print(f"\nPresent: {len(present)} | Absent: {len(selected)-len(present)} | Measured: {total/1048576:.2f} GiB", flush=True)
    if not args.apply:
        print("PREVIEW ONLY; NO FILES MODIFIED.")
        return 0
    if not data["user_approved"]:
        reject("Plan not user-approved; refusing deletion")
    if not present:
        print("No targets to delete")
        return 0
    allguards = set(g for entry, _, _, _ in present for g in entry["requires_quit"])
    active = running(allguards)
    if active:
        for name, pids in sorted(active.items()):
            print(f"STOP: {name}: PID {', '.join(map(str, sorted(pids)))}")
        reject("Relevant apps/processes still running; nothing deleted")
    # Check explicit target usage (e.g., current npx package or daemon build).
    for entry, path, _, _ in present:
        used = running([], path)
        if used:
            reject(f"Target is referenced in running command: {entry['path']} {used}")
    print("WARNING: deletion is PERMANENT; some downloads may be needed again.", flush=True)
    try:
        answer = terminal_confirm()
    except OSError as exc:
        reject(f"No interactive terminal; no deletion ({exc})")
    if not answer:
        print("CANCELLED: no files deleted")
        return 1
    free_before = shutil.disk_usage(home).free
    failures, deleted = [], 0
    for entry, original, size, identity in present:
        try:
            path = resolve_target(entry, home)
            if path != original or not path.exists() or check_target_type(path) != identity:
                raise RuntimeError("Path identity changed after preview")
            if running(entry["requires_quit"], path):
                raise RuntimeError("Application or referenced target became active")
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            if path.exists() or path.is_symlink():
                raise RuntimeError("Deletion incomplete")
            deleted += size
            print(f"[DELETED {size/1024:9.1f} MiB] {entry['path']}", flush=True)
        except (Exception,) as exc:
            failures.append((entry["path"], str(exc)))
            print(f"[FAILED] {entry['path']}: {exc}", flush=True)
    free_after = shutil.disk_usage(home).free
    print(f"\nRESULT: {deleted/1048576:.2f} GiB measured targets deleted, {len(failures)} failed")
    print(f"Free before: {free_before/2**30:.2f} GiB | after: {free_after/2**30:.2f} GiB | net: {(free_after-free_before)/2**30:+.2f} GiB")
    print("APFS clones, hardlinks, snapshots and concurrent writes can change net free space.")
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, json.JSONDecodeError) as err:
        print("ERROR:", err, file=sys.stderr)
        raise SystemExit(2)
