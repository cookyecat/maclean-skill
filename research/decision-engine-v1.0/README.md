# MacLean v1.0 — Native cache-operation adapter laboratory

**Frozen product philosophy:** 用户不用懂技术，AI 能判断得准，程序能删得安全。

## Purpose

The v0.9 research classifier increased default *gross candidate allocation* from 70.3 MiB to 3,148.1 MiB by eliminating a broad app-process-family veto from **recommendation eligibility**. But recommendation was not execution ready. v1.0 tests actual **publisher-native npm/npx/uv cleanup semantics**, confined to private **disposable fixtures**. It makes **no change** to `main`, released v1.4 original `cleanup_plan.py`, or the user's unapproved plan.

## Executable isolated experiments

- `isolated_native_lab.py` creates its own 0700 `maclean-native-v10-*` temporary root, with exact synthetic marker and independent HOME, npm configuration, npm cache, logging directory, TMPDIR and uv cache.
- Only fixed native command argument shapes are accepted. It has **no user-supplied cache-root argument**, `--apply`, network fetch, service stop or real-target mode.
- It uses local synthetic tarball data to seed npm's content cache, two fake npx keys for exact key removal, native npm `cache verify` and `cache clean --force`, and native uv `cache prune` / `cache clean`. These operations DO delete **synthetic disposable test files**, not user data.
- `synthetic_runtime_race.py` proves that **npm npx rm can successfully delete a specific cache entry while a synthetic process remains alive; that process later fails to find a lazily loaded file**. Current in-use npx keys therefore require narrow operation-specific protection; detecting an unrelated npm process is not enough.
- `native_method_contract.py` accepts **only** `~/.npm/_cacache`, `~/.npm/_npx/<16 lowercase hex>`, `~/.cache/uv` combined with the correct v0.9 operation IDs. It returns **non-executable records**. Exact paths are identity contracts; it does NOT open, delete or prove safety of those real directories.
- `test_native_v10.py` and `test_method_contract_v10.py`: 28 tests passed on the authorized Mac.

## Observed native Mac results (npm 12.2.0, uv 0.12.5)

| Operation on the test fixture | Outcome |
|---|---|
| Native `npm cache npx ls` | 2 synthetic keys appeared |
| Native `npm cache npx rm <one-key>` | Only selected key removed; sibling survived |
| Native `npm cache verify` | Seeded valid content cache remained |
| Native `npm cache clean --force` | `_cacache` removed; test `_npx` entry remained |
| Native `uv cache prune` | Succeeded inside isolated cache |
| Native `uv cache clean` | Succeeded; on this version isolated `uv-cache` directory did **not** remain |
| Active synthetic npx entry removal | Native removal succeeded but later file lookup by live test process failed |

Native success is **not** proof of safe concurrency on real workloads, nor a guaranteed reclaim of all measured allocation. There is **no verified real-target native adapter yet**; all `production_operation_adapter_verified` / `user_approved` / `executable` flags remain false.

## Reproduce only in fresh disposable fixtures

```sh
python3 research/decision-engine-v1.0/isolated_native_lab.py --run-disposable-lab
python3 research/decision-engine-v1.0/synthetic_runtime_race.py
cd research/decision-engine-v1.0
python3 -m unittest -v test_native_v10 test_method_contract_v10
```

**Do not pass a real user cache or repurpose the script as a generic cleaner.** Parent symlinks, nested cache symlinks, world-readable roots and unsupported npm/uv arguments are explicitly rejected.

## Engineering implication

Use the *smallest app-specific safety rule*:

- npm content cache: prefer native content-cache operation; do not block for unrelated `npm` process merely existing. **Production concurrent clean has not been accepted**.
- npx: enumerate and bind exact key, remove only approved key, **avoid currently used entry**, not all npx caches because one npm process exists.
- uv: prefer native `cache prune` for routine maintenance, not direct file deletion. Its lock behavior is owned by uv; tested only in an empty disposable root so amount reclaimed remains unknown.
- Codex/Cursor installed daemons and browser runtimes: outside these adapters. Redownloadability alone does not justify deleting a binary backing a live task.

**Next:** build a versioned real-source adapter RFC with independent executor path / approval checks and exact per-operation concurrency, error/timeout and APFS accounting. No real cleanup without explicit separate user consent.

Publisher references:
- https://github.com/npm/cli/blob/latest/docs/lib/content/commands/npm-cache.md
- https://docs.astral.sh/uv/concepts/cache/
