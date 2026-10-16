# Remote Privacy Safe audit — v1.3.1

## Privacy boundary
Never run recursive du/find over Home, Library, .codex, Developer or any unselected parent directory. Even with Full Disk Access, personal content must not be enumerated or measured. The original scanner only measures technical leaves approved by privacy_policy.py. complete_within_policy is not full Home coverage.

## Actual bundled commands
After original manifest verification, use a newly authorized private report directory (0700; JSON 0600):

```bash
python3 scripts/verify_bundle.py --json
python3 scripts/audit_session.py --scope home --output-dir "$REPORT_DIR" --timeout 180
python3 scripts/audit_session.py --scope library --output-dir "$REPORT_DIR" --timeout 180
python3 scripts/audit_session.py --scope triage --output-dir "$REPORT_DIR" --timeout 180
```

Only after the user explicitly selects a project, invoke:

```bash
python3 scripts/audit_session.py --scope developer --project-root "$HOME/Developer/your-project" --output-dir "$REPORT_DIR" --timeout 180
```

This analyzes the project's allowed build target; it is not permission to traverse sources or sibling projects. For an exact user-selected app cache leaf, use --scope path with --user-selected-cache and the precise permitted target, never a parent directory.

## Receipts and uncertainty
Use original scripts, not ad-hoc shell equivalents. A process-start event is not completion. Retrieve report, exit code and script SHA; timeout or missing receipt is UNKNOWN/PARTIAL, not PASS. Do not share local paths, raw process args or detailed receipts by default. No sudo, no TCC/FDA permission workaround, no root recursion. If temporary report writes were forbidden, do not stage files or claim a full acceptance.
