# MacLean · Evidence sufficiency ladder v0.1 (research contract)

**Goal:** preserve the frozen product philosophy while allowing real automated usefulness:
**用户不用懂技术，AI 能判断得准，程序能删得安全。**

## Three distinct questions

1. **What is this artifact?** Identity, publisher-specified role, exact safe leaf, size, provenance.
2. **Could it be rebuilt, with what consequences?** Source-backed application lifecycle, current environment and offline/re-download dependencies.
3. **Is now a good time?** User workload and system activity; exact-path references, active processes, resource cost and expected physical reclaim.

Only after all three are answered may AI put a case into a default batch recommendation; the original script independently revalidates hard vetoes.

## Evidence levels

| Level | Name | What counts | What does NOT follow |
|---|---|---|---|
| **E0** | Unknown / label only | Filename or cache category, size, coarse process family match | No assurance that cache is reconstructable |
| **E1** | Publisher lifecycle documentation | App's official cache semantics, reinstall/prune/GC commands | The current local files are covered, or user can download now |
| **E2** | Scoped, reproducible local check | Verified package/version/cache identity, matching installed command or a reversible synthetic fixture replay | Production deletion authorization |
| **E3** | Current-use assessment | Fresh process/path evidence, offline/current-job requirements and reinstall network feasibility | A blanket deletion guarantee |
| **E4** | Independent executor permission | Exact plan, user batch approval, live fail-closed guard, real terminal confirmation | AI may bypass executor under any circumstance |

Publisher-documented cache **reinstallability** must not be promoted automatically to **current-user recoverability**. Service Worker CacheStorage may carry offline Web App dependencies; remote sync/reinstallation cannot be assumed merely from its name.

## Concrete follow-up contracts

**Puppeteer browser download cache:** Publisher documents browser downloads, default cache and re-installation. E1 supported by https://pptr.dev/guides/installation and https://pptr.dev/guides/configuration . E2/E3 missing until local browser version mapping, use status and downloadable artifact access are safely checked.

**uv package/build cache:** Publisher documents `uv cache prune` and `uv cache clean`; it explicitly cautions against manual cache modification. E1 supported by https://docs.astral.sh/uv/concepts/cache/ . The original successful Trial #001 used the existing MacLean exact-path executor, not uv's native command. Future integration needs a separate safety contract for native operations, including lock contention and physical reclaim estimation.

**Playwright browser runtime:** Publisher documents OS cache location, browser version coupling, reinstallation and stale-client GC. E1 supported by https://playwright.dev/docs/browsers . E2/E3 require precise version-client linkage and application use checks, not generic deletion of the whole directory.

**Feishu/Chrome Profile CacheStorage:** E0/E1 may provide Web API storage semantics, but cannot establish all offline app assets or unsynced state are recoverable. Default KEEP/DEFER pending app-specific verification.

## Research requirements

- All evidence citations must be source IDs rooted in verified local audit or named public publisher documentation. No model-invented source IDs.
- Preserve provenance granularity: official doc `E1` is not user activity `E3`; hypothetical scenario assumptions never count as observed evidence.
- Independent human annotation must precede comparison with model outputs; use blind labels and a disagreement/arbitration step.
- Record time, versions, source hashes, anonymization fields, reviewer judgment and uncertainty.
- Never use more candidate GiB recommended as a proxy for model intelligence.
- AI should be able to distinguish an **unknown but promising** target from a **permanently protected** one; both may be KEEP in the current input, but their missing-evidence plan differs.
- Do not automatically merge any revised execution policy into stable `main`. First prove E2/E3 on disposable fixtures and negative safety tests.
