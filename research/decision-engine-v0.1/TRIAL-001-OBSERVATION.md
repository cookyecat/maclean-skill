# Real cleanup observation · Trial 001 · 2026-10-17

**Data provenance:** User-supplied operator terminal output and the subsequent MacLean/Luna verification summary. This is a **single observational test**, not a controlled filesystem experiment or independent raw-telemetry audit. No usernames, temporary directory names, plan hashes, PIDs or private file paths are reproduced.

## Precondition and reported result

| Field | Observation |
|---|---|
| Candidate category | uv package/build cache |
| Model decision | Recommend only this one cache; other targets excluded |
| Approval | Explicit single-target approval and separate physical-terminal `DELETE` |
| Program | Original MacLean 1.4.0 candidate `cleanup_plan.py --apply`, after reported verification |
| Measured target allocation | **764.6 MiB** (approx **0.7467 GiB**) |
| Execution status | **1 deletion succeeded, 0 failures**, target later confirmed absent |
| APFS available before, as printed by executor | **18.08 GiB** |
| APFS available after, as printed by executor | **18.38 GiB** |
| Observed APFS net increase | **about +0.30 GiB** |
| Follow-up read-only observation | about **18.373 GiB**, compatible with rounded output |
| Native cleanup method used | **No** — original executor removed cache directory directly |

## Measurement semantics

```text
Measured allocation of selected target: 764.6 MiB
Reported actual volume free-space net gain: ~0.30 GiB
Observed net / measured allocation: ~40% (rounded, not causal)
```

Do not infer that 60% was "not deleted." APFS clones/hardlinks/snapshots, shared free space and concurrent filesystem writes can produce differences, but this trial did **not** isolate which factor dominated. We do not infer causal attribution from the before/after delta.

## Engineering consequences

1. Report **requested/successfully deleted measured bytes** separately from **APFS available-space delta**.
2. Distinguish `du` allocation from **physical space reclaimed**, with a documented uncertainty interval where available.
3. Prefer an application's supported native cache interface when semantics are verified. For uv, research `uv cache prune` versus `uv cache clean` and physical-space preview before proposing migration from exact-path deletion. Never invoke those commands merely for metrics in a read-only test.
4. Track operational effects (next use, download bytes, rebuild delays) in future opt-in trials. These were **not measured** in Trial 001.
5. One successful safe deletion is evidence that the **single selected workflow completed once**, not a universal safety guarantee or sufficient validation for v1.4.0 release.

## Follow-up experiment idea

Use two separate, explicitly authorized trials with identical app conditions, one native application cleanup and one exact-path mechanism if justified, and repeat pre/post APFS checks with background writers observed. **Do not** perform further real deletion without separate user approval and native method review.
