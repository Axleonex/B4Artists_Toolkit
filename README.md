# B4Artists Anim Tools

Two animation add-ons for **Bforartists** (the Blender fork). Both are **Bforartists-exclusive** — they do not run on standard Blender.

| Tool | Version | What it does |
|---|---|---|
| **Anim Assist** | 12.0.4 | A production animation workflow suite (~400 operators across 11 feature phases): key editing, breakdowns, trajectory polish, retiming, proxies, IK/FK matching, mirroring, animation layers, and a hybrid PREVIEW/SHIPPED lipsync system. Inspired by Maya's AnimBot. |
| **Ghost Tool** | 3.3.5 | Ghost keyframe visualization and manipulation: generates draggable in-between markers in 3D space and recalculates f-curves live. Includes onion skinning, motion trails, easing presets, snapshots, Physics Feel archetypes, and Visual Diff Mode. |

> These tools were built with heavy AI assistance and are under active bug-fixing. If you hit an issue, a screenshot or a note about what you were doing helps a lot — please open an [issue](../../issues).

## Download & install

The ready-to-install add-ons live in [`releases/`](releases/):

- `b4_anim_assist_v12.0.4.zip`
- `b4_ghost_tool_v3.3.5.zip`

That folder holds only the current build of each tool. Earlier builds stay
available through git history and the release tags — see
[`releases/VERSIONS.md`](releases/VERSIONS.md) for the version index, checksums,
and how to read the real version out of a zip.

To install in Bforartists:

1. **Edit -> Preferences -> Add-ons -> Install from Disk...**
2. Pick the `.zip` for the tool you want.
3. Enable the add-on by ticking its checkbox.
4. Press **N** to open the sidebar. In the **3D Viewport**, Anim Assist adds the tabs **AnimAssist** (Lipsync, Help, Diagnostics), **Pose**, **Motion**, **Rig**, **Workspace** and **Layers**; Ghost Tool adds **Ghost Tool**. In the **Graph Editor** sidebar you get **Keys** (curve and key tools) and **Motion**; in the **Dope Sheet** sidebar, **Pose** (breakdowns) and **Keys**.
5. On the **Workspace** tab, run **First Run Setup** once — it builds the Quick Shelf and default hotkeys.

You don't need to unzip anything by hand — Bforartists installs directly from the `.zip`.

## Browse the source

The unpacked, readable source for each tool is in this repository so you can read it on GitHub without downloading anything:

- [`anim_assist/`](anim_assist/) — Anim Assist source (`core/`, `operators/`, `ui/`, `tests/`)
- [`ghost_tool/`](ghost_tool/) — Ghost Tool source

The source folders and the `releases/` zips contain the same code; the zips are just packaged for one-click install.

## Documentation

Human-readable manuals are in [`docs/`](docs/):

- [`docs/anim_assist/`](docs/anim_assist/) — Anim Assist user manual (PDF)
- [`docs/ghost_tool/`](docs/ghost_tool/) — Ghost Tool user manual (PDF)

## Requirements

- **Bforartists 4.2+** (Anim Assist) / **Bforartists 4.x** (Ghost Tool). Not compatible with standard Blender.
- Registration, first-run setup and teardown of both add-ons are verified headless on **Bforartists 5.1.2** (Blender 5.2 base) via [`tests/smoke_bforartists.py`](tests/smoke_bforartists.py).

## License

Released under the **GNU General Public License v2.0 or later** — see [`LICENSE`](LICENSE).
