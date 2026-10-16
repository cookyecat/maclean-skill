# AI Decision / Executor Safety Contract

The design deliberately separates a **semantic decision** from a **technical safety constraint**.

| Actor | Responsibility | Must not do |
|---|---|---|
| AI assistant | Review measured size, rebuildability, dependency on active jobs, offline impact, opportunity cost, and user's objective; explain alternative options and propose conditions | Infer approval from `REVIEW`, prioritize purely by size, invent evidence, or auto-approve real deletion |
| Local audit scripts | Enumerate only specifically approved technical leaves, measure allocated size, return redacted machine evidence | Decide that a candidate *ought* to be deleted, scan private parents, or upload data |
| Local plan executor | Parse literal target, apply hard privacy/path/symlink/Git/process rules, preview and enforce user approval + TTY confirmation | Bypass a failed check because AI is confident; grant itself access; substitute heuristic cleanup preferences |
| Human user | Select scope, decide whether to share details, approve the disclosed exact target list as one batch, optionally complete physical TTY confirmation | N/A |

## Decision states

- `MEASURED`: a size observation, not a recommendation.
- `REVIEW`: no technical safety blocker was found under the defined checks, **not** an AI recommendation or consent.
- `ACTIVE`: conservative activity blocker; a matching process does not necessarily establish an exact open-file reference.
- `PROTECTED`: hard protective check blocked ordinary cleanup.
- `UNKNOWN`: evidence missing; do not infer that deletion is safe.

## Minimal AI rationale for any candidate

1. **Identity:** what type of technical artifact is this, and how certain are we?
2. **Benefit:** measured KiB/MiB, potential but **not guaranteed** APFS recovery.
3. **Loss/recovery:** rebuild/download time, bandwidth, offline capability, saved state at risk.
4. **Conditions:** exact path review, backups when relevant, which apps/services must stop safely (AI must not stop them automatically).
5. **Decision:** recommend, defer, keep, or ask for details. Record uncertainty.
6. **Consent:** user reviews the exact items and can authorize or decline the proposed batch as a whole.

## Plan and dry-run

The `cleanup_plan.py --plan FILE` command is a preview: it can refuse unsafe targets and display exact target paths **to the authorized user**, but it cannot delete. A schema-v3 AI-reviewed cache plan is supported for an *explicitly selected* narrow `~/Library/Caches/<app>` leaf, requiring an `ai_analysis` and `conditions` field; an AI assessment is still not authorization. The executor's fixed rules are intended solely to impose non-negotiable technical safety limits.

**No real `--apply`** is allowed during G0–G7 acceptance. This agreement intentionally does not provide an example of an auto-approved deletion plan.

**Candidate review UX:** AI prepares a single batch of reproducible low-risk candidates. No app-profile cache is automatically treated as reconstructable merely because its name contains CacheStorage. Users should see total estimated allocation, offline risks, active blockers, and the exact batch before approval. The executor never infers consent; human TTY confirmation remains required for actual mutation.
