# MacLean Decision Engine v0.5 · Native CLI E2 + Bounded Real E3

> **用户不用懂技术，AI 能判断得准，程序能删得安全。**

**Status:** Research / fail-closed; not merged to stable main, no native deletion adapter. The frozen [product philosophy](../../docs/research/PRODUCT-PHILOSOPHY-v1.md) and two v1 architecture diagrams remain unchanged.

## Research goal and new distinction

Can MacLean independently substantiate **what a publisher-native list command really proves**, and obtain **current-use evidence** without disclosing personal paths or reading content?

Separate the claims:

1. `CLI_LISTED`: Native tool returns a browser entry. May not prove binary existence or integrity.
2. `EXECUTABLE_PRESENT`: Independently observed executable under a verified installation root. Still does not prove runnable, correctly signed or recoverable.
3. `CURRENT_OPEN_REFERENCE`: Read-only OS inspection positively observes an open reference to a known safe technical cache leaf. Hard veto for cleaning now.
4. `NO_REFERENCE_OBSERVED`: Only a *limited* negative signal, never proof of unused cache or absence of future project need.
5. `E3_COMPLETE`: Requires reproducible install identity, current client/version reference map, online/offline recovery, workload conditions, and authenticated source provenance. **Not reached in v0.5.**

The research-only [fail-closed gate](e3_failclosed_gate.py) refuses to transform 1, 2 or 4 into cleanup permission.

## Native publisher E2 lab — actual macOS CLI, disposable only

The Mac did not have standalone Playwright/Puppeteer CLIs in PATH or Python Playwright package available. Rather than invoking `npx` (which may auto-download/install), we created a fresh 0700 `/tmp/maclean-v05-native-e2.*` root and temporarily fetched these **pinned package modules** with npm:

- `@puppeteer/browsers@3.2.5`
- `playwright-core@1.64.1`

**Installation guard:** isolated HOME, independent npm cache, npm package lifecycle scripts disabled (`--ignore-scripts`), no global/project install, no browser binaries downloaded, no real user's original npm/browser caches read or deleted. The packages themselves **were downloaded into the disposable temp root**. This was explicitly a temporary research dependency, not a claim of zero downloads.

Using the actual Node CLI scripts directly:

- Puppeteer `list --help` documents `--path`; `list --path <fixture>` on an empty cache returns success and no entries.
- With a **fake** folder named `chrome/mac_arm-999.0.0.0` (and **no browser executable**), Puppeteer **still lists it as an installed Chrome build**. Verified against 3.2.5 on this Mac. A directory-name-based list can thus be a **false-positive installation signal**.
- Playwright `install --list` returned nonzero against a newly empty root missing the internal `.links` directory. Creating **only** an empty `.links` inside the disposable fixture yielded a successful empty list.
- Playwright `install --dry-run` returned success and printed **proposed install locations**, which must never be interpreted as existing browser builds. Nothing was installed.

Scripts: [native_capability_probe.py](native_capability_probe.py), [native_cli_e2_lab.py](native_cli_e2_lab.py). The latter **does not install npm packages**; it requires the pinned packages already present in an isolated root and has no browser install/delete options. Future runs need a manually prepared throwaway root; CI does not fetch these packages.

Official documentation: https://pptr.dev/browsers-api ; https://playwright.dev/docs/browsers .

## Real read-only E3 sensor

The [e3_positive_sensor.py](e3_positive_sensor.py) only accepts two **exact existing MacLean Privacy Safe technical leaves**:

- `~/.cache/puppeteer`
- `~/Library/Caches/ms-playwright`

No arbitrary target, browser Profile, full Home/Library enumeration, user projects or personal content. It checks symlink components, then uses **`lsof +d`** (direct children only; **not** recursive `+D`) and returns only categories/status counts. Important privacy detail: `lsof +d` **may inspect child entry metadata within these exact technical cache leaves**; the response does not expose child names, process commands, PIDs or paths. No cached payload is read.

Observed on Mac:
- Own disposable child kept a known test file open: `OPEN_REFERENCE_OBSERVED` **PASS**.
- Real Puppeteer catalog leaf: present, `NOT_OBSERVED_IN_SHALLOW_SCAN`. This is **NOT** `unused`.
- Real Playwright default catalog leaf: `ABSENT` at that exact location. This is **NOT** `Playwright never installed`.

Read-only, no services stopped, no real cleanup, no user-file modification. The sensor cannot prove negative absence of dependency, especially for nested handles, sleeping tasks, unsupported alternate caches or future client use. Time and provenance remain explicitly limited.

## Program tests and boundaries

[20 unit regressions](test_native_e3_v05.py) on macOS: all PASS. They check real disposable positive signal, strict target allowlist, symlink rejection, stale/future timestamps, unexpected privacy scope, unexpected scanner categories, unknown sensor states, and absolute prohibition on authorization. GitHub offline CI never downloads packages or queries the user's Mac.

**The native E2 lab demonstrated one false-positive native listing; it did not validate a real browser binary, signature, full project dependency graph, successful browser restoration or executable cleanup method.** The pure research output always has no deletion authorization.

Read [RESULTS-v0.5.md](RESULTS-v0.5.md) and [RESEARCH_CHECKPOINT-v0.5.md](RESEARCH_CHECKPOINT-v0.5.md).

## v0.6 next research: evidence sufficiency, not more folders

1. Publisher-native installed-list parser plus **independent executable existence/type/integrity checks** on disposable builds. Do not infer valid from directory name.
2. Read-only **client-reference graph** from individually authorized project metadata, not personal application Profiles; define privacy rules for path hashing and package manifest reads before enabling. A negative `lsof` remains insufficient.
3. E3 evidence source authenticity / freshness. A SHA of an untrusted JSON record is not attestation. Explore direct executor-owned sensors, per-target snapshots and TOCTOU refusal.
4. Prospective independent human Gold, including KEEP/DEFER/RECOMMEND with `UNRESOLVED`, for the next unused fresh anonymized sample set.
5. Only after verified method semantics, exact approval scope and live recheck should native operations even be considered for an executor RFC.

No future research step may override: **AI judges value, application-specific adapter proves scope, executor enforces deletion safety, user approves one exact batch.**
