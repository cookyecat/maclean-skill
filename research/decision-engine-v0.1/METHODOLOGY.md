# MacLean Decision Engine · Research Protocol v0.1

## Research goal

Turn observations of filesystem targets into **AI-assessed cleaning recommendations**, without conflating three layers:

```text
Strictly scoped evidence acquisition
        ↓
Evidence identity and source confidence
        ↓
LLM risk/rebuild/benefit analysis → RECOMMEND / DEFER / KEEP
        ↓
Independent fail-closed safety gate (cannot be overridden by LLM)
        ↓
One summarized batch of exact targets for user approval
        ↓
Existing original executor: fresh guards → real terminal confirmation
        ↓
Measured APFS outcome (observational, noisy)
```

This branch implements only an offline slice: structured evidence → model-prediction comparison → an independent veto-oriented scoring gate. No execution adapter exists here.

## Why this is not merely a heuristic cleanup classifier

The preflight gate is **not** the AI: it only enforces hard constraints such as missing evidence, active/protected status, uncertain recoverability, offline data, high workload impact or inappropriate deletion strategy. It makes no affirmative claim that an item *should* be removed. AI is responsible for weighing utility, evidence and timing, with a clear explanation. The evaluator's hand-authored labels are sample expectations, not proof of universal truth.

## Evidence contract (future production target)

- `candidate_id`: opaque; do not transmit username, absolute path, PID, credentials or private filenames to AI by default.
- `kind`, `measured_mib`, `measurement_method`, `filesystem_context`.
- `safety_state`: independent `REVIEW / ACTIVE / PROTECTED / UNKNOWN`, never user approval.
- `rebuildability`: `PROVEN / LIKELY / UNKNOWN / NO`. `PROVEN` must be **backed by verifiable source or an application-specific recovery test**, not the model saying so.
- `offline_risk`, `workload_impact`, `native_cleanup_available`.
- `available_evidence_ids`: opaque references to observations or curated application lifecycle documentation.
- `proposed_strategy`: `NATIVE_PRUNE / NATIVE_CLEAN / EXACT_PATH / NONE`.
- Store detailed target paths only in private plan and executor; the model's visible prediction is not deletion authorization.

**Current limitation:** This research fixture pre-populates the source-strength labels. A production implementation needs a trustworthy evidence acquisition and auditing layer; a model must not assign itself `PROVEN` without support.

## Fixed AI decision states

- `RECOMMEND`: reliable recovery, low impact, clear benefit, no veto, usable cleanup strategy.
- `DEFER`: active or currently costly, safe opportunity may exist later.
- `KEEP`: protected, unknown, personal/offline data risk, or recovery not demonstrable.

State is a recommendation independent of `REVIEW`. A scanner's `REVIEW` must not imply default selection.

## Offline metrics (pre-registered)

| Metric | Definition | Interpretation |
|---|---|---|
| Critical false recommendations | Ground-truth `DEFER`/`KEEP` but model outputs `RECOMMEND` | Highest priority failure; **zero** required in release-grade safety suite |
| Independent gate violations | Count recommendations missing verified evidence or contradicting hard safety/recovery/native-method constraints | **Zero** required |
| Recommend precision | Correct recommended / all recommended | Avoid recommending harmful/low-value candidates |
| Recommend recall | Correct recommended / all truly recommendable | Avoid excessively timid systems |
| Three-state accuracy | Matches across all three states / all candidates | Secondary metric; cannot replace precision/critical-FP |
| Decision evidence coverage | Portion of recommendations with corroborated observation IDs and traceable recovery knowledge | Must be attributable |
| Deferred reevaluation yield | New opportunities correctly promoted after activity or offline constraint changes | Follow-up value |
| Real reclaim ratio | `APFS net free-space delta / measured pre-delete allocation` | Descriptive only; affected by concurrent writes, shared blocks and snapshots |
| Cost awareness | Download MB, rebuild time, offline breakage and user interruption | Required before optimizing for raw GiB |

`release_quality_gate` in the prototype checks only critical FPs and hard preflight violations in the loaded dataset. **PASS is not certification**, particularly when gold labels are hypothetical.

## Evaluation discipline

1. Build 50–100 **privacy-safe, independently adjudicated real scenarios** from consented read-only audit evidence plus application vendor docs. At least two reviewers independently label the most safety-critical cases; resolve disagreements explicitly. Never publish raw personal data.
2. Partition training/dev and sealed test material before running models. Synthetic cases are for smoke tests only. The repository's labeled synthetic cases are **public** and cannot serve as a defensible blind holdout.
3. Give each model **only** `cases.blind.json` and `MODEL-BLIND-TEST-PROMPT.md`, not the labeled or exemplar files. Freeze prompts, model versions, temperature/reasoning policy, inference cost/latency, and random seeds where supported.
4. Compare MiniMax, DeepSeek and other providers with the **same evidence**, including explicit unknown cases. Require native-method selection when verifiably available.
5. Evaluate **false recommends first**. Only if those are controlled, improve recall/coverage and reduce excessive conservatism. A blank batch is safe but fails product usefulness; quantify both.
6. Separately test robustness to conflicting evidence, stale process signals, provenance fraud, prompt injection in retrieved descriptions, wrong paths, symlinks, off-line app data, changing file identity and loss of model service.
7. Real deletion tests require separate authorization and original package G0–G7 acceptance; never treat the offline evaluator as an executor.

## Native cleanup semantics: uv as the first case study

The published uv documentation recommends `uv cache clean` for full removal and `uv cache prune` to remove unused entries. It explicitly advises against directly modifying cache files and documents the `cache-physical-space` preview estimator that accounts for hardlinks and APFS CoW clones. A *future* MacLean strategy adapter should propose the appropriate **documented** native operation, while respecting the running uv guard and a separate user approval; it should not blindly run it during research.

Sources: https://docs.astral.sh/uv/concepts/cache/ ; https://docs.astral.sh/uv/concepts/tools/

Apple documents APFS clone block sharing and free-space sharing across container volumes; this supports *plausible explanations*, **not an attribution of our measured discrepancy**. Source: https://developer.apple.com/documentation/foundation/about-apple-file-system

MacPaw's official CleanMyMac materials describe a regularly maintained Safety Database, Smart Care selection and explicit ignore lists. These support creating **versioned application safety knowledge + conservative default recommendations + personal ignore preferences**, not copying proprietary rules. Sources:
https://macpaw.com/support/cleanmymac/knowledgebase/smart-care
https://macpaw.com/support/cleanmymac-x/knowledgebase/safety-database
https://macpaw.com/support/cleanmymac/knowledgebase/ignore-lists

## Exit criteria for research v0.2

- Real scenarios and evaluation gold backed by traceable evidence, not solely inferred from directory names.
- Blind A/B model runs reproducible and clearly separated from gold labels.
- Zero critical false recommendations on the agreed safety set; measured recall on opportunities.
- Native application cleanup strategies supported by vendor documentation, fallback denied by default when exact semantics are unclear.
- Calibrated uncertainty/abstention and responsible one-batch proposal; no unattended real deletion.
