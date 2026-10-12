# Ghost Tool 4.2.6 user guide

This guide and its PDF describe the current repository test build, including the persistent toolbar, cached visibility and independent target folds. See the [Ghost toolbar guide](toolbar/README.md) for placement and recovery details.

Current repository version: 4.2.6. Live Update Markers and Live Update Skin default off. Ghosts pause during native gestures and refresh after animation edits settle. All 178 checks/cases pass on a Blender stand-in; native Bforartists validation remains pending.

## Install and find Ghost Tool

Download the [4.2.6 ZIP](../../releases/b4_ghost_tool_v4.2.6.zip?raw=1). In Bforartists, open Edit > Preferences > Add-ons > Install from Disk, select the ZIP and enable Ghost Tool. The internal package name is `ghost_tool`. When updating, restart Bforartists after installation. Existing saved scenes retain their live-update choices; turn off Live Update Markers and Live Update Skin once if you want snapshots while scrubbing.

The main entry is the Ghost Tool menu in the 3D Viewport header. In Edit > Preferences > Add-ons > Ghost Tool, choose Top Header, Top Toolbar, Right Sidebar (N), or Left Tool Shelf (T). Top Header remains the default. All locations share feature controls. Save preferences normally to retain your choice. Separate Window and Prototype Settings Editor launch controls have been removed.

This is a Bforartists add-on. Version 4.2.6 was checked using Blender 5.1.2 as a stand-in, with only the host registration gate patched. Native Bforartists toolbar geometry, Tool Shelf integration and production-rig validation are pending.

## Use the persistent toolbar

Choose Top Toolbar to keep Ghost actions in the native Tool Settings row beneath the main viewport header when headers are aligned at the top. Native tool and mode controls remain available. Wide layouts expose every feature; compact layouts place Compare, Physics, Look and Settings under More. Narrow layouts provide full access through Ghost in the same feature order.

Show Markers and Show Onion Skin generate and display previews. Their adjacent arrows open Marker options and Onion Skin options without generating. Use Show cached markers or Show cached skin at the top of those options to change existing preview visibility without rebuilding. Hidden markers cannot be picked or box-selected. Clear All Ghosts removes both markers and onion skins.

Hide Toolbar hides Ghost controls while keeping previews, targets, settings and the native row. Open Ghost Tool in the main header and choose Show Toolbar to recover it. That explicit action also reveals the native row if it was hidden through View controls. Leaving Top Toolbar preserves native region visibility.

Marker Targets, Compare Capture Targets and each saved reference's Snapshot Targets fold independently. Expanding one list leaves the other tools accessible. Options remain available when no target is selected; generation actions explain their missing prerequisites.

## Author new keyframes with live ghosts

Leave Ghost Tool enabled and move, rotate or scale your object or pose control. The backend keeps the last ghost snapshot throughout a native gesture, including gizmo interaction, without stepping through animation frames. After you confirm or cancel, it waits briefly for edits to settle and refreshes once. Auto-key can remain enabled; without auto-key, insert a key after confirming the pose.

Live Update Markers controls whether markers follow timeline changes; Live Update Skin controls onion skins. Both default off, and Show Markers or Show Onion Skin preserves your choices. With these controls off, scrubbing shows the last refreshed snapshot. Finishing an animation edit still refreshes existing ghosts. Freeze pauses these automatic refreshes too.

After installing 4.2.6, test a new pose on your rig, wait for a ghost refresh, and insert the key. Seek away and return to confirm it saved correctly. Repeat with auto-key enabled and with mesh ghosts or a pinned motion path visible. Record any jitter or lost pose in the [issue tracker](https://github.com/Axleonex/B4Artists_Toolkit/issues).

## Show and inspect motion

Start with an animated object or pose bone. Select the target and use Show Markers. The displayed target identifies the object or bone being inspected. Show Markers displays generated motion markers; it does not require saving a comparison snapshot.

Use the motion-path controls for object and bone paths. Onion Skin and mesh-ghost controls provide additional pose context. Generated markers and paths are derived displays; a saved comparison snapshot is a separate record.

## Edit motion

Use the path and handle tools to change the selected motion. Handle editing adjusts the curve's Bezier handles. The existing Shift+G access and handle-end dragging remain available; Alt keeps the handle pair aligned.

Easing presets change the motion between keys. Custom easing uses the four configured handle values. Draw to Keys converts annotation strokes into location keys: the longest stroke is the path and crossing dashes identify keys. Its dialog retains the target chosen when it opens.

Escape cancels a drag or preview and restores the original curves and marker positions. A lost target, file/history change or add-on shutdown also cancels the active gesture against surviving original curves. Inspect the result and use Undo/Redo to verify recovery in your scene.

The existing repair for persistent curve tags that blocked adding a Cycles modifier is retained. Old tags are removed on file load or when the add-on is enabled.

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

Folded display options keep the primary actions accessible. Settings are available through the chosen Ghost location and shared Settings popover. Check the target and existing values before adjustment. Restricted or missing targets should show an explanation rather than silently change another target.

For final review, test marker discovery, handle dragging and Escape, snapshot visibility, variants, restore, Undo/Redo, save/reopen, long names and a narrow panel. Use both object and bone animation. Record the failed step if anything is unexpected.

## Release verification

The exact 4.2.6 ZIP passed 117 background checks, 56 native toolbar checks and five native auto-key cases. Toolbar checks cover Object/Pose, full/compact/narrow/high-scale layouts, cache-preserving hide/show, missing targets and reload. Native move cases cover object and pose moves with live updates off and on, plus cancellation. They preserve the ghost snapshot during movement, refresh once after settlement and check the keyed pose after seeking away and back. See the [4.2.6 package receipt](releases/4.2.6/package-receipt.json) and [release notes](releases/4.2.6/RELEASE-NOTES.md).

These checks use a Blender 5.1.2 stand-in. Full keyboard navigation, theme variants and production rigs in Bforartists remain unverified. The toolbar adds no new sampling scheduler or backend jitter repair. Historical builds and their original evidence remain listed in the [release index](../../releases/VERSIONS.md).
