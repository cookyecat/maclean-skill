---
name: macos-disk-auditor
description: Privacy-first, evidence-backed macOS disk auditing and AI-guided, separately approved cleanup. Default scanner only measures known technical caches, never broad Home or private user data.
---

# macOS Disk Auditor & Safe Cleanup — v1.3.1

## Non-negotiable boundaries

**AI makes the judgment.** The assistant determines which technical files could be worth reclaiming, tradeoffs, rebuild costs, conditions and recommendations. The scripts DO NOT algorithmically recommend or approve deletion; they collect limited machine evidence, enforce hard safety/privacy constraints, and execute only separately approved exact plans.

**Privacy before access.** Having Full Disk Access is NOT consent to scan Mail, Messages, CloudDocs, MobileSync, com.apple.TCC, AddressBook, FaceTime, Knowledge, FileProvider, Keychains, browser profiles, other personal content, or whole Home/Library/Developer trees. Do not read, enumerate, or size these paths, even if permitted by macOS. Never perform an ad-hoc `du -sh ~`, `du -sk ~/Library`, `find ~`, or exhaustive filesystem scan as a workaround. No network upload or telemetry by the scripts.

**Mutation** is always separate. AI proposes an evidence-backed exact-path plan; user expressly approves each target; executor checks immutable safety/privacy restrictions, process activity, symlink and inode changes and demands *physical* TTY `DELETE` for `--apply`. This does NOT transfer the AI's selection judgment to fixed heuristics. The helper's safety veto is not a cleanup recommendation. NEVER run real `--apply` in an audit/acceptance run.

## Scan profiles and consent

- Default **Privacy Safe**: `--scope home` measures only precise recognized technical leaves under npm, uv, Puppeteer, Codex caches/releases; `--scope library` checks only specifically recognized technical runtime leaves such as `~/Library/Caches/ms-playwright` and individual Cursor Agent versions. Both scopes explicitly **do not** measure Home/Library total, enumerate Documents or recurse on parents. No fallback broad `du`.
- `--scope triage`: collects machine observations and fail-closed blockers about permitted technical leaves, with `ai_assessment=REQUIRED`, `user_approved=false`; results ARE NOT deletion advice.
- **Developer Scoped**, only when user names the project: `--scope developer --project-root <authorized-project>` examines only that selected project's `target/` Cargo build output. It does not read source contents, inspect unrelated projects or scan the project parent. Project scope must be inside developer/worktree locations.
- **User-Selected App Cache**, only with separate user authorization: `--scope path --root "$HOME/Library/Caches/<specific-app>" --user-selected-cache`. Without the flag, an unrecognized cache scope is denied. No personal-profile directories. AI decides whether such a cache is genuinely disposable.
- `--details` is a separate, explicitly approved **local-only** detailed report setting. Default reports must omit actual usernames, hostname, exact paths, PID details and raw process commands.

## G0–G7 real acceptance gates

| Gate | Mandatory proof |
|---|---|
| G0 release | Read current installed `SKILL.md`, execution contract and manifest. Version from authoritative first titles must match 1.3.1; historical mentions not current version. If resource and installed bytes conflict, show both exact SHA-256 rather than pretend PASS. |
| G1 connection | Authorized connector reaches actual Mac, ordinary user, process context. |
| G2 original deployment | Original installed source bytes staged in independently authorized temporary directory on Mac. No assistant rewrite substituted. |
| G3 integrity | Run original `scripts/verify_bundle.py --json` ON Mac, all manifest hashes and declared versions match. |
| G4 on-Mac tests | Run shipped `scripts/self_test.py` as non-root in disposable HOME, with timeout, durable stdout/stderr/exit code. Do not change normal TMPDIR. Only fixture deletion permitted. |
| G5 real audit | Run shipped `audit_session.py` for home, library, triage. Read actual report receipts and statuses. No broad recursive probes. |
| G6 AI review | AI assesses candidate tradeoffs using limited evidence; distinguish status blockers from AI suitability and never treat `REVIEW` as consent. Do not invent Home total or bytes freed. |
| G7 privacy boundary | Validate known protected paths denied, du targets limited to approved leaves, symlink attacks fail, default JSON redacted, log dir 0700/file 0600, exclusions not labeled errors. |

Overall end-to-end PASS requires evidence for all G0–G7. If a gate is untested, mark PARTIAL/NOT TESTED. No smoke test in cloud substitutes for Mac execution. Original bundled scripts are mandatory, not ad-hoc equivalents.

## Workflow on the Mac

Read `references/execution-contract.md`, `references/privacy-threat-model.md`, `references/transport.md`, `references/classification.md`, `references/home-targets.md` and all scripts relevant to the action before running.

1. Deploy original bundle to an **authorized, disposable** staging dir; first check `python3 scripts/verify_bundle.py --json`. No sudo, SIP/TCC changes or credential access.
2. For explicit acceptance, run original `self_test.py` under normal UID and record exit/output durably. It creates and deletes only its own test fixtures.
3. Run using a fresh, caller-owned **0700** report dir:

```bash
python3 scripts/audit_session.py --scope home --output-dir "$REPORT_DIR" --timeout 180
python3 scripts/audit_session.py --scope library --output-dir "$REPORT_DIR" --timeout 180
python3 scripts/audit_session.py --scope triage --output-dir "$REPORT_DIR" --timeout 180
```

4. Only if user expressly selected a developer project: `python3 scripts/audit_session.py --scope developer --project-root "$PROJECT" --output-dir "$REPORT_DIR"`.
5. Offer AI analysis using candidate classes/sizes/blockers. Ask permission before revealing local detailed paths or writing an actual deletion plan. If user approves a plan, `python3 scripts/cleanup_plan.py --plan plan.json` performs **preview / dry-run** and cannot delete. Only after fresh separate authorization may `--apply` be considered, with human physical TTY confirmation. Never autonomously pipe confirmation.

## Data semantics and reporting

- Default JSON is sanitized at source, not cleaned by ChatGPT after collection. It contains policy ID, IDs, cache kinds, sizes, machine safety blockers, and policy exclusions **by category**. No `excluded_actual_count` estimate (we intentionally never inspect excluded directories).
- `complete_within_policy=true` means the **allowed technical targets** were successfully measured, NOT that all Home/Library data was covered. `home_total_measured` MUST be false. Keep intentional policy skips distinct from actual I/O failures.
- Host filesystem `disk.total_gib` and `disk.free_gib` are volume-level and NOT Home occupancy. Candidate `du` allocation is NOT guaranteed APFS reclaim after delete. Avoid overlapping sums.
- If connector cannot access a permitted technical target, record `UNKNOWN_ERROR`/partial; **never** grant permissions or switch to scan private areas to force completeness.
- Treat unknown app caches or build directories as user/AI assessment tasks; no script-inferred delete eligibility. For AI-selected arbitrary app caches, schema v3 requires reason/conditions and exact path under an explicitly authorized cache leaf; production executor still enforces hard restrictions.

## File manifest & maintained safety behavior

`verify_bundle.py` hashes all shipped reference/scripts. v1.3.1 extends scan privacy and report security while keeping earlier fail-closed controls: cancellation, unapproved plans, TTY gate, active npm/Codex/Cursor checks, current/fallback versions, clean Git/Cargo target checks, PTY EOF and macOS `/var` alias regression.

For transport/permission failures use an independently authorized connector only, otherwise stop and report. Never fabricate verification evidence. No real cleanup is authorized by requesting a dry-run or acceptance test.
