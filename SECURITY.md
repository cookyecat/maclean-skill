# Security Policy

## Supported baseline

`v1.3.0` is a **tested baseline**, not a promise of universal compatibility or a security certification. See [COMPATIBILITY.md](docs/COMPATIBILITY.md). This repository is publicly available under MIT; known embedded-documentation issues and limited compatibility evidence are disclosed in the release checklist.

## Reporting a vulnerability privately

**Do not open a public GitHub issue containing an exploit, sensitive log, private directory path, token or identifying details.** Once the maintainer enables GitHub's *Private vulnerability reporting* feature, use **Security → Report a vulnerability** in that repository. Before that feature is enabled, contact the maintainer by an independently established private channel; no contact address is published in this draft. If no secure channel is available, withhold technical exploit details until one is arranged.

When privately reporting, include the version, macOS/Python versions, a **synthetic** reproduction, affected boundaries, and expected/observed behavior. Never upload real personal files or credentials.

## Security architecture

- Default deny outside recognized technical scan leaves. No Home/Library root recursion and no tool-driven permission escalation.
- Plans are not authorization; AI value assessments do not override privacy/path/process vetoes.
- Report files are owner-only where the audit runner creates them. Detailed local output must be handled separately.
- User confirmation is required before any real deletion. Acceptance runs must not invoke real `--apply`.
- Manifest SHA-256 detects accidental/replaced files **relative to the manifest**; it does not authenticate an unknown publisher. Compare the externally published release checksum from a trusted source.

## Limits and non-guarantees

The accepted run exercised synthetic fixtures and a real Mac under one environment. The private-path negative tests are finite and not a formal proof of complete nonaccess or absence of vulnerabilities. The Skill does not back up files, guarantee reversibility, ensure APFS block recovery, or guarantee that all caches are safe to delete. A compromised AI environment or privileged connector is outside the scripts' direct control.
