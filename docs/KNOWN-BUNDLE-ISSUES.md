# Known documentation drift inside the accepted, unchanged v1.3.0 ZIP

The ZIP is byte-identical to the version tested on a real Mac. Because its manifest validates all referenced Markdown, we **cannot silently fix these files inside the same release and preserve the claimed acceptance**.

1. `references/install.md`: title and four filename snippets still say `v1.2.3`, not `v1.3.0`.
2. `references/transport.md`: its ZIP filename and verification expectation still say `1.2.3`. This directly risks wrong-bundle installation or a false mismatch during G0–G3.
3. `references/remote-scan.md`: an older sentence advises `Path.iterdir()` on dot-directories even though v1.3.0 Privacy Safe disallows arbitrary Home directory enumeration.
4. `references/classification.md`: an older TCC/Full Disk Access workaround should be explicitly limited and subordinated to the new rule that permissions are not consent and no personal directories should be inspected.
5. `references/home-targets.md`: header says v1.1; update version context to remove ambiguity, while preserving historical migrations in a clearly labeled history section.

**Public-release repair path:** create a documentation-only patch release with a new patch version (or rerun acceptance on the exact newly repacked bytes); update all declarations, regenerated manifest and public checksum, then obtain an on-Mac G0–G7 report for that precise artifact. No changes have been made to the v1.3.0 core in this community preparation kit.
