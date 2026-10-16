# Decision Engine v0.6 checkpoint — next session research handoff

**Research branch:** `research/decision-engine-trustchain-v0.6`  
**Base:** `research/decision-engine-native-e3-v0.5`  
**Product law:** **用户不用懂技术，AI 能判断得准，程序能删得安全。**

## Frozen foundation (must not drift)
- [Product philosophy](../../docs/research/PRODUCT-PHILOSOPHY-v1.md)
- [AI three-state decision chart](../../docs/research/AI-DECISION-STATES-v1.md)
- [One-batch confirmation UX chart](../../docs/research/ONE-CLICK-CLEANUP-UX-v1.md)

## Evolution and experiments
- v0.1: independent three-state offline evaluator against synthetic controls; no real AI correctness claim.
- v0.2: anonymous 12-case real Mac blind comparison; both models kept all 12; gold unavailable; revealed missing E3.
- v0.3: official E1 and isolated native uv E2; fictional complete E3 generated 3/9 positive recommendations but method mismatch.
- v0.4: 7 typed publisher operation IDs, synthetic browser/client mapping, exact approved-set checks and TOCTOU drift invalidation.
- v0.5: isolated real Puppeteer/Playwright CLI listings, false-positive Puppeteer installed entry, real shallow positive-only `lsof`, 20/20 tests.
- **v0.6:** proven Playwright CLI follows `.links` to client `browsers.json` and also relies on `package.json` in test; real CLI lists fake browser directory without executable; bounded binary metadata guard and explicit client root allowlist; anti-tamper/freshness/replay research HMAC; 46/46 Mac tests.

## Grounded key findings
1. Official list output can be **incomplete, false-positive or privacy-sensitive**; do not treat it as ground truth.
2. Browser directory/executable mode is not a publisher-signed valid executable.
3. An allowed cache root does not authorize reading client metadata at arbitrary `.links` targets.
4. Parent-directory symlinks require rejection **before** touching descendants.
5. HMAC only protects integrity under a trusted key holder; no signer/separate trust boundary or full host E3 has been built.
6. Freshness and graph source identity must be rechecked at actual proposed operation time. The research branch has no apply adapter.

## Current implementation / evidence
- `research/decision-engine-v0.6/native_e2_fixture.py`
- `research/decision-engine-v0.6/client_reference_guard.py`
- `research/decision-engine-v0.6/evidence_envelope.py`
- `test_trustchain_v06.py`, `test_client_guard_v06.py`
- `RESULTS-v0.6.md`
- All research code confined to disposable-only metadata experiments; **no real deletion**.
- No change to production `cleanup_plan.py`, publicly released `main`, or any established user batch authorization law.

## Next v0.7 must be preregistered
A. Allow exact user-selected **developer project metadata** only with bounded read-only consent and independently checked provenance; no deep browsing of personal profiles or default Home recursion.

B. Real **client-version graph completeness**: absence in partial link inventory is not absence of dependency. Quantify coverage and false negative modes, keep UNKNOWN when incomplete.

C. Trusted E3 sensor: executor-owned process authenticates source readings and plan-specific digest, expiring evidence and retry after state changes; HMAC in a test script is not production sensor attestation.

D. Publisher binary integrity: verify platform-appropriate binaries and signatures without executing unknown payloads. Real platform authenticity requires stronger evidence than chmod+x.

E. Independent prospective human gold: two blind annotators, adjudication, new held-out cases; then dual-model evidence studies. Existing v0.2/v0.3 exposed synthetic cases are not valid held-out gold.

**No real cache may be deleted or users asked to classify paths as a condition for v0.7 research.** User simplicity must emerge from machine-verifiable evidence, without silently bypassing independent executor guards.
