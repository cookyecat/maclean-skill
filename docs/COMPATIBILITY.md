# Compatibility and evidence matrix

Compatibility means **validated behavior in the stated environment**, not the absence of known failures elsewhere.

| Component | Evidence-backed status | Notes |
|---|---|---|
| Mac mini / macOS **26.5.2** | **G0–G7 PASS** on 2026-10-16 | Single authorized device; no cleanup of real user files |
| Python **3.14.7** | **Tested** | Interpreter used in recorded Mac run |
| Mac MCP Gateway (updated installation) | **Tested in acceptance run** | Another gateway build or remote permissions are not automatically covered |
| macOS 15, 14, 13 or other builds | **Not independently validated** | No claim of failure or of support |
| Python 3.10–3.13 | **Not independently validated** | ≥3.10 is inferred from source syntax (`Path | None`), not verified compatibility |
| Intel macOS, other Apple Silicon devices | **Not independently validated** | Read-only audit likely platform-specific; do not state universal support |
| APFS snapshots, shared/hard-linked blocks | **Not full-recovery tested** | `du` sizes may differ from actual space reclaimed |
| Other ChatGPT/Codex/agent host setups | **Not independently validated** | Skill registration and tool transport vary by host |
| Linux / Windows | **Not supported claim** | Script behavior and system tooling are macOS-specific |

## Evidence details

G0–G7 were reported PASS for the same original v1.3.0 package: manifest 17/17, 53/53 self-tests, permitted technical target sizes 20/20 (Home policy) and 4/4 (Library policy), triage read-only, two AI-reviewed candidates dry-run only, and privacy negative tests in synthetic fixtures. The original `self_test.py` did **not** include a direct `/var` alias assertion; a separate original-executor read-only alias test was performed. This distinction is intentional.

These results support *one validated end-to-end baseline*. They do not verify a real-user deletion, all app types, all macOS versions, all connector privilege contexts, or future product-version interactions.

## Pre-release compatibility work

- An independent Mac on another supported macOS release and different permission context.
- Python 3.10, 3.11, 3.12 or 3.13 smoke/regression test (or document an explicitly narrower interpreter support range).
- Simulated symlink, hardlink, APFS snapshot and active-runtime cases across versions.
- Preserve all privacy protections when any API or environment behavior changes.
