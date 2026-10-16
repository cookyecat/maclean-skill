# Native Executor v1.1 — Real read-only Mac acceptance and fixture apply

Date: 2026-10-17. Host: authorized Mac MCP Gateway. Research only.

## Real HOME read-only source-bounded acceptance

Actual original v1.4.0 bundle was verified against **four pinned source digests** for its scripts and passed original 17-file SHA manifest validation. The native executor reused original `cleanup_plan.resolve_target`, original process classification data and original Privacy Safe scope. It did not modify the originals.

| Native item | Count | Gross allocated candidate size | v1.1 status |
|---|---:|---:|---|
| npm `_cacache` | 1 | **2,356.8 MiB** | Default selected for review, passes fresh real path/inode and no-apply preview |
| npx `_npx/<key>` | 10 | **663.2 MiB** | Optional, passes preview; hard blocked from real `--apply` |
| uv | 0 | n/a | Not present as an original catalog candidate on this Mac after earlier approved deletion; method tested in isolated fixture |

Final refreshed real Mac research plan at `/tmp/maclean-v11-final-verified.G4hH2q/unapproved-native-batch.json`, 0600 under private 0700 directory. The plan is **UNAPPROVED**, `user_approved=false`, SHA-256 of draft: `c809241bd9530ffe05542d959550a7aa99636a71c7654c36e8785dc87a06ba09`. This path and hash are an experiment receipt, NOT approval or an instruction to apply.

Real Mac v1.1 preview on `npm_cache-001`: **PASS**, 2,356.8 MiB gross allocation, no net reclaim estimate, no deletion. One npx key (the original triage ID `npx_install-003`) was separately previewed and returned `blocked_from_execution`.

## Native end-to-end behavior on disposable fixture

Real npm 12.2.0 `cache clean --force` executed against an owner-private synthetic `.npm/_cacache` only, after a **test-only mocked approval and terminal-confirmation function**. The synthetic cache was removed while adjacent synthetic `_npx` entry survived.

Real uv 0.12.5 `cache prune` similarly executed **only on an ephemeral private uv fixture**, while adjacent npm and npx fixture folders survived.

Initial npm integration test failed due to sharing one empty config file as userconfig and globalconfig; npm 12 rejected double loading. Code was corrected to use two separate empty files and regression passed.

## Regression and safety results

**24/24 Mac fixture tests passed**. They cover: original verifier spoofing refusal; generation of unapproved draft; path-free user list; read-only preview; npx preview-only; missing/wrong approval and selected IDs; true/false approval; missing physical TTY; changed inode, symlink or safety state; expired draft; material allocation change; unwanted operation types; evil inherited npm config sanitization; exact durable per-operation journal; exclusive no-replay execution lock; synthetic npm and uv actual native clean/prune.

No service stopped. No real user cache deleted. No user approved an actual native cleanup. **APFS net gain was not measured from any live cache**. Gross allocation shown is not a guaranteed or verified reclaim.

## Remaining risks / product priority

Even when an npm cache is reproducible, in-flight npm installs may fail if full native cache clean intersects an active dependency fetch. This is a distinct current-task risk, not proof of irrecoverable data. The prototype requires explicit human consent but **has not yet established zero in-flight disruptions**. npx exact in-use runtime is blocked outright pending better safeguards.

The new executor is a separate, pinned research script; it is not an installed MacLean v1.5 release, and the old v1.4.0 `cleanup_plan.py` was never patched.

Important goal: ordinary users see one DEFAULT/OPTIONAL review, not low-level CacheStorage, E3 or process guard switches.

## Cross-platform acceptance and genuine failure repaired

The first Linux GitHub run **FAILED**, even though macOS passed: Linux may immediately reuse the same inode when a directory is deleted and recreated. Device/inode alone was insufficient to detect the replacement. v1.1 was corrected to bind a stable macOS birthtime (or conservative Linux ctime ns), owner UID, device and inode. The exact negative regression now passes on both Mac and GitHub. This improvement is NOT a claim of race-free atomic native path access.

**Latest GitHub research CI success:** https://github.com/cookyecat/maclean-skill/actions/runs/38973266888 . **Latest static source integrity CI success:** https://github.com/cookyecat/maclean-skill/actions/runs/38973266892 . Latest local Mac **24/24 PASS**.
