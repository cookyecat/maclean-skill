# Install and genuine acceptance in ChatGPT / Codex — v1.4.0

## ChatGPT web Skill upload

Upload `macos-disk-auditor-v1.4.0.zip` through the Skills uploader available in your workspace. Update/replace older versions when supported; otherwise retire the old version in the UI and import the ZIP. After installing, open a **new conversation** and explicitly select the Skill if the UI requires selection.

A Skill displayed in the UI **is not proof** that the active session can read its `SKILL.md`. ChatGPT Skill execution does not copy the scripts to your Mac automatically. The agent must transfer the exact bundled files (or verify the user's already installed copy) and run the originals there. See `references/execution-contract.md` and `references/transport.md`.

## Codex installation

Repository scoped:

```bash
mkdir -p /path/to/repo/.agents/skills
unzip -q macos-disk-auditor-v1.4.0.zip -d /path/to/repo/.agents/skills
```

Follow repo `AGENTS.md` and the user's Mac connection permissions.

## Install on authorized Mac manually when transfer isn't supported

Use the trusted ZIP that was provided to the user (not a random download):

```bash
STAGE=$(mktemp -d)
unzip -q "$HOME/Downloads/macos-disk-auditor-v1.4.0.zip" -d "$STAGE"
cd "$STAGE/macos-disk-auditor"
python3 scripts/verify_bundle.py --json
```

Keep `$STAGE` only long enough for the acceptance run; do not remove any preexisting files. The user can choose whether to delete the temporary staging and JSON report directories after verification. No sudo.

## Real packaged-script test on the Mac

Choose a fresh scratch report directory with sufficient space and user permission. These audit runs only create JSON audit receipts there; they do not modify analyzed files. `self_test.py` does delete temporary **fixtures**, so run it only if the user allows temporary test-file creation/removal.

```bash
REPORT_DIR=$(mktemp -d)
chmod 700 "$REPORT_DIR"
python3 scripts/self_test.py
python3 scripts/audit_session.py --scope home    --output-dir "$REPORT_DIR" --timeout 180
python3 scripts/audit_session.py --scope library --output-dir "$REPORT_DIR" --timeout 180
python3 scripts/audit_session.py --scope triage  --output-dir "$REPORT_DIR" --timeout 180
```

When running via Remote Desktop Commander, choose a supported process/read-file protocol to collect the receipts from `$REPORT_DIR`, and never claim the test passed if they can't be retrieved. Only the original script executions count as Skill script evidence. Independently run `ps`/`git` for activity/classification supplements.

## For a no-write acceptance

Do not stage scripts if all writes are prohibited; user must preinstall the Skill scripts themselves. If scripts are preinstalled, execute the original `audit_disk.py` and `triage_home.py` with `--json` without writing report files. If the remote connector cannot return long command output, mark the test incomplete. Never substitute shell commands to claim G5 passed.
