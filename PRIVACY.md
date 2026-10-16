# Privacy Policy and Data Boundary (v1.3.0)

This describes the **local scripts' designed behavior and the tested default workflow**, not a representation of how external AI platforms or third-party connectors independently process data. Read their separate policies before connecting.

## Purpose and default collection

The Skill assesses *storage cost* of a narrow allowlist of technical caches and runtime/build artifacts. The local scanner executes `du -sk` only on policy-authorized leaves. It does not open personal file contents, recursively walk Home or Library as a whole, or count intentionally excluded private directories.

Default structured audit output includes policy identifier, anonymous candidate ID, technical category, storage size, blockers and coverage status. `complete_within_policy` measures completeness **within that policy only**, not total disk coverage. Filesystem total/free values concern the mounted volume, not Home size.

## Intentionally excluded

Personal documents and desktop folders, Mail, Messages, Photos, iCloud/CloudDocs, MobileSync, FaceTime, AddressBook, Keychains, TCC data, FileProvider, browser profiles and arbitrary third-party application state. A user-granted Full Disk Access permission does **not** authorize this Skill to inspect those paths.

A developer scope operates on a user-selected Cargo `target/` only. A user-selected app cache needs separate consent and remains subject to the hard privacy veto. Known cache directories may themselves contain user-generated material, so **do not treat the cache label as a guarantee of safe deletion**.

## Output, storage, and connector exposure

- Default audit JSON omits username, hostname, absolute target paths, raw process command lines and PID fields. The tool creates owner-only evidence directories (mode `0700`) and report files (`0600`).
- Local console receipts can expose **the chosen output directory**; cleanup preview deliberately prints **exact target paths** and the HOME path for a human review. Error messages or explicitly requested `--details` may also reveal paths. Do not publish raw terminal logs, dry-run plans or detailed reports.
- The scripts do not include a network uploader or telemetry endpoint. However, **when an AI agent or remote connector carries returned results into a chat or external service, that service may process the results under its own policy**. Only share the minimum necessary information.
- Artifacts remain locally until the user removes them. The scripts do not implement a global retention/secure-erasure guarantee; treat temporary reports as sensitive local records.
- There is no background monitoring, scheduled scan, or automatic collection in the default workflow.

## Human consent and deletion

Audit consent is not deletion consent. AI produces a contextual recommendation; user approves exact targets separately. `cleanup_plan.py --plan <file>` is preview only. `--apply` requires fresh per-target permission, technical safety checks and local physical TTY confirmation. The executor can veto unsafe requests even when an AI or user requested them. Deletion may be permanent and cache recreation may require downloads or interrupt offline use.

## Reporting privacy issues

Please do **not** attach real personal directory listings, user paths, tokens or process arguments to public issues. See [SECURITY.md](SECURITY.md) for private security reporting. Privacy design is informed by the frozen [`references/privacy-threat-model.md`](skill/macos-disk-auditor/references/privacy-threat-model.md), but implementation remains subject to future review and testing.
