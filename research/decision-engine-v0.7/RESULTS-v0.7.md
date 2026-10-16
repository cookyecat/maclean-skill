# v0.7 Results — Selected Client Coverage and Attested Snapshot Freshness

**Date:** 2026-10-17. **Host:** authorized Mac MCP Gateway / macOS arm64. **Mode:** private disposable metadata fixtures; no cleanup.

## 1. Synthetic exact client graph

A fresh owner-private disposable directory contained:
- an explicitly selected `client-ALPHA` with fixed `node_modules/playwright-core/package.json` and `browsers.json` file locations;
- a `.links` file pointing at that selected client;
- an additional `.links` file containing an unapproved Home-subtree string, to test scope boundaries.

Result: the selected client produced one browser revision from synthetic metadata. The extra link yielded **one unknown client reference**. **No lookup, stat, resolution, file read or native CLI call was made on the unselected target.** The entire real-host client universe remains **UNKNOWN**, not complete.

## 2. Pinned official publisher metadata E2

Reused previously installed `playwright-core@1.64.1` in a private temporary npm prefix from v0.5; copied only its two manifest files into a newly generated disposable client fixture. No new network installation, browser binary download, service stop or real-cache access.

| Observation | Measured |
|---|---:|
| Official Playwright client version | 1.64.1 |
| Browser descriptor entries | **7** |
| Selected fixture clients | **1** |
| Deliberately unselected `.links` entries | **1** |
| Real-host client coverage | **PARTIAL_REAL_HOST_UNPROVEN** |
| Real browser binary authenticity | NOT PROVEN |
| Real cache deletions | **0** |

This proves the *bounded parser can ingest actual publisher metadata*, **not** that its version list is the current operating system's complete installed-browser graph.

## 3. Experimental plan-bound evidence issuer

The research issuer generates a fresh snapshot by directly calling the fixture reader, binds it to:
- an exact synthetic plan's SHA-256 digest;
- a unique random request nonce;
- short TTL and HMAC-SHA256 integrity;
- live **re-read** of the fixture during verification.

Tests reject wrong plan/nonces, modified record, invalid tag, different issuer, replay, stale data and altered client manifest or `.links` sets. Even when this passes, the returned `deletion_authorized` remains **false** and `approved_cleanup_targets` remains empty.

**Limit:** The issuer is a test object in the same process/security principal. This is not a separate privileged service, cryptographically authenticated source or complete E3 witness. There is still a possible post-verification race, so an actual future executor would need to bind verification to its atomic commit/preflight boundary.

## 4. Negative and privacy regressions

**34/34 macOS local unit tests passed**, including: symlinked manifest/project/node_modules/registry, Home-root rejection, unapproved and missing client IDs, duplicate IDs and links, bad browser revision, oversized publisher manifest, newline in link, partial evidence, fake HMAC, snapshot replay, expired evidence, changed dependency state, and root permissions.

CI contains the portable tests without any npm installation; the optional native publisher test is skipped when the original Mac-only disposable package fixture is not present. **Do not sum or mislabel a skip as a native CLI pass.**

## 5. Findings and research recommendation

The right model is **partial knowledge with explicit coverage**, not a binary "has dependency" flag. A client selected and read accurately is not enough to safely infer another client's *non-use*.

Proposed future E3 capability should obtain a trusted, bounded dependency graph under exact authorization and treat out-of-scope clients as UNKNOWN. A safe user experience can still offer a simple single batch: the system silently excludes unknown candidates rather than asking users to assess technical folders.

No production adapter has been modified. There is no new real-user RECOMMEND, no independent model accuracy estimate and no clearance to run `--apply`.