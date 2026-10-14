# B4Artists Toolkit

Two animation add-ons for **Bforartists** (the Blender fork), plus an optional rigging add-on, BoneCraft. All of them are **Bforartists-exclusive** — they do not run on standard Blender.

| Tool | Version | What it does |
|---|---|---|
| **Anim Assist** | 12.6.0 | Animation tools for key editing, breakdowns, retiming, matching, mirroring, baking, layers and lipsync. Seven Timeline families expose 89 searchable and pinnable actions. Configurable quick buttons, Search and Pin are available in the existing Timeline header. Inspired by Maya's AnimBot. |
| **Ghost Tool** | 4.2.10 | Ghost keyframe visualization and manipulation: generates draggable in-between markers in 3D space and recalculates f-curves live. Includes onion skinning, motion trails, easing presets, snapshots, Physics Feel archetypes, and Visual Diff Mode. Persistent Top Toolbar, right sidebar and left Tool Shelf locations share feature controls. Marker and Compare target names fold independently. Cached visibility controls preserve previews. Ghosts pause during native gestures and refresh after animation edits settle. Live marker and skin updates default off. |

### Optional add-on: BoneCraft (rigging)

BoneCraft is the **advanced version of [BoneForge](https://github.com/Axleonex/BoneForge_ALTERNATIVE_CATS_for_5.0_Blender)**, the free rigging and avatar add-on for standard Blender. It includes everything in BoneForge plus advanced rigging tools that are not available in the open Blender version (see the comparison in [`docs/bonecraft/`](docs/bonecraft/)). It is a separate, optional add-on for rigging characters before you animate them with the tools above. You don't need it to use Anim Assist or Ghost Tool, and they don't need it.

| Tool | Version | What it does |
|---|---|---|
| **BoneCraft** | 9.2.1 | Auto-rigging for humanoid characters (VRoid/VRM and similar): a Rig Builder wizard that finds the joints on the mesh, generates a skeleton and skin weights, then builds an animator control rig: IK/FK arms and legs with no-pop switching, a Control Picker, twist bones, joint corrective shapes, skirt/dress bones, and face controls (eye aim, blinks, jaw with lip follow). Also retargets walk/run clips and exports to VRChat, Unity and Unreal, with an optional T-pose export. Manual: [bonecraft/docs](bonecraft/docs/README.md). |

See [`docs/bonecraft/`](docs/bonecraft/) for a short guide.

If you hit an issue, please open an [issue](https://github.com/Axleonex/B4Artists_Toolkit/issues) with a screenshot and the steps that caused it.

## Download

Install add-on ZIPs directly in your existing Bforartists installation.

| Add-on | Direct download |
|---|---|
| Anim Assist 12.6.0 | [b4_anim_assist_v12.6.0.zip](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/v12.6.0/b4_anim_assist_v12.6.0.zip) |
| Ghost Tool 4.2.10 candidate | [b4_ghost_tool_v4.2.10.zip](releases/b4_ghost_tool_v4.2.10.zip?raw=1) |
| BoneCraft 9.2.1 (optional) | [BoneCraft-BFA-9.2.1.zip](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/bonecraft-v9.2.1/BoneCraft-BFA-9.2.1.zip) |

## Browse the source

The unpacked, readable source for each tool is in this repository so you can read it on GitHub without downloading anything:

- [`anim_assist/`](anim_assist/) — Anim Assist source (`core/`, `operators/`, `ui/`, `tests/`)
- [`ghost_tool/`](ghost_tool/) — Ghost Tool source
- [`bonecraft/boneforge/`](bonecraft/boneforge/) — BoneCraft 9.2.1 source

The ZIPs package their recorded release source for one-click installation. The unpublished Ghost Tool 4.2.10 ZIP matches the current source modules; see its [candidate status](docs/ghost_tool/releases/4.2.10/verification-status.json).

## Documentation

Human-readable manuals are in [`docs/`](docs/):

- [Anim Assist 12.6.0 add-on](docs/anim_assist/releases/12.6.0/RELEASE-NOTES.md) — installation, quick tools and validation; [tool access coverage](docs/anim_assist/releases/12.6.0/tool-access-coverage.md) records the actions and gestures. [Suite manuals](docs/anim_assist/) cover the other animation tools.
- [`docs/ghost_tool/`](docs/ghost_tool/) — Ghost Tool 4.2.10 candidate guide, PDF and toolbar notes
- [`bonecraft/docs/`](bonecraft/docs/) — BoneCraft 9.2.1 English manual and translation status

## Requirements

- Anim Assist, Ghost Tool and BoneCraft require Bforartists.

- Ghost Tool 4.2.10 candidate's 15 pure width-policy checks pass. Two native GUI starts timed out before the shelf test script ran, so native width evidence and screenshots are missing. See the [verification status](docs/ghost_tool/releases/4.2.10/verification-status.json) and [release notes](docs/ghost_tool/releases/4.2.10/RELEASE-NOTES.md).

- Historical Ghost Tool 4.2.9 passed **89 focused tests/checks in Bforartists 5.2.0** from its exact ZIP: 54 background tests and 35 native split-view checks. Named options, the master switch, full-row consistency, panning and cached-state preservation pass. See the [package receipt](docs/ghost_tool/releases/4.2.9/package-receipt.json).

- Historical Ghost Tool 4.2.8 passed **77 focused tests/checks in Bforartists 5.2.0** from the exact ZIP: 53 background tests and 24 native split-view checks. Object/Pose, UI scale, new splits, horizontal panning, hide/show and frame/cache preservation pass. See the [package receipt](docs/ghost_tool/releases/4.2.8/package-receipt.json). Production rigs, full keyboard navigation and alternate themes remain unverified.

- Historical Ghost Tool 4.2.7 passed **148 checks/cases in actual Bforartists 5.2.0** from the exact ZIP: 118 background checks and 30 GUI checks for fresh defaults and legacy-header migration. See the [package receipt](docs/ghost_tool/releases/4.2.7/package-receipt.json). Production-rig acceptance and a complete visual check of every display location remain pending.

- **Bforartists 4.2+** (Anim Assist) / **Bforartists 4.x** (Ghost Tool). None of these add-ons are compatible with standard Blender.
- Historical Ghost Tool 4.2.6 passed **178 checks/cases** on a **Blender 5.1.2 stand-in**, including four native toolbar layouts and five native auto-key cases. See the [4.2.6 package receipt](docs/ghost_tool/releases/4.2.6/package-receipt.json). Native Bforartists validation remains pending. The older results below belong to their named builds.
- Historical Ghost Tool 4.2.0 r4 and BoneCraft 9.1.2 checks passed on **Bforartists 5.2.0**, with Blender runtime 5.3.0 Alpha, build `0a1ca45552db`. See the [verification summary](docs/releases/2026-10-11/VERIFICATION.md) for scope and limits.
- Historical Ghost Tool 4.2.1 had 229 passing checks on a **Blender 5.1.2 stand-in**, including 13 authoring regressions. Ten supplemental cases fail the same way on 4.2.0 because of stand-in host limitations. See the [4.2.1 verification report](docs/ghost_tool/authoring-fix/verification.md). Bforartists viewport validation was pending for that release.

- Historical Ghost Tool 4.2.2 passed **230 background checks across nine suites** and **five native auto-key cases** on a Blender 5.1.2 stand-in. See the [4.2.2 verification report](docs/ghost_tool/authoring-pause/verification.md). These include actual native object/pose moves with live updates off and on, plus cancellation; Bforartists production-rig validation remained pending for that release.
- Historical Ghost Tool 4.2.3 passed **50 of 51 focused checks** on the Blender stand-in, including all six target-fold checks and all 20 authoring regressions. The remaining native Tool Shelf assertion fails identically on 4.2.2 because it requires Bforartists. See the [4.2.3 verification report](docs/ghost_tool/marker-targets/verification.md).
- Historical Ghost Tool 4.2.5 passed **96 of 96 focused checks** from the exact ZIP on the Blender stand-in, including location switching, Compare/marker folds, header, authoring and snapshot targets. Preference persistence and rendered header/right-sidebar layouts passed separate checks. Native Bforartists left Tool Shelf validation remained pending for that release. See the [location report](docs/ghost_tool/display-location/verification.md) and [Compare report](docs/ghost_tool/compare-targets/verification.md).

- Historical Ghost Tool 4.2.4 passed **54 focused checks** on the Blender stand-in, including header UI, gesture regressions, all six target-fold checks and all 20 authoring regressions. See the [4.2.4 verification report](docs/ghost_tool/releases/4.2.4/VERIFICATION.md). Native Bforartists UI validation remained pending for that release.
- BoneCraft 9.2.0 adds nine visible starter thumbnails, category filters, a shelf switch and dependency-aware Rigify activation. Native click/drop, cancellation and undo/redo pass on Bforartists 5.2.0; see the [starter catalog evidence](docs/bonecraft/starter-shelf-implementation/README.md).

## License

Released under the **GNU General Public License v2.0 or later** — see [`LICENSE`](LICENSE).
