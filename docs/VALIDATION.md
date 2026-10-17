# Reproducible validation and acceptance

## Two different verification layers

**Static integrity:** Verify shipped files match their manifest. This proves content consistency, **not** publisher authenticity or runtime behavior.

```bash
python3 skill/macos-disk-auditor/scripts/verify_bundle.py --json
```

**Real Mac acceptance:** Read the actually installed Skill (G0); connect to authorized Mac (G1); deploy identical original files (G2); run verifier (G3); isolate-test with temporary HOME (G4); run home/library/triage as bundled (G5); AI-review/dry-run only (G6); test privacy policy with synthetic fixtures and output permissions (G7).

No shell approximation of the scanner counts as shipped-Skill execution. Do not infer `G7 PASS` merely because a default JSON does not print personal filenames. Inspect actual command-scope evidence and negative tests against synthetic private folders.

## Safe example acceptance request

> Use the installed **macos-disk-auditor v1.4.0 source (or clearly identify a historical v1.3.x ZIP)** Privacy-First Skill and the separately authorized Mac connector. Read the actual installed `SKILL.md`, version and manifest. Do a genuine G0–G7 check: deploy identical bundle to a private temp directory; verify hashes on Mac; run bundled `self_test.py` only inside its fixture HOME; run original Privacy Safe home/library/triage reports without broad root traversal; independently have the AI assess technical candidates and perform dry-run only with `user_approved=false`; check privacy negative fixtures, symlink refusal and default output redaction. Never visit personal directories, stop an existing service, elevate permissions or run `--apply`. Report each Gate honestly and distinguish observed macOS evidence from untested systems.

## Historical packaged-release hash check (v1.3.1)

The following ZIP commands verify the **historical v1.3.1 artifact**, not v1.4.0 source. For v1.4.0 source run its bundled `verify_bundle.py --json` and verify repository provenance separately.

Mac:

```bash
shasum -a 256 artifacts/macos-disk-auditor-v1.3.1.zip
```

Linux:

```bash
sha256sum artifacts/macos-disk-auditor-v1.3.1.zip
```

Check the hash against `artifacts/SHA256SUMS.txt` obtained from a trusted publisher channel. `verify_bundle.py` uses the manifest to check internal file integrity only.

## Status vocabulary

`PASS` evidence-backed; `PARTIAL` some required scopes incomplete; `FAIL` an attempted gate failed; `SKIPPED/BLOCKED` not run due to prerequisite. `complete_within_policy=true` is not a claim that the whole filesystem was measured.
