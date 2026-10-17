# Ghost Tool 4.3.1 user guide

Ghost Tool for Bforartists displays ghost meshes, motion paths and editable motion markers. Version 4.3.1 brings the direct viewport toolbar, separate Before/Ahead counts, hold-open tool settings, persistent marker dragging and refreshed snapshot marker restoration into the versioned guide.

This guide accompanies the [Ghost Tool 4.3.1 installation ZIP](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.3.1/b4_ghost_tool_v4.3.1.zip). Updating repository source does not update an installed add-on automatically: install the new ZIP and restart Bforartists. See the [release notes](releases/4.3.1/RELEASE-NOTES.md) and [package receipt](releases/4.3.1/package-receipt.json) for the packaged version and checksum.

## Install and find Ghost Tool

Download `b4_ghost_tool_v4.3.1.zip` and install it through Edit > Preferences > Add-ons > Install from Disk. Enable Ghost Tool and restart Bforartists after replacing an installed version. Check that Preferences reports version 4.3.1. An older ZIP still installs its original version.

Ghost Tool defaults to Top Toolbar in the native 3D Viewport Tool Settings row. With native headers at the top, this row sits just beneath the main viewport header. It follows native header alignment. Preferences also offer Right Sidebar (N) and Left Tool Shelf (T). Older saved Top Header choices migrate to the visible toolbar; the preference is now called Top Toolbar.

Native tool and mode controls remain available. Narrow or split viewports keep the full Ghost toolbar in the same order; middle-mouse drag the native row horizontally to reach tools outside the visible width. Choose View > Show Ghost Toolbar if its controls are hidden. Save preferences normally to retain display choices.

## Quick start: inspect an animated target

Select an animated object or pose bone and enable the first ghost icon. Click Ghosts to show mesh previews; set Before and Ahead independently. Click Wire or Solid to choose their appearance. Hold Ghosts to choose frame-step or keyframe sampling and adjust opacity, fade or In Front.

Click Paths to display a motion line. If no path target exists, the action can add the selected animated target. Use Add Selected Path for another target, or Follow Selection for a path that follows the current selection. Turn on Markers Display to expose editable points on a pinned path.

Click Drag, then pick and move markers in the 3D Viewport. Confirm a move and pick another marker without restarting Drag. Click Drag again or press Escape to leave the mode. Hold Drag before editing to choose how released markers affect the animation.

## Read the top toolbar from left to right

**Ghost Tool:** the first ghost icon enables or disables the overall tool. It is separate from the Ghosts mesh-display button. Turning the tool off also disarms its marker and handle edit modes. Hold it for Update Meshes While Scrubbing, Update Markers While Scrubbing and Freeze Updates.

**Ghosts:** click to show or hide ghost meshes. The adjacent Before and Ahead number controls each have minus and plus buttons. Wire Ghosts and Solid Ghosts are two explicit style selectors. Hiding meshes keeps the selected style; choosing a style does not serve as the visibility switch.

**Paths:** click to show or hide motion paths. Its own Before and Ahead controls sit beside it, followed by Add Selected Path and Follow Selection. Added targets remain when you select another object or bone. Follow Selection adds a preview for the current selection. Path targets and pinned edit markers are different concepts.

**Drag:** starts persistent Drag Markers mode. **Pin:** starts a marker pick that pins or unpins the marker you click. **Markers Display:** the diamond button immediately to the right of Pin shows or hides editable path markers. Hover names identify the tools themselves.

**Arc Style:** opens a single-click menu containing Solid, Speed Colored and Fade directly. It controls the ghost motion arc; it does not select Wire or Solid mesh display. Paths have a separate Line Style setting in their hold menu. **Spacing Ticks:** toggles spacing indicators; hold it for Acceleration Indicators.

**Settings:** opens the advanced Ghost controls, including the existing marker-generation, target, range, editing, comparison, physics and appearance workflows. The top row no longer repeats Generate and Clear as standalone icons. These operations remain accessible in the advanced controls.

## Set Before and Ahead counts

There are two numbers beside Ghosts and two beside Paths. The first is Before: samples earlier than the current frame. The second is Ahead: samples later than the current frame. They are independent counts, not a single combined density control. Edit a number directly or use its minus and plus buttons in the top toolbar. A count of zero disables samples on that side.

Counts specify how many samples to request. Sampling determines where those samples lie. With the playhead at frame 20, Ghosts Before 3, Ahead 2 and a frame step of 2 request earlier samples at 18, 16 and 14 and later samples at 22 and 24, subject to available animation and range limits. The playhead pose is not one of those before/ahead samples.

By Keyframe uses the target's animation keys instead of evenly spaced frames. Its interval can skip keys. Editing the Paths count fields selects the count-based window around the playhead. Advanced frame-range modes remain available in Settings; they use their own range rules.

## Hold a tool for its settings

An ordinary click performs the main action. Press and hold a supported tool button to open its parameter menu. Arc Style is the exception: an ordinary click opens its three choices immediately. Settings uses a normal click to open the advanced popover.

**Hold Ghosts:** choose frame-step or keyframe sampling. Frame-step sampling exposes Every (Frames); set it to 1 for every frame. Keyframe sampling exposes Keyframe Interval, including a custom interval. Appearance controls include Opacity, In Front and Fade.

**Hold Paths:** choose sampling and its frame or key interval. Line Style, Frame Numbers and Bezier Handles control the path display. Enable Bezier Handles when you want to inspect or edit curve handles.

**Hold Markers Display:** change the sampling shared with Motion Paths, show keyframe dots and toggle marker frame numbers. This menu is available on the top toolbar. Markers do not have an independent third sampling mode; changing it here also changes Paths sampling.

**Hold Drag:** choose When Released, Curve Shape or Smooth Neighbours as applicable, Nearby Frame Reach and Falloff. **Hold Pin:** read the pin instructions or choose Unpin All Markers. **Hold Follow Selection:** adjust Highlight Active Path. **Hold Spacing Ticks:** choose Acceleration Indicators.

## Use the bottom Timeline toolbar

The compact Ghost strip sits inline beside the native Timeline buttons. It is not a second custom row underneath the Timeline toolbar. The 4.3.1 documentation update does not redesign this strip.

Its order is: overall ghost on/off; mesh Ghosts display; previous and ahead mesh counts; Wire and Solid; Drag Markers; editable-marker diamond; Paths display; previous and ahead path counts. The two numbers in each pair follow the same earlier/later order as the top toolbar.

Hold the Timeline Ghosts or Paths button for Frame by Frame, By Keyframe, sampling intervals and display settings. More Ghost Settings opens the fuller options. The bottom diamond is a direct marker toggle; its separate hold menu is on the top toolbar's Markers Display button. Snapshots are available through Compare in advanced settings, not as a bottom-strip button.

## Drag markers repeatedly

Enable Ghost Tool and display editable markers for an animated target. Clicking Drag arms the picker; the status text asks you to click a marker in the 3D Viewport. A click near empty space keeps the picker waiting, so move closer to a visible marker. Confirming a marker move leaves Drag active for the next edit. All buttons that launch Drag Markers share this mode.

Click Drag again or press Escape to turn it off. Escape during a move cancels that move and restores its original curves and marker positions. Confirmed earlier moves are separate edits; use Undo to reverse them. Turning off the tool, losing a target, changing file/history or shutting down the add-on also ends or cancels affected edit sessions.

Path-handle dragging also supports a persistent wait mode. Display Bezier Handles, start the handle-drag action and pick successive visible handles. Shift+G access remains available. Alt toggles aligned-handle behavior during a handle drag. Escape cancels an in-progress handle move and exits the mode.

## Choose smooth or sharp motion edits

Hold Drag and inspect When Released. Reshape Handles changes existing Bezier handles so the curve passes through the moved sample without adding a keyframe. Curve Shape offers Free, Locked and Smooth: Free allows unrestricted handle adjustment, Locked preserves handle angles, and Smooth redistributes handle influence across the segment.

Insert Keyframe writes a real key at the marker's frame. Smooth Neighbours can smooth the adjacent key handles after that insertion. Nearby Frame Reach and Falloff control how surrounding frames participate in sculpting.

The visible line also depends on sampling density. Widely spaced samples form a coarse line even when the underlying animation is curved. Use a smaller frame step to inspect the result. A sharp turn can come from the interpolation/handles or the edit mode; adding more display samples alone does not change the animation's curve shape.

## Pin markers and manage path targets

Click Pin, then click a visible marker to toggle its pinned state. Pin is a pick action, not the persistent Drag toggle; invoke it again to pick another marker. You can pin multiple markers. There is no one-pin-only workflow. Pinned markers remain fixed while reshaping, and a refresh preserves matching pinned marker records. Hold Pin and choose Unpin All Markers to release them together.

Adding a path target retains the object or bone in the path list; it does not freeze all its animation samples. Follow Selection changes the selection preview while explicitly added targets remain. Use the path list in Settings to manage those targets. Use Markers Display for the editable points along pinned paths; Keyframe Dots are a separate display aid.

## Live updates and native animation editing

Live Update Markers and Live Update Skin default off; existing scenes retain their saved values. With them off, scrubbing keeps the last refreshed preview. Use the update options under the master ghost icon to change this behavior. Freeze Updates pauses automatic refreshes too.

During native move, rotate, scale and gizmo gestures, Ghost keeps the last preview instead of stepping through animation frames. After confirmation or cancellation, it waits for edits to settle and refreshes existing ghosts. Auto-key can remain enabled; without auto-key, insert the intended key after confirming the pose. Generate in the advanced marker controls provides explicit regeneration when needed.

The advanced controls still offer Marker Targets, onion-skin sources, range, subdivision and appearance options. Cached marker and cached skin visibility hide or show their existing previews without rebuilding them. Clear All Ghosts removes markers and onion skins; use visibility controls when you only want to hide them. Hidden markers cannot be picked or box-selected.

## Save, compare and restore snapshots

Open Compare through Settings. Select the intended capture scope before Save Snapshot: Active Object / Selected Bones, Selected Path, selected marker channels or explicit scene scope. Confirm the target shown in the panel. Snapshots retain frozen samples and captured keyframes/handles, and are stored with the scene across save/reopen and add-on disable/re-enable.

Hide/Show changes a snapshot overlay without changing animation. Save Variant creates an independent alternate with its origin recorded; deleting the parent preserves the alternate. At ten retained snapshots, delete unwanted records before saving another. Capture, variants, binding, visibility, deletion and restore participate in native Undo/Redo.

Restore validates scene, object, action, slot, bone and channel identity before writing. It restores the captured curves and marker records for the snapshot's scope and refreshes the display, including when live updates are off or frozen. It does not restore unrelated objects or arbitrary Action modifiers. Older sample-only references restore suitable sampled values where curves can be reshaped.

Replaced targets require deliberate binding. Shared action slots are refused; make animation single-user first. Bind to Active Target supports one original object and its named bone channels per reference. Multi-object imported references remain viewable and unbound rather than being collapsed onto one target. Bone renames are followed. After save/reopen, channel identity identifies the curve; during a gesture, a replaced curve does not receive rollback writes intended for its original.

## Transfer snapshots and use advanced tools

Export snapshots to JSON for comparison-data transfer. Import validates and merges records, remaps ID collisions and rejects unsupported versions or capacity overflow atomically. Imported and legacy references remain viewable, but restoration requires explicit binding because JSON cannot prove original object identity. Unreadable existing scene records are preserved if an import fails.

Edit Motion retains easing presets and custom easing controls. Draw to Keys converts the longest annotation stroke into a location path; crossing dashes identify keys. Its dialog retains the selected target. Physics Feel, Look, Compare and other advanced tools remain available through Settings and the alternative sidebar/shelf locations.

## Troubleshooting and version notes

If nothing appears, confirm the first ghost icon is enabled, the target is animated, the relevant display is on and its counts are above zero. For missing editable points, add the target to Paths and enable Markers Display. More visible samples may require a smaller step or a different keyframe interval. Marker sampling follows Paths sampling.

If the toolbar is missing, select Top Toolbar in Ghost preferences and use View > Show Ghost Toolbar. If it is cut off in a split viewport, scroll the native row horizontally. Left shelf width preferences remain available; their full width/scale verification was incomplete in 4.2.11, so this release does not promise that all shelf-width cases were fixed.

The direct-tool implementation received 188 targeted background checks before this version/documentation update, covering toolbar UI, authoring, paths, snapshots, startup, display location and cached display. Those results describe the previously tested implementation. The 4.3.1 archive has separately checked ZIP integrity, version metadata and byte-for-byte source matching; no new functional test run is claimed for this packaging step. Use the [issue tracker](https://github.com/Axleonex/B4Artists_Toolkit/issues) to report the target, operation and failed step.
