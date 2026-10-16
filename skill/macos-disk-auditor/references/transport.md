# Trusted source transfer to a real Mac

**Installing in ChatGPT does not install scripts on the connected Mac.** Correct deployment is a required, independently evidenced step.

## Preconditions

The user has authorized access to the target machine and has allowed temporary staging. If the user prohibits **all** writes, do not stage anything; ask for a preinstalled exact Skill package and mark the end-to-end Skill execution as unverified. Never change macOS settings or mount protected directories.

## Transport strategy (in order)

1. **Verified preexisting user ZIP:** If the user has placed `macos-disk-auditor-v1.3.1.zip` on their Mac, use the appropriate local read/extract mechanism to a *new* disposable staging directory. Do not overwrite a previously installed package. Extract without `sudo`. The ZIP's internal top-level folder must be `macos-disk-auditor/` with original script sources and `manifest.json`.
2. **Authorized file-transfer tools:** If supported, transfer **exact bytes** of every package file from the trusted installed Skill, not model-regenerated code. For text-only Desktop Commander `write_file`, transfer original texts in safe chunks with rewrite followed by append. Transfer all files in `manifest.json` **plus** `manifest.json`. Preserve original bytes and UTF-8 line endings. Do not edit code to "make it work" during transport.
3. **User-assisted transfer:** If the bridge cannot send original files, ask user to download/install the official provided ZIP on their Mac and run the verification step. This is more honest than replacing bundled scripts with a shell paraphrase.

Always stage under a new temporary per-session folder such as a `mktemp -d` path under `$TMPDIR` or `$HOME` temporary area. Stage directory must be accessible to the ordinary user. Write audit results to another explicitly chosen ephemeral report folder; retain until reviewed, then ask user before deletion if they required no deletes.

## Mandatory target verification

From the extracted/staged `macos-disk-auditor` root:

```bash
python3 scripts/verify_bundle.py --json
```

Check `ok: true`, `version: 1.3.1`, `checked: expected_files` and report `manifest_sha256`. `manifest.json` verifies that files match the **manifest shipped with the trusted Skill**; it is not cryptographic authentication of a package from an arbitrary stranger. If false, DO NOT execute other scripts and DO NOT recreate auditor commands by hand for acceptance. Repair transport or mark failure.

No direct web download, `curl | sh`, auto-install of dependencies, privileged operations, runtime disablement, or modifying app/system state is part of deployment.

## Files that must arrive on target

- `SKILL.md`, `manifest.json`, `README_zh.md`
- all `scripts/*.py`, especially `verify_bundle.py`, `audit_session.py`, `audit_disk.py`, `triage_home.py`, `self_test.py` and `cleanup_plan.py`
- all `references/*.md`, `examples/*.json`

In a *strict read-only audit* `cleanup_plan.py` is never invoked, even in preview, unless explicitly requested; it is transferred only for integrity/completeness.
