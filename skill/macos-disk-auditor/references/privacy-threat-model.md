# Privacy threat model — v1.3.1

## Assets at risk
Personal documents, contact data, messages, iCloud documents, call history, TCC privacy data, browser profiles, developer source names, API tokens in process arguments, host/user identity, raw audit reports.

## Trust boundaries
- macOS permission != user consent. A connector with Full Disk Access is still forbidden to audit personal data.
- AI is the semantic assessor, not an authorizer of mutations. AI may make mistakes; production code enforces hard privacy/symlink/concurrency invariants independently.
- Shell tools are only run on approved technical leaves. Recursing on parents (e.g. `du -sk ~/Library`) violates privacy even if reports hide the output.
- Detailed local reports require separate explicit user authorization. Default structured data is anonymized before returned to the assistant.

## Controls
1. Default deny outside exact known technical leaves. No broad HOME enumeration.
2. User-selected Developer scopes only inspect an exact Cargo `target/`, not source content. User-selected app cache scope must be an exact Library/Caches app leaf; never a privacy subtree.
3. AI can propose exact targets and prerequisites for schema v3, but hard privacy veto remains non-overridable by ordinary cleanup plans.
4. Reject symlink path components; do not follow symlinks in `du`; no report content for personal paths.
5. Default reports are owner-only (directory 0700; JSON 0600), omit host/user/absolute paths/PIDs.
6. Intentional privacy exclusions must not be mistaken for I/O failure. Do not enumerate excluded paths just to count them.

## Acceptance negatives
Attempt to scan an AddressBook/CloudDocs fixture directly => rejected before any `du`. `du` spy must not see private paths or Home/Library ancestor. A symlink from an approved cache leaf to personal data => rejected. An AI-reviewed cleanup request under a protected personal-data location => vetoed even with `user_approved=true`. Default JSON cannot contain fixture private filenames or hostname.

## Limits
The default allowed cache leaves can hold user-generated data; this tool only measures allocated blocks, not contents. Treat eligibility for deletion as separate AI assessment with explicit user consent. A finite set of tests cannot prove all macOS builds and connector environments perfectly secure.
