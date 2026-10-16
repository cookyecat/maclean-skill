# Community publishing checklist — mandatory blockers

**Status: PUBLIC SOURCE RELEASE; PATCH-REVALIDATION AND BROADER SUPPORT STILL PENDING**

## Public-source publication complete; next tagged-release and patch steps

- [x] **MIT License** chosen by the owner; root `LICENSE` credits copyright (c) 2026 cookyecat.
- [ ] **Repair frozen package's stale bundled instructions** in a new versioned patch, particularly `references/install.md` and `references/transport.md` (`v1.2.3` filenames/version), `references/remote-scan.md` (old advice implying broad hidden-folder traversal), and `references/classification.md` (old Full Disk Access workaround without privacy-first caveat). Do not silently modify the acceptance-verified 1.3.0 ZIP in place.
- [ ] Rebuild manifest and public asset with the patched version number; rerun verifier + on-Mac G0–G7; publish new hashes. A README on GitHub does **not** fix stale instructions inside an independently installed Skill.
- [ ] Confirm the **scope and privacy language**: accurate default JSON; note raw stdout receipts, exception diagnostics, `--details` and cleanup previews can contain paths. Do not claim provable zero access under every execution environment.
- [ ] Set up **private vulnerability reporting** and a real maintainer-controlled security contact/response route. No real email or contact is invented in this draft.
- [ ] Remove/redact machine-specific material from example files, ZIP comments, screenshots, issues, discussions, CI logs, full test traces and commit history.
- [ ] Verify ownership/rights for all source, examples, artwork, external dependencies and any bundled third-party content.
- [ ] Run `python3 scripts/verify_bundle.py --json` on source and extracted release ZIP; validate the external release asset SHA-256 after upload.
- [ ] Require a new on-Mac acceptance report for the actual release bytes; **do not reuse v1.3.0 PASS for a modified package**.
- [x] Owner explicitly approved publishing source to the already-public `cookyecat/maclean-skill` repository. A separately tagged release is optional.

## Compatibility enhancements before broad stable labeling

- [ ] macOS second device or different macOS release/permission context.
- [ ] Python 3.10–3.13 smoke checks, or narrow declared supported interpreter versions.
- [ ] Model/connector variation with privacy-scoped scanning and negative tests.
- [ ] Confirm actual user-facing Skill importer behavior with exact release ZIP in a clean new session.

## Acceptable now

- [x] Preserve unchanged accepted v1.3.0 ZIP and its manifest (17/17).
- [x] Create bilingual README and privacy/security/AI-executor/compatibility docs.
- [x] Provide redacted G0–G7 evidence summary rather than raw device logs.
- [x] Draft issues/PR templates and CI syntax/manifest verification.
- [x] Document hard boundaries and no-auto-apply expectations.

## Release sign-off record

- Release owner: **cookyecat**
- Public repository URL: **https://github.com/cookyecat/maclean-skill**
- Published source: **v1.3.0, original tested bundle unchanged**
- LICENSE: **MIT**
- Original ZIP SHA-256: **4dc20c4a33b57ee6a0bc76296042cd97834a5d21be6afd6d8450bda47bdf3a09**
- Future patch: **embedded-docs cleanup + manifest regen + renewed acceptance**
