# MacLean Decision Engine · Real-evidence blind pilot v0.2

> **Research only. No cleanup, no local file deletion, no production recommendation gate.**

Built on the frozen research product philosophy:
**用户不用懂技术，AI 能判断得准，程序能删得安全。**

## Design goal

Move beyond self-labeled synthetic gold, with two distinct tracks:

1. A real **privacy-minimized** triage snapshot from an authorized Mac; machine state is observed but no independently validated semantic gold is invented.
2. Two-provider blinded judgment on 12 coarse real candidates, and a separately labeled synthetic **counterfactual evidence enrichment** to test sensitivity.

The collector invokes original, manifest-verified v1.4.0 `triage_home.py --json`. It never invokes `--apply`, scans outside the original Privacy Safe scope, reads file payloads, or uses `--details`.

## Source and privacy boundary

- Snapshot and model outputs saved **only on the user's Mac**, mode `0600` under a `0700` temporary research directory. They are **not** checked into public GitHub.
- The public repo includes the programs, their non-identifying aggregate results and provenance descriptions, but **not** the full real cache inventory, usernames, exact paths, PIDs, command lines, profile identifiers, API tokens or exact per-app sizes.
- A second transformation maps 32 candidates to 12 cases (every REVIEW plus at most four distinct ACTIVE kinds and two distinct PROTECTED kinds). Each case's exact measured size becomes a coarse size band.
- The two external provider calls receive only these minimized 12 case records. No human gold, report path, source filename, local hostname or API key is included in the model prompt.
- Provider secrets are loaded in process memory from existing local RAOS configuration and suppressed from logs. The provider endpoint hostname is allowlisted; no secrets are committed.
- This experiment explicitly does **not** establish full privacy or endpoint security for every configuration. It reflects the limited, inspected payload here.

## Programs

| Script | Role |
|---|---|
| [collect_real_snapshot.py](collect_real_snapshot.py) | verify original v1.4 bundle; execute original read-only triage; store reduced private evidence |
| [prepare_blind.py](prepare_blind.py) | stratified sample and coarse redaction; freeze SHA-256 of exact model input |
| [run_provider_probe.py](run_provider_probe.py) | optional HTTPS MiniMax or DeepSeek probe; no cache cleanup capability |
| [compare_blind.py](compare_blind.py) | two-provider state counts and disagreements; **does not calculate accuracy** |
| [make_evidence_contrast.py](make_evidence_contrast.py) | create a fully **synthetic** counterfactual overlay, never new facts about this Mac |
| [test_blind_v02.py](test_blind_v02.py) | offline no-network unit tests for sampling, size bucketing and guard metrics |

## Pilot results

See [PILOT-RESULTS-v0.2.md](PILOT-RESULTS-v0.2.md) for exact control statistics and [EVIDENCE-LADDER-v0.1.md](EVIDENCE-LADDER-v0.1.md) for follow-up experiments.

This pilot **does not have independent human gold**. Two models agreeing to KEEP cannot imply they are correct; Cohen's kappa is undefined when both predict the same constant label. The model is receiving very sparse evidence: no proof that cached files are independently recoverable or currently irrelevant to the user.

A synthetic overlay with one official Puppeteer installation reference and hypothetical workflow conditions also elicited KEEP-only responses. That finding cannot establish that the models fail to use good evidence, because the extra conditions are explicitly hypotheses and no current-environment attestation exists.

## Usage

Only operate on files you own and on an authorized Mac, and do not publish local snapshot or prediction files. No script executes cleanup.

Run the offline unit tests:

```bash
cd research/decision-engine-v0.2
python3 -m unittest -v test_blind_v02
```

Real audit collection or outbound provider calls should be undertaken only in an independently authorized operator context, after reviewing the provider's data-handling boundaries; no automated GitHub Actions job makes external model requests.

## Next preregistered milestone

Create independent evidence-backed human adjudication for the 12 **masked** candidates, ideally two annotators and a third arbitration stage. Separately test category-specific regeneration on safe synthetic fixtures. Verify that a conservative model changes from KEEP only when *presently valid* source, restore, activity and offline-impact evidence is available. **Do not use generated model labels as human gold.**
