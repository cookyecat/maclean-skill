# Mandatory genuine Skill acceptance contract — v1.3.0

The executing agent MUST distinguish: (a) installed source loaded, (b) original files transported byte-identically, (c) original scripts executed on authorized Mac, (d) AI interpreted evidence, and (e) privacy boundary enforced.

G0: Record installed resource URI, SKILL.md main title and SHA if raw bytes available, manifest version and title. A resource-vs-local contradiction is PARTIAL, not a reason to claim the bundle wrong without comparing hashes.
G1: Authorized Mac connection. Do not equate connector health with Full Disk Access and NEVER try to acquire access to protected personal folders.
G2: Stage original source to user-approved isolated temp path. Shell implementations copied from ChatGPT are not original scripts.
G3: Run bundled verify_bundle.py --json on Mac, require ok=true and all manifest entries match.
G4: Run self_test.py on Mac normal user, bounded timeout and durable test log/exit; no real user data mutated.
G5: Invoke original audit_session.py home, library, triage, read report JSON. Privacy Safe only: no root du, no user personal folder traversal. `complete_within_policy` != complete filesystem.
G6: AI assesses machine facts, recommends only on evidence and user intent; statuses REVIEW/ACTIVE/PROTECTED are safeguards, never AI delete decisions.
G7: Verify privacy_policy enforcement, no broad recursive du, direct user-data path rejection, symlink rejection, sanitized default JSON, private 0700/0600 files, and user-selectable Developer Scoped. Confirm G7 test output from Mac fixtures; never probe real sensitive directories to test it.

No automatic deletion or stop-process action. Dry-run `cleanup_plan.py --plan plan.json` only previews. An AI-authored plan needs separate precise user authorization before real `--apply` plus interactive DELETE. The executor may veto but never self-approve.

Accept a policy-complete Privacy Safe scan as G5 PASS even though Home total is excluded by design. Count errors for inaccessible *authorized* targets as PARTIAL; do not count intentionally unscanned private content as errors. Protect full paths and process commands from chat output by default.
