# Ghost Tool 4.2.1 user guide

Current repository test build: 4.2.1. It fixes live refresh resetting an unkeyed pose while you author a new keyframe. All 13 focused authoring checks pass on a Blender stand-in; Bforartists viewport validation remains pending. The earlier 4.2.0 prerelease remains on GitHub Releases.

## Install and find Ghost Tool

Download the [4.2.1 ZIP](../../releases/b4_ghost_tool_v4.2.1.zip?raw=1). In Bforartists, open Edit > Preferences > Add-ons > Install from Disk, select the ZIP and enable Ghost Tool. The internal package name is `ghost_tool`. When updating from 4.2.0, restart Bforartists after installation.

The main entry is the 3D Viewport header: the ghost toggle and Ghost Tool menu next to Pose. The menu groups display, editing, comparison and settings controls. Open in Separate Window keeps the controls available in a separate window.

This is a Bforartists add-on. Version 4.2.1 was checked using Blender 5.1.2 as an animation-evaluation stand-in. Its Bforartists viewport validation is pending. The earlier 4.2.0 build passed its recorded checks on Bforartists 5.2.0, with Blender runtime 5.3.0 Alpha, build `0a1ca45552db`.

## Author new keyframes with live ghosts

Leave Ghost Tool and live ghosts enabled, move or rotate your object or pose control, confirm the transform, then insert a key. Live sampling preserves your unkeyed transform values and waits during native move, rotate and scale operations. The ghost display refreshes after the operation finishes.

After installing 4.2.1, test a new pose on your rig, wait for a ghost refresh, and insert the key. Seek away and return to confirm it saved correctly. Repeat with auto-key enabled and with mesh ghosts or a pinned motion path visible. Record any jitter or lost pose in the [issue tracker](https://github.com/Axleonex/B4Artists_Toolkit/issues).

## Show and inspect motion

Start with an animated object or pose bone. Select the target and use Show Markers. The displayed target identifies the object or bone being inspected. Show Markers displays live generated motion markers; it does not require saving a comparison snapshot.

Use the motion-path controls for object and bone paths. Onion Skin and mesh-ghost controls provide additional pose context. Generated markers and paths are derived displays; a saved comparison snapshot is a separate record.

## Edit motion

Use the path and handle tools to change the selected motion. Handle editing adjusts the curve's Bezier handles. The existing Shift+G access and handle-end dragging remain available; Alt keeps the handle pair aligned.

Easing presets change the motion between keys. Custom easing uses the four configured handle values. Draw to Keys converts annotation strokes into location keys: the longest stroke is the path and crossing dashes identify keys. Its dialog retains the target chosen when it opens.

Escape cancels a drag or preview and restores the original curves and marker positions. A lost target, file/history change or add-on shutdown also cancels the active gesture against surviving original curves. Inspect the result and use Undo/Redo to verify recovery in your scene.

Version 4.2.1 includes the 4.2.0 r4 repair for persistent curve tags that previously blocked adding a Cycles modifier. Old tags from r1-r3 are removed on file load or when the add-on is enabled.

## Save snapshots and variants

In Compare, select the intended scope before Save Snapshot: Active Object / Selected Bones, Selected Path, selected marker channels or explicit scene scope. Check the displayed target.

A snapshot retains frozen samples and captured keyframes/handles. It is stored with the scene and survives save/reopen and add-on disable/re-enable. Capture, variants, binding, visibility, deletion and restore participate in native Undo/Redo.

Use Hide/Show to compare a saved overlay with the current animation. Changing overlay visibility does not change animation. Save Variant creates an independent alternate with its origin recorded. Deleting the parent does not delete the alternate.

At ten retained snapshots, delete unwanted records before saving another. Existing records are not silently evicted. Review any deletion confirmation.

## Restore and bind deliberately

Restore checks scene, object, action, slot, bone and channel identity before writing. Replaced targets require deliberate binding. Shared action slots are refused because changing them would also affect another object; make the animation single-user first.

Current snapshots restore captured keyframes and handles, not arbitrary Action modifiers or unrelated channels. Older sample-only references restore their sampled values where the curve can be reshaped. Bone renames are followed; unsuitable sampled segments are skipped.

Bind to Active Target supports one original object and its named bone channels per reference. A multi-object imported reference remains viewable and unbound; it is not silently collapsed onto one object.

After save/reopen, channel identity identifies the curve. A channel deleted and re-keyed across that boundary is treated as the same channel. During a gesture, a replaced curve does not receive rollback writes intended for the original.

## JSON transfer

Export snapshots when transferring comparison data. Import validates and merges records, remaps ID collisions and rejects unsupported versions or capacity overflow atomically.

JSON cannot prove original object identity. Imported and legacy references remain viewable, but restoration requires explicit binding. An import into a scene with unreadable saved records fails with existing data preserved.

## Settings and review

Folded display options keep the primary actions accessible. The optional Settings Editor remains labeled Prototype. Check its target and existing values before adjustment. Restricted or missing targets should show an explanation rather than silently change another target.

For final review, test marker discovery, handle dragging and Escape, snapshot visibility, variants, restore, Undo/Redo, save/reopen, long names and a narrow panel. Use both object and bone animation. Record the failed step if anything is unexpected.

## Release verification

The exact 4.2.1 ZIP passed all 13 focused authoring checks. Across ten suites, 229 checks passed on a Blender 5.1.2 stand-in. Ten supplemental cases fail the same way on the 4.2.0 ZIP: nine depend on annotation APIs unavailable in this stand-in, and one fresh-process case encounters the Bforartists-only registration gate. See [4.2.1 repair verification](authoring-fix/verification.md) and its [package receipt](authoring-fix/package-receipt.json).

The earlier 4.2.0 r4 ZIP passed 320 checks across 17 suites on its recorded Bforartists host. Those results describe that build, not the 4.2.1 repair. See [4.2.0 verification](afterimage-release/VERIFICATION-r4.md) and the [owner checklist](afterimage-release/UAT.md). Bforartists viewport validation and final owner acceptance of 4.2.1 remain pending.
