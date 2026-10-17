# B4Artists Toolkit

Two animation add-ons for **Bforartists** (the Blender fork), plus an optional rigging add-on, BoneCraft. All of them are **Bforartists-exclusive** — they do not run on standard Blender.

| Tool | Version | What it does |
|---|---|---|
| **Anim Assist** | 12.9.0 | Animation tools for key editing, breakdowns, retiming, matching, mirroring, baking, layers and lipsync. Seven Timeline families expose 89 searchable actions. Eight configurable numeric tools offer inline or popout sliders in a row at the bottom of the Timeline, with per-tool settings and user-named layouts. Stage tabs (Block, Spline, Polish, Deliver) filter the row by animation stage. Includes editor-specific NLA, Graph and Dope Sheet sidebars. Inspired by Maya's AnimBot. |
| **Ghost Tool** | 4.2.11 | Defers viewport initialization during startup. Ghost keyframe visualization and manipulation: generates draggable in-between markers in 3D space and recalculates f-curves live. Includes onion skinning, motion trails, easing presets, snapshots, Physics Feel archetypes, and Visual Diff Mode. Persistent Top Toolbar, right sidebar and left Tool Shelf locations share feature controls. Marker and Compare target names fold independently. Cached visibility controls preserve previews. Ghosts pause during native gestures and refresh after animation edits settle. Live marker and skin updates default off. |
| **BoneCraft** | 9.2.5 | Auto-rigging for humanoid characters (VRoid/VRM and similar): a Rig Builder wizard that finds the joints on the mesh, generates a skeleton and skin weights, then builds an animator control rig: IK/FK arms and legs with no-pop switching, a Control Picker, twist bones, joint corrective shapes, skirt/dress bones, and face controls (eye aim, blinks, jaw with lip follow). Also retargets walk/run clips and exports to VRChat, Unity and Unreal, with an optional T-pose export. Manual: [bonecraft/docs](bonecraft/docs/README.md). |

BoneCraft is the **advanced version of [BoneForge](https://github.com/Axleonex/BoneForge_ALTERNATIVE_CATS_for_5.0_Blender)**, the free rigging and avatar add-on for standard Blender. It includes everything in BoneForge plus advanced rigging tools that are not available in the open Blender version (see the comparison in [`docs/bonecraft/`](docs/bonecraft/)). It is a separate, optional add-on for rigging characters before you animate them with the tools above. You don't need it to use Anim Assist or Ghost Tool, and they don't need it.

See [`docs/bonecraft/`](docs/bonecraft/) for a short guide.

If you hit an issue, please open an [issue](https://github.com/Axleonex/B4Artists_Toolkit/issues) with a screenshot and the steps that caused it.

## Download

Install add-on ZIPs directly in your existing Bforartists installation.

| Add-on | Direct download |
|---|---|
| Anim Assist 12.9.0 | [b4_anim_assist_v12.9.0.zip](https://raw.githubusercontent.com/Axleonex/B4Artists_Toolkit/main/releases/b4_anim_assist_v12.9.0.zip) |
| Ghost Tool 4.2.11 | [b4_ghost_tool_v4.2.11.zip](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.2.11/b4_ghost_tool_v4.2.11.zip) |
| BoneCraft 9.2.5 | [BoneCraft-BFA-9.2.5.zip](https://github.com/Axleonex/B4Artists_Toolkit/raw/refs/heads/main/releases/BoneCraft-BFA-9.2.5.zip) |

## Browse the source

The unpacked, readable source for each tool is in this repository so you can read it on GitHub without downloading anything:

- [`anim_assist/`](anim_assist/) — Anim Assist source (`core/`, `operators/`, `ui/`, `tests/`)
- [`ghost_tool/`](ghost_tool/) — Ghost Tool source
- [`bonecraft/boneforge/`](bonecraft/boneforge/) — BoneCraft 9.2.5 source


## Documentation

Human-readable manuals are in [`docs/`](docs/):

- [Anim Assist 12.9.0](docs/anim_assist/releases/12.9.0/RELEASE-NOTES.md) — Timeline stage tabs filter the bottom row by animation stage without changing saved layouts. [Qualification](docs/anim_assist/releases/12.9.0/qualification.md).
- [Anim Assist 12.8.0](docs/anim_assist/releases/12.8.0/RELEASE-NOTES.md) — NLA clip arrangement and corrections, Graph/Dope Sheet refinements, preserved baking and selected-key scope fixes. [Qualification and screenshots](docs/anim_assist/releases/12.8.0/qualification.md) records the checks and limits. [Suite manuals](docs/anim_assist/) cover the other animation tools.
- [`docs/ghost_tool/`](docs/ghost_tool/) — Ghost Tool 4.2.11 guide, PDF and toolbar notes
- [`bonecraft/docs/`](bonecraft/docs/) — BoneCraft 9.2.5 source manual and translation status

## Requirements

- Anim Assist, Ghost Tool and BoneCraft require Bforartists.

## License

Released under the **GNU General Public License v2.0 or later** — see [`LICENSE`](LICENSE).
