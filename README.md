# MacLean — Privacy-First macOS Disk Auditing (AI-Guided)

**Source tree · v1.4.0 · Latest prebuilt ZIP · v1.3.1 · MIT License**

macOS Disk Auditor is a reusable agent Skill for identifying *technical cache and build artifacts* that might be worth reclaiming. It measures a deliberately narrow set of paths and gives the assistant evidence for analysis. **The AI assesses reclaim value and risk; scripts do not decide what should be deleted.** A separate executor enforces technical safety checks and requires explicit, per-target human approval for any real deletion.

> **Privacy by default:** No broad recursive scan of Home, Library, Documents or personal application data. Filesystem access permission does not itself grant consent to inspect personal information.

## What it does

- Privacy Safe scan of recognized technical leaves (npm/npx, uv, Puppeteer, known Codex runtime installations, and limited technical items within Library).
- Optional developer-scoped Cargo `target` measurement **only when a specific project is selected**.
- Read-only candidate triage, risk/blocker information and human-readable AI review.
- Structured, limited-information JSON, local report directory `0700` and report file `0600`.
- Plan **preview / dry-run**. Real deletion is **out of scope for default auditing**, and requires a separate per-target authorization and an interactive local-terminal confirmation.

## What it does NOT do

- It does not measure the total space used by Home or Library, index all files, or scan Mail, Messages, Photos, iCloud documents, AddressBook, Keychains or browser profiles.
- It does not automatically delete files, stop active processes, grant Full Disk Access, elevate privileges or upload telemetry.
- A `REVIEW` classification is **not** an AI recommendation or permission to delete.
- Cache size measured by `du` is **not** a guarantee of free space recovered on APFS.

## Quick start

1. **v1.4.0 source:** review the exact files in [`skill/macos-disk-auditor/`](skill/macos-disk-auditor/), obtain the complete directory from a trusted repository checkout, then run its bundled `python3 scripts/verify_bundle.py --json`. Package it into a Skill only through an installation workflow you trust. The internal manifest checks integrity, not publisher authenticity.
2. **Historical prebuilt ZIP:** `artifacts/macos-disk-auditor-v1.3.1.zip` is still available and hash-verifiable via [`SHA256SUMS.txt`](artifacts/SHA256SUMS.txt), but it installs **v1.3.1, not v1.4.0**. No v1.4.0 ZIP has been published in this source-only update.
3. Authorize a Mac connector **separately**. Installing a Skill does not authorize filesystem access or execute a Mac script.
4. Ask for a read-only Privacy Safe audit first, including manifest verification, and **prohibit any real cleanup**.
5. Review the anonymous candidate summary; ask the AI for reasons and conditions before requesting any precise-path preview.

For the manual extraction workflow and safe commands, read [INSTALLATION.md](docs/INSTALLATION.md). For a copyable acceptance prompt, see [VALIDATION.md](docs/VALIDATION.md).

## Verified baseline (one environment, not a certification)

The unchanged v1.4.0 source bundle passed its 17-file internal manifest verification and **67/67** temporary-HOME self-tests on an authorized Mac on 2026-10-17. This is source and fixture verification, not new full G0–G7 publication acceptance or permission for real cleanup.

The original unchanged v1.3.0 package passed G0–G7 on an authorized Mac mini with macOS **26.5.2** and Python **3.14.7** on **2026-10-16**: 17/17 hashed files, 53/53 on-device isolation checks, 20/20 Home-policy targets and 4/4 Library-policy targets measured, three original audit scopes executed, and no real user deletion. See the privacy-sanitized [acceptance summary](docs/ACCEPTANCE-SUMMARY.md). Other macOS releases, Python versions, Macs and connectors **have not yet received equivalent published evidence**.

## Trust and AI responsibility

**AI** assesses: Is it actually disposable? Is it valuable to delete? What is the rebuild cost? Are offline requirements important? What must the user verify?

**Local scripts** measure limited data, validate a plan, block forbidden/active/unsafe targets and enforce explicit authorization. They **must not** algorithmically make the value judgment or infer approval from a dry-run. The safety veto may refuse an AI-approved suggestion.

More: [AI ↔ executor contract](docs/AI-EXECUTOR-CONTRACT.md), [privacy policy](PRIVACY.md), [security policy](SECURITY.md), [compatibility](docs/COMPATIBILITY.md), and [FAQ](docs/FAQ.md).

## Release status and licensing

**Public source code under the [MIT License](LICENSE), copyright (c) 2026 cookyecat.** The current Skill **source is v1.4.0**; the existing published ZIP archives remain **v1.3.0 and v1.3.1** and are checked separately. v1.3.0 was the separately tested G0–G7 baseline. See [v1.4.0 source sync notes](docs/RELEASE-NOTES-v1.4.0.md). This is a published source repository, not a claim of universal compatibility or a promise of safe deletion on every Mac.



Read [中文说明](README.zh-CN.md) · [Contributing](CONTRIBUTING.md) · [Report security vulnerabilities](SECURITY.md)

**Historical v1.3.1** fixes [Issue #1](https://github.com/cookyecat/maclean-skill/issues/1). If installing that ZIP, independently verify the installed version is v1.3.1; it is not the new v1.4.0 source.
