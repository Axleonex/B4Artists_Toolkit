# BoneCraft

**Current repository build: BoneCraft 9.2.15.**
[Install BoneCraft-BFA-9.2.15.zip](../releases/BoneCraft-BFA-9.2.15.zip).
Repairs MMD/PMX installation and material combining. Adds active-group Select All /
Deselect All for materials and textures and folds detailed controls away from the
main Analyze, choose sources, Bake Checked Sources workflow.
[Fixes and verification](docs/material-combiner-fixes-2026-10-23.md).
No standalone GitHub Release is created by this repository update.


A rigging and avatar toolkit for **[Bforartists](https://www.bforartists.de/)** (the Blender fork). BoneCraft runs
only in Bforartists: in standard Blender it does not load and shows a single "Get Bforartists" notice instead.

| | |
|---|---|
| **Add-on** | BoneCraft |
| **Version** | 9.2.5 |
| **Host** | Bforartists (tested on 5.2) — not standard Blender |
| **Category** | Rigging / Animation |
| **License** | GPL v2.0 or later |

> This tool was built with heavy AI assistance and is under active bug-fixing. If you hit an issue, a screenshot
> or a note about what you were doing helps a lot.

## What it does

BoneCraft is organized into tool packages you can switch on and off (Preferences → Add-ons → BoneCraft → Tools):

- **Rig Builder** — Quick Rig, the Auto-Rig Wizard (joint detection from the mesh, a control rig with IK/FK,
  face rig, correctives, skirt and clothing bones), Mannequin, and a nine-starter thumbnail catalog. Basic Humanoid
  needs no Rigify; the other starters offer Enable Rigify & Add Rig when needed.
- **Mechanisms** — rigs for props and machines: hinges, slides, telescopes, pistons, gear links, follow and
  sequences, built with guided steps.
- **Rig UI and animation** — bone-collection panel, bookmarks, pose library, graph tools, corrective shape keys,
  animation layers, the Control Picker and the animator control layer.
- **Weights and deform** — weight mirror, transfer and table, deform-bone control, delta mush, proximity wrap.
- **Advanced rigging** — rig validator, space switching, spline IK, ribbons, chain dynamics, set driven keys.
- **Retargeting and export** — retargeting with source maps and per-bone tweaks; validated export profiles for
  Unreal, Unity, VRChat, Godot and generic FBX / glTF.
- **VRChat, VRM and MMD** — the CATS tools (Fix Model, visemes, eye tracking, atlas), clothing merge, hair
  PhysBones, performance ranking, the VRM and MMD bridges.

Switching a package off unregisters its classes, so it costs nothing until you switch it back on.

## Install

1. In Bforartists: **Edit → Preferences → Add-ons → Install from Disk…**, and pick the BoneCraft `.zip` ([current repository ZIP: BoneCraft 9.2.5](../releases/BoneCraft-BFA-9.2.5.zip)).
2. Tick its checkbox.
3. In the 3D Viewport, the **BoneCraft** and **Rig Builder** tabs are on the left Tool Shelf (press **T**) and the
   **CATS** tab is on the right sidebar (press **N**). Each tab's side can be changed in the add-on's preferences
   (**Tabs**). Rig Builder, Mechanisms, CATS, Avatar Tools, VRChat Tools and Import / Export are also in the Properties
   editor's Scene tab while **Tabs → Scene Properties → Show** is on (the default).

Current repository changes and checks: [BoneCraft 9.2.5 notes](../docs/bonecraft/releases/9.2.5/RELEASE-NOTES.md).

Repository build 9.2.5: [installable ZIP](../releases/BoneCraft-BFA-9.2.5.zip). The latest tagged GitHub Release remains 9.2.3.

### 9.2.5 local changes

- Starter Rigs uses one native catalog tab; its top-left header controls are removed.
- Enable Starter Rigs once from the bottom shelf catalog menu to display its tab.

### Previous changes (9.2.4)

- The rebuilt ZIP fixes Grab/Move and native tool cycling with BoneCraft enabled in Object and Pose modes.
- Open Health Check runs the registered validator and shows refreshable results.
- Quick Wins and Remaining Tasks show each task once.
- Armatures and rig-bound meshes are accepted; unavailable validator packages are explained.

### Previous changes (9.2.3)

- Removes the duplicate Export to VRChat panel and export overview row from Avatar Tools.
- Retains VRChat export under CATS → Import / Export → Unity / VRChat.

### Previous changes (9.2.2)

- Bone Merge is under BoneCraft → Setup Rigging.
- Delta Mush and Proximity Wrap are under BoneCraft → Skin.
- Viseme Library is under CATS → Avatar Tools, between Hair Physics and Export.
- VRChat Viseme Mapping and Face Tracking are under CATS → VRChat Tools → Facial.
- Other Tools and its grouping hooks are removed.

Placement, drawing, visibility and tool-toggle host checks pass. Live-window appearance is not verified.
See the current release notes and package receipt for archive and host checks.

## Manual

New to rig controls? [IK/FK beginner walkthrough](docs/tutorials/ikfk-beginner.md) includes a narrated video and a practice file for Rigify Quick Rig and Auto-Rig Wizard controls. Captured with BoneCraft 9.1.3; see the guide for version details and the observed Rigify snapping limitation.

The current English manual and six translated editions: [docs/README.md](docs/README.md). The translations have 9.1.2 release notes, but their usage chapters are not yet synchronized with the current English interface guide.

Example file: [examples/crescent-rose](examples/crescent-rose/README.md) — Crescent Rose rigged with Mechanisms, built step by step in the manual's chapter 12.

## Browse the source

The readable source is in [`boneforge/`](boneforge/) (the add-on's package name is still `boneforge`, so saved
preferences carry over).

## License

Released under the **GNU General Public License v2.0 or later** — see [`LICENSE`](LICENSE).
