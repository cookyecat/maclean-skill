# MacLean public source release — macos-disk-auditor v1.3.0

> **MIT-licensed public source release.** The exact acceptance-tested v1.3.0 core is unchanged. A tagged GitHub Release, if desired, is a separate publication step.

## Highlights

- **Privacy-first default:** Measure approved technical cache/runtime leaves; no broad Home or Library recursion and no personally protected directory enumeration.
- **AI-led assessment:** The assistant, not a fixed algorithm, judges whether each measured artifact is worth reclaiming. Script-level vetoes remain mandatory.
- **Human-governed mutations:** Read-only triage and dry-run are separate from any future, independently authorized real deletion.
- **Private reports:** Minimal default JSON, local `0700` report directories and `0600` files.
- **Traceable execution:** Original bundle manifest/checksum verification plus G0–G7 real execution evidence.

## Verified on-device acceptance

On 2026-10-16, the original v1.3.0 ZIP passed G0–G7 on a Mac mini (macOS 26.5.2, Python 3.14.7): 17/17 manifest entries, 53/53 isolated self-tests, Home 20/20, Library 4/4 policy-scoped targets, and an unapproved, two-candidate dry-run; no real deletion. See [summary](ACCEPTANCE-SUMMARY.md).

## Breaking change versus v1.2.x

`--scope home` and `--scope library` no longer measure the entire Home or Library. `complete_within_policy=true` now refers only to permitted cache/artifact targets. Manual broad `du` is forbidden in the Skill workflow; personal directories cannot be probed to compensate for missing results. Detailed output requires separate user consent.

## Known limitations and blockers

- Bundled `references/install.md` and `references/transport.md` still show v1.2.3 commands, and one older `remote-scan.md` statement about hidden-directory traversal conflicts with the default privacy-first narrative. Resolve in a **new versioned source patch** with renewed acceptance before publishing.
- MIT license is provided by the repository owner. Private vulnerability reporting should be enabled by the maintainer; do not submit exploitable details to public issues.
- Full runtime verification only covers one published Mac setup. No completed cross-version compatibility matrix yet.
- Default technical cache leaves can contain generated user material; no unconditional guarantee of safe cleanup or of space recovered after deletion.

## Release assets

- `macos-disk-auditor-v1.3.0.zip` (original, byte-identical acceptance baseline)
- `SHA256SUMS.txt` (independently hash the published asset after upload)
- This public documentation set; **never publish internal raw acceptance logs**.
