# MacLean Decision Engine v0.7 — Exact-Project Evidence & Plan-Bound Freshness

> **用户不用懂技术，AI 能判断得准，程序能删得安全。**
>
> **Status:** Research only. No real-project scanning, no new deletion permission.

## Why v0.7

v0.6 demonstrated that the real Playwright CLI may follow `.links` outside its browser cache to a client installation containing `package.json` / `browsers.json`, and a native browser list can still show missing browser binaries. An HMAC can detect tampering but is not proof that the observation came from a trustworthy independently isolated E3 sensor.

v0.7 tests two separate hypotheses **only on fresh synthetic private project fixtures**:

1. Can an explicitly selected Playwright client be read without following unrelated `.links` targets, including paths pointing at Home?
2. Can evidence be bound to a specific research plan and challenge, with live re-scan invalidation when the client graph changes?

**We did not select or inspect any real developer project this turn.** The future real-project reader is not implemented and must require a separate exact-scope privacy review and authorization.

## Code

| File | Purpose |
|---|---|
| [project_witness.py](project_witness.py) | Synthetic-only exact client allowlist; fixed `node_modules/playwright-core/{package.json,browsers.json}` metadata; compare unknown `.links` target strings without dereferencing them; preserve partial coverage |
| [pinned_metadata_e2.py](pinned_metadata_e2.py) | Reuse v0.5's installed pinned `playwright-core@1.64.1` metadata **in a new disposable fixture**; no new package/browser downloads |
| [fixture_attestation.py](fixture_attestation.py) | Experimental issuer reads its own fixture (not arbitrary model claims), binds SHA-256 plan digest and request nonce, applies HMAC and TTL and **re-reads the fixture** during verification |
| [test_project_e3_v07.py](test_project_e3_v07.py) | 34 safety, scope, metadata, drift, replay and integrity regressions |

## Experiment boundaries

- Temporary root is marker-protected `maclean-v07-fixture-*`, mode 0700 and directly under the OS temp directory. No arbitrary root is accepted.
- A selected client must match an exact allowlisted opaque ID and have strictly bounded package/browser metadata.
- The client link list can contain *unknown* targets; those are counted as unknown and **never read, stat'ed or resolved**. New or missing links invalidate fresh evidence.
- All results report `real_client_universe_complete=false` and `deletion_authorized=false`.
- The plan-specific attestation demonstrates **integrity and freshness**, not actual source authenticity or a production authorization scheme. The secret remains in the same test user's process context; a genuine trusted executor/sensor isolation boundary is absent.
- The fixture uses ordinary filesystem path checks and remains vulnerable to possible adversarial race conditions without a fully openat/dirfd-based capture; it is **not a safe parser for hostile real directories**.
- No `lsof` negative result is promoted into idle/recoverable state. No user cache was modified.

## Reproduction

```bash
cd research/decision-engine-v0.7
python3 -m unittest -v test_project_e3_v07
python3 project_witness.py
python3 fixture_attestation.py
```

The optional pinned Playwright native-metadata E2 test runs only when the previous private macOS test package root exists. GitHub CI correctly **skips** that Mac-only test when it is unavailable; all remaining tests require only Python's standard library.

## Current measured findings

See [RESULTS-v0.7.md](RESULTS-v0.7.md). The actual pinned package had seven browser descriptors. Selecting one disposable client does not prove every other Playwright client on the machine is known. The HMAC-scoped preview correctly rejects changed client metadata or new links **on re-verification**, but still cannot authorize deletion. Any further drift after verification would require recheck at the actual executor commit boundary.

## Next-stage acceptance contract

- Implement opt-in **single real-project** source observation with a dedicated Privacy Safe contract; no broad Home search, personal Profiles or recursive enumeration. Programmatic selection should be silent and safe when possible, not require users to understand technical directories.
- Use directory-file-descriptor based, no-follow bounded reads and source ownership checks; report access failures explicitly.
- Design an executor-owned, actually isolated sensor identity and a plan/nonce proof accepted only from its own trusted process. Model-generated JSON must not be signable as E3.
- Measure real-client coverage limitations across Playwright and Puppeteer with independent evidence, not a blanket “no other clients” claim.
- Collect new, prospective **independent human Gold**; dual-model agreement cannot replace adjudicated correctness.
- Keep the original AI three-state and one-batch safety confirmation UX frozen.

References: [Playwright browser management](https://playwright.dev/docs/browsers) and [Puppeteer browser APIs](https://pptr.dev/browsers-api).