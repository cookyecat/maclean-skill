# MacLean Decision Engine v0.8 — Pragmatic Cleanup Policy & One-Batch Preview

> **用户不用懂技术，AI 能判断得准，程序能删得安全。**

**Status:** independent research branch; v1.4.0 original executor still owns actual deletion. No production release, cleanup, or modification of the frozen v1 diagrams.

## Why the policy changed

v0.2–v0.7 established that E3 proof is essential for *uncertain* browser/profile/client dependencies, but this should NOT block every known regenerable log, updater or package cache. A model that always returns KEEP is safe but not useful.

The October 2026 CleanMyMac documentation explicitly describes **Smart Selection** of known classes, per-item/per-category review and an **Ignore List**. Some cache/build categories are excluded by default. We adapt this **product pattern**, not its private Safety Database, proprietary rules or a claim that every cache is safe.

Sources:
- https://cms-static.macpaw.com/support/cleanmymac/knowledgebase/system-junk (2026-10-12)
- https://cms-static.macpaw.com/support/cleanmymac/knowledgebase/system-junk-cleanup-list
- https://macpaw.com/support/cleanmymac/knowledgebase/cleanmymac-safety

## A practical, documented policy

**Risk routing is performed only after original v1.4.0 Privacy Safe triage and its independent process/privacy guards.** The policy does not invent new scannable locations or allow broad Home/Library deletion.

| User-facing group | Rule | Selection | Examples |
|---|---|---|---|
| 默认推荐 | Known, documented catalog leaf with ordinary rebuild/diagnostics cost, `REVIEW` state | Checked in ONE draft batch, user may uncheck | `uv_cache`, `npm_cache`, diagnostic app logs, expired Codex installer, update packages, editor CachedData |
| 可选清理 | Specific catalog leaf, possible significant download/build/offline cost, `REVIEW` state | Unchecked; user can consciously check it | Puppeteer/Playwright downloaded browsers, npx execution packages, Rust build outputs, streaming cache, older fallback builds |
| 自动保留/暂缓 | ACTIVE, PROTECTED, UNKNOWN or risky personal/offline/unvetted content | Cannot be checked into a regular one-batch plan | Chrome/Feishu Profile CacheStorage, offline preloads and offline-media risk, unknown app caches, active IDE/npm/Codex |

Within the frozen **AI three-state chart**, both DEFAULT and OPTIONAL are **eligible RECOMMEND variants with different default checkbox states**; ACTIVE always maps to DEFER, and protected/unknown maps to KEEP. This does **not** reclassify KEEP/DEFER as selectable. OPTIONAL always carries explicit tradeoffs, and the user must consent to the exact resulting batch.

No universal "safe because name contains Cache", no arbitrary Profile/IndexedDB/database selection, no automatic cleanup, and no native browser GC operation without its proper adapter. For known routine garbage the *catalog contract* plus live machine hard veto is sufficient for recommending; full E3 is not an across-the-board prerequisite. Hard-delete safety remains enforced by the original executor.

## Files

- [pragmatic_policy.py](pragmatic_policy.py): strict (kind, risk) allowlist for DEFAULT / OPTIONAL / BLOCKED and original hard machine veto.
- [preview_batch.py](preview_batch.py): verify original v1.4.0 manifest, rerun ORIGINAL detailed read-only triage locally, generate a single **unapproved** exact-path batch, call ORIGINAL `cleanup_plan.py --plan` for its true read-only preview.
- [render_review.py](render_review.py): simple human-readable checked/unchecked list; no raw private paths/PIDs.
- [test_pragmatic_v08.py](test_pragmatic_v08.py): 36 policy / process / selection / drift / privacy regressions.
- [RESULTS-v0.8.md](RESULTS-v0.8.md), [RESEARCH_CHECKPOINT-v0.8.md](RESEARCH_CHECKPOINT-v0.8.md): real read-only pilot and handoff.

### Operator research-only reproducibility

With a **separately verified original v1.4.0 skill root** (do not point to a random repository clone without successful manifest verification), use an owner-private temporary report directory. This CLI is a proof-of-concept, **not** an installed graphical application:

```bash
umask 077
out=$(mktemp -d /tmp/maclean-v08-review.XXXXXX)
chmod 700 "$out"
python3 research/decision-engine-v0.8/preview_batch.py \
  --skill-root "/path/to/verified/macos-disk-auditor" \
  --private-output-dir "$out"
python3 research/decision-engine-v0.8/render_review.py \
  --private-review "$out/redacted-review.json"
```

Optional and default-checkbox changes require `--expected-catalog-sha256` from the previously displayed snapshot to bind a changing ordinal candidate ID to its exact kind/path. The operator/user interface must pass that digest automatically:

```text
--include-optional puppeteer_cache-002 --expected-catalog-sha256 <PREVIOUS_IDENTITY_DIGEST>
--exclude-default app_cache-029 --expected-catalog-sha256 <PREVIOUS_IDENTITY_DIGEST>
```

If candidates move or change identity, **refuse and re-display**, not silently swap. IDs above are **specific to one real read-only pilot, not stable names or a cleanup command**.

All review JSON and pending plans are local `0600` under `0700` directories. The plan has `user_approved=false`, and research code has **no --apply entrypoint**. The original executor, future explicit plan approval and real terminal `DELETE` remain independently required. No GUI one-click cleaner is claimed to exist yet.

## Exact boundaries

- Measured `du` allocation is **not** guaranteed APFS net free space.
- The catalog risk label is an explicit *bounded assumption*. Users may incur downloads, loss of past diagnostic logs, slower startup or lost streaming offline playback for opt-in data.
- App/command activity guards are intentionally conservative; **false-positive process-family matches may suppress many good candidates**. Improve guard precision using separate reviewed experiments rather than bypassing an ACTIVE veto.
- This research does not add a vendor-level safety database, scanning of arbitrary app directories, browser metadata signing, a live E3 sensor or a production cleanup method.
- User benefit and execution safety must be evaluated separately. Default recommendation = suggested for review, **never** authorization to delete.

## v0.9 milestone

Refine overly broad activity matching (without removing hard veto), expand the hand-reviewed catalog carefully by product class, and build a *small default-on selection interface* so a nontechnical user sees a single batch with expandable risks. Keep the original protected-directory and exact-target executor as the independent mutation authority.
