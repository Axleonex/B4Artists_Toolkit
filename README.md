# B4Artists Toolkit

Two animation add-ons for **Bforartists** (the Blender fork), plus an optional rigging add-on, BoneCraft. All of them are **Bforartists-exclusive** — they do not run on standard Blender.

| Tool | Version | What it does |
|---|---|---|
| **Anim Assist** | 12.7.0 | Animation tools for key editing, breakdowns, retiming, matching, mirroring, baking, layers and lipsync. Seven Timeline families expose 89 searchable actions. Eight configurable numeric tools offer inline or popout sliders beside the native Timeline header, with per-tool settings and user-named layouts. Inspired by Maya's AnimBot. |
| **Ghost Tool** | 4.2.11 | Defers viewport initialization during startup. Ghost keyframe visualization and manipulation: generates draggable in-between markers in 3D space and recalculates f-curves live. Includes onion skinning, motion trails, easing presets, snapshots, Physics Feel archetypes, and Visual Diff Mode. Persistent Top Toolbar, right sidebar and left Tool Shelf locations share feature controls. Marker and Compare target names fold independently. Cached visibility controls preserve previews. Ghosts pause during native gestures and refresh after animation edits settle. Live marker and skin updates default off. |
| **BoneCraft** | 9.2.4 | Auto-rigging for humanoid characters (VRoid/VRM and similar): a Rig Builder wizard that finds the joints on the mesh, generates a skeleton and skin weights, then builds an animator control rig: IK/FK arms and legs with no-pop switching, a Control Picker, twist bones, joint corrective shapes, skirt/dress bones, and face controls (eye aim, blinks, jaw with lip follow). Also retargets walk/run clips and exports to VRChat, Unity and Unreal, with an optional T-pose export. Manual: [bonecraft/docs](bonecraft/docs/README.md). |

BoneCraft is the **advanced version of [BoneForge](https://github.com/Axleonex/BoneForge_ALTERNATIVE_CATS_for_5.0_Blender)**, the free rigging and avatar add-on for standard Blender. It includes everything in BoneForge plus advanced rigging tools that are not available in the open Blender version (see the comparison in [`docs/bonecraft/`](docs/bonecraft/)). It is a separate, optional add-on for rigging characters before you animate them with the tools above. You don't need it to use Anim Assist or Ghost Tool, and they don't need it.

See [`docs/bonecraft/`](docs/bonecraft/) for a short guide.

If you hit an issue, please open an [issue](https://github.com/Axleonex/B4Artists_Toolkit/issues) with a screenshot and the steps that caused it.

## Download

Install add-on ZIPs directly in your existing Bforartists installation.

BoneCraft 9.2.4 is the current repository build: [changes and checks](docs/bonecraft/releases/9.2.4/RELEASE-NOTES.md). Its latest tagged GitHub Release remains 9.2.3.

| Add-on | Direct download |
|---|---|
| Anim Assist 12.7.0 (repository build) | [b4_anim_assist_v12.7.0.zip](https://raw.githubusercontent.com/Axleonex/B4Artists_Toolkit/main/releases/b4_anim_assist_v12.7.0.zip) |
| Ghost Tool 4.2.11 | [b4_ghost_tool_v4.2.11.zip](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.2.11/b4_ghost_tool_v4.2.11.zip) |
| BoneCraft 9.2.4 (optional; repository build) | [BoneCraft-BFA-9.2.4.zip](https://github.com/Axleonex/B4Artists_Toolkit/raw/refs/heads/main/releases/BoneCraft-BFA-9.2.4.zip) |

**Anim Assist:** install the ZIP through Preferences and restart after updating.
Its tool row appears inside the Timeline above a bottom header; with a top
header, the frame ruler stays above the tool row. Breakdown and Smooth start
as inline sliders. Right-click numeric tools for their settings; Settings
chooses modes and saves named layouts. Search pins tools and More contains
overflow. **View > Show Anim
Assist Tool Row** restores a hidden row. No separate application is required.

## Browse the source

The unpacked, readable source for each tool is in this repository so you can read it on GitHub without downloading anything:

- [`anim_assist/`](anim_assist/) — Anim Assist source (`core/`, `operators/`, `ui/`, `tests/`)
- [`ghost_tool/`](ghost_tool/) — Ghost Tool source
- [`bonecraft/boneforge/`](bonecraft/boneforge/) — BoneCraft 9.2.4 source


## Documentation

Human-readable manuals are in [`docs/`](docs/):

- [Anim Assist 12.7.0 add-on](docs/anim_assist/releases/12.7.0/RELEASE-NOTES.md) — installation, sliders and named layouts; [qualification and screenshots](docs/anim_assist/releases/12.7.0/qualification.md) records the current checks. [Suite manuals](docs/anim_assist/) cover the other animation tools.
- [`docs/ghost_tool/`](docs/ghost_tool/) — Ghost Tool 4.2.11 guide, PDF and toolbar notes
- [`bonecraft/docs/`](bonecraft/docs/) — BoneCraft 9.2.4 source manual and translation status

## Requirements

- Anim Assist, Ghost Tool and BoneCraft require Bforartists.

## License

Released under the **GNU General Public License v2.0 or later** — see [`LICENSE`](LICENSE).
