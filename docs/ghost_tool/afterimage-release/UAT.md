# Ghost Tool 4.2.0 hands-on check

Status: automated checks pass; final owner usability acceptance is pending. Earlier prototype acceptance does not accept this exact r4 candidate.

Install [the 4.2.0 ZIP](../../../releases/b4_ghost_tool_v4.2.0.zip) through Bforartists Preferences > Add-ons. Use a saved copy of a scene with an animated object and, for the bone checks, an animated armature. The recorded test host is Bforartists 5.2.0.

## Review sequence

1. Select the animated object. Use Show Markers and check the displayed target and immediate marker display.
2. In Compare, choose Active Object / Selected Bones and Save Snapshot. Check the target and saved-with-scene wording.
3. Change easing or drag a path handle. Cancel a drag with Escape and check both curves and marker positions recover.
4. Hide/Show the snapshot. Confirm visibility does not change animation.
5. Save Variant. Check its origin; delete the parent and confirm the alternate remains usable.
6. Restore, then Undo and Redo. Also undo a snapshot deletion and visibility change.
7. Save under a new name and reopen. Check snapshots, visibility and binding. Changing selection must not silently change a reference's restore target. Test explicit binding for imported JSON.
8. Test narrow panels, long names, object and bone paths, and mesh ghosts. Check pointer feel and discoverability.

Record that this exact r4 candidate passes, or report the numbered step and what failed. The exact ZIP has already passed 320 automated checks across 17 suites on the real host; those checks do not replace this owner review.

SHA256: `443abacb14e2154251dff4b6a98eb56ffb5bf9b0b3d1d88a0cce30c3a2bc79b3`.
