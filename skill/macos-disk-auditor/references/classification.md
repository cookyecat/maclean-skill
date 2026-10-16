# Disk attribution and cleanup classification

## Green — normally regenerable (still check app activity)
- Application diagnostic logs and crash logs: `BambuStudio/log`, appropriately scoped `*.log` archives.
- Streaming caches: `.../Caches/online_play_cache`, image/thumb caches, app `Cache`, `CachedData`.
- Redundant auto-updater packages: old `.zip`/`.dmg`, *after* confirming current app version starts correctly.
- Stale download caches: only literal, reviewed paths. Never delete a whole `Caches` parent reflexively.

## Amber — replaceable but impacts offline capabilities
- Playwright browser downloads `~/Library/Caches/ms-playwright`: after deletion, subsequent automated tests may download Chromium/WebKit/Firefox again. Check active browser/test processes before cleanup.
- Service Worker `CacheStorage`: can store offline web content; remove only that specific cache storage after closing the app. Keep `IndexedDB`, `Local Storage`, cookies and user profile.
- Education app `preload`: re-downloads courses/resources; may disrupt offline lessons.
- Old Cursor Agent Worker runtimes (`.../cursor-agent/versions/<build>`): check `ps` for the actual active build, preserve all active and recent fallback builds; do not kill remote Worker by accident.
- Steam `appcache`: Steam should be closed; cache is generally regenerated.

## Red — do not touch without separate, app-aware backup/migration plan
- `~/Library/Application Support/Cursor/User/globalStorage/state.vscdb`, conversation databases and WAL; `Cursor/snapshots`, `Cursor/User/History`, repository code and agent state.
- WeChat/QQ message DB, chats, shared media, downloaded attachments; don't infer `Documents` means junk.
- `~/Library/Containers/*/Data` wholesale; browser `Default` profile, Extensions, History, Cookies, IndexedDB and Local Storage.
- iCloud, Keychains, Mail, Messages, Photos, Notes, game saves, printer settings, `.git`, any app's account config.

## macOS filesystem reality
- `du -sh` usually reports allocated blocks; `du -lsh` counts hard-linked content differently. Finder or Storage UI can report apparent/shared sizes or be affected by caching.
- APFS snapshots, shared blocks and open files can make physical free-space increase differ from `du` sum. Report `df -h ~` both before and after.
- TCC `Operation not permitted` is *not* necessarily fixed by `sudo`. In System Settings → Privacy & Security → Full Disk Access, the user can choose to authorize the actual terminal app (such as iTerm2). Restart the app after granting access.
- A process with PPID 1 may be orphaned but still meaningful. Inspect complete arguments (redact credentials), process type and project/worker ownership. `CursorUIViewService` is an Apple input-related service, not Cursor IDE.
- In scripts implemented as `python3 - <<'PY'`, `input()` reads exhausted source stdin. `/dev/tty` can be used; Python `open('/dev/tty','r+')` may cause ESPIPE (non-seekable). Use `os.open` + `os.read`/`os.write`, or run a standalone Python program whose stdin is free.

## Community v1.3.0 privacy
The AI decides suitability for cleanup from evidence and user intent. Script status REVIEW is a request for AI examination, not eligibility or authorization. No private content or root directory scans; respect hard privacy veto regardless of host access permissions.
