# B4Artists Anim Tools

Three animation add-ons for **Bforartists** (the Blender fork). All three are **Bforartists-exclusive** — they do not run on standard Blender.

| Tool | Version | What it does |
|---|---|---|
| **Anim Assist** | 12.0.4 | A production animation workflow suite (~400 operators across 11 feature phases): key editing, breakdowns, trajectory polish, retiming, proxies, IK/FK matching, mirroring, animation layers, and a hybrid PREVIEW/SHIPPED lipsync system. Inspired by Maya's AnimBot. |
| **Ghost Tool** | 3.3.5 | Ghost keyframe visualization and manipulation: generates draggable in-between markers in 3D space and recalculates f-curves live. Includes onion skinning, motion trails, easing presets, snapshots, Physics Feel archetypes, and Visual Diff Mode. |
| **B4Artists Machine Learning** | 0.38.0 beta | Standalone, local procedural animation assistance for humanoid and quadruped rigs. The beta includes deterministic posing, interpolation, contact and bounded secondary-motion workflows; learned motion remains explicitly unqualified. The 0.38.0 beta reorganizes the panel into a five-stage workflow (Setup, Pose, Motion, Review, Advanced) with persistent feedback and Timeline/Dope Sheet integration. |

> These tools were built with heavy AI assistance and are under active bug-fixing. If you hit an issue, a screenshot or a note about what you were doing helps a lot — please open an [issue](../../issues).

## Download & install

The ready-to-install add-ons live in [`releases/`](releases/):

- `b4_anim_assist_v12.0.4.zip`
- `b4_ghost_tool_v3.3.5.zip`

That folder holds only the current build of each tool. Earlier builds stay
available through git history and the release tags — see
[`releases/VERSIONS.md`](releases/VERSIONS.md) for the version index, checksums,
and how to read the real version out of a zip.

B4Artists Machine Learning's beta archive is not committed here: build
`b4artists_ml_v0.38.0-beta.1.zip` locally with
`training/b4artists_ml/build_public_beta_package_v1.py` and attach it to a GitHub prerelease.

To install in Bforartists:

1. **Edit -> Preferences -> Add-ons -> Install from Disk...**
2. Pick the `.zip` for the tool you want.
3. Enable the add-on by ticking its checkbox.
4. Press **N** to open the sidebar. In the **3D Viewport**, Anim Assist adds the tabs **AnimAssist** (Lipsync, Help, Diagnostics), **Pose**, **Motion**, **Rig**, **Workspace** and **Layers**; Ghost Tool adds **Ghost Tool**; B4Artists Machine Learning adds **B4Artists ML**. In the **Graph Editor** sidebar you get **Keys** (curve and key tools) and **Motion**; in the **Dope Sheet** sidebar, **Pose** (breakdowns) and **Keys**.
5. On the **Workspace** tab, run **First Run Setup** once — it builds the Quick Shelf and default hotkeys.

B4Artists Machine Learning is an experimental public beta for Bforartists testing. Its current verified surface is deterministic/procedural posing, interpolation, contact workflows and bounded secondary motion; learned temporal quality, independent animator review and Cascadeur comparison are not yet qualified. It requires Bforartists and does not run on standard Blender. Test it on a copy of a `.blend` before using it in production work.

You don't need to unzip anything by hand — Bforartists installs directly from the `.zip`.

## Browse the source

The unpacked, readable source for each tool is in this repository so you can read it on GitHub without downloading anything:

- [`anim_assist/`](anim_assist/) — Anim Assist source (`core/`, `operators/`, `ui/`, `tests/`)
- [`ghost_tool/`](ghost_tool/) — Ghost Tool source
- [`b4artists_ml/`](b4artists_ml/) — B4Artists Machine Learning source

The source folders and the `releases/` zips contain the same code; the zips are just packaged for one-click install.

## Documentation

Human-readable manuals are in [`docs/`](docs/):

- [`docs/anim_assist/`](docs/anim_assist/) — Anim Assist user manual (PDF)
- [`docs/ghost_tool/`](docs/ghost_tool/) — Ghost Tool user manual (PDF)
- [`docs/b4artists_ml/`](docs/b4artists_ml/) — B4Artists Machine Learning specifications, evidence and delivery records
- [`docs/b4artists_ml/PUBLIC-BETA-v0.38.0.md`](docs/b4artists_ml/PUBLIC-BETA-v0.38.0.md) — beta scope, safety notes and feedback instructions

## Requirements

- **Bforartists 4.2+** (Anim Assist) / **Bforartists 4.x** (Ghost Tool). B4Artists Machine Learning development builds are verified on the recorded Bforartists test host. None of these add-ons are compatible with standard Blender.
- Registration, first-run setup and teardown of both add-ons are verified headless on **Bforartists 5.1.2** (Blender 5.2 base) via [`tests/smoke_bforartists.py`](tests/smoke_bforartists.py).

## License

Released under the **GNU General Public License v2.0 or later** — see [`LICENSE`](LICENSE).
