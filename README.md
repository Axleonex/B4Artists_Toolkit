# B4Artists Toolkit

Three animation add-ons for **Bforartists** (the Blender fork), plus an optional rigging add-on, BoneCraft BFA. All of them are **Bforartists-exclusive** — they do not run on standard Blender.

| Tool | Version | What it does |
|---|---|---|
| **Anim Assist** | 12.1.0 | A production animation workflow suite (~400 operators across 11 feature phases): key editing, breakdowns, trajectory polish, retiming, proxies, IK/FK matching, mirroring, animation layers, and a hybrid PREVIEW/SHIPPED lipsync system. Inspired by Maya's AnimBot. |
| **Ghost Tool** | 3.6.0 | Ghost keyframe visualization and manipulation: generates draggable in-between markers in 3D space and recalculates f-curves live. Includes onion skinning, motion trails, easing presets, snapshots, Physics Feel archetypes, and Visual Diff Mode. |
| **B4Artists Machine Learning** | 1.0.0 | **Experimental; Not Tested:** Local, procedural posing and motion for humanoid and quadruped rigs, in a guided five-step panel (Setup, Pose, Motion, Review, Polish): pose with draggable targets, generate the in-betweens between key poses, keep or discard the result, then add contacts, cleanup and secondary motion. Key poses show as markers in the Timeline and Dope Sheet. Everything runs on your machine — nothing is uploaded. |

### Optional add-on: BoneCraft BFA (rigging)

BoneCraft BFA is the **advanced version of [BoneForge](https://github.com/Axleonex/BoneForge_ALTERNATIVE_CATS_for_5.0_Blender)**, the free rigging and avatar add-on for standard Blender. It includes everything in BoneForge plus advanced rigging tools that are not available in the open Blender version (see the comparison in [`docs/bonecraft/`](docs/bonecraft/)). It is a separate, optional add-on for rigging characters before you animate them with the tools above. You don't need it to use Anim Assist, Ghost Tool or B4Artists ML, and they don't need it.

| Tool | Version | What it does |
|---|---|---|
| **BoneCraft BFA** | 8.9.9 | Auto-rigging for humanoid characters (VRoid/VRM and similar): a Rig Builder wizard that finds the joints on the mesh, generates a skeleton and skin weights, then builds an animator control rig: IK/FK arms and legs with no-pop switching, a Control Picker, twist bones, joint corrective shapes, skirt/dress bones, and face controls (eye aim, blinks, jaw with lip follow). Also retargets walk/run clips and exports to VRChat, Unity and Unreal, with an optional T-pose export. |

See [`docs/bonecraft/`](docs/bonecraft/) for a short guide.

> These tools were built with heavy AI assistance and are under active bug-fixing. If you hit an issue, a screenshot or a note about what you were doing helps a lot — please open an [issue](../../issues).

## Download

Click a link to download the add-on's `.zip`, then install it with the steps below. Don't unzip it — Bforartists installs directly from the `.zip`.

| Add-on | Direct download |
|---|---|
| Anim Assist 12.1.0 | [b4_anim_assist_v12.1.0.zip](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/v12.1.0/b4_anim_assist_v12.1.0.zip) |
| Ghost Tool 3.6.0 | [b4_ghost_tool_v3.6.0.zip](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v3.6.0/b4_ghost_tool_v3.6.0.zip) |
| B4Artists Machine Learning 1.0.0 | [b4artists_ml_v1.0.0.zip](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ml-v1.0.0/b4artists_ml_v1.0.0.zip) |
| BoneCraft BFA 8.9.9 (optional) | [BoneCraft-BFA-8.9.9.zip](releases/BoneCraft-BFA-8.9.9.zip) |

Release notes and checksums for each download are on the [Releases page](../../releases). The Anim Assist and Ghost Tool zips are also kept in [`releases/`](releases/) — see [`releases/VERSIONS.md`](releases/VERSIONS.md) for the version index, checksums, and how to read the real version out of a zip.

## Install

1. In Bforartists, open **Edit -> Preferences -> Add-ons -> Install from Disk...**
2. Pick the `.zip` you downloaded.
3. Enable the add-on by ticking its checkbox.
4. Find the add-on:
   - **Anim Assist** lives in three places, each organised for its editor, and each starts with an **Anim Assist** label:
     - **Graph Editor** sidebar (press **N**), **Anim Assist** tab, organised by what you do to curves: Select, Shape Curves, Retime, Clean Up, Pose & Rig, Quick Shelf.
     - **Dope Sheet** sidebar (press **N**), **Anim Assist** tab, organised by animation stage: Block, Inbetween, Time, Mirror & Match, Keys & Channels, Shelf & Macros.
     - **Properties editor**, **Scene** tab, **Anim Assist** section (near the bottom), organised by scope: This Pose, Whole Animation, Rig, Face, then Setup, Settings and Help.

     Each of those editors' headers also has an **Anim Assist** menu with the most-used tools. The menu can open the full panel, switch to the **Anim Assist workspace** (the Animation layout plus a Graph Editor, with every home open), or open the panel in a **separate window** you can move to a second monitor.
   - **Ghost Tool** home is the **3D Viewport header**: a ghost on/off toggle and a **Ghost Tool** dropdown after the **Pose** menu, grouped as Show Ghosts, Onion Skin, Edit Motion, Compare, Physics, Look and Settings. **Open in Separate Window** at the bottom keeps it open in its own window.
   - **B4Artists Machine Learning** adds the **B4Artists ML** tab. Select an armature and click **Check Rig** to start; the panel walks you through the remaining steps.
   - **BoneCraft BFA** (optional) adds the **Rig Builder** and **BoneCraft** tabs to the 3D Viewport sidebar (press **N**). Select your character's mesh and start the wizard on the **Rig Builder** tab.
5. Anim Assist only: in **Properties > Scene > Anim Assist > Setup**, run **First Run Setup** once. It builds the Quick Shelf. The same section can add the Anim Assist workspace, and **Settings** turns on the optional **Anim Assist pie** shortcut (Shift Alt D, off by default).

## Browse the source

The unpacked, readable source for each tool is in this repository so you can read it on GitHub without downloading anything:

- [`anim_assist/`](anim_assist/) — Anim Assist source (`core/`, `operators/`, `ui/`, `tests/`)
- [`ghost_tool/`](ghost_tool/) — Ghost Tool source
- [`b4artists_ml/`](b4artists_ml/) — B4Artists Machine Learning source

The source folders and the downloadable zips contain the same code; the zips are just packaged for one-click install.

## Documentation

Human-readable manuals are in [`docs/`](docs/):

- [`docs/anim_assist/`](docs/anim_assist/) — Anim Assist user manual (PDF)
- [`docs/ghost_tool/`](docs/ghost_tool/) — Ghost Tool user manual (PDF)
- [`docs/b4artists_ml/`](docs/b4artists_ml/) — B4Artists Machine Learning specifications, evidence and delivery records

## Requirements

- **Bforartists 4.2+** (Anim Assist) / **Bforartists 4.x** (Ghost Tool) / **Bforartists 5.1.2** (B4Artists Machine Learning, verified). None of these add-ons are compatible with standard Blender.
- Registration, first-run setup and teardown of Anim Assist and Ghost Tool are verified headless on **Bforartists 5.1.2** (Blender 5.2 base) via [`tests/smoke_bforartists.py`](tests/smoke_bforartists.py).

## License

Released under the **GNU General Public License v2.0 or later** — see [`LICENSE`](LICENSE).
