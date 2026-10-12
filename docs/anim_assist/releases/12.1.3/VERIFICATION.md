# Anim Assist 12.1.3 verification

The exact ZIP passed the actual Bforartists 5.2.0 run: 170 internal tests, 26 repair checks and 16 workflow checks. Host runtime: Blender 5.3.0 Alpha, build `0a1ca45552db`. Exit code: 0.

Archive SHA256: `b30547b2afacbe1f56d0d8066ac7e607aeaa24297aa8612d9482272a37b493e1`. Source and package match.

The single Action slot, legacy Recents ordering, configured shape-key bake/rebake and manual-key preservation all pass. Panel layout, file lifecycle and workflow checks also pass.

This does not establish every interactive operator or other host builds. Rhubarb was not exercised. See the [shared verification](../../../releases/2026-10-11/VERIFICATION.md).
