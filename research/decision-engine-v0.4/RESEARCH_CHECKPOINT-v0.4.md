# MacLean research checkpoint — Decision Engine v0.4

**Date:** 2026-10-17  
**Branch:** `research/decision-engine-operations-v0.4`  
**Base:** `research/decision-engine-evidence-v0.3`  
**Review:** [PR #6](https://github.com/cookyecat/maclean-skill/pull/6)  
**Status:** research prototype only; no merge to production, no native browser cleanup adapter.

## Locked design history

- Product principle: **用户不用懂技术，AI 能判断得准，程序能删得安全。**
- Frozen v1 decision diagram: `docs/research/AI-DECISION-STATES-v1.md`.
- Frozen one-batch confirmation UX: `docs/research/ONE-CLICK-CLEANUP-UX-v1.md`.
- v0.1: synthetic, independent three-state/evidence-reference evaluator; historical + expanded cases.
- v0.2: 32 post-uv real Privacy Safe candidates; 12 anonymous blind, both providers 12/12 KEEP. No independent gold.
- v0.3: publisher E1 and sandbox uv E2; synthetic E3 boosts recommendation to 3/9 for both providers, but method semantics fail for browser proposals.
- **v0.4:** exact app-operation IDs; bounded synthetic browser client-dependency graph; test scopes, extra touched versions, hard veto, symlink boundaries, stale assessment TOCTOU.

## Code and empirical receipt

| Item | v0.4 |
|---|---|
| Typed operations | **7** (uv 2, Puppeteer 2, Playwright 3) |
| Tested synthetic browser builds | 3 |
| Synthetic fixture clients | 2 |
| Local macOS regressions | **29/29 PASS** |
| New real browser cache reads | **0** |
| New real deletions / stopped processes | **0** |
| Production-eligible operation plans | **0** (explicitly false) |
| GitHub research CI | expected to be verified on exact PR HEAD before readiness |

Do not claim actual native browser uninstall equivalence or current-user E3 evidence. The fixture manifests are **invented**, not Puppeteer/Playwright formats, and full client coverage only holds inside the fixture.

## Independent findings

1. Targeted hypothetical uninstall can match one synthetic approved orphan version, but the native API has not been locally validated.
2. Browser clear-all or uninstall-all can exceed a one-item approved set and affect currently referenced versions.
3. Automatic Playwright stale-browser GC is a dynamic operation; do **not** map it to universal NATIVE_CLEAN or assume a fixed touched set.
4. A new client reference or newly installed browser build **after** preview invalidates the old preflight snapshot. A hash detects change but is not a trusted attestation or execution authorization.
5. Synthetic correct scope, AI RECOMMEND and production execution permission remain three separate questions. Every current preview is not executable.

## Research v0.5 next steps (preregistered)

A. **Publisher-native disposable CLI fixtures**: isolate dedicated browser cache + package manager state; no downloads by default; call only installed publisher-approved read-only `list`/`--dry-run`. Verify actual JSON/CLI output semantics and how to avoid npx downloading code unexpectedly.

B. **Bounded real read-only E3 feasibility**: with user-authorized paths only, compare registry/version references and active process handles. No recursive Home scanning, no browser Profile content, no leakage of client paths/profile identities. Negative evidence (“not open in lsof”) must not prove no future use.

C. **Typed scope contract**: design separately for `puppeteer.browsers.uninstall_build`, `playwright.browsers.gc_unused`, `uv.cache.prune`; preflight verifies exact targets and process guards; enforce approval digest and TOCTOU revalidation. No integration until test fixture and privacy review.

D. **Prospective gold**: new independently labeled, blinded real cases from v0.2 protocol. Model agreement is not accuracy and the already exposed v0.2/0.3 cases are not an unseen holdout.

## Safety rule for continuing

Do not run `rm`, `uv cache clean`, `npx ... clear`, `npx playwright uninstall`, or GitHub release publication against real user caches as part of research. Any eventual production cleanup must retain original independent user batch approval and physical-terminal confirmation; research scripts are not executable adapters.

**Checkpoint conclusion:** scoped method research is viable; real E3 and genuine publisher binary fixture acceptance are **not yet complete**. Proceed to v0.5 without weakening frozen privacy and user-authorization boundaries.
