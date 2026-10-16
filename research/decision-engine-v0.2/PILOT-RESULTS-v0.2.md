# Blind two-provider research pilot · Results (2026-10-17)

**Important: This is neither a cleaning recommendation nor a real-world model accuracy benchmark.** Only non-sensitive aggregate observations are published here. Detailed candidate records and reasons remain in private local reports.

## Audit baseline

- Source: the shipped v1.4.0 Privacy Safe triage after successful manifest verification. Original script executed read-only; no cleanup requested.
- Real candidates: **32**, with these independent machine statuses:

| Status | Count | Measured allocation |
|---|---:|---:|
| REVIEW | 6 | 785.4 MiB |
| ACTIVE | 21 | 6,310.9 MiB |
| PROTECTED | 5 | 2,040.1 MiB |
| UNKNOWN | 0 | 0 MiB |
| **Total** | **32** | **9,136.4 MiB (≈8.92 GiB)** |

This was collected **after** the previously authorized 764.6 MiB uv-cache cleanup; old 33-item observations must not be silently substituted. Allocation is not recoverable APFS capacity.

## Private blind input

The 12 selected cases: **6 REVIEW, 4 ACTIVE, 2 PROTECTED**. Input properties contain only artifact category, coarse size band, relevant machine state, broad rebuild/offline risk cue and source IDs. No absolute paths, usernames, profile IDs, PID, command line, file contents or raw case-specific byte sizes.

SHA-256 of canonicalized blinded JSON: `8c4e16b86f6b0ba01e854394b7380ef606a055aa3f65844405c52c5ad8888564`.

### Experiment 1: Real minimal evidence (blind)

| Provider | Output | RECOMMEND | DEFER | KEEP | Model request elapsed |
|---|---|---:|---:|---:|---:|
| MiniMax | Valid 12/12 | 0 | 0 | 12 | 9.7 s |
| DeepSeek | Valid 12/12 | 0 | 0 | 12 | 27.9 s |

- Exact 3-state agreement: **100% (12/12)**.
- Cohen's kappa: **undefined**, because both returned a constant label.
- **Ground-truth accuracy, precision and recall: NOT AVAILABLE.**
- Independent offline checks found zero `RECOMMEND` outputs without current-evidence proof. This is a safe abstention observation, **not** evidence of positive cleaning discrimination.

### Experiment 2: Explicitly synthetic evidence contrast

Creates 12 *counterfactual* cases from the selected categories. It adds one official Puppeteer re-download reference and *hypothetical* statements about current network availability, no active usage, and reconstructability for some currently active categories. **These statements are not facts about the user's Mac.**

SHA-256 of canonicalized synthetic contrast: `5968cd0f08996108c18cc33d422271c5f762a6184cfee1695f464d23ede781ef`.

| Provider | Output | RECOMMEND | DEFER | KEEP | Model request elapsed |
|---|---|---:|---:|---:|---:|
| MiniMax | Valid 12/12 | 0 | 0 | 12 | 43.9 s |
| DeepSeek | Valid 12/12 | 0 | 0 | 12 | 24.2 s |

Agreement is also 100%, kappa undefined. The contrast is not a controlled test of truly verified current environment evidence; hence it does **not** justify concluding that either model ignores trusted evidence.

Official public reference for the Puppeteer hypothetical: https://pptr.dev/guides/installation.

## Audit of methodology

- Two providers ran the **same cases and text instruction**, but do not necessarily have comparable compute: MiniMax was configured with `reasoning_effort=max`, DeepSeek used its supported thinking mode. Latencies are single observed calls, **not a speed benchmark**.
- Model results cannot be graded against synthetic labels, which are researcher assumptions. No retrospective relabeling was performed.
- The all-KEEP pattern shows why **safety without decision utility is not enough**: we still need an authoritative evidence layer to distinguish confidently reconstructable and currently unnecessary caches from uncertain ones.
- Observational `REVIEW` status is only a machine-safety filter; no process signal is not proof of no workload dependency.
- The real-case snapshot and both provider result sets remain on Mac local owner-only disk, not public GitHub.

## Negative regression

The v0.2 offline unit tests passed **5/5** on the authorized Mac: deterministic selection, coarse size buckets, agreement-without-gold warning, hard-veto detection and frozen prompt SHA matching.

## Limitations and next experiment

1. Annotate blind real evidence independently, with an auditable adjudication protocol and **UNKNOWN** available rather than forced labels.
2. Add an **evidence sufficiency ladder** backed by source citations and local reversible fixture tests, distinguishing hypothetical facts from verified current-user conditions.
3. Compare models after a richer, fully attested input—not only static `kind/size/status` tuples.
4. Run at least two repeats or crossed orders before making claims about speed or stochastic stability.
5. Keep `cleanup_plan.py --apply` entirely separate from this experiment.
