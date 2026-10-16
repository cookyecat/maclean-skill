# MacLean Decision Engine v0.4 · Application-Scoped Operations

**Status:** frozen exploratory research candidate (2026-10-17). **Not a production cleanup adapter.**

> **用户不用懂技术，AI 能判断得准，程序能删得安全。**

This branch extends [v0.3 E1–E3 evidence](../decision-engine-v0.3/RESULTS-v0.3.md) without modifying released MacLean binaries, the frozen design diagrams, or the production cleanup executor.

## Research question

Given an AI recommendation to remove a *specific* old browser build, how do we know an application-native cleanup operation will touch **only** the user's approved target, while leaving other browser versions required by client workloads intact?

AI deciding a cleanup is desirable, a publisher method covering the intended scope, and the original execution safety gate are **three separate decisions**.

## Seven typed operations

The [registry](operation_registry.py) removes the ambiguous `NATIVE_CLEAN` abstraction:

| Typed operation ID | Publisher-documented conceptual scope | Research gate |
|---|---|---|
| `uv.cache.prune` | uv-defined unused entries; may include cached project environments | uv E2 isolated fixture, **no real E3** |
| `uv.cache.clean_all` | Entire selected uv cache | uv E2 isolated fixture, **broad** |
| `puppeteer.browsers.uninstall_build` | Publisher uninstall API targeting a selected build | No actual bounded native uninstall fixture |
| `puppeteer.browsers.clear_all` | All installed browser builds in the chosen Puppeteer cache | Overbroad if approval selects only one |
| `playwright.browsers.uninstall_client` | Browser set of a selected Playwright installation | Client-scoped; may still be shared/referenced |
| `playwright.browsers.uninstall_all` | Browser builds belonging to Playwright installations | Overbroad for single-target approval |
| `playwright.browsers.gc_unused` | Playwright-managed stale browser garbage collection | **Dynamic/unverified precise touched set** |

Official documentation:
- https://docs.astral.sh/uv/concepts/cache/
- https://pptr.dev/browsers-api
- https://playwright.dev/docs/browsers

**Important:** This table describes publisher behavior, not a claim that actual native command invocation will have exactly the same effect as the synthetic graph preview. The registry never returns an executable command.

## Synthetic browser dependency graph

The [bounded fixture](synthetic_dependency_graph.py) creates a fresh, private 0700 temporary directory with exactly three made-up browser builds:

```text
Synthetic browser installation set
  chrome-0999  ← no synthetic client references
  chrome-1111  ← used by web-research and qa-suite
  firefox-1542 ← used by qa-suite
```

The test manifest format is **invented for MacLean's research**; it is **not** Puppeteer's or Playwright's on-disk registry format. Each graph explicitly declares its app family, so operations from one tool cannot be applied to the other's graph. It assumes a complete *fixture-only* client universe, which must **never** be generalized to the real Mac.

Pure `assess(...)` computes a simulated potential effect set, compares it against a synthetic approved target list, and flags currently referenced builds, active/protected IDs, unmapped native operations and missing real-user evidence. It **always** sets `production_eligible=false` and `deletion_authorized=false`. No `apply`, `rm` or browser management CLI is called.

## Results

See [RESULTS-v0.4.md](RESULTS-v0.4.md). Highlights:

- Targeted orphan-build scope matches one exact approved synthetic version, while production permission stays **false**.
- Clear-all and uninstall-all can extend beyond a one-item approval and into versions other simulated clients still reference.
- A Playwright automatic GC method is **not assumed** to have the same effect as a scoped uninstall.
- Dependency graph changed between assessment and proposed operation: revalidation reports `GRAPH_CHANGED_REVIEW_REQUIRED`, even when the old target name remains unchanged.
- Browser file symlink, client manifest symlink, missing version, forged orphan claim, incomplete client universe and world-readable fixture are rejected.

## Reproducibility

Using Python 3.14 or compatible Python 3.11+:

```bash
cd research/decision-engine-v0.4
python3 -m unittest -v test_operations_v04
python3 synthetic_dependency_graph.py
```

Only creates and removes newly generated **synthetic temporary files**. No model provider calls or credentials are needed. The scripts do not accept a live user's Playwright/Puppeteer cache path as an argument.

## Boundaries and next experiment

- No read-only real browser dependency map yet. Real Playwright version reference tracking is a publisher capability, but the synthetic JSON cannot be presented as a live validated client map.
- No Playwright/Puppeteer native uninstall/clear experiments have been executed; their real side-effect scope is still E1, not E2.
- A graph SHA-256 is an internal drift indicator, **not** a signature or trustworthy independent E3 attestation.
- No private Home, Library, user project, browser profiles, or live process trees were scanned.
- No real cleanup or process stop. This research does not support production automatic deletion.
- The next stage should verify precise publisher-native browser **list** output and client-usage evidence on **authorized disposable installations**, checking whether CLI dry-run / list data can bound an operation. Keep `PLAYWRIGHT_SKIP_BROWSER_GC` and multiple client versions in negative coverage.
- Only then design an explicit immutable plan digest and signed/attested E3 sensor boundary that the original executor could verify separately; preserve user batch approval and terminal confirmation.

This research respects the [frozen philosophy](../../docs/research/PRODUCT-PHILOSOPHY-v1.md) and two [UI baseline diagrams](../../docs/research/AI-DECISION-STATES-v1.md).
