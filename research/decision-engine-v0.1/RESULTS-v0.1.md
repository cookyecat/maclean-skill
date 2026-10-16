# AI Decision Engine v0.1 · Cross-baseline control report

**Date:** 2026-10-17. **Mode:** offline, synthetic and non-destructive. **Mac:** authorized macOS / Python 3.14.7, isolated test files.  
**No production model has been evaluated yet. No MacLean cleanup was performed in this run.**

## Why two datasets?

The branch already contained **20 researcher-authored hypothetical cases**, 10 tests and a methodology document before network interruption. This continuation **preserves those cases**, while adding a separate **18-case synthetic calibration suite** intended to catch two trivial ways to game safety metrics: always recommend everything or never recommend anything.

The evaluator contract was strengthened to check:
- labels and prediction IDs match exactly; all recommendations cite case-listed evidence IDs;
- `RECOMMEND` respects safety state, rebuildability, offline risk and workload impact;
- cleanup strategy matches allowed method; if native cleanup is part of a scenario, the evaluator can reject indiscriminate exact-path removal;
- **zero** erroneous RECOMMEND results and **zero** gate violations, plus at least **0.80 recall** for the human-labeled synthetic recommendations.

These are offline **research gates**, not permission to delete and not proof of real-world reliability.

## Actual on-Mac test results

| Evaluation | Cases | Critical false recommendations | Gate violations | Recommend recall | Result |
|---|---:|---:|---:|---:|---|
| Original manually labeled calibration | 20 | 0 | 0 | 1.0 | PASS |
| Original deliberately unsafe red team | 20 | **4** | **17** | Not used for acceptance | FAIL |
| New hand-crafted oracle control | 18 | 0 | 0 | 1.0 | PASS |
| New over-eager recommend-all control | 18 | **12** | **43** | 1.0 | FAIL |
| New timid keep-all control | 18 | 0 | 0 | **0.0** | FAIL |
| Program unit tests | — | — | — | — | **22/22 PASS** |

The original red-team gate violations increased relative to historical output because the amended evaluator now checks independent evidence and strategy compatibility. These output changes are expected and do **not** mean the older 20-case corpus was rewritten to change its gold labels.

## Blinding check

`make_blind_input.py --cases fixtures/cases.synthetic.v0.1.json` emits 18 scenarios **without** `human_expected`, `label_rationale` or `acceptable_strategies`. The model must provide a separate JSON predictions document. Built-in oracle predictions are deliberately not blind and **must never be reported as model performance**.

The legacy 20-case `cases.blind.json` is also explicitly a synthetic model challenge; it is not a secured holdout dataset.

## Scientific limits

- Source evidence IDs in this suite are synthetic labels, not independently validated file data. The evaluator checks references, not semantic truth or prompt injection resistance.
- The "gold" labels are author-assigned. A true model benchmark needs separate human annotation, ambiguous-case arbitration and locked held-out examples.
- `PROVEN` rebuildability in the fixtures is an **assumption**, not proof that a real user has no offline data.
- Zero test errors in 38 synthetic cases would still not establish a safe-to-delete model.
- The native cleanup strategy requires separate command-level safety research; the evaluator never runs those commands.
- All `PASS` verdicts are scoped to the synthetic checks and may not be shown as production release certification.

## First real cleanup observation (separate from this test)

See [TRIAL-001-OBSERVATION.md](TRIAL-001-OBSERVATION.md), grounded in a user-provided successful single `uv_cache` deletion: **764.6 MiB** measured allocation and **about +0.30 GiB** rounded APFS net gain. The run cannot attribute the gap to any particular filesystem cause.

## Next real experiment

Collect privacy-safe source-backed cases independently of the model under test, freeze ground truth and train/holdout split, compare at least two model runs **blind**, audit every false-positive recommendation, and link the selected cleanup method to a separately verified read-only preview. Keep the production executor and user authorization outside the evaluation harness.
