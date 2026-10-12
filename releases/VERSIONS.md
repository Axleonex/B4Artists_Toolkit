# Release versions

Latest repository builds. GitHub release publication is a separate step.

| Tool | Version | Archive | Bytes | SHA256 prefix | Status |
|---|---|---|---:|---|---|
| Anim Assist | 12.1.3 | [b4_anim_assist_v12.1.3.zip](b4_anim_assist_v12.1.3.zip) | 556,067 | `b30547b2afac` | Actual Bforartists regression checks pass; unpublished |
| Ghost Tool | 4.2.0 r4 | [ghost_tool-afterimage-candidate-r4.zip](ghost_tool-afterimage-candidate-r4.zip) | 211,131 | `443abacb14e2` | Actual Bforartists checks pass; owner usability acceptance pending; unpublished candidate |
| BoneCraft | 9.1.2 | [BoneCraft-BFA-9.1.2.zip](BoneCraft-BFA-9.1.2.zip) | 1,019,015 | `9901bdb98da4` | Full host suite passes; no GitHub Release published |

Anim Assist uses the package root `B4_anim_assist`; Ghost Tool uses `ghost_tool`; BoneCraft uses `boneforge`.

## Checks and notes

- [All three builds: verification and full hashes](../docs/releases/2026-10-11/VERIFICATION.md).
- [Anim Assist 12.1.3 release notes](../docs/anim_assist/releases/12.1.3/RELEASE-NOTES.md).
- [Ghost Tool r4 release notes](../docs/ghost_tool/afterimage-release/RELEASE-NOTES.md) and [owner checklist](../docs/ghost_tool/afterimage-release/UAT.md).
- [BoneCraft 9.1.2 release notes](../docs/bonecraft/releases/9.1.2/RELEASE-NOTES.md).

Published builds remain Anim Assist 12.1.0 and Ghost Tool 4.0.0 on the [GitHub Releases page](https://github.com/Axleonex/B4Artists_Toolkit/releases). Old published ZIPs are retained; local experimental and superseded candidate ZIPs are not part of the publishing update.

## Identify a build

Read the add-on version in Preferences > Add-ons or in the ZIP's top-level `__init__.py` `bl_info` field. Candidate revisions share the 4.2.0 version, so use the filename and full checksum to distinguish r4 from earlier revisions. The oldest Ghost archives used build counters in filenames; filenames alone are not reliable evidence of their internal version.
