# Contributing

Contributions should improve privacy-preserving technical disk auditing **without expanding scanning or mutation authority by default**.

## Before opening an issue

- Prefer synthetic paths and small, reproducible examples; never post real account names, Host IDs, home paths, credentials, raw `ps` commands, or personal files.
- For exploitable or privacy-impacting bugs, report privately as described in [SECURITY.md](SECURITY.md).
- Explain the macOS version, Python version, invocation mode and expected behavior without including machine-identifying details.

## Pull request requirements

1. Explain how the change affects **Privacy Boundary**, **AI/executor separation**, and **Mutation Boundary**.
2. Keep default Privacy Safe deny-by-default. A new scanning target requires an explicit technical justification and synthetic negative tests for parents, symlinks and protected descendants.
3. No automatic deletion, `sudo`, process termination, TCC/Full Disk Access changes, remote telemetry, or non-interactive typing of `DELETE`.
4. Any new output field must be privacy-reviewed. Avoid exposing path, hostname, PID, raw process command line or credentials in the default structured report.
5. Update and rehash manifest-managed files; run `verify_bundle.py --json`; run on-Mac `self_test.py` with a disposable HOME, plus G0–G7 when changing scan/cleanup boundaries.
6. Attach only redacted proof and no actual-user-data deletion logs. A passing Ubuntu static CI job is **not** a substitute for a macOS G0–G7 run.

This draft intentionally does not state a contribution license or contributor agreement until the project owner selects the repository's software license.
