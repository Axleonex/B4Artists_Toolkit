# Release versions

Current repository packages and their publication status.

| Tool | Version | Archive | Bytes | SHA256 prefix | Status |
|---|---|---|---:|---|---|
| Anim Assist | 12.1.3 | [b4_anim_assist_v12.1.3.zip](b4_anim_assist_v12.1.3.zip) | 556,067 | `b30547b2afac` | Published release; actual Bforartists regression checks pass |
| Ghost Tool | 4.2.1 | [b4_ghost_tool_v4.2.1.zip](b4_ghost_tool_v4.2.1.zip?raw=1) | 212,103 | `dc5e374a8d7e` | Repository test build; 13 authoring checks pass on Blender stand-in; Bforartists viewport validation pending |
| Ghost Tool (previous) | 4.2.0 | [b4_ghost_tool_v4.2.0.zip](b4_ghost_tool_v4.2.0.zip) | 211,099 | `16a354dc92d6` | Published prerelease; recorded Bforartists checks pass; owner usability acceptance pending |
| BoneCraft | 9.1.2 | [BoneCraft-BFA-9.1.2.zip](BoneCraft-BFA-9.1.2.zip) | 1,019,015 | `9901bdb98da4` | Published release; full host suite passes |

Anim Assist uses the package root `B4_anim_assist`; Ghost Tool uses `ghost_tool`; BoneCraft uses `boneforge`.

## Checks and notes

- [All three builds: verification and full hashes](../docs/releases/2026-10-11/VERIFICATION.md).
- [Anim Assist 12.1.3 release notes](../docs/anim_assist/releases/12.1.3/RELEASE-NOTES.md).
- [Ghost Tool 4.2.1 repair and verification](../docs/ghost_tool/authoring-fix/verification.md): live refresh preserves unkeyed edits and waits during native transforms; 229 checks pass, with ten unchanged stand-in host failures.
- [Ghost Tool 4.2.0 r4 release notes](../docs/ghost_tool/afterimage-release/RELEASE-NOTES.md) and [owner checklist](../docs/ghost_tool/afterimage-release/UAT.md).
- [BoneCraft 9.1.2 release notes](../docs/bonecraft/releases/9.1.2/RELEASE-NOTES.md).

Published builds: [Anim Assist 12.1.3](https://github.com/Axleonex/B4Artists_Toolkit/releases/tag/v12.1.3), [Ghost Tool 4.2.0 prerelease](https://github.com/Axleonex/B4Artists_Toolkit/releases/tag/ghost-v4.2.0) and [BoneCraft 9.1.2](https://github.com/Axleonex/B4Artists_Toolkit/releases/tag/bonecraft-v9.1.2). Ghost Tool 4.2.1 is available from this repository; a GitHub release has not been published for it. Prior published downloads remain on GitHub Releases, and the repository retains the 4.2.0 ZIP for comparison.

## Identify a build

Read the add-on version in Preferences > Add-ons or in the ZIP's top-level `__init__.py` `bl_info` field. The current Ghost Tool repository archive is 4.2.1. Its [package receipt](../docs/ghost_tool/authoring-fix/package-receipt.json) records the full checksum and test results. The published 4.2.0 prerelease used internal revision r4. Older experimental archives used build counters in filenames; check the internal version and checksum to identify a build.
