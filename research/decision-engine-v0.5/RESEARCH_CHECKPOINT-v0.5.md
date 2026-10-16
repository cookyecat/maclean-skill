# MacLean Research Checkpoint v0.5 · Next Session Handoff

**Date:** 2026-10-17
**Research branch:** `research/decision-engine-native-e3-v0.5`
**Base:** `research/decision-engine-operations-v0.4`
**Core frozen phrase:** **用户不用懂技术，AI 能判断得准，程序能删得安全。**

## How the design evolved

1. Frozen user-facing UX: three AI states and exactly one AI-reviewed batch; user approves, original executor independently rechecks and physical terminal confirmation remains required.
2. v0.1: independent synthetic recommendation evaluator (detects both "recommend everything" and "keep everything").
3. v0.2: private real audit and MiniMax/DeepSeek blind research; no human Gold; all-KEEP without E3.
4. v0.3: publisher E1 / disposable uv E2 / hypothetical E3; conditional recommendations emerged, but methods were often mismatched to publisher scope.
5. v0.4: 7 typed app-specific operation contracts, synthetic client/build dependency graph, preview-vs-approved-set comparison, stale-graph TOCTOU refusal; 29/29 local tests.
6. **v0.5:** real pinned Playwright/Puppeteer CLI installed in disposable temp, native list and dry-run verified; discovered native-list false-positive / internal .links dependency; bounded real leaf E3 positive-only evidence; 20/20 local tests. **No deletion of user files.**

## Key validated evidence and caveats

- @puppeteer/browsers 3.2.5 `list --path` included intentionally empty, fake browser-build directory with nonexistent binary. Never promote native-list entry to confirmed executable.
- playwright-core 1.64.1 `install --list` on empty cache failed without `.links`, then succeeded with empty `.links`. `install --dry-run` previews possible future locations only.
- macOS `lsof +d` positive synthetic fd observed; real catalog Puppeteer leaf present with no shallow direct open reference observed, NOT proved idle. Exact default Playwright leaf absent. Shallow lsof may inspect direct child metadata; never outputs raw paths/PIDs.
- Current code does not verify current-user browser/client version graph, offline dependency, download availability, or complete E3. This is **partial E3**, not production readiness.
- Both tools were installed as fixed npm dependencies in owner-only temporary prefix **with disabled install scripts**, not into user projects or global runtime. npm packages downloaded; no browser binaries downloaded.
- v0.5: 20 local regression tests pass; exact CI outcome must be checked after final push.
- Stable main and released v1.3.1 remain untouched.

## Next v0.6 recommended work

**Workstream 1: publisher metadata truth.** Bounded native enumeration + executable existence validation + version signature where possible. Reproduce fake-entry case and potential symlink/alias vulnerabilities on disposable fixtures. Do not treat failed native list as absence.

**Workstream 2: full E3 feasibility.** User-authorized per-project metadata only, no broad Home scan. Build signed/provenance-bound, narrow client-version and process-reference evidence; represent absence as uncertainty, not safe removal. Quantify false-negative types.

**Workstream 3: empirical safety.** Independent annotation and new holdout test before adding any production recommendation ability. A model's confident statement never authenticates E3.

**Workstream 4: product UX.** Maintain one AI-reviewed batch for ordinary users; the user should not need to understand npm/Playwright internals. Keep expandable reasons and exact targets, with user batch consent and physical terminal confirmation. No unreviewed mutation.

## Non-negotiable execution boundary

v0.5 research scripts provide only observations; no `--apply`, no production mutation adapters. Real cache deletion requires a separate, explicitly approved exact-target plan through the original trusted executor. No CLI listing, invented synthetic data, shallow lsof result, model confidence or hash alone grants it.
