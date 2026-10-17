# MacLean v1.4.0 — original source synchronization

**2026-10-17 · Source only · No new ZIP release**

The verified original `macos-disk-auditor v1.4.0` source was copied byte-for-byte from the authorized Mac's original bundle into the public GitHub source tree.

## What changed relative to v1.3.1 source

The 18-file directory `skill/macos-disk-auditor/` has its own `manifest.json` with **17 SHA-256-verified files**. Versioned skill instructions, README, audit and triage scripts, privacy policy, cleanup-plan executor, policy references and the bundled self-tests are updated. One example plan stayed byte-identical.

The v1.4.0 original **passed its built-in 67/67 temporary-HOME fixture self-tests** and `verify_bundle.py --json` on an authorized Mac. This is not an assertion that the entire G0–G7 acceptance was re-run or that any real user cache cleanup was approved. **No real cache deletion occurred during the source synchronization.**

The source retains its original privacy-first scanner, safety policy and explicit user approval model. Later experimental v0.9, v1.0 and v1.1 Decision Engine / native executor research is **not part of this source release**.

## Release artifact status

This repository still includes its original and independently hash-verifiable `macos-disk-auditor-v1.3.0.zip` and `macos-disk-auditor-v1.3.1.zip` in `artifacts/`. They remain **historic package releases**. The source-tree version is now v1.4.0 and is intentionally **not compared to the old v1.3.1 ZIP**. No v1.4.0 packaged ZIP, new checksum line or GitHub Release is created in this update.

Both versioned historical ZIPs are independently verified against their embedded manifests and pinned SHA-256 in `tools/check_release_integrity.py`. The v1.4.0 source is verified against its own manifest.

## Next for a distributable v1.4.0 ZIP

Build a reproducible ZIP using exactly this verified source, generate a newly published SHA-256 and run full release acceptance on the complete final package. Do not republish an old ZIP with a new filename. This requires a separate release decision.

See [README](../README.md), [中文说明](../README.zh-CN.md), [Installation](INSTALLATION.md), [Validation](VALIDATION.md).
