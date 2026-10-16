# AI-reviewed technical cleanup scopes — v1.3.1

The plan executor is an intentionally restricted tool, not a generic filesystem cleaner. Each path needs explicit user approval **and** physical-terminal `DELETE`. Any other type/path is report-only.

| `kind` | Allowed exact path pattern | Why / cautions |
|---|---|---|
| `npm_cache` | `~/.npm/_cacache` | Re-downloadable npm tarballs. Prefer `npm cache clean --force` if package-manager semantics suit the user's workflow. May slow future installs. |
| `npx_install` | `~/.npm/_npx/<lowercase-hex-hash>` | Individual prior npx unpacked copies only; **never** all of `_npx`. Confirm specific npx process is not using the package. |
| `uv_cache` | `~/.cache/uv` | UV Python packages/build cache; often replaceable. Prefer `uv cache clean` for uv-specific maintenance. Does not delete project `.venv`. |
| `puppeteer_cache` | `~/.cache/puppeteer` | Puppeteer browser runtimes; re-download needed. Ensure browsers/automation scripts have exited. |
| `codex_runtime_installer` | `~/.cache/codex-runtimes/codex-runtime-install-<id>` | Temporary install copies only, at least 7 days old; **never** `codex-primary-runtime` or the whole `codex-runtimes` parent. |
| `codex_daemon_old` | `~/.codex/packages/app-server-daemon/releases/<semantic-version-arch>` | Only a single older build, excluding the `current` symlink destination and two newest builds; check active processes. |
| `cargo_target` | `~/Developer/<project>/target`, nested project under `~/Developer/`, or `~/.codex/worktrees/<id>/<project>/target` | Requires Git checkout root, `Cargo.toml`, git-ignored target, no tracked files in target, clean working tree, known Cargo build structure. Target artifacts may be expensive to rebuild and contain useful experiment binaries; review before approval. |

v1 `~/Library/...` classes still work: `cache`, `log`, `updater`, `downloaded_runtime` (only `~/Library/Caches/ms-playwright`), `preload`, and `old_version` (only individual dated Cursor Agent builds; two newest protected). v1 plans are accepted for Library only. New Home plans require `schema_version: 2`.

**Not supported:** arbitrary `~/Downloads` files, `.codex/worktrees` roots, `.codex/sessions`, `state.vscdb`, `.npm` root, `~/.cache` root, Rust source trees, Conda packages/environments, Homebrew `Cellar`, PostgreSQL data, `/System/Library/AssetsV2`. Manually review these separately; do not hack the plan file to fake a supported kind.

## Plan example (must be reviewed before changing approval)

```json
{
  "schema_version": 2,
  "user_approved": false,
  "targets": [
    {
      "path": "~/.npm/_cacache",
      "kind": "npm_cache",
      "reason": "Reviewed npm tarball cache; all download content is recoverable",
      "requires_quit": ["Npm"]
    },
    {
      "path": "~/.cache/uv",
      "kind": "uv_cache",
      "reason": "Reviewed uv Python package cache; will re-download wheels when required",
      "requires_quit": ["Uv"]
    }
  ]
}
```

`user_approved: false` means **preview only**. Change only after user has explicitly consented to *each exact path*. The runner also requires direct TTY confirmation during apply. A malformed/overbroad plan aborts.

## Inspect active packages without revealing credentials

For PID listings, redact `--api-key`, access tokens and environment files before showing user. Use the command path to identify whether a daemon or npx hash is live; mere PPID 1 is not proof of safe termination. Always preserve running Cursor Agent Workers, even when editor is closed.

## Community v1.3.1 AI-reviewed explicit cache targets
Schema v3 optionally supports `kind: agent_reviewed_cache` for an explicitly user-selected `~/Library/Caches/<specific-app>` leaf. AI must provide `ai_analysis` (why re-creatable, what risks) and `conditions` (app shutdown, dependencies, offline concerns). This never grants consent: `user_approved` and TTY `DELETE` remain separate. A hard privacy veto still applies to personal data irrespective of the AI review. No default scanning of arbitrary Library/Caches subtrees.
