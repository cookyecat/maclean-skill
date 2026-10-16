# v1.0 empirical result — native npm/npx/uv cleanup in disposable fixtures

**Date:** 2026-10-17. **Host:** authorized macOS arm64. **Scope:** isolated temporary directories **only**.

## Actual observed
- Native **npm 12.2.0** and **uv 0.12.5** executed against private owner-only fixture HOME/cache paths.
- A locally generated package tarball was added to *sandbox* npm `_cacache`. `npm cache verify` succeeded **without removing the valid seeded cache**. `npm cache clean --force` then removed `_cacache`.
- Two synthetic entries inserted under sandbox `_npx`. Native `npm cache npx ls` found both. Native `npm cache npx rm 0123456789abcdef` removed **only** that key; the sibling remained. The sibling also survived clearing `_cacache`.
- Native `uv cache prune` and `uv cache clean` succeeded against a newly isolated uv cache; after clean, the directory was absent on the tested uv 0.12.5 version. There was **no nontrivial uv package payload seeded for this test**, so no reclaimed-space or in-use uv concurrency claim is supported.
- One synthetic child process was kept alive while its *synthetic npx entry* was removed natively. The process later failed to locate a file lazily: **native npx rm does not inherently protect runtime dependencies**.
- A synthetic sentinel outside the disposable cache remained unchanged.
- Zero real cache files deleted; zero real processes stopped; zero production executor modifications.

## Safety regressions

**28/28 local tests passed**: 16 disposable native/scope/concurrency tests plus 12 exact-operation identity-contract tests. Fixture guards refuse Home roots, absent markers, world-readable roots, parent/nested symlinks, dangerous unsupported command argv, traversals, invalid npx keys and malformed method-to-target correspondence. Contract output never authorizes deletion.

**CI nuance:** CI may not have native uv installed; Mac native integration is a separate measured test. GitHub portable contract tests do not substitute for real macOS behavior.

## Implications for next product iteration

The key v0.9 conclusion survives: an application process-family match alone must not globally block normal regenerable caches. But **exact currently used npx runtime entries** can be hazardous to delete. No universal E3 dependency graph is needed: a narrow **native key + current-task protection** is sufficient as the next implementation target.

Proposed exact methods:
- `npm.cache.clean_all` has target `~/.npm/_cacache` only; distinct from `npm.cache.npx.rm_exact` at `~/.npm/_npx/<hex-key>`. Real concurrent clear safety not yet demonstrated.
- `uv.cache.prune` applies to an explicitly approved uv cache root and uses **uv's own native locking**, never a direct raw delete.
- `uv.cache.clean` is higher impact and not a default recommendation.
- Real installed Codex/Cursor daemons are NOT npm package caches and remain separately protected.

**Do not claim that v0.9's 3,148.1 MiB DEFAULT is presently executable.** It remains a gross allocated recommendation figure without an approved real-user native executor or APFS gain measurement.
