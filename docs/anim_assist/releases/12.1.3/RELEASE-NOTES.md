# Anim Assist 12.1.3

Local release, 2026-10-11. Not published to GitHub. Bug fixes only; no interface, tool ID, setting or default changes.

## Fixes

- **Lipsync on animation layers (Blender 5.x).** Bake and Rebake Lipsync on a layer that Animation Layers had already keyed created a second Action slot. The layer stack reads only the first slot, so baked keys did not appear. Lipsync now reuses the layer Action's only slot. Clear Auto Keys and Mark Manual no longer create slots.
- **Recents from older files.** Files saved by 12.1.0 and earlier stored Recents oldest-first, so Repeat Last ran the oldest tool. Recents and Repeat Last now follow each entry's timestamp, and the stored list is reordered the next time a tool is recorded.

Includes all 12.1.2 changes.

## Install

Install `releases/b4_anim_assist_v12.1.3.zip` through Bforartists Preferences > Add-ons > Install from Disk, replacing 12.1.2. The archive's package root is `B4_anim_assist`; all four version fields are 12.1.3.

SHA256: `b30547b2afacbe1f56d0d8066ac7e607aeaa24297aa8612d9482272a37b493e1` (556,067 bytes). File layout matches 12.1.2 (201 files). See `package-receipt.json`.

## Verification

The exact ZIP now passes on **Bforartists 5.2.0**, Blender runtime 5.3.0 Alpha, build `0a1ca45552db`: 170 internal tests, 26 repair checks and 16 workflow checks; exit 0. The configured shape-key bake/rebake check confirms manual keys survive rebake. The single Action slot and legacy Recents checks pass.

See [VERIFICATION.md](VERIFICATION.md) for scope and limitations. Earlier Blender 5.1.2 stand-in evidence is superseded as the actual-host gate by this fresh verification. Historical raw logs are retained locally. Publication remains pending.
