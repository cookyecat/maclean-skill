#!/usr/bin/env python3
"""Run real-mac regression with disposable HOME fixtures; never cleans real user data."""
import fcntl
import json
import os
from pathlib import Path
import pty
import shutil
import hashlib
import select
import subprocess
import sys
import tempfile
import termios
import time

BASE = Path(__file__).resolve().parent
TESTS = 0


def check(value, message):
    global TESTS
    assert value, message
    TESTS += 1
    print(f"PASS {TESTS:02d} {message}")


def execute(home, script, args):
    return subprocess.run([sys.executable, str(BASE / script), *args],
                          env={**os.environ, "HOME": str(home)}, text=True, capture_output=True)


def plan_file(home, targets, approved=False, schema=2):
    f = home / "plan.json"
    f.write_text(json.dumps({"schema_version": schema, "user_approved": approved, "targets": targets}))
    return f


def target(path, kind, guards):
    return {"path": path, "kind": kind, "reason": "Reviewed temporary synthetic cleanup fixture only", "requires_quit": guards}


def drain_pty(master, output, max_wait=0.3):
    """Drain a finished child PTY. macOS read() returns b'' on EOF while
    select() may continue reporting the fd readable indefinitely; Linux
    commonly raises EIO instead. Both mean EOF, never spin on either.
    """
    deadline = time.monotonic() + max_wait
    while time.monotonic() < deadline and select.select([master], [], [], 0)[0]:
        try:
            chunk = os.read(master, 16384)
        except OSError as exc:
            if exc.errno == 5:  # EIO: typical Linux PTY EOF
                break
            raise
        if not chunk:  # b'' on macOS: without this, loops at ~100% CPU
            break
        output.extend(chunk)


def test_pty_eof():
    """Exercise EOF handling even if a child PTY closes before any output."""
    master, slave = pty.openpty()
    os.close(slave)
    try:
        buffer = bytearray()
        started = time.monotonic()
        drain_pty(master, buffer, max_wait=0.5)
        check(time.monotonic() - started < 1.0,
              "Closed PTY EOF terminates output drain (macOS returns b'')")
    finally:
        os.close(master)

def interactive(home, plan, answer):
    master, slave = pty.openpty()
    def attach():
        os.setsid()
        fcntl.ioctl(slave, termios.TIOCSCTTY, 0)
    proc = subprocess.Popen([sys.executable, str(BASE / "cleanup_plan.py"), "--plan", str(plan), "--apply"],
                            env={**os.environ, "HOME": str(home)},
                            stdin=slave, stdout=slave, stderr=slave,
                            preexec_fn=attach, close_fds=True)
    os.close(slave)
    output = bytearray()
    sent = False
    try:
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline and proc.poll() is None:
            if select.select([master], [], [], .05)[0]:
                try:
                    chunk = os.read(master, 16384)
                    if not chunk:  # macOS EOF
                        break
                    output.extend(chunk)
                except OSError:
                    break
            if b"Type DELETE" in output and not sent:
                os.write(master, (answer + "\n").encode())
                sent = True
        proc.wait(timeout=3)
        drain_pty(master, output)
        return proc.returncode, sent, output.decode(errors="replace")
    finally:
        os.close(master)
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=3)


def make_file(path, content="disposable"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def main():
    if os.geteuid() == 0:
        raise RuntimeError("Run self_test.py as a normal user, not root")
    test_pty_eof()
    with tempfile.TemporaryDirectory(prefix="macos-disk-auditor-test-") as td:
        home = Path(td)
        db = home / "Library/Application Support/Cursor/User/globalStorage/state.vscdb"
        make_file(db, "MUST KEEP")
        cache = home / "Library/Application Support/BambuStudio/log/old.log"
        make_file(cache)
        log_entry = target("~/Library/Application Support/BambuStudio/log", "log", ["BambuStudio"])
        f = plan_file(home, [log_entry], approved=False, schema=1)
        r = execute(home, "cleanup_plan.py", ["--plan", str(f)])
        check(r.returncode == 0 and cache.exists() and "PREVIEW ONLY" in r.stdout, "Legacy v1 preview does not delete")
        r = execute(home, "cleanup_plan.py", ["--plan", str(f), "--apply"])
        check(r.returncode != 0 and cache.exists(), "Unapproved plan never deletes")
        f = plan_file(home, [target("~/Library/Application Support/Cursor/User/globalStorage/state.vscdb", "cache", ["Cursor"])], True)
        r = execute(home, "cleanup_plan.py", ["--plan", str(f)])
        check(r.returncode != 0 and db.read_text() == "MUST KEEP", "Cursor state database is protected")
        f = plan_file(home, [log_entry], True)
        code, sent, _ = interactive(home, f, "CANCEL")
        check(code != 0 and sent and cache.exists(), "TTY cancellation leaves data untouched")
        code, sent, out = interactive(home, f, "DELETE")
        check(code == 0 and sent and not cache.exists() and "DELETED" in out, "TTY DELETE removes exact authorized Library target")
        check(db.read_text() == "MUST KEEP", "Unrelated database remains intact")

        npm = home / ".npm/_cacache/index-v5/bucket"
        make_file(npm)
        ent = target("~/.npm/_cacache", "npm_cache", ["Npm"])
        f = plan_file(home, [ent], False)
        r = execute(home, "cleanup_plan.py", ["--plan", str(f)])
        check(r.returncode == 0 and npm.exists(), "Home npm cache is supported in read-only preview")
        r = execute(home, "cleanup_plan.py", ["--plan", str(f), "--apply"])
        check(r.returncode != 0 and npm.exists(), "Unapproved Home plan is rejected")
        f = plan_file(home, [ent], True)
        code, sent, out = interactive(home, f, "DELETE")
        if code == 0 and sent and not npm.exists():
            check(True, "Approved Home npm cache deleted via physical TTY (no active npm)")
        elif (code != 0 and not sent and npm.exists() and
              "STOP: Npm:" in out and "Relevant apps/processes still running" in out):
            # On a real Mac, Remote Desktop Commander itself can be launched
            # via `npm exec ... remote`. This is a *correct production refusal*.
            # Never disable the guard just to make a test pass.
            check(True, "Active host npm blocks synthetic npm deletion (fail closed)")
        else:
            raise AssertionError("npm physical TTY case failed unexpectedly: " + repr(out[-1800:]))


        uv = home / ".cache/uv/archive-v0/wheel"
        make_file(uv)
        f = plan_file(home, [target("~/.cache/uv", "uv_cache", ["Uv"])], True)
        r = execute(home, "cleanup_plan.py", ["--plan", str(f)])
        check(r.returncode == 0 and uv.exists(), "UV preview supports Home cache")
        code, sent, out = interactive(home, f, "DELETE")
        if code == 0 and sent and not uv.exists():
            check(True, "UV cache cleaned after consent when uv is idle")
        elif (code != 0 and not sent and uv.exists() and
              "STOP: Uv:" in out and "Relevant apps/processes still running" in out):
            check(True, "Active host uv blocks synthetic cache deletion (fail closed)")
        else:
            raise AssertionError("uv physical TTY case failed unexpectedly: " + repr(out[-1800:]))


        secret = home / ".codex/thread_history_1.sqlite"
        make_file(secret, "history")
        protected = [target("~/.codex/thread_history_1.sqlite", "npm_cache", ["Npm"]),
                     target("~/.codex/worktrees", "cargo_target", ["Cargo"]),
                     target("~/Developer/project/.git", "cargo_target", ["Cargo"]),
                     target("~/.npm", "npm_cache", ["Npm"]),
                     target("~/Library/Containers", "cache", ["Cursor"]),
                     target("~/Library/Application Support/Cursor/snapshots", "cache", ["Cursor"]),
                     target("~/../../etc", "npm_cache", ["Npm"])]
        for p in protected:
            f = plan_file(home, [p], True)
            r = execute(home, "cleanup_plan.py", ["--plan", str(f)])
            check(r.returncode != 0, "Protected/invalid path rejected: " + p["path"])
        check(secret.read_text() == "history", "Codex history database preserved")

        link_target = home / ".cache/uv"
        (home / ".cache").mkdir(exist_ok=True)
        link_target.symlink_to(home / "Library", target_is_directory=True)
        f = plan_file(home, [target("~/.cache/uv", "uv_cache", ["Uv"])], True)
        r = execute(home, "cleanup_plan.py", ["--plan", str(f)])
        check(r.returncode != 0 and link_target.is_symlink(), "Symlink substitution rejected")
        link_target.unlink()

        # Deterministic process-guard integration: spawn ONLY a disposable test
        # child whose command line includes `npm exec`. Never stop host processes.
        controlled = home / ".npm/_cacache/protected-by-process"
        make_file(controlled)
        blocked_plan = plan_file(home, [target("~/.npm/_cacache", "npm_cache", ["Npm"])], True)
        synthetic_npm = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(15)",
                                          "npm exec synthetic-guard-fixture"],
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            # Wait for child to be visible in the OS process table before test.
            time.sleep(0.07)
            code, sent, out = interactive(home, blocked_plan, "DELETE")
            check(code != 0 and not sent and controlled.exists() and
                  "STOP: Npm:" in out and str(synthetic_npm.pid) in out,
                  "Synthetic active npm PID blocks even explicitly approved cleanup")
        finally:
            if synthetic_npm.poll() is None:
                synthetic_npm.terminate()  # only the self-test's own child
                try:
                    synthetic_npm.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    synthetic_npm.kill()
                    synthetic_npm.wait(timeout=2)

        a = home / ".npm/_cacache"
        b = home / ".npm/_npx/4b4c857f6efdfb61"
        make_file(a / "file")
        make_file(b / "package.json")
        f = plan_file(home, [target("~/.npm/_npx/4b4c857f6efdfb61", "npx_install", ["Npm"])], False)
        r = execute(home, "cleanup_plan.py", ["--plan", str(f)])
        check(r.returncode == 0 and b.exists(), "npx individual cache supported, root _npx not supported")
        f = plan_file(home, [target("~/.npm/_npx", "npx_install", ["Npm"])], False)
        r = execute(home, "cleanup_plan.py", ["--plan", str(f)])
        check(r.returncode != 0, "Whole _npx directory rejected")

        codex = home / ".codex/packages/app-server-daemon/releases"
        for ver in ["0.159.3-aarch64-apple-darwin", "0.160.0-aarch64-apple-darwin", "0.160.1-aarch64-apple-darwin"]:
            make_file(codex / ver / "daemon")
        (codex.parent / "current").symlink_to(codex / "0.160.1-aarch64-apple-darwin", target_is_directory=True)
        f = plan_file(home, [target("~/.codex/packages/app-server-daemon/releases/0.160.1-aarch64-apple-darwin", "codex_daemon_old", ["Codex"])], False)
        r = execute(home, "cleanup_plan.py", ["--plan", str(f)])
        check(r.returncode != 0, "Currently linked Codex daemon cannot be removed")
        f = plan_file(home, [target("~/.codex/packages/app-server-daemon/releases/0.160.0-aarch64-apple-darwin", "codex_daemon_old", ["Codex"])], False)
        r = execute(home, "cleanup_plan.py", ["--plan", str(f)])
        check(r.returncode != 0, "Codex fallback daemon cannot be removed")
        f = plan_file(home, [target("~/.codex/packages/app-server-daemon/releases/0.159.3-aarch64-apple-darwin", "codex_daemon_old", ["Codex"])], False)
        r = execute(home, "cleanup_plan.py", ["--plan", str(f)])
        check(r.returncode == 0, "Older Codex daemon can be previewed safely")

        project = home / ".codex/worktrees/testbranch/star-main"
        project.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(project)], check=True, stdout=subprocess.DEVNULL)
        make_file(project / "Cargo.toml", "[package]\nname='test'\nversion='0.1.0'\nedition='2021'\n")
        make_file(project / ".gitignore", "target/\n")
        subprocess.run(["git", "-C", str(project), "add", "Cargo.toml", ".gitignore"], check=True)
        subprocess.run(["git", "-C", str(project), "-c", "user.email=test@example.org",
                        "-c", "user.name=Test", "commit", "-qm", "fixture"], check=True)
        target_build = project / "target/debug/.rustc_info.json"
        make_file(target_build)
        cargo_plan = plan_file(home, [target("~/.codex/worktrees/testbranch/star-main/target", "cargo_target", ["Cargo"])], True)
        r = execute(home, "cleanup_plan.py", ["--plan", str(cargo_plan)])
        check(r.returncode == 0 and target_build.exists(), "Cargo target preview only for ignored clean Git checkout")
        make_file(project / "valuable-untracked.txt")
        r = execute(home, "cleanup_plan.py", ["--plan", str(cargo_plan)])
        check(r.returncode != 0 and target_build.exists(), "Cargo worktree with untracked files is protected")
        (project / "valuable-untracked.txt").unlink()
        code, sent, out = interactive(home, cargo_plan, "CANCEL")
        cancelled = code != 0 and sent and target_build.exists()
        blocked = (code != 0 and not sent and target_build.exists() and
                   "STOP: Cargo:" in out and "Relevant apps/processes still running" in out)
        check(cancelled or blocked, "Cargo cancellation or active-build guard preserves build data")
        code, sent, out = interactive(home, cargo_plan, "DELETE")
        deleted = code == 0 and sent and not target_build.exists() and (project / "Cargo.toml").exists()
        blocked = (code != 0 and not sent and target_build.exists() and
                   "STOP: Cargo:" in out and "Relevant apps/processes still running" in out)
        check(deleted or blocked, "Cargo synthetic target: approved delete or fail-closed active-build guard")
        if not (deleted or blocked):
            raise AssertionError("cargo physical TTY case failed: " + repr(out[-1800:]))

        # Privacy-safe scan: no parent-directory du, no private-file reads.
        private = home / "Library/Application Support/AddressBook"
        make_file(private / "secret.db", "NO_TOUCH")
        private2 = home / "Library/Application Support/CloudDocs"
        make_file(private2 / "document", "NO_TOUCH")
        result = execute(home, "audit_disk.py", ["--scope", "home", "--root", str(home), "--json"])
        parsed = json.loads(result.stdout)
        check(result.returncode == 0 and parsed["complete_within_policy"] and
              not parsed["home_total_measured"] and parsed["policy"] == "privacy-safe-v1",
              "Privacy-safe Home scan reports only in-policy completeness")
        check(private.joinpath("secret.db").read_text() == "NO_TOUCH" and
              private2.joinpath("document").read_text() == "NO_TOUCH" and
              'AddressBook' not in result.stdout and 'CloudDocs' not in result.stdout,
              "Private source files preserved and hidden from summary")
        forbidden = execute(home, "audit_disk.py", ["--scope", "path", "--root", str(private), "--json"])
        check(forbidden.returncode != 0 and "PRIVACY_SCOPE_DENIED" in forbidden.stderr,
              "Direct private-directory scope refused")
        private_cache = private / "Cache"
        make_file(private_cache / "item")
        f = plan_file(home, [target("~/Library/Application Support/AddressBook/Cache", "cache", ["Cursor"])], True)
        no_private_cleanup = execute(home, "cleanup_plan.py", ["--plan", str(f)])
        check(no_private_cleanup.returncode != 0 and private_cache.exists(),
              "AI-approved plan cannot bypass personal-data privacy veto")
        private_link = home / ".cache/puppeteer"
        private_link.symlink_to(private, target_is_directory=True)
        via_symlink = execute(home, "audit_disk.py", ["--scope", "path", "--root", str(private_link), "--json"])
        check(via_symlink.returncode != 0, "Symlink to personal data cannot bypass privacy scan policy")
        private_link.unlink()

        # Spy on every du invocation in an isolated fixture on the REAL host.
        spybin = home / "spybin"
        spybin.mkdir()
        spylog = home / "spy-du.log"
        spy = spybin / "du"
        spy.write_text("#!/bin/sh\nprintf '%s\\n' \"$*\" >> \"$DU_SPY_LOG\"\nprintf '1\\t%s\\n' \"$3\"\n")
        spy.chmod(0o700)
        env = {**os.environ, "HOME": str(home), "PATH": str(spybin) + os.pathsep + os.environ.get("PATH", ""),
               "DU_SPY_LOG": str(spylog)}
        observed = subprocess.run([sys.executable, str(BASE / "audit_disk.py"),
                                   "--scope", "home", "--root", str(home), "--json"],
                                  env=env, capture_output=True, text=True)
        calls = spylog.read_text() if spylog.exists() else ""
        check(observed.returncode == 0 and all(
              bad not in calls for bad in ("AddressBook", "CloudDocs", str(home) + '\n', str(home) + '/Library')),
              "Actual du calls never include private directories or broad parents")

        cache_app = home / "Library/Caches/ReviewedApp"
        make_file(cache_app / "generated-data")
        app = execute(home, "audit_disk.py", ["--scope", "path", "--root", str(cache_app),
                                               "--user-selected-cache", "--json"])
        check(app.returncode == 0 and json.loads(app.stdout)["candidate_count"] == 1,
              "Explicit user-selected technical app cache may be scanned")
        unapproved_app = execute(home, "audit_disk.py", ["--scope", "path", "--root", str(cache_app), "--json"])
        check(unapproved_app.returncode != 0, "User-selected app cache denied without explicit opt-in")
        # AI decision is an input, not an algorithmic endorsement.
        analysis = "The AI evaluated this disposable cache, its regeneration cost and its app-dependency conditions."
        reviewed = target("~/Library/Caches/ReviewedApp", "agent_reviewed_cache", ["Chrome"])
        reviewed.update({"ai_analysis": analysis, "conditions": ["App fully closed", "User approves exact path"]})
        reviewed_file = plan_file(home, [reviewed], True, schema=3)
        reviewed_result = execute(home, "cleanup_plan.py", ["--plan", str(reviewed_file)])
        check(reviewed_result.returncode == 0 and cache_app.exists(),
              "AI-reviewed exact cache accepted for dry-run only; nothing deleted")
        reviewed_missing = dict(reviewed)
        reviewed_missing.pop("ai_analysis")
        missing_file = plan_file(home, [reviewed_missing], True, schema=3)
        missing_result = execute(home, "cleanup_plan.py", ["--plan", str(missing_file)])
        check(missing_result.returncode != 0 and cache_app.exists(),
              "AI-reviewed cache requires written reasoning and conditions")
        result = execute(home, "triage_home.py", ["--json"])
        parsed = json.loads(result.stdout)
        check(result.returncode == 0 and parsed["read_only"] and parsed["user_approved"] is False, "Read-only triage never grants deletion approval")
        check(db.read_text() == "MUST KEEP" and secret.read_text() == "history", "All protected user state survived tests")
        # v1.2 execution integrity and real bundled-script runner checks.
        verifier = execute(home, "verify_bundle.py", ["--json"])
        valid = json.loads(verifier.stdout)
        check(verifier.returncode == 0 and valid["ok"] and valid["version"] == "1.3.1",
              "Installed v1.3.1 manifest validates shipped scripts")
        check(valid["checked"] == valid["expected_files"] and valid["checked"] >= 12,
              "Manifest covers all shipped executable sources/references")
        check(valid["declared_versions"] == {
                  "SKILL.md": "1.3.1",
                  "README_zh.md": "1.3.1",
                  "references/execution-contract.md": "1.3.1"},
              "All release headings match manifest; historical version mentions are ignored")

        # Corrupt one file inside a completely separate copy; never change the real package.
        cloned = home / "broken-package"
        shutil.copytree(BASE.parent, cloned, ignore=shutil.ignore_patterns("__pycache__"))
        tampered = cloned / "scripts" / "triage_home.py"
        with tampered.open("a", encoding="utf-8") as fp:
            fp.write("\n# corrupted test copy\n")
        mismatch = subprocess.run([sys.executable, str(cloned / "scripts/verify_bundle.py"),
                                   "--json"], capture_output=True, text=True)
        invalid = json.loads(mismatch.stdout)
        check(mismatch.returncode != 0 and not invalid["ok"] and
              any("Hash mismatch" in x for x in invalid["errors"]),
              "Tampered transferred script is rejected")
        # Attack the heading AND update the copy's manifest checksum. The
        # semantic release declaration check must still detect the mismatch.
        tampered.write_bytes((BASE / "triage_home.py").read_bytes())
        cloned_skill = cloned / "SKILL.md"
        original_title = "# macOS Disk Auditor & Safe Cleanup — v1.3.1"
        assert original_title in cloned_skill.read_text()
        cloned_skill.write_text(cloned_skill.read_text().replace(
            original_title, "# macOS Disk Auditor & Safe Cleanup — v1.2.2", 1))
        cloned_manifest_file = cloned / "manifest.json"
        cloned_manifest = json.loads(cloned_manifest_file.read_text())
        cloned_manifest["files"]["SKILL.md"] = hashlib.sha256(cloned_skill.read_bytes()).hexdigest()
        cloned_manifest_file.write_text(json.dumps(cloned_manifest))
        response = subprocess.run([sys.executable, str(cloned / "scripts/verify_bundle.py"),
                                   "--json"], capture_output=True, text=True)
        semantic_result = json.loads(response.stdout)
        check(response.returncode != 0 and not semantic_result["ok"] and
              any("Release version mismatch: SKILL.md" in e for e in semantic_result["errors"]),
              "Forged heading fails even if altered manifest hash matches")
        before_reports = list(home.glob("audit-*.json"))
        runner = execute(home, "audit_session.py", ["--scope", "home",
                                                    "--output-dir", str(home), "--timeout", "35"])
        receipt = json.loads(runner.stdout)
        audit_report = json.loads(Path(receipt["report_path"]).read_text())
        check(runner.returncode == 0 and audit_report["status"] == "ok" and
              audit_report["version"] == "1.3.1" and
              audit_report["executed_script"] == "scripts/audit_disk.py" and
              audit_report["result"]["root_total_skipped"] is True,
              "Audit session runs original audit_disk.py and checkpoints verified scope")
        correct_hash = hashlib.sha256((BASE / "audit_disk.py").read_bytes()).hexdigest()
        check(audit_report["executed_script_sha256"] == correct_hash and
              audit_report["platform"] and audit_report["scope"] == "home",
              "Checkpoint contains original script hash, platform and scope evidence")
        triage_runner = execute(home, "audit_session.py", ["--scope", "triage", "--output-dir", str(home),
                                                           "--timeout", "35"])
        triage_receipt = json.loads(triage_runner.stdout)
        triage_report = json.loads(Path(triage_receipt["report_path"]).read_text())
        check(triage_runner.returncode == 0 and
              triage_report["executed_script"] == "scripts/triage_home.py" and
              triage_report["result"]["user_approved"] is False,
              "Audit session invokes bundled triage_home.py without auto-approval")
        failed_scope = execute(home, "audit_session.py", ["--scope", "path", "--root", str(home / "absent"),
                                                          "--output-dir", str(home)])
        check(failed_scope.returncode != 0,
              "Invalid audit scope is rejected rather than simulated")
        check(db.read_text() == "MUST KEEP" and secret.read_text() == "history",
              "Acceptance runner and tampering test never change real protected fixture")
        print(f"ALL {TESTS} TESTS PASSED; sandbox was temporary HOME only")


if __name__ == "__main__":
    main()
