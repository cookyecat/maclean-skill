# MacLean Decision Engine v0.6 — Browser Identity & E3 Evidence Trust Chain

> **用户不用懂技术，AI 能判断得准，程序能删得安全。**
>
> **Status:** research only; no new cleanup authorization or production integration.

## Research problem

Previous iterations established:

- v0.3: E1 publisher documentation and disposable uv E2, but synthetic model recommendations often selected incompatible browser cleanup methods.
- v0.4: typed cleanup operations, exact synthetic effect-vs-approved-set comparisons, and dependency TOCTOU.
- v0.5: real publisher-native Playwright/Puppeteer list calls. Puppeteer can list a fake build directory without a browser executable; shallow `lsof` positives are useful but negatives do not prove unused.
- **v0.6:** examine how publisher-native browser lists consult **client metadata outside browser caches**, verify file-type/mode and symlink constraints on a disposable browser fixture, and test integrity/replay/freshness of a research evidence envelope.

Core distinction: **published list entry ≠ executable existence ≠ genuine browser integrity ≠ complete client dependency information ≠ current safe-to-delete state**.

## New experiments (real publisher CLI; disposable only)

The [native E2 fixture](native_e2_fixture.py) uses **pre-existing pinned packages from the earlier v0.5 disposable installation**, not the user's project or shared caches:

- `playwright-core@1.64.1`
- `@puppeteer/browsers@3.2.5` (validated as part of pinned root identity)

The script creates a new, owner-private, disposable browser-cache/client fixture. Its fake browser folder `chromium-1248` contains **no executable**. It creates a fixture `.links` entry with an **absolute path** to a local disposable test client whose metadata was copied from the pinned Playwright package.

Observed on macOS: Playwright's real `install --list` succeeds after the test client has both `browsers.json` and `package.json`. It displays the deliberately fake browser directory and **includes the client path** in native output. Missing `package.json` caused an error; no real browser binary was downloaded or launched.

The [independent binary check](native_e2_fixture.py) distinguishes:
- missing executable,
- existing but non-executable fixture file,
- executable-permission fixture file **which is still not authenticated as a browser**,
- symlink denial and `../` path escape denial,
- rejection of non-disposable user Home paths.

A native list is **not trusted by itself**.

## Real Playwright client reference privacy boundary

Inspection of **pinned `playwright-core@1.64.1` source** revealed: its `.links` files hold client directory locations; `install --list` traverses those client references and reads browser metadata. In this version, the list path may also require `package.json`.

**Do not run the publisher's native list against an arbitrary real-user cache in Privacy Safe mode.** Even a nominally read-only command may read outside that cache via client metadata references or include paths in output.

The [client reference guard](client_reference_guard.py) is not a production Playwright parser. It tests the correct future boundary: only private fixture roots, only declared `client-*` directories, reject parent symlinks before child lookup, no arbitrary absolute link targets, bounded manifests, no raw path output and **never** claim the real host's client universe is complete.

## Evidence origin, integrity and expiry

The [research envelope](evidence_envelope.py) demonstrates HMAC-SHA256 integrity, opaque subject identity, source allowlisting, short TTL, replay nonce detection and closed evidence schema.

**Crucial limitation:** integrity **is not** source authenticity. It is only meaningful if a separate trusted process controls the secret and captures evidence itself. This v0.6 branch has **no deployed independent sensor signer**, no key-management scheme, no signed production E3, and no actual browser completeness/integrity proof. A model cannot self-attest evidence. All records explicitly report `deletion_authorized=false`.

## Files and reproduction

- [native_e2_fixture.py](native_e2_fixture.py): actual publisher Playwright CLI run on disposable fake browser and test client.
- [client_reference_guard.py](client_reference_guard.py): path-scope checks before any linked client manifest read.
- [evidence_envelope.py](evidence_envelope.py): HMAC-sealed experimental evidence, freshness and anti-replay.
- [test_trustchain_v06.py](test_trustchain_v06.py) and [test_client_guard_v06.py](test_client_guard_v06.py): **46 local Mac regressions**.
- [RESULTS-v0.6.md](RESULTS-v0.6.md): measured results, nonclaims and failure cases.
- [RESEARCH_CHECKPOINT-v0.6.md](RESEARCH_CHECKPOINT-v0.6.md): accumulated progress and next research gates.

```bash
cd research/decision-engine-v0.6
python3 -m unittest -v test_trustchain_v06 test_client_guard_v06
```

GitHub CI executes all portable tests without dependencies or network access. The native Playwright CLI regression **only** runs when the previously authorized disposable pinned package fixture is available; otherwise CI correctly marks it skipped rather than claiming successful native E2 on its runner.

## Current boundary

No real user cache, personal profile, project file or stored credentials were inspected by v0.6. Experiments read only the previously downloaded pinned packages and their own new synthetic temp directories. No real browser download, install, uninstall, cache clear, service stop or `cleanup_plan.py --apply`.

## Next milestone v0.7

1. Propose an **opt-in, exact-project** metadata observation adapter under privacy review. Decline unselected project paths and browser Profiles, avoid broad Home recursion.
2. Check precise Playwright client-to-browser revisions and publisher-native listing consistency; preserve unknown/partial coverage.
3. Independently assess browser *actual* binary identity (platform signature, provenance, safe version match) with explicit safe source policy; executable mode alone is not integrity.
4. Design an executor-owned sensor signer with actual trust isolation, nonce binding to the approved plan and an immediate preflight recheck; an in-process HMAC library is not enough.
5. Use prospectively frozen, independently annotated new real cases. Repeated model agreement is not ground-truth accuracy.

User experience remains one AI-reviewed batch, one explicit approval and an independent safe executor; ordinary users are never expected to understand `.links` or process internals.
