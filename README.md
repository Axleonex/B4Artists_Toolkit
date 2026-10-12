# B4Artists Toolkit

Two animation add-ons for **Bforartists** (the Blender fork), plus an optional rigging add-on, BoneCraft. All of them are **Bforartists-exclusive** — they do not run on standard Blender.

| Tool | Version | What it does |
|---|---|---|
| **Anim Assist** | 12.1.3 | A production animation workflow suite (~400 operators across 11 feature phases): key editing, breakdowns, trajectory polish, retiming, proxies, IK/FK matching, mirroring, animation layers, and a hybrid PREVIEW/SHIPPED lipsync system. Inspired by Maya's AnimBot. |
| **Ghost Tool** | 4.2.6 | Ghost keyframe visualization and manipulation: generates draggable in-between markers in 3D space and recalculates f-curves live. Includes onion skinning, motion trails, easing presets, snapshots, Physics Feel archetypes, and Visual Diff Mode. Persistent Top Toolbar, header, right sidebar and left Tool Shelf locations share feature controls. Marker and Compare target names fold independently. Cached visibility controls preserve previews. Ghosts pause during native gestures and refresh after animation edits settle. Live marker and skin updates default off. |

### Optional add-on: BoneCraft (rigging)

BoneCraft is the **advanced version of [BoneForge](https://github.com/Axleonex/BoneForge_ALTERNATIVE_CATS_for_5.0_Blender)**, the free rigging and avatar add-on for standard Blender. It includes everything in BoneForge plus advanced rigging tools that are not available in the open Blender version (see the comparison in [`docs/bonecraft/`](docs/bonecraft/)). It is a separate, optional add-on for rigging characters before you animate them with the tools above. You don't need it to use Anim Assist or Ghost Tool, and they don't need it.

| Tool | Version | What it does |
|---|---|---|
| **BoneCraft** | 9.2.0 | Auto-rigging for humanoid characters (VRoid/VRM and similar): a Rig Builder wizard that finds the joints on the mesh, generates a skeleton and skin weights, then builds an animator control rig: IK/FK arms and legs with no-pop switching, a Control Picker, twist bones, joint corrective shapes, skirt/dress bones, and face controls (eye aim, blinks, jaw with lip follow). Also retargets walk/run clips and exports to VRChat, Unity and Unreal, with an optional T-pose export. Manual: [bonecraft/docs](bonecraft/docs/README.md). |

See [`docs/bonecraft/`](docs/bonecraft/) for a short guide.

> These tools were built with heavy AI assistance and are under active bug-fixing. If you hit an issue, a screenshot or a note about what you were doing helps a lot — please open an [issue](https://github.com/Axleonex/B4Artists_Toolkit/issues).

## Download

Click a link to download the add-on's `.zip`, then install it with the steps below. Don't unzip it — Bforartists installs directly from the `.zip`.

| Add-on | Direct download |
|---|---|
| Anim Assist 12.1.3 | [b4_anim_assist_v12.1.3.zip](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/v12.1.3/b4_anim_assist_v12.1.3.zip) |
| Ghost Tool 4.2.6 (test build) | [b4_ghost_tool_v4.2.6.zip](releases/b4_ghost_tool_v4.2.6.zip?raw=1) |
| BoneCraft 9.2.0 (optional) | [BoneCraft-BFA-9.2.0.zip](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/bonecraft-v9.2.0/BoneCraft-BFA-9.2.0.zip) |

Anim Assist 12.1.3 passes its recorded host checks. BoneCraft 9.2.0 adds the complete starter catalog and passes its [recorded host and native viewport checks](docs/bonecraft/releases/9.2.0/RELEASE-NOTES.md). Ghost Tool 4.2.6 is a repository test build with the persistent toolbar, shared feature options and cached visibility controls. Marker Targets, Capture Targets and each saved reference's Snapshot Targets fold independently. Live updates default off and ghosts pause during native gestures. Bforartists rig and left Tool Shelf validation remain pending.

See [`releases/VERSIONS.md`](releases/VERSIONS.md) for status and checksums. The published [Ghost Tool 4.2.2 prerelease](https://github.com/Axleonex/B4Artists_Toolkit/releases/tag/ghost-v4.2.2) remains available on GitHub Releases.

The [Ghost toolbar guide](docs/ghost_tool/toolbar/README.md) covers the current 4.2.6 package. Earlier archives and their verification reports remain available as history.

## Install

1. In Bforartists, open **Edit -> Preferences -> Add-ons -> Install from Disk...**
2. Pick the `.zip` you downloaded.
3. Enable the add-on by ticking its checkbox.

   When updating Ghost Tool to 4.2.6, restart Bforartists after installation. Marker Targets, Capture Targets and Snapshot Targets open their full lists independently of the other tools. Saved scenes retain their existing live-update choices: turn off Live Update Markers and Live Update Skin to keep snapshots while scrubbing. Test a move with auto-key enabled; ghosts should refresh after you finish moving.
4. Find the add-on:
   - **Anim Assist** lives in three places, each organised for its editor, and each starts with an **Anim Assist** label:
     - **Graph Editor** sidebar (press **N**), **Anim Assist** tab, organised by what you do to curves: Select, Shape Curves, Retime, Clean Up, Pose & Rig, Quick Shelf.
     - **Dope Sheet** sidebar (press **N**), **Anim Assist** tab, organised by animation stage: Block, Inbetween, Time, Mirror & Match, Keys & Channels, Shelf & Macros.
     - **Properties editor**, **Scene** tab, **Anim Assist** section (near the bottom), organised by scope: This Pose, Whole Animation, Rig, Face, then Setup, Settings and Help.

     Each of those editors' headers also has an **Anim Assist** menu with the most-used tools. The menu can open the full panel, switch to the **Anim Assist workspace** (the Animation layout plus a Graph Editor, with every home open), or open the panel in a **separate window** you can move to a second monitor.
   - **Ghost Tool** defaults to the **3D Viewport header** dropdown. In **Edit > Preferences > Add-ons > Ghost Tool**, choose **Top Header**, **Top Toolbar**, **Right Sidebar (N)** or **Left Tool Shelf (T)**. Top Toolbar keeps actions in the native Tool Settings row. Its **Ghost** menu and the main-header **Ghost Tool** menu provide Hide/Show Toolbar. All locations share feature options. Save preferences normally to retain your choice.
   - **BoneCraft** (optional) adds the **BoneCraft** and **Rig Builder** tabs to the left Tool Shelf (press **T**) and the **CATS** tab to the right sidebar (press **N**); each tab's side can be changed in its preferences. Select your character's mesh and start the wizard on the **Rig Builder** tab.
5. Anim Assist only: in **Properties > Scene > Anim Assist > Setup**, run **First Run Setup** once. It builds the Quick Shelf. The same section can add the Anim Assist workspace, and **Settings** turns on the optional **Anim Assist pie** shortcut (Shift Alt D, off by default).

## Browse the source

The unpacked, readable source for each tool is in this repository so you can read it on GitHub without downloading anything:

- [`anim_assist/`](anim_assist/) — Anim Assist source (`core/`, `operators/`, `ui/`, `tests/`)
- [`ghost_tool/`](ghost_tool/) — Ghost Tool source
- [`bonecraft/boneforge/`](bonecraft/boneforge/) — BoneCraft 9.2.0 source

The ZIPs package their recorded release source for one-click installation. The current Ghost Tool 4.2.6 ZIP matches the source modules; see its [package receipt](docs/ghost_tool/releases/4.2.6/package-receipt.json).

## Documentation

Human-readable manuals are in [`docs/`](docs/):

- [`docs/anim_assist/`](docs/anim_assist/) — Anim Assist 12.1.3 guide (Markdown and PDF)
- [`docs/ghost_tool/`](docs/ghost_tool/) — Ghost Tool 4.2.6 guide, PDF and toolbar notes
- [`bonecraft/docs/`](bonecraft/docs/) — BoneCraft 9.2.0 English manual and translation status

## Requirements

- Anim Assist, Ghost Tool and BoneCraft require Bforartists.

- **Bforartists 4.2+** (Anim Assist) / **Bforartists 4.x** (Ghost Tool). None of these add-ons are compatible with standard Blender.
- Ghost Tool 4.2.6 passes **178 checks/cases** on a **Blender 5.1.2 stand-in**, including four native toolbar layouts and five native auto-key cases. See the [4.2.6 package receipt](docs/ghost_tool/releases/4.2.6/package-receipt.json). Native Bforartists validation remains pending. The older results below belong to their named builds.
- Anim Assist 12.1.3, Ghost Tool 4.2.0 r4 and BoneCraft 9.1.2 checks passed on **Bforartists 5.2.0**, with Blender runtime 5.3.0 Alpha, build `0a1ca45552db`. See the [verification summary](docs/releases/2026-10-11/VERIFICATION.md) for scope and limits.
- Ghost Tool 4.2.1 has 229 passing checks on a **Blender 5.1.2 stand-in**, including 13 authoring regressions. Ten supplemental cases fail the same way on 4.2.0 because of stand-in host limitations. See the [4.2.1 verification report](docs/ghost_tool/authoring-fix/verification.md). Bforartists viewport validation is pending.

- Ghost Tool 4.2.2 passes **230 background checks across nine suites** and **five native auto-key cases** on a Blender 5.1.2 stand-in. See the [4.2.2 verification report](docs/ghost_tool/authoring-pause/verification.md). These include actual native object/pose moves with live updates off and on, plus cancellation; Bforartists production-rig validation remains pending.
- Ghost Tool 4.2.3 passes **50 of 51 focused checks** on the Blender stand-in, including all six target-fold checks and all 20 authoring regressions. The remaining native Tool Shelf assertion fails identically on 4.2.2 because it requires Bforartists. See the [4.2.3 verification report](docs/ghost_tool/marker-targets/verification.md).
- Ghost Tool 4.2.5 passes **96 of 96 focused checks** from the exact ZIP on the Blender stand-in, including location switching, Compare/marker folds, header, authoring and snapshot targets. Preference persistence and rendered header/right-sidebar layouts pass separate checks. Native Bforartists left Tool Shelf validation remains pending. See the [location report](docs/ghost_tool/display-location/verification.md) and [Compare report](docs/ghost_tool/compare-targets/verification.md).

- Ghost Tool 4.2.4 passes **54 focused checks** on the Blender stand-in, including header UI, gesture regressions, all six target-fold checks and all 20 authoring regressions. See the [4.2.4 verification report](docs/ghost_tool/releases/4.2.4/VERIFICATION.md). Native Bforartists UI validation remains pending.
- BoneCraft 9.2.0 adds nine visible starter thumbnails, category filters, a shelf switch and dependency-aware Rigify activation. Native click/drop, cancellation and undo/redo pass on Bforartists 5.2.0; see the [starter catalog evidence](docs/bonecraft/starter-shelf-implementation/README.md).

## License

Released under the **GNU General Public License v2.0 or later** — see [`LICENSE`](LICENSE).
