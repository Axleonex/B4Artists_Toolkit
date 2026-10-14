# Add-on-only distribution cleanup

Prepared on October 13, 2026 (America/New_York).

## Repository changes

- Keep Anim Assist 12.6.0 and its exact published add-on ZIP.
- Restore the single Anim Assist download in the README and version ledger.
- Document installation in existing Bforartists and existing-header tool access.
- Remove the custom application's build patch, build scripts and packaging script.
- Retain clearly marked historical qualification evidence and Git history.

## Publication actions after merge confirmation

1. Remove only these task-created assets from release `v12.6.0`:
   - `Bforartists_5.2.0_AnimAssist_12.6.0_Windows_x64.zip` (asset 638722399).
   - `Bforartists_5.2.0_AnimAssist_12.6.0_Windows_x64.zip.sha256` (asset 638622366).
2. Replace the release body with `GITHUB-RELEASE-NOTES.md`.
3. Keep `b4_anim_assist_v12.6.0.zip` (asset 638622368), the version and tag.
4. Push and merge the reviewed cleanup branch, then verify the remaining download.
5. Remove the temporary `codex/anim-assist-release-transfer` branch used only
   to assemble the application upload.

This cleanup changes distribution and documentation, not add-on behavior.
Local application archives are not public repository downloads and are not
deleted by this cleanup. Standard Blender compatibility is not introduced.
