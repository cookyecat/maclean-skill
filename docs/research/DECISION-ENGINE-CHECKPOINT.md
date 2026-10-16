# MacLean AI Decision Engine · Research Checkpoint

**Date:** 2026-10-17  
**Status:** R0 complete — offline decision evaluator and synthetic safety regression  
**Research branch:** `research/decision-engine-eval-v0.1`  
**Review PR:** https://github.com/cookyecat/maclean-skill/pull/3  
**Frozen upstream:** `research/ai-decision-batch-ux-v1`, product philosophy and both architecture/UX diagrams **unchanged**.  
**Stable release:** v1.3.1 on `main`; v1.4 cache-catalog remains separate development candidate.

## What is actually implemented

1. Pure-stdlib `evaluate.py` reads hypothetical candidate records and AI-submitted predictions; computes confusion matrix, recommendation precision/recall, independent preflight flags and quality pass/fail. **It does not call an LLM, audit actual disks, approve or delete anything.**
2. Twenty **synthetic** cases and labeled expectations; separately exported **blind** inputs without correct answers.
3. Ten unittest checks run on Mac in temporary directory — **10/10 PASS**.
4. Example expected-label predictions — **0 critical false recommendations, 0 gate violations** (illustrative only; expected answers were copied into prediction file, so no model result).
5. Intentional unsafe predictions — **4 critical false recommendations, 5 independent gate violations, FAIL**.
6. Exact source/ZIP/manifests in published main and the v1.4 candidate have **not been changed** by this research work.
7. GitHub research PR CI static validation — **PASS**: https://github.com/cookyecat/maclean-skill/actions/runs/38947054287

## Confirmed new findings

- Cleaners need a **strategy selection** layer distinct from AI candidate recommendation and independent execution permissions.
- For uv, vendor documentation offers `uv cache prune`, `uv cache clean`, physical-space preview and warns against manual cache mutations. Future MacLean native cleanup integration is preferable to naïve exact-path deletion when semantics are verified.
- Trial 001, per provided operator log: ~764.6 MiB target allocation deleted; observed APFS net free-space gain ~0.30 GiB. The approximately 40% ratio is an **observational net change**, not a causal reclaim efficiency estimator. Root cause not isolated.
- macOS APFS can share blocks via clones and shares free capacity among volumes; neither alone proves the reason for that one trial's difference.
- CleanMyMac safety database, intelligent default selection and ignore lists offer useful **public design patterns**, not authoritative logic transferable without validating each MacLean target.

## Critical unknowns

- **No actual LLM** has yet been evaluated blindly on the 20 synthetic cases, and the synthetic cases are not an independently adjudicated gold set.
- Application-specific recovery claims are currently **fixture assumptions**; not yet independently verified across app versions.
- Actual application-specific safe-cleanup adapters do **not** exist. Current production-style executor still uses exact-path removal.
- No proof of generalization to other macOS versions, other users, or an automatic one-click release.
- Zero new real user cleanup actions in this research stage.

## Required R1 next steps

1. Collect a privacy-sanitized, permissioned **real-case evaluation set** without exposed private paths; attach vendor evidence and mark its reliability.
2. For safety-critical examples, use two independent human judgments, reconcile disputed labels and freeze a sealed holdout **before** model probes.
3. Use [blind prompt](../../research/decision-engine-v0.1/MODEL-BLIND-TEST-PROMPT.md) to run MiniMax and DeepSeek on identical inputs; document model IDs, reasoning effort, prompts, costs and timing. Existing public synthetic test cannot stand in for sealed holdout.
4. Review hard veto on unsupported provenance and test cases including offline Chrome/Feishu data, active npm/Codex/Cursor, safety-protected fallback versions, symlink and identity drift.
5. Prototype a uv-native strategy contract **in a separate feature branch**, read-only or synthetic-first; do not call real `uv cache clean/prune` without new deletion authorization.
6. Promote to implementation only after critical false recommendations meet safety exit criteria, recall/utility is measured, and frozen product philosophy remains satisfied.

## Session handoff

Read in order: [Product Philosophy](../../docs/research/PRODUCT-PHILOSOPHY-v1.md) → [Three-State Contract](../../docs/research/AI-DECISION-STATES-v1.md) → [One-Batch UX](../../docs/research/ONE-CLICK-CLEANUP-UX-v1.md) → [Methodology](../../research/decision-engine-v0.1/METHODOLOGY.md) → [Evaluator](../../research/decision-engine-v0.1/evaluate.py) → this checkpoint. Do not mistake demonstration PASS for real LLM performance or a deletion authorization.
