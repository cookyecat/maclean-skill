# Research checkpoint — Decision Engine v0.8 (Pragmatic Cache Selection)

**Date:** 2026-10-17  
**Branch:** `research/decision-engine-pragmatic-v0.8`  
**Base:** `research/decision-engine-project-e3-v0.7`  
**Product philosophy (FROZEN):** **用户不用懂技术，AI 能判断得准，程序能删得安全。**

## Research shift, authorized by the user

The user specifically said **do not lose touch with practicality, do not demand excessive evidence for known junk, follow CleanMyMac's vetted-folder defaults or allow user selection**. Thus v0.8 creates a **pragmatic catalog/UX layer** instead of extending an E3 proof chain for every innocuous cache.

Read through:
- v0.1 independent three-state synthetic evaluation.
- v0.2 blinded real anonymized pilot; both models returned KEEP due sparse evidence.
- v0.3 publisher E1 and isolated uv native E2; synthetic E3 shows positive recommendations can emerge but method scope must be checked.
- v0.4 typed operations, exact scope and dependent-client TOCTOU.
- v0.5 real native browser CLI can produce false-positive listings and incomplete read-only signals.
- v0.6 source/client link reading could leave cache privacy scope; HMAC alone isn't E3.
- v0.7 exact selected synthetic client, partial coverage and plan-bound HMAC prototype.
- **v0.8:** pragmatic known-junk defaults / optional checkbox / automatic protect, real original v1.4 read-only triage and plan preview, reviewer-facing concise list.

## Invariants retained

1. Real original `triage_home.py` and exact `cleanup_plan.py` safety guards are upstream and downstream; policy may not override them.
2. `REVIEW` is not itself a recommendation. Only explicitly catalogued kinds + risk are eligible.
3. ACTIVE → DEFER, PROTECTED/UNKNOWN and privacy/offline-sensitive data → KEEP; neither may enter normal batch.
4. DEFAULT and OPTIONAL are two UI subgroups of AI RECOMMEND, with different checkbox defaults. Keep frozen three-state meanings and original two design diagrams intact.
5. User may exclude DEFAULT or explicitly include eligible OPTIONAL; candidate ID+path binding must match the **previously reviewed snapshot**.
6. Pending plan always `user_approved=false`. Real deletion still needs separate exact target approval and physical `DELETE` through original executor.
7. No broad parent/delete arbitrary paths, no profile deletion, no application-process bypass, no owner-private findings uploaded to public GitHub.
8. User sees ONE compact recommendation list, expandable precise details and implications. Technical identifiers are handled by the software, not typed by ordinary users.
9. Estimate `du` allocated size and true APFS free-space delta separately.
10. No real cache deletion executed in v0.8 research.

## Real Mac status on this session

Original 17/17 verified v1.4 read-only scan of 32 candidates:
- 1 DEFAULT (70.3 MiB, VS Code CachedData)
- 2 OPTIONAL (661.9 MiB, Puppeteer 549.6 + NetEase 112.3)
- 29 BLOCKED (8,424.9 MiB), of which many are ACTIVE.
- An exact original unapproved executor dry-run passed on default-only and default+Puppeteer. Unchecking the default produced no executable plan.
- 36/36 Mac offline program tests passed.
- Stable main / v1.3.1 release unchanged.

## Honest limitations

- The public GitHub catalog is smaller and less mature than CleanMyMac's proprietary database; this research must not pretend to inherit its warranties or comprehensive safety list.
- `editor_rebuild` CachedData is assumed regenerable based on exact leaf + known app semantics, and may cause brief restart/index cost; not a guarantee for arbitrary editor folders.
- Process guard is coarse by app family, not necessarily precise file usage; preserve its veto until precision tests validate any narrowing.
- CLI preview + text review is operational now, but a genuine graphical one-click batch UI does **not** exist in this branch.
- Optional selections with stale ordinal candidate IDs now require candidate identity SHA match; if changed, prompt rescan. This is behind-the-scenes, not extra burden for the user.
- No real deletion and no APFS gain claim.

## Next milestone v0.9 (pragmatic)

1. Light interactive selection UI or app-facing structured plan interface for defaults/optionals; show total and rebuild warnings. Require **one** explicit confirmation of final exact list.
2. Safely improve process-guard precision; do not use absence of open files as proof of global inactivity.
3. Expand vetted catalog incrementally (e.g. npm, app logs, update staging) with versioned rules, exceptions, and per-app ignore preferences, but keep strict privacy exclusions.
4. Measure actual recovery with **separately approved** cleanups, distinct from research; report APFS net delta.
5. Maintain frozen diagrams and the user product law; do not allow research shortcuts into production executor.

**Do not re-run 30 minutes of E3 proof for an ordinary known diagnostic log. Do not delete a possible offline application profile just because its folder is named Cache.**
