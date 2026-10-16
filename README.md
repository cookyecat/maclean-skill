# MacLean — Privacy-First macOS Disk Auditing (AI-Guided)

**Public source release · v1.3.0 · MIT License**

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

1. Obtain the release ZIP from a publisher/source you trust; verify its published SHA-256 (see `artifacts/SHA256SUMS.txt`). Do not infer source authenticity from an internal manifest alone.
2. Upload `macos-disk-auditor-v1.3.0.zip` as a Skill in your compatible ChatGPT environment, or unpack it into an applicable Skills directory. Start a new session and verify the loaded Skill title is **v1.3.0**.
3. Authorize a Mac connector **separately**. Installing a Skill does not authorize filesystem access or execute a Mac script.
4. Ask for a read-only Privacy Safe audit first, including manifest verification, and **prohibit any real cleanup**.
5. Review the anonymous candidate summary; ask the AI for reasons and conditions before requesting any precise-path preview.

For the manual extraction workflow and safe commands, read [INSTALLATION.md](docs/INSTALLATION.md). For a copyable acceptance prompt, see [VALIDATION.md](docs/VALIDATION.md).

## Verified baseline (one environment, not a certification)

The original unchanged v1.3.0 package passed G0–G7 on an authorized Mac mini with macOS **26.5.2** and Python **3.14.7** on **2026-10-16**: 17/17 hashed files, 53/53 on-device isolation checks, 20/20 Home-policy targets and 4/4 Library-policy targets measured, three original audit scopes executed, and no real user deletion. See the privacy-sanitized [acceptance summary](docs/ACCEPTANCE-SUMMARY.md). Other macOS releases, Python versions, Macs and connectors **have not yet received equivalent published evidence**.

## Trust and AI responsibility

**AI** assesses: Is it actually disposable? Is it valuable to delete? What is the rebuild cost? Are offline requirements important? What must the user verify?

**Local scripts** measure limited data, validate a plan, block forbidden/active/unsafe targets and enforce explicit authorization. They **must not** algorithmically make the value judgment or infer approval from a dry-run. The safety veto may refuse an AI-approved suggestion.

More: [AI ↔ executor contract](docs/AI-EXECUTOR-CONTRACT.md), [privacy policy](PRIVACY.md), [security policy](SECURITY.md), [compatibility](docs/COMPATIBILITY.md), and [FAQ](docs/FAQ.md).

## Release status and licensing

**Public source code under the [MIT License](LICENSE), copyright (c) 2026 cookyecat.** The Skill source and installation ZIP here are **byte-for-byte identical to the G0–G7-tested v1.3.0 baseline**. This is a published source repository, not a claim of universal compatibility or a promise of safe deletion on every Mac.

**Known bundled documentation issue:** a few older installation and transport instructions *inside* the frozen Skill refer to v1.2.3, and one historical remote-scan note could be read as suggesting broad directory traversal. The [current installation guide](docs/INSTALLATION.md), [Privacy Policy](PRIVACY.md) and [Known Bundle Issues](docs/KNOWN-BUNDLE-ISSUES.md) clarify v1.3.0's Privacy Safe behavior. Do **not** run broad Home/Library recursion from historical examples. A versioned patch with renewed acceptance will update those embedded references.

The checked-in ZIP is the verified v1.3.0 package; a separately tagged GitHub Release may follow.

Read [中文说明](README.zh-CN.md) · [Contributing](CONTRIBUTING.md) · [Report security vulnerabilities](SECURITY.md)
