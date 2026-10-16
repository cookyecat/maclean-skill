# Public, redacted G0–G7 acceptance summary — 2026-10-16

**Decision:** PASS for the tested scope and environment.

**Device class:** Mac mini (device/person identifiers intentionally omitted). **OS:** macOS 26.5.2. **Interpreter:** Python 3.14.7. **Execution path:** authorized Mac MCP Gateway after its update.

| Gate | Public result | Independent limits |
|---|---|---|
| G0 | PASS | Installed Skill title/manifest/contract all declared 1.3.0 |
| G1 | PASS | Connected to this device only; not a proof about other Mac permissions |
| G2 | PASS | Original source transferred unchanged |
| G3 | PASS | Manifest 17/17; original verifier exit 0 |
| G4 | PASS | Original on-Mac `self_test.py`: 53/53, exit 0, 3.913 seconds; a separate original-executor `/var`/`/private/var` preview test also passed |
| G5 | PASS | Home 20/20 and Library 4/4 **policy-authorized** targets measured; triage read-only; no full Home measurement |
| G6 | PASS | AI judged only two REVIEW candidates; unapproved dry-run measured ~1.28 GiB of cache allocation; no real cleanup |
| G7 | PASS | Synthetic private-path/symlink/`du` negative tests, source-redacted default JSON, owner-private local reports |

The **manifest SHA-256** is `6dcdc492aad867b28e96ba25142c37c7e81f3c0e0219872d13c420dce5aafbe5`.

**Explicit limits:** G7 is based on the tested real workflow and synthetic fixtures, not an independent proof of all possible filesystem activity. The tests did not access real private user folders or delete real user data. The original self-test's 53 count excludes the independently-run `/var` alias test. No real `--apply` operation was performed; recovered APFS blocks are unknown. This public summary intentionally omits internal Skill URI, usernames, addresses, private project paths, raw command lines, test PID and local report file paths.
