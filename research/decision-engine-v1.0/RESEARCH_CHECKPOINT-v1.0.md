# MacLean Decision Engine v1.0 — research handoff checkpoint

**Branch:** `research/decision-engine-native-adapters-v1.0`  
**Base:** `research/decision-engine-regenerability-v0.9`  
**Frozen philosophy:** **用户不用懂技术，AI 能判断得准，程序能删得安全。**

## Evolution and purpose

v0.1–v0.7 examined evaluator accuracy, E1/E2/E3, operation scopes and trust constraints; v0.8 established pragmatic CleanMyMac-style DEFAULT/OPTIONAL/BLOCKED selection and an actual unapproved v1.4 executor preview; v0.9 removed coarse `RELATED_PROCESS_RUNNING` veto from **recommendation** for known regenerable types. User explicitly requested this simplification while preserving task functionality.

v0.9 real Mac candidates: 7 DEFAULT / 3,148.1 MiB; 15 OPTIONAL / 2,824.6 MiB; 10 BLOCKED / 3,184.4 MiB, compared to v0.8 DEFAULT 70.3 MiB. These are gross candidate allocations, **not recovery or executor approval**.

**v1.0 goal:** build real application-native mechanics **only in a fresh private disposable fixture**, measure methods and limits, never bypass v1.4 original guards in live Home.

## Files and measured tests
- `isolated_native_lab.py`: owner-private disposable HOME/npm cache/uv cache, exact argv allowlist and path/symlink marker guards; actual npm 12.2.0 `cache npx ls/rm`, `cache verify/clean` and uv 0.12.5 `cache prune/clean` run **only in synthetic cache**.
- `synthetic_runtime_race.py`: running fixture process can lose a lazily loaded file after exact native npx rm. **Therefore runtime disruption is possible even when the cache is recreatable.**
- `native_method_contract.py`: exact known native method-to-leaf mapping; no production authorization or filesystem operation.
- `test_native_v10.py`, `test_method_contract_v10.py`: **28/28 Mac tests PASS**.
- `RESULTS-v1.0.md`, `README.md`: reproducible methods and nonclaims.

## Next gates
1. **Production adapter RFC, not an unsafe patch:** allowlist exact operations, identity and user-batch approval; pass original path privacy validation, symlink refusal, native root reconciliation and stop/abort conditions. Detect current npx entry use narrowly, not blanket `npm` process.
2. **Concurrency:** native npm cache clean's self-healing does not automatically prove full operational safety while other npm tasks run; characterize locks/races in disposable concurrent workloads. uv prune uses uv-native locks; test nontrivial fixture content if feasible before real execution.
3. **Execution:** real user cleanup only after a separate, explicitly approved plan; no `--apply` today, no altered v1.4 process guard, no deletion of running Codex/Cursor binaries.
4. **Measurement:** report native method reclaimed bytes and APFS net change separately; native `npm verify`/uv prune may recover much less than gross cache allocation.
5. **UX:** one clear default/optional/protected batch; ordinary users do not need to inspect CLI keys or E3 diagrams.

## Status
**v1.0 isolated methods and guardrails passed; production execution integration is not implemented or approved.** The original stable `main` and v1.4 package remain unchanged. Prior 70.3 MiB unapproved plan left untouched. No real user caches modified.
