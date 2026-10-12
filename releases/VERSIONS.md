# Release versions

Current repository packages and their publication status.

| Tool | Version | Archive | Bytes | SHA256 prefix | Status |
|---|---|---|---:|---|---|
| Anim Assist | 12.5.0 | [b4_anim_assist_v12.5.0.zip](b4_anim_assist_v12.5.0.zip?raw=1) | 570,901 | `27fea6cfd596` | Repository candidate; Needs Review: native Redo and trail geometry findings; actual Bforartists and owner acceptance pending |
| Anim Assist (last published release) | 12.1.3 | [b4_anim_assist_v12.1.3.zip](b4_anim_assist_v12.1.3.zip) | 556,067 | `b30547b2afac` | Published release; actual Bforartists regression checks pass |
| Ghost Tool | 4.2.6 | [b4_ghost_tool_v4.2.6.zip](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.2.6/b4_ghost_tool_v4.2.6.zip) | 219,281 | `e195239e6ae8` | Published release; persistent toolbar and cached visibility; 178 checks/cases pass in Blender stand-in; native Bforartists validation pending |
| Ghost Tool (4.2.5) | 4.2.5 | [b4_ghost_tool_v4.2.5.zip](b4_ghost_tool_v4.2.5.zip?raw=1) | 216,002 | `5cfb8cee7805` | Repository test build; display location preference and Compare folds; 96/96 focused stand-in checks pass; native Bforartists left Tool Shelf validation pending |
| Ghost Tool (4.2.4) | 4.2.4 | [b4_ghost_tool_v4.2.4.zip](b4_ghost_tool_v4.2.4.zip?raw=1) | 214,194 | `1c32458cb0fa` | Merged repository build; 54 focused checks pass on Blender stand-in; GitHub Release publication and Bforartists UI validation pending |
| Ghost Tool (4.2.3) | 4.2.3 | [b4_ghost_tool_v4.2.3.zip](b4_ghost_tool_v4.2.3.zip?raw=1) | 214,475 | `352864a728ba` | Earlier repository test build; 50 of 51 focused checks pass on Blender stand-in; one unchanged native Tool Shelf host failure; Bforartists UI validation pending |
| Ghost Tool (4.2.2) | 4.2.2 | [b4_ghost_tool_v4.2.2.zip](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.2.2/b4_ghost_tool_v4.2.2.zip) | 214,338 | `d74c692e4c6e` | Prerelease; 230 background checks and five native auto-key cases pass on Blender stand-in; Bforartists rig validation pending |
| Ghost Tool (4.2.1) | 4.2.1 | [b4_ghost_tool_v4.2.1.zip](b4_ghost_tool_v4.2.1.zip?raw=1) | 212,103 | `dc5e374a8d7e` | Prerelease; 13 authoring checks pass on Blender stand-in; Bforartists viewport validation pending |
| Ghost Tool (4.2.0) | 4.2.0 | [b4_ghost_tool_v4.2.0.zip](b4_ghost_tool_v4.2.0.zip) | 211,099 | `16a354dc92d6` | Published prerelease; recorded Bforartists checks pass; owner usability acceptance pending |
| BoneCraft | 9.2.0 | [BoneCraft-BFA-9.2.0.zip](BoneCraft-BFA-9.2.0.zip) | 1,238,057 | `655ad55bfac3` | Starter catalog; targeted host and native viewport checks pass |

Anim Assist uses the package root `B4_anim_assist`; Ghost Tool uses `ghost_tool`; BoneCraft uses `boneforge`.

## Checks and notes

- [Anim Assist 12.5.0 release notes](../docs/anim_assist/releases/12.5.0/RELEASE-NOTES.md), [usage screenshots](../docs/anim_assist/releases/12.5.0/USAGE.md), [qualification](../docs/anim_assist/releases/12.5.0/qualification.md) and [package receipt](../docs/anim_assist/releases/12.5.0/package-receipt.json). Full SHA256: `27fea6cfd5962ba4d4bf93744bf0b705f28c05863d12f136accd06f04e8790ab`. The source metadata and exact ZIP identify 12.5.0; the owner checkpoint remains open. The retained 12.4.0 archive is the local verification baseline.
- [Ghost Tool 4.2.6 toolbar release notes](../docs/ghost_tool/releases/4.2.6/RELEASE-NOTES.md) and [package receipt](../docs/ghost_tool/releases/4.2.6/package-receipt.json).
- [All three builds: verification and full hashes](../docs/releases/2026-10-11/VERIFICATION.md).
- [Anim Assist 12.1.3 release notes](../docs/anim_assist/releases/12.1.3/RELEASE-NOTES.md).
- [Ghost Tool 4.2.2 authoring pause and verification](../docs/ghost_tool/authoring-pause/verification.md): defaults off, native gesture freeze and one refresh after editing settles.
- [Ghost Tool 4.2.2 release notes](../docs/ghost_tool/authoring-pause/RELEASE-NOTES.md).
- [Ghost Tool 4.2.3 marker target fold](../docs/ghost_tool/marker-targets/verification.md).
- [Ghost Tool 4.2.4 interface cleanup and verification](../docs/ghost_tool/releases/4.2.4/VERIFICATION.md).
- [Ghost Tool 4.2.5 Compare target folds](../docs/ghost_tool/compare-targets/verification.md).
- [Ghost Tool 4.2.5 display location](../docs/ghost_tool/display-location/verification.md).
- [Ghost Tool 4.2.1 repair and verification](../docs/ghost_tool/authoring-fix/verification.md): live refresh preserves unkeyed edits and waits during native transforms; 229 checks pass, with ten unchanged stand-in host failures.
- [Ghost Tool 4.2.0 r4 release notes](../docs/ghost_tool/afterimage-release/RELEASE-NOTES.md) and [owner checklist](../docs/ghost_tool/afterimage-release/UAT.md).
- [BoneCraft 9.2.0 release notes](../docs/bonecraft/releases/9.2.0/RELEASE-NOTES.md) and [package checksum and verification](../docs/bonecraft/releases/9.2.0/package-receipt.json).
- [BoneCraft 9.1.2 release notes](../docs/bonecraft/releases/9.1.2/RELEASE-NOTES.md).

Published builds: [Anim Assist 12.1.3](https://github.com/Axleonex/B4Artists_Toolkit/releases/tag/v12.1.3), [Ghost Tool 4.2.6 release](https://github.com/Axleonex/B4Artists_Toolkit/releases/tag/ghost-v4.2.6) and [BoneCraft 9.2.0](https://github.com/Axleonex/B4Artists_Toolkit/releases/tag/bonecraft-v9.2.0). The Ghost Tool release includes the tested ZIP and updated PDF guide. Earlier [4.2.2](https://github.com/Axleonex/B4Artists_Toolkit/releases/tag/ghost-v4.2.2), [4.2.1](https://github.com/Axleonex/B4Artists_Toolkit/releases/tag/ghost-v4.2.1) and [4.2.0](https://github.com/Axleonex/B4Artists_Toolkit/releases/tag/ghost-v4.2.0) downloads remain available for comparison.

## Identify a build

Read the add-on version in Preferences > Add-ons or in the ZIP's top-level `__init__.py` `bl_info` field. The current Ghost Tool repository archive is 4.2.6; its [package receipt](../docs/ghost_tool/releases/4.2.6/package-receipt.json) records the full checksum, source matching and 178 passing checks/cases. The 4.2.5 archive and reports are historical. The concurrently merged 4.2.4 interface cleanup is retained. The earlier 4.2.2 [package receipt](../docs/ghost_tool/authoring-pause/package-receipt.json) records that build's evidence. The published 4.2.0 prerelease used internal revision r4. Older experimental archives used build counters in filenames; check the internal version and checksum to identify a build.
