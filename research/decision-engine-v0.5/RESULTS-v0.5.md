# Decision Engine v0.5 · Real Native CLI and Partial E3 Evidence Results

**Observed on 2026-10-17 (Asia/Tokyo), macOS arm64, authorized Mac MCP Gateway.**

## Result summary

| Experiment | Observed | Provenance | NOT proven |
|---|---|---|---|
| Preinstalled CLI probe | uv/lsof/node/npm/npx available; standalone Puppeteer and Playwright absent | Host PATH, Python module capability (read-only) | No installation anywhere else on the Mac |
| Temporary package E2 | Pinned @puppeteer/browsers 3.2.5 and playwright-core 1.64.1 installed into private throwaway folder | Exact package.json versions | Browser installations, global availability |
| Puppeteer native list | `list --path` accepts isolated root; lists a **fake empty browser version folder** | Actual publisher CLI 3.2.5, no real browser downloaded | That listed browser exists as a runnable binary |
| Playwright native list | Without fixture `.links`: error; after empty fixture `.links`: successful empty list | Actual playwright-core CLI 1.64.1 | Global client coverage or reliable "no browser" without setup |
| Playwright dry-run | Returns proposed browser install locations | Actual CLI `install --dry-run` | Existing installed browser inventory |
| E3 positive control | `lsof +d` sees a synthetic held-open file | Real OS process/fd in private temp fixture | Complete nested handle coverage |
| Known Puppeteer cache | Root present; no direct/root-level open reference observed | Exact MacLean catalog leaf, shallow read-only `lsof` | Unused, safe-to-delete or offline recoverable |
| Known Playwright cache | Default leaf absent on this snapshot | Exact catalog path existence check | No other Playwright cache, no other installed browser |
| Fail-closed regressions | **20/20** PASS on Mac | Runtime `unittest` | Production G0–G7, browser cleanup safety |

**Changes to real user caches, projects, app configurations or running services:** **0**.  
**Temporary work:** npm downloaded two packages and their dependencies into an owner-private temporary research prefix with lifecycle scripts disabled; disposable fake directory, isolated cache and own synthetic test process created. **No browser binary downloaded.**

## Key new failure case: publisher native list is not filesystem truth

The MacLean experiment created only:

`<private fixture>/chrome/mac_arm-999.0.0.0/`

No browser executable or payload was present. Nevertheless `@puppeteer/browsers 3.2.5 list --path <fixture>` returned that build with a computed executable path. **The computed path did not exist.**

Conclusion: `CLI_LISTED` is a catalog *index observation*, not independent `EXECUTABLE_PRESENT`. Treating the former as the latter is a potential false-positive E3 classification, which can mislead both recovery and deletion decisions.

This is a finding about the tested version and fixture, **not** proof that all Puppeteer releases or other CLIs share the issue. Independent path verification and client mapping remain necessary.

## A distinct failure case: native list failure ≠ no installed browsers

The Playwright 1.64.1 CLI `install --list` exited 1 on a fresh, empty isolated cache lacking `.links`. It succeeded with no entries after an empty `.links` directory was created there. `install --dry-run` showed planned build locations, not installed builds.

The original Playwright documentation states that versions are connected to client packages and can be garbage-collected when no clients require them. It does **not** allow MacLean to infer completeness from a single empty or failed list.

## E3 real host evidence: asymmetric meaning

A positive observation from the narrowly scoped `lsof` is enough to **veto or defer** a deletion of the affected target. A negative observation is **not evidence of lack of future dependency**.

The only 2 catalog roots checked in this experiment are already in MacLean's existing privacy policy; neither whole Home/Library nor personal Profile content was scanned. `lsof +d` may enumerate direct child metadata in a catalog technical leaf; stdout is discarded after in-memory aggregation and not published. No recursive `+D` was used.

- `Puppeteer=NOT_OBSERVED_IN_SHALLOW_SCAN` -> `KEEP` / insufficient evidence.
- `Playwright=ABSENT` at that fixed path -> `KEEP` / nothing to remove at that location.
- Any `OPEN_REFERENCE_OBSERVED` -> `DEFER` (independent live-use veto).

The sensor has **no authenticated real-E3 full-use proof** and deliberately cannot produce `RECOMMEND` or `--apply` authorizations.

## Measured quality and next acceptance

- 20/20 local negative tests passed.
- Existing 29/29 v0.4 sandboxed graph tests remain separate; do not add totals as if they represent real-world accuracy.
- No independent Gold or real model quality estimate in v0.5.
- No production-native browser management semantics have been used to remove even a disposable browser installation; only listing and dry-run.

Follow-up v0.6 should focus on independent executable verification, actual publisher client-reference semantics and evidence source authenticity, not on making a model more permissive by default.

Official citations:
- https://pptr.dev/browsers-api
- https://playwright.dev/docs/browsers
- https://docs.astral.sh/uv/concepts/cache/
