# Ghost Tool 4.2.0 - complete user manual

Published build: **4.2.0**, released as a **prerelease**. Its package receipt records internal revision r4. Automated host checks pass; final owner pointer/usability acceptance remains pending. This manual covers every source-defined command, scene setting, preference and operator argument in that build.

Ghost Tool displays motion in the viewport and lets you reshape it. Generated markers, motion paths, mesh onion skins, Visual Diff references and retained snapshots are different kinds of data. Learn their purpose before using an editing or restore command.

## Contents

- [1. Install, upgrade and locate the controls](#1-install-upgrade-and-locate-the-controls)
- [2. Motion data, targets and a first exercise](#2-motion-data-targets-and-a-first-exercise)
- [3. Marker generation, subdivision and display](#3-marker-generation-subdivision-and-display)
- [4. Marker selection, pinning and dragging](#4-marker-selection-pinning-and-dragging)
- [5. Persistent motion paths, folders and batch controls](#5-persistent-motion-paths-folders-and-batch-controls)
- [6. Editing path handles and applying easing](#6-editing-path-handles-and-applying-easing)
- [7. Onion skin, mesh ghosts and skeleton display](#7-onion-skin-mesh-ghosts-and-skeleton-display)
- [8. Visual Diff and reference staleness](#8-visual-diff-and-reference-staleness)
- [9. Physics Suggest, ballistic preview and Physics Feel](#9-physics-suggest-ballistic-preview-and-physics-feel)
- [10. Draw to Keys from annotation strokes](#10-draw-to-keys-from-annotation-strokes)
- [11. Saved snapshots, variants and visibility](#11-saved-snapshots-variants-and-visibility)
- [12. Restore, explicit binding and JSON transfer](#12-restore-explicit-binding-and-json-transfer)
- [13. Live refresh, performance and Settings Editor](#13-live-refresh-performance-and-settings-editor)
- [14. Troubleshooting and verification](#14-troubleshooting-and-verification)
- [15. How to use the complete reference](#15-how-to-use-the-complete-reference)
- [Reference A. Complete command reference](#reference-a-complete-command-reference)
- [Reference B. Named easing profiles](#reference-b-named-easing-profiles)
- [Reference B2. Built-in help topics](#reference-b2-built-in-help-topics)
- [Reference C. Complete settings and saved-record reference](#reference-c-complete-settings-and-saved-record-reference)
- [Reference D. Command lookup index](#reference-d-command-lookup-index)

## 1. Install, upgrade and locate the controls

Download the [4.2.0 install ZIP](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.2.0/b4_ghost_tool_v4.2.0.zip). Open Bforartists > Edit > Preferences > Add-ons > Install from Disk, select the ZIP and enable Ghost Tool. The internal package folder is `ghost_tool`. Install the archive directly.

For an upgrade, save the scene, finish or cancel any Ghost Tool gesture, replace the installed addon and verify the version in Preferences. Restart Bforartists if an older module remains loaded. Open a copied scene and check targets, retained snapshots and animation before saving over your working file.

Ghost Tool is intended for Bforartists. Standard Blender receives an unsupported-host notice. The actual-host run used Bforartists 5.2.0 with Blender runtime 5.3.0 Alpha, build `0a1ca45552db`; other builds were not verified by that run.

The main home is the **3D Viewport header**, beside the Pose menu: a ghost toggle and the **Ghost Tool** dropdown. The grouped interface provides display, onion skin, editing, comparison, physics, look and settings controls. It does not add a normal Ghost Tool tab to the main viewport sidebar.

**Open in Separate Window** provides another viewport with Ghost Tool controls. The floating toolbar offers the same grouped workflow. **Settings Editor (Prototype)** is a different, opt-in window that captures a target and exposes persistent settings. It retains its prototype status in 4.2.0.

The **Timeline and Dope Sheet headers** also have a compact ghost strip: enable/disable, Generate/Clear, subdivision, drag, pin, snapshot, arc/spacing/onion-skin toggles and motion-path controls. The **Graph Editor header** has the ghost toggle and compact Paths controls. Paths, Add, Follow and the path-options popover let you manage the display while adjusting timing or curves. If the header reports that paths are slow, reduce their frame range or sampling cost. Start spatial drags in the source 3D Viewport where you can see the markers or handles.

## 2. Motion data, targets and a first exercise

**Markers** sample positions between existing animation keys. Moving a marker can change the underlying curves, depending on Editing Mode. A marker is not automatically a real keyframe.

**Motion paths** trace selected objects, bones or vertices across time. Their visible curve handles provide another way to edit keyed motion. A path list keeps pinned paths available after the selection changes.

**Mesh ghosts/onion skins** show evaluated mesh poses at other frames. They provide silhouette and spacing context. Generated mesh duplicates are display objects, not a substitute for the original rig or animation.

**Visual Diff** compares the current pose against a pinned frame. **Snapshots** retain samples and captured keyframe data for comparison and deliberate restoration. **Variants** capture an independent alternate with a recorded origin. Hiding a reference overlay does not remove animation keys.

**First exercise: a moving object.**

1. Save a test scene and select one object. Add location keys at frames 1 and 25 with visibly different positions.
2. Enable Ghost Tools and use Show Markers or Generate Ghosts for that target. Use a low subdivision level initially.
3. Enable an arc or path display to see the motion between the keys.
4. Move the pointer over a marker. Use Shift+G to start a drag, make a small change and cancel with Escape. Confirm the original curve and marker position return.
5. Repeat, confirm the edit, and use Undo to compare the previous motion.
6. Save a snapshot before exploring insertion, easing or physics stamping.

For a rig, make the armature active, enter Pose Mode and choose the bones whose motion you want to inspect. Read the displayed target before editing. A path's traced point, an object's origin and a pose bone are not interchangeable targets.

## 3. Marker generation, subdivision and display

Generate Ghosts samples the active object and selected bones. Subdivision controls how many in-between marker levels are generated. Level visibility switches control what you see; hiding a level does not remove the animation that produced it.

Custom range settings constrain generation. Start and End are frame limits, while Before/After settings in other display modes are relative to the playhead. Review which range mode is active before entering numbers. A dense range and high subdivision can make selection harder and increase display cost.

Keyframe markers show actual keyed positions. In-between markers show sampled motion between keys. Key bookends and hover labels help you identify the surrounding timing. Past/future coloring, level colors, marker size, opacity and fade affect readability rather than animation values.

Motion arcs, spacing ticks and acceleration markers help inspect trajectory and timing. Uniform sample times with uneven spatial gaps show changing speed. A crowded overlay can conceal that pattern; reduce the visible range or show fewer levels.

**Example: compare spacing through an acceleration.**

1. Generate markers on an object with Bezier location animation.
2. Enable the motion arc and spacing ticks.
3. Inspect samples at equal time intervals: narrow gaps indicate less movement during those intervals.
4. Change easing or handles, then regenerate or allow live refresh.
5. Compare the new spatial spacing with the intended action instead of judging only the curve's screen shape.

Clear All Ghosts clears the generated marker display for the current scene and invalidates its generated cache. It is separate from deleting a retained snapshot or clearing the pinned motion-path list. Use the matching command for the data you intend to remove.

## 4. Marker selection, pinning and dragging

Select Ghost chooses a marker under the pointer. Its selection workflow supports a single selection and toggle/extend behavior. **Shift+B** invokes the addon box-selection tool in Object or Pose Mode. Drag a rectangle to select the visible screen-space markers; use its extend option when retaining an existing selection.

**Shift+G** starts marker dragging in Object or Pose Mode. The same gesture is also offered to motion-path handle dragging: if the pointer is near a visible handle end, that tool can handle the event first. Move the pointer away from a handle when you intend to drag a marker.

During a marker drag, X, Y or Z constrains an axis; Shift plus the axis constrains the perpendicular plane. Inspect the modal prompt and confirm behavior for the invoked gesture. Escape or right-click cancels and restores surviving original curves and marker positions. Undo handles a completed edit.

**Reshape Handles** changes Bezier handle influence to reach a sampled target without treating every marker as a new key. **Insert Keyframe** writes a real key at the edited marker time. Smooth Neighbors on Commit and sculpt falloff extend or soften the change according to their settings. A falloff radius of zero avoids a broader neighboring influence.

Curve Shape Mode offers Free, Locked and Smooth behavior. Read the choices in the settings reference before choosing how handles may change. A handle shape change and a change in a key's time are separate edits.

Pin/Unpin Ghost marks a generated marker as pinned; Unpin All clears those marker pins. Pinning a marker is not the same as saving a persistent reference. Regeneration, target changes and file reopening should be checked against the specific saved data you intend to preserve.

**Example: sculpt one arc without adding keys.**

1. Generate markers for one keyed target and save a snapshot.
2. Choose Reshape Handles and a small or zero falloff radius.
3. Drag an in-between marker slightly toward the desired arc. Keep the target and editor context available.
4. Cancel the first trial, then repeat and confirm a small edit.
5. Inspect the Graph Editor: verify which handles changed and that no unintended insertion occurred.
6. Try Insert Keyframe only when an additional keyed pose is your intended result.

A lost target, file/history change or addon shutdown cancels an active gesture against the surviving original curves. Replaced curves are not safe rollback targets. Finish or cancel the current gesture before starting another Ghost operation.

## 5. Persistent motion paths, folders and batch controls

**Add Path for Selected** pins paths for selected objects, selected bones in Pose Mode, or selected mesh vertices in Edit Mode. Vertex paths have a limit of 50 additions per click. A vertex path follows the evaluated mesh point and can be more costly than an object-origin path.

Use the path list to control individual visibility, color, thickness, key dots, frame numbers, in-front drawing and traced point. A per-path Own Range overrides the global range for that path. Otherwise, global range and sampling determine what it displays. Follow Selection provides a live selection-related display; pinned list entries provide an explicitly retained set.

**Add Folder** groups checked paths. Open or Close Folder changes the list presentation. Removing a folder moves its paths to the top level rather than silently deleting every path inside it. Removing a path unpins that path; Clear Paths unpins the whole list.

Checked rows are the batch scope. **Apply to Checked** copies the selected path's style and traced-point settings to checked paths. **Checked Paths** offers the supported show, hide, remove, range-reset and move actions. Check the rows before applying an action; a selected row and a checked row are different states.

**Example: organise hands and feet.**

1. Pin the two hand paths and two foot paths from the active armature.
2. Check the hand rows and add a Hands folder. Repeat for Feet.
3. Give one hand path an identifiable color and line thickness, then copy it to the checked hand rows if desired.
4. Use per-path range only for a path needing a special contact interval; keep the others on the global range.
5. Collapse folders to shorten the list and toggle visibility to reduce viewport clutter.

In Front makes a path visible through scene geometry; it changes display occlusion, not the path coordinates. When frame numbers or key dots appear crowded, increase sampling step, shorten the range or hide labels.

## 6. Editing path handles and applying easing

Enable Handles on a motion path to display the Bezier handle ends for location keys. Start near a handle end with a left-click or Shift+G. Drag Path Handle changes its value while retaining the handle's time and the key's position. Alt toggles aligned behavior so the opposite handle turns with it. Escape or right-click restores the original state.

Path-handle editing is a location-curve workflow. It does not imply that every rotation or custom-property curve can be manipulated as a spatial path. If a handle is missing, check the selected path, Handles visibility, keyed location channels and interpolation.

**Example: reduce an overshoot.**

1. Pin the object's path and show its key dots and handles.
2. Find the outgoing or incoming handle responsible for the overshoot.
3. Drag its value toward a flatter tangent, cancel to compare, then confirm the intended result.
4. Check whether aligned behavior should move the paired tangent.
5. Inspect the Graph Editor and play through the edited segment.

Apply Easing Preset changes the handle profile between keys in the selected ghost range. Presets include the named profiles listed in the easing reference. Choose a small known segment and check that the correct channels are in scope before applying one.

Custom easing uses Left Handle X/Y and Right Handle X/Y as normalised offsets relative to the segment's time and value span. These values are not world-space positions. Start with small adjustments; extreme vertical offsets can create visible overshoot. Key type, key time, interpolation and handle profile remain distinct concepts.

## 7. Onion skin, mesh ghosts and skeleton display

Generate Mesh Ghosts creates translucent evaluated mesh duplicates for the configured frames. Clear Mesh Ghosts removes those generated duplicates. Toggle Mesh Ghost Mode cycles the available mesh display modes. The main settings control past/future counts, frame step, opacity, fade, source selection, X-Ray and the interval/range modes.

Use onion skins to compare silhouettes, contacts and overlap. An object-origin marker cannot show how a bent arm or a deforming face changed; a mesh ghost can. More mesh samples require more evaluated geometry, so begin with a few past/future frames and a larger step.

Source options determine which meshes participate. Confirm that the intended character meshes are selected or otherwise included by that mode. Hidden or unrelated objects should not be treated as evidence of a target error until you have checked the source selection.

**Example: inspect a landing silhouette.**

1. Move to the landing frame and choose the intended character mesh sources.
2. Generate a small set of past and future onion skins.
3. Lower opacity and use different past/future colors so the current pose remains readable.
4. Inspect foot contact, torso compression and arm overlap.
5. Hide or clear the mesh ghosts after the comparison. They are generated display objects, not editable duplicate characters.

Skeleton View is another display aid, with a bone filter for choosing what is shown. It does not automatically change the rig's constraints, weights or control selection. Use it to simplify a view that would otherwise be obscured by mesh ghosts.

## 8. Visual Diff and reference staleness

Visual Diff pins the current pose as a comparison reference and colors bone differences between cool and warm according to distance. Diff Max Distance sets the scale at which the warm end is reached; it is not a movement limit. Cool/Warm colors change the overlay's presentation.

Use **Pin Diff Reference** at the pose you want to compare, then inspect another frame with the overlay enabled. **Unpin Diff Reference** clears that reference. A Visual Diff reference is separate from a retained snapshot with restorable curves.

The staleness guard compares the current target/anchor state with the pinned reference state. When it no longer matches, the overlay is marked stale rather than pretending the comparison is current. Inspect the target and repin deliberately. The Mode Label helps show such state.

**Example: compare a revised hand pose.**

1. At the reference frame, select the intended armature and pin the Diff reference.
2. Make or inspect a revised pose and enable Visual Diff.
3. Adjust Diff Max Distance to make the meaningful positional differences readable.
4. If the reference is marked stale, check the target and anchor changes before repinning.
5. Save a retained snapshot separately if you need complete curve restoration later.

## 9. Physics Suggest, ballistic preview and Physics Feel

Physics tools provide motion shapes and previews. They are not a general rigid-body simulation or collision solver.

**Physics Suggest (Preview)** computes a parabolic correction for generated markers. It uses the selected markers when available, otherwise the generated set. Choose Gravity Strength and Gravity Axis. Left-click or Enter confirms the preview; right-click or Escape discards it. Check the target segments before applying a suggestion.

Ballistic Preview displays a gravity-shaped guide using its own gravity and offset settings. An overlay is not automatically keyed animation. Physics Feel archetypes supply stylised motion shapes: Pendulum, Bounce, Settle, Wobble and Springback. Their available profiles and controls are listed in the settings reference.

**Stamp to Keys** writes the chosen archetype to the selected location axis of the active object's Action, or the active pose bone when applicable. An existing location curve for that axis is required. Active NLA strips are refused by the command. End must be greater than Start.

Stamping removes keys on that target channel **inside the inclusive Start/End range**, then writes one key per frame using the archetype displacement multiplied by Amplitude. Keys outside the range remain. The stamped values are the archetype values, not a guaranteed additive offset from the target's current position. Save a snapshot and inspect the curve before and after stamping.

**Example: create a controlled bounce study.**

1. Use a copied scene with one animated object and an existing location-Z curve.
2. Save a snapshot, choose Bounce, Z, a modest Amplitude and a short frame range.
3. Enable Archetype Preview and inspect the shape. Check that the range does not contain unrelated motion you want to keep.
4. Press Stamp to Keys. Inspect the densely keyed Z curve and the range boundaries.
5. Use Undo to compare. Adjust the range or amplitude and try again only after the result is understood.

For Physics Suggest, test cancellation before confirmation. For stamping, test Undo after completion. These are different recovery paths. Use a longer or different range only after the small study produces the expected result.

## 10. Draw to Keys from annotation strokes

Draw to Keys reads usable 3D-space annotation strokes from the active visible annotation layer/frame at the playhead. The longest usable stroke supplies the path. Other strokes are timing dashes; accepted crossings along the path become location keys. A dot or a non-3D-space stroke is not a valid path stroke.

The target is the active pose bone in Pose Mode, otherwise the active object. The dialog captures that target when it opens, so changing selection while it is open does not silently retarget the pending operation.

**Example: block a prop's path.**

1. Select the prop and draw one clear 3D annotation path in the intended view/placement mode.
2. Draw short dashes across that path at the positions that should become keyed beats.
3. Open Draw to Keys and verify its target. Choose location axes, Start at Playhead or an explicit Start, and Step.
4. With Start 1 and Step 4, accepted crossings create successive keys at 1, 5, 9 and so on. The dashes' spatial spacing controls the sampled positions; Step controls their time spacing.
5. Choose Constant, Linear, Bezier or Preferences interpolation. Adjust Tolerance only if valid crossings are being missed or unintended crossings are included.
6. Leave Clear Strokes off for the first attempt. Run the conversion and inspect the resulting location curves.
7. Enable Clear Strokes only when you intend to remove the usable strokes read by the command. Skipped strokes are retained.

Stroke Value optionally keys a custom property recording distance along the path. It is additional output, not a replacement for location keys. The command does not infer orientation, contacts or a complete character performance from the drawing.

## 11. Saved snapshots, variants and visibility

Save Snapshot records the chosen scope: active object/selected bones, selected path, selected marker channels or explicit scene scope. The current target label and scope are the selection contract. A scene-wide capture may include multiple objects; choose it deliberately.

A retained snapshot stores frozen samples and captured keyframe/handle data with the scene. It survives saving/reopening and addon disable/re-enable. Capture, variants, binding, visibility, deletion and restoration participate in native Undo/Redo.

Hide/Show controls the saved overlay and does not change the animation. **Save Variant** captures an independent alternate using the reference's scope and records its origin. It is not an empty child record that depends on its parent remaining present. Deleting the parent does not delete the variant.

The build retains at most ten snapshots. At capacity, delete unwanted records before saving another. It does not silently discard the oldest record to make space. Confirm the selected record before deleting it or deleting all snapshots.

**Example: compare two takes.**

1. Set the scope to the character controls you intend to revise and Save Snapshot with a readable name.
2. Edit the animation and Save Variant from the reference using another readable name.
3. Toggle the two saved overlays to compare their sampled motion against the live animation.
4. Keep the desired records and remove only the ones you no longer need.
5. Save/reopen a copied .blend and check that the records and bindings remain available.

## 12. Restore, explicit binding and JSON transfer

Restore checks the scene, object, Action, slot, bone and channel identity before writing. A replaced target must be deliberately bound. Shared Action slots are refused because modifying them would affect another object; make the animation single-user before using a restoration workflow that writes those curves.

Current snapshots restore their captured keyframes and handles. They do not promise to restore arbitrary Action modifiers or unrelated animation channels. Legacy sample-only snapshots restore sampled values where the existing curve can be reshaped; unsuitable segments are skipped. Bone renames can be followed by the saved binding logic.

**Bind to Active Target** binds one original object and its named bone channels to the active target. Multi-object imported references remain viewable and unbound rather than being collapsed onto one object. Inspect the recorded scope before binding.

After save/reopen, a channel deleted and re-keyed at the same identity is treated as the same channel. Within an active gesture, a replaced curve is not given rollback data intended for the original. This identity boundary matters when deliberately rebuilding Actions or channels between sessions.

**Example: restore a known original take.**

1. Save a .blend backup and choose the reference captured from the intended target.
2. Verify the object, Action/slot and bone/channel scope.
3. Restore and inspect the complete curves in the animation editor.
4. Check Undo/Redo and the reference overlay.
5. If restoration is refused, resolve its identity/shared-slot message. Do not bind a different target merely to bypass a warning.

Export Ghosts writes JSON for transferring tool/reference data. Import validates the payload and retained records, remaps identifier collisions consistently and rejects unsupported versions or capacity overflow without a partial merge. Import into unreadable existing saved records fails with existing data preserved.

JSON cannot prove the original object identity. Imported and legacy references can be viewed, but restoration requires explicit binding where identity is unavailable. A JSON file is not a .blend backup and does not carry the rig, mesh, audio, constraints or the whole scene.

**Example: transfer a comparison reference.**

1. Export from the source scene and save the original .blend separately.
2. Open the intended destination scene and import the JSON.
3. Inspect the imported overlays before binding anything.
4. Bind only a single-object reference to the deliberately selected matching target when restoration is intended.
5. For multi-object data, retain it as comparison data unless the supported binding workflow can establish its targets.

## 13. Live refresh, performance and Settings Editor

Live Bone Markers and Live Onion Skin control automatic updates of their respective displays. Throttle limits update frequency; a larger interval reduces how often expensive work runs. Freeze stops live refresh while you inspect a display. A frozen overlay can be useful, but it is not evidence that the live animation stayed unchanged.

Keep the visible time range, number of traced vertices, marker subdivision and onion-skin count modest. Increase them only when the extra detail helps the task. Clear unused generated geometry and hide unused paths rather than making every overlay visible throughout a shot.

**Settings Editor (Prototype)** captures a scene, object and path target. Its explicit target helps avoid editing a different object when the viewport selection changes. **Refresh Target** adopts the source viewport's current selection deliberately. **Return to Viewport** closes only that prototype window and retains the viewport selection.

Check the target label before changing settings in this editor. A missing or restricted target should explain its state. The editor is a convenience for persistent settings, not a replacement for the source viewport's context during a modal drag.

## 14. Troubleshooting and verification

**No markers:** select an animated object or pose bone, check keyed location channels, generation range, Ghost Tools activation and level visibility. A hidden level or range outside the keyed motion can make a valid generated set appear empty.

**Shift+G edits a path handle instead of a marker:** move away from visible handle ends or hide handles temporarily. Handle dragging gets a chance to handle the shared gesture first.

**A drag cannot begin:** finish/cancel the active gesture, confirm the target exists and check whether the pointer is within Grab Radius of an eligible marker or handle.

**Motion looks unchanged after an edit:** check Freeze and live-refresh switches, inspect the actual Action and selected channels, then refresh the display. Do not repeatedly key a different target to make an overlay move.

**Too much viewport clutter:** shorten the range, reduce subdivision and mesh count, hide frame labels, collapse path folders and disable unused overlays.

**Stamping is refused:** use a valid Start/End range, an active Action with the required location curve, and no conflicting active NLA strips. Stamping does not create every missing animation prerequisite.

**Draw to Keys finds no valid stroke:** check the active visible annotation layer/frame, 3D-space strokes, a path with at least two points and crossing dashes. A screen-space annotation is not automatically a 3D path.

**Restore is refused:** inspect the captured target, shared Action slot, Action assignment and binding. Imported data may need deliberate binding; a multi-object record is not a single-object restore shortcut.

**Visual Diff is stale:** check target/anchor changes and repin the intended reference. A stale diff is separate from a retained snapshot's restore readiness.

**Cycles cannot be added after an older Ghost edit:** 4.2.0 r4 removes old persistent Limits tags on load/enable. Save a copy, enable the current addon and inspect remaining modifiers. Current curve identity avoids leaving a modifier merely to tag a curve.

The exact original r4 candidate passed 320 checks across 17 suites on the recorded host. Publication cleanup removed one descriptive comment; executable AST and all other package entries were preserved. The current package checksum is in [the package receipt](afterimage-release/package-receipt-r4.json). Pointer feel, every custom rig and all other host builds are not established by those background checks. Final owner usability acceptance remains pending.

## 15. How to use the complete reference

The command reference below documents all source-defined operators, including navigation and lifecycle helpers. Its prerequisite messages are the messages present in that operator's polling logic. Some additional target restrictions are checked when the command runs; the workflow chapters explain the important ones.

The settings reference documents scene settings, path records, addon preferences, easing settings, saved binding records and command arguments. A stored binding identifier is not a normal artistic control. Defaults apply to newly created data; upgraded scenes can retain different values. The internal field identifier distinguishes similarly named controls such as the several Range, Color and Falloff fields.

## Reference A. Complete command reference

### Visual Diff

#### Pin Diff Reference

Pin the current frame as the Visual Diff reference. Bones will be colored warm/cool by their distance from this pose

Pin the current frame as the Visual Diff reference pose.

Captures world-space bone positions at the current frame and stores a
SHA-256 hash of the underlying keyframe data so the Staleness Guard can
detect post-pin edits.

**Command:** `ghost_tool.pin_diff_reference`. Declared as an undoable operation.

#### Unpin Diff Reference

Clear the pinned Diff Reference and hide the diff overlay

**Command:** `ghost_tool.unpin_diff_reference`. Declared as an undoable operation.

### Draw to Keys

#### Draw to Keys

Turn annotation strokes into location keys: the longest stroke is the path, every other stroke a timing
dash; each crossing becomes a key at Start, Start + Step, ... on the chosen axes

**Command:** `ghost_tool.paths_draw_to_keys`. Declared as an undoable operation.

**Prerequisite messages:** Select an object, or a bone in Pose mode. Draw a path and timing dashes with the Annotate tool (Surface or 3D Cursor).

- **Axes** (`axes`): Location axes to key New-data default: X, Y, Z. Choices: X: Key location X (`X`); Y: Key location Y (`Y`); Z: Key location Z (`Z`).

- **Start at Playhead** (`use_current_frame`): Start at the current frame instead of the Start field New-data default: On.

- **Start** (`start_frame`): Frame of the first crossing's key New-data default: 1.

- **Step** (`frame_step`): Frames between the keys of neighbouring crossings New-data default: 4. Allowed range: 1 to no explicit upper limit.

- **Interpolation** (`interpolation`): Interpolation of the new keys New-data default: Bezier. Choices: Constant: Hold each key until the next (`CONSTANT`); Linear: Straight lines between keys (`LINEAR`); Bezier: Smooth curves between keys (`BEZIER`); Preferences: Use the interpolation set in the preferences (`SCENE`).

- **Stroke Value** (`write_stroke_value`): Also key a stroke_value custom property with the distance along the path New-data default: Off.

- **Tolerance** (`crossing_tolerance`): How near a dash must come to the path, as a fraction of the path length New-data default: 0.02. Allowed range: 0.0001 to 0.5.

- **Clear Strokes** (`clear_annotations_after`): Remove the strokes after keying New-data default: Off.

### Easing

#### Apply Easing Preset

Apply an easing preset to the selected ghost range.

**Command:** `ghost_tool.apply_easing`. Declared as an undoable operation.

**Prerequisite messages:** Select an object with an animation action. Generate inbetween markers between two keys first.

- **Preset** (`preset`): Easing preset to apply New-data default: Ease In/Out. Choices: Ease In: Slow start, fast finish  -  acceleration from rest (`EASE_IN`); Ease Out: Fast start, slow finish  -  deceleration to rest (`EASE_OUT`); Ease In/Out: Slow at both ends  -  classic S-curve motion (`EASE_IN_OUT`); Linear: Constant speed  -  no easing (`LINEAR`); Overshoot: Slight overshoot past the target, then settle back (`OVERSHOOT`); Anticipate: Small reverse motion before the main movement (`ANTICIPATE`); Bounce: Simulated bouncing at the end of motion (`BOUNCE`); Custom: User-defined bezier tangent values (`CUSTOM`).

- **Left X** (`custom_left_x`): Outgoing handle time as a fraction of the key interval New-data default: 0.33. Allowed range: 0 to 1.

- **Left Y** (`custom_left_y`): Outgoing handle value as a fraction of the change between keys New-data default: . Allowed range: -2 to 2.

- **Right X** (`custom_right_x`): Incoming handle time offset as a fraction of the key interval New-data default: -0.33. Allowed range: -1 to 0.

- **Right Y** (`custom_right_y`): Incoming handle value offset as a fraction of the change between keys New-data default: . Allowed range: -2 to 2.

### JSON transfer

#### Export Ghosts

Export ghost configuration to a JSON file.

**Command:** `ghost_tool.export_ghosts`.

- **File Path** (`filepath`): Path for the export JSON file New-data default: //ghost_export.json.

#### Import Ghosts

Import ghost configuration from a JSON file.

**Command:** `ghost_tool.import_ghosts`. Declared as an undoable operation.

- **File Path** (`filepath`): Path to the ghost JSON file to import

- **Remap to Active Object** (`remap_to_active`): Remap imported ghosts to the currently active object New-data default: On.

### Scene initialization

#### Initialize Ghost Tool

Attach Ghost Tool settings to this scene

Initialize Ghost Tool on the current scene.

This operator attaches the GhostToolSceneSettings PropertyGroup
to bpy.types.Scene if it is missing.  It is shown as a button in
the Ghost Tool menu when the addon detects that `scene.ghost_tool` does
not exist  -  typically after a failed registration or a file that
was saved before the addon was installed.

**Command:** `ghost_tool.initialize`. Declared as an undoable operation.

### Mesh ghosts and onion skin

#### Generate Mesh Ghosts

Create transparent mesh duplicates at frames around the playhead to visualize the character pose at different times

**Command:** `ghost_tool.generate_mesh_ghosts`. Declared as an undoable operation.

**Prerequisite messages:** Select a character (its armature, mesh or curve) first.

#### Clear Mesh Ghosts

Remove all transparent mesh ghost duplicates from the scene

**Command:** `ghost_tool.clear_mesh_ghosts`. Declared as an undoable operation.

#### Toggle Mesh Ghost Mode

Cycle through mesh ghost display modes: Solid, Wireframe, Off

**Command:** `ghost_tool.toggle_mesh_mode`.

### Markers, selection and direct editing

#### Drag Ghost

Modal operator for dragging ghost markers in the 3D viewport.

When invoked, this operator finds the ghost nearest to the mouse cursor
and enters a modal loop.  The user drags the ghost in 3D space, with
optional axis constraints, and the f-curve is recalculated in real time.

Keybindings during modal:
    MOUSEMOVE  -  Update ghost position
    X/Y/Z  -  Activate single-axis constraint
    SHIFT+X/Y/Z  -  Activate plane constraint (perpendicular to that axis)
    LEFT MOUSE release  -  Confirm and push to undo
    RIGHT MOUSE or ESC  -  Cancel and restore original f-curve

**Command:** `ghost_tool.drag_ghost`. Declared as an undoable operation.

**Prerequisite messages:** Initialize Ghost Tool first. Turn on Ghost Tool first. Generate markers for an animated object first.

#### Generate Ghosts

Generate ghost markers for the active object and selected bones.

Samples f-curves at midpoints between keyframes and creates Ghost
objects for visualization and manipulation.

**Command:** `ghost_tool.generate_ghosts`. Declared as an undoable operation.

**Prerequisite messages:** Select an animated object or a bone in Pose mode. Add animation keys to the selected object first.

#### Clear All Ghosts

Remove all ghosts from the current scene.

Clears the ghost store, invalidates the cache, and optionally clears
any mesh ghost objects if they exist.

**Command:** `ghost_tool.clear_ghosts`. Declared as an undoable operation.

#### Pin/Unpin Ghost

Toggle pin state on the ghost nearest to the cursor.

**Command:** `ghost_tool.pin_ghost`. Declared as an undoable operation.

**Prerequisite messages:** Turn on Ghost Tool first.

#### Unpin All Ghosts

Unpin all pinned ghosts in the current scene.

Iterates through the ghost store and resets the is_pinned flag on all
ghosts that are currently pinned.

**Command:** `ghost_tool.unpin_all`. Declared as an undoable operation.

#### Ghost Hover Detect

Automatic hover helper started when markers are generated. Tracks the nearest marker for hover rings and frame labels and stops when display is disabled or cleared. Normally do not invoke it manually.

**Command:** `ghost_tool.hover_detect`.

#### Select Ghost

Select or toggle-select the ghost under the cursor.

Plain click: select one ghost (clear others).
Shift-click: toggle the ghost in/out of the multi-selection set.

**Command:** `ghost_tool.select_ghost`.

**Prerequisite messages:** Initialize Ghost Tool first. Turn on Ghost Tool first. Generate markers for an animated object first.

### Motion paths and folders

#### Add Path for Selected

Pin a motion path for each selected bone (Pose mode), vertex (Edit Mode, up to 50 per click) or object

**Command:** `ghost_tool.paths_add_selected`. Declared as an undoable operation.

**Prerequisite messages:** Select bones, objects or (in Edit Mode) vertices first.

#### Remove Path

Unpin this motion path; removing a folder moves its paths to the top level

**Command:** `ghost_tool.paths_remove`. Declared as an undoable operation.

- **Index** (`index`): Active row in the associated list; the interface updates this as you select a row. New-data default: -1.

#### Add Folder

Add a folder row to group motion paths; checked paths move into it

**Command:** `ghost_tool.paths_add_folder`. Declared as an undoable operation.

#### Open or Close Folder

Show or hide this folder's paths in the list

**Command:** `ghost_tool.paths_toggle_folder`. Declared as an undoable operation.

- **Index** (`index`): Active row in the associated list; the interface updates this as you select a row. New-data default: -1.

#### Apply to Checked

Copy the selected path's colours, thickness, dot size, in front and traced point to every checked path

**Command:** `ghost_tool.paths_apply_to_checked`. Declared as an undoable operation.

**Prerequisite messages:** Select a path in the list to copy from. Check the paths to copy to.

- **Include Range** (`include_range`): Also copy the selected path's own frame range New-data default: Off.

#### Checked Paths

Show, hide, remove, reset the range of, or move the checked rows

**Command:** `ghost_tool.paths_checked_action`. Declared as an undoable operation.

- **Action** (`action`): What to do with the checked rows New-data default: Show. Choices: Show: Show the checked rows (`SHOW`); Hide: Hide the checked rows (`HIDE`); Remove: Remove the checked rows; a removed folder's paths move to the top level (`REMOVE`); Reset Range: Checked paths follow the global range again (`RESET_RANGE`); Move to Folder: Move the checked paths into a folder, or to the top level (`MOVE`).

- **Folder** (`folder`): Key of the folder to move into; empty moves to the top level New-data default: empty.

#### Clear Paths

Unpin every motion path

**Command:** `ghost_tool.paths_clear`. Declared as an undoable operation.

#### Toggle Path

Show or hide one motion path, or all of them

**Command:** `ghost_tool.paths_toggle_visible`. Declared as an undoable operation.

- **Action** (`action`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: One. Choices: One (`ONE`); All on (`ALL_ON`); All off (`ALL_OFF`).

- **Index** (`index`): Active row in the associated list; the interface updates this as you select a row. New-data default: -1.

#### Path In Front

Draw one motion path, or all of them, in front of the scene or hidden behind geometry

**Command:** `ghost_tool.paths_toggle_front`. Declared as an undoable operation.

- **Action** (`action`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: One. Choices: One: Flip this path (`ONE`); All in front: Every path draws in front (`ALL_ON`); All behind: Every path hides behind geometry (`ALL_OFF`).

- **Index** (`index`): Active row in the associated list; the interface updates this as you select a row. New-data default: -1.

#### Path Settings

Change the colours, thickness, dot size, traced point and own frame range of this motion path

**Command:** `ghost_tool.paths_set_color`. Declared as an undoable operation.

- **Index** (`index`): Active row in the associated list; the interface updates this as you select a row. New-data default: -1.

- **Colour** (`color`): Colour of this path Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

- **Colour Before** (`color_before`): Colour of this path before the playhead (style Split) Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

- **Thickness** (`thickness`): Line width of this path in pixels New-data default: 2. Allowed range: 1 to 6.

- **Dot Size** (`dot_size`): Size of this path's key dots in pixels New-data default: 6. Allowed range: 1 to 12.

- **Trace** (`anchor`): Which point of the bone the path traces New-data default: Head. Choices: Head: Trace the bone head (`HEAD`); Tail: Trace the bone tail (`TAIL`).

- **Own Range** (`use_own_range`): Give this path its own frame range instead of the global one

- **Range** (`own_range_mode`): Which frames this path covers New-data default: Around Playhead. Choices: Around Playhead: Frames before and after the playhead (`AROUND_CURSOR`); Scene: The scene frame range (`SCENE`); Custom: This path's own start and end frames (`CUSTOM`).

- **Before** (`own_before`): Frames this path draws before the playhead New-data default: 12. Allowed range: 0 to 500.

- **After** (`own_after`): Frames this path draws after the playhead New-data default: 12. Allowed range: 0 to 500.

- **Every** (`own_step`): Sample every Nth frame along this path New-data default: 1. Allowed range: 1 to 24.

- **Start** (`own_start`): First frame of this path's custom range New-data default: 1.

- **End** (`own_end`): Last frame of this path's custom range New-data default: 250.

### Path handle editing

#### Drag Path Handle

Drag a Bezier handle shown on a motion path: the handle's value changes, its time and the key stay.
Alt toggles Aligned (the opposite handle turns with it); Esc or right-click restores.

**Command:** `ghost_tool.path_handle_drag`. Declared as an undoable operation.

- **Pick Handle** (`wait_for_click`): Click a visible handle after choosing this action from the header New-data default: Off. Hidden command/state field; set through the normal workflow rather than as a general preference.

### Physics preview and stamping

#### Physics Suggest (Preview)

Preview and apply parabolic arc correction to ghosts (physics suggestion).

Enters a modal preview state showing suggested positions as dashed overlay
markers. Confirm with LEFTMOUSE or ENTER to apply. Cancel with RIGHTMOUSE
or ESC to discard.

**Command:** `ghost_tool.physics_suggest`. Declared as an undoable operation.

**Prerequisite messages:** Initialize Ghost Tool first. Generate markers between animation keys first.

- **Gravity Strength** (`gravity_strength`): Gravity magnitude in scene units per second squared New-data default: 9.81. Allowed range: 0.0 to 100.0.

- **Gravity Axis** (`gravity_axis`): Axis along which gravity acts (negative direction) New-data default: Z. Choices: X: Gravity along -X (`X`); Y: Gravity along -Y (`Y`); Z: Gravity along -Z (`Z`).

#### Stamp to Keys

Replaces keys inside the inclusive Start/End range on the chosen location axis and writes one archetype value per frame, multiplied by Amplitude. Other keys on that channel outside the range remain. Requires an active Action and the existing target location curve; active NLA strips are refused. Values are written directly, not added to the old curve. Inspect the preview and save a reference before stamping.

**Command:** `ghost_tool.archetype_bake`. Declared as an undoable operation.

**Prerequisite messages:** Select an object with an animation action first.

### Box selection

#### Box Select Ghosts

Draw a selection rectangle to select multiple ghost markers.

Click and drag to draw a box. All ghosts whose screen-space positions
fall within the box are selected. Shift-drag extends the existing
selection. Plain drag replaces it.

Keybindings during modal:
    MOUSEMOVE  -  Update box corner
    LEFTMOUSE release  -  Confirm selection
    RIGHTMOUSE or ESC  -  Cancel

**Command:** `ghost_tool.box_select`.

**Prerequisite messages:** Initialize Ghost Tool first. Turn on Ghost Tool first. Generate markers for an animated object first.

### Settings Editor

#### Settings Editor (Prototype)

Open persistent settings for an explicitly captured scene, object and path

**Command:** `ghost_tool.open_settings_editor`.

**Prerequisite messages:** Open a 3D Viewport window first.

- **Section** (`section`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: Paths. Choices: Paths: Open this settings section (`paths`); Edit: Open this settings section (`edit`); Look: Open this settings section (`look`); Settings: Open this settings section (`settings`). Hidden command/state field; set through the normal workflow rather than as a general preference.

#### Refresh Target

Use the source viewport's current selection as the editor target

**Command:** `ghost_tool.refresh_editor_target`.

**Prerequisite messages:** Open the prototype settings editor first.

#### Return to Viewport

Close only this prototype window and retain the viewport selection

**Command:** `ghost_tool.return_from_editor`.

**Prerequisite messages:** Use Return from the prototype settings editor.

### Snapshots, variants and restoration

#### Take Snapshot

Save markers and complete curves for the chosen target in this blend file

**Command:** `ghost_tool.take_snapshot`. Declared as an undoable operation.

- **Name** (`snapshot_name`): Name for this snapshot New-data default: Snapshot.

#### Save Variant

Capture current motion with the same target scope and retain the chosen reference as its origin

**Command:** `ghost_tool.save_variant`. Declared as an undoable operation.

- **Parent Uid** (`parent_uid`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. Hidden command/state field; set through the normal workflow rather than as a general preference.

- **Name** (`snapshot_name`): Optional name; otherwise use the parent name New-data default: empty.

#### Bind to Active Target

Use the active object and matching bone channels as the explicit restore target for this reference

**Command:** `ghost_tool.bind_snapshot`. Declared as an undoable operation.

- **Snapshot Uid** (`snapshot_uid`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. Hidden command/state field; set through the normal workflow rather than as a general preference.

#### Restore Snapshot

Apply the snapshot's complete captured curves; legacy snapshots restore sampled values

**Command:** `ghost_tool.restore_snapshot`. Declared as an undoable operation.

- **Snapshot UID** (`snapshot_uid`): UID of the snapshot to restore

#### Toggle Snapshot Visibility

Toggle the visibility of a snapshot overlay.

**Command:** `ghost_tool.toggle_snapshot`. Declared as an undoable operation.

- **Snapshot UID** (`snapshot_uid`): Internal identifier of the snapshot whose visibility will change

#### Delete Snapshot

Delete this snapshot. Use Undo to restore it

**Command:** `ghost_tool.delete_snapshot`. Declared as an undoable operation.

- **Snapshot UID** (`snapshot_uid`): Internal identifier of the snapshot to delete

### Interface, help and windows

#### Ghost Tool Help

Show detailed help for this Ghost Tool section

**Command:** `ghost_tool.show_help_popup`. Internal helper, normally invoked by the interface rather than as an independent artist task.

- **Help Topic** (`topic`): Internal identifier of the Ghost Tool help topic to display New-data default: overview.

#### Open in Separate Window

Open a separate viewport window with Ghost Tool in its sidebar. It stays open while you work; move it anywhere, or to a second monitor

**Command:** `ghost_tool.open_window`.

**Prerequisite messages:** Open a 3D Viewport window first.

#### Ghost Tool  -  Floating Toolbar

Pop out the Ghost Tool layout as a floating panel under the mouse.

**Command:** `ghost_tool.floating_toolbar`.

## Reference B. Named easing profiles

### Ease In

Slow start, fast finish  -  acceleration from rest Profile identifier: `EASE_IN`.

Left outgoing handle offset: [0.42, 0.0]; right incoming handle offset: [-0.15, -1.0]. Offsets are fractions of the segment time/value span. Handle types: FREE / FREE.

### Ease Out

Fast start, slow finish  -  deceleration to rest Profile identifier: `EASE_OUT`.

Left outgoing handle offset: [0.15, 1.0]; right incoming handle offset: [-0.42, 0.0]. Offsets are fractions of the segment time/value span. Handle types: FREE / FREE.

### Ease In/Out

Slow at both ends  -  classic S-curve motion Profile identifier: `EASE_IN_OUT`.

Left outgoing handle offset: [0.42, 0.0]; right incoming handle offset: [-0.42, 0.0]. Offsets are fractions of the segment time/value span. Handle types: FREE / FREE.

### Linear

Constant speed  -  no easing Profile identifier: `LINEAR`.

Left outgoing handle offset: [0.33, 0.33]; right incoming handle offset: [-0.33, -0.33]. Offsets are fractions of the segment time/value span. Handle types: FREE / FREE.

### Overshoot

Slight overshoot past the target, then settle back Profile identifier: `OVERSHOOT`.

Left outgoing handle offset: [0.25, 1.0]; right incoming handle offset: [-0.25, 0.15]. Offsets are fractions of the segment time/value span. Handle types: FREE / FREE.

### Anticipate

Small reverse motion before the main movement Profile identifier: `ANTICIPATE`.

Left outgoing handle offset: [0.25, -0.15]; right incoming handle offset: [-0.25, -1.0]. Offsets are fractions of the segment time/value span. Handle types: FREE / FREE.

### Bounce

Simulated bouncing at the end of motion Profile identifier: `BOUNCE`.

Left outgoing handle offset: [0.15, 0.8]; right incoming handle offset: [-0.08, 0.1]. Offsets are fractions of the segment time/value span. Handle types: FREE / FREE.

### Custom

User-defined bezier tangent values Profile identifier: `CUSTOM`.

Left outgoing handle offset: [0.33, 0.0]; right incoming handle offset: [-0.33, 0.0]. Offsets are fractions of the segment time/value span. Handle types: FREE / FREE.

## Reference B2. Built-in help topics

### Ghost Tool Workflow

Generate markers, drag them with Shift+G, then refine the resulting animation curves.

Enable Ghost Tools, choose the marker range and subdivision level, and generate markers. Drag a marker to reshape motion, pin important markers, and use snapshots before larger edits.

**Help topic:** `overview`.

### Onion Skin

Show translucent mesh poses before and after the current frame.

Use onion skins to compare silhouette, spacing, and overlap. Reduce the range or opacity when the viewport becomes crowded.

**Help topic:** `onion_skin`.

### Motion Trails

Draw the path and timing spacing of animated motion through the viewport.

Arc lines reveal trajectory shape. Spacing ticks reveal acceleration: dense marks indicate slower movement and wider gaps indicate faster movement.

**Help topic:** `motion_trails`.

### Marker Placement

Choose which frames become editable ghost markers.

Set the frame range and subdivision level before generating. Higher subdivision produces more editable inbetweens but also creates a denser viewport.

**Help topic:** `marker_placement`.

### Marker Display

Control marker colors, size, labels, arcs, and mesh visualization.

Display settings change only viewport presentation; they do not alter animation data. Use simpler display modes when working with dense shots.

**Help topic:** `marker_display`.

### Marker Tools

Edit, select, pin, snapshot, ease, and apply physics-shaped motion.

Drag Marker is the main editing action. Choose what happens on confirmation, use falloff to affect neighbors, and take a snapshot before stamping Physics Feel keys.

**Help topic:** `marker_tools`.

### Export and Import

Export retained reference data to JSON for transfer. Import validates and merges retained records, handles identifier collisions and rejects invalid payloads without a partial merge. Imported data cannot establish original target identity; inspect overlays and bind deliberately when supported. JSON is not a .blend backup.

**Help topic:** `export_import`.

### Ghost Tool Settings

Adjust interaction, performance, and viewport behavior for the current scene.

Keep marker counts and display complexity modest for heavy rigs. Add-on-wide visual defaults and the extended-help switch live in the installed add-on preferences.

**Help topic:** `settings`.

### Saved Snapshots

Capture restorable Ghost Tool states before experimenting.

Restore a snapshot to return to its captured curve state, toggle its overlay for comparison, or delete snapshots that are no longer useful.

**Help topic:** `snapshots`.

### Motion Paths

Pin a path to any bone or object and watch it follow the playhead.

Add pins the selected bones (Pose mode) or objects. Follow adds a grey path for whatever is selected. Paths sample the bone itself, so they work with markers off; turn Markers on to drag keys along a path. A bone path traces its head or its tail: click H/T in the list to switch. The cube button hides a path behind geometry. Split colours a path differently before the playhead; Glow marks the path selected in the list. Range and style apply to all paths; a path can take its own range in its settings (the colour swatch). Folders and checkboxes organise the list; Apply to Checked copies the selected path's look. Handles shows each key's Bezier handles: Shift+G or click an end to drag it (Alt keeps the pair aligned). Draw to Keys turns Annotate strokes into location keys: the longest stroke is the path, each crossing dash a key.

**Help topic:** `motion_paths`.

## Reference C. Complete settings and saved-record reference

Controls are grouped by their owning settings or record. Use the command entries for command-only arguments. Record fields such as indices, names, identifiers and collections describe stored state and are usually managed by the interface. Numeric color/vector defaults are component values, not hex colors. An empty string means no text/target has been assigned yet.

### Individual paths and path folders

#### Object

Object this path follows; on a folder row, the folder's name

**Field:** `object_name`. **Owner:** Individual paths and path folders. **Data type:** String.

#### Folder

This row is a folder that groups paths, not a path New-data default: Off.

**Field:** `is_folder`. **Owner:** Individual paths and path folders. **Data type:** Bool.

#### Folder Key

Fixed identity of this folder row; its paths store it in Folder New-data default: empty.

**Field:** `folder_key`. **Owner:** Individual paths and path folders. **Data type:** String.

#### In Folder

Key of the folder this path is in; empty is the top level New-data default: empty.

**Field:** `folder`. **Owner:** Individual paths and path folders. **Data type:** String.

#### Collapsed

Hide this folder's paths in the list New-data default: Off.

**Field:** `collapsed`. **Owner:** Individual paths and path folders. **Data type:** Bool.

#### Checked

Include this row in Apply to Checked and the Checked menu actions New-data default: Off.

**Field:** `checked`. **Owner:** Individual paths and path folders. **Data type:** Bool.

#### Vertex

Mesh vertex this path follows; -1 follows the object origin or the bone New-data default: -1. Allowed range: -1 to no explicit upper limit.

**Field:** `vertex_index`. **Owner:** Individual paths and path folders. **Data type:** Int.

#### Bone

Bone this path follows; empty follows the object origin New-data default: empty.

**Field:** `bone_name`. **Owner:** Individual paths and path folders. **Data type:** String.

#### Visible

Draw this path New-data default: On.

**Field:** `visible`. **Owner:** Individual paths and path folders. **Data type:** Bool.

#### Color

Colour of this path New-data default: 0.96, 0.71, 0.0. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `color`. **Owner:** Individual paths and path folders. **Data type:** FloatVector.

#### Thickness

Line width of this path in pixels New-data default: 2. Allowed range: 1 to 6.

**Field:** `thickness`. **Owner:** Individual paths and path folders. **Data type:** Int.

#### Anchor

Which point of the bone the path traces New-data default: Head. Choices: Head: Bone head / object origin (`HEAD`); Tail: Bone tail (`TAIL`).

**Field:** `anchor`. **Owner:** Individual paths and path folders. **Data type:** Enum.

#### Colour Before

Colour of this path before the playhead when the style is Split Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `color_before`. **Owner:** Individual paths and path folders. **Data type:** FloatVector.

#### Dot Size

Size of this path's key dots in pixels New-data default: 6. Allowed range: 1 to 12.

**Field:** `dot_size`. **Owner:** Individual paths and path folders. **Data type:** Int.

#### In Front

Draw this path through the scene; off hides it behind geometry New-data default: On.

**Field:** `in_front`. **Owner:** Individual paths and path folders. **Data type:** Bool.

#### Own Range

Give this path its own frame range instead of the global one New-data default: Off.

**Field:** `use_own_range`. **Owner:** Individual paths and path folders. **Data type:** Bool.

#### Range

Which frames this path covers New-data default: Around Playhead. Choices: Around Playhead: Frames before and after the playhead (`AROUND_CURSOR`); Scene: The scene frame range (`SCENE`); Custom: This path's own start and end frames (`CUSTOM`).

**Field:** `own_range_mode`. **Owner:** Individual paths and path folders. **Data type:** Enum.

#### Before

Frames this path draws before the playhead New-data default: 12. Allowed range: 0 to 500.

**Field:** `own_before`. **Owner:** Individual paths and path folders. **Data type:** Int.

#### After

Frames this path draws after the playhead New-data default: 12. Allowed range: 0 to 500.

**Field:** `own_after`. **Owner:** Individual paths and path folders. **Data type:** Int.

#### Every

Sample every Nth frame along this path New-data default: 1. Allowed range: 1 to 24.

**Field:** `own_step`. **Owner:** Individual paths and path folders. **Data type:** Int.

#### Start

First frame of this path's custom range New-data default: 1.

**Field:** `own_start`. **Owner:** Individual paths and path folders. **Data type:** Int.

#### End

Last frame of this path's custom range New-data default: 250.

**Field:** `own_end`. **Owner:** Individual paths and path folders. **Data type:** Int.

### Scene display, editing and physics settings

#### Ghost Tools

Enable Ghost Tool visualization and controls in the viewport New-data default: On.

**Field:** `is_active`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Subdivision Level

Number of recursive subdivision passes (1 = midpoints only) New-data default: 1. Allowed range: 1 to 5.

**Field:** `subdivision_level`. **Owner:** Scene display, editing and physics settings. **Data type:** Int.

#### Show Level 1

Show ghosts from the first subdivision level (midpoints between keyframes) New-data default: On.

**Field:** `show_level_1`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Show Level 2

Show ghosts from the second subdivision level (midpoints of midpoints) New-data default: On.

**Field:** `show_level_2`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Show Level 3

Show ghosts from the third subdivision level New-data default: On.

**Field:** `show_level_3`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Show Level 4

Show ghosts from the fourth subdivision level New-data default: On.

**Field:** `show_level_4`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Show Level 5

Show ghosts from the fifth subdivision level (maximum depth) New-data default: On.

**Field:** `show_level_5`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Show Motion Arc

Draw a line connecting ghosts and keyframes New-data default: On.

**Field:** `show_motion_arc`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Show Spacing Ticks

Draw tick marks along the arc showing frame spacing New-data default: Off.

**Field:** `show_spacing_ticks`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Show Acceleration Markers

Display markers at points where velocity changes significantly. Green ticks indicate acceleration (speeding up), red ticks indicate deceleration (slowing down) New-data default: Off.

**Field:** `show_acceleration_markers`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Curve Shape Mode

How f-curve handles behave when a ghost is moved New-data default: Free. Choices: Free: Handles adjust freely to pass through new position (`FREE`); Locked: Handle angle is preserved, only length changes (`LOCKED`); Smooth: Handle influence is redistributed across the segment (`SMOOTH`).

**Field:** `curve_mode`. **Owner:** Scene display, editing and physics settings. **Data type:** Enum.

#### Grab Radius

Screen-space pixel radius for ghost picking New-data default: 20. Allowed range: 5 to 100.

**Field:** `grab_radius`. **Owner:** Scene display, editing and physics settings. **Data type:** Int.

#### Use Custom Range

Limit ghost generation to a custom frame range New-data default: Off.

**Field:** `use_custom_range`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Range Start

Start frame for ghost generation New-data default: 1.

**Field:** `custom_range_start`. **Owner:** Scene display, editing and physics settings. **Data type:** Int.

#### Range End

End frame for ghost generation New-data default: 250.

**Field:** `custom_range_end`. **Owner:** Scene display, editing and physics settings. **Data type:** Int.

#### Show Mesh Ghosts

Display transparent mesh duplicates at ghost frames (onion skinning) New-data default: Off.

**Field:** `show_mesh_ghosts`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Past Ghosts

Number of mesh ghosts to show before the current frame New-data default: 3. Allowed range: 0 to 16.

**Field:** `mesh_ghost_past_count`. **Owner:** Scene display, editing and physics settings. **Data type:** Int.

#### Future Ghosts

Number of mesh ghosts to show after the current frame New-data default: 3. Allowed range: 0 to 16.

**Field:** `mesh_ghost_future_count`. **Owner:** Scene display, editing and physics settings. **Data type:** Int.

#### Frame Step

Frame interval between mesh ghosts New-data default: 2. Allowed range: 1 to 24.

**Field:** `mesh_ghost_step`. **Owner:** Scene display, editing and physics settings. **Data type:** Int.

#### Mesh Ghost Mode

How mesh ghosts are displayed in the viewport New-data default: Solid. Choices: Solid: Semi-transparent shaded mesh (`SOLID`); Wireframe: Wireframe silhouette only (`WIRE`).

**Field:** `mesh_ghost_mode`. **Owner:** Scene display, editing and physics settings. **Data type:** Enum.

#### X-Ray

Draw onion skins in front of everything, so poses behind the character stay visible New-data default: Off.

**Field:** `mesh_ghost_xray`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Onion Skin Fade

How onion skins fade with distance from the current frame New-data default: Linear. Choices: Linear: Even fade across the range (`LINEAR`); Smooth: Gentle near the current frame and at the ends, faster in the middle (`SMOOTH`); Exponential: Fade quickly near the current frame, long faint tail (`EXPONENTIAL`); Constant: No fade: every onion skin at the same opacity (`CONSTANT`).

**Field:** `mesh_ghost_falloff`. **Owner:** Scene display, editing and physics settings. **Data type:** Enum.

#### Mesh Opacity

Maximum opacity for the closest mesh ghosts New-data default: 0.35. Allowed range: 0.05 to 0.8.

**Field:** `mesh_ghost_opacity`. **Owner:** Scene display, editing and physics settings. **Data type:** Float.

#### Mesh Frame Mode

How mesh ghost frames are selected New-data default: Frame Step. Choices: Frame Step: Mesh ghosts at every Nth frame around the playhead (`STEP`); Keyframes Only: Mesh ghosts only at keyframe positions (`KEYFRAMES`).

**Field:** `mesh_ghost_frame_mode`. **Owner:** Scene display, editing and physics settings. **Data type:** Enum.

#### Keyframe Interval

Set the stepped interval between ghost keyframes. Controls how many keyframes to skip between each ghost  -  e.g. 'Every 2nd' places a ghost at every other keyframe New-data default: Every. Choices: Every: Place a ghost at every keyframe (no skipping) (`1`); Every 2nd: Place a ghost at every 2nd keyframe (skip one between each) (`2`); Every 3rd: Place a ghost at every 3rd keyframe (skip two between each) (`3`); Every 5th: Place a ghost at every 5th keyframe (skip four between each) (`5`); Every 10th: Place a ghost at every 10th keyframe (skip nine between each) (`10`); Custom: Enter a custom interval number for keyframe stepping (`CUSTOM`).

**Field:** `mesh_ghost_keyframe_skip`. **Owner:** Scene display, editing and physics settings. **Data type:** Enum.

#### Custom Interval

Custom keyframe stepped interval  -  e.g. 4 means place a ghost at every 4th keyframe, skipping three in between New-data default: 4. Allowed range: 1 to 100.

**Field:** `mesh_ghost_keyframe_skip_custom`. **Owner:** Scene display, editing and physics settings. **Data type:** Int.

#### Past Mesh Color

Color tint for mesh ghosts before the current frame New-data default: 0.25, 0.55, 1.0. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `mesh_ghost_past_color`. **Owner:** Scene display, editing and physics settings. **Data type:** FloatVector.

#### Future Mesh Color

Color tint for mesh ghosts after the current frame New-data default: 1.0, 0.55, 0.15. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `mesh_ghost_future_color`. **Owner:** Scene display, editing and physics settings. **Data type:** FloatVector.

#### Show Past Meshes

Show mesh ghosts from before the current frame New-data default: On.

**Field:** `show_mesh_past`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Show Future Meshes

Show mesh ghosts from after the current frame New-data default: On.

**Field:** `show_mesh_future`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Onion Skin Sources

Objects the onion skins follow, pinned by Show Onion Skin (newline-separated names). Empty: follow the selection New-data default: empty. Hidden command/state field; set through the normal workflow rather than as a general preference.

**Field:** `mesh_ghost_sources`. **Owner:** Scene display, editing and physics settings. **Data type:** String.

#### Motion Paths

Collection of records managed by the corresponding list and its add/remove commands.

**Field:** `motion_paths`. **Owner:** Scene display, editing and physics settings. **Data type:** Collection.

#### Motion Paths Index

Active row in the associated list; the interface updates this as you select a row. New-data default: -1.

**Field:** `motion_paths_index`. **Owner:** Scene display, editing and physics settings. **Data type:** Int.

#### Motion Paths

Draw motion paths for the pinned bones and objects New-data default: Off.

**Field:** `paths_enabled`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Follow Selection

Also draw a grey path for whatever is selected right now New-data default: Off.

**Field:** `paths_follow_selection`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Markers on Paths

Generate draggable ghost markers on the pinned paths. Head paths show location keys; Tail paths also show rotation keys New-data default: Off.

**Field:** `paths_show_markers`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Key Dots

Mark keyframes on each path New-data default: On.

**Field:** `paths_show_key_dots`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Frame Numbers

Label each sampled frame New-data default: Off.

**Field:** `paths_show_frame_numbers`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Range

Which frames every motion path covers New-data default: Around Playhead. Choices: Around Playhead: Frames before and after the playhead (`AROUND_CURSOR`); Scene: The scene frame range (`SCENE`); Custom: The custom range from Settings (`CUSTOM`).

**Field:** `paths_range_mode`. **Owner:** Scene display, editing and physics settings. **Data type:** Enum.

#### Before

Frames drawn before the playhead New-data default: 12. Allowed range: 0 to 500.

**Field:** `paths_before`. **Owner:** Scene display, editing and physics settings. **Data type:** Int.

#### After

Frames drawn after the playhead New-data default: 12. Allowed range: 0 to 500.

**Field:** `paths_after`. **Owner:** Scene display, editing and physics settings. **Data type:** Int.

#### Every

Sample every Nth frame along the paths New-data default: 1. Allowed range: 1 to 24.

**Field:** `paths_step`. **Owner:** Scene display, editing and physics settings. **Data type:** Int.

#### Style

How the path line is coloured New-data default: Solid. Choices: Solid: One colour (`SOLID`); Speed: Blue slow, red fast (`SPEED`); Fade: Fade with distance from the playhead (`FADE`); Split: Each path's before-colour up to the playhead, its colour after it (`SPLIT`).

**Field:** `paths_style`. **Owner:** Scene display, editing and physics settings. **Data type:** Enum.

#### Glow

Draw a wide faint glow under the path selected in the list New-data default: On.

**Field:** `paths_active_glow`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Handles

Show the Bezier handles of each key's location curves at its key dot New-data default: Off.

**Field:** `paths_show_handles`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Ghost Mode

How ghost frames are selected New-data default: Frame Step. Choices: Subdivision: Recursive midpoint subdivision between keyframes (original mode) (`SUBDIVISION`); Frame Step: Ghost at every Nth frame (`FRAME_STEP`); Keyframes Only: Ghost only at keyframe positions (`KEYFRAMES_ONLY`).

**Field:** `ghost_mode`. **Owner:** Scene display, editing and physics settings. **Data type:** Enum.

#### Range Mode

Which frames to generate ghosts across New-data default: Around Cursor. Choices: Around Cursor: Show N ghosts before/after the current frame (`AROUND_CURSOR`); Full Timeline: Show ghosts across the entire action or scene range (`FULL_TIMELINE`); Between Keys: Only between adjacent keyframes (like subdivision) (`BETWEEN_KEYS`); Custom Range: User-specified start/end frame (`CUSTOM`).

**Field:** `ghost_range_mode`. **Owner:** Scene display, editing and physics settings. **Data type:** Enum.

#### Frame Step

Generate a ghost every N frames New-data default: 2. Allowed range: 1 to 24.

**Field:** `frame_step`. **Owner:** Scene display, editing and physics settings. **Data type:** Int.

#### Before

Number of ghost frames before the current frame (Around Cursor mode) New-data default: 8. Allowed range: 0 to 64.

**Field:** `ghosts_before`. **Owner:** Scene display, editing and physics settings. **Data type:** Int.

#### After

Number of ghost frames after the current frame (Around Cursor mode) New-data default: 8. Allowed range: 0 to 64.

**Field:** `ghosts_after`. **Owner:** Scene display, editing and physics settings. **Data type:** Int.

#### Color Mode

How ghosts are colored in the viewport New-data default: Past/Future. Choices: By Level: Color by subdivision level (original mode) (`LEVEL`); Past/Future: Blue for past frames, orange for future (`TIME`); Proximity Fade: Bright near cursor, fading with distance (`FADE`); Rainbow: Full spectrum spread across the frame range (`RAINBOW`); Key/Inbetween: Distinct colors for keyframe vs in-between ghosts (`KEY_INBETWEEN`).

**Field:** `ghost_color_mode`. **Owner:** Scene display, editing and physics settings. **Data type:** Enum.

#### Fade Factor

How quickly ghost opacity fades with distance from the current frame New-data default: 0.7. Allowed range: 0.0 to 1.0.

**Field:** `ghost_fade_factor`. **Owner:** Scene display, editing and physics settings. **Data type:** Float.

#### Past Color

Color for ghosts before the current frame (Past/Future mode) New-data default: 0.25, 0.55, 1.0. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `ghost_past_color`. **Owner:** Scene display, editing and physics settings. **Data type:** FloatVector.

#### Future Color

Color for ghosts after the current frame (Past/Future mode) New-data default: 1.0, 0.55, 0.15. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `ghost_future_color`. **Owner:** Scene display, editing and physics settings. **Data type:** FloatVector.

#### Key Color

Color for ghosts at keyframe positions (Key/Inbetween mode) New-data default: 1.0, 0.85, 0.0. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `ghost_key_color`. **Owner:** Scene display, editing and physics settings. **Data type:** FloatVector.

#### Inbetween Color

Color for ghosts between keyframes (Key/Inbetween mode) New-data default: 0.4, 0.75, 1.0. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `ghost_inbetween_color`. **Owner:** Scene display, editing and physics settings. **Data type:** FloatVector.

#### Label Color

Color for frame number labels displayed next to ghosts New-data default: 0.9, 0.9, 0.9. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `ghost_label_color`. **Owner:** Scene display, editing and physics settings. **Data type:** FloatVector.

#### Min Alpha

Minimum opacity for the most distant ghosts. Higher values keep far ghosts more visible New-data default: 0.15. Allowed range: 0.0 to 0.5.

**Field:** `ghost_min_alpha`. **Owner:** Scene display, editing and physics settings. **Data type:** Float.

#### Falloff Curve

How ghost opacity falls off with distance from the current frame New-data default: Linear. Choices: Linear: Straight-line fade  -  even reduction across the range (`LINEAR`); Smooth: Ease-in-out fade  -  gentle start and end, faster middle (`SMOOTH`); Exponential: Quick fade near cursor, slow tail  -  emphasis on close ghosts (`EXPONENTIAL`); Constant: No fade  -  all ghosts at full opacity (`CONSTANT`).

**Field:** `ghost_falloff_curve`. **Owner:** Scene display, editing and physics settings. **Data type:** Enum.

#### Ghost Outline

Add a solid outline (Solidify modifier) to mesh ghosts for silhouette clarity New-data default: Off.

**Field:** `ghost_outline_enabled`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Outline Width

Thickness of the mesh ghost outline in scene units New-data default: 0.002. Allowed range: 0.0005 to 0.05.

**Field:** `ghost_outline_width`. **Owner:** Scene display, editing and physics settings. **Data type:** Float.

#### Outline Color

Color of the mesh ghost outline edges New-data default: 0.0, 0.0, 0.0. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `ghost_outline_color`. **Owner:** Scene display, editing and physics settings. **Data type:** FloatVector.

#### Ballistic Preview

Show a physics-informed arc preview of where ghosts would land under gravity New-data default: Off.

**Field:** `show_ballistic_preview`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Ballistic Offset

Manual offset applied to ballistic preview positions (scene units) New-data default: 0.0, 0.0, 0.0. Components: 3.

**Field:** `ballistic_offset`. **Owner:** Scene display, editing and physics settings. **Data type:** FloatVector.

#### Ballistic Gravity

Gravity strength for ballistic preview (m/s²) New-data default: 9.81. Allowed range: 0.0 to 100.0.

**Field:** `ballistic_gravity`. **Owner:** Scene display, editing and physics settings. **Data type:** Float.

#### Gravity Axis

Axis along which gravity acts for ballistic preview New-data default: Z. Choices: X: Gravity along -X (`X`); Y: Gravity along -Y (`Y`); Z: Gravity along -Z (`Z`).

**Field:** `ballistic_gravity_axis`. **Owner:** Scene display, editing and physics settings. **Data type:** Enum.

#### Archetype Preview

Show a physics-feel displacement overlay for the selected archetype.  Non-destructive  -  stamp to keyframes separately New-data default: Off.

**Field:** `show_archetype_preview`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Archetype

Physics-feel curve shape to preview and stamp New-data default: Bounce. Choices: Pendulum: Damped swing  -  oscillates out from rest and settles back (`PENDULUM`); Bounce: Impact arcs  -  decaying parabolic bounces toward the floor (`BOUNCE`); Settle: Exponential approach  -  accelerates toward target and arrives (`SETTLE`); Wobble: Decaying ring  -  symmetric oscillation fading to rest after impulse (`WOBBLE`); Springback: Overshoot cubic  -  snaps past target, returns toward rest (`SPRINGBACK`).

**Field:** `archetype_active`. **Owner:** Scene display, editing and physics settings. **Data type:** Enum.

#### Amplitude

Peak displacement applied by the archetype (scene units) New-data default: 1.0. Allowed range: 0.001 to 100.0.

**Field:** `archetype_amplitude`. **Owner:** Scene display, editing and physics settings. **Data type:** Float.

#### Axis

World-space axis along which the archetype displacement is applied New-data default: Z. Choices: X: Apply displacement along the X axis (`X`); Y: Apply displacement along the Y axis (`Y`); Z: Apply displacement along the Z axis (`Z`).

**Field:** `archetype_axis`. **Owner:** Scene display, editing and physics settings. **Data type:** Enum.

#### Start Frame

First frame of the archetype bake range New-data default: 1. Allowed range: 0 to no explicit upper limit.

**Field:** `archetype_start_frame`. **Owner:** Scene display, editing and physics settings. **Data type:** Int.

#### End Frame

Last frame (inclusive) of the archetype bake range New-data default: 24. Allowed range: 1 to no explicit upper limit.

**Field:** `archetype_end_frame`. **Owner:** Scene display, editing and physics settings. **Data type:** Int.

#### Show Arc Lines

Draw continuous trajectory lines through ghost positions across the timeline New-data default: On.

**Field:** `show_arc_lines`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Arc Style

Visual style for the trajectory arc lines New-data default: Speed Colored. Choices: Solid: Solid colored line (`SOLID`); Speed Colored: Blue where slow, red where fast (`SPEED`); Fade: Line fades with distance from the cursor (`FADE`).

**Field:** `arc_line_style`. **Owner:** Scene display, editing and physics settings. **Data type:** Enum.

#### Show Frame Numbers

Display frame numbers next to each ghost marker New-data default: Off.

**Field:** `show_frame_numbers`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Live Bone Markers

Live Mode: bone markers follow the playhead as you scrub. Turn off for Snapshot Mode  -  markers stay frozen at the frame where they were generated New-data default: On.

**Field:** `live_point_ghosts`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Live Onion Skin

Live Mode: onion skin meshes follow the playhead as you scrub. Turn off for Snapshot Mode  -  meshes stay frozen at the frame where they were generated New-data default: On.

**Field:** `live_mesh_ghosts`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Throttle (ms)

Minimum milliseconds between live updates. Lower = more responsive but heavier on CPU. 50ms ≈ 20 updates/sec, 100ms ≈ 10 updates/sec New-data default: 50. Allowed range: 16 to 500.

**Field:** `live_throttle_ms`. **Owner:** Scene display, editing and physics settings. **Data type:** Int.

#### Freeze

Temporarily pause all live ghost updates without disabling the feature. Useful during playback scrubbing or heavy scene operations New-data default: Off.

**Field:** `live_freeze`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Editing Mode

What happens when you confirm a ghost drag New-data default: Reshape Handles. Choices: Reshape Handles: Adjust bezier handles to hit the target position  -  non-destructive, no new keyframes (`RESHAPE`); Insert Keyframe: Insert a real keyframe at the ghost position  -  the ghost becomes a key (`INSERT_KEY`).

**Field:** `editing_mode`. **Owner:** Scene display, editing and physics settings. **Data type:** Enum.

#### Smooth Neighbors on Commit

After inserting a keyframe from a ghost drag (INSERT_KEY mode), smooth the handles of the two adjacent keyframes for a cleaner curve transition through the new key New-data default: Off.

**Field:** `smooth_neighbors_on_commit`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Show Keyframe Markers

Render keyframe positions on the trail with a distinct visual style (larger, different color) so they stand out from ghost in-betweens New-data default: On.

**Field:** `show_keyframe_markers`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Keyframe Marker Color

Color for keyframe position markers on the motion trail New-data default: 1.0, 0.85, 0.0, 0.9. Allowed range: 0.0 to 1.0. Components: 4. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `keyframe_marker_color`. **Owner:** Scene display, editing and physics settings. **Data type:** FloatVector.

#### Show Key Bookends

Always show keyframe markers at the two keyframes immediately before and after the ghost range, even if those frames are outside the configured range. Helps maintain context. New-data default: On.

**Field:** `show_key_bookends`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Key Bookend Color

Color for bookend keyframe markers outside the ghost range New-data default: 0.8, 0.8, 0.8, 0.5. Allowed range: 0.0 to 1.0. Components: 4. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `key_bookend_color`. **Owner:** Scene display, editing and physics settings. **Data type:** FloatVector.

#### Show Frame Label on Hover

Display the frame number when hovering over a ghost marker New-data default: On.

**Field:** `show_hover_frame_label`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Hover Highlight Color

Color of the highlight ring shown when hovering over a ghost New-data default: 0.8, 0.9, 1.0, 0.9. Allowed range: 0.0 to 1.0. Components: 4. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `hover_highlight_color`. **Owner:** Scene display, editing and physics settings. **Data type:** FloatVector.

#### Falloff Radius

Number of frames around the dragged ghost that are affected. 0 means only the dragged ghost moves (single-ghost mode). Higher values create smoother sculpted adjustments New-data default: . Allowed range: 0 to 20.

**Field:** `sculpt_falloff_radius`. **Owner:** Scene display, editing and physics settings. **Data type:** Int.

#### Falloff Curve

Shape of the falloff curve applied to neighboring ghosts New-data default: Smooth. Choices: Linear: Linear falloff from center to edge (`LINEAR`); Smooth: Smooth (cosine) falloff  -  natural feel (`SMOOTH`); Sharp: Sharp falloff  -  strong center, fast drop (`SHARP`).

**Field:** `sculpt_falloff_curve`. **Owner:** Scene display, editing and physics settings. **Data type:** Enum.

#### Visual Diff Mode

Show a per-bone warm/cool overlay comparing the current pose against a pinned reference frame.  Pin a frame with the 'Pin Diff Reference' operator New-data default: Off.

**Field:** `show_diff_overlay`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Diff Reference Frame

Frame number pinned as the Visual Diff reference pose New-data default: . Allowed range: 0 to no explicit upper limit.

**Field:** `diff_anchor_frame`. **Owner:** Scene display, editing and physics settings. **Data type:** Int.

#### Diff Cool Color

Color for bones that have moved less than average (cool end of diff spectrum) New-data default: 0.2, 0.4, 1.0, 0.75. Allowed range: 0.0 to 1.0. Components: 4. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `diff_cool_color`. **Owner:** Scene display, editing and physics settings. **Data type:** FloatVector.

#### Diff Warm Color

Color for bones that have moved more than average (warm end of diff spectrum) New-data default: 1.0, 0.25, 0.05, 0.75. Allowed range: 0.0 to 1.0. Components: 4. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `diff_warm_color`. **Owner:** Scene display, editing and physics settings. **Data type:** FloatVector.

#### Diff Max Distance

World-space distance considered 100% movement for diff coloring. Bones moving further than this value are fully warm New-data default: 0.5. Allowed range: 0.001 to 10.0.

**Field:** `diff_max_distance`. **Owner:** Scene display, editing and physics settings. **Data type:** Float.

#### Show Mode Label

Display a persistent HUD label in the viewport showing the active ghost mode (Live, Snapshot, Diff, or Bake in Progress) New-data default: On.

**Field:** `show_mode_label`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Skeleton View

Collapse the motion arc to root and spine bones only. Reduces visual clutter on dense rigs by showing a simplified skeleton trail New-data default: Off.

**Field:** `show_skeleton_view`. **Owner:** Scene display, editing and physics settings. **Data type:** Bool.

#### Skeleton Bone Filter

Comma-separated list of bone name substrings to include in Skeleton View. Leave empty to use the built-in root/spine heuristic New-data default: empty.

**Field:** `skeleton_view_bone_filter`. **Owner:** Scene display, editing and physics settings. **Data type:** String.

### Addon preferences

#### Show Extended Help Popups

Show Ghost Tool question-mark buttons that open detailed help popups; native Bforartists hover tooltips are unaffected New-data default: On.

**Field:** `show_extended_help`. **Owner:** Addon preferences. **Data type:** Bool.

#### Ghost Radius

World-space radius of ghost marker circles New-data default: 0.05. Allowed range: 0.005 to 1.0.

**Field:** `ghost_radius`. **Owner:** Addon preferences. **Data type:** Float.

#### Ghost Opacity

Overall opacity of ghost markers New-data default: 0.85. Allowed range: 0.1 to 1.0.

**Field:** `ghost_opacity`. **Owner:** Addon preferences. **Data type:** Float.

#### Level 1 Color

Color for first-generation ghosts New-data default: 0.2, 0.7, 1.0. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `level_1_color`. **Owner:** Addon preferences. **Data type:** FloatVector.

#### Level 2 Color

Color for second-generation ghosts New-data default: 0.3, 1.0, 0.5. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `level_2_color`. **Owner:** Addon preferences. **Data type:** FloatVector.

#### Level 3 Color

Color for third-generation ghosts New-data default: 1.0, 0.8, 0.2. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `level_3_color`. **Owner:** Addon preferences. **Data type:** FloatVector.

#### Level 4 Color

Color for fourth-generation ghosts New-data default: 1.0, 0.4, 0.2. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `level_4_color`. **Owner:** Addon preferences. **Data type:** FloatVector.

#### Level 5 Color

Color for fifth-generation ghosts New-data default: 0.9, 0.2, 0.8. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `level_5_color`. **Owner:** Addon preferences. **Data type:** FloatVector.

#### Past Ghost Color

Default color for ghosts before the current frame New-data default: 0.25, 0.55, 1.0. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `past_ghost_color`. **Owner:** Addon preferences. **Data type:** FloatVector.

#### Future Ghost Color

Default color for ghosts after the current frame New-data default: 1.0, 0.55, 0.15. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `future_ghost_color`. **Owner:** Addon preferences. **Data type:** FloatVector.

#### Key Ghost Color

Default color for ghosts at keyframe positions New-data default: 1.0, 0.85, 0.0. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `key_ghost_color`. **Owner:** Addon preferences. **Data type:** FloatVector.

#### Inbetween Ghost Color

Default color for ghosts between keyframes New-data default: 0.4, 0.75, 1.0. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `inbetween_ghost_color`. **Owner:** Addon preferences. **Data type:** FloatVector.

#### Outline Color

Default color for mesh ghost outlines New-data default: 0.0, 0.0, 0.0. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `outline_color`. **Owner:** Addon preferences. **Data type:** FloatVector.

#### Outline Width

Default width for mesh ghost outlines New-data default: 0.002. Allowed range: 0.0005 to 0.05.

**Field:** `outline_width`. **Owner:** Addon preferences. **Data type:** Float.

#### Arc Color

Color of the motion arc line New-data default: 0.5, 0.5, 0.5. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `arc_color`. **Owner:** Addon preferences. **Data type:** FloatVector.

#### Arc Line Width

Width of the motion arc line in pixels New-data default: 2.0. Allowed range: 1.0 to 10.0.

**Field:** `arc_line_width`. **Owner:** Addon preferences. **Data type:** Float.

#### Tick Cool Color

Color for slow-motion spacing ticks (dense frames) New-data default: 0.2, 0.4, 1.0. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `tick_cool_color`. **Owner:** Addon preferences. **Data type:** FloatVector.

#### Tick Warm Color

Color for fast-motion spacing ticks (sparse frames) New-data default: 1.0, 0.3, 0.1. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `tick_warm_color`. **Owner:** Addon preferences. **Data type:** FloatVector.

#### Default Subdivision Level

Default number of subdivision passes for new ghost generation New-data default: 1. Allowed range: 1 to 5.

**Field:** `default_subdivision_level`. **Owner:** Addon preferences. **Data type:** Int.

#### Grab Radius

Screen-space pixel radius for ghost picking New-data default: 20. Allowed range: 5 to 100.

**Field:** `grab_radius`. **Owner:** Addon preferences. **Data type:** Int.

#### Default Curve Mode

Default curve shape preservation mode for ghost dragging New-data default: Free. Choices: Free: Handles adjust freely (`FREE`); Locked: Handle angle preserved (`LOCKED`); Smooth: Handles redistributed evenly (`SMOOTH`).

**Field:** `default_curve_mode`. **Owner:** Addon preferences. **Data type:** Enum.

### Saved target-binding fields

#### Source Scene

Assigned data owner or settings record. Choose or initialise it through the matching workflow.

**Field:** `source_scene`. **Owner:** Saved target-binding fields. **Data type:** Pointer.

#### Source Object

Assigned data owner or settings record. Choose or initialise it through the matching workflow.

**Field:** `source_object`. **Owner:** Saved target-binding fields. **Data type:** Pointer.

#### Source Action

Assigned data owner or settings record. Choose or initialise it through the matching workflow.

**Field:** `source_action`. **Owner:** Saved target-binding fields. **Data type:** Pointer.

#### Scene Anchor

Assigned data owner or settings record. Choose or initialise it through the matching workflow.

**Field:** `scene_anchor`. **Owner:** Saved target-binding fields. **Data type:** Pointer.

#### Slot

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls.

**Field:** `slot`. **Owner:** Saved target-binding fields. **Data type:** Int.

#### Bone Uid

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls.

**Field:** `bone_uid`. **Owner:** Saved target-binding fields. **Data type:** String.

#### Bone Name

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls.

**Field:** `bone_name`. **Owner:** Saved target-binding fields. **Data type:** String.

#### Channel

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls.

**Field:** `channel`. **Owner:** Saved target-binding fields. **Data type:** String.

#### Curve Uid

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls.

**Field:** `curve_uid`. **Owner:** Saved target-binding fields. **Data type:** String.

#### Path Uid

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls.

**Field:** `path_uid`. **Owner:** Saved target-binding fields. **Data type:** String.

### Retained snapshot records

#### Uid

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls.

**Field:** `uid`. **Owner:** Retained snapshot records. **Data type:** String.

#### Schema Version

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: 2.

**Field:** `schema_version`. **Owner:** Retained snapshot records. **Data type:** Int.

#### Payload

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls.

**Field:** `payload`. **Owner:** Retained snapshot records. **Data type:** String.

#### Bindings

Collection of records managed by the corresponding list and its add/remove commands.

**Field:** `bindings`. **Owner:** Retained snapshot records. **Data type:** Collection.

### Easing controls

#### Easing Preset

Select an easing curve feel to apply between keyframes New-data default: Ease In/Out. Choices: Ease In: Slow start, fast finish  -  acceleration from rest (`EASE_IN`); Ease Out: Fast start, slow finish  -  deceleration to rest (`EASE_OUT`); Ease In/Out: Slow at both ends  -  classic S-curve motion (`EASE_IN_OUT`); Linear: Constant speed  -  no easing (`LINEAR`); Overshoot: Slight overshoot past the target, then settle back (`OVERSHOOT`); Anticipate: Small reverse motion before the main movement (`ANTICIPATE`); Bounce: Simulated bouncing at the end of motion (`BOUNCE`); Custom: User-defined bezier tangent values (`CUSTOM`).

**Field:** `active_preset`. **Owner:** Easing controls. **Data type:** Enum.

#### Left Handle X

Horizontal position of the left keyframe's outgoing handle (0 = at keyframe, 1 = at next keyframe) New-data default: 0.33. Allowed range: 0.0 to 1.0.

**Field:** `custom_left_x`. **Owner:** Easing controls. **Data type:** Float.

#### Left Handle Y

Vertical position of the left keyframe's outgoing handle (0 = flat, positive = overshoot) New-data default: . Allowed range: -2.0 to 2.0.

**Field:** `custom_left_y`. **Owner:** Easing controls. **Data type:** Float.

#### Right Handle X

Horizontal position of the right keyframe's incoming handle (0 = at keyframe, -1 = at previous keyframe) New-data default: -0.33. Allowed range: -1.0 to 0.0.

**Field:** `custom_right_x`. **Owner:** Easing controls. **Data type:** Float.

#### Right Handle Y

Vertical position of the right keyframe's incoming handle (0 = flat, positive = overshoot) New-data default: . Allowed range: -2.0 to 2.0.

**Field:** `custom_right_y`. **Owner:** Easing controls. **Data type:** Float.

## Reference D. Command lookup index

The identifiers below link labels to the exact source-defined commands. Search the PDF for an identifier or label to locate its detailed reference. Internal and automatic helpers are identified in their entries.

- `ghost_tool.apply_easing` - Apply Easing Preset

- `ghost_tool.archetype_bake` - Stamp to Keys

- `ghost_tool.bind_snapshot` - Bind to Active Target

- `ghost_tool.box_select` - Box Select Ghosts

- `ghost_tool.clear_ghosts` - Clear All Ghosts

- `ghost_tool.clear_mesh_ghosts` - Clear Mesh Ghosts

- `ghost_tool.delete_snapshot` - Delete Snapshot

- `ghost_tool.drag_ghost` - Drag Ghost

- `ghost_tool.export_ghosts` - Export Ghosts

- `ghost_tool.floating_toolbar` - Ghost Tool  -  Floating Toolbar

- `ghost_tool.generate_ghosts` - Generate Ghosts

- `ghost_tool.generate_mesh_ghosts` - Generate Mesh Ghosts

- `ghost_tool.hover_detect` - Ghost Hover Detect

- `ghost_tool.import_ghosts` - Import Ghosts

- `ghost_tool.initialize` - Initialize Ghost Tool

- `ghost_tool.open_settings_editor` - Settings Editor (Prototype)

- `ghost_tool.open_window` - Open in Separate Window

- `ghost_tool.path_handle_drag` - Drag Path Handle

- `ghost_tool.paths_add_folder` - Add Folder

- `ghost_tool.paths_add_selected` - Add Path for Selected

- `ghost_tool.paths_apply_to_checked` - Apply to Checked

- `ghost_tool.paths_checked_action` - Checked Paths

- `ghost_tool.paths_clear` - Clear Paths

- `ghost_tool.paths_draw_to_keys` - Draw to Keys

- `ghost_tool.paths_remove` - Remove Path

- `ghost_tool.paths_set_color` - Path Settings

- `ghost_tool.paths_toggle_folder` - Open or Close Folder

- `ghost_tool.paths_toggle_front` - Path In Front

- `ghost_tool.paths_toggle_visible` - Toggle Path

- `ghost_tool.physics_suggest` - Physics Suggest (Preview)

- `ghost_tool.pin_diff_reference` - Pin Diff Reference

- `ghost_tool.pin_ghost` - Pin/Unpin Ghost

- `ghost_tool.refresh_editor_target` - Refresh Target

- `ghost_tool.restore_snapshot` - Restore Snapshot

- `ghost_tool.return_from_editor` - Return to Viewport

- `ghost_tool.save_variant` - Save Variant

- `ghost_tool.select_ghost` - Select Ghost

- `ghost_tool.show_help_popup` - Ghost Tool Help

- `ghost_tool.take_snapshot` - Take Snapshot

- `ghost_tool.toggle_mesh_mode` - Toggle Mesh Ghost Mode

- `ghost_tool.toggle_snapshot` - Toggle Snapshot Visibility

- `ghost_tool.unpin_all` - Unpin All Ghosts

- `ghost_tool.unpin_diff_reference` - Unpin Diff Reference
