# MacLean · AI Decision Engine Research v0.1

**Branch:** `research/decision-engine-eval-v0.1`  
**Based on:** frozen [Product Philosophy](../../docs/research/PRODUCT-PHILOSOPHY-v1.md), [Decision States](../../docs/research/AI-DECISION-STATES-v1.md), [One-Batch UX](../../docs/research/ONE-CLICK-CLEANUP-UX-v1.md).

> **用户不用懂技术，AI 能判断得准，程序能删得安全。**

## Research question

Can an LLM **select low-risk worthwhile cleanup opportunities** while preserving strong independent safety vetoes, instead of simply recommending every triage `REVIEW` item?

**Important:** This is an *offline evaluation harness*, not a release, agent implementation, real-time scanner, permission grant, or cleaner. It does not use model keys or execute cleanup. v1.3.1 remains the published stable version; v1.4 is still a candidate.

## What was implemented

- [Evaluator](evaluate.py) with strict three-state schema: `RECOMMEND`, `DEFER`, `KEEP`; comparison against researcher-authored expectations; refusal of missing/invented evidence ID in **recommended** items; independent preflight audit of recommendation safety.
- [20 hypothetical cases](cases.synthetic.json) covering uv, npm, Codex, Cursor, npx, Puppeteer, browser/Feishu profile, app update, offline media, symlink, Cargo and unmeasured targets.
- [Blind model inputs](cases.blind.json) with expected labels **removed**; use only these inputs when asking a model to predict.
- [Illustrative expected outputs](predictions.illustrative.json), copied from hand-authored example labels **for checking the tool**. Do not report their accuracy as model performance.
- [Adversarial outputs](predictions.redteam.json) for testing that dangerous recommendations fail.
- [Original unit tests](test_evaluate.py) covering 10 failure and positive controls.
- [Expanded adversarial tests](test_evaluator.py) (12 additional tests); 22/22 offline tests pass.
- [Additional 18-case synthetic dataset](fixtures/cases.synthetic.v0.1.json) with [handcrafted oracle](fixtures/predictions.oracle-control.json), [recommend-all](fixtures/predictions.overeager-control.json) and [keep-all](fixtures/predictions.timid-control.json) controls.
- [Blind export helper](make_blind_input.py) removes gold labels from the new synthetic corpus.
- [Cross-baseline results](RESULTS-v0.1.md) includes all five controls and explicit limitations.
- [Methodology & metrics](METHODOLOGY.md), [model protocol](MODEL-BLIND-TEST-PROMPT.md), and [real cleanup observation](TRIAL-001-OBSERVATION.md).

## Run offline (Python 3.10+ syntax)

```bash
cd research/decision-engine-v0.1
python3 -m unittest -v test_evaluate test_evaluator
python3 evaluate.py --cases cases.synthetic.json --predictions predictions.illustrative.json
python3 evaluate.py --cases cases.synthetic.json --predictions predictions.redteam.json
python3 evaluate.py --cases fixtures/cases.synthetic.v0.1.json --predictions fixtures/predictions.oracle-control.json
python3 evaluate.py --cases fixtures/cases.synthetic.v0.1.json --predictions fixtures/predictions.overeager-control.json
python3 evaluate.py --cases fixtures/cases.synthetic.v0.1.json --predictions fixtures/predictions.timid-control.json
```

The adversarial invocation intentionally returns exit code **3** because it detects dangerous recommendations. Input/schema errors return **2**; passing quality gate returns **0**. No command triggers cleanup or filesystem scanning.

## First evaluation result (research baseline, not a model benchmark)

| Run | Samples | Critical false recommendations | Safety/evidence gate violations | Gate |
|---|---:|---:|---:|---|
| Illustrative hand-labeled predictions | 20 | 0 | 0 | PASS |
| Deliberately unsafe red-team predictions | 20 | 4 | 17 | FAIL |
| Original + expanded unit tests | 22 | — | — | 22/22 |

**This does not establish LLM accuracy.** It only establishes that the current evaluator detects examples of known bad recommendations and that the sample inputs/outputs are coherent. The next required experiment is a truly independent, blinded model run and adjudicated non-synthetic dataset.

## Product research outputs, separated

1. **Which target?** `RECOMMEND / DEFER / KEEP` with explicit evidence and source strength.
2. **Which strategy?** Native app-level pruning/cleanup when supported, never blindly call `shutil.rmtree` on arbitrary app data.
3. **Can execute now?** Independent executor checks, fresh target state, user batch consent, physical-terminal confirmation.
4. **Was space actually reclaimed?** Record measured allocation, successful deletion, APFS free-space delta separately.

Original two frozen diagrams and product philosophy must not be silently revised because of this research.

## Continuation after 2026-10-17 connectivity interruption

The initial 20-case research baseline has been **preserved and migrated** to the evidence-linked case contract. An independent 18-case synthetic suite was added. The evaluator now checks evidence IDs against annotated case IDs, preferred cleanup method, absence of unproven/offline risks and **at least 80% recommendation recall**; this prevents a no-delete model from achieving a misleading quality PASS. See [full results](RESULTS-v0.1.md).

**Do not conflate these synthetic controls with model evaluation:** model comparison against blinded, independently adjudicated real anonymized evidence is the next phase. This research branch does not allow cleanup or change stable `main`.
