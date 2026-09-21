# B4Artists Anim Tools

Two animation add-ons for **Bforartists** (the Blender fork). Both are **Bforartists-exclusive** — they do not run on standard Blender.

| Tool | Version | What it does |
|---|---|---|
| **Anim Assist** | 12.0.2 | A production animation workflow suite (~400 operators across 11 feature phases): key editing, breakdowns, trajectory polish, retiming, proxies, IK/FK matching, mirroring, animation layers, and a hybrid PREVIEW/SHIPPED lipsync system. Inspired by Maya's AnimBot. |
| **Ghost Tool** | 3.3.3 | Ghost keyframe visualization and manipulation: generates draggable in-between markers in 3D space and recalculates f-curves live. Includes onion skinning, motion trails, easing presets, snapshots, Physics Feel archetypes, and Visual Diff Mode. |
| **B4Artists Machine Learning** | 0.37.51 beta | Standalone, local procedural animation assistance for humanoid and quadruped rigs. The beta includes deterministic posing, interpolation, contact and bounded secondary-motion workflows; learned motion remains explicitly unqualified. |

> These tools were built with heavy AI assistance and are under active bug-fixing. If you hit an issue, a screenshot or a note about what you were doing helps a lot — please open an [issue](../../issues).

## Download & install

The ready-to-install add-ons live in [`releases/`](releases/):

- `b4_anim_assist_v12.0.2.zip`
- `b4_ghost_tool_v3.3.3.zip`
- `b4artists_ml_v0.37.51-beta.1.zip` — public-beta candidate; build locally with `training/b4artists_ml/build_public_beta_package_v1.py` before attaching it to a GitHub prerelease

To install in Bforartists:

1. **Edit -> Preferences -> Add-ons -> Install from Disk...**
2. Pick the `.zip` for the tool you want.
3. Enable the add-on by ticking its checkbox.
4. Open the **N-panel** in the 3D Viewport — Anim Assist adds tabs (Keys, Pose, Motion, Rig, Workspace, Layers, Lipsync); Ghost Tool adds a **Ghost Tool** tab; B4Artists Machine Learning adds a **B4Artists ML** tab.

B4Artists Machine Learning is an experimental public beta for Bforartists testing. Its current verified surface is deterministic/procedural posing, interpolation, contact workflows and bounded secondary motion; learned temporal quality, independent animator review and Cascadeur comparison are not yet qualified. It requires Bforartists and does not run on standard Blender. Test it on a copy of a `.blend` before using it in production work.

You don't need to unzip anything by hand — Bforartists installs directly from the `.zip`.

## Browse the source

The unpacked, readable source for each tool is in this repository so you can read it on GitHub without downloading anything:

- [`anim_assist/`](anim_assist/) — Anim Assist source (`core/`, `operators/`, `ui/`, `tests/`)
- [`ghost_tool/`](ghost_tool/) — Ghost Tool source
- [`b4artists_ml/`](b4artists_ml/) — B4Artists Machine Learning source

The source folders and the `releases/` zips contain the same code; the zips are just packaged for one-click install.

## Documentation

Human-readable manuals and diagnostic reports are in [`docs/`](docs/):

- [`docs/anim_assist/`](docs/anim_assist/) — Anim Assist user manual (PDF) + diagnostics report
- [`docs/ghost_tool/`](docs/ghost_tool/) — Ghost Tool user manual (PDF) + diagnostics report
- [`docs/b4artists_ml/`](docs/b4artists_ml/) — B4Artists Machine Learning specifications, evidence and delivery records
- [`docs/b4artists_ml/PUBLIC-BETA-v0.37.51.md`](docs/b4artists_ml/PUBLIC-BETA-v0.37.51.md) — beta scope, safety notes and feedback instructions

## Requirements

- **Bforartists 4.2+** (Anim Assist) / **Bforartists 4.x** (Ghost Tool). B4Artists Machine Learning development builds are verified on the recorded Bforartists test host. None of these add-ons are compatible with standard Blender.

## License

Released under the **GNU General Public License v2.0 or later** — see [`LICENSE`](LICENSE).
