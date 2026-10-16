# Research handoff — MacLean Decision Engine v0.7

**Date:** 2026-10-17
**Branch:** `research/decision-engine-project-e3-v0.7`
**Base:** `research/decision-engine-trustchain-v0.6`
**Frozen product principle:** **用户不用懂技术，AI 能判断得准，程序能删得安全。**

## Accumulated design and experiment trail

- v0.1: independent 3-state synthetic evaluator; catches over-eager delete-all and timid keep-all control.
- v0.2: real but anonymized 12-case model blind comparison, both models KEEP all; no human Gold.
- v0.3: original manufacturer/publisher E1 and uv E2 disposable native prune/clean; richer **synthetic** E3 elicited selective recommendations, but methods were often mismatched.
- v0.4: seven typed app-specific methods, exact approved-set scope and synthetic browser client graph with TOCTOU denial.
- v0.5: actual pinned Puppeteer/Playwright native CLI. Puppeteer listed a non-existent binary; Playwright native list depended on `.links` and client metadata. Partial positive-only lsof on exact technical cache leaves; no complete E3.
- v0.6: tested pinned Playwright client metadata and fake browser revisions, rejected symlink parent, and built **research-only** HMAC/nonce/freshness demonstration (46 tests on Mac).
- **v0.7:** explicitly selected synthetic project metadata scan; no unselected .links targets dereferenced; official pinned Playwright manifest 7 descriptors ingested in disposable fixture; plan digest + challenge + TTL + HMAC + live re-read invalidate stale evidence; 34/34 Mac tests.

## Architecture invariants — MUST remain true

1. Machine safety status and AI decision (RECOMMEND/DEFER/KEEP) remain independent.
2. Application-specific method scope must equal the approved exact target set, not generic `NATIVE_CLEAN`.
3. **Incomplete client coverage is UNKNOWN**, not verified idle; native CLI success / failure cannot resolve it.
4. Executable mode, directory names and native list entries are **not publisher binary authenticity**.
5. No AI self-attested E3. HMAC in the same user process proves neither trusted capture nor clean authorization.
6. Original executor guards, user exact-batch approval and terminal confirmation cannot be bypassed.
7. No automatic cleanup or private-profile scanning added by research; original stable `main` unchanged.
8. Ordinary users need one coherent recommendation, not dozens of technical per-cache decisions.

## Exactly what was and wasn't done

**Done:** fake disposable project metadata scanning, read of a previously pinned Playwright 1.64.1 manifest from a v0.5 private test package, 34 local tests, research GitHub branch/CI/PR, checked source and experimental uncertainty.

**Not done:** read real project files; build a trusted separate E3 authority; demonstrate full installed-browser client universe; verify real browser signature/rebuildability; evaluate two models against independent adjudicated real Gold; modify the production executor or delete any real cache.

**Risk to fix before real project integration:** `project_witness.py` uses conventional lstat/is_symlink/is_dir path checks that are not resistant to arbitrary adversarial races in writable directories. Upgrade to dirfd-based no-follow operations and verify all components during capture.

## v0.8 preregistered direction

- Bounded exact-project opt-in reader, with explicit user's authorization and careful privacy minimization, no browser Profiles; root mounted per-project not broad Home or arbitrary `.links` target.
- True executor-owned sensor process separate from LLM, process/code provenance and plan-nonce binding, immediate revalidation; HMAC API alone insufficient.
- Coverage ledger with proof of observation versus non-observation, app-specific browser binary authenticity and reinstatement cost.
- Fresh independent human Gold and repeated model comparisons, with user-facing three-state batch behavior unchanged.

**Safety stop condition:** any unexpected private folder traversal, attempt to generalize from unknown clients, invalid scope, missing trusted evidence, or live process state mismatch excludes the target from the recommended batch.
