# v0.4 Research Results · Typed Application Cleanup Scope

**2026-10-17, Mac MCP Gateway authorized machine; non-destructive research.**

## What was verified

- The code was executed on the Mac in a fresh disposable fixture; not a scan of real user caches.
- A purely synthetic browser set had three versions and two synthetic client manifests. The fixture orphaned one old version.
- **29/29 local unit regression tests passed** (scope, app ownership, hard vetoes, dependency mapping, symlinks, malformed manifests, privacy boundary, and TOCTOU).
- One publisher-native fixture capability (**uv prune/clean**) was already tested in v0.3; this v0.4 step does not repeat that real-cache operation and does not execute any native browser uninstall.
- The original production MacLean executor was **not** run.

## Bounded simulated operation outcomes

| Simulated operation | Approved target(s) | Calculated potential effect | Guard conclusion |
|---|---|---|---|
| Puppeteer build-specific uninstall | Only `chrome-0999` | `chrome-0999` | Scope matches synthetic approval, but native effect unverified |
| Puppeteer clear-all | Only `chrome-0999` | All three synthetic builds | **EXACT_APPROVED_SET_MISMATCH**; referenced builds impacted |
| Uninstall still-referenced build | Only `chrome-1111` | `chrome-1111` | **SYNTHETIC_CLIENT_STILL_REFERENCES_TARGET** |
| Playwright unused GC | Only `chrome-0999` | Cannot independently predict true native touched set | **EFFECT_SCOPE_UNPROVEN** |
| Playwright uninstall-all | Only `chrome-0999` | All three synthetic builds | Broad scope mismatch |

All results retain `deletion_authorized=false` and `production_eligible=false`.

### TOCTOU / stale evidence

A fresh synthetic client begins using `chrome-0999` **after** preview: revalidation detects graph digest change and new client dependence.

A fourth browser build arrives after a previously assessed clear-all preview: revalidation detects both the stale graph **and** that the new operation would touch an unapproved build.

This supports the contract that candidate discovery and preflight operation assessment **cannot be reused indefinitely**. It does not establish an E3 sensor for a real user's cache.

## Publisher semantics and limitations

- `uv cache prune` applies uv's own notion of unused items, not a list of Playwright/Puppeteer browser builds.
- Puppeteer's `clear` explicitly clears all installed browsers. The publisher documents more targeted uninstall APIs, but their native behavior on macOS is not yet bounded-fixture verified.
- Playwright manages browser-client references, but `uninstall --all` is not the same as GC of unused versions; there is an environment/configuration opt-out from GC. No code here reads Playwright's private registry format.

Public publisher references: https://docs.astral.sh/uv/concepts/cache/ ; https://pptr.dev/browsers-api ; https://playwright.dev/docs/browsers .

## Research evaluation

**Pass:** the deliberately broad operation gets blocked in the model; unsafe cases (live reference, protected, symlink, changed dependency set, missing client) cannot produce a production-ready plan.

**Not validated:** actual native browser CLI effects, browser re-download/restoration, real E3 current dependencies, actual APFS freed space, model semantic correctness against independent human Gold, and multi-provider comparative accuracy.

**Next:** publisher-native read-only list/preview and disposable rebuild/lifecycle E2 tests, followed by a prospective independently annotated real-cache E3 cohort. Do not merge into stable `main` or claim that any real cache can now be safely removed automatically.
