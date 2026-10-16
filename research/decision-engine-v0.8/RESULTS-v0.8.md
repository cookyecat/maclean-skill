# MacLean v0.8 — Pragmatic Decision Engine Research Results

**Date:** 2026-10-17, authorized macOS arm64 and verified original v1.4.0 package, read-only.

## Official comparative product research

CleanMyMac documentation updated 2026-10-12 describes automatic Smart Selection of general system/application junk, a detail view with per-item selections, category/batch clean and exclusions for categories such as Gradle cache and Xcode Archives/Module Cache. This is **the high-level UX pattern** MacLean deliberately adopts.

It is not evidence that any third-party directory is categorically safe; CleanMyMac maintains its own evolving safety rules. MacLean v0.8 has a smaller auditable explicit catalog and separate immutable original executor.

Publisher documentation: https://cms-static.macpaw.com/support/cleanmymac/knowledgebase/system-junk

## Real, fresh, read-only trial

The existing **original** v1.4.0 MacLean `triage_home.py --json --details` was run on Mac after successfully checking the original 17-file bundle manifest with `verify_bundle.py --json`. Detailed paths and process metadata were held only in private local memory; no raw findings were published to GitHub.

| Selection class | Count | Allocated space measured |
|---|---:|---:|
| **DEFAULT** recommended and prechecked | **1** | **70.3 MiB** |
| **OPTIONAL** recommended but unchecked | **2** | **661.9 MiB** |
| **BLOCKED** deferred or preserved | **29** | **8,424.9 MiB** |
| **Total** | **32** | **9,157.1 MiB** |

The selected default leaf was precisely catalogued VS Code `CachedData` (**70.3 MiB**), with no related activity detected at triage. The two opt-in options were Puppeteer browser download cache (**549.6 MiB**) and NetEase streaming playback cache (**112.3 MiB**). Profile/offline-risk targets and activity-blocked items were excluded automatically. The selected VS Code cache may rebuild on launch and briefly slow the editor; it is a recommendation, not a guarantee of zero impact.

**Why default 1 only?** 21 candidates were classified ACTIVE by original process-family guards, 5 PROTECTED and 6 REVIEW; of those six REVIEW, only one met pragmatic DEFAULT, two were OPTIONAL, three remained BLOCKED. v0.8 did **not** weaken the original ACTIVE safeguard to inflate reclaim amounts.

## Real original executor preview acceptance

Three independent non-destructive local trial scenarios passed:

| Scenario | Selected | Sum of measured allocation | Original executor |
|---|---:|---:|---|
| Default only | **1** | **70.3 MiB** | PREVIEW PASS |
| User additionally opts into Puppeteer | **2** | **619.9 MiB** | PREVIEW PASS |
| User unchecks the sole default | **0** | **0 MiB** | No executable plan generated |

Every plan had `user_approved=false` and was confined to a private temporary folder. `--apply` was **never invoked**. No user's caches, services or settings were changed. The optional scenario was **only** a proof that the original executor accepted a properly shaped unapproved preview; no recommendation to actually delete Puppeteer's browser revisions is made here.

The total optional measured space is not the space of the opt-in example (661.9 MiB = Puppeteer + NetEase; 619.9 MiB = Puppeteer + default VS Code). This distinction is deliberate and auditable.

## Safety and UX controls

- **36 local unit tests passed**, including canonical routine-log/cache classification, absent/unknown/protected/active machine hard vetoes, privacy profile exclusion, missing/zero size, no silent target substitution, optional selection and default deselection, preflight activity change, original executor preview refusal, owner-only output permissions and zero approval.
- After discovering an ordinal candidate ID could map to a different target following a new scan, v0.8 introduced a **full candidate-ID-to-(kind,path) fingerprint**. Any user choice from a previous snapshot requires exact fingerprint match, otherwise refused and freshly displayed.
- [render_review.py](render_review.py) creates a compact user-facing list with checked defaults and unchecked optional items; ordinary users never have to type Python or understand the underlying private paths in the eventual product. This CLI is still a research prototype, not that eventual app.

## Confirmed limits and product decisions

1. A small vetted cache rule set is enough to **recommend** deletion of known regenerable files. Do not force E3 as a prerequisite for every cache/log/updater.
2. **Safety hard veto remains universal** for active/protected/unknown targets, unexpected symlinks, identity mismatches, broad parents and approved plan scope. The verified original executor has final authority.
3. Some opt-in data might contain offline availability value, e.g. streaming cached playback; user choices must have visible warnings.
4. The original executor's process-family activity matching is conservative; many candidate GiB remain blocked. This is a **precision + user-experience issue**, not a reason to weaken vetoes silently.
5. No real APFS free-space change was measured because no deletion was performed. An APFS outcome can only come from a separate explicit approved trial.

**Conclusion:** The product can be useful now with selective rules and optional review, without sacrificing privacy or original deletion guards. The next step is to give that workflow a lightweight usable selection surface, tighten activity guard precision carefully, and expand catalog coverage only with source-backed semantic review.
