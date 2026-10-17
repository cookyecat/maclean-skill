# Installation and safe first run — v1.4.0 source / v1.3.1 historical ZIP

> **v1.4.0 is currently a source-only sync.** The packaged ZIP retained in `artifacts/` is v1.3.1; installing it does NOT install v1.4.0. The historical v1.3.0 G0–G7 result is not a universal certification of later versions.

## Install from verified v1.4.0 source

Obtain a trusted full repository checkout, inspect [`skill/macos-disk-auditor/`](../skill/macos-disk-auditor/) and use that exact directory when installing a Skill from source in an environment that supports it:

```sh
cd skill/macos-disk-auditor
python3 scripts/verify_bundle.py --json
```

Confirm `ok=true`, `version=1.4.0`, and the source provenance independently. Installing the Skill does not authorize Mac access, and verifying a manifest is not authorization to delete files. **No v1.4.0 installation ZIP is included in this source update.**

## Historical v1.3.1 ZIP installation

## ChatGPT with an authorized Mac connector

1. Import the exact `macos-disk-auditor-v1.3.1.zip` from `artifacts/` via your supported Skill installation UI. An installed or selected Skill does **not** grant access to the Mac.
2. In a new conversation, ask the agent to read the *actually installed* `SKILL.md` and manifest; verify version `1.3.1`, and request **read-only Privacy Safe** audit.
3. Authorize Mac MCP Gateway or another Mac computer connector **separately**, subject to your own chosen scope. Do not enable Full Disk Access as a requirement of this Skill.
4. Allow deployment of verified original files and reports to a fresh disposable location only. The agent must run **bundled** scripts, not replace them with ad hoc `find`/`du` commands.
5. Review anonymous candidate data; do **not** approve `--apply` as part of a scan or installation.

## Manual verification on an authorized Mac

Run only after you trust and locally possess the ZIP. The commands below create a staging directory and owner-private reports, but do not delete any audited user data:

```bash
ZIP="$HOME/Downloads/macos-disk-auditor-v1.3.1.zip"
STAGE="$(mktemp -d)"
unzip -q "$ZIP" -d "$STAGE"
cd "$STAGE/macos-disk-auditor" || exit 1
python3 scripts/verify_bundle.py --json
REPORT_DIR="$(mktemp -d)"
chmod 700 "$REPORT_DIR"
python3 scripts/audit_session.py --scope home --output-dir "$REPORT_DIR" --timeout 180
python3 scripts/audit_session.py --scope library --output-dir "$REPORT_DIR" --timeout 180
python3 scripts/audit_session.py --scope triage --output-dir "$REPORT_DIR" --timeout 180
```

The `--scope home` and `--scope library` commands **do not recurse over the Home or Library roots**. They only inspect specific policy-allowed technical leaves. They do not measure a Home total. They write JSON files (`0600`) in `$REPORT_DIR` and emit a receipt containing that report path—do not publish raw receipts. Avoid running `--details` unless you separately want detailed **local-only** information.

## Optional developer scope

Only if the user selects an exact project root:

```bash
python3 scripts/audit_session.py --scope developer   --project-root "$HOME/Developer/your-project"   --output-dir "$REPORT_DIR" --timeout 180
```

This targets that project's Cargo `target/` only, **not** all of `~/Developer`, Git source contents, or sibling projects.

## Acceptance test, *only* when temporary-fixture writes are approved

```bash
python3 scripts/self_test.py
```

It creates/deletes its own disposable fixture HOME; do not mistake this for permission to clean any other file. Record the actual passing count, exit code and evidence instead of relying on historical reports. See [VALIDATION.md](VALIDATION.md).

## Plan preview, not deletion

AI may propose a precise plan after reviewing storage evidence, app activity, rebuild costs and user constraints. `user_approved: false` is the default. Only after the user explicitly requests a plan should a concrete plan be prepared. The following **never** deletes:

```bash
python3 scripts/cleanup_plan.py --plan /path/to/unapproved-or-approved-plan.json
```

Never autonomously invoke `--apply`, pipe `DELETE`, change system permissions, or stop a user's processes. A real cleanup must be authorized separately for each precise target.

## Compatibility

Published full Mac acceptance evidence exists for **macOS 26.5.2, Python 3.14.7**, one Mac mini and one Gateway configuration. Python language syntax in the package suggests Python ≥3.10; that is a **minimum syntax requirement**, not proof of testing on every Python version. See [COMPATIBILITY.md](COMPATIBILITY.md).
