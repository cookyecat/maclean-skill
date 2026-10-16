# MacLean v0.9 — regenerability-first experiment

Principle: **用户不用懂技术，AI 能判断得准，程序能删得安全。**

Original verified v1.4.0 Privacy Safe triage on Mac found **32 candidates / 9,157.1 MiB**. The new research classifier ignores *only* coarse `RELATED_PROCESS_RUNNING` when recommending documented regenerable cache types; PROTECTED, UNKNOWN, offline/profile risk and other vetoes remain blocked.

| Group | Count | Candidate allocation |
|---|---:|---:|
| DEFAULT | 7 | 3,148.1 MiB |
| OPTIONAL | 15 | 2,824.6 MiB |
| BLOCKED | 10 | 3,184.4 MiB |

Previously v0.8 default: **70.3 MiB**. **19** candidates regained recommendation eligibility. This is gross cache allocation, **not confirmed reclaim or executor-ready cleanup**.

Largest proposed methods: npm.cache.clean_all 2,356.8 MiB; versioned runtime removal 1,499.5 MiB (OPTIONAL); npm.cache.npx.rm_exact 663.2 MiB; aged Codex installer 596.7 MiB; Puppeteer browser 549.6 MiB (OPTIONAL). Native npm 12.2.0 `npm cache npx ls` read-only listing corresponded to **all 11** triage npx leaves (10 nonempty). Neither npm cache clean, verify, nor npx removal was executed.

**29/29 unit tests passed on the Mac.** Every suggested operation remains `execution_ready=false`, `operation_adapter_verified=false`, `user_approved=false`. The original v1.4 executor has NOT changed and still vetoes running process families. This study did **not** produce a new executable deletion plan, did not delete caches, and did not measure APFS gain.

See `regenerability_policy.py`, `render_stdin.py` and `test_regenerability_v09.py`.

Next: test npm and npx native operations in disposable, isolated fixture caches (scope, concurrency and current-runtime protection); then propose a separately reviewed v1.5 executor adapter with one exact batch approval and terminal confirmation. Never bypass old guards by empty or fabricated process requirements.

Official semantics: https://github.com/npm/cli/blob/latest/docs/lib/content/commands/npm-cache.md and https://docs.astral.sh/uv/concepts/cache/.

## Read-only typed proposal contract

`native_method_proposal.py` transforms **already verified** detailed triage records into a private 0600 **research-only** document containing a per-candidate typed native operation and exact local path. It deliberately uses schema `maclean-native-method-proposal-v0.9-research-only` rather than the original v1.4.0 executable plan schema. Each item is `REQUIRES_SEPARATE_OPERATION_ADAPTER`; `user_approved=false`, `may_not_apply=true`. It cannot be submitted as an original executor plan. Six additional safety tests check private intent, protected exclusion and candidate identity changes, for **29/29** total macOS regression tests. No live command invoked by the proposal builder.
