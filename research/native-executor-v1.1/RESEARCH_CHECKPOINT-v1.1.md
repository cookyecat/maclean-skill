# MacLean native executor v1.1 — next session handoff

**Branch:** `research/native-executor-v1.1`
**Parent:** `research/decision-engine-native-adapters-v1.0`
**Product law:** **用户不用懂技术，AI 能判断得准，程序能删得安全。**

## History / why this branch exists
- v0.1–0.7: E3/identity research, synthetic evaluation; too much gatekeeping produced few recommendations.
- v0.8: pragmatic CleanMyMac-like three groups and one batch; real first default 70.3 MiB from 32 candidates because 21 were ACTIVE under app-family guard.
- v0.9: catalog-driven regenerability rather than generic process veto, 7 DEFAULT 3,148.1 MiB gross; 15 OPTIONAL 2,824.6 MiB; 10 BLOCKED. This was non-executable.
- v1.0: actual native npm 12.2.0, npx and uv 0.12.5 sandbox tests, 28/28 tests; native npx rm broke a running synthetic task's lazy file lookup. Npx needs precise in-use protection.
- **v1.1:** separate standalone exact-plan native executor, able to run approved native npm clean and uv prune under original verified source/path protections, with explicit signed-by-file plan SHA, live identity checks and console terminal confirmation, per-operation journal and exclusive lock. **npx remains preview-only.**

## Real Mac achieved
Verified original MacLean v1.4.0 script SHA-256 and original whole bundle manifest, ran fresh original read-only triage. Generated one owner-private 0600 **unapproved draft** containing 1 npm cache 2,356.8 MiB and 10 npx keys 663.2 MiB. Preview against real npm cache passed. User-facing `--review` hides all raw technical paths and offers DEFAULT/OPTIONAL metadata. Zero real deletion. Existing original 70.3 MiB plan untouched.

## Local tests
**24/24** synthetic and real native fixture tests on Mac: approval, original verification, plan expiration, inode/symlink, content changes, terminal confirmation, npx denial, npm clean synthetic execution, uv prune synthetic execution, exclusive once-only lock and fsynced journal. Original npm config collision bug discovered and fixed. GitHub workflow `research-native-executor-v11.yml` separately runs portable tests.

## Important distinction
The old v1.4 process guard is NOT overwritten; a *separate native operation executor* is built and tested. The research script has an `--apply` entrypoint requiring independent SHA-bound user approval and physical terminal confirmation. **It was NOT invoked against the real user's caches.** The same-user approval JSON is not an external cryptographic authority; terminal presence and visible one-batch scope remain necessary.

## Known unresolved production limitations
1. npm full clean in-flight concurrency safety not proven; explicit risk acceptance and/or narrower method needed.
2. npx active key could disrupt running tool; real apply remains blocked.
3. No atomic protection against malicious symlink/path races inside native tool; preflight identity revalidation reduces but does not eliminate TOCTOU.
4. No real end-to-end stable UI integration or accepted v1.5 release. Do not merge to `main` without explicit user request and proper G0-G7 review.
5. No actual APFS benefit measured on real home due no deletion.
6. The standalone research executor pins four SHA-256 values from original v1.4 scripts; any original version update requires deliberate review and new pin.

## Next milestone
Conduct concurrent real native npm operations **only in owner-private disposable cache** and measure disruption; implement dirfd/no-follow safety for preflight or explicitly document trust assumptions of self-owned HOME and native CLI; decide whether npm full clean should be default or optional in active npm situations. Integrate user-facing review with one approved batch and no technical parameter editing. Plan a separate explicitly authorized single-target live pilot, with before/after APFS measurement and no implicit prior approval.

**Do not interpret research PR approval or test mock approval as user consent for real deletion.**

### Final acceptance update

Latest Mac draft **not approved**: `/tmp/maclean-v11-final-verified.G4hH2q/unapproved-native-batch.json`, SHA-256 `c809241bd9530ffe05542d959550a7aa99636a71c7654c36e8785dc87a06ba09`; real npm preview PASS, 1 default / 2,356.8 MiB gross, 10 npx OPTIONAL / 663.2 MiB gross (preview-only). Zero real deletion. Linux GitHub initial identity test found instant inode reuse after delete/recreate; fixed by device + inode + birthtime/ctime + owner. Mac 24/24 and latest GitHub research workflow PASS.
