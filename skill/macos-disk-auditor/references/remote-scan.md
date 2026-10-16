# Remote audit execution and bounded outputs

## Why a single `du -sh "$HOME" (FORBIDDEN in privacy-safe mode)` can fail remotely

Huge directory traversal may exceed a bridge's response timeout. A tool returning `Process is running` is not a completed command; if the follow-up session is gone there is no proof that the measurement finished. Do not fabricate totals.

## The v1.2 remedy

Run original `audit_session.py` repeatedly using separate scopes. Every scope independently writes a JSON completion record in an explicitly authorized ephemeral report directory and prints a small receipt. Examples:

```bash
# Set REPORT_DIR to a freshly created scratch directory from an authorized connector.
python3 scripts/audit_session.py --scope home --output-dir "$REPORT_DIR" --timeout 180
python3 scripts/audit_session.py --scope library --output-dir "$REPORT_DIR" --timeout 180
python3 scripts/audit_session.py --scope triage --output-dir "$REPORT_DIR" --timeout 180
python3 scripts/audit_session.py --scope path --root "$HOME/.codex" --output-dir "$REPORT_DIR" --timeout 180
python3 scripts/audit_session.py --scope path --root "$HOME/Developer" --output-dir "$REPORT_DIR" --timeout 180
```

Privacy-safe mode NEVER scans the Home/Library roots or private directory trees; it measures allowlisted technical leaves. Previously the scanner used `--skip-root-total` to avoid duplicate root scans; now it is a permanent policy boundary.

For permitted technical leaves, and per-du batch `--du-timeout 45` (configurable). Any scope that times out still yields a **timeout receipt** when the wrapper reaches its handler. A scope with `du` warnings yields **partial**, with errors in the JSON; its `root_kib` is deliberately null. Each invocation is independent, so a slow Home scope must not prevent a successful npm or library scope.

If the connector can only return after ~3 seconds, use its process-output follow-up to retrieve the receipt; if that mechanism drops the session, read the JSON file from `REPORT_DIR` using its read-file tool. When the job was killed before creating a record, that scope remains unverified. Never equate "process started" with "audit completed".

`du` may fail for TCC-protected content even without `sudo` and with a privileged account. Log errors and exclude unknown-size folders from numeric totals. Include hidden folders by scanning `Path.iterdir()`; never filter dot-prefixed directories. Filesystem totals come from `disk_usage`/`df`, not from summing overlapping directories.

A strict no-write request means **even ephemeral receipts require separate permission or user-preinstalled outputs**. In that case invoke original `audit_disk.py` / `triage_home.py` directly with `--json` and capture output through the connector; if output cannot be retrieved, mark failed instead of silently switching to homemade `du`.

## Privacy rules v1.3.0
Never scan or probe real private folders, even with Full Disk Access. Use only the `privacy_policy.py` allowlisted leaves; `complete_within_policy` replaces claims of full Home coverage. Default report sanitizes paths/host/PID.
