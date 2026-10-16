# Frequently asked questions

**Does the Skill read all files to find large ones?**  No. Default Privacy Safe only measures a narrow allowlist of technical cache leaves, not entire Home/Library or personal data.

**If I grant Full Disk Access, does the scanner inspect my iCloud, contacts or chats?**  No. Permissions and informed scan consent are different. The Skill does not require Full Disk Access to force a `PASS`.

**Why does the report show `complete_within_policy=true` but no Home total?**  It means authorized technical leaves were measured; the entire Home was deliberately not traversed or totaled.

**Does a `REVIEW` item mean I should delete it?**  No. A machine blocker check and an AI value judgment are independent. Ask the AI to assess rebuildability and your current work before deciding.

**Will running the audit delete anything?**  Audits are read-only for inspected targets but may write private reports to an explicitly approved temporary directory. The separate `self_test.py` creates and removes disposable synthetic fixtures. A plan preview does not delete.

**Can I remove caches using just ChatGPT?**  Real deletion requires per-target user approval and an interactive confirmation from the local terminal; do not pipe approval or bypass the safety checks.

**What if an app process is running?**  The executor conservatively blocks relevant operations. It will not automatically kill the process. A generic process match does not necessarily identify the exact version currently in use.

**Why didn't the promised free disk space appear after cleanup?**  `du` measurements and APFS available-block deltas can differ because of clones, hardlinks, snapshots, and concurrent disk activity. No recovery guarantee is made.

**Can I share the JSON?**  Default audit JSON is minimized, but inspect it first. Console receipts, detailed reports and cleanup previews can include paths. Never share unredacted debug logs or credentials.

**Which macOS versions are supported?**  The full published baseline covers a Mac mini on macOS 26.5.2 with Python 3.14.7. Other versions are not yet independently verified.
