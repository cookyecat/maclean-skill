# MacLean v0.6 experimental results — Native client references and evidence integrity

**Date:** 2026-10-17. **Host:** authorized macOS arm64, disposable fixtures. **Type:** research E2, not complete real E3.

## 1. Actual Playwright 1.64.1 behavior in an isolated test

A test client was created **only** under an owner-private disposable temp directory. A `.links` entry contained its absolute directory location. The client metadata was copied from the previously pinned, official `playwright-core@1.64.1` installation.

| Condition | Native Playwright `install --list` outcome |
|---|---|
| `.links` with test client manifest but **without** its `package.json`; fake browser dir present | Exit **1**, reported missing `package.json` (path redacted) |
| `.links` with both `browsers.json` and `package.json`; fake `chromium-1248` directory present | Exit **0**, listed that browser directory and its client reference |
| Fake browser has **no executable**, only directory | Native list can still include it |
| Full real system's Playwright client dependency set | **UNKNOWN** |

The pinned Playwright implementation's `_traverseBrowserInstallations` reads link file values as client paths, loads `browsers.json` there, and reports relevant browser descriptors. This was checked against the package's own source and actual CLI behavior. The exercise did not use the real macOS `ms-playwright` cache or read any user project manifests.

**Privacy consequence:** a tool branded as a cache list may read client metadata outside the selected cache. MacLean must not presume publisher CLI traversal itself obeys its Privacy Safe leaf boundary. All raw native output remains local to the isolated experiment.

## 2. Executable identity counterexamples

| Synthetic evidence | Independent check | Can claim genuine browser? |
|---|---|---|
| Native browser list entry | Browser executable missing | **No** |
| Synthetic file in browser cache, not executable | Present file but no execution mode | **No** |
| Synthetic file with executable mode set | `EXECUTABLE_MODE_ONLY` | **No**: neither valid binary structure, platform signature nor publisher provenance verified |
| Symlink to another location | `SYMLINK_DENIED` | **No** |
| Relative `../` escape | `INVALID_RELATIVE` | **No** |
| Attempt to use actual Home as fixture root | `OUTSIDE_DISPOSABLE_FIXTURE_DENIED` | **No**, no user data accessed |

All checks are no-mutation metadata checks restricted to disposable folders.

## 3. Evidence envelope and failure modes

Experimental HMAC-SHA256 sealing catches payload modification and wrong-key checks; source ID and opaque subject binding, maximum age and nonce-set tracking reject wrong subjects, stale/future reports and replay.

**Strict interpretation:**
- A valid HMAC can demonstrate record integrity under a secret held outside the model; it does **not** authenticate the sensor, source content, full E3 coverage or future workload inactivity by itself.
- No production signer is installed; no persistent key or user secret is used.
- Synthetic observations cannot assert that real cache was checked. `coverage_complete=true` is disallowed in the v0.6 contract.
- `NOT_OBSERVED_SHALLOW` remains KEEP, `POSITIVE_OPEN_REFERENCE` remains DEFER, never automatic deletion.

## 4. Independent Playwright .links guard

The fixture-only guard rejects: links outside exact client allowlist, symlinked link files, symlinked **parent directories** (before child metadata probes), missing/bad `package.json` or `browsers.json`, oversized/duplicate links, missing `.links`, world-readable fixture root and malformed IDs. It outputs aggregate counts only and never a production plan.

## 5. Tests and release scope

- **46/46 regression tests passed on the authorized Mac** (29 evidence/identity tests and 17 client-link boundary tests).
- GitHub offline CI should mark the pinned native CLI fixture test skipped when its disposable Mac-only dependency is absent; a skipped native check is not a passed publisher E2 on GitHub.
- Original v0.5 native Puppeteer phantom-list result and partial positive-only `lsof` remain valid, but this v0.6 research did not update the user's actual cache or claim newer full real E3.
- No real browser binary downloaded, no cache deletion or service termination. The only E2 side effects are disposable test files.

**Conclusion:** Better file and client-reference evidence is possible without exposing user details, but native CLI list and a sealed JSON document do **not** complete E3. Trusted, authorization-scoped client metadata acquisition and revalidation remain prerequisite to a default cleanup recommendation.

### Public publisher references
- https://playwright.dev/docs/browsers
- https://pptr.dev/browsers-api
