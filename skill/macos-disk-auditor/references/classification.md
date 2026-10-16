# Privacy-first technical classification — v1.3.1

AI decides which candidate is worth reclaiming, based on the actual size, rebuild/re-download costs, workflow dependencies, data loss risk and user intent. Script classification REVIEW is evidence for AI inspection, not approval or a deletion decision.

## Conditional technical candidates
- npm/uv/Puppeteer package and browser download caches: usually reproducible, but require working network and may interrupt offline tasks.
- Old Codex/Cursor worker/runtime versions: protect current and fallback builds, any active process and critical session/databases.
- Cargo target in an explicitly user-selected Git checkout: requires clean worktree, ignored build target, correct repo identity and no active Cargo operations.
- Exact app-specific ~/Library/Caches/<app> leaves selected by the user: a directory named Cache alone is not sufficient to treat private app data as regenerable.

## Outside scope and hard privacy veto
Never enumerate, size, inspect or remove personal files, Mail, Messages, Photos, iCloud/CloudDocs, MobileSync, AddressBook, FaceTime, Knowledge, FileProvider, TCC, Keychains, browser profiles, private app container data, project source or user account databases. Full Disk Access is a technical permission, **not consent**; never suggest enabling it merely to enlarge MacLean coverage. No sudo or permission workarounds.

## Accounting and execution
du measures allocated blocks for an allowed exact leaf; APFS clones, snapshots, hardlinks and concurrent writes make freed disk space different from summed target sizes. Do not measure Home/Library roots or count nested targets twice. An orphaned process may remain essential. Only after AI analysis and explicit per-target user approval may an executor check narrow path allowlists, activity, TTY confirmation and other hard safety vetoes. Preview is never authorization to apply.
