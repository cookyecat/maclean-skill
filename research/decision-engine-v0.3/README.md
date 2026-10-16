# MacLean Decision Engine v0.3 · Verified Evidence and Restore-Method Research

> **用户不用懂技术，AI 能判断得准，程序能删得安全。**
>
> **Branch:** `research/decision-engine-evidence-v0.3`  
> **Status:** exploratory; no real cache cleanup or production execution changes.

## Why v0.3?

In v0.2, both MiniMax and DeepSeek returned KEEP on 12/12 privacy-minimized real candidates. That experiment lacked current reproducibility and workload-usage evidence. It **did not** prove the models are bad at cleaning decisions or that all candidate files are irreplaceable.

v0.3 separates five kinds of evidence:

- **E0:** permitted cache category, size band and coarse process-family signal;
- **E1:** authoritative publisher lifecycle description (capability, not local proof);
- **E2:** independently repeatable **disposable** local maintenance method check;
- **E3:** current target identity, exact-use and recoverability attestations (future operational sensor);
- **E4:** independent original executor recheck, user batch approval and physical confirmation. **Not implemented by this branch**.

`evidence_contract.py` is a narrow fail-closed **research contract**, not an executable cleanup plan. The research inputs must never be allowed to assert E3 directly in production. `attestation_origin` explicitly separates `SYNTHETIC_TEST` from a planned `INDEPENDENT_LOCAL_SENSOR` source. The latter is a **future trust interface only**, with no signer, authorization or production adapter yet.

## Official publisher evidence (E1)

| App | Supported documented behavior | Crucial limitation |
|---|---|---|
| uv | `uv cache prune` removes unused cache entries and centralized environments; `uv cache clean` clears all or selected package entries; the native cache has a lock and is not safe to modify by directly deleting files. | Package reinstall, centralized env recreation, lock state and actual physical reclaim are still workload-specific |
| Puppeteer | Installs compatible Chrome for Testing and headless shell, defaults to shared browser cache; re-download via browser install. | Some package managers suppress install scripts, so browser re-download is not guaranteed by “package installed” alone |
| Playwright | Browser versions depend on client packages; supported automatic stale-browser garbage collection, installed-browser listing and `uninstall` operations. | Real client-to-version refs, current sessions and `PLAYWRIGHT_SKIP_BROWSER_GC` must be examined; blanket deletion is inappropriate |

Authoritative links:
- uv cache: https://docs.astral.sh/uv/concepts/cache/
- Puppeteer install: https://pptr.dev/guides/installation
- Puppeteer configuration: https://pptr.dev/guides/configuration
- Playwright browsers: https://playwright.dev/docs/browsers

**Important:** An E1 statement that a cache *can be downloaded* does not establish that the current user's offline state, build artifacts or preferred browser revision can be recovered at this instant.

## Actual disposable E2 experiment on macOS

Platform: macOS arm64, local installed uv `0.12.5`. The original production cache path was **not** inspected or modified.

`sandbox_uv_e2.py` always generates a fresh 0700 temp directory with its own marker, uses an isolated `uv-cache` inside that directory, forces `--offline --no-config --cache-dir <fixture>`, excludes `--force`, and calls native `cache prune` and `cache clean` **only** there.

Observed results:
- **Native prune: PASS**, **native clean: PASS**; neither command touched real caches.
- External sentinel preserved; target guard rejected 3 invalid paths and symlink to Home.
- A synthetic test child opens a disposable file; PID-scoped `lsof` successfully detects its **exact open-file reference**. No real process-wide file lists are output or retained.
- All operations were on a disposable fixture. Cleanup is performed automatically only on these created test files, never on the user's data.

**E2 limit:** This proves that the installed uv binary accepts and operates on an isolated cache location and that exact-open detection is technically feasible. It **does not** prove installed package restoration, cache contents classification, user downtime, actual reclaim, or absence of open files on the user's real caches.

## What v0.3 does *not* yet implement

- No real E3 sensor for production paths or false-negative proof for `lsof`. A file not open in `lsof` can still be required by a future job.
- No Puppeteer or Playwright binary download, version inspection or cache GC on the real Mac.
- No native-cleanup `--apply` adapter, no automatic temporary credentials, no browser profile scan, no process termination, no user-file cleanup.
- No independent held-out human Gold. Synthetic scenario predictions are **not** a real accuracy benchmark.
- No assumptions that an AI can attest to E2 or E3 via free-form text.

## Pilot: synthetic E0/E1/E2/E3 decision ladder

`ladder_cases.synthetic.json` defines 9 **entirely hypothetical** combinations (document-only, fixture-only, full E3 hypotheses, ACTIVE, PROTECTED, and offline Profile). It sends no user files to providers. Source citations are public publisher links; hypothetical local checks are explicitly tagged as synthetic, not verified about the Mac.

Run `run_synthetic_probe.py` **only** in an authorized operator session with existing provider configuration. Store all outputs privately. Do not use them to approve or run cleanup.

The purpose of these cases is to test whether a model can **change its recommendation as trustworthy evidence increases**, without losing ACTIVE/PROTECTED vetoes. Results live in `RESULTS-v0.3.md`.

## Reproducing local evidence without touching user caches

```bash
cd research/decision-engine-v0.3
python3 -m unittest -v test_evidence_v03
python3 sandbox_uv_e2.py
```

Python standard library only; uv and lsof are optional system tools. CI that lacks uv cannot claim E2 was tested (the uv-specific check is skipped). On macOS, subprocesses run with a fixture-only `HOME` and `UV_CACHE_DIR`, and uv is forbidden from network access for the test.

## Next research objective

1. Devise **read-only** independently generated E3 attestations of exact identity, current browser-version usage and offline dependence, with raw paths retained only on operator's Mac.
2. Validate native cleanup scope with reversible fixtures and negative tests, not by deleting active user caches.
3. Obtain independent prospective gold for a new held-out real anonymized cohort; compare multiple providers blind, without retrospective label editing.
4. Only after E3 sensor precision and user authorization are verified consider optional **native app-maintenance adapters** behind the executor's existing hard gates.
