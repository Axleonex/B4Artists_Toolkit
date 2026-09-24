# B4Artists Anim Tools

Three animation add-ons for **Bforartists** (the Blender fork). All three are **Bforartists-exclusive** — they do not run on standard Blender.

| Tool | Version | What it does |
|---|---|---|
| **Anim Assist** | 12.0.4 | A production animation workflow suite (~400 operators across 11 feature phases): key editing, breakdowns, trajectory polish, retiming, proxies, IK/FK matching, mirroring, animation layers, and a hybrid PREVIEW/SHIPPED lipsync system. Inspired by Maya's AnimBot. |
| **Ghost Tool** | 3.3.5 | Ghost keyframe visualization and manipulation: generates draggable in-between markers in 3D space and recalculates f-curves live. Includes onion skinning, motion trails, easing presets, snapshots, Physics Feel archetypes, and Visual Diff Mode. |
| **B4Artists Machine Learning** | 1.0.0 | Local, procedural posing and motion for humanoid and quadruped rigs, in a guided five-step panel (Setup, Pose, Motion, Review, Polish): pose with draggable targets, generate the in-betweens between key poses, keep or discard the result, then add contacts, cleanup and secondary motion. Key poses show as markers in the Timeline and Dope Sheet. Everything runs on your machine — nothing is uploaded. |

> These tools were built with heavy AI assistance and are under active bug-fixing. If you hit an issue, a screenshot or a note about what you were doing helps a lot — please open an [issue](../../issues).

## Download

Click a link to download the add-on's `.zip`, then install it with the steps below. Don't unzip it — Bforartists installs directly from the `.zip`.

| Add-on | Direct download |
|---|---|
| Anim Assist 12.0.4 | [b4_anim_assist_v12.0.4.zip](https://github.com/Axleonex/B4Artists_Anim_Tools/releases/download/v12.0.4/b4_anim_assist_v12.0.4.zip) |
| Ghost Tool 3.3.5 | [b4_ghost_tool_v3.3.5.zip](https://github.com/Axleonex/B4Artists_Anim_Tools/releases/download/ghost-v3.3.5/b4_ghost_tool_v3.3.5.zip) |
| B4Artists Machine Learning 1.0.0 | [b4artists_ml_v1.0.0.zip](https://github.com/Axleonex/B4Artists_Anim_Tools/releases/download/ml-v1.0.0/b4artists_ml_v1.0.0.zip) |

Release notes and checksums for each download are on the [Releases page](../../releases). The Anim Assist and Ghost Tool zips are also kept in [`releases/`](releases/) — see [`releases/VERSIONS.md`](releases/VERSIONS.md) for the version index, checksums, and how to read the real version out of a zip.

## Install

1. In Bforartists, open **Edit -> Preferences -> Add-ons -> Install from Disk...**
2. Pick the `.zip` you downloaded.
3. Enable the add-on by ticking its checkbox.
4. Press **N** in the **3D Viewport** to open the sidebar, then open the add-on's tab:
   - **Anim Assist** adds the tabs **AnimAssist** (Lipsync, Help, Diagnostics), **Pose**, **Motion**, **Rig**, **Workspace** and **Layers**. In the **Graph Editor** sidebar you get **Keys** (curve and key tools) and **Motion**; in the **Dope Sheet** sidebar, **Pose** (breakdowns) and **Keys**.
   - **Ghost Tool** adds the **Ghost Tool** tab.
   - **B4Artists Machine Learning** adds the **B4Artists ML** tab. Select an armature and click **Check Rig** to start; the panel walks you through the remaining steps.
5. Anim Assist only: on the **Workspace** tab, run **First Run Setup** once — it builds the Quick Shelf and default hotkeys.

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
