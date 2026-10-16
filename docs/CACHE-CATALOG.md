# Scoped cache discovery catalog — v1.4.0 development

The catalog is **machine observation evidence**, not a deletion list.
It does not search arbitrary HOME, Library or application profile parents.

| Category | Recognized location or family | Primary decision risk |
|---|---|---|
| BambuStudio | Diagnostic log leaf | Debugging history can be lost |
| NetEase Music | online_play_cache | Streaming / offline requirements |
| Baidu Netdisk, Youku, Tencent Video | Known updater or cache leaves | App must not be active; re-download |
| Cursor, VS Code | Recognized Cache, CachedData and logs | Editors may recreate or depend on cache |
| Xmind | Dated updater archive ZIP within known updater directory | Avoid cleanup during update |
| Xueersi | Preload directory | Offline lesson resources |
| Steam | appcache | Launcher restart/re-download |
| Chrome | Default/Service Worker/CacheStorage only | Offline web apps, possibly non-recoverable |
| Feishu | one fixed CacheStorage leaf beneath recognized profile ID | Offline collaborative resources, possibly non-recoverable |
| Previous v1.3 categories | npm, npx, uv, Puppeteer, Codex, Cursor Agent and Playwright | Install/build time, live agents |

**Browser history, Cookies, IndexedDB, Local Storage, app databases,
credentials and entire profiles are never catalog cleanup targets.**

This catalog is narrow by construction and is meant to grow with evidence.
Exact path specifications and process guards are implemented in
scripts/privacy_policy.py and scripts/cleanup_plan.py.
Default reports redact Feishu opaque profile IDs and exact user paths.
Do not assume all cache content is recoverable, or that measured allocation
equals APFS free-space gain.

## One-batch plan workflow

1. Scanner collects permitted leaf sizes, app identity and rebuild risk.
2. Safety triage labels blocked, uncertain and reviewable candidates.
3. AI reviews **all** findings against workload, loss and re-download cost.
4. AI proposes a compact batch of exact low-risk paths with reasons and
   explicitly defers uncertain profile/offline-dependent caches.
5. User reviews the batch summary and can approve it together.
6. Dry-run previews each target. Production --apply still requires all guards
   and a separate physical-terminal confirmation; no unattended delete.
