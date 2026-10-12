# Ghost Tool 4.2.2

Keeps cached ghosts stable while you move an animated object or pose control with auto-key enabled, then refreshes after the gesture ends and edits settle.

- Renames the two timeline controls to **Live Update Markers** and **Live Update Skin**. Both default off; generating ghosts preserves your choices.
- Pauses background frame sampling during native modal gestures and refreshes existing snapshots after animation edits, even with timeline following off.
- Ignores unchanged evaluation and generated ghost notifications to prevent repeated refreshes.
- Retains the 4.2.1 protection for unkeyed poses during sampling.

Install `b4_ghost_tool_v4.2.2.zip` through Bforartists Preferences > Add-ons > Install from Disk, then restart Bforartists. Saved scenes retain their old settings: turn Live Update Markers and Live Update Skin off once to keep cached snapshots while scrubbing.

The exact ZIP passes 230 background checks across nine suites, including 20 authoring regressions, and five native GUI auto-key move/cancel cases on Blender 5.1.2. Bforartists production-rig validation and owner acceptance remain pending, so this is a prerelease.

With auto-key enabled, move your object or pose control. Ghosts should hold during the move and refresh afterward. Scrub away and return to check the key; repeat with gizmo, rotation, scale and cancellation.

[Verification report](https://github.com/Axleonex/B4Artists_Toolkit/blob/89ad6d265cf1adab0b700b05214c18fc1389974c/docs/ghost_tool/authoring-pause/verification.md)

ZIP SHA256: `d74c692e4c6e62608fe3a093e6c5f6f9c891583b01429934ea42e96817ffff2b`.
