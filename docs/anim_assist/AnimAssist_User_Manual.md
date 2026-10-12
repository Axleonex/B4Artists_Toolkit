# Anim Assist 12.1.3 - complete user manual

Published release: **12.1.3**. This manual describes the code shipped in `b4_anim_assist_v12.1.3.zip`, including the current editor layout, every source-defined command, every help topic, and the settings used by those commands.

Use the workflow chapters to learn a task. Use the feature reference to understand individual tools. The command identifiers beside reference entries distinguish tools with similar names and help when reporting a problem. Settings marked as stored state or command arguments are not necessarily editable buttons in the interface.

## Contents

- [1. Installation, upgrade and first run](#1-installation-upgrade-and-first-run) (PDF page 2)
- [2. Navigation, scope and shortcuts](#2-navigation-scope-and-shortcuts) (PDF page 2)
- [3. Keys, channels and cleanup workflow](#3-keys-channels-and-cleanup-workflow) (PDF page 3)
- [4. Curves, breakdowns and in-betweens](#4-curves-breakdowns-and-in-betweens) (PDF page 4)
- [5. Transform offsets, space, pivots and falloff](#5-transform-offsets-space-pivots-and-falloff) (PDF page 4)
- [6. Trajectory, arcs and spacing diagnostics](#6-trajectory-arcs-and-spacing-diagnostics) (PDF page 5)
- [7. Retiming, ripple, gaps and time warp](#7-retiming-ripple-gaps-and-time-warp) (PDF page 5)
- [8. Temporary controls, proxies, locators and baking](#8-temporary-controls-proxies-locators-and-baking) (PDF page 5)
- [9. Matching, rig detection and space switching](#9-matching-rig-detection-and-space-switching) (PDF page 6)
- [10. Mirroring and left/right pair management](#10-mirroring-and-leftright-pair-management) (PDF page 6)
- [11. Quick Shelf, search, Recents, macros and batches](#11-quick-shelf-search-recents-macros-and-batches) (PDF page 7)
- [12. Animation layers](#12-animation-layers) (PDF page 7)
- [13. Lipsync: audio, bones, shape keys and live/baked modes](#13-lipsync-audio-bones-shape-keys-and-livebaked-modes) (PDF page 8)
- [14. Troubleshooting, recovery and maintenance](#14-troubleshooting-recovery-and-maintenance) (PDF page 9)
- [15. How to use the complete reference](#15-how-to-use-the-complete-reference) (PDF page 9)
- [Reference A1. General settings, diagnostics and core tools](#reference-a1-general-settings-diagnostics-and-core-tools) (PDF page 10)
- [Reference A2. Keys, channels and metadata](#reference-a2-keys-channels-and-metadata) (PDF page 13)
- [Reference A3. Breakdowns, in-betweens and pose comparison](#reference-a3-breakdowns-in-betweens-and-pose-comparison) (PDF page 21)
- [Reference A4. Offsets and transforms](#reference-a4-offsets-and-transforms) (PDF page 28)
- [Reference A5. Trajectory and spacing](#reference-a5-trajectory-and-spacing) (PDF page 33)
- [Reference A6. Retiming and timing diagnostics](#reference-a6-retiming-and-timing-diagnostics) (PDF page 38)
- [Reference A7. Temporary controls, proxies and baking](#reference-a7-temporary-controls-proxies-and-baking) (PDF page 46)
- [Reference A8. Matching and space switching](#reference-a8-matching-and-space-switching) (PDF page 52)
- [Reference A9. Mirroring and pair management](#reference-a9-mirroring-and-pair-management) (PDF page 60)
- [Reference A10. Shelf, macros, batches and recovery](#reference-a10-shelf-macros-batches-and-recovery) (PDF page 66)
- [Reference A11. Animation layers](#reference-a11-animation-layers) (PDF page 72)
- [Reference A12. Lipsync](#reference-a12-lipsync) (PDF page 75)
- [Reference B. Additional commands and workflow controls](#reference-b-additional-commands-and-workflow-controls) (PDF page 77)
- [Reference C. Complete settings and saved-record reference](#reference-c-complete-settings-and-saved-record-reference) (PDF page 94)
- [Reference D. Command lookup index](#reference-d-command-lookup-index) (PDF page 132)

## 1. Installation, upgrade and first run

Download the [12.1.3 install ZIP](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/v12.1.3/b4_anim_assist_v12.1.3.zip). In Bforartists, choose Edit > Preferences > Add-ons > Install from Disk, select the ZIP and enable Anim Assist. Install the archive directly. Its internal package folder is `B4_anim_assist`; the repository's readable source folder is named `anim_assist`.

When upgrading, save the scene, close active modal tools, replace the installed addon, and restart Bforartists if an older version remains loaded. Check the version in Preferences before continuing. Open an existing file, inspect animation and saved tool settings, then save a new copy. Do not use Deep Uninstall for an ordinary upgrade: it is the explicit purge operation described in the maintenance reference.

This addon is intended for Bforartists. The recorded release run used Bforartists 5.2.0 with Blender runtime 5.3.0 Alpha, build `0a1ca45552db`. That evidence does not verify every other host version. Do not infer standard Blender support from the Blender runtime version.

Open Properties > Scene > Anim Assist > Setup and run **First Run Setup**. It seeds the tool registry and Quick Shelf. The same area can create an Anim Assist workspace. The workspace is a convenience layout; changing workspaces does not convert or repair a character rig.

Choose a saved scene copy for learning. Start with one animated object, or one selected control bone in Pose Mode. Give it keys at frames 1 and 25. Most tools are easier to understand when the affected channels and time range are small.

## 2. Navigation, scope and shortcuts

Anim Assist has three main homes. It does not add its main panels to the ordinary 3D Viewport sidebar.

- **Graph Editor > N sidebar > Anim Assist:** Select, Shape Curves, Retime, Clean Up, Pose & Rig, Quick Shelf. Use this home when the selected curves and keys are the important scope.
- **Dope Sheet > N sidebar > Anim Assist:** Block, Inbetween, Time, Mirror & Match, Keys & Channels, Shelf & Macros. Use this home for blocking poses and timing.
- **Properties > Scene > Anim Assist:** This Pose, Whole Animation, Rig, Face, Setup, Settings, Help & Diagnostics. Use this home for rig-wide tasks, trajectory, layers, lipsync and setup.

The 3D Viewport, Graph Editor and Dope Sheet headers also offer Anim Assist menus. **Open Anim Assist Panel** opens the editor's home. **Open in Separate Window** opens an additional working window. **Add Anim Assist Workspace** creates a layout with the animation editors available. These are navigation commands; they do not add animation keys.

The optional Anim Assist pie menu defaults to **Shift+Alt+D** and is disabled until enabled in Settings. Rebind it through Bforartists keymap settings if it conflicts with another addon. The current unified header pie is the supported navigation shortcut; older source files containing other pie bindings are not instructions to enable them.

Some tools use an interactive drag. The offset drag supports Shift for finer motion, Ctrl for coarser motion, left-click or Enter to confirm, and right-click or Escape to cancel. A modal tool must finish or cancel before you start another action. Check its on-screen prompt: controls belong to that tool and are not universal keyboard shortcuts.

### Scope before every edit

An object selection, a pose-bone selection, a channel selection and a key selection are different things. Selecting a bone in the viewport does not select all its keyframes in the Graph Editor. A tool may use the active object, selected bones, selected f-curves, selected keys, the current frame, or an explicit range. Read its scope controls before applying it.

For key operations, put the pointer in the intended animation editor and select the actual keys. For rig operations, make the armature active, enter Pose Mode and select control bones. For lipsync shape-key targets, verify the assigned mesh rather than assuming the active armature owns the shape keys.

Properties named Axis, Channel Mask, Space, Pivot, Range, Preserve Contact, Exclusion Pattern or Assigned Bones narrow a task. They are not interchangeable. A channel mask filters what can change; a time range filters when it can change; a pivot or coordinate space changes how a transform is calculated.

### Help and disabled controls

Enable Extended Help to show the detailed popup controls. **Help & Diagnostics > Help Browser** groups the help topics by category. The manual carries those descriptions into the reference and adds commands not covered by the original help seeds.

A disabled tool usually lacks its editor, target, keys, module settings or rig mapping. Correct the prerequisite reported by the tool. Repeating the command with a different active object can edit the wrong animation, so verify the target first.

## 3. Keys, channels and cleanup workflow

Use selection tools to establish scope before changing data. Selection by key type distinguishes ordinary keys, breakdowns and other keyframe types. Key metadata and tags provide additional organisation. Channel filtering and isolation make dense rigs easier to inspect without changing the rig itself.

Keyframe type and interpolation are separate. A Breakdown key type is a visual/semantic tag. Constant, Linear and Bezier determine how values change between keys. Handle types control the Bezier tangent behavior. Changing a key's type does not automatically create the interpolation you want.

**Example: clean a hand control without disturbing the body.**

1. Make the armature active and select the hand control in Pose Mode.
2. Open the Graph Editor and isolate or filter the relevant channels.
3. Select only the hand keys in the range to inspect.
4. Run key analysis first: dense, redundant or spike checks identify candidates. A diagnostic result is not approval to delete every flagged key.
5. Tag or protect intentional contacts and important accents. Inspect what each cleanup operation respects; protection is not a universal lock for every command.
6. Apply one cleanup tool, play the result, and compare neighboring frames. Use Undo if the motion changes more than intended.

Use key movement for explicit frame shifts and value offsets. **Insert Frames** changes timing by introducing space rather than adding a pose. Delete-by-type and redundant-key removal remove data; check the selected channels and protection policy before using them. Bookmarks record useful frames for later recall or batch operations; they are not duplicate animation keys.

## 4. Curves, breakdowns and in-betweens

Breakdown tools calculate a pose or value between surrounding keyed poses. Midpoint uses a balanced result. Favor Previous and Favor Next bias toward one neighbor. Weighted breakdowns expose a numerical blend. A breakdown factor is a value balance, not necessarily a change in the time of the key.

Channel subsets let you work on location, rotation, scale or filtered channels. Exclusion patterns keep unwanted channels out of a breakdown operation. Presets save useful breakdown behavior. Modal breakdown tools let you audition a value before confirmation. Pose Compare makes a reference available for judging the change.

**Example: create a held anticipation.**

1. Key a neutral pose at frame 1 and the action pose at frame 25.
2. Move the playhead to frame 18, select the controls that should participate, and confirm that neighboring poses exist.
3. Use Favor Previous or a weighted breakdown to keep the character closer to the frame-1 pose.
4. Inspect the resulting silhouette. Tag the new key as a Breakdown if useful.
5. Set interpolation separately: Constant for blocking, or Bezier for a smooth transition.
6. Adjust the keys' timing in the Dope Sheet if the held pose lasts too long. Do not use value bias as a substitute for timing.

The core curve tools include Blend Frame, Blend Offset, Blend to Neighbor, Ease To Ease, Push / Pull and Smooth Keys. They reshape existing values or handles. Select a short test range and judge the result in both the viewport and Graph Editor. The command reference describes the specific targets and numerical options.

User breakdown presets, interpolation options, pose references and bookmarks serve different purposes. A preset stores tool behavior; a pose reference stores comparison information; a bookmark stores a time. Name them for the task so they remain recognisable later.

## 5. Transform offsets, space, pivots and falloff

Transform offsets change translation, rotation or scale across the targets and frames chosen by the tool. **Nudge Current Frame** works at the playhead; **Offset Selected Keys** walks selected key times. Push and Pull supply signed offsets along an axis. Pose offset presets and modal offsets provide quicker ways to audition the same family of changes.

Choose the coordinate space before the amount. A local-axis offset follows the target's orientation; a world-space operation uses scene axes. The pivot affects rotations and scale. Channel masks and axis filtering restrict the channels. Auto-Key Missing determines whether a tool can create keys on channels that were not keyed already.

Falloff distributes the offset across time or neighboring targets as specified by that tool. Preserve-contact options constrain a contact-related workflow; verify the actual rig setup and contact range instead of assuming the checkbox reconstructs ground contact automatically.

**Example: raise an existing jump without moving the takeoff pose.**

1. Select the jump control and the keys around the airborne apex.
2. Choose the intended space and allow only the vertical location channel.
3. Start with a small positive offset. Choose a falloff that fades toward the selected range's ends.
4. Apply to selected keys or audition the modal offset. Confirm only after checking the takeoff and landing frames.
5. Inspect the actual location curves. If a previously unkeyed channel now has keys, check Auto-Key Missing and undo before correcting the scope.

Fast Offset Mode and Auto-key Outside Margins are preferences for the older Anim Offset workflow. Their effects are described in the settings reference. Do not assume they govern every transform tool in the later workflow modules.

## 6. Trajectory, arcs and spacing diagnostics

Trajectory tools sample motion to show its path through space. Arc overlays reveal bends and discontinuities. Spacing analysis reveals changes in speed; closely spaced samples mean less movement during the sampled interval. Sampling step and range determine both the detail and the cost of the display.

Trajectory diagnostics, issue navigation and path overlays are analysis aids. Use the next/previous issue controls to inspect a flagged frame, then decide whether the motion is intentional. A planted foot, snap or contact can legitimately differ from smooth airborne motion.

**Example: check a wrist arc.**

1. Select a wrist control on an animated armature.
2. Open Properties > Scene > Anim Assist > Whole Animation and enable its trajectory display.
3. Set a range around the gesture and a small sampling step.
4. Enable spacing or arc diagnostics, inspect flagged frames, and compare with the character's silhouette.
5. Correct the animation with curve, timing or offset tools, then refresh the sampled display.
6. Reduce the range or sample density when working on a dense rig. Disable overlays you no longer need.

## 7. Retiming, ripple, gaps and time warp

Retiming changes key times. Scale operations expand or compress timing around a pivot. Offset operations shift it. Ripple operations move later keys along with the edit. Gap tools add or remove empty time. Time-warp tools redistribute timing across a range. Snapping and rounding tools align key times to a grid.

A scale factor is not a frame count. For a tool that scales key times, 1 leaves the timing unchanged, values below 1 compress it, and values above 1 expand it. Check that operator's pivot and range settings before applying a factor. Subframe keys and coincident keys need attention when rounding or compressing.

**Example: speed up the middle of a gesture without moving the opening.**

1. Select the middle gesture's keys in the Dope Sheet or Graph Editor.
2. Set the pivot to the intended start of that range.
3. Apply a modest time scale below 1. Inspect the selected range's end.
4. Use ripple only if following action should move with the shortened gesture.
5. Check all affected body parts and later keys, not only the active control.
6. Run timing diagnostics and inspect any collisions or fractional times before snapping them.

Use range-from-selection and range-from-scene helpers to establish explicit limits. Modal retime tools are useful for auditioning a change; cancel before trying a different tool. Preserve intentional holds and contacts when cleaning up timing.

## 8. Temporary controls, proxies, locators and baking

A proxy or temporary locator provides another control for an existing target. It does not make the original rig disposable. Session tools track the temporary objects and constraints so they can be baked and cleaned up in an organised way.

Use locator and proxy creation only after selecting the intended rig controls. Inspect the resulting constraints and the space they operate in. Bake transfers evaluated motion to keys according to the chosen targets, frame range and sampling. Cleanup removes temporary support objects or constraints; it should happen after you have confirmed the baked result.

**Example: edit a prop through a temporary control.**

1. Save the scene and select the animated prop or its rig control.
2. Start a temporary-control session and create the appropriate locator or proxy.
3. Edit the proxy while inspecting the original target's evaluated motion.
4. Bake the intended range to the original target. Compare the result at the beginning, middle and end of the range.
5. Remove the temporary constraints or controls with the matching cleanup tool.
6. Play the scene again. If cleanup changes the result, Undo and revisit the bake settings before deleting support objects.

Batch proxy and one-click workflows shorten this sequence, but their scope still matters. Session management, cleanup and recovery tools are included individually in the reference.

## 9. Matching, rig detection and space switching

Matching copies a pose or transform according to its space and target rules. IK/FK and space switching also depend on rig-specific controls and switch properties. Detection can suggest mappings; it cannot guarantee that every custom rig follows the same naming convention.

Run the setup/detection tools for the actual armature. Inspect the detected chains, pair names, switch property and values. Test a single limb before batching the whole character. Transform matching, switch compensation and switch baking solve different tasks: matching aligns a pose, compensation limits a discontinuity, and baking writes a change over a time range.

**Example: test an IK/FK handoff.**

1. Pick one limb and set the playhead to a pose where a mismatch is easy to see.
2. Confirm the rig's control mapping and switch property in Setup.
3. Use the appropriate match command, inspect the aligned result, then switch the rig mode.
4. Check the frame before and after the switch. Use the switch compensation or bake workflow when needed.
5. Test contact-preservation behavior with a planted hand or foot before applying it across a shot.

If detection finds the wrong chain, correct the mapping. Repeated matching cannot repair an incorrect switch-property assignment. Keep custom rig constraints, drivers and control hierarchy in mind when evaluating the result.

## 10. Mirroring and left/right pair management

Mirroring needs reliable pairs and a defined mirror plane or space. Opposite Selection changes the selection to paired controls; it does not mirror the pose. Pair detection and overrides establish which controls correspond. Mirror Pose, mirror transforms and batch mirror operations affect animation according to their own scope.

**Example: mirror an arm pose.**

1. Detect pairs for the active armature and inspect the left/right control matches.
2. Add overrides for controls whose names do not follow the detected convention.
3. Select the source side, set the mirror axis/space and limit channels if needed.
4. Apply the pose mirror at the playhead. Inspect rotation and scale as well as location.
5. Check asymmetric controls and custom properties separately. Use batch mirroring only after the single-pose result is correct.

Pair exceptions, custom names, mirror scope, transforms and diagnostics have separate reference entries. Local axes on the two sides of a rig may differ; a mirrored silhouette alone does not prove every keyed channel is correct.

## 11. Quick Shelf, search, Recents, macros and batches

Use Quick Shelf to keep frequent tools visible. Favorites are chosen tools; Recents are completed tool runs. Search uses the registered tool inventory. Repeat Last reads the newest completed Recent entry. Version 12.1.3 also orders older files' Recents by timestamp and rewrites the stored order when another completed tool is recorded.

Cancelled commands and tools still waiting for modal input do not count as completed actions. A command absent from Recents may still be available through Search. Clearing Recents empties that list rather than restoring defaults.

Macros run a sequence of registered tool steps. Add a macro, add its steps and parameters, validate it, then try it on a small test scene. Validation checks the sequence; it does not establish that every operation is artistically appropriate for the current rig. Batch: Selected Targets and Batch: Bookmarked Frames broaden the task's scope. Review the targets and frame bookmarks before running them.

**Example: make a repeatable finishing pass.**

1. Run the intended tools individually on a copied scene.
2. Create a custom macro and add those exact tools with explicit parameters.
3. Validate the macro, then run it on one target and a short range.
4. Inspect the result and operation history. Correct the macro before using a batch command.
5. Add the validated macro or frequently used tools to Favorites as appropriate.

Workspace profiles and preset export/import transfer tool configuration. They do not package the rig, audio, animation or external binaries. Tool recovery snapshots are a separate feature from Ghost Tool snapshots; read their scope and retention controls before relying on them.

## 12. Animation layers

Initialize Layers for the active armature before building a stack. The base layer refers to the existing animation; additional layers hold separate Actions. Give each layer a clear name and assign its bones or parts so a face layer does not unintentionally affect the entire character.

Layer **weight** controls influence. **Override** replaces lower-layer channel values according to weight. **Additive** adds a correction. **Multiply** scales lower-layer values. **Combine** uses the layer engine's channel-specific combination rules. Verify rotation behavior on your rig rather than assuming all Euler or quaternion rotations blend identically.

In 12.1.3, selecting a layer sets the active row in the layer list; it does not automatically switch the armature's active Action. New layers create backing Actions named from the layer, such as `AA_Layer_Breathing`. To author keys there, explicitly choose that Action in the Action Editor and confirm its owner/slot. Initialize Layers records the original Action on the base layer. Keep that original Action available when returning from a correction pass.

**Evaluate Stack** applies the combined result at the current frame. This build does not install a general frame-change playback evaluator for the layer stack. Check a pose with Evaluate Stack and use the supported merge/flatten workflow when you need final keyed output. Do not treat a layer list selection or its weight slider as proof that every playback frame is being evaluated automatically.

**Edit Active Only**, **Auto-Assign on Key** and the per-layer **Auto Key** flags are exposed and stored, but the shipped source does not connect them to a general interception of native key insertion. Assign bones manually and check the actual Action receiving keys. These flags are not a dependable lock on ordinary Bforartists posing/keying outside the addon commands.

Mute disables a layer's contribution. Solo isolates layers for inspection. Lock and protection are editing/management controls, not synonyms for mute. Layer order affects evaluation. Scope and custom filters narrow the channels, while per-channel overrides customise their blend behavior.

**Example: add a secondary breathing pass.**

1. Initialize the stack with the existing animation as its base.
2. Add a new layer, name it Breathing, and assign only the torso controls that should participate.
3. Choose Additive, select the layer and explicitly select its `AA_Layer_Breathing` Action in the Action Editor. Add a small keyed correction using the rig's suitable channels.
4. Return to the original Action for normal scene evaluation. At a test frame, use Evaluate Stack; adjust the layer's weight, then evaluate again with mute/solo changes to compare its contribution.
5. Check that the arms, face and other unassigned controls have not changed.
6. Use merge/flatten only when you intend to commit the stack into output animation. Save a copy before reducing a stack you may need to edit later.

For modern slotted Actions, lipsync baking in 12.1.3 reuses the layer Action's single slot. The older second-slot issue could leave keys invisible to the layer evaluator. Do not solve it by adding arbitrary extra slots; update the addon and rebake using the configured target.

## 13. Lipsync: audio, bones, shape keys and live/baked modes

The lipsync system can target **Bones**, **Shape Keys**, or **Both**. Assign the actual armature and/or mesh, wire the bone roles or shape-key names, choose the viseme library and bind supported audio to a lipsync layer link. A layer link records the target, audio, timing, library, backend and workflow mode.

Built-in libraries are Basic Mouth Open, Cartoon (5 visemes) and Realistic (12 visemes). Use a library that your rig can represent. A missing jaw or mouth shape cannot be supplied by selecting a more elaborate library. Capture Viseme and related controls let you record or manage custom poses; shape-key wiring maps a viseme name to an existing key block on the target mesh.

**Amplitude Only** analyses the WAV envelope and gives approximate mouth motion without an external executable. **Rhubarb Lip Sync** uses the configured Rhubarb binary for phoneme-based output. Read any fallback notice when Rhubarb is unavailable. The recorded 12.1.3 verification exercised Amplitude, not the Rhubarb backend.

**PREVIEW (Live)** uses drivers and a saved cue table. In that mode, Bake updates cue data; it does not mean that final animation keys have been written. **SHIPPED (Baked)** writes curves to the configured targets and removes the relevant live drivers. Use the toggle when moving from iteration to render/export output, and inspect the target Actions afterward. The render-preview warning is guidance; it is not automatic final approval of the output.

**Example: shape-key dialogue pass.**

1. Select the mesh that owns the mouth shape keys. Set the lipsync target to Shape Keys and assign that mesh explicitly.
2. Autofill wiring only if its detected names are appropriate; otherwise wire each required viseme to the actual shape-key name.
3. Set the audio, frame offset, library and backend. Choose PREVIEW for iteration.
4. Bake/analyse the audio to populate cues, then scrub the shot and inspect the live mouth shapes.
5. Switch to SHIPPED and inspect the baked shape-key Action.
6. Polish selected output keys and run **Mark as Manual Override** on them before rebaking. Do not assume every hand edit is protected merely because it was made manually.
7. Rebake and confirm the marked keys survive. **Clear Auto Keys** removes automatic output while retaining marked manual work.

For a bone target, configure the armature, layer and bone wiring instead. For Both, inspect both output owners. Setup modes such as Markers Only provide timing guidance without the same output as a full keyed pass. Anticipation frames shift the mouth's preparation before a cue onset; frame offset places the audio-derived sequence in the shot.

Audio hashes detect changed source files. Refresh Audio Hash updates the recorded identity; it does not make old animation match changed audio. Reanalyse or rebake as appropriate. Check the saved audio path on another machine and verify the assigned mesh/armature after reopening.

## 14. Troubleshooting, recovery and maintenance

**Nothing changes:** check the editor under the pointer, selected keys, active object, bone selection, time range and channel masks. Read the tool's prerequisite message. Confirm that the relevant workflow module is enabled in Settings.

**A transform changes too much:** inspect scope, space, pivot, falloff and Auto-Key Missing. Undo before changing these controls and trying again.

**A bake disappears from a layer:** verify the active armature, layer Action and Action slot. Install 12.1.3, use the supported layer target and inspect the output in that Action.

**Recents or Repeat Last uses the wrong entry:** 12.1.3 reads stored timestamps. Run a completed tool to normalise the list or explicitly clear Recents. Cancelled operations are not completed entries.

**Lipsync is silent or produces no keys:** check that the audio path exists, the WAV is supported, a layer link is selected, the target owner exists, and wiring has at least the channels required for that target. PREVIEW uses drivers/cues; inspect SHIPPED output when you need keys.

**Rebake loses polish:** verify that the edited keys were marked as manual overrides on the actual target Action before the rebake. General key tags are not automatically the same as lipsync manual-override metadata.

**Panels seem missing:** check the three current homes and header menus. The Help Browser is under Properties > Scene > Anim Assist > Help & Diagnostics. Older help descriptions that mention a generic viewport sidebar refer to the earlier layout.

**Registration or stale settings problem:** use Check Saved Settings Version, diagnostics or Repair Registration as described in the maintenance reference. Deep Uninstall purges addon data and requires deliberate confirmation; save a backup before using it.

Use native Undo for an unwanted edit and save/reopen a test scene to check persistence. Operation history, error logs and diagnostics help reproduce an issue; they do not replace a .blend backup. Report the addon version, Bforartists build, command identifier, target type, selection, range and exact reproduction steps.

## 15. How to use the complete reference

The following reference groups the shipped help topics by workflow and category, then documents remaining commands and all source-defined settings. Entries contain the tool's purpose and behavior, its command when applicable, available arguments and prerequisite messages. Use the workflow chapter for the selection and context shared by that family of tools.

The settings reference includes user controls, command arguments and stored record fields. A stored record field explains saved state; it is not an invitation to modify internal identifiers. Defaults describe newly created settings, not necessarily the values in an upgraded file. Dynamic choices depend on the current rig, scene or registered tools and are identified as such.

The manual is source-checked documentation, not evidence that every interactive command has been tested on every rig. The release passed 170 internal tests, 26 repair checks and 16 workflow checks on the recorded host. See the [release verification](releases/12.1.3/VERIFICATION.md) for the test boundary.

## Reference A1. General settings, diagnostics and core tools

**Find this workflow:** Properties > Scene > Anim Assist > Settings or Help & Diagnostics; core curve tools are under Graph Editor > Shape Curves.

### Diagnostics

#### Show Diagnostics Panel

Controls whether the Anim Assist Diagnostics panel appears in the Properties editor: Scene tab > Anim Assist > Help & Diagnostics.

The panel itself has no performance cost when collapsed; this toggle is provided so you can hide it entirely when demoing to artists.

**Help topic:** `pref.diagnostics_visible`.

#### Dense Key Min Gap

The diagnostics scan flags consecutive keys whose gap falls below this value as 'dense'. Typical values range from 1.0 (sub-frame keys) to 2.0 (back-to-back integer keys).

**Help topic:** `pref.p2_dense_min_gap`.

#### Redundant Key Tolerance

A key is flagged as redundant when its value lies within this tolerance of the straight line between its two neighbours. Tighten this to catch only exact duplicates; loosen it to catch near-flat segments.

**Help topic:** `pref.p2_redundant_tolerance`.

#### Spike Ratio

The spike detector compares each key's deviation from the local smoothed curve against the median neighbour deviation. Values at or above this ratio are flagged as spikes.

**Help topic:** `pref.p2_spike_ratio`.

#### Refresh Diagnostics

Forces a fresh capability probe, cache flush and runtime state rebuild. Use this if an external addon has changed the scene between your last interaction and now.

**Help topic:** `op.anim_assist.refresh_diagnostics`.

**Command:** `anim_assist.refresh_diagnostics`.

#### Copy Diagnostics

Copies a text dump of the diagnostics panel  -  active target, timeline range, editor presence, capabilities, runtime cache  -  to the system clipboard, suitable for pasting into a bug report.

**Help topic:** `op.anim_assist.copy_diagnostics`.

**Command:** `anim_assist.copy_diagnostics`.

#### Diagnostics Panel

The Anim Assist Diagnostics panel lives in the Properties editor: Scene tab > Anim Assist > Help & Diagnostics. It surfaces the active target, the effective timeline range, which animation editors are open, the capabilities registry, and the current runtime cache.

Everything it shows is read-only; the Refresh and Copy buttons rebuild or export the snapshot.

**Help topic:** `panel.aa_pt_diagnostics`.

### General

#### Debug Mode

When enabled, Anim Assist logs DEBUG-level messages from every subsystem to the Blender console.

Use this when investigating an unexpected behaviour or when reporting an issue. The log level is applied live the moment you toggle the checkbox  -  no reload required.

**Help topic:** `pref.debug_mode`.

#### Performance Mode

Performance Mode suppresses non-essential draw passes and diagnostic scans while you are actively editing keys on complex rigs.

Leave this off during normal work  -  turn it on only when the sidebar feels sluggish on very dense actions.

**Help topic:** `pref.performance_mode`.

#### Show Extended Help Popups

When enabled, every Anim Assist control that has a registered help entry gains a small question-mark icon beside it. Clicking the icon opens a popup with a long-form explanation of the control.

Disable this to hide every explainer icon across the addon. Native Bforartists hover tooltips and the Help Browser remain available.

**Help topic:** `pref.show_explainer_help`.

#### Compact UI Mode

Compact UI Mode keeps explainer icons visible but hides their neighbouring text labels, so sidebar panels remain dense on small screens.

Has no effect when Show Extended Help Popups is disabled.

**Help topic:** `pref.compact_ui_mode`.

### Modules

#### Selection Tools

Master switch for the Selection Tools module. Disabling it prevents its operators and panels from registering at startup.

**Help topic:** `pref.enable_selection`.

#### Key Utilities

Master switch for the Key Utilities module (copy/paste, offset, mirror, snap, safe delete).

**Help topic:** `pref.enable_keys`.

#### Transform Workflows

Master switch for the Transform Workflows module (future phase).

**Help topic:** `pref.enable_transform`.

#### Breakdown Tools

Master switch for the Breakdown Tools module (future phase).

**Help topic:** `pref.enable_breakdown`.

#### Trajectory Tools

Master switch for the Trajectory Tools module (future phase).

**Help topic:** `pref.enable_trajectory`.

#### Retime Tools

Master switch for the Retime Tools module (future phase).

**Help topic:** `pref.enable_retime`.

#### Temp Controls

Master switch for the Temp Controls module (future phase).

**Help topic:** `pref.enable_controls`.

#### Matching Workflows

Master switch for the Matching Workflows module (future phase).

**Help topic:** `pref.enable_matching`.

### Settings

#### Export Settings

Exports every Anim Assist preference (general, modules, tool behaviour, diagnostics settings) to a JSON file you can commit to a project repo or share with a team-mate.

The operator never writes scene data  -  only addon preferences.

**Help topic:** `op.anim_assist.export_settings`.

**Command:** `anim_assist.export_settings`.

- **Filter Glob** (`filter_glob`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: *.json. Hidden command/state field; set through the normal workflow rather than as a general preference.

#### Import Settings

Loads preferences previously saved with Export Settings. Unknown fields in the JSON are ignored so a file exported from a newer build can still be imported into an older one.

**Help topic:** `op.anim_assist.import_settings`.

**Command:** `anim_assist.import_settings`. Declared as an undoable operation.

- **Filter Glob** (`filter_glob`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: *.json. Hidden command/state field; set through the normal workflow rather than as a general preference.

### Tool Behaviour

#### Fast Offset Mode

In Fast Offset Mode the Anim Offset modal operator defers its propagation pass until you release the mouse. This is significantly faster on complex rigs at the cost of not seeing the final result live during the drag.

**Help topic:** `pref.animassist_fast_offset`.

#### Auto-key Outside Margins

When enabled, Anim Offset auto-inserts keys on frames that fall outside the active mask's blend region so those frames get preserved explicitly rather than relying on interpolation.

**Help topic:** `pref.animassist_autokey_outside_margins`.

#### Drag Sensitivity

Number of screen-space pixels the mouse must travel for a modal drag operator to reach its full factor. Lower values feel twitchier; higher values give finer control.

**Help topic:** `pref.animassist_drag_sensitivity`.

## Reference A2. Keys, channels and metadata

**Find this workflow:** Graph Editor > Anim Assist > Select / Clean Up, or Dope Sheet > Keys & Channels.

### Channel Filtering

#### Show All Channels

Sets fc.hide = False on every FCurve reachable through the active animation editor. Resets any previous isolation.

**Help topic:** `op.animassist.show_all_channels`.

**Command:** `animassist.show_all_channels`. Declared as an undoable operation.

#### Invert Channel Visibility

Toggles fc.hide on every visible FCurve. Hidden becomes visible and vice versa.

**Help topic:** `op.animassist.invert_channel_visibility`.

**Command:** `animassist.invert_channel_visibility`. Declared as an undoable operation.

#### Mute Unselected Channels

Sets fc.mute on every FCurve whose select flag is False, leaving the selected curves audible. Use this for solo-style evaluation tests.

**Help topic:** `op.animassist.mute_unselected_channels`.

**Command:** `animassist.mute_unselected_channels`. Declared as an undoable operation.

#### Save Channel Isolation State

Snapshots every FCurve's hide and select state and pushes the snapshot onto an internal stack so you can restore it later with Restore Channel Isolation State.

**Help topic:** `op.animassist.push_channel_isolation`.

**Command:** `animassist.push_channel_isolation`.

#### Restore Channel Isolation State

Restores hide and select on every FCurve to the most recently pushed snapshot. Reports a warning if the stack is empty.

**Help topic:** `op.animassist.pop_channel_isolation`.

**Command:** `animassist.pop_channel_isolation`. Declared as an undoable operation.

### Channel Isolation

#### Isolate Selected Channels

Hides every FCurve in the active editor whose select flag is False, leaving only the currently selected curves visible. Restore the previous state with Restore Channel Isolation State.

**Help topic:** `op.animassist.isolate_selected_channels`.

**Command:** `animassist.isolate_selected_channels`. Declared as an undoable operation.

#### Isolate Transform Channels

Filters visible FCurves to one transform group: Location, Rotation, Scale, or all three combined. Curves on custom properties or constraints are hidden.

**Help topic:** `op.animassist.isolate_transform`.

**Command:** `animassist.isolate_transform`. Declared as an undoable operation.

- **Channel Group** (`channel`): Which transform group to isolate New-data default: Location. Choices: Location: Isolate Location FCurves (`loc`); Rotation: Isolate Rotation FCurves (`rot`); Scale: Isolate Scale FCurves (`scale`); All Transforms: Isolate every transform FCurve (`all_transform`).

#### Isolate Selected Bones

Restricted to armature objects. Hides every FCurve whose data path does not target one of the currently selected pose bones.

**Help topic:** `op.animassist.isolate_selected_bones`.

**Command:** `animassist.isolate_selected_bones`. Declared as an undoable operation.

#### Isolate Custom Properties

Hides every FCurve except those whose data path targets a custom (ID) property  -  useful when tuning rig sliders.

**Help topic:** `op.animassist.isolate_custom_props`.

**Command:** `animassist.isolate_custom_props`. Declared as an undoable operation.

#### Isolate Channels by Regex

Hides every FCurve whose data_path string does not match the supplied Python regular expression. Compilation errors are reported and the operation is cancelled.

**Help topic:** `op.animassist.isolate_by_regex`.

**Command:** `animassist.isolate_by_regex`. Declared as an undoable operation.

- **Regex** (`pattern`): Python regular expression matched against fc.data_path New-data default: empty.

### Key Analysis

#### Scan Dense Keys

Scans every visible FCurve for adjacent keys whose frame gap is below the supplied min_gap. Hits are selected and a summary is stored for the panel readout.

**Help topic:** `op.animassist.scan_dense_keys`.

**Command:** `animassist.scan_dense_keys`. Declared as an undoable operation.

- **Min Gap** (`min_gap`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: 1.0. Allowed range: 0.0 to no explicit upper limit.

#### Scan Redundant Keys

Flags any key whose value is within the supplied tolerance of the linear interpolation between its two immediate neighbours. Useful for cleaning up over-keyed curves.

**Help topic:** `op.animassist.scan_redundant_keys`.

**Command:** `animassist.scan_redundant_keys`. Declared as an undoable operation.

- **Tol** (`tol`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: 0.0001. Allowed range: 0.0 to no explicit upper limit.

#### Scan Spike Keys

Flags any key whose deviation from the local smoothed curve exceeds the supplied ratio compared to the median neighbour deviation. Hits are selected and counted.

**Help topic:** `op.animassist.scan_spike_keys`.

**Command:** `animassist.scan_spike_keys`. Declared as an undoable operation.

- **Ratio** (`ratio`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: 4.0. Allowed range: 1.0 to no explicit upper limit.

### Key Editing

#### Copy Selected Keys

Stores every selected key's frame, value and both handles in an in-process clipboard. Subsequent Paste operators read from this clipboard.

**Help topic:** `op.animassist.copy_selected_keys`.

**Command:** `animassist.copy_selected_keys`.

#### Paste Keys at Frame

Inserts every key from the in-process clipboard at its original frame plus the supplied frame_offset. Existing keys at the target frames are overwritten. Reports a warning if the clipboard is empty.

**Help topic:** `op.animassist.paste_keys_at_frame`.

**Command:** `animassist.paste_keys_at_frame`. Declared as an undoable operation.

- **Frame Offset** (`frame_offset`): Frames added to each pasted key relative to the current frame New-data default: .

#### Offset Selected Keys (Frame)

Adds dx to the X coordinate of every selected key. Handles are translated together so curve shape is preserved. Only FCurves that actually changed get fc.update() called.

**Help topic:** `op.animassist.offset_selected_frames`.

**Command:** `animassist.offset_selected_frames`. Declared as an undoable operation.

- **Frame Delta** (`dx`): Number of frames to add to each selected key's time New-data default: 1.0.

#### Offset Selected Keys (Value)

Adds dy to the Y coordinate of every selected key. Handles are translated together so curve shape is preserved.

**Help topic:** `op.animassist.offset_selected_values`.

**Command:** `animassist.offset_selected_values`. Declared as an undoable operation.

- **Value Delta** (`dy`): Amount to add to each selected key's value (co.y) New-data default: 0.1.

#### Snap Selected Keys to Integer Frames

Rounds every selected key's X coordinate to the nearest integer frame and translates its handles by the same delta so the curve shape stays intact.

**Help topic:** `op.animassist.snap_keys_to_integer_frames`.

**Command:** `animassist.snap_keys_to_integer_frames`. Declared as an undoable operation.

#### Mirror Selected Keys at Current Frame

Reflects every selected key across the current frame on the X axis. Handle X positions are swapped relative to the pivot and handle Y values are swapped between left and right so bezier curvature stays correct.

**Help topic:** `op.animassist.mirror_selected_keys`.

**Command:** `animassist.mirror_selected_keys`. Declared as an undoable operation.

#### Safe Delete Selected Keys

Walks the current selection, skips any key whose metadata carries the Protected flag, and removes the rest. Reports the number deleted and the number skipped.

**Help topic:** `op.animassist.safe_delete_selected_keys`.

**Command:** `animassist.safe_delete_selected_keys`. Declared as an undoable operation.

### Key Metadata

#### Tag Selected Keys

Writes the supplied tag string into the per-scene metadata record for every selected key. Empty tag is rejected. Use Select Keys by Tag to query the result later.

**Help topic:** `op.animassist.tag_selected_keys`.

**Command:** `animassist.tag_selected_keys`. Declared as an undoable operation.

- **Tag** (`tag`): String written into the tag field of every selected key's metadata New-data default: empty.

#### Clear Tags on Selected Keys

Sets the tag field to an empty string on every selected key's metadata record. Other metadata fields (note, flavor, protected) are left untouched.

**Help topic:** `op.animassist.clear_tag_selected_keys`.

**Command:** `animassist.clear_tag_selected_keys`. Declared as an undoable operation.

#### Set Note on Selected Keys

Stores the supplied note string in the metadata record of every selected key. Notes are free-form and intended for human-readable annotations.

**Help topic:** `op.animassist.set_key_note`.

**Command:** `animassist.set_key_note`. Declared as an undoable operation.

- **Note** (`note`): Free-form annotation written into the metadata note field New-data default: empty.

#### Set Key Flavor

Stores the supplied flavor string on every selected key. Flavor is a secondary tag axis distinct from the main tag, intended for keying-pass labels such as 'block', 'spline', or 'polish'.

**Help topic:** `op.animassist.set_key_flavor`.

**Command:** `animassist.set_key_flavor`. Declared as an undoable operation.

- **Flavor** (`flavor`): Secondary tag axis stored in the metadata flavor field New-data default: empty.

#### Protect / Unprotect Selected Keys

Toggles the Protected flag on every selected key's metadata record. Protected keys are skipped by Safe Delete and shown in their own selection filter.

The same operator runs both Protect and Unprotect via the 'protected' boolean property; the panel exposes both as separate buttons.

**Help topic:** `op.animassist.protect_selected_keys`.

**Command:** `animassist.protect_selected_keys`. Declared as an undoable operation.

- **Protected** (`protected`): True to protect, False to clear the protected flag New-data default: On.

#### Prune Orphan Key Metadata

Walks every metadata record and removes those whose (object, data_path, array_index, frame) identity no longer matches a real keyframe. Run after large key edits or object renames.

**Help topic:** `op.animassist.prune_orphan_key_metadata`.

**Command:** `animassist.prune_orphan_key_metadata`. Declared as an undoable operation.

#### Clear All Key Metadata

Empties the per-scene metadata collection. Tags, notes, flavors and protection flags are all wiped. There is no undo for this  -  only the operator's own undo step.

**Help topic:** `op.animassist.clear_all_key_metadata`.

**Command:** `animassist.clear_all_key_metadata`. Declared as an undoable operation.

### Key Selection

#### Select All Visible Keys

Selects every key on every FCurve currently visible in the active animation editor. Hidden, muted, or filtered FCurves are skipped.

**Help topic:** `op.animassist.select_all_visible`.

**Command:** `animassist.select_all_visible`. Declared as an undoable operation.

#### Deselect All Visible Keys

Clears the selection on every visible FCurve. Use this as a reset before building a new selection with the predicate operators.

**Help topic:** `op.animassist.deselect_all_visible`.

**Command:** `animassist.deselect_all_visible`. Declared as an undoable operation.

#### Invert Key Selection

Inverts the per-key selection state on every visible FCurve. Selected keys become deselected and vice versa.

**Help topic:** `op.animassist.invert_selection`.

**Command:** `animassist.invert_selection`. Declared as an undoable operation.

#### Select Keys by Type

Selects every key whose Blender key type matches the chosen value: Keyframe, Breakdown, Moving Hold, Extreme, or Jitter.

Enable Extend to add to the existing selection instead of replacing it.

**Help topic:** `op.animassist.select_by_key_type_adv`.

**Command:** `animassist.select_by_key_type_adv`. Declared as an undoable operation.

- **Key Type** (`key_type`): Blender key type to match New-data default: Keyframe. Choices: Keyframe (`KEYFRAME`); Breakdown (`BREAKDOWN`); Moving Hold (`MOVING_HOLD`); Extreme (`EXTREME`); Jitter (`JITTER`).

- **Extend** (`additive`): Add to the existing selection instead of replacing it New-data default: Off.

#### Select Keys by Interpolation

Selects keys whose interpolation type matches Constant, Linear, or Bezier. Useful when reviewing curves for stepped animation passes.

**Help topic:** `op.animassist.select_by_interpolation`.

**Command:** `animassist.select_by_interpolation`. Declared as an undoable operation.

- **Interpolation** (`interp`): Interpolation type to match New-data default: Bezier. Choices: Constant (`CONSTANT`); Linear (`LINEAR`); Bezier (`BEZIER`).

- **Extend** (`additive`): Add to the existing selection instead of replacing it New-data default: Off.

#### Select Keys by Handle Type

Selects keys whose left or right handle type matches Auto Clamped, Auto, Vector, Aligned, or Free.

**Help topic:** `op.animassist.select_by_handle_type_adv`.

**Command:** `animassist.select_by_handle_type_adv`. Declared as an undoable operation.

- **Handle Type** (`handle_type`): Handle type to match on either side of the key New-data default: Auto Clamped. Choices: Auto Clamped (`AUTO_CLAMPED`); Auto (`AUTO`); Vector (`VECTOR`); Aligned (`ALIGNED`); Free (`FREE`).

- **Extend** (`additive`): Add to the existing selection instead of replacing it New-data default: Off.

#### Select Keys in Frame Range

Selects every key on visible FCurves whose frame coordinate lies inside the supplied [start, end] interval (inclusive).

**Help topic:** `op.animassist.select_frame_range`.

**Command:** `animassist.select_frame_range`. Declared as an undoable operation.

- **Start** (`start`): First frame of the inclusive selection range New-data default: 1.0.

- **End** (`end`): Last frame of the inclusive selection range New-data default: 250.0.

#### Select Keys in Playback Range

Shortcut for Select Keys in Frame Range using the scene's frame_start and frame_end. Respects the current scene only.

**Help topic:** `op.animassist.select_playback_range`.

**Command:** `animassist.select_playback_range`. Declared as an undoable operation.

#### Select Keys in Preview Range

Shortcut for Select Keys in Frame Range using the scene's frame_preview_start and frame_preview_end. Only enabled when Use Preview Range is on.

**Help topic:** `op.animassist.select_preview_range`.

**Command:** `animassist.select_preview_range`. Declared as an undoable operation.

#### Select Every Nth Key

Selects keys at index 0, N, 2N, ... on each visible FCurve. Use the Offset property to start the stride at a different index. Useful for thinning dense pose tests.

**Help topic:** `op.animassist.select_every_nth`.

**Command:** `animassist.select_every_nth`. Declared as an undoable operation.

- **N** (`n`): Stride between selected keys (1 selects every key) New-data default: 2. Allowed range: 1 to 1000.

- **Offset** (`offset`): Index of the first key to select on each FCurve New-data default: . Allowed range: 0 to 1000.

#### Extend Selection to Neighbours

Adds the immediate neighbours of every currently-selected key to the selection. Direction can be Left, Right, or Both.

**Help topic:** `op.animassist.select_neighbors`.

**Command:** `animassist.select_neighbors`. Declared as an undoable operation.

- **Direction** (`direction`): Which neighbours to add to the selection New-data default: Both. Choices: Left: Add the immediate left neighbour of every selected key (`LEFT`); Right: Add the immediate right neighbour of every selected key (`RIGHT`); Both: Add both neighbours of every selected key (`BOTH`).

#### Select Between First/Last Selected

Computes the bounding frame interval of the current selection and selects every key inside that interval. Reports a warning if nothing is currently selected.

**Help topic:** `op.animassist.select_between_selected`.

**Command:** `animassist.select_between_selected`. Declared as an undoable operation.

#### Select First/Last Keys

Selects only the first key, the last key, or both endpoints of every visible FCurve. Use this to grab anchor poses without dragging through the timeline.

**Help topic:** `op.animassist.select_first_last`.

**Command:** `animassist.select_first_last`. Declared as an undoable operation.

- **Endpoint** (`mode`): Which endpoint keys to select New-data default: Both. Choices: First: Select only the first key of each FCurve (`FIRST`); Last: Select only the last key of each FCurve (`LAST`); Both: Select both endpoint keys of each FCurve (`BOTH`).

#### Select Local Extremes

Walks each visible FCurve and selects every key whose value is strictly greater (peak) or strictly less (valley) than both immediate neighbours. Endpoints are included if they differ from their single neighbour.

**Help topic:** `op.animassist.select_local_extremes`.

**Command:** `animassist.select_local_extremes`. Declared as an undoable operation.

#### Select Keys in Flat Segments

Selects keys whose value matches at least one neighbour within the supplied tolerance. Use this to identify hold regions inside otherwise active curves.

**Help topic:** `op.animassist.select_flat_segments`.

**Command:** `animassist.select_flat_segments`. Declared as an undoable operation.

- **Tolerance** (`tol`): Maximum value delta to a neighbour that still counts as flat New-data default: 0.0001. Allowed range: 0.0 to no explicit upper limit.

#### Select Keys by Value Range

Selects every key whose Y value lies inside the supplied value range. Min and Max are sorted automatically. Enable Extend to add to the current selection.

**Help topic:** `op.animassist.select_by_value_range`.

**Command:** `animassist.select_by_value_range`. Declared as an undoable operation.

- **Min** (`lo`): Lower bound of the inclusive value range New-data default: .

- **Max** (`hi`): Upper bound of the inclusive value range New-data default: 1.0.

- **Extend** (`additive`): Add to existing selection instead of replacing it New-data default: Off.

#### Select Keys by Tag

Looks up every key against the per-scene metadata registry and selects those whose stored tag exactly equals the supplied string. Empty tag selects nothing.

**Help topic:** `op.animassist.select_by_tag`.

**Command:** `animassist.select_by_tag`. Declared as an undoable operation.

- **Tag** (`tag`): Exact tag string to match against each key's metadata record New-data default: empty.

#### Select Protected Keys

Selects every key whose metadata record carries the Protected flag. Toggle Invert to select unprotected keys instead.

Protected keys are exempted from Safe Delete.

**Help topic:** `op.animassist.select_protected`.

**Command:** `animassist.select_protected`. Declared as an undoable operation.

- **Invert** (`invert`): Select unprotected keys instead of protected ones New-data default: Off.

## Reference A3. Breakdowns, in-betweens and pose comparison

**Find this workflow:** Dope Sheet > Anim Assist > Block / Inbetween; interpolation controls also appear in Graph Editor > Shape Curves.

### Breakdown Core

#### Breakdown at Current Frame

Inserts a new key at the scene's current frame on every targeted fcurve, blended between the previous and next pose using the factor on the breakdownpanel. Honours the active mask, exclusion set, and interpolation options.

**Help topic:** `op.animassist.breakdown_current_frame`.

**Command:** `animassist.breakdown_current_frame`. Declared as an undoable operation.

#### Weighted Previous/Next

Identical to Breakdown at Current Frame but explicitly reads the factor slider so animators can scrub it while the operator re-runs via repeat-last. Use this for quick A/B comparisons of different blend weights.

**Help topic:** `op.animassist.breakdown_weighted`.

**Command:** `animassist.breakdown_weighted`. Declared as an undoable operation.

- **Factor** (`factor`): Override factor for this run. 0 favours the previous pose, 1 favours the next. New-data default: 0.5. Allowed range: -1.0 to 2.0.

#### Favor Previous Pose

Writes a breakdown heavily biased toward the previous pose (factor 0.25). Useful for snappy outs where most of the pose should hold on the starting key.

**Help topic:** `op.animassist.breakdown_favor_prev`.

**Command:** `animassist.breakdown_favor_prev`. Declared as an undoable operation.

#### Favor Next Pose

Writes a breakdown heavily biased toward the next pose (factor 0.75). Useful for heavy anticipation where the pose should lean into the next key.

**Help topic:** `op.animassist.breakdown_favor_next`.

**Command:** `animassist.breakdown_favor_next`. Declared as an undoable operation.

#### Midpoint Breakdown

Writes a perfect midpoint (factor 0.5) on every targeted fcurve. The cleanest starting point for pose-to-pose inbetweens.

**Help topic:** `op.animassist.breakdown_midpoint`.

**Command:** `animassist.breakdown_midpoint`. Declared as an undoable operation.

#### Push From Previous

Extrapolates the new key past the previous pose using the Push Strength setting. Produces a snappier out than a vanilla weighted breakdown.

**Help topic:** `op.animassist.breakdown_push_prev`.

**Command:** `animassist.breakdown_push_prev`. Declared as an undoable operation.

#### Push Into Next

Extrapolates the new key past the next pose using the Push Strength setting. Produces a heavier anticipation than a vanilla weighted breakdown.

**Help topic:** `op.animassist.breakdown_push_next`.

**Command:** `animassist.breakdown_push_next`. Declared as an undoable operation.

#### Pull To Previous

Softens the new key toward the previous pose using the Pull Strength setting (clamped 0..1). Useful for easing into a hold.

**Help topic:** `op.animassist.breakdown_pull_prev`.

**Command:** `animassist.breakdown_pull_prev`. Declared as an undoable operation.

#### Pull To Next

Softens the new key toward the next pose using the Pull Strength setting (clamped 0..1). Useful for easing out of a hold.

**Help topic:** `op.animassist.breakdown_pull_next`.

**Command:** `animassist.breakdown_pull_next`. Declared as an undoable operation.

#### 25 / 50 / 75 Quick Buttons

Writes a breakdown at a fixed percentage (25%, 50%, or 75%) without touching the factor slider. Ideal for muscle-memory pose-to-pose blocking.

**Help topic:** `op.animassist.breakdown_percentage`.

**Command:** `animassist.breakdown_percentage`. Declared as an undoable operation.

- **Percent** (`percent`): Fixed breakdown percentage, 0 favours the previous pose and 100 favours the next. New-data default: 50. Allowed range: 0 to 100.

#### Relative Offset

Adds a numeric offset to the currently evaluated value at the target frame instead of blending between neighbours. Useful for nudging a key without touching the blend factor.

**Help topic:** `op.animassist.breakdown_offset`.

**Command:** `animassist.breakdown_offset`. Declared as an undoable operation.

#### Batch Over Selected Frames

Reads the set of selected key frames and runs the current breakdown recipe at each one in turn. Respects the active mask and exclusion set. Large selections can be slow  -  watch the console.

**Help topic:** `op.animassist.breakdown_batch_frames`.

**Command:** `animassist.breakdown_batch_frames`. Declared as an undoable operation.

#### Numeric Breakdown

Opens a numeric prompt for factor, frame, and mode and runs a single breakdown. The most precise entry point when you already know the exact percentage you want.

**Help topic:** `op.animassist.breakdown_numeric`.

**Command:** `animassist.breakdown_numeric`. Declared as an undoable operation.

- **Factor** (`factor`): Blend factor. 0 favours the previous pose, 1 favours the next. New-data default: 0.5. Allowed range: -1.0 to 2.0.

- **Frame** (`target_frame`): Frame at which to insert the new breakdown key. New-data default: 1.0.

- **Mode** (`mode`): Blend mode for this numeric breakdown. New-data default: Replace. Choices: Replace: Clean blend (`REPLACE`); Offset: Offset current value (`OFFSET`); Push Prev: Extrapolate past prev (`PUSH_PREV`); Push Next: Extrapolate past next (`PUSH_NEXT`); Pull Prev: Soften toward prev (`PULL_PREV`); Pull Next: Soften toward next (`PULL_NEXT`).

#### Repeat Last Breakdown

Re-runs the last breakdown recipe (factor, mode, mask) on the current selection. Useful when stepping frame-by-frame through a block.

**Help topic:** `op.animassist.breakdown_repeat_last`.

**Command:** `animassist.breakdown_repeat_last`. Declared as an undoable operation.

### Breakdown Presets

#### Apply Breakdown Preset

Applies the built-in preset selected on the breakdownpanel. Each preset bundles a factor, mode, and mask kind so you can swap between common pose-to-pose recipes with one click.

**Help topic:** `op.animassist.apply_preset`.

**Command:** `animassist.apply_preset`. Declared as an undoable operation.

- **Preset Name** (`preset_name`): Name of the built-in preset to apply. Leave empty to use the active preset from the property group. New-data default: empty.

#### Save Current As Preset

Captures the current factor, mode, and mask kind into a new user preset stored on the Scene. User presets persist across save/reload alongside the blend file.

**Help topic:** `op.animassist.save_preset`.

**Command:** `animassist.save_preset`. Declared as an undoable operation.

- **Preset Name** (`preset_name`): Human-readable name for the new user preset. New-data default: Custom Preset.

#### Delete User Preset

Removes the active user preset from the Scene. Built-in presets cannot be deleted.

**Help topic:** `op.animassist.delete_preset`.

**Command:** `animassist.delete_preset`. Declared as an undoable operation.

#### Manage Exclusion Set

Adds or removes an fcurve data_path substring from the breakdownexclusion set. Fcurves matching any pattern are skipped by every breakdownbreakdown operator.

**Help topic:** `op.animassist.manage_exclusion_set`.

**Command:** `animassist.manage_exclusion_set`. Declared as an undoable operation.

- **Action** (`action`): Whether to add a new empty pattern row or remove the currently selected one. New-data default: Add. Choices: Add: Append a new empty exclusion pattern row. (`ADD`); Remove: Remove the currently selected exclusion pattern row. (`REMOVE`); Clear: Remove every exclusion pattern row. (`CLEAR`).

### Breakdown Subsets

#### Transform Only

Applies the breakdown only to location, rotation, and scale channels, leaving custom properties untouched.

**Help topic:** `op.animassist.breakdown_transform_only`.

**Command:** `animassist.breakdown_transform_only`. Declared as an undoable operation.

#### Rotation Only

Applies the breakdown only to rotation channels (Euler and quaternion). Location and scale are left untouched.

**Help topic:** `op.animassist.breakdown_rotation_only`.

**Command:** `animassist.breakdown_rotation_only`. Declared as an undoable operation.

#### Location Only

Applies the breakdown only to location channels. Rotation and scale are left untouched.

**Help topic:** `op.animassist.breakdown_location_only`.

**Command:** `animassist.breakdown_location_only`. Declared as an undoable operation.

#### Scale Only

Applies the breakdown only to scale channels. Location and rotation are left untouched.

**Help topic:** `op.animassist.breakdown_scale_only`.

**Command:** `animassist.breakdown_scale_only`. Declared as an undoable operation.

#### Selected Controls Only

Limits the breakdown target set to the currently selected pose bones or objects. When nothing is selected the operator cancels with a report.

**Help topic:** `op.animassist.breakdown_selected_controls`.

**Command:** `animassist.breakdown_selected_controls`. Declared as an undoable operation.

#### Custom Channel Subset

Runs the breakdown using the kind and per-axis checkboxes on the breakdownmask panel. Combine with the exclusion set for precise scoping.

**Help topic:** `op.animassist.breakdown_channel_subset`.

**Command:** `animassist.breakdown_channel_subset`. Declared as an undoable operation.

#### Per-Axis Masking

Per-axis checkboxes let you restrict a breakdown to, for example, only the Y component of location channels. Axis indices map to 0=X, 1=Y, 2=Z, and 3=W for quaternion channels.

**Help topic:** `prop.p3_mask_axis`.

#### Ignore Locked Axes

When enabled, the breakdown engine silently skips any fcurve with its lock flag set so locked transforms stay untouched.

**Help topic:** `prop.p3_skip_locked`.

#### Respect Exclusion Set

When enabled, every fcurve whose data_path matches any pattern in the active exclusion set is skipped by every breakdownbreakdown operator.

**Help topic:** `prop.p3_respect_exclusions`.

### Inbetween Tools

#### Inbetween in Selected Gap

Detects the gap between the two currently selected keys on each fcurve and inserts a fresh inbetween using the factor on the breakdownpanel. Ignores fcurves that do not have exactly two selected keys.

**Help topic:** `op.animassist.inbetween_selected_gap`.

**Command:** `animassist.inbetween_selected_gap`. Declared as an undoable operation.

#### Evenly Distribute Inbetweens

Inserts ``Inbetween Count`` keys evenly spaced inside the gap between the two selected keys on each fcurve. Uses the active interpolation options.

**Help topic:** `op.animassist.inbetween_distribute`.

**Command:** `animassist.inbetween_distribute`. Declared as an undoable operation.

#### Inbetween on Key Clusters

Walks the selected keys, groups consecutive keys into clusters, and inserts inbetweens between clusters. Useful for cleaning up rough block passes where you blocked with multiple keys per pose.

**Help topic:** `op.animassist.inbetween_on_clusters`.

**Command:** `animassist.inbetween_on_clusters`. Declared as an undoable operation.

#### Inbetween Count

Controls how many inbetween keys the Evenly Distribute and Clusters operators insert inside each gap.

**Help topic:** `prop.p3_inbetween_count`.

### Interpolation Options

#### Quaternion-Aware Interpolation

When enabled, rotation_quaternion channels are blended with a true slerp across all four components so the resulting rotation never flips mid-arc. Strongly recommended for any rig using quaternion rotations.

**Help topic:** `prop.p3_quaternion_aware`.

#### Euler Continuity

When enabled, Euler rotations that cross a ±π boundary take the shortest path instead of the long way round.

**Help topic:** `prop.p3_euler_wrap_aware`.

#### Visual Transform

When enabled, the breakdown samples ``fcurve.evaluate()`` at the target frame instead of linearly interpolating between neighbour keys. Useful for constrained rigs where the visible pose diverges from the raw key values.

**Help topic:** `prop.p3_visual_transform`.

#### Local / World Computation

Switches visual-transform sampling between the channel's own local space and world space. The world branch converts the sampled value back into the channel space when possible.

**Help topic:** `prop.p3_space_toggle`.

#### Preserve World Contact

When enabled, the breakdown attempts to keep world-space contacts (feet, hands) stable. Depends heavily on rig setup and constraint topology.

**Help topic:** `prop.p3_preserve_world_contact`.

#### Preserve Child Contact

When enabled, the breakdown attempts to keep parented child-object contacts stable. Depends on rig setup.

**Help topic:** `prop.p3_preserve_child_contact`.

#### Preserve Tangent Continuity

When enabled, the new breakdown key inherits its handle type from the closer neighbour key so the resulting curve flows cleanly instead of defaulting to Auto Clamped.

**Help topic:** `prop.p3_match_tangents`.

#### Auto-Key Missing Channels

When enabled, channels with no neighbouring keys receive an anchor key at their currently evaluated value so the breakdown has something to blend off next time.

**Help topic:** `prop.p3_auto_key_missing`.

### Modal Breakdown

#### Modal Drag Breakdown

Enter modal mode and drag the mouse horizontally to scrub the breakdown factor between the previous and next pose. LMB commits, RMB / Esc cancels and restores the pre-drag state.

**Help topic:** `op.animassist.modal_drag_breakdown`.

**Command:** `animassist.modal_drag_breakdown`. Declared as an undoable operation.

#### Preview Breakdown

Writes a preview breakdown at the current frame without marking it as committed. Animators can inspect the result and either press Commit Preview to keep it or run any other operator to discard it.

**Help topic:** `op.animassist.preview_breakdown`.

**Command:** `animassist.preview_breakdown`. Declared as an undoable operation.

#### Commit Preview

Marks the currently staged preview breakdown as committed so it is no longer rolled back by the next preview operator.

**Help topic:** `op.animassist.commit_preview`.

**Command:** `animassist.commit_preview`. Declared as an undoable operation.

### Pose Compare

#### Snapshot Previous Pose

Walks every fcurve on the active object, evaluates its value at the previous key frame, and stores the result in the Previous slot of the pose compare state. Used by the Pose Compare Report.

**Help topic:** `op.animassist.pose_snapshot_prev`.

**Command:** `animassist.pose_snapshot_prev`. Internal helper, normally invoked by the interface rather than as an independent artist task.

#### Snapshot Next Pose

Walks every fcurve on the active object, evaluates its value at the next key frame, and stores the result in the Next slot of the pose compare state.

**Help topic:** `op.animassist.pose_snapshot_next`.

**Command:** `animassist.pose_snapshot_next`. Internal helper, normally invoked by the interface rather than as an independent artist task.

#### Snapshot Reference Pose

Stores the current-frame pose as a reference that other breakdown tools can blend toward. Used by Blend Toward Reference.

**Help topic:** `op.animassist.pose_snapshot_reference`.

**Command:** `animassist.pose_snapshot_reference`. Internal helper, normally invoked by the interface rather than as an independent artist task.

#### Pose Compare Report

Reports channel-by-channel differences between the Previous and Next pose snapshots in the Info editor, with a one-row summary box shown on the breakdownpanel.

**Help topic:** `op.animassist.pose_compare_report`.

**Command:** `animassist.pose_compare_report`. Internal helper, normally invoked by the interface rather than as an independent artist task.

- **Tolerance** (`tolerance`): Channels whose absolute difference is below this value are treated as equal. New-data default: 1e-05. Allowed range: 0.0 to 1.0.

#### Breakdown From Clipboard A/B

Uses the Previous (A) and Next (B) pose snapshots as the blend targets instead of the nearest keys. Runs the breakdown at the current frame.

**Help topic:** `op.animassist.breakdown_from_clipboard`.

**Command:** `animassist.breakdown_from_clipboard`. Declared as an undoable operation.

- **Slot** (`slot`): Which stored pose snapshot to blend toward. New-data default: Previous Pose. Choices: Previous Pose: Use the 'previous pose' compare slot. (`PREV`); Next Pose: Use the 'next pose' compare slot. (`NEXT`).

#### Blend Toward Reference

Blends the current-frame pose toward the stored reference snapshot by the current factor. Useful for gradually pulling a frame back to a canonical pose without resetting it.

**Help topic:** `op.animassist.blend_toward_reference`.

**Command:** `animassist.blend_toward_reference`. Declared as an undoable operation.

## Reference A4. Offsets and transforms

**Find this workflow:** Properties > Scene > Anim Assist > This Pose, or Dope Sheet > Inbetween; the core Anim Offset range tools also appear under Retime.

### Axis Filtering

#### Translation Only

Applies the current translate delta and ignores rotation and scale amounts. Equivalent to setting channel mask to Translation and running Nudge.

**Help topic:** `op.animassist.p4_offset_translate_only`.

**Command:** `animassist.p4_offset_translate_only`.

#### Rotation Only

Applies the current rotate delta and ignores translation and scale.

**Help topic:** `op.animassist.p4_offset_rotate_only`.

**Command:** `animassist.p4_offset_rotate_only`.

#### Scale Only

Applies the current scale delta and ignores translation and rotation.

**Help topic:** `op.animassist.p4_offset_scale_only`.

**Command:** `animassist.p4_offset_scale_only`.

#### Combined TRS

Applies the full T+R+S delta in one atomic write. Use for compound pose tweaks where you want the whole offset to land as a single undo step.

**Help topic:** `op.animassist.p4_offset_trs_combined`.

**Command:** `animassist.p4_offset_trs_combined`.

### Falloff

#### Linear Falloff

Offsets ramp in from 0 at the window start to 1 at the midpoint and back to 0 at the window end.

**Help topic:** `prop.p4_falloff_linear`.

#### Ease-In Distribution

Applies less of the offset at the start of the window and more at the end. Does not modify fcurve tangents  -  it only weights the amount of the delta applied per frame.

**Help topic:** `prop.p4_falloff_ease_in`.

#### Ease-Out Distribution

Applies more of the offset at the start of the window and less at the end. Does not modify fcurve tangents.

**Help topic:** `prop.p4_falloff_ease_out`.

#### Bell Falloff

Offset weight rises smoothly from zero at each edge of the window to full weight at the midpoint. Use for tapered nudges over a range.

**Help topic:** `prop.p4_falloff_bell`.

#### Frame Range Falloff

Sets Scope to Frame Range and uses Range Start / Range End as the falloff window regardless of which keys are currently selected.

**Help topic:** `prop.p4_frame_range_falloff`.

### Modal Offset

#### Modal Drag Offset

Invokes a modal drag: mouse X maps to horizontal delta, mouse Y to vertical delta, Shift for fine, Ctrl for coarse, LMB or Enter to commit, RMB or Esc to cancel. On cancel the scene is restored to its pre-drag state.

**Help topic:** `op.animassist.p4_modal_offset`.

**Command:** `animassist.p4_modal_offset`. Declared as an undoable operation.

- **Sensitivity** (`sensitivity`): Pixels per unit of offset delta during modal drag. New-data default: 100.0. Allowed range: 1.0 to no explicit upper limit.

#### Screen-Space Horizontal Drag

While modal, the horizontal mouse movement is mapped to the horizontal offset axis in the current space.

**Help topic:** `prop.p4_modal_screen_h`.

#### Screen-Space Vertical Drag

While modal, the vertical mouse movement is mapped to the vertical offset axis in the current space.

**Help topic:** `prop.p4_modal_screen_v`.

#### Commit / Cancel

Commit finalises the offset and records it as Last Offset. Cancel restores every affected fcurve to its exact pre-drag state using the snapshot taken on invoke.

**Help topic:** `prop.p4_modal_commit_cancel`.

#### Numeric Offset Entry

While in modal drag, typing digits, minus, and dot populates a numeric buffer shown in the header. Enter commits the typed value as the exact offset and exits modal.

**Help topic:** `prop.p4_modal_numeric_entry`.

#### Preview Ghost

Shows the current delta in the area header while modal drag is active. All fcurve writes are reversible by cancelling  -  the scene is never committed until the user releases with LMB or Enter.

**Help topic:** `prop.p4_modal_preview_ghost`.

### Offset Presets

#### Apply Preset

Applies the currently selected transform multiplier preset (Tiny / Small / Normal / Big / Huge) to the entered offset amounts and runs Nudge Current Frame.

**Help topic:** `op.animassist.p4_apply_preset`.

**Command:** `animassist.p4_apply_preset`.

#### Fine Step

When on, every offset operator reduces its entered amounts by a factor of ten. Modal drag also honours this while Shift is held.

**Help topic:** `prop.p4_fine_step`.

#### Reapply Last

Re-runs the most recent offset request with identical amounts, space, pivot, scope, and falloff. Useful for stepping through a sequence of identical nudges.

**Help topic:** `op.animassist.p4_reapply_last`.

**Command:** `animassist.p4_reapply_last`. Declared as an undoable operation.

#### Invert Last

Negates every T/R/S component of the most recent offset and re-runs with the same options. Effectively an explicit 'undo the offset' that survives non-offset edits in between.

**Help topic:** `op.animassist.p4_invert_last`.

**Command:** `animassist.p4_invert_last`. Declared as an undoable operation.

### Offset Targets

#### Selected Channels Only

When on, only fcurves whose keyframe points are selected in the Dope Sheet or Graph Editor are written. Safer for surgical edits.

**Help topic:** `prop.p4_selected_channels_only`.

#### Selected Targets Only

Targets are always resolved from the current selection  -  this entry documents that behavior for the Help Browser.

**Help topic:** `prop.p4_selected_targets_only`.

#### Keyed Channels Only

Prevents creating new fcurves during an offset. Recommended for polishing passes where you only want to modify existing keys.

**Help topic:** `prop.p4_keyed_channels_only`.

#### Auto-Key Missing

When on, offsetinserts a new key on channels that do not already have one at the affected frame. Off by default to keep offsets strictly additive to your existing pose.

**Help topic:** `prop.p4_auto_key_missing`.

#### Preserve Contact Axis

Forces the translation delta on one axis to zero before the pipeline runs. Use Preserve Z to keep feet planted while nudging sideways.

**Help topic:** `prop.p4_preserve_contact`.

#### Locked & Muted Safety Filters

The Skip Locked and Skip Muted filters are on by default. Turning them off lets offsets write through locked or muted fcurves  -  do so deliberately.

**Help topic:** `prop.p4_safety_filters`.

#### Mirror Sign by Name

When enabled, any target whose name contains a recognised side token (.L/.R, _L/_R, Left/Right) on the mirrored side receives the delta negated on the configured mirror axis.

**Help topic:** `prop.p4_mirror_sign`.

### Pivot Modes

#### Median of Selection

Rotation and scale offsets rotate and scale around the averaged origin of the selected targets.

**Help topic:** `prop.p4_pivot_average`.

#### Active Target Pivot

Rotation and scale offsets rotate and scale around the active object or active pose bone, regardless of how many other targets are selected.

**Help topic:** `prop.p4_pivot_active`.

#### Individual Origins

Default mode. Each selected target is offset independently around its own origin. Best for mass pose tweaks.

**Help topic:** `prop.p4_pivot_individual`.

#### Custom Pivot Point

Rotation and scale offsets use the world-space custom pivot set on the offsetpanel. Useful for rotating a group around a scene landmark.

**Help topic:** `prop.p4_pivot_custom`.

#### 3D Cursor Pivot

Rotation and scale offsets pivot around the scene's 3D cursor.

**Help topic:** `prop.p4_pivot_cursor`.

#### Active Bone Head

Only meaningful in Pose Mode. Rotation and scale offsets pivot around the head of the active pose bone.

**Help topic:** `prop.p4_pivot_bone_head`.

#### Active Bone Tail

Only meaningful in Pose Mode. Rotation and scale offsets pivot around the tail of the active pose bone.

**Help topic:** `prop.p4_pivot_bone_tail`.

### Push/Pull

#### Push X

Applies a positive translation delta on X using the current push/pull amount. Space, falloff, and mirror sign apply. Useful for adding overshoot and snappier anticipation on sideways motion.

**Help topic:** `op.animassist.p4_push_x`.

**Command:** `animassist.p4_push_x`.

#### Push Y

Applies a positive translation delta on Y using the current push/pull amount. Space, falloff, and mirror sign apply.

**Help topic:** `op.animassist.p4_push_y`.

**Command:** `animassist.p4_push_y`.

#### Push Z

Applies a positive translation delta on Z. Space, falloff, and mirror sign apply. Common for adding vertical overshoot on jumps and squashes.

**Help topic:** `op.animassist.p4_push_z`.

**Command:** `animassist.p4_push_z`.

#### Pull X

Applies a negative translation delta on X using the current push/pull amount. Inverse of Push X.

**Help topic:** `op.animassist.p4_pull_x`.

**Command:** `animassist.p4_pull_x`.

#### Pull Y

Applies a negative translation delta on Y. Inverse of Push Y.

**Help topic:** `op.animassist.p4_pull_y`.

**Command:** `animassist.p4_pull_y`.

#### Pull Z

Applies a negative translation delta on Z. Inverse of Push Z.

**Help topic:** `op.animassist.p4_pull_z`.

**Command:** `animassist.p4_pull_z`.

### Space Modes

#### Local Space

The fastest space because no conversion is performed. Offsets feed straight into location / rotation / scale channels. Best for per-bone-local pose tweaks.

**Help topic:** `prop.p4_space_local`.

#### World Space

Offsets are rotated from world space into the target's basis before being written. Use this when you want a single direction (e.g. +Z up) to mean the same thing regardless of how a bone is rotated.

**Help topic:** `prop.p4_space_world`.

#### Parent Space

Offsets are converted from the parent bone or parent object's local space into the target's basis. Useful for propagating a consistent nudge down a chain.

**Help topic:** `prop.p4_space_parent`.

#### Visual Space

Identical to World Space but the world matrix is read from the depsgraph-evaluated object, so constraints and drivers contribute to the reference frame. Writes still land on the basis channels.

**Help topic:** `prop.p4_space_visual`.

#### Gimbal Space

Rotation deltas are applied axis-aligned in the target's own rotation order. Useful for keeping euler curves clean when tweaking a single axis. Falls back to Local Space on quaternion targets.

**Help topic:** `prop.p4_space_gimbal`.

### Transform Nudge

#### Nudge Current Frame

Applies the current translate, rotate, and scale amounts to every selected target at the scene's current frame. Honours channel mask, space, pivot, preserve-contact, and mirror-sign options. Writes keys only on channels that already have a key unless Auto-Key Missing is enabled.

**Help topic:** `op.animassist.p4_nudge_current`.

**Command:** `animassist.p4_nudge_current`.

#### Offset Selected Keys

Walks every selected keyframe point on the target channels and applies the offset delta at that frame. Falloff and mirror sign are applied per frame. Frames without any selected key are skipped entirely.

**Help topic:** `op.animassist.p4_offset_selected`.

**Command:** `animassist.p4_offset_selected`.

## Reference A5. Trajectory and spacing

**Find this workflow:** Properties > Scene > Anim Assist > Whole Animation > trajectory controls.

### Arc Diagnostics

#### Run Diagnostics

Executes every enabled detector (drift, flat arc, zig-zag, pop, spacing, reversal, stop, apex/contact) and replaces the current issue list. Results are drawn as red marker dots in the viewport.

**Help topic:** `op.animassist.p5_run_diagnostics`.

**Command:** `animassist.p5_run_diagnostics`.

#### Arc Drift Detector

Uses a 3-point circumradius fit to measure how far each sample deviates from a smooth arc. Points exceeding the drift tolerance are flagged as ARC_DRIFT issues.

**Help topic:** `prop.p5_enable_drift_detect`.

#### Flat Arc Detector

Analyses variance along each axis in a sliding window. If the two smallest variances are both below the threshold, the segment is flagged as FLAT_ARC  -  indicating a linear motion that might lack arc appeal.

**Help topic:** `prop.p5_enable_flat_detect`.

#### Zig-Zag Detector

Counts velocity sign changes in a sliding window. If the reversal count exceeds the threshold, a ZIGZAG issue is flagged  -  often indicating jitter or over-keying.

**Help topic:** `prop.p5_enable_zigzag_detect`.

#### Pop Detector

Compares each sample's speed against the median. Samples exceeding the pop ratio are flagged as POP issues  -  indicating a potential interpolation glitch or missing ease.

**Help topic:** `prop.p5_enable_pop_detect`.

#### Reversal Detector

Flags points where the velocity dot product with the previous sample is negative, indicating the motion changed direction.

**Help topic:** `prop.p5_enable_reversal_detect`.

#### Stop Detector

Flags frames where the computed speed falls below the stop threshold. Useful for finding unintended holds or plateaus.

**Help topic:** `prop.p5_enable_stop_detect`.

#### Apex/Contact Detector

Marks local highs as APEX and local lows as CONTACT on the Z-axis (configurable). Useful for timing checks on jump arcs.

**Help topic:** `prop.p5_enable_apex_contact_detect`.

#### Drift Tolerance

Points where the normalised deviation (deviation / circumradius) exceeds this value are flagged. Lower values catch subtler deviations but may produce more false positives.

**Help topic:** `prop.p5_drift_tolerance`.

#### Pop Ratio

A sample's speed must exceed this multiple of the median speed to be flagged as a pop. Default is 4.0.

**Help topic:** `prop.p5_pop_ratio`.

### Issue Navigation

#### Next Issue

Moves the scene's current frame to the frame of the next issue after the current position. Wraps around to the first issue if there are no more issues ahead.

**Help topic:** `op.animassist.p5_jump_next_issue`.

**Command:** `animassist.p5_jump_next_issue`. Declared as an undoable operation.

#### Previous Issue

Moves the scene's current frame to the frame of the most recent issue before the current position. Wraps to the last issue if there are no issues behind.

**Help topic:** `op.animassist.p5_jump_prev_issue`.

**Command:** `animassist.p5_jump_prev_issue`. Declared as an undoable operation.

#### Select Bad-Arc Keys

Walks all location-channel keyframe points and selects those within the proximity radius of a detected issue. Deselects keyframes that are not near any issue.

**Help topic:** `op.animassist.p5_select_bad_arc_keys`.

**Command:** `animassist.p5_select_bad_arc_keys`. Declared as an undoable operation.

- **Proximity** (`proximity`): Frame distance within which a keyframe is considered 'near' an issue New-data default: 2.0. Allowed range: 0.5 to no explicit upper limit.

#### Suggest Candidate Keys

Sorts issues by severity and reports the top N frames where a new keyframe insertion could reduce arc deviation. Deduplicates within a 2-frame radius.

**Help topic:** `op.animassist.p5_suggest_candidates`.

**Command:** `animassist.p5_suggest_candidates`.

- **Max Suggestions** (`max_suggestions`): Maximum number of candidate frames to report New-data default: 5. Allowed range: 1 to no explicit upper limit.

### Path Configuration

#### Scope Mode

Around Current Frame samples a window centred on the playhead. Full Playback Range uses the scene's start/end frames. Custom Range lets you set explicit start and end frames.

**Help topic:** `prop.p5_scope_mode`.

#### Frames Before

Only applies in Around Current Frame mode. Increase for a wider view of the trajectory history.

**Help topic:** `prop.p5_window_before`.

#### Frames After

Only applies in Around Current Frame mode. Increase to see more of the upcoming trajectory.

**Help topic:** `prop.p5_window_after`.

#### Space Mode

World draws the path in absolute world coordinates. Camera projects relative to the active camera. Local draws in the object's own coordinate space.

**Help topic:** `prop.p5_space_mode`.

#### Isolate Target

Switches display mode to Isolate and sets the named target as the sole visible trajectory. Useful for focusing on a specific bone in a complex rig.

**Help topic:** `op.animassist.p5_isolate_target`.

**Command:** `animassist.p5_isolate_target`. Declared as an undoable operation.

- **Target Key** (`target_key`): Target key in object_name::bone_name format New-data default: empty.

#### Mute Unselected

Switches display mode to Multi Control, which inherently only shows selected bones or objects. Provides a quick way to declutter the viewport.

**Help topic:** `op.animassist.p5_mute_unselected`.

**Command:** `animassist.p5_mute_unselected`. Declared as an undoable operation.

#### Comparison Mode

When enabled, a second target's trajectory is drawn alongside the primary target using the comparison palette colours.

**Help topic:** `prop.p5_comparison_enabled`.

### Path Overlays

#### Frame Ticks

When enabled, each sampled frame along the path is marked with a small grey dot. Useful for visualising frame spacing at a glance.

**Help topic:** `prop.p5_show_frame_ticks`.

#### Keyframe Ticks

Yellow dots mark the positions of actual keyframes on the path. Frame numbers can optionally be drawn next to these ticks.

**Help topic:** `prop.p5_show_keyframe_ticks`.

#### Frame Numbers

Adds text labels with the frame number beside each keyframe tick. Useful for identifying which key corresponds to which frame.

**Help topic:** `prop.p5_show_frame_numbers`.

#### Velocity Vectors

Green lines extending from each sample point in the direction of motion. Length is proportional to speed. Helps visualise easing.

**Help topic:** `prop.p5_show_velocity`.

#### Tangent Lines

Blue lines through keyframe positions showing the direction of the trajectory at that point. Useful for checking handle alignment.

**Help topic:** `prop.p5_show_tangent`.

#### Ghost Points

Shows the 2 frames before and after the current frame as faded dots, providing local context without cluttering the full path.

**Help topic:** `prop.p5_show_ghost_points`.

### Sampling Options

#### Sample Step

Controls the density of samples along the trajectory. Values below 1.0 enable subframe sampling for smoother paths at the cost of increased computation.

**Help topic:** `prop.p5_sample_step`.

#### Max Samples

Prevents viewport stalls on long frame ranges. If the range divided by the step would exceed this value, sampling stops early. Default is 160.

**Help topic:** `prop.p5_max_samples`.

#### Subframe Sampling

Enables sampling at fractional frame positions. The step property can be set below 1.0 when this is active. Increases computation cost proportionally.

**Help topic:** `prop.p5_use_subframe`.

#### Constraint Evaluation

When enabled, the sampler calls scene.frame_set() and depsgraph.update() for every sample, producing positions that reflect IK, Copy Rotation, and other constraints. Much slower than fcurve-only mode  -  recommended only when constraints drive the motion.

**Help topic:** `prop.p5_use_constraints`.

#### Custom Start Frame

Sets the beginning of the sampling window when scope mode is set to Custom Range.

**Help topic:** `prop.p5_custom_start`.

#### Custom End Frame

Sets the end of the sampling window when scope mode is set to Custom Range.

**Help topic:** `prop.p5_custom_end`.

### Spacing Analysis

#### Spacing Colorization

Segments longer than the median are tinted toward the issue-high colour; shorter segments toward the issue-low colour. The base path colour represents median spacing.

**Help topic:** `prop.p5_show_spacing_color`.

#### Arc Deviation Heatmap

Uses a blue-to-red colour ramp where blue indicates good arc conformance and red indicates high deviation. Overrides spacing colorization when both are enabled.

**Help topic:** `prop.p5_show_deviation_heatmap`.

#### Overspaced Ratio

When a segment between two consecutive samples is longer than spacing_hi times the median segment length, an OVERSPACED issue is reported. Default is 1.8.

**Help topic:** `prop.p5_spacing_hi`.

#### Underspaced Ratio

When a segment is shorter than spacing_lo times the median, an UNDERSPACED issue is reported. Default is 0.4.

**Help topic:** `prop.p5_spacing_lo`.

### Trajectory Display

#### Enable Overlay

Registers a POST_VIEW handler for 3D trajectory geometry and a POST_PIXEL handler for 2D labels and the arc score badge. Triggers an initial sampling pass for all visible targets.

**Help topic:** `op.animassist.p5_enable_overlay`.

**Command:** `animassist.p5_enable_overlay`. Declared as an undoable operation.

#### Disable Overlay

Tears down both draw handlers, clears the draw data buffer, resets RuntimeState.overlay_enabled, and invalidates the path cache.

**Help topic:** `op.animassist.p5_disable_overlay`.

**Command:** `animassist.p5_disable_overlay`. Declared as an undoable operation.

#### Refresh Overlay

Bumps the SessionCache generation counter to invalidate all cached entries, then re-samples every target and rebuilds the draw data. Use this after editing keyframes if auto-refresh is not active.

**Help topic:** `op.animassist.p5_refresh_overlay`.

**Command:** `animassist.p5_refresh_overlay`.

#### Display Mode

Active Control shows only the active bone or object. Multi Control shows every selected bone or object (up to Max Display Targets). Isolate shows only the explicitly named target.

**Help topic:** `prop.p5_display_mode`.

#### Color Preset

Three built-in palettes: Default (blue path, yellow keyframes), Contrast (high-contrast colours for bright scenes), and Pastel (muted tones that reduce visual noise).

**Help topic:** `prop.p5_color_preset`.

#### Path Width

Controls the GPU line width used for the main trajectory path. Increase for visibility on high-DPI displays or crowded scenes.

**Help topic:** `prop.p5_path_width`.

#### Max Display Targets

In Multi Control mode, only the first N selected targets will have their trajectories drawn. Increase for rigs with many controls, decrease if the viewport is lagging. The default is conservative so turning the overlay on does not slow down pose work.

**Help topic:** `prop.p5_max_display_targets`.

## Reference A6. Retiming and timing diagnostics

**Find this workflow:** Graph Editor > Anim Assist > Retime, or Dope Sheet > Time.

### Gap Tools

#### Detect Gaps

A gap is a contiguous window where no FCurve has a keyframe. Only gaps at least as wide as the Gap Threshold are reported. Results are stored on the scene and displayed in the diagnostics sub-panel. The Jump Next/Prev Gap operators use these cached results.

**Help topic:** `op.animassist.p6_detect_gaps`.

**Command:** `animassist.p6_detect_gaps`.

#### Fill Gaps

Constant Hold  -  inserts a key at the gap midpoint on every FCurve, holding the value from the key before the gap. Linear Bridge  -  inserts a midpoint key with LINEAR interpolation to smoothly bridge the gap. Mark Only  -  reports gaps without inserting any keys.

**Help topic:** `op.animassist.p6_fill_gaps`.

**Command:** `animassist.p6_fill_gaps`. Declared as an undoable operation.

#### Collapse Gap at Playhead

Finds the detected gap whose midpoint is nearest the current frame, then ripple-shifts all keys after the gap's start frame backward by the gap's size. This closes the gap without affecting values or relative key spacing outside the collapsed region.

**Help topic:** `op.animassist.p6_collapse_gap`.

**Command:** `animassist.p6_collapse_gap`. Declared as an undoable operation.

#### Distribute Keys

The first and last keys in the range are fixed (boundary keys stay put). All inner keys are repositioned at equal time intervals between the boundaries. Enable 'Snap to Frames' in modal preferences to round the result to integer frames.

**Help topic:** `op.animassist.p6_distribute_keys`.

**Command:** `animassist.p6_distribute_keys`. Declared as an undoable operation.

#### Normalize Spacing

Each consecutive key pair's spacing is compared to the mean spacing for the range. Pairs wider than the mean are compressed; pairs narrower are expanded. This reduces spacing variance without dramatically reshuffling the animation. Multiple passes may be needed for highly irregular timing.

**Help topic:** `op.animassist.p6_normalize_spacing`.

**Command:** `animassist.p6_normalize_spacing`. Declared as an undoable operation.

- **Strength** (`strength`): How strongly to pull toward even spacing (0 = no change, 1 = full distribute) New-data default: 0.5. Allowed range: 0.0 to 1.0.

#### Gap Threshold

Gaps narrower than this value are silently ignored by Detect Gaps and Fill Gaps. Increase when working with densely keyed actions where small gaps are intentional.

**Help topic:** `prop.p6_gap_threshold`.

#### Fill Mode

Constant Hold  -  holds the value from the key immediately before the gap. Linear Bridge  -  inserts a midpoint key and sets interpolation to LINEAR. Mark Only  -  reports the gap location without inserting any new keys.

**Help topic:** `prop.p6_gap_fill_mode`.

### Modal Tools

#### Interactive Scale

Move the mouse left/right after invoking to preview timing scale changes in real-time. The scale factor is displayed in the header. LMB or Enter confirms and pushes an undo step. RMB or Esc cancels and restores original positions. Hold Shift for 0.1 x  precision. Hold Ctrl to snap results to whole frames.

**Help topic:** `op.animassist.p6_modal_scale`.

**Command:** `animassist.p6_modal_scale`. Declared as an undoable operation.

#### Interactive Offset

Move the mouse left/right after invoking to preview offset changes in real-time. The frame delta is displayed in the header. LMB or Enter confirms and pushes an undo step. RMB or Esc cancels and restores original positions. Hold Shift for sub-frame precision. Hold Ctrl to snap to whole frames.

**Help topic:** `op.animassist.p6_modal_offset`.

**Command:** `animassist.p6_modal_offset`. Declared as an undoable operation.

#### Snap in Modal

When enabled, the modal operator rounds the result to the nearest frame after each mouse move. Can also be toggled mid-operation by holding Ctrl.

**Help topic:** `prop.p6_modal_snap`.

### Retiming Basics

#### Scale Keys

All keys (or only those inside the active range) are rescaled around the chosen anchor frame. A factor > 1 spreads keys apart (slower animation); a factor < 1 compresses them (faster animation). Bézier handles are scaled proportionally to preserve curve shape. Use the Anchor Mode drop-down to choose whether to scale from the first key, last key, playhead, active key, or a manually specified custom frame.

**Help topic:** `op.animassist.p6_scale_keys`.

**Command:** `animassist.p6_scale_keys`. Declared as an undoable operation.

- **Scale Factor** (`scale_factor`): Timing multiplier applied around the chosen pivot New-data default: 1.0. Allowed range: 0.01 to 100.0.

#### Offset Keys

The Offset field sets the number of frames to move. Positive values push keys later in time; negative values pull them earlier. When a timing range is active only keys inside that range are affected. Bézier handles shift by the same amount so the curve shape is perfectly preserved.

**Help topic:** `op.animassist.p6_offset_keys`.

**Command:** `animassist.p6_offset_keys`. Declared as an undoable operation.

- **Offset** (`offset_frames`): Number of frames to shift the affected keyframes New-data default: 1.0.

#### Set Pivot from Playhead

Sets the Custom Frame pivot to the current playhead position. Switch Anchor Mode to 'Custom Frame' to use this value in all subsequent scale operations. Useful for keeping a specific pose locked in place while expanding or contracting the animation on either side.

**Help topic:** `op.animassist.p6_set_pivot`.

**Command:** `animassist.p6_set_pivot`. Declared as an undoable operation.

#### Anchor Mode

First Key  -  pivot at the earliest keyframe of the action. Last Key  -  pivot at the latest keyframe. Current Frame  -  pivot at the playhead (most common for in-context edits). Active Key  -  pivot at the highlighted keyframe; falls back to the playhead when no specific key is active. Custom Frame  -  pivot at the value stored in the Custom Frame field.

**Help topic:** `prop.p6_anchor_mode`.

#### Scale Factor

2.0 doubles the animation duration (everything runs at half-speed). 0.5 halves the duration (double speed). The formula is: new_x = pivot + (old_x - pivot)  x  factor. Handles are rescaled by the same factor to preserve tangent continuity.

**Help topic:** `prop.p6_scale_factor`.

#### Offset Frames

Positive = shift later; negative = shift earlier. Both the key position and its Bézier handles are translated by the same amount, so no curve distortion occurs.

**Help topic:** `prop.p6_offset_frames`.

### Ripple Edit

#### Ripple Forward

All keyframes with a time value strictly greater than the current frame are shifted forward by the configured Ripple Amount. Keys at or before the playhead are untouched. This is equivalent to inserting blank time after the playhead without creating new keys.

**Help topic:** `op.animassist.p6_ripple_forward`.

**Command:** `animassist.p6_ripple_forward`. Declared as an undoable operation.

- **Ripple Amount** (`ripple_delta`): Number of frames to shift keys after the playhead New-data default: 1.0.

#### Ripple Backward

All keyframes strictly before the current frame are shifted backward by the Ripple Amount. Useful for pulling in a wind-up or anticipation section when the performance needs more preparation before a hit.

**Help topic:** `op.animassist.p6_ripple_backward`.

**Command:** `animassist.p6_ripple_backward`. Declared as an undoable operation.

- **Ripple Amount** (`ripple_delta`): Number of frames to shift keys before the playhead New-data default: 1.0.

#### Insert Time

A ripple-forward operation sized to exactly N frames (the Frame Count property). No new keyframes are created; existing keys after the playhead are translated to make room. Equivalent to Blender's Timeline  ->  Insert Frames but scoped to the active action.

**Help topic:** `op.animassist.p6_insert_time`.

**Command:** `animassist.p6_insert_time`. Declared as an undoable operation.

- **Frames** (`insert_frames`): Number of blank frames to insert at the playhead New-data default: 1. Allowed range: 1 to no explicit upper limit.

#### Remove Time

Keys inside the removed window (playhead to playhead + N) are deleted first, then all keys after the window's end are rippled backward to close the gap. Equivalent to cutting a section of time from the animation.

**Help topic:** `op.animassist.p6_remove_time`.

**Command:** `animassist.p6_remove_time`. Declared as an undoable operation.

- **Frames** (`remove_frames`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: 1. Allowed range: 1 to no explicit upper limit.

#### Ripple to End

Identical to Ripple Forward but applies only from the playhead to the end of the action rather than to every subsequent key. Useful for quickly closing a gap created by deleting a section of animation.

**Help topic:** `op.animassist.p6_ripple_to_end`.

**Command:** `animassist.p6_ripple_to_end`. Declared as an undoable operation.

- **Ripple Amount** (`ripple_delta`): Number of frames to shift keys from the playhead to the end New-data default: 1.0.

#### Compress Timing

Computes the scale factor needed to make the current range's content fit into the target duration, then applies it. Useful when a walk cycle needs to be tightened to match a shorter audio cue.

**Help topic:** `op.animassist.p6_compress_timing`.

**Command:** `animassist.p6_compress_timing`. Declared as an undoable operation.

- **Target Duration (frames)** (`target_duration`): Desired duration of the active range after compression New-data default: 24.0. Allowed range: 1.0 to no explicit upper limit.

#### Ripple Amount

Positive = shift forward; negative = shift backward. For Ripple Backward the value is automatically negated so you can always enter a magnitude.

**Help topic:** `prop.p6_ripple_delta`.

#### Frame Count

Used by Insert Time (adds blank frames) and Remove Time (collapses a window of frames). Minimum 1.

**Help topic:** `prop.p6_insert_frames`.

### Snap & Clean

#### Snap to Frames

Sub-frame keyframes (e.g. frame 12.37) are nudged to the nearest whole frame. Bézier handles move by the same correction delta so the curve shape is preserved. Reports the count of keys that were moved.

**Help topic:** `op.animassist.p6_snap_to_frames`.

**Command:** `animassist.p6_snap_to_frames`. Declared as an undoable operation.

#### Remove Duplicates

When two or more keys land on the same integer frame, all but the first are removed. This prevents doubled-up keys that cause interpolation glitches and inflated key counts. Useful after ripple or scale operations that may overlap keys.

**Help topic:** `op.animassist.p6_clear_doubles`.

**Command:** `animassist.p6_clear_doubles`. Declared as an undoable operation.

### Time Warp

#### Time Warp %

A convenience wrapper around Scale Keys that accepts a percentage directly. Enter 200 to make the animation run at half speed, 50 to make it run at double speed. Internally this is just (percentage / 100) used as the scale factor. The same Anchor Mode and range restrictions apply.

**Help topic:** `op.animassist.p6_time_warp`.

**Command:** `animassist.p6_time_warp`. Declared as an undoable operation.

- **Warp %** (`warp_percent`): Timing percentage where 100 percent leaves timing unchanged New-data default: 100.0. Allowed range: 1.0 to 10000.0.

#### Reverse Keys

The first key's timing becomes the last and vice-versa. All key values are untouched; only the x (time) coordinates are mirrored around the range's midpoint. Useful for creating reversed or palindrome cycles. The formula is: new_x = (range_start + range_end) - old_x.

**Help topic:** `op.animassist.p6_reverse_keys`.

**Command:** `animassist.p6_reverse_keys`. Declared as an undoable operation.

#### Bake to Integer Frames

Sub-frame keyframes introduced by slow-motion retiming or fractional offset operations are rounded to the nearest integer frame. Bézier handles shift by the same correction delta so curve shape is preserved. Returns a count of how many keys were moved.

**Help topic:** `op.animassist.p6_bake_timing`.

**Command:** `animassist.p6_bake_timing`. Declared as an undoable operation.

#### Reset Timing

The addon stores a keyframe snapshot before each destructive retiming operation (Scale, Offset, Ripple, etc.). Reset Timing rolls back to that snapshot in a single undo step. Only the most recent snapshot is kept; the snapshot is cleared when the file is closed or reloaded.

**Help topic:** `op.animassist.p6_reset_timing`.

**Command:** `animassist.p6_reset_timing`. Declared as an undoable operation.

**Prerequisite messages:** Run a retiming operation before resetting its timing.

#### Match Timing

The reference is the previously active (or second-most-recently selected) object. The active object's action is scaled  -  using the FIRST anchor  -  so that its total key span equals the reference's total key span. Useful for syncing secondary characters or props to a hero rig.

**Help topic:** `op.animassist.p6_match_timing`.

**Command:** `animassist.p6_match_timing`. Declared as an undoable operation.

**Prerequisite messages:** Select a source and a target object to match timing.

### Timing Diagnostics

#### Run Diagnostics

Scans all FCurves in the active action and reports: (1) Timing gaps wider than the Gap Threshold. (2) Key clusters tighter than the Cluster Radius. (3) A Timing Score (0-100) based on spacing variance  -  100 is perfectly even spacing, 0 is maximally erratic. Results are cached on the scene for Jump operators and the report panel.

**Help topic:** `op.animassist.p6_run_diagnostics`.

**Command:** `animassist.p6_run_diagnostics`.

#### Jump to Next Gap

Requires Detect Gaps to have been run first. Wraps around to the first gap after the last one. The gap start frame is set as the scene's current frame.

**Help topic:** `op.animassist.p6_jump_next_gap`.

**Command:** `animassist.p6_jump_next_gap`. Declared as an undoable operation.

#### Jump to Previous Gap

Requires Detect Gaps to have been run first. Wraps around to the last gap after the first one.

**Help topic:** `op.animassist.p6_jump_prev_gap`.

**Command:** `animassist.p6_jump_prev_gap`. Declared as an undoable operation.

#### Jump to Next Cluster

Requires Run Diagnostics to have been run first. A cluster is a group of two or more keys within the Cluster Radius of each other. Jumps to the arithmetic centre of the cluster's frame range.

**Help topic:** `op.animassist.p6_jump_next_cluster`.

**Command:** `animassist.p6_jump_next_cluster`. Declared as an undoable operation.

#### Copy Diagnostics Report

The report includes key count, frame span, average spacing, timing score, and listings of all detected gaps and clusters. Useful for pasting into production notes or sharing with collaborators.

**Help topic:** `op.animassist.p6_copy_diag_report`.

**Command:** `animassist.p6_copy_diag_report`.

#### Clear Diagnostics

Clears the gap/cluster caches and resets the timing score stored on the scene. The Jump Next/Prev Gap operators become unavailable until the next Detect Gaps run.

**Help topic:** `op.animassist.p6_clear_diagnostics`.

**Command:** `animassist.p6_clear_diagnostics`.

#### Cluster Radius

A cluster of two or more keys within this radius is flagged as potential over-keying. Adjust to match the key density of your animation style  -  a lower value catches very tight clusters; a higher value is more lenient.

**Help topic:** `prop.p6_cluster_radius`.

### Timing Ranges

#### Set Range Start

Sets the Custom Start field to the current playhead position. Switch Range Mode to 'Custom' to make range-aware operators use this value.

**Help topic:** `op.animassist.p6_set_range_start`.

**Command:** `animassist.p6_set_range_start`. Declared as an undoable operation.

#### Set Range End

Sets the Custom End field to the current playhead position. Switch Range Mode to 'Custom' to make range-aware operators use this value.

**Help topic:** `op.animassist.p6_set_range_end`.

**Command:** `animassist.p6_set_range_end`. Declared as an undoable operation.

#### Select Keys in Range

Uses whichever Range Mode is currently active (From Selection, Scene Range, or Custom). Combines naturally with Scale Range and Offset Range for surgical edits on a specific time window.

**Help topic:** `op.animassist.p6_select_keys_in_range`.

**Command:** `animassist.p6_select_keys_in_range`. Declared as an undoable operation.

#### Scale Range

Identical to Scale Keys but with an implicit frame_range filter applied. Keys outside the active range are completely unaffected.

**Help topic:** `op.animassist.p6_scale_range`.

**Command:** `animassist.p6_scale_range`. Declared as an undoable operation.

#### Offset Range

Identical to Offset Keys but with an implicit frame_range filter applied. Keys outside the active range are completely unaffected.

**Help topic:** `op.animassist.p6_offset_range`.

**Command:** `animassist.p6_offset_range`. Declared as an undoable operation.

#### Store Range

The stored range survives file save and reload. Use Restore Range to recall it. Only one preset is stored at a time; calling Store Range again replaces the previous one.

**Help topic:** `op.animassist.p6_store_range`.

**Command:** `animassist.p6_store_range`. Declared as an undoable operation.

#### Restore Range

Only available after Store Range has been called at least once on this scene. The Range Mode is automatically switched to Custom so the restored values take effect immediately.

**Help topic:** `op.animassist.p6_restore_range`.

**Command:** `animassist.p6_restore_range`. Declared as an undoable operation.

#### Clear Range

Also clears the stored range preset flag. After this operation Restore Range becomes unavailable until Store Range is called again.

**Help topic:** `op.animassist.p6_clear_range`.

**Command:** `animassist.p6_clear_range`. Declared as an undoable operation.

#### Range Mode

From Selection  -  derives the range from the frame extents of currently selected keyframes. Scene Range  -  uses the scene's frame_start and frame_end. Custom  -  uses the manually entered Start and End values. All range-aware operators (Scale Range, Offset Range, Distribute Keys, etc.) respect this setting.

**Help topic:** `prop.p6_range_mode`.

## Reference A7. Temporary controls, proxies and baking

**Find this workflow:** Properties > Scene > Anim Assist > Rig; bake shortcuts also appear under the animation editors' Pose & Rig / Mirror & Match groups.

### Bake Workflows

#### Bake Range

Uses the Bake Range Mode (Scene, Action, Custom, Selection, or Preview) to determine start and end frames, then bakes the active object's evaluated transform within that range.

**Help topic:** `op.animassist.p7_bake_range`.

**Command:** `animassist.p7_bake_range`. Declared as an undoable operation.

#### Bake Preview Range

Uses the scene's preview range (frame_preview_start/end) as the bake range. Only available when Use Preview Range is enabled.

**Help topic:** `op.animassist.p7_bake_preview`.

**Command:** `animassist.p7_bake_preview`. Declared as an undoable operation.

#### Bake Selected Channels

Determines which transform channels already have animation and bakes only those, leaving un-keyed channels untouched.

**Help topic:** `op.animassist.p7_bake_selected_channels`.

**Command:** `animassist.p7_bake_selected_channels`. Declared as an undoable operation.

#### Smart Bake

Performs a full-range bake then applies Ramer-Douglas-Peucker simplification to remove keys whose deletion causes less than the Smart Bake Tolerance deviation.

**Help topic:** `op.animassist.p7_smart_bake`.

**Command:** `animassist.p7_smart_bake`. Declared as an undoable operation.

#### Preserve Timing Bake

Only updates values at frames where keyframes already exist, preserving the animator's original timing decisions. Does not insert new keyframes.

**Help topic:** `op.animassist.p7_bake_preserve_timing`.

**Command:** `animassist.p7_bake_preserve_timing`. Declared as an undoable operation.

### Batch Proxy

#### Apply Offset

Reads the proxy's current offset from its target and applies it as an additive layer on the target's animation.

**Help topic:** `op.animassist.p7_apply_offset`.

**Command:** `animassist.p7_apply_offset`. Declared as an undoable operation.

#### Zero-Out Proxy

Sets the active proxy's location to (0,0,0), rotation to zero, and scale to (1,1,1). Useful as a quick reset before re-posing.

**Help topic:** `op.animassist.p7_zero_proxy`.

**Command:** `animassist.p7_zero_proxy`. Declared as an undoable operation.

#### Recenter Proxy

Reads the target's current world-space position and moves the proxy to match. Useful after the target has drifted or been manually adjusted.

**Help topic:** `op.animassist.p7_recenter_proxy`.

**Command:** `animassist.p7_recenter_proxy`. Declared as an undoable operation.

#### Temporary Pivot

Places a POLE-type empty at the 3D cursor with no constraint or owner. Acts as a general-purpose pivot point for manual workflows.

**Help topic:** `op.animassist.p7_temp_pivot`.

**Command:** `animassist.p7_temp_pivot`. Declared as an undoable operation.

#### Batch Create Proxies

For each selected object, creates a proxy of the configured type and adds the appropriate constraint. All proxies share one session.

**Help topic:** `op.animassist.p7_batch_create_proxies`.

**Command:** `animassist.p7_batch_create_proxies`. Declared as an undoable operation.

#### Auto Cleanup

Scans for P7-tagged objects not tracked by any active session and removes them automatically.

**Help topic:** `op.animassist.p7_auto_cleanup`.

**Command:** `animassist.p7_auto_cleanup`. Declared as an undoable operation.

#### Validate Session

Scans the session's artifact registry against the actual scene data and reports any mismatches: deleted objects, missing constraints, or unsupported configurations.

**Help topic:** `op.animassist.p7_validate_session`.

**Command:** `animassist.p7_validate_session`.

#### Check Setup

Examines the target object for pre-existing constraints or transform issues that may conflict with proxy operation.

**Help topic:** `op.animassist.p7_check_setup`.

**Command:** `animassist.p7_check_setup`.

#### Mirror Proxy

Duplicates the proxy and mirrors its position across the YZ plane. Uses L/R naming convention swap for the mirrored copy.

**Help topic:** `op.animassist.p7_mirror_proxy`.

**Command:** `animassist.p7_mirror_proxy`. Declared as an undoable operation.

### One-Click Workflows

#### One-Click Proxy & Bake

Creates a Translation proxy, bakes the constrained animation, then removes all session artifacts. Net result: baked animation with no lingering temporary objects.

**Help topic:** `op.animassist.p7_one_click_proxy_bake`.

**Command:** `animassist.p7_one_click_proxy_bake`. Declared as an undoable operation.

#### One-Click Cleanup

First bakes every constrained object in the session, then performs a full session cleanup.

**Help topic:** `op.animassist.p7_one_click_cleanup`.

**Command:** `animassist.p7_one_click_cleanup`. Declared as an undoable operation.

#### Quick Proxy

Shortcut that skips the proxy-type selection: creates a Translation Proxy with current defaults, auto-constrained to the active object.

**Help topic:** `op.animassist.p7_quick_proxy`.

**Command:** `animassist.p7_quick_proxy`. Declared as an undoable operation.

#### Export Session

Serializes the active session's full state to a JSON string and copies it to the system clipboard.

**Help topic:** `op.animassist.p7_export_session`.

**Command:** `animassist.p7_export_session`.

#### List Sessions

Reports session ID, stage, object count, and constraint count for every session in the Python-side registry.

**Help topic:** `op.animassist.p7_list_sessions`.

**Command:** `animassist.p7_list_sessions`.

### Proxy Cleanup

#### Cleanup Session

Rolls back the current session: removes constraints first (safe for rigs), then deletes proxy/locator objects, then removes empty collections.

**Help topic:** `op.animassist.p7_cleanup_session`.

**Command:** `animassist.p7_cleanup_session`. Declared as an undoable operation.

#### Cleanup All Sessions

Scans every object, pose bone, and collection for P7 tags and removes all matching artifacts. Use as a last-resort cleanup.

**Help topic:** `op.animassist.p7_cleanup_all`.

**Command:** `animassist.p7_cleanup_all`. Declared as an undoable operation.

### Proxy Constraints

#### Orientation Proxy

Creates a single-arrow empty and adds a Copy Rotation constraint from the target to the proxy. Animate the proxy's rotation to control the target's orientation indirectly.

**Help topic:** `op.animassist.p7_create_proxy.ORIENTATION`.

#### Translation Proxy

Creates a plain-axes empty and adds a Copy Location constraint. Animate the proxy to drive the target's position. Useful for space-switching or offset workflows.

**Help topic:** `op.animassist.p7_create_proxy.TRANSLATION`.

#### Aim Proxy

Creates a cone empty and adds a Track To constraint on the target aimed at the proxy. Move the proxy to control where the target looks.

**Help topic:** `op.animassist.p7_create_proxy.AIM`.

#### Pole Helper

Creates a sphere empty at the target's position with no automatic constraint. Position the helper to serve as an IK pole-target reference.

**Help topic:** `op.animassist.p7_create_proxy.POLE`.

#### Up-Vector Helper

Creates a single-arrow empty with no automatic constraint. Use it as the up-target in Track To or Damped Track setups to control the rolling axis.

**Help topic:** `op.animassist.p7_create_proxy.UP_VECTOR`.

#### Multi-Target Average

Creates a cube empty at the centroid of all selected objects. No automatic constraint is added; set up a Copy Location with multiple targets manually.

**Help topic:** `op.animassist.p7_create_proxy.MULTI_TARGET`.

#### Parent-Space Proxy

Creates a cube empty and adds a Child Of constraint. The target follows the proxy as if parented, and the constraint can be keyed on/off for dynamic parenting changes.

**Help topic:** `op.animassist.p7_create_proxy.PARENT_SPACE`.

#### World-Space Proxy

Creates an arrows empty and adds a Copy Transforms constraint. The proxy drives the target's full world-space transform.

**Help topic:** `op.animassist.p7_create_proxy.WORLD_SPACE`.

#### Camera-Space Proxy

Creates a camera-data empty with no auto constraint. Designed for manual constraint setups where influence is keyed between 0 and 1 to blend camera-relative motion over time.

**Help topic:** `op.animassist.p7_create_proxy.CAMERA_SPACE`.

### Proxy Display

#### Toggle Proxy Display

Cycles through the three display modes: Full (normal size and colour), Dimmed (reduced size and muted colour), Hidden (not visible in the viewport). Affects all proxies in the active session.

**Help topic:** `op.animassist.p7_toggle_display`.

**Command:** `animassist.p7_toggle_display`. Declared as an undoable operation.

#### Set Proxy Color

Reads the Proxy Color value from the temporarysettings and applies it to the active proxy object's display colour.

**Help topic:** `op.animassist.p7_set_proxy_color`.

**Command:** `animassist.p7_set_proxy_color`. Declared as an undoable operation.

#### Rename Proxy

Rebuilds the proxy object's name using the standard pattern: AA_P7_Proxy_<target>_<type>_<session>. Useful after the target object has been renamed.

**Help topic:** `op.animassist.p7_rename_proxy`.

**Command:** `animassist.p7_rename_proxy`. Declared as an undoable operation.

#### Toggle Collection

Shows or hides the session's AA_P7_Temp collection in the viewport. Useful for quickly decluttering the scene without changing individual proxy visibility.

**Help topic:** `op.animassist.p7_toggle_collection`.

**Command:** `animassist.p7_toggle_collection`. Declared as an undoable operation.

### Session Management

#### Reconnect Session

Detects orphaned P7 artifacts in the scene and rebuilds a session from them, restoring cleanup and management capabilities.

**Help topic:** `op.animassist.p7_reconnect_session`.

**Command:** `animassist.p7_reconnect_session`. Declared as an undoable operation.

#### Session Info

Displays session ID, stage, scene, number of tracked objects, constraints, and collections in the info area.

**Help topic:** `op.animassist.p7_show_session_info`.

**Command:** `animassist.p7_show_session_info`.

#### Mute/Unmute Constraints

Mutes or unmutes every constraint registered under the active session. Muted constraints are ignored during evaluation, letting you preview the original animation.

**Help topic:** `op.animassist.p7_mute_constraints`.

**Command:** `animassist.p7_mute_constraints`. Declared as an undoable operation.

#### Lock Original Target

Locks location, rotation, and scale on the original target object to prevent accidental edits while a proxy is driving it.

**Help topic:** `op.animassist.p7_lock_target`.

**Command:** `animassist.p7_lock_target`. Declared as an undoable operation.

#### Switch Proxy Mode

Switches the active proxy mode between Constrain (proxy replaces target motion) and Offset (proxy adds on top of existing motion).

**Help topic:** `op.animassist.p7_switch_proxy_mode`.

**Command:** `animassist.p7_switch_proxy_mode`. Declared as an undoable operation.

### Temp Locators

#### Create Locator

Adds a plain-axes empty snapped to the active object's world-space position (or the active bone's head if an armature bone is selected). The locator is tagged as a temporarytemporary artifact and tracked by the active session.

**Help topic:** `op.animassist.p7_create_locator`.

**Command:** `animassist.p7_create_locator`. Declared as an undoable operation.

#### Locator at Average

Computes the centroid of every selected object's world position and places a new locator empty there. Useful for finding the centre of a group of controls.

**Help topic:** `op.animassist.p7_create_locator_average`.

**Command:** `animassist.p7_create_locator_average`. Declared as an undoable operation.

#### Locator at Cursor

Places a new locator empty at the exact position of the 3D cursor. Allows manual placement independent of any selected object.

**Help topic:** `op.animassist.p7_create_locator_cursor`.

**Command:** `animassist.p7_create_locator_cursor`. Declared as an undoable operation.

#### Parent to Locator

Sets the locator as the active object's parent without affecting the object's world transform (uses Blender's 'keep transform' parent mode).

**Help topic:** `op.animassist.p7_parent_locator`.

**Command:** `animassist.p7_parent_locator`. Declared as an undoable operation.

#### Constrain Target  ->  Locator

Injects a Copy Location constraint on the active object (or active pose bone) with the locator as target. The constraint is named with the session prefix so it can be cleaned up on rollback.

**Help topic:** `op.animassist.p7_constrain_target_to_locator`.

**Command:** `animassist.p7_constrain_target_to_locator`. Declared as an undoable operation.

#### Constrain Locator  ->  Target

Injects a Copy Location constraint on the session's locator with the active object as target. The locator then follows the target.

**Help topic:** `op.animassist.p7_constrain_locator_to_target`.

**Command:** `animassist.p7_constrain_locator_to_target`. Declared as an undoable operation.

#### Bake Locator from Target

Iterates over the bake frame range, evaluating the active object's world matrix at each frame and inserting location keyframes on the target locator.

**Help topic:** `op.animassist.p7_bake_locator_from_target`.

**Command:** `animassist.p7_bake_locator_from_target`. Declared as an undoable operation.

#### Bake Target from Locator

Iterates over the bake frame range, sampling the locator's world position and inserting keyframes on the active object's location channels.

**Help topic:** `op.animassist.p7_bake_target_from_locator`.

**Command:** `animassist.p7_bake_target_from_locator`. Declared as an undoable operation.

#### Match Target  ->  Locator

Copies world-space location from the session locator to the active object at the current frame. No keyframe is inserted automatically.

**Help topic:** `op.animassist.p7_match_target_to_locator`.

**Command:** `animassist.p7_match_target_to_locator`. Declared as an undoable operation.

#### Match Locator  ->  Target

Reads the active object's world matrix at the current frame and sets the locator's location to match.

**Help topic:** `op.animassist.p7_match_locator_to_target`.

**Command:** `animassist.p7_match_locator_to_target`. Declared as an undoable operation.

## Reference A8. Matching and space switching

**Find this workflow:** Properties > Scene > Anim Assist > This Pose / Setup, Graph Editor > Pose & Rig, or Dope Sheet > Mirror & Match.

### Contact Preservation

#### Contact Preservation

When enabled, the compensation algorithm records contact-bone world positions and blends the result to keep those bones planted.  Reduces sliding on IK hands and feet during space switches.

**Help topic:** `prop.p8_contact_preserve`.

#### Contact Mask

Specify which bones should be considered contact points.  Typical values: foot_ik_L, foot_ik_R, hand_ik_L, hand_ik_R.  Use the 'Mask from Selection' button to populate from selected bones.

**Help topic:** `prop.p8_contact_mask`.

#### Contact-Preserving Match

Performs a standard match on the target but then adjusts the result so that contact-mask bones maintain their world positions.  Requires contact preservation to be enabled with at least one bone in the mask.

**Help topic:** `op.animassist.p8_contact_preserve_match`.

**Command:** `animassist.p8_contact_preserve_match`. Declared as an undoable operation.

#### Mask from Selection

In Pose mode, reads the names of all selected pose bones and writes them as a comma-separated list into the contact mask field.  Quick alternative to manually typing bone names.

**Help topic:** `op.animassist.p8_contact_mask_from_selection`.

**Command:** `animassist.p8_contact_mask_from_selection`. Declared as an undoable operation.

### Rig Detection

#### Detect Space Enums

Examines object-level and pose-bone custom properties whose names contain keywords like 'space', 'switch', 'parent', or 'follow'.  Results are ranked by confidence and cached for the panel list.

**Help topic:** `op.animassist.p8_detect_space_enums`.

**Command:** `animassist.p8_detect_space_enums`. Declared as an undoable operation.

#### Detect Parent Patterns

Looks for 0/1 custom properties on bones that suggest parent-space toggles (e.g. IK/FK switches, follow toggles).

**Help topic:** `op.animassist.p8_detect_parent_patterns`.

**Command:** `animassist.p8_detect_parent_patterns`. Declared as an undoable operation.

#### Detect Influence Patterns

Identifies Child Of, Copy Transforms, and similar constraints whose influence values may be used as space switches.  Scores higher when constraint names contain switch keywords.

**Help topic:** `op.animassist.p8_detect_influence_patterns`.

**Command:** `animassist.p8_detect_influence_patterns`. Declared as an undoable operation.

#### Detect Custom Properties

Catch-all detector that finds all numeric custom properties.  Lower confidence than specific detectors but ensures nothing is missed on custom rigs.

**Help topic:** `op.animassist.p8_detect_custom_props`.

**Command:** `animassist.p8_detect_custom_props`. Declared as an undoable operation.

#### Detect All Patterns

Combines enum, boolean, influence, and custom-property detection into a single pass.  Deduplicates results and ranks by confidence.  This is the recommended starting point for new rigs.

**Help topic:** `op.animassist.p8_detect_all`.

**Command:** `animassist.p8_detect_all`. Declared as an undoable operation.

#### Apply Detected Pattern

Copies the detected pattern's property path, bone name, and switch type into the matchingsettings so you can immediately use the compensation and switching tools with that pattern.

**Help topic:** `op.animassist.p8_apply_detected_pattern`.

**Command:** `animassist.p8_apply_detected_pattern`. Declared as an undoable operation.

#### Debug Diagnostics

Generates a comprehensive report including constraint types, driver count, custom property inventory, and bone hierarchy analysis.  Copies the report to the clipboard for sharing with TD support.

**Help topic:** `op.animassist.p8_debug_diagnostics`.

**Command:** `animassist.p8_debug_diagnostics`.

### Space Switching

#### Single-Frame Compensation

Records the control's visual world matrix, changes the specified switch property, forces a depsgraph update, then computes and applies the local transform that recovers the original visual result.  Optionally inserts keyframes on both the switch property and the compensated transform channels.

**Help topic:** `op.animassist.p8_compensate_single`.

**Command:** `animassist.p8_compensate_single`. Declared as an undoable operation.

#### Multi-Frame Compensation

Applies single-frame compensation at every frame in the selected range.  For each frame: moves playhead, records visual state, applies switch, updates depsgraph, compensates, and keys.  Restores the playhead to the original frame when done.

**Help topic:** `op.animassist.p8_compensate_multi`.

**Command:** `animassist.p8_compensate_multi`. Declared as an undoable operation.

#### Switch Enum Property

Changes a detected enum/integer switch property to a specified value and immediately compensates the transform to prevent visual popping.  The new value is passed as an operator property.

**Help topic:** `op.animassist.p8_switch_enum`.

**Command:** `animassist.p8_switch_enum`. Declared as an undoable operation.

- **Value** (`value`): Enum or integer value to set New-data default: .

#### Switch Boolean Property

Flips a boolean (0/1) custom property (typically a follow or IK/FK toggle) and compensates the visual transform.  Reads the current value and sets it to the opposite.

**Help topic:** `op.animassist.p8_switch_bool`.

**Command:** `animassist.p8_switch_bool`. Declared as an undoable operation.

#### Switch Influence Property

Changes a constraint's influence (0.0-1.0) and compensates the resulting transform change.  Useful for blending between constraint targets (e.g. Child Of, Copy Transforms).

**Help topic:** `op.animassist.p8_switch_influence`.

**Command:** `animassist.p8_switch_influence`. Declared as an undoable operation.

- **Influence** (`influence`): Influence value to set New-data default: 1.0. Allowed range: 0.0 to 1.0.

#### Restore Previous Switch

Reads the most recent switch event from history and reverses it by setting the property back to its old value, then compensates.  Acts like a targeted undo for the switch operation.

**Help topic:** `op.animassist.p8_restore_switch`.

**Command:** `animassist.p8_restore_switch`. Declared as an undoable operation.

#### Switch Preview Mode

When enabled, switch operations show a preview of the result without committing.  Disabling preview mode restores the original state.  Useful for testing different switch values.

**Help topic:** `op.animassist.p8_toggle_preview`.

**Command:** `animassist.p8_toggle_preview`. Declared as an undoable operation.

### Switch Baking

#### Bake Switch (Selected Range)

Identifies the frame range of selected keyframes, applies the switch property change, and bakes compensation at every frame in that range.  Produces clean animation across the transition.

**Help topic:** `op.animassist.p8_bake_switch_range`.

**Command:** `animassist.p8_bake_switch_range`. Declared as an undoable operation.

#### Bake Switch (Preview Range)

Uses the scene's preview range (or full scene range) and bakes compensation at every frame.  Ideal for processing an entire shot's worth of space-switch animation.

**Help topic:** `op.animassist.p8_bake_switch_preview`.

**Command:** `animassist.p8_bake_switch_preview`. Declared as an undoable operation.

#### Batch Switch

Iterates through every selected object, applies the configured switch property change, and compensates each one independently.  Handles per-target bone resolution when a bone name is specified.

**Help topic:** `op.animassist.p8_batch_switch`.

**Command:** `animassist.p8_batch_switch`. Declared as an undoable operation.

#### Switch Marker

Adds a named marker to the timeline at the playhead position.  Markers serve as visual reference points for where space switches occur in the animation.

**Help topic:** `op.animassist.p8_switch_marker`.

**Command:** `animassist.p8_switch_marker`. Declared as an undoable operation.

### Switch Compensation

#### Auto Compensate

When enabled, any switch operation automatically records the visual matrix beforehand and applies compensation afterward.  Disable this to perform raw switches without compensation.

**Help topic:** `prop.p8_auto_compensate`.

#### Auto-Key Compensated Channels

Automatically inserts keyframes on both the switch property and all compensated transform channels.  Requires Blender's auto-key to be independent of this setting  -  this controls only matchingswitch-specific keying.

**Help topic:** `prop.p8_auto_key_switch`.

#### Respect Locked Transforms

Prevents the match or compensation from overriding channels the animator has explicitly locked.  Locked axes are silently skipped rather than producing an error.

**Help topic:** `prop.p8_respect_locks`.

#### Respect Driven Channels

Avoids overwriting transform channels that are controlled by drivers.  Writing to driven channels can cause dependency cycles or unexpected behavior.

**Help topic:** `prop.p8_respect_drivers`.

#### Match Channels

Controls whether matching and compensation affect all channels, location only, rotation only, scale only, or location+rotation.  Combined with per-axis toggles for precise control.

**Help topic:** `prop.p8_match_channels`.

#### Axis Filter

Enable or disable individual axes for matching.  When used with the axis-filtered match operator, only checked axes are affected.  Useful for constraining a match to a single plane or axis.

**Help topic:** `prop.p8_match_axis`.

### Switch History

#### Next Switch Event

Finds the first recorded switch event after the current frame and moves the playhead there.  Skips forward through the timeline switch-by-switch.

**Help topic:** `op.animassist.p8_nav_next_switch`.

**Command:** `animassist.p8_nav_next_switch`. Declared as an undoable operation.

#### Previous Switch Event

Finds the last recorded switch event before the current frame and moves the playhead there.

**Help topic:** `op.animassist.p8_nav_prev_switch`.

**Command:** `animassist.p8_nav_prev_switch`. Declared as an undoable operation.

#### Clear Switch History

Wipes the ephemeral switch history.  This cannot be undone.  History is session-only and does not survive file save/reload.

**Help topic:** `op.animassist.p8_clear_history`.

**Command:** `animassist.p8_clear_history`. Declared as an undoable operation.

#### Repeat Last Switch

Reads the last switch event from history and performs the same property change with compensation at the current playhead frame.  Useful for applying the same space switch at different frames.

**Help topic:** `op.animassist.p8_repeat_last_switch`.

**Command:** `animassist.p8_repeat_last_switch`. Declared as an undoable operation.

### Switch Presets

#### Save Switch Preset

Stores the current property path, bone name, switch type, and default value as a named preset on the scene.  Presets persist with the .blend file and can be shared between shots.

**Help topic:** `op.animassist.p8_save_switch_preset`.

**Command:** `animassist.p8_save_switch_preset`. Declared as an undoable operation.

#### Load Switch Preset

Applies the stored property path, bone name, switch type, and default value from the named preset back into the matchingsettings panel.

**Help topic:** `op.animassist.p8_load_switch_preset`.

**Command:** `animassist.p8_load_switch_preset`. Declared as an undoable operation.

- **Preset Name** (`preset_name`): Name of the preset to load New-data default: empty.

#### Delete Switch Preset

Permanently deletes the named preset from the scene's stored presets.  This cannot be undone.

**Help topic:** `op.animassist.p8_delete_switch_preset`.

**Command:** `animassist.p8_delete_switch_preset`. Declared as an undoable operation.

- **Preset Name** (`preset_name`): Name of the preset to delete New-data default: empty.

#### Compensation Report

Summarizes all switch events in the history stack, listing frames, properties changed, old and new values, and channels compensated.  Copies the report to the clipboard.

**Help topic:** `op.animassist.p8_compensation_report`.

**Command:** `animassist.p8_compensation_report`.

#### Unsupported Setup Check

Scans for potential issues: missing animation data, complex constraint stacks, drivers on transform channels, and locked transforms.  Reports warnings so the user can work around them.

**Help topic:** `op.animassist.p8_unsupported_warning`.

**Command:** `animassist.p8_unsupported_warning`.

### Transform Matching

#### Match to World

Resets the active control so its visual world-space transform matches the scene origin (identity matrix).  Useful for zeroing out a control relative to world space.  Respects channel filters and lock settings.

**Help topic:** `op.animassist.p8_match_to_world`.

**Command:** `animassist.p8_match_to_world`. Declared as an undoable operation.

#### Match to Parent

Sets the active control's local transform to identity so it sits exactly at its parent's position and orientation.  Equivalent to zeroing the local offset.

**Help topic:** `op.animassist.p8_match_to_parent`.

**Command:** `animassist.p8_match_to_parent`. Declared as an undoable operation.

**Prerequisite messages:** Select an object with a parent to match its parent's transform.

#### Match to Target

Snaps the active object's visual transform to match the other selected object's world-space pose.  Requires exactly two objects selected: the active is the target, the other is the source.

**Help topic:** `op.animassist.p8_match_to_target`.

**Command:** `animassist.p8_match_to_target`. Declared as an undoable operation.

**Prerequisite messages:** Select a target, then the object to match.

#### Match Selected to Active

Batch-matches every selected object (except the active) so they all share the active object's visual world-space pose.  Useful for snapping multiple controls to one reference.

**Help topic:** `op.animassist.p8_match_selected_to_active`.

**Command:** `animassist.p8_match_selected_to_active`. Declared as an undoable operation.

**Prerequisite messages:** Select a target, then the object to match.

#### Visual Transform Match

Performs the match using the depsgraph-evaluated visual matrix, which accounts for all constraints, drivers, and modifiers.  This is the most accurate match mode for constrained rigs.

**Help topic:** `op.animassist.p8_visual_match`.

**Command:** `animassist.p8_visual_match`. Declared as an undoable operation.

#### Location Match

Matches only the position (XYZ location) of the target to the source, leaving rotation and scale unchanged.  Respects per-axis filtering and transform locks.

**Help topic:** `op.animassist.p8_match_location`.

**Command:** `animassist.p8_match_location`. Declared as an undoable operation.

**Prerequisite messages:** Select a target, then the object to match.

#### Rotation Match

Matches only the orientation (Euler rotation) of the target to the source, leaving location and scale unchanged.

**Help topic:** `op.animassist.p8_match_rotation`.

**Command:** `animassist.p8_match_rotation`. Declared as an undoable operation.

**Prerequisite messages:** Select a target, then the object to match.

#### Scale Match

Matches only the scale of the target to the source, leaving location and rotation unchanged.

**Help topic:** `op.animassist.p8_match_scale`.

**Command:** `animassist.p8_match_scale`. Declared as an undoable operation.

**Prerequisite messages:** Select a target, then the object to match.

#### Full TRS Match

Performs a complete transform match covering all channels.  This is the default match mode that snaps the target to the source across all axes and all transform types.

**Help topic:** `op.animassist.p8_match_trs`.

**Command:** `animassist.p8_match_trs`. Declared as an undoable operation.

**Prerequisite messages:** Select a target, then the object to match.

#### Axis-Filtered Match

Uses the X/Y/Z axis checkboxes in the panel to selectively match only certain axes.  Combined with the channel mode, this gives fine-grained control over which components are affected.

**Help topic:** `op.animassist.p8_match_axis_filtered`.

**Command:** `animassist.p8_match_axis_filtered`. Declared as an undoable operation.

**Prerequisite messages:** Select a target, then the object to match.

#### Match with Offset

Computes the match but preserves the original offset between the source and target.  Useful when you want to maintain relative positioning while updating the match relationship.

**Help topic:** `op.animassist.p8_match_with_offset`.

**Command:** `animassist.p8_match_with_offset`. Declared as an undoable operation.

**Prerequisite messages:** Select a target, then the object to match.

#### Match without Offset

Forces an exact snap to the source transform with zero offset, regardless of the Maintain Offset checkbox state.  Use this for a one-shot precise alignment.

**Help topic:** `op.animassist.p8_match_without_offset`.

**Command:** `animassist.p8_match_without_offset`. Declared as an undoable operation.

**Prerequisite messages:** Select a target, then the object to match.

#### Quick Match

Performs a full TRS visual match from the source to the active object using default channel settings.  Auto-keys if the auto-key option is enabled.  The fastest way to snap-match two objects.

**Help topic:** `op.animassist.p8_quick_match`.

**Command:** `animassist.p8_quick_match`. Declared as an undoable operation.

#### Match Visual Matrix

Explicitly uses the evaluated depsgraph for both source and target matrices.  Accounts for all constraints and drivers in the rig hierarchy.  This is the most accurate match mode.

**Help topic:** `op.animassist.p8_match_visual_matrix`.

**Command:** `animassist.p8_match_visual_matrix`. Declared as an undoable operation.

**Prerequisite messages:** Select a target, then the object to match.

#### Match Local Matrix

Uses the source object's local matrix (pre-constraint) as the match target.  Useful when you want to match the authored transform rather than the visual result.

**Help topic:** `op.animassist.p8_match_local_matrix`.

**Command:** `animassist.p8_match_local_matrix`. Declared as an undoable operation.

**Prerequisite messages:** Select a target, then the object to match.

#### Match Opposite Side

Finds the opposite-side bone by mirror-naming convention (L to R, Left to Right) and matches the active bone to it.  Only available in Pose mode with a valid mirror naming pattern.

**Help topic:** `op.animassist.p8_match_opposite`.

**Command:** `animassist.p8_match_opposite`. Declared as an undoable operation.

## Reference A9. Mirroring and pair management

**Find this workflow:** Properties > Scene > Anim Assist > This Pose / Setup, Graph Editor > Pose & Rig, or Dope Sheet > Mirror & Match.

### Batch Mirror

#### Batch Mirror

Iterates through every selected bone, finds its opposite, and applies mirroring.  Unselected bones are unaffected.  Respects axis mask and transform space settings.

**Help topic:** `op.animassist.p9_batch_mirror`.

**Command:** `animassist.p9_batch_mirror`. Declared as an undoable operation.

#### Mirror Active Side

Determines whether the active bone is on the left or right side, then mirrors all bones on that same side to the opposite.  Useful for mirroring an entire limb at once.

**Help topic:** `op.animassist.p9_batch_mirror_active_side`.

**Command:** `animassist.p9_batch_mirror_active_side`. Declared as an undoable operation.

#### Channel Resolver

Analyzes which channels (Loc X/Y/Z, Rot X/Y/Z, Scale X/Y/Z) exist on opposite bones and determines how to map them correctly.  Handles rigs with selective channel visibility.

**Help topic:** `op.animassist.p9_channel_resolver`.

**Command:** `animassist.p9_channel_resolver`.

#### Mirror Metadata

Copies custom properties, marker data, or other metadata from the active bone to its opposite.  Preserves secondary data during mirroring operations.

**Help topic:** `op.animassist.p9_mirror_metadata`.

**Command:** `animassist.p9_mirror_metadata`. Declared as an undoable operation.

#### Mirror Preset Values

For bones with stored preset transforms, mirrors the preset values to the opposite side.  Useful for syncing rest poses or animation templates.

**Help topic:** `op.animassist.p9_mirror_preset_values`.

**Command:** `animassist.p9_mirror_preset_values`. Declared as an undoable operation.

#### Repeat Last Mirror

Re-applies the last mirror operation (same settings, scope, and space) to the current selection.  Useful for applying the same mirror multiple times.

**Help topic:** `op.animassist.p9_repeat_mirror`.

**Command:** `animassist.p9_repeat_mirror`. Declared as an undoable operation.

### Mirror Diagnostics

#### Mirror Report

After a mirror operation, generates a detailed report listing each bone, its opposite, the transform values applied, and any warnings.  Copies the report to the clipboard.

**Help topic:** `op.animassist.p9_mirror_report`.

**Command:** `animassist.p9_mirror_report`.

#### Missing Opposite

Alerts when a selected or mirrored bone has no known opposite.  Provides suggestions for fixing the naming or adding a manual override.

**Help topic:** `op.animassist.p9_missing_warning`.

**Command:** `animassist.p9_missing_warning`.

#### Ambiguous Pair

Alerts when a bone's naming pattern matches multiple candidates on the opposite side.  Suggests resolving ambiguity via manual overrides.

**Help topic:** `op.animassist.p9_ambiguous_warning`.

**Command:** `animassist.p9_ambiguous_warning`.

### Mirror Scope

#### Axis Mask

Checkboxes for X, Y, and Z axes.  When unchecked, that axis is skipped during mirroring.  Combines with channel mode to give fine-grained control over which components are affected.

**Help topic:** `p9_axis_mask`.

#### Naming Exceptions

Opens a UI table where you can manually specify which bones pair with which, overriding automatic detection.  Useful for rigs with naming inconsistencies or special cases.

**Help topic:** `op.animassist.p9_naming_exceptions`.

#### Mirror Frame

Applies mirroring only to the playhead's current frame.  No keyframes are inserted unless auto-key is enabled.  Useful for tweaking a single frame.

**Help topic:** `op.animassist.p9_mirror_frame`.

**Command:** `animassist.p9_mirror_frame`. Declared as an undoable operation.

#### Mirror Range

Identifies the frame range of all selected keyframes and applies mirroring at every frame in that range.  Produces a symmetric animation across the selection.

**Help topic:** `op.animassist.p9_mirror_range`.

**Command:** `animassist.p9_mirror_range`. Declared as an undoable operation.

- **Start Frame** (`start_frame`): First frame of range to mirror New-data default: 1. Allowed range: 0 to no explicit upper limit.

- **End Frame** (`end_frame`): Last frame of range to mirror New-data default: 100. Allowed range: 0 to no explicit upper limit.

#### Mirror Preview Range

Uses the scene's preview/playback range (or the full frame range if no preview is set) and mirrors at every frame.  Ideal for processing an entire shot.

**Help topic:** `op.animassist.p9_mirror_preview`.

**Command:** `animassist.p9_mirror_preview`. Declared as an undoable operation.

#### Mirror Keyed Only

When enabled, the mirror operation skips frames where a channel has no keyframe.  Prevents creating unintended new animation on non-keyed channels.

**Help topic:** `op.animassist.p9_mirror_keyed_only`.

**Command:** `animassist.p9_mirror_keyed_only`. Declared as an undoable operation.

#### Mirror Visible Only

Respects Blender's channel hide/show toggles in the Graph Editor or Dopesheet.  Hidden channels are not mirrored.

**Help topic:** `op.animassist.p9_mirror_visible_only`.

**Command:** `animassist.p9_mirror_visible_only`. Declared as an undoable operation.

### Mirror Space

#### Local Space Mirror

Performs mirroring in the local space of each bone (relative to its parent).  This is the default for FK rigs and typical animation workflows.

**Help topic:** `p9_mirror_local`.

#### World Space Mirror

Performs mirroring in world space, ignoring the bone hierarchy.  Useful for root-level controls or when you want absolute positioning.

**Help topic:** `p9_mirror_world`.

#### Visual Mirror

Uses the depsgraph-evaluated visual matrices that account for all constraints and drivers.  The most accurate option for complex rigs with heavy constraints.

**Help topic:** `op.animassist.p9_visual_mirror`.

**Command:** `animassist.p9_visual_mirror`. Declared as an undoable operation.

#### Mirror With Offset

Computes the mirror but preserves any existing offset between the active and opposite bones.  Useful when you want to maintain a deliberate asymmetry.

**Help topic:** `op.animassist.p9_mirror_with_offset`.

**Command:** `animassist.p9_mirror_with_offset`. Declared as an undoable operation.

#### Mirror Without Offset

Forces an exact mirror with zero offset, overriding any existing asymmetry.  Use for a clean symmetric result.

**Help topic:** `op.animassist.p9_mirror_without_offset`.

**Command:** `animassist.p9_mirror_without_offset`. Declared as an undoable operation.

### Mirror Transforms

#### Match to Opposite

Copies the transform values from the opposite-side bone to the active bone, including any mirroring of rotation axes if needed.  Does not affect keyframes, only changes the current pose.

**Help topic:** `op.animassist.p9_match_to_opposite`.

**Command:** `animassist.p9_match_to_opposite`. Declared as an undoable operation.

#### Match Opposite to Active

Copies the transform values from the active bone to its opposite, with automatic axis flipping for rotation.  Useful for creating symmetric poses by starting with one side.

**Help topic:** `op.animassist.p9_match_opposite_to_active`.

**Command:** `animassist.p9_match_opposite_to_active`. Declared as an undoable operation.

#### Mirror Pose

Applies mirroring to all bones in the armature that have a known opposite pair.  Bones without pairs are left unchanged.  Respects the current axis mask and transform space settings.

**Help topic:** `op.animassist.p9_mirror_pose`.

**Command:** `animassist.p9_mirror_pose`. Declared as an undoable operation.

#### Mirror Selected

Iterates through selected bones, finds their opposites, and applies mirroring.  Unselected bones are unaffected.  Useful for mirroring only part of the pose.

**Help topic:** `op.animassist.p9_mirror_selected`.

**Command:** `animassist.p9_mirror_selected`. Declared as an undoable operation.

#### Mirror Location

Mirrors only the position (XYZ location) across the pair axis, leaving rotation and scale unchanged.  Respects per-axis filtering.

**Help topic:** `op.animassist.p9_mirror_location`.

**Command:** `animassist.p9_mirror_location`. Declared as an undoable operation.

#### Mirror Rotation

Mirrors only the rotation (Euler angles) by flipping the side axes and negating them if needed, leaving location and scale unchanged.

**Help topic:** `op.animassist.p9_mirror_rotation`.

**Command:** `animassist.p9_mirror_rotation`. Declared as an undoable operation.

#### Mirror Scale

Mirrors only the scale, typically by negating the side axis.  Location and rotation are left unchanged.  Less common than location and rotation mirroring.

**Help topic:** `op.animassist.p9_mirror_scale`.

**Command:** `animassist.p9_mirror_scale`. Declared as an undoable operation.

### Opposite Selection

#### Select Opposite

Deselects all bones and selects only the opposite-side pair of the currently active bone.  Requires a valid pair cache.  Useful for switching focus between left and right sides.

**Help topic:** `op.animassist.p9_select_opposite`.

**Command:** `animassist.p9_select_opposite`. Declared as an undoable operation.

#### Add Opposite

For each selected bone with a known opposite, adds that opposite to the selection (multi-select).  Keeps existing selections intact.  Useful for creating symmetric selections.

**Help topic:** `op.animassist.p9_add_opposite`.

**Command:** `animassist.p9_add_opposite`. Declared as an undoable operation.

#### Swap Selection

Exchanges the active bone with its opposite-side pair.  All other selections remain unchanged.  The opposite becomes the new active and active becomes a regular selection.

**Help topic:** `op.animassist.p9_swap_selection`.

**Command:** `animassist.p9_swap_selection`. Declared as an undoable operation.

### Pair Detection

#### Detect .L/.R

Scans the armature for bones whose names end in .L or .R and builds a mapping of opposite sides.  Case-sensitive.  Useful for rigs following Blender's standard naming convention.

**Help topic:** `op.animassist.p9_detect_dot_lr`.

#### Detect _L/_R

Scans the armature for bones whose names end in _L or _R and builds a mapping of opposite sides.  Case-sensitive.  Common in many production rigs.

**Help topic:** `op.animassist.p9_detect_under_lr`.

#### Detect Left/Right

Scans for bones containing the words 'Left' or 'Right' and builds a reverse mapping.  Case-insensitive.  Supports variations like 'Arm_Left' or 'LeftFinger'.

**Help topic:** `op.animassist.p9_detect_word_lr`.

#### Custom Pattern

Opens a dialog to specify a regex pattern or custom naming rule for detecting bone pairs.  Allows flexibility for non-standard naming conventions specific to your rig.

**Help topic:** `op.animassist.p9_custom_pattern`.

**Command:** `animassist.p9_custom_pattern`. Declared as an undoable operation.

#### Build Pair Cache

Runs a pair-detection pass using the currently selected pattern and stores the mapping in memory.  This cache is used by all mirror operations to look up opposite-side bones.

**Help topic:** `op.animassist.p9_build_cache`.

**Command:** `animassist.p9_build_cache`.

### Pair Management

#### Swap L/R Poses

Exchanges the transforms of every left-right bone pair, including location, rotation, and scale.  Useful for compositing or reference work.

**Help topic:** `op.animassist.p9_swap_poses`.

**Command:** `animassist.p9_swap_poses`. Declared as an undoable operation.

#### Pair Manager

Opens a dedicated panel where you can view, edit, add, and delete bone pair overrides.  Provides a centralized interface for all pair-related settings.

**Help topic:** `op.animassist.p9_pair_manager`.

#### Add Pair Override

Manually specify that bone A pairs with bone B, overriding automatic detection.  Useful for rigs with irregular naming or non-standard symmetry.

**Help topic:** `op.animassist.p9_add_pair_override`.

**Command:** `animassist.p9_add_pair_override`.

#### Save Pair Preset

Stores the current pair detection settings and any manual overrides as a named preset on the scene.  Presets persist with the .blend and speed up setup for new shots.

**Help topic:** `op.animassist.p9_save_pair_preset`.

**Command:** `animassist.p9_save_pair_preset`. Declared as an undoable operation.

#### Mirror Switch Targets

On the active bone, finds a constraint pointing to a target and repoints it to the opposite-side target.  Useful for swapping IK targets between limbs.

**Help topic:** `op.animassist.p9_mirror_switch_targets`.

**Command:** `animassist.p9_mirror_switch_targets`.

#### Mirror Proxy Helpers

Clones proxy/helper bone setups from one side to the other, adjusting names and parent relationships appropriately.

**Help topic:** `op.animassist.p9_mirror_proxy_helpers`.

**Command:** `animassist.p9_mirror_proxy_helpers`.

#### Mirror Selection Sets

Takes a selection set on one side (e.g., 'Arm_L_All') and creates a mirrored version on the opposite side (e.g., 'Arm_R_All').

**Help topic:** `op.animassist.p9_mirror_selection_sets`.

**Command:** `animassist.p9_mirror_selection_sets`.

#### Next Unpaired

Moves the selection to the next bone that could not be paired.  Useful for systematically fixing naming issues in the rig.

**Help topic:** `op.animassist.p9_nav_next_unpaired`.

**Command:** `animassist.p9_nav_next_unpaired`.

#### Validate Pairs

Generates a report listing bones without pairs, bones with multiple possible pairs, and inconsistencies.  Helps identify rig naming problems.

**Help topic:** `op.animassist.p9_validate_pairs`.

**Command:** `animassist.p9_validate_pairs`.

## Reference A10. Shelf, macros, batches and recovery

**Find this workflow:** Graph Editor > Quick Shelf, Dope Sheet > Shelf & Macros, or Properties > Scene > Anim Assist > Setup / Settings / Help & Diagnostics.

### Audit Trail

#### Transaction History

Displays a timeline of every operator, macro, and batch operation run in the session.  Click to jump to that point in history or re-execute.

**Help topic:** `op.animassist.p10_transaction_history`.

#### Operation Audit

For each logged operation, shows input parameters, target bones, affected frames, and result summary.  Useful for understanding what happened.

**Help topic:** `op.animassist.p10_operation_audit`.

#### Error Log

Collects and displays all errors, warnings, and info messages generated by operations.  Helps debug issues and understand why an operation failed.

**Help topic:** `op.animassist.p10_error_log`.

### Batch Processing

#### Selected Targets

Applies an operator (e.g., Bake, Simplify, Clean Keys) to every item in the current selection.  Saves time when processing multiple targets at once.

**Help topic:** `op.animassist.p10_batch_selected_targets`.

#### Bookmarked Channels

Applies an operation to a pre-defined set of channels across multiple bones.  Useful for processing a consistent set of properties on every rig.

**Help topic:** `op.animassist.p10_batch_bookmarked_channels`.

#### Frame Steps

Runs an operation every N frames across a time range.  Useful for adding keys, baking, or processing at consistent intervals without manual stepping.

**Help topic:** `op.animassist.p10_batch_frame_steps`.

**Command:** `animassist.p10_batch_frame_steps`. Declared as an undoable operation.

- **Operator ID** (`op_id`): Operator bl_idname to run at each frame step New-data default: empty.

### Diagnostics

#### System Diagnostics

Runs checks on available memory, GPU support, plugin load state, and Blender version compatibility.  Generates a report of potential issues.

**Help topic:** `op.animassist.p10_system_diagnostics`.

**Command:** `animassist.p10_system_diagnostics`.

#### Leak Checker

Inspects registered handlers, callbacks, and persistent data to find unreleased resources.  Reports orphaned objects that should be cleaned.

**Help topic:** `op.animassist.p10_leak_checker`.

#### Stale Cleanup

Deletes expired snapshots, unused presets, and orphaned cached data.  Frees memory and keeps the addon lightweight.

**Help topic:** `op.animassist.p10_stale_cleanup`.

**Command:** `animassist.p10_stale_cleanup`. Declared as an undoable operation.

#### Metadata Cleanup

Scans the armature for corrupted or inconsistent custom properties.  Repairs or removes invalid metadata.  Prevents crashes from bad data.

**Help topic:** `op.animassist.p10_metadata_cleanup`.

**Command:** `animassist.p10_metadata_cleanup`. Declared as an undoable operation.

#### Rebuild Caches

Clears and rebuilds the pair cache, tool lookup table, and other internal caches.  Use if you suspect stale data after editing the rig.

**Help topic:** `op.animassist.p10_rebuild_caches`.

**Command:** `animassist.p10_rebuild_caches`. Declared as an undoable operation.

#### Reset UI

Restores the default shelf and pie menus.  Clears custom buttons and favorites.  Useful if the UI becomes unusable.

**Help topic:** `op.animassist.p10_reset_ui`.

**Command:** `animassist.p10_reset_ui`. Declared as an undoable operation.

### Help & Debug

#### Tooltip / Help Link

Hover over any operator or UI element to see a tooltip.  Click the help icon to open the full documentation page in a browser.

**Help topic:** `op.animassist.p10_tooltip_help`.

#### Debug Toggle

Switches the addon into debug mode, printing detailed logs to the console.  Useful for troubleshooting or reporting bugs.

**Help topic:** `op.animassist.p10_debug_toggle`.

#### Final Validation

Scans the current file for common issues (missing targets, broken constraints, etc.) before saving.  Prevents corrupted saves.

**Help topic:** `op.animassist.p10_final_validation`.

**Command:** `animassist.p10_final_validation`.

### Macro Operations

#### Breakdown + Offset

A single operation that applies a breakdown frame at the playhead and then offsets it by a configurable amount.  Useful for quick timing tweaks.

**Help topic:** `op.animassist.p10_macro_breakdown_offset`.

**Command:** `animassist.p10_macro_breakdown_offset`. Declared as an undoable operation.

#### Proxy Workflow

Automatically creates and configures proxy bones, parent constraints, and visibility toggles for the selected control.  Streamlines IK/FK proxy setup.

**Help topic:** `op.animassist.p10_macro_proxy_workflow`.

**Command:** `animassist.p10_macro_proxy_workflow`. Declared as an undoable operation.

#### Switch + Compensate

Toggles an IK/FK constraint and automatically adjusts the opposite chain to match current position, eliminating pops.  One-click seamless switching.

**Help topic:** `op.animassist.p10_macro_switch_compensate`.

**Command:** `animassist.p10_macro_switch_compensate`. Declared as an undoable operation.

#### Diagnose + Jump

Scans the timeline for frames with warnings (gimbal lock, popping, etc.) and jumps the playhead to the next one.  Guides you through problem areas.

**Help topic:** `op.animassist.p10_macro_diagnose_jump`.

**Command:** `animassist.p10_macro_diagnose_jump`. Declared as an undoable operation.

#### Mirror + Match

Mirrors one side to the opposite while preserving any intentional asymmetry or offset.  Creates mirrored poses without losing character.

**Help topic:** `op.animassist.p10_macro_mirror_match`.

**Command:** `animassist.p10_macro_mirror_match`. Declared as an undoable operation.

### Pie Menus

#### Key Tools Pie

Pie menu (RMB or hotkey) with Insert Keyframe, Delete Keyframe, Clear Keyframe, and other key operations arranged in 8 directions.  Fast access without submenus.

**Help topic:** `op.animassist.p10_pie_key_tools`.

**Command:** `animassist.p10_pie_key_tools`.

#### Breakdown Pie

Pie menu with Breakdown, Offset, Retime, and related tools.  Useful for spacing and timing adjustments in the middle of your animation.

**Help topic:** `op.animassist.p10_pie_breakdown`.

**Command:** `animassist.p10_pie_breakdown`.

#### Transform Pie

Pie menu with Move, Rotate, Scale, and space toggles (Local/World/Normal).  Quick switching between transform modes without leaving the pie.

**Help topic:** `op.animassist.p10_pie_transform`.

**Command:** `animassist.p10_pie_transform`.

#### Proxy Pie

Pie menu with Toggle IK/FK, Switch Target, Mirror Targets, and proxy helper controls.  Streamlines constraint and proxy workflows.

**Help topic:** `op.animassist.p10_pie_proxy`.

**Command:** `animassist.p10_pie_proxy`.

#### Switch Pie

Pie menu with Object/Edit/Pose mode toggles, shape-key or driver switches, and other mode-based operations.  One-click context switching.

**Help topic:** `op.animassist.p10_pie_switch`.

**Command:** `animassist.p10_pie_switch`.

#### Symmetry Pie

Pie menu with Mirror Pose, Mirror Selected, Swap Poses, and axis toggles.  Fastest way to access your mirror settings.

**Help topic:** `op.animassist.p10_pie_symmetry`.

**Command:** `animassist.p10_pie_symmetry`.

### Presets

#### Preset Browser

Opens a file browser showing saved presets for operators.  Select and apply a preset to instantly configure an operator with pre-tuned settings.

**Help topic:** `op.animassist.p10_preset_browser`.

#### Tagging

Organize presets with user-defined tags (e.g., 'Walk', 'Run', 'Idle').  Filter and search presets by tag for faster discovery.

**Help topic:** `op.animassist.p10_preset_tagging`.

#### Export / Import

Export presets to a file for sharing or backup.  Import presets from files to add them to your library.  Facilitates team workflows.

**Help topic:** `op.animassist.p10_preset_export_import`.

#### Workspace Profiles

Captures the current shelf, pie menus, hotkeys, and preferences.  Swap between different profiles for different tasks (e.g., FK vs. IK focus).

**Help topic:** `op.animassist.p10_workspace_profiles`.

### Quick Shelf

#### Quick Shelf

Displays a horizontal or vertical toolbar with pinned operators and macros.  Customizable buttons for instant access to your favorite tools.  Reduces clicks and speeds up workflow.

**Help topic:** `op.animassist.p10_quick_shelf`.

#### Compact Mode

Hides labels and shows only icons on shelf buttons.  Saves screen space while maintaining visual recognition.  Useful on smaller monitors or crowded UI layouts.

**Help topic:** `op.animassist.p10_shelf_compact_mode`.

#### Expanded Mode

Shows both icon and label text on every shelf button.  Clearer for discovery and onboarding.  Takes more space but improves readability.

**Help topic:** `op.animassist.p10_shelf_expanded_mode`.

#### Context-Sensitive

The shelf adapts to show relevant tools depending on the active object type, mode, or selection.  For example, rigging tools appear when an armature is selected.

**Help topic:** `op.animassist.p10_context_sensitive_shelf`.

#### Favorites

Opens a menu to select operators and macros to add as shelf buttons.  Star-mark your most-used tools.  Favorites are saved per-project or globally.

**Help topic:** `op.animassist.p10_shelf_favorites`.

#### Shelf Filter

Type to search shelf buttons by name, category, or shortcut.  Reduces visual clutter and helps locate tools in large shelves.  Filter state persists during the session.

**Help topic:** `op.animassist.p10_shelf_filter`.

### Recovery

#### Snapshot

Records the current pose, keyframes, and rig configuration to an in-memory snapshot.  Use before risky operations.  Multiple snapshots can be stored.

**Help topic:** `op.animassist.p10_snapshot`.

#### Restore

Revert the armature (pose, keys, properties) to a previously-saved snapshot.  Useful for undoing complex multi-step operations or recovering from mistakes.

**Help topic:** `op.animassist.p10_restore`.

### Setup & Validation

#### Safe Disable

Saves state and configuration, then disables the addon.  Re-enabling restores everything.  Prevents corruption or lost settings.

**Help topic:** `op.animassist.p10_safe_disable`.

**Command:** `animassist.p10_safe_disable`.

#### Hotkey Conflicts

Scans for overlapping keybindings with other addons or Blender defaults.  Suggests remapping or disabling conflicting keys.

**Help topic:** `op.animassist.p10_hotkey_conflicts`.

#### First-Run Setup

Wizard to configure basic preferences, create default presets, and populate the shelf.  Customizes the addon for the user's workflow.

**Help topic:** `op.animassist.p10_first_run_setup`.

**Command:** `animassist.p10_first_run_setup`. Declared as an undoable operation.

#### Demo Config

Applies a pre-built shelf, pie menus, and hotkeys designed for learning.  Resets to sensible defaults for new users.

**Help topic:** `op.animassist.p10_demo_config`.

### Tool Access

#### Quick Search

Opens a search dialog (like Blender's F3 menu) filtering AnimAssist operators.  Type to find and run any tool without menus or hotkeys.

**Help topic:** `op.animassist.p10_quick_search`.

#### Recent Tools

Displays a list of the last N operators you ran, in reverse chronological order.  Click to repeat or re-open with settings.  Quick re-access without digging through menus.

**Help topic:** `op.animassist.p10_recent_tools`.

#### Repeat Last

Repeats the last operator execution using the previous settings and scope.  Useful for applying the same operation multiple times in a row.

**Help topic:** `op.animassist.p10_repeat_last`.

**Command:** `animassist.p10_repeat_last`.

#### Repeat with Settings

Repeats the last operation but pops up the settings dialog first, allowing you to tweak parameters before re-execution.  Faster than running from scratch.

**Help topic:** `op.animassist.p10_repeat_with_settings`.

## Reference A11. Animation layers

**Find this workflow:** Properties > Scene > Anim Assist > Whole Animation > animation layers.

### Blend & Merge

#### Merge Layer Down

Bakes the current layer's contribution into the layer below it.  The blend mode and weight are evaluated at every keyed frame, and the combined result is written into the lower layer's Action.  The upper layer is then removed.

Use this to 'commit' a layer when you're happy with the blend.

**Help topic:** `op.animassist.p11_merge_down`.

**Command:** `animassist.p11_merge_down`. Declared as an undoable operation.

#### Flatten All Layers

Collapses the entire layer stack into the base layer.  All layers are merged from top to bottom, evaluating blend modes and weights.  The result is a single Action with the combined animation.

WARNING: This is destructive  -  layer separation is lost.

**Help topic:** `op.animassist.p11_flatten_all`.

**Command:** `animassist.p11_flatten_all`. Declared as an undoable operation.

#### Blend Between Layers

Interactive slider that blends between two layers.  Select a source and target layer, then drag the factor to interpolate between them.  Useful for creating in-between poses across layer variations.

Rotation uses quaternion slerp for smooth interpolation.

**Help topic:** `op.animassist.p11_blend_layers`.

**Command:** `animassist.p11_blend_layers`. Declared as an undoable operation.

- **Source Layer** (`source_index`): Active row in the associated list; the interface updates this as you select a row. New-data default: . Allowed range: 0 to no explicit upper limit.

- **Target Layer** (`target_index`): Active row in the associated list; the interface updates this as you select a row. New-data default: 1. Allowed range: 0 to no explicit upper limit.

- **Blend Factor** (`factor`): 0.0 = fully source, 1.0 = fully target New-data default: 0.5. Allowed range: 0.0 to 1.0.

### Blend Modes

#### Layer Blend Mode

Controls how a layer's values combine with layers below it:

OVERRIDE  -  Lerp between the base and layer values.  At 100% weight the layer fully replaces the base.  Standard for primary poses.

ADDITIVE  -  Layer values are added ON TOP of the base as deltas from the rest pose.  Ideal for secondary motion, breathing, overlap, and adjustments that should combine with any base animation.

MULTIPLY  -  Scale existing animation values.  Useful for dampening or amplifying motion on specific parts.

COMBINE  -  NLA-style: location adds, rotation concatenates, scale multiplies.  Matches Blender's NLA Combine strip type.

**Help topic:** `p11.blend_mode`.

#### Layer Weight / Influence

Controls the strength of this layer's contribution (0%-100%).  Drag this slider to blend between having no effect (0%) and full contribution (100%).  This is the primary way to create seamless partial animations  -  e.g. set an arm correction layer to 60% to only partially apply the fix.

Per-channel weight overrides (in Advanced) let you set different weights for location vs rotation vs scale on individual bones.

**Help topic:** `p11.weight`.

### Editing

#### Layer Scope

Controls which transform channels this layer affects:

ALL  -  Location, rotation, and scale.
LOCATION ONLY  -  Only location channels.
ROTATION ONLY  -  Only rotation channels.
SCALE ONLY  -  Only scale channels.
CUSTOM  -  Use a comma-separated filter string.

Combined with part assignment, this gives very precise control over what a layer can modify.

**Help topic:** `p11.layer_scope`.

### Layer Stack

#### Enable Animation Layers

Master toggle for the animation layer system.  When disabled, only the object's base Action is used.  Enable this to start layering animations on top of each other  -  similar to Maya's Animation Layer stack or Blender's NLA strips, but with direct keyframe editing per layer.

**Help topic:** `p11.layers_enabled`.

#### Edit Active Layer Only

Exposed and saved layer preference. In the 12.1.3 source, this flag is stored and serialised but is not used to enforce native key insertion or automatically assign every keyed bone. Assign the intended bones manually, select the layer backing Action explicitly in the Action Editor, and inspect where keys are written.

**Help topic:** `p11.edit_active_only`.

#### Auto-Assign on Key

Exposed and saved layer preference. In the 12.1.3 source, this flag is stored and serialised but is not used to enforce native key insertion or automatically assign every keyed bone. Assign the intended bones manually, select the layer backing Action explicitly in the Action Editor, and inspect where keys are written.

**Help topic:** `p11.auto_assign_on_key`.

### Layer States

#### Solo Layer

When solo is enabled, ONLY this layer (and the base layer) are evaluated.  All other layers are temporarily muted.  This is useful for isolating a layer to see its contribution in isolation.

If multiple layers have solo enabled, all soloed layers are evaluated.

**Help topic:** `p11.solo`.

#### Mute Layer

Temporarily disable a layer without removing it.  The layer's keyframes and settings are preserved but it has no effect on the final result.  Toggle mute to A/B compare with and without a layer's contribution.

**Help topic:** `p11.mute`.

#### Lock Layer

Prevent any editing on this layer.  Keyframe insertion, deletion, and value changes are blocked.  Use this to protect approved animation while you work on other layers.

**Help topic:** `p11.locked`.

### Part Assignment

#### Assigned Bones / Parts

The bones (body parts) that this layer is allowed to edit.  When empty, the layer affects ALL bones (whole-body layer).

Assign bones to create part-specific layers:
  - Upper body layer (spine, arms, head)
  - Lower body layer (hips, legs, feet)
  - Face layer (facial bones)
  - Fingers layer

With 'Edit Active Only' enabled, you can only key bones that are assigned to the active layer.  This prevents accidental edits to other body parts while you work.

**Help topic:** `p11.assigned_bones`.

#### Per-Channel Weight Overrides

Fine-grained control over blend weights per bone per channel.  For example, you might want a layer's location changes at 100% but its rotation at only 50% on a specific bone.

Add overrides for individual bones when the global layer weight doesn't give you enough control.  Leave a bone without an override to use the layer's global weight.

**Help topic:** `p11.channel_overrides`.

#### Upper / Lower Body Preset

Creates a two-layer setup: Upper Body (spine and above) and Lower Body (hips and below).  The split point is auto-detected from the rig hierarchy.  Useful for blocking body mechanics on separate layers.

**Help topic:** `p11.preset_upper_lower`.

## Reference A12. Lipsync

**Find this workflow:** Properties > Scene > Anim Assist > Face; initial rig and target wiring is also available in Setup.

### Audio

#### Audio File

Path to the audio file used to drive the lipsync layer. v11.0.0 supports .wav only. The file's SHA-256 is recorded at bake time; if the file changes later, the layer header turns amber to prompt a rebake. Manual override keys still survive that rebake.

**Help topic:** `p12.audio_path`.

#### Audio Changed

Set automatically when the system re-hashes the audio file and finds the digest no longer matches the one recorded at the last bake. Indicates that the lipsync no longer matches the audio. Hit Rebake to refresh  -  your manual edits are preserved.

**Help topic:** `p12.is_stale`.

### Bake

#### Bake Lipsync

Analyses the bound audio and updates the cue table. PREVIEW uses the cue table for live drivers; SHIPPED also writes curves to the configured Bones, Shape Keys or Both targets. Mark selected polished keys as manual overrides before rebaking. Automatic output is replaced while marked manual output is retained. Anticipation and frame offset control timing.

**Help topic:** `p12.bake_lipsync`.

**Command:** `animassist.p12_bake_lipsync`. Declared as an undoable operation.

**Prerequisite messages:** Enable Anim Assist's lipsync and animation-layer settings for this scene.

- **Layer Name** (`layer_name`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: empty.

#### Clear Auto Keys

Walks the layer's Action and deletes every keyframe flagged as auto-baked. Manual override keys are preserved. Useful when you want to rebake from scratch with a different viseme library or backend setting.

**Help topic:** `p12.clear_auto_keys`.

**Command:** `animassist.p12_clear_auto_keys`. Declared as an undoable operation.

- **Layer Name** (`layer_name`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: empty.

#### Rebake

Convenience: clear-auto-keys followed by bake. Manual override keys survive both steps. Run this when audio has changed (the layer header turns amber to flag stale audio) or when you want to apply new bake settings.

**Help topic:** `p12.rebake`.

**Command:** `animassist.p12_rebake`. Declared as an undoable operation.

- **Layer Name** (`layer_name`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: empty.

### Setup

#### Setup Lipsync

Creates a Phase 11 override layer scoped to the face bone group, drops the chosen audio file as a sequencer sound strip, binds the layer to that strip, and loads the selected viseme library. After this runs, hit 'Bake Lipsync' to generate viseme keys, or pick 'Markers Only' mode to place phoneme markers without writing keys.

**Help topic:** `p12.setup_lipsync`.

**Command:** `animassist.p12_setup_lipsync`. Declared as an undoable operation.

- **Audio File** (`audio_path`): Path to the .wav file used for analysis New-data default: empty.

- **Viseme Library** (`viseme_library`): Which viseme set drives the bake Choices: Basic Mouth Open: Single jaw bone driven by audio amplitude (`BASIC_JAW`); Cartoon (5 visemes): A, E, I, O, U + closed - snappy stylised reads (`CARTOON_5`); Realistic (12 visemes): Preston Blair viseme set with anticipation (`REALISTIC_12`).

- **Setup Mode** (`setup_mode`): How the layer is populated when audio arrives Choices: Auto Bake: Run audio analysis immediately and write viseme keys (`AUTO_BAKE`); Markers Only: Place phoneme markers on the timeline; key by hand (`MARKER_ONLY`).

#### Viseme Library

Three built-in libraries ship by default:

Basic Mouth Open  -  single jaw bone driven by audio amplitude. The safest choice; works on any rig with a 'jaw' bone.

Cartoon (5 visemes)  -  A, E, I, O, U + closed. Snappy, stylised reads. Good fit for animated shorts and stylised game work.

Realistic (12 visemes)  -  Preston Blair viseme set with anticipation. Used for naturalistic dialogue performance. Requires more bones to be wired in the Rig Wiring section.

**Help topic:** `p12.viseme_library`.

#### Backend

Amplitude Only  -  always available. Reads the WAV envelope and drives the jaw between rest and open across speech onsets. Approximate but reliable.

Rhubarb Lip Sync  -  invokes the external Rhubarb CLI for phoneme-accurate viseme output. Requires the Rhubarb binary to be on your PATH or specified in the Rhubarb Path field. If not available, the system falls back to amplitude-only and surfaces a notice.

**Help topic:** `p12.backend`.

#### Setup Mode

Auto Bake  -  runs analysis immediately and writes viseme keys to the layer. Best for blocking-stage performance.

Markers Only  -  drops phoneme markers on the timeline but does not write keys. Hand-key against the markers, or hit Bake later. Best when you don't trust the auto output and want the markers as timing reference only.

**Help topic:** `p12.setup_mode`.

### Visemes

#### Capture Viseme

Reads the current pose of the wired face bones and stores it as the named viseme in the scene's viseme library. Overrides the built-in for that viseme. Use this when a built-in pose doesn't fit your character  -  pose the face manually, hit Capture.

**Help topic:** `p12.capture_viseme`.

**Command:** `animassist.p12_capture_viseme`. Declared as an undoable operation.

- **Viseme Name** (`viseme_name`): Logical viseme name; matches an entry in the active library New-data default: rest.

#### Rig Wiring

Viseme libraries reference logical roles (jaw, lip_upper, lip_lower, corner_L, corner_R, tongue) so the same library drives any rig. The rig wiring table maps each role to a concrete bone name on the active armature. Save the wiring as a preset to reuse it across shots for the same character.

**Help topic:** `p12.rig_wiring`.

### Workflow

#### Highlight Manual Overrides

When enabled, the panel marks keyframes the animator has touched with a distinct visual indicator so you can see at a glance which polish would survive a rebake versus which would be regenerated. Does not change behaviour  -  purely informational.

**Help topic:** `p12.show_manual_overrides`.

## Reference B. Additional commands and workflow controls

### Core tools, navigation and maintenance

**Find this workflow:** Properties > Scene > Anim Assist > Settings or Help & Diagnostics; core curve tools are under Graph Editor > Shape Curves. Search Tools and the relevant Help Browser category provide additional access where registered.

#### Anim Offset

Toggle Anim Offset mode and propagate current-frame edits across keyed animation

**Command:** `animassist.anim_offset`. Declared as an undoable operation.

#### Set Offset Range

Set the start and end frames of the Anim Offset mask

**Command:** `animassist.anim_offset_set_range`. Declared as an undoable operation.

- **Start** (`start`): First frame of the offset mask New-data default: 1.0.

- **End** (`end`): Last frame of the offset mask New-data default: 250.0.

#### Range from Scene

Copy the scene frame range into the Anim Offset mask

**Command:** `animassist.anim_offset_range_from_scene`. Declared as an undoable operation.

#### Toggle Mask

Enable or disable the Anim Offset frame mask

**Command:** `animassist.anim_offset_toggle_mask`. Declared as an undoable operation.

#### Blend Frame

Blend selected keys toward the value at the reference frame

**Command:** `animassist.blend_frame`. Declared as an undoable operation.

- **Factor** (`factor`): Strength of the blend toward the reference-frame value New-data default: .

#### Blend Offset

Offset selected keys using the difference between their neighboring keys

**Command:** `animassist.blend_offset`. Declared as an undoable operation.

- **Factor** (`factor`): Signed strength of the neighboring-key offset New-data default: .

#### Ease To Ease

Blend selected keys from linear spacing toward a smooth ease-in/ease-out curve

**Command:** `animassist.ease_to_ease`. Declared as an undoable operation.

- **Factor** (`factor`): Strength of the ease-in/ease-out shaping New-data default: .

#### Blend to Neighbor

Blend selected keys toward the line between their unselected neighbors

**Command:** `animassist.blend_neighbor`. Declared as an undoable operation.

- **Factor** (`factor`): Strength of the blend toward neighboring keys New-data default: .

#### Push / Pull

Scale selected keys away from or toward the reference frame value

**Command:** `animassist.push_pull`. Declared as an undoable operation.

- **Factor** (`factor`): Amount to push away from or pull toward the reference value New-data default: .

#### Smooth Keys

Blend selected keys toward the average of their immediate neighbors

**Command:** `animassist.smooth_keys`. Declared as an undoable operation.

- **Factor** (`factor`): Strength of smoothing toward neighboring-key averages New-data default: .

#### Set Reference Frame

Use the current playhead frame as the reference for blend tools

**Command:** `animassist.set_reference_frame`. Declared as an undoable operation.

#### Add Frame Bookmark

Save the current reference frame as a named bookmark

**Command:** `animassist.add_bookmark`. Declared as an undoable operation.

- **Name** (`name`): Display name for the new frame bookmark New-data default: Bookmark.

#### Remove Frame Bookmark

Delete the active frame bookmark

**Command:** `animassist.remove_bookmark`. Declared as an undoable operation.

#### Recall Bookmark

Set the reference frame from a saved bookmark

**Command:** `animassist.recall_bookmark`. Declared as an undoable operation.

- **Index** (`index`): Stored bookmark index to recall New-data default: .

#### Anim Assist Help

Show a detailed explanation for this control

**Command:** `anim_assist.show_help_popup`. Internal helper, normally invoked by the interface rather than as an independent artist task.

- **Help ID** (`help_id`): Unique id of the help entry to display New-data default: empty.

#### Open Anim Assist Panel

Show the full Anim Assist panel: the sidebar tab in the Graph Editor and Dope Sheet, or Properties > Scene > Anim Assist elsewhere

**Command:** `animassist.open_home`.

#### Open in Separate Window

Open the Anim Assist panel in its own window that stays open while you work; move it anywhere, or to a second monitor

**Command:** `animassist.open_home_window`.

#### Add Anim Assist Workspace

Switch to the Anim Assist workspace, adding it first if needed: a copy of the Animation workspace with a Graph Editor and every Anim Assist home open. Your Animation workspace is not changed

**Command:** `animassist.add_workspace`.

#### Batch Set Interpolation

Set all selected keyframes to the chosen interpolation type (Constant, Linear, or Bezier)

**Command:** `animassist.batch_interpolation`. Declared as an undoable operation.

- **Interpolation** (`interp_type`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: Bezier. Choices: Constant: No interpolation (`CONSTANT`); Linear: Linear interpolation (`LINEAR`); Bezier: Bezier interpolation (`BEZIER`).

#### Select Handles

Select the left, right, or both handles of selected keyframes

**Command:** `animassist.select_handles`. Declared as an undoable operation.

- **Side** (`side`): Which handles to select on each selected keyframe New-data default: Left. Choices: Left: Select left handles (`LEFT`); Right: Select right handles (`RIGHT`); Both: Select both handles (`BOTH`).

#### Set Key Type

Assign the chosen semantic key type to selected keyframes

**Command:** `animassist.set_key_type`. Declared as an undoable operation.

- **Key Type** (`key_type`): Semantic type to assign to selected keys New-data default: Keyframe. Choices: Keyframe (`KEYFRAME`); Breakdown (`BREAKDOWN`); Moving Hold (`MOVING_HOLD`); Extreme (`EXTREME`); Jitter (`JITTER`).

#### Set Handle Type

Set both Bezier handle types on selected keyframes

**Command:** `animassist.set_handle_type`. Declared as an undoable operation.

- **Handle Type** (`handle_type`): Bezier handle behavior to apply to selected keys New-data default: Auto Clamped. Choices: Free (`FREE`); Aligned (`ALIGNED`); Vector (`VECTOR`); Auto (`AUTO`); Auto Clamped (`AUTO_CLAMPED`).

#### Select by Key Type

Select or deselect every keyframe of the chosen semantic type

**Command:** `animassist.select_by_key_type`. Declared as an undoable operation.

- **Key Type** (`key_type`): Semantic key type to find New-data default: Breakdown. Choices: Keyframe (`KEYFRAME`); Breakdown (`BREAKDOWN`); Moving Hold (`MOVING_HOLD`); Extreme (`EXTREME`); Jitter (`JITTER`).

- **Deselect** (`deselect`): Deselect matching keys instead of selecting them New-data default: Off.

#### Delete by Key Type

Delete every keyframe of the chosen semantic type

**Command:** `animassist.delete_by_key_type`. Declared as an undoable operation.

- **Key Type** (`key_type`): Semantic key type to delete New-data default: Jitter. Choices: Keyframe (`KEYFRAME`); Breakdown (`BREAKDOWN`); Moving Hold (`MOVING_HOLD`); Extreme (`EXTREME`); Jitter (`JITTER`).

#### Insert Frames

Make room in the animation by shifting later keyframes forward

**Command:** `animassist.insert_frames`. Declared as an undoable operation.

- **Frame Count** (`count`): Number of frames to insert New-data default: 1. Allowed range: 1 to no explicit upper limit.

- **Insert Mode** (`mode`): Where the inserted time begins New-data default: At Cursor. Choices: At Cursor: Insert at current frame (`AT_CURSOR`); Between Selected: Insert after first selected key (`BETWEEN_SELECTED`).

#### Move Keys

Shift selected keyframes by a frame offset

**Command:** `animassist.move_keys`. Declared as an undoable operation.

- **Frame Offset** (`offset`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: 1.

#### Anim Assist: Deep Uninstall (Purge All Data)

Wipe all Anim Assist data from the current .blend.

Run BEFORE disabling/uninstalling the addon for a clean slate. After
this finishes, disable the addon and re-enable it (or install a new
version) - no leftover state will collide.

WARNING: This is destructive. It removes hand-flagged manual override
keys, lipsync sequencer strips, and Speakers created by the setup
operator. Hand-keyed animation data on the bones themselves is NOT
removed - only Anim Assist's per-key metadata sidecar.

**Command:** `animassist.deep_uninstall`.

- **Manual Override Flags** (`purge_action_props`): Remove the per-keyframe manual-override sidecar metadata from every Action. Your keyframes themselves are not deleted. New-data default: On.

- **Scene PropertyGroups** (`purge_scene_data`): Clear all Anim Assist scene-level configuration (layer stacks, lipsync layer links, viseme captures, rig wiring). Resets the addon to a fresh state on this .blend. New-data default: On.

- **Lipsync Sequencer Strips** (`purge_sequencer`): Remove sound strips named AA_P12_* from every scene's sequencer New-data default: On.

- **Lipsync Speakers** (`purge_speakers`): Remove Speaker datablocks named AA_P12_* New-data default: On.

- **App Handlers** (`purge_handlers`): Remove any application handlers (load_post, undo_post, etc.) registered by the addon. Defensive cleanup if a previous register() left handlers behind New-data default: On.

#### Anim Assist: Repair Registration

Force-unregister leftover Anim Assist classes from a previous load. Use when enabling reports 'class already registered'

**Command:** `animassist.purge_zombie_classes`.

#### Anim Assist: Check Saved Settings Version

Report any open scenes saved with a newer Anim Assist than installed.

**Command:** `animassist.report_saved_versions`.

### Shelf, macros, batches and recovery

**Find this workflow:** Graph Editor > Quick Shelf, Dope Sheet > Shelf & Macros, or Properties > Scene > Anim Assist > Setup / Settings / Help & Diagnostics. Search Tools and the relevant Help Browser category provide additional access where registered.

#### Show Operation History

Display recent operation history in the info area.

**Command:** `animassist.p10_show_history`.

- **Limit** (`limit`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: 20. Allowed range: 1 to 100.

#### Show Error Log

Display recent errors in the info area.

**Command:** `animassist.p10_show_errors`.

- **Limit** (`limit`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: 20. Allowed range: 1 to 100.

#### Session Statistics

Display session audit statistics.

**Command:** `animassist.p10_show_stats`.

#### Clear History

Clear the operation history buffer.

**Command:** `animassist.p10_clear_history`.

#### Clear Errors

Clear the error log.

**Command:** `animassist.p10_clear_errors`.

#### Batch: Selected Targets

Apply an operator to each selected pose bone

**Command:** `animassist.p10_batch_selected`. Declared as an undoable operation.

- **Operator ID** (`op_id`): Operator bl_idname to run on each selected bone New-data default: empty.

#### Batch: Bookmarked Frames

Apply an operator at each bookmarked frame

**Command:** `animassist.p10_batch_bookmarked`. Declared as an undoable operation.

- **Operator ID** (`op_id`): Operator bl_idname to run at each bookmark New-data default: empty.

#### Leak Check

Check for resource leaks.

**Command:** `animassist.p10_leak_check`.

#### Validate Registration

Validate that all expected classes are registered.

**Command:** `animassist.p10_validate_registration`.

#### Run Custom Macro

Run a user-defined macro from the macros collection

**Command:** `animassist.p10_run_custom_macro`. Declared as an undoable operation.

- **Macro Index** (`index`): Index of the macro in the p10.macros collection Allowed range: 0 to no explicit upper limit.

#### Add Macro

Add a new empty macro entry

**Command:** `animassist.p10_add_macro`. Declared as an undoable operation.

- **Name** (`name`): Name of the new macro New-data default: New Macro.

#### Remove Macro

Remove a macro by index

**Command:** `animassist.p10_remove_macro`. Declared as an undoable operation.

- **Macro Index** (`index`): Index of the macro to remove Allowed range: 0 to no explicit upper limit.

#### Add Macro Step

Add a step to a macro

**Command:** `animassist.p10_add_macro_step`. Declared as an undoable operation.

- **Macro Index** (`macro_index`): Index of the macro Allowed range: 0 to no explicit upper limit.

- **Operator ID** (`op_id`): Blender operator ID (e.g., 'wm.open_mainfile') New-data default: empty.

- **Step Label** (`label`): User-friendly label for the step New-data default: Step.

#### Remove Macro Step

Remove a step from a macro

**Command:** `animassist.p10_remove_macro_step`. Declared as an undoable operation.

- **Macro Index** (`macro_index`): Index of the macro Allowed range: 0 to no explicit upper limit.

- **Step Index** (`step_index`): Index of the step to remove Allowed range: 0 to no explicit upper limit.

#### Validate Macro

Validate all steps in a macro

**Command:** `animassist.p10_validate_macro`.

- **Macro Index** (`index`): Index of the macro to validate Allowed range: 0 to no explicit upper limit.

#### Export Workspace Profile

Export workspace profile to file

**Command:** `animassist.p10_export_workspace`.

- **File Path** (`filepath`): Filepath for the exported workspace profile

- **Filter Glob** (`filter_glob`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: *.json. Hidden command/state field; set through the normal workflow rather than as a general preference.

#### Import Workspace Profile

Import workspace profile from file

**Command:** `animassist.p10_import_workspace`. Declared as an undoable operation.

- **File Path** (`filepath`): Filepath of the workspace profile to import

- **Filter Glob** (`filter_glob`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: *.json. Hidden command/state field; set through the normal workflow rather than as a general preference.

#### Save Profile

Save current settings as a named profile

**Command:** `animassist.p10_save_profile`.

- **Profile Name** (`name`): Name for the new profile New-data default: Default.

#### Load Profile

Load a profile from the collection

**Command:** `animassist.p10_load_profile`. Declared as an undoable operation.

- **Profile Index** (`index`): Index of the profile to load New-data default: . Allowed range: 0 to no explicit upper limit.

#### Remove Profile

Remove a profile by index

**Command:** `animassist.p10_remove_profile`. Declared as an undoable operation.

- **Profile Index** (`index`): Index of the profile to remove New-data default: . Allowed range: 0 to no explicit upper limit.

#### Tag Preset

Add a tag to a profile (stored in data_json metadata)

**Command:** `animassist.p10_tag_preset`. Declared as an undoable operation.

- **Profile Index** (`index`): Index of the profile to tag New-data default: . Allowed range: 0 to no explicit upper limit.

- **Tag** (`tag`): Tag to add to the profile New-data default: empty.

#### Take Snapshot

Take a recovery snapshot of current addon state.

**Command:** `animassist.p10_take_snapshot`.

- **Label** (`label`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: empty.

#### Restore Snapshot

Restore addon state from a recovery snapshot.

**Command:** `animassist.p10_restore_snapshot`. Declared as an undoable operation.

- **Index** (`index`): Active row in the associated list; the interface updates this as you select a row. New-data default: .

#### Clear Snapshots

Clear all recovery snapshots.

**Command:** `animassist.p10_clear_snapshots`.

#### List Snapshots

List recovery snapshots in the info area.

**Command:** `animassist.p10_list_snapshots`.

#### Check Hotkey Conflicts

Check for hotkey conflicts in the registered hotkeys.

**Command:** `animassist.p10_check_hotkey_conflicts`.

#### Load Demo Config

Load a demo configuration for testing purposes.

**Command:** `animassist.p10_load_demo_config`. Declared as an undoable operation.

#### Toggle Debug Panel

Toggle the debug panel visibility.

**Command:** `animassist.p10_toggle_debug`.

#### Toggle Shelf Mode

Cycle shelf display mode: COMPACT  ->  EXPANDED  ->  FAVORITES  ->  COMPACT

**Command:** `animassist.p10_toggle_shelf_mode`.

#### Add to Favorites

Add current tool to favorites list

**Command:** `animassist.p10_add_favorite`.

- **Operator ID** (`op_id`): The operator ID to add as favorite New-data default: empty.

- **Label** (`label`): Display label for the favorite New-data default: empty.

- **Icon** (`icon`): Icon identifier New-data default: NONE.

#### Remove Favorite

Remove a favorite by index

**Command:** `animassist.p10_remove_favorite`. Declared as an undoable operation.

- **Index** (`index`): Index of favorite to remove New-data default: . Allowed range: 0 to no explicit upper limit.

#### Search Tools

Open tool search popup

**Command:** `animassist.p10_search_tools`.

- **Tool** (`tool_enum`): Select a tool to run Choices are provided dynamically by the current scene, rig, registered tools or the owning workflow.

#### Record Recent Tool

Record a tool usage in the recents list

**Command:** `animassist.p10_record_recent`. Internal helper, normally invoked by the interface rather than as an independent artist task.

- **Operator ID** (`op_id`): The operator ID being used New-data default: empty.

- **Label** (`label`): Display label for the tool New-data default: empty.

#### Clear Recents

Clear the recent tools list

**Command:** `animassist.p10_clear_recents`. Declared as an undoable operation.

### Animation layers

**Find this workflow:** Properties > Scene > Anim Assist > Whole Animation > animation layers. Search Tools and the relevant Help Browser category provide additional access where registered.

#### Assign Selected

Assign currently selected pose bones to the active layer

**Command:** `animassist.p11_assign_selected`. Declared as an undoable operation.

#### Remove Bone

Remove a bone from the active layer's assignment

**Command:** `animassist.p11_remove_bone`. Declared as an undoable operation.

- **Bone Index** (`index`): Index of the bone assignment to remove New-data default: . Allowed range: 0 to no explicit upper limit.

#### Remove Selected

Remove currently selected pose bones from the active layer

**Command:** `animassist.p11_remove_selected`. Declared as an undoable operation.

#### Clear Assignments

Clear all bone assignments (make layer affect all bones)

**Command:** `animassist.p11_clear_assignments`. Declared as an undoable operation.

#### Assign by Pattern

Assign bones matching a name pattern to the active layer

**Command:** `animassist.p11_assign_by_pattern`. Declared as an undoable operation.

- **Pattern** (`pattern`): Regex pattern to match bone names (e.g. 'arm|hand|finger' for arm bones, 'spine|chest|neck|head' for upper body) New-data default: empty.

#### Auto-Partition Layers

Automatically create layers for body part groups

**Command:** `animassist.p11_auto_partition`. Declared as an undoable operation.

- **Preset** (`preset`): Partitioning scheme New-data default: Upper / Lower Body. Choices: Upper / Lower Body: Split at the spine: upper body on one layer, lower on another (`UPPER_LOWER`); Face / Body: Facial bones on one layer, body on another (`FACE_BODY`); Left / Right: Left side bones on one layer, right side on another (`LEFT_RIGHT`); Fingers / Hands / Arms: Separate layers for fingers, hands, and arms (`FINGERS_HANDS`); Custom: User-defined layer partition (`CUSTOM`).

#### Select Assigned Bones

Select all pose bones assigned to the active layer

**Command:** `animassist.p11_select_assigned`. Declared as an undoable operation.

#### Add Channel Override

Add a per-channel weight override for a bone on the active layer

**Command:** `animassist.p11_add_channel_override`. Declared as an undoable operation.

- **Bone** (`bone_name`): Bone to add override for New-data default: empty.

#### Remove Channel Override

Remove a per-channel weight override

**Command:** `animassist.p11_remove_channel_override`. Declared as an undoable operation.

- **Override Index** (`index`): Active row in the associated list; the interface updates this as you select a row. New-data default: . Allowed range: 0 to no explicit upper limit.

#### Set Blend Factor

Apply a specific blend factor between source and target layers

**Command:** `animassist.p11_set_blend_factor`. Declared as an undoable operation.

- **Factor** (`factor`): Blend amount between the source and target animation layers New-data default: 0.5. Allowed range: 0.0 to 1.0.

#### Save Layer Preset

Save the current layer stack as a preset

**Command:** `animassist.p11_save_preset`. Declared as an undoable operation.

- **Preset Name** (`preset_name`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: My Preset.

#### Load Layer Preset

Load a saved layer stack preset

**Command:** `animassist.p11_load_preset`. Declared as an undoable operation.

#### Remove Preset

Remove a saved layer preset

**Command:** `animassist.p11_remove_preset`. Declared as an undoable operation.

#### Set Layer Weight

Set the weight of the active layer

**Command:** `animassist.p11_set_weight`. Declared as an undoable operation.

- **Weight** (`weight`): Influence of the active animation layer New-data default: 1.0. Allowed range: 0.0 to 1.0.

#### Set Blend Mode

Set the blend mode of the active layer

**Command:** `animassist.p11_set_blend_mode`. Declared as an undoable operation.

- **Mode** (`mode`): How the active animation layer combines with layers below it New-data default: Override. Choices: Override (`OVERRIDE`); Additive (`ADDITIVE`); Multiply (`MULTIPLY`); Combine (`COMBINE`).

#### Initialize Layers

Initialize the animation layer stack with a base layer

**Command:** `animassist.p11_init_layers`. Declared as an undoable operation.

#### Add Layer

Add a new animation layer to the stack

**Command:** `animassist.p11_add_layer`. Declared as an undoable operation.

- **Name** (`name`): Name for the new layer New-data default: New Layer.

- **Blend Mode** (`blend_mode`): How this layer combines with layers below New-data default: Override. Choices: Override: Replace base values (`OVERRIDE`); Additive: Add on top of base (`ADDITIVE`); Multiply: Scale base values (`MULTIPLY`); Combine: NLA-style combine (`COMBINE`).

- **Weight** (`weight`): Initial layer weight New-data default: 1.0. Allowed range: 0.0 to 1.0.

#### Remove Layer

Remove the active animation layer

**Command:** `animassist.p11_remove_layer`. Declared as an undoable operation.

#### Move Layer Up

Move the active layer up in the stack (higher priority)

**Command:** `animassist.p11_move_layer_up`. Declared as an undoable operation.

#### Move Layer Down

Move the active layer down in the stack (lower priority)

**Command:** `animassist.p11_move_layer_down`. Declared as an undoable operation.

#### Duplicate Layer

Duplicate the active animation layer

**Command:** `animassist.p11_duplicate_layer`. Declared as an undoable operation.

#### Toggle Solo

Toggle solo on the active layer

**Command:** `animassist.p11_toggle_solo`. Declared as an undoable operation.

#### Toggle Mute

Toggle mute on the active layer

**Command:** `animassist.p11_toggle_mute`. Declared as an undoable operation.

#### Toggle Lock

Toggle lock on the active layer

**Command:** `animassist.p11_toggle_lock`. Declared as an undoable operation.

#### Set Active Layer

Selects the active row/index in the layer list. It does not automatically switch the armature's Action. Choose the matching layer backing Action explicitly in the Action Editor before authoring keys.

**Command:** `animassist.p11_set_active`. Declared as an undoable operation.

- **Layer Index** (`index`): Index of the layer to activate New-data default: . Allowed range: 0 to no explicit upper limit.

#### Rename Layer

Rename the active animation layer

**Command:** `animassist.p11_rename_layer`. Declared as an undoable operation.

- **New Name** (`new_name`): New name for the active layer New-data default: empty.

#### Evaluate Layer Stack

Evaluates the stack at the current playhead frame and applies its combined transforms to the armature in Pose Mode. It is an explicit current-frame preview command, not a continuous playback handler or an automatic bake.

**Command:** `animassist.p11_evaluate_stack`. Declared as an undoable operation.

#### Select Layer

Selects the active row/index in the layer list. It does not automatically switch the armature's Action. Choose the matching layer backing Action explicitly in the Action Editor before authoring keys.

**Command:** `animassist.p11_select_layer`.

- **Index** (`index`): Active row in the associated list; the interface updates this as you select a row. New-data default: . Allowed range: 0 to no explicit upper limit.

### Lipsync

**Find this workflow:** Properties > Scene > Anim Assist > Face; initial rig and target wiring is also available in Setup. Search Tools and the relevant Help Browser category provide additional access where registered.

#### Mark as Manual Override

Flag the selected keyframes (bones AND shape keys) as manual overrides.

**Command:** `animassist.p12_mark_manual`. Declared as an undoable operation.

- **Layer Name** (`layer_name`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: empty.

#### Toggle Live Preview <-> Shipped Bake

Switch the active lipsync layer between PREVIEW (live drivers) and SHIPPED (baked fcurves).

PREVIEW -> SHIPPED: bake shape key fcurves from the cue table, then remove drivers.
SHIPPED -> PREVIEW: clear auto-baked keys (manual override frames preserved), then install drivers.

**Command:** `animassist.p12_toggle_mode`. Declared as an undoable operation.

- **Layer Name** (`layer_name`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: empty.

#### Install Lipsync Drivers

Install PREVIEW drivers on the active lipsync layer's wired shape keys.

**Command:** `animassist.p12_install_drivers`.

- **Layer Name** (`layer_name`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: empty.

#### Remove Lipsync Drivers

Remove PREVIEW drivers from the active lipsync layer's wired shape keys.

**Command:** `animassist.p12_remove_drivers`. Declared as an undoable operation.

- **Layer Name** (`layer_name`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: empty.

#### Refresh Audio Hash

Recompute the audio file's SHA-256 and update the stale flag.

Called by the panel automatically when drawn, and exposed as a button so
the user can force a refresh after editing the audio externally.

**Command:** `animassist.p12_refresh_audio_hash`.

- **Layer Name** (`layer_name`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: empty.

#### Autofill Shape Key Wiring

Auto-fill the shape_key_wiring rows by name-matching viseme names to shape keys.

**Command:** `animassist.p12_autofill_shape_key_wiring`. Declared as an undoable operation.

- **Library** (`library_id`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: CARTOON_5.

#### Use Active Mesh

Set the active lipsync link's mesh_name from the currently selected mesh.

**Command:** `animassist.p12_pick_mesh`. Declared as an undoable operation.

#### Capture Viseme (Shape Keys)

Capture the current shape key values as the named viseme.

For shape-key-driven faces, this is how you teach the rig what each
viseme looks like on this character. Pose the face with shape key
sliders, run this op, name the viseme.

**Command:** `animassist.p12_capture_viseme_shape`. Declared as an undoable operation.

- **Viseme** (`viseme_name`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: A.

#### Reset to Built-in

Discard the user capture for the named viseme; revert to the library default.

**Command:** `animassist.p12_reset_viseme`. Declared as an undoable operation.

- **Viseme Name** (`viseme_name`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: empty.

#### Autofill Rig Wiring

Pre-fill rig wiring entries by name-matching face roles to bones.

Adds rows for any roles required by the active library that aren't yet
in the wiring table. Best-guess only  -  animator confirms in the panel.

**Command:** `animassist.p12_autofill_wiring`. Declared as an undoable operation.

- **Library** (`library_id`): Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: CARTOON_5.

### Offsets and transforms

**Find this workflow:** Properties > Scene > Anim Assist > This Pose, or Dope Sheet > Inbetween; the core Anim Offset range tools also appear under Retime. Search Tools and the relevant Help Browser category provide additional access where registered.

#### Pivot from 3D Cursor

Set the custom pivot vector to the current 3D cursor location.

**Command:** `animassist.p4_set_pivot_cursor`. Declared as an undoable operation.

#### Pivot from Bone Head

Set the custom pivot vector to the active pose bone's head.

**Command:** `animassist.p4_set_pivot_head`. Declared as an undoable operation.

#### Pivot from Bone Tail

Set the custom pivot vector to the active pose bone's tail.

**Command:** `animassist.p4_set_pivot_tail`. Declared as an undoable operation.

### Retiming and timing diagnostics

**Find this workflow:** Graph Editor > Anim Assist > Retime, or Dope Sheet > Time. Search Tools and the relevant Help Browser category provide additional access where registered.

#### Detect & Fill Gaps

Run gap detection then fill all found gaps automatically

**Command:** `animassist.p6_detect_and_fill`. Declared as an undoable operation.

### Temporary controls, proxies and baking

**Find this workflow:** Properties > Scene > Anim Assist > Rig; bake shortcuts also appear under the animation editors' Pose & Rig / Mirror & Match groups. Search Tools and the relevant Help Browser category provide additional access where registered.

#### Reduce Keys

Simplify the active object's existing animation by removing keyframes whose deletion causes less than the tolerance deviation

**Command:** `animassist.p7_reduce_keys`. Declared as an undoable operation.

#### Bake Selected

Bake the evaluated transform of every selected object within the configured bake range

**Command:** `animassist.p7_bake_selected`. Declared as an undoable operation.

#### Bake with Step

Bake the active object's evaluated transform at every Nth frame (controlled by the Frame Step setting)

**Command:** `animassist.p7_bake_step`. Declared as an undoable operation.

#### Remove Proxy

Delete the active proxy object and any session-managed constraints that reference it

**Command:** `animassist.p7_remove_proxy`. Declared as an undoable operation.

#### Remove Session Constraints

Remove every constraint registered under the active session but keep all proxy and locator objects in the scene

**Command:** `animassist.p7_remove_constraints`. Declared as an undoable operation.

#### Create Proxy

Create a proxy helper of the chosen type, optionally auto-constraining it to the active object or bone

**Command:** `animassist.p7_create_proxy`. Declared as an undoable operation.

- **Proxy Type** (`proxy_type`): Type of temporary helper to create for the active object or bone New-data default: Orientation. Choices: Orientation: Temporary rotation proxy  -  mirrors target orientation via Copy Rotation. (`ORIENTATION`); Translation: Temporary translation proxy  -  mirrors target position via Copy Location. (`TRANSLATION`); Aim: Temporary aim proxy  -  drives target aim via Track To constraint. (`AIM`); Pole: Temporary pole helper  -  IK pole target reference with no auto-constraint. (`POLE`); Up-Vector: Temporary up-vector helper  -  reference for aim/track-to up axis. (`UP_VECTOR`); Multi-Target Avg: Average-position proxy driven by multiple targets. (`MULTI_TARGET`); Parent-Space: Parent-space proxy  -  temporary re-parenting via Child Of constraint. (`PARENT_SPACE`); World-Space: World-space proxy  -  mirrors full transform via Copy Transforms. (`WORLD_SPACE`); Camera-Space: Camera-space proxy  -  constraint influence keyed for camera-relative motion. (`CAMERA_SPACE`).

#### Purge Proxy Artifacts

Remove all temporary objects, constraints, and collections created by proxy/bake workflows

**Command:** `animassist.p7_purge_artifacts`. Declared as an undoable operation.

#### Recover Proxy Session

Detect incomplete proxy sessions and roll back their artifacts to restore the scene to a clean state

**Command:** `animassist.p7_recover_session`. Declared as an undoable operation.

### Matching and space switching

**Find this workflow:** Properties > Scene > Anim Assist > This Pose / Setup, Graph Editor > Pose & Rig, or Dope Sheet > Mirror & Match. Search Tools and the relevant Help Browser category provide additional access where registered.

#### Detect IK Chains

Scan every pose bone on the active armature for IK constraints and resolve the full chain hierarchy from tip to root

**Command:** `animassist.p8_detect_chains`. Declared as an undoable operation.

- **Include Muted** (`include_muted`): Also detect chains whose IK constraint is currently muted New-data default: Off.

#### Detect Chain for Bone

Find IK chains where the active bone is the constraint tip

**Command:** `animassist.p8_detect_chain_for_bone`. Declared as an undoable operation.

#### Select Chain Bones

Select every pose bone in the active IK chain, making it easy to key, match, or batch-process the whole chain at once

**Command:** `animassist.p8_select_chain_bones`. Declared as an undoable operation.

- **Chain Index** (`chain_index`): Index into the cached chains list New-data default: . Allowed range: 0 to no explicit upper limit.

- **Extend Selection** (`extend`): Add chain bones to existing selection instead of replacing New-data default: Off.

#### Navigate Chains

Cycle through detected IK chains

**Command:** `animassist.p8_chain_nav`. Declared as an undoable operation.

- **Direction** (`direction`): +1 for next chain, -1 for previous New-data default: 1.

#### Chain  ->  Match

Set the selected chain's tip bone as the active match target, bridging chain detection into the switch compensation workflow

Feed the selected chain's tip into the match tool.

Copies the chain tip bone into the switch bone field so the match
and compensation operators know which bone to operate on.

**Command:** `animassist.p8_chain_to_match`. Declared as an undoable operation.

#### Find Chains for Bone

Find every IK chain that the active bone participates in, whether as tip, root, or intermediate member

**Command:** `animassist.p8_find_bone_chains`. Declared as an undoable operation.

#### Chain Summary

Generate a diagnostic report of all IK chains on the active armature and display it in the info header

**Command:** `animassist.p8_chain_summary`.

#### Clear Chain Cache

Clear cached chain detection results so the next scan performs a fresh hierarchy walk

**Command:** `animassist.p8_invalidate_chain_cache`.

### Mirroring and pair management

**Find this workflow:** Properties > Scene > Anim Assist > This Pose / Setup, Graph Editor > Pose & Rig, or Dope Sheet > Mirror & Match. Search Tools and the relevant Help Browser category provide additional access where registered.

#### Mirror Local

Mirror selected bones in local space

**Command:** `animassist.p9_mirror_local`. Declared as an undoable operation.

#### Mirror World

Mirror selected bones in world space

**Command:** `animassist.p9_mirror_world`. Declared as an undoable operation.

#### Remove Pair Override

Remove the selected manual pair override.

**Command:** `animassist.p9_remove_pair_override`. Declared as an undoable operation.

- **Index** (`index`): Index of the pair override to remove New-data default: . Allowed range: 0 to no explicit upper limit.

#### Add Naming Exception

Add a naming exception for bones that do not follow standard naming conventions.

**Command:** `animassist.p9_add_naming_exception`.

#### Remove Naming Exception

Remove the selected naming exception.

**Command:** `animassist.p9_remove_naming_exception`. Declared as an undoable operation.

- **Index** (`index`): Index of the naming exception to remove New-data default: . Allowed range: 0 to no explicit upper limit.

#### Load Pair Preset

Load pair overrides and naming exceptions from the saved JSON preset.

**Command:** `animassist.p9_load_pair_preset`. Declared as an undoable operation.

## Reference C. Complete settings and saved-record reference

Controls are grouped by their owning settings or record. Use the command entries for command-only arguments. Record fields such as indices, names, identifiers and collections describe stored state and are usually managed by the interface. Numeric color/vector defaults are component values, not hex colors. An empty string means no text/target has been assigned yet.

### Favorite tool records

#### Operator ID

Operator bl_idname New-data default: empty.

**Field:** `op_id`. **Owner:** Favorite tool records. **Data type:** String.

#### Label

Display name for the favorite New-data default: empty.

**Field:** `label`. **Owner:** Favorite tool records. **Data type:** String.

#### Icon

Blender icon identifier New-data default: NONE.

**Field:** `icon`. **Owner:** Favorite tool records. **Data type:** String.

### Recent tool records

#### Operator ID

Operator bl_idname New-data default: empty.

**Field:** `op_id`. **Owner:** Recent tool records. **Data type:** String.

#### Label

Display name for the recent item New-data default: empty.

**Field:** `label`. **Owner:** Recent tool records. **Data type:** String.

#### Timestamp

Time when this item was last used (time.time()) New-data default: .

**Field:** `timestamp`. **Owner:** Recent tool records. **Data type:** Float.

### Macro steps

#### Operator ID

Operator bl_idname New-data default: empty.

**Field:** `op_id`. **Owner:** Macro steps. **Data type:** String.

#### Label

Display name for the step New-data default: empty.

**Field:** `label`. **Owner:** Macro steps. **Data type:** String.

#### Enabled

Whether this step is executed New-data default: On.

**Field:** `enabled`. **Owner:** Macro steps. **Data type:** Bool.

### Custom macros

#### Name

Macro name New-data default: Untitled Macro.

**Field:** `name`. **Owner:** Custom macros. **Data type:** String.

#### Steps

Macro steps

**Field:** `steps`. **Owner:** Custom macros. **Data type:** Collection.

#### Description

Macro description New-data default: empty.

**Field:** `description`. **Owner:** Custom macros. **Data type:** String.

#### Icon

Blender icon identifier New-data default: SEQUENCE.

**Field:** `icon`. **Owner:** Custom macros. **Data type:** String.

### Workspace profiles

#### Name

Profile name New-data default: Untitled Profile.

**Field:** `name`. **Owner:** Workspace profiles. **Data type:** String.

#### Data JSON

Serialized profile settings as JSON New-data default: empty.

**Field:** `data_json`. **Owner:** Workspace profiles. **Data type:** String.

### Shelf, macros, batches and recovery settings

#### First Run Complete

Whether the initial Anim Assist setup has completed New-data default: Off. Hidden command/state field; set through the normal workflow rather than as a general preference.

**Field:** `first_run_complete`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** Bool.

#### Shelf Mode

Display mode for the tool shelf Choices: Compact: Show compact shelf view (`COMPACT`); Expanded: Show expanded shelf view (`EXPANDED`); Favorites: Show only favorites (`FAVORITES`).

**Field:** `shelf_mode`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** Enum.

#### Tool Group

Show only tools from one group on the shelf (0 shows all groups) New-data default: . Allowed range: 0 to 10.

**Field:** `shelf_filter_phase`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** Int.

#### Shelf Search Query

Current search query for shelf filtering New-data default: empty.

**Field:** `shelf_search_query`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** String.

#### Favorites

Favorite tool entries

**Field:** `favorites`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** Collection.

#### Active Favorite Index

Index of the active favorite New-data default: . Allowed range: 0 to no explicit upper limit.

**Field:** `active_favorite_index`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** Int.

#### Recents

Recently used tool entries

**Field:** `recents`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** Collection.

#### Max Recents

Maximum number of recent items to store New-data default: 20. Allowed range: 5 to 50.

**Field:** `max_recents`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** Int.

#### Macros

Saved macro entries

**Field:** `macros`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** Collection.

#### Active Macro Index

Index of the active macro New-data default: . Allowed range: 0 to no explicit upper limit.

**Field:** `active_macro_index`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** Int.

#### Profiles

Workspace configuration profiles

**Field:** `profiles`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** Collection.

#### Active Profile Index

Index of the active profile New-data default: . Allowed range: 0 to no explicit upper limit.

**Field:** `active_profile_index`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** Int.

#### Recovery Enabled

Enable automatic state recovery New-data default: On.

**Field:** `recovery_enabled`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** Bool.

#### Max Snapshots

Maximum number of recovery snapshots to store New-data default: 10. Allowed range: 1 to 50.

**Field:** `max_snapshots`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** Int.

#### Audit Enabled

Enable operation audit logging New-data default: On.

**Field:** `audit_enabled`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** Bool.

#### Max Audit Entries

Maximum number of audit entries to store New-data default: 100. Allowed range: 10 to 500.

**Field:** `max_audit_entries`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** Int.

#### Show Debug Panel

Show debug information panel New-data default: Off.

**Field:** `show_debug_panel`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** Bool.

#### Batch Mode

Batch processing mode Choices: Selected Objects: Process selected objects (`SELECTED`); Bookmarked Frames: Process bookmarked frames (`BOOKMARKED`); Frame Steps: Process frames by step size (`FRAME_STEPS`).

**Field:** `batch_mode`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** Enum.

#### Batch Frame Step

Frame step size for batch processing New-data default: 1. Allowed range: 1 to 100.

**Field:** `batch_frame_step`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** Int.

#### Batch Frame Start

Starting frame for batch processing New-data default: 1.

**Field:** `batch_frame_start`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** Int.

#### Batch Frame End

Ending frame for batch processing New-data default: 250.

**Field:** `batch_frame_end`. **Owner:** Shelf, macros, batches and recovery settings. **Data type:** Int.

### Layer bone assignments

#### Bone

Name of the bone assigned to this layer New-data default: empty.

**Field:** `bone_name`. **Owner:** Layer bone assignments. **Data type:** String.

### Layer channel overrides

#### Bone

Bone this override applies to New-data default: empty.

**Field:** `bone_name`. **Owner:** Layer channel overrides. **Data type:** String.

#### Location Weight

Override weight for location channels on this bone New-data default: 1.0. Allowed range: 0.0 to 1.0.

**Field:** `location_weight`. **Owner:** Layer channel overrides. **Data type:** Float.

#### Rotation Weight

Override weight for rotation channels on this bone New-data default: 1.0. Allowed range: 0.0 to 1.0.

**Field:** `rotation_weight`. **Owner:** Layer channel overrides. **Data type:** Float.

#### Scale Weight

Override weight for scale channels on this bone New-data default: 1.0. Allowed range: 0.0 to 1.0.

**Field:** `scale_weight`. **Owner:** Layer channel overrides. **Data type:** Float.

### Individual animation layers

#### Layer Name

Display name for this animation layer New-data default: Layer.

**Field:** `name`. **Owner:** Individual animation layers. **Data type:** String.

#### Color

Visual accent color for this layer in the UI New-data default: Default. Choices: Default: Use theme default color (`DEFAULT`); Red: Red layer accent (`RED`); Orange: Orange layer accent (`ORANGE`); Yellow: Yellow layer accent (`YELLOW`); Green: Green layer accent (`GREEN`); Blue: Blue layer accent (`BLUE`); Purple: Purple layer accent (`PURPLE`); Cyan: Cyan layer accent (`CYAN`).

**Field:** `layer_color`. **Owner:** Individual animation layers. **Data type:** Enum.

#### Weight

Influence of this layer on the final result (0%% = no effect, 100%% = full contribution). Drag to blend between layers New-data default: 1.0. Allowed range: 0.0 to 1.0.

**Field:** `weight`. **Owner:** Individual animation layers. **Data type:** Float.

#### Blend Mode

How this layer combines with layers below it in the stack New-data default: Override. Choices: Override: Layer fully replaces channels below it (scaled by weight). Equivalent to Maya Override mode (`OVERRIDE`); Additive: Layer values are added on top of the layer below. Ideal for secondary motion, breathing, overlap. Equivalent to Maya Additive mode (`ADDITIVE`); Multiply: Layer values are multiplied with the layer below. Useful for scaling existing animation intensities (`MULTIPLY`); Combine: Channels are combined using Blender NLA-style mixing. Location adds, rotation concatenates, scale multiplies (`COMBINE`).

**Field:** `blend_mode`. **Owner:** Individual animation layers. **Data type:** Enum.

#### Mute

Disable this layer without removing it New-data default: Off.

**Field:** `mute`. **Owner:** Individual animation layers. **Data type:** Bool.

#### Solo

Only evaluate this layer (and the base layer). Other layers are temporarily muted New-data default: Off.

**Field:** `solo`. **Owner:** Individual animation layers. **Data type:** Bool.

#### Lock

Prevent editing on this layer (read-only) New-data default: Off.

**Field:** `locked`. **Owner:** Individual animation layers. **Data type:** Bool.

#### Protected

Prevent accidental deletion of this layer New-data default: Off.

**Field:** `protected`. **Owner:** Individual animation layers. **Data type:** Bool.

#### Auto Key

Stored layer-workflow flag. In 12.1.3 this setting does not intercept all native posing or key insertion. Assign bones explicitly and select the intended backing Action before authoring keys; inspect the written channels. New-data default: Off.

**Field:** `auto_key`. **Owner:** Individual animation layers. **Data type:** Bool.

#### Scope

Which transform channels this layer affects New-data default: All Channels. Choices: All Channels: Layer affects all channels on assigned bones (`ALL`); Location Only: Layer only affects location channels (`LOCATION`); Rotation Only: Layer only affects rotation channels (`ROTATION`); Scale Only: Layer only affects scale channels (`SCALE`); Custom: Layer uses a custom fcurve path filter (`CUSTOM`).

**Field:** `layer_scope`. **Owner:** Individual animation layers. **Data type:** Enum.

#### Custom Filter

Comma-separated fcurve data_path substrings to include (e.g. 'location,rotation_euler'). Used when scope is Custom New-data default: empty.

**Field:** `custom_filter`. **Owner:** Individual animation layers. **Data type:** String.

#### Assigned Bones

Bones that this layer is allowed to edit. Empty means ALL bones (whole-body layer)

**Field:** `assigned_bones`. **Owner:** Individual animation layers. **Data type:** Collection.

#### Active Bone

Active row in the associated list; the interface updates this as you select a row. New-data default: . Allowed range: 0 to no explicit upper limit.

**Field:** `assigned_bones_index`. **Owner:** Individual animation layers. **Data type:** Int.

#### Channel Overrides

Per-bone channel weight overrides. Allows different blend percentages for loc/rot/scale on individual bones within this layer

**Field:** `channel_overrides`. **Owner:** Individual animation layers. **Data type:** Collection.

#### Active Override

Active row in the associated list; the interface updates this as you select a row. New-data default: . Allowed range: 0 to no explicit upper limit.

**Field:** `channel_overrides_index`. **Owner:** Individual animation layers. **Data type:** Int.

#### Base Layer

Whether this is the base (bottom) layer. The base layer always uses Override mode at 100%% weight New-data default: Off.

**Field:** `is_base_layer`. **Owner:** Individual animation layers. **Data type:** Bool.

#### Action

Name of the Blender Action backing this layer's keyframes. Each layer stores its animation in a separate Action New-data default: empty.

**Field:** `action_name`. **Owner:** Individual animation layers. **Data type:** String.

### Layer presets

#### Preset Name

Display name for this layer preset New-data default: Preset.

**Field:** `name`. **Owner:** Layer presets. **Data type:** String.

#### Preset Data

JSON-encoded layer stack configuration New-data default: empty.

**Field:** `preset_json`. **Owner:** Layer presets. **Data type:** String.

### Animation layers settings

#### Animation Layers

Stack of animation layers, evaluated bottom to top

**Field:** `layers`. **Owner:** Animation layers settings. **Data type:** Collection.

#### Active Layer

Index of the currently active layer for editing New-data default: . Allowed range: 0 to no explicit upper limit.

**Field:** `active_layer_index`. **Owner:** Animation layers settings. **Data type:** Int.

#### Enable Layers

Master toggle for the animation layer system. When disabled, only the base action is used New-data default: On.

**Field:** `layers_enabled`. **Owner:** Animation layers settings. **Data type:** Bool.

#### Edit Active Only

Stored layer-workflow flag. In 12.1.3 this setting does not intercept all native posing or key insertion. Assign bones explicitly and select the intended backing Action before authoring keys; inspect the written channels. New-data default: On.

**Field:** `edit_active_only`. **Owner:** Animation layers settings. **Data type:** Bool.

#### Auto-Assign on Key

Stored layer-workflow flag. In 12.1.3 this setting does not intercept all native posing or key insertion. Assign bones explicitly and select the intended backing Action before authoring keys; inspect the written channels. New-data default: Off.

**Field:** `auto_assign_on_key`. **Owner:** Animation layers settings. **Data type:** Bool.

#### Show Layer Colors

Color-code bones in the viewport by their layer assignment New-data default: On.

**Field:** `show_layer_colors`. **Owner:** Animation layers settings. **Data type:** Bool.

#### Warn Unassigned

Show a warning when attempting to key a bone that is not assigned to any layer New-data default: On.

**Field:** `show_unassigned_warning`. **Owner:** Animation layers settings. **Data type:** Bool.

#### Blend Source

Index of the source layer for interactive blend New-data default: . Allowed range: 0 to no explicit upper limit.

**Field:** `blend_source_index`. **Owner:** Animation layers settings. **Data type:** Int.

#### Blend Target

Index of the target layer for interactive blend New-data default: 1. Allowed range: 0 to no explicit upper limit.

**Field:** `blend_target_index`. **Owner:** Animation layers settings. **Data type:** Int.

#### Blend Factor

Interpolation factor between source and target layers (0.0 = fully source, 1.0 = fully target) New-data default: 0.5. Allowed range: 0.0 to 1.0.

**Field:** `blend_factor`. **Owner:** Animation layers settings. **Data type:** Float.

#### Layer Presets

Saved layer stack configurations

**Field:** `user_presets`. **Owner:** Animation layers settings. **Data type:** Collection.

#### Active Preset

Index of the selected animation-layer preset New-data default: . Allowed range: 0 to no explicit upper limit.

**Field:** `user_presets_index`. **Owner:** Animation layers settings. **Data type:** Int.

#### Eval Generation

Incremented when layer stack changes to invalidate caches New-data default: .

**Field:** `eval_generation`. **Owner:** Animation layers settings. **Data type:** Int.

### Audio cue rows

#### Time

Cue timestamp in seconds from start of audio New-data default: . Allowed range: 0.0 to no explicit upper limit.

**Field:** `time_seconds`. **Owner:** Audio cue rows. **Data type:** Float.

#### Viseme

Logical viseme name from the active library New-data default: rest.

**Field:** `viseme_name`. **Owner:** Audio cue rows. **Data type:** String.

### Shape-key wiring

#### Viseme

Logical viseme name (matches a viseme in the active library) New-data default: A.

**Field:** `viseme_name`. **Owner:** Shape-key wiring. **Data type:** String.

#### Shape Key

Shape key (key block) on the mesh that holds this viseme pose New-data default: empty.

**Field:** `shape_key_name`. **Owner:** Shape-key wiring. **Data type:** String.

### Saved viseme poses

#### Viseme

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: rest.

**Field:** `viseme_name`. **Owner:** Saved viseme poses. **Data type:** String.

#### Pose JSON

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: {}.

**Field:** `pose_json`. **Owner:** Saved viseme poses. **Data type:** String.

#### Built-in

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: Off.

**Field:** `is_builtin`. **Owner:** Saved viseme poses. **Data type:** Bool.

### Face-bone wiring

#### Role

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: jaw.

**Field:** `role`. **Owner:** Face-bone wiring. **Data type:** String.

#### Bone

Bone assigned to this logical facial role New-data default: empty.

**Field:** `bone_name`. **Owner:** Face-bone wiring. **Data type:** String.

### Lipsync layer links

#### Layer Name

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: empty.

**Field:** `layer_name`. **Owner:** Lipsync layer links. **Data type:** String.

#### Armature

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: empty.

**Field:** `armature_name`. **Owner:** Lipsync layer links. **Data type:** String.

#### Audio File

WAV audio file used to generate this lipsync layer New-data default: empty.

**Field:** `audio_path`. **Owner:** Lipsync layer links. **Data type:** String.

#### Audio Hash

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: empty.

**Field:** `audio_sha256`. **Owner:** Lipsync layer links. **Data type:** String.

#### Sequencer Strip

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: empty.

**Field:** `speaker_strip_name`. **Owner:** Lipsync layer links. **Data type:** String.

#### Viseme Library

Viseme naming and pose library used for speech shapes New-data default: Basic Mouth Open. Choices: Basic Mouth Open: Single jaw bone driven by audio amplitude (`BASIC_JAW`); Cartoon (5 visemes): A, E, I, O, U + closed - snappy stylised reads (`CARTOON_5`); Realistic (12 visemes): Preston Blair viseme set with anticipation (`REALISTIC_12`).

**Field:** `viseme_library`. **Owner:** Lipsync layer links. **Data type:** Enum.

#### Backend

Speech-analysis backend used to generate viseme cues New-data default: Amplitude Only. Choices: Amplitude Only: Use audio RMS envelope - always available (`AMPLITUDE`); Rhubarb Lip Sync: External Rhubarb CLI for phoneme-accurate visemes (`RHUBARB`).

**Field:** `backend`. **Owner:** Lipsync layer links. **Data type:** Enum.

#### Setup Mode

Whether setup creates markers only or also performs the initial bake New-data default: Auto Bake. Choices: Auto Bake: Run audio analysis immediately and write viseme keys (`AUTO_BAKE`); Markers Only: Place phoneme markers on the timeline; key by hand (`MARKER_ONLY`).

**Field:** `setup_mode`. **Owner:** Lipsync layer links. **Data type:** Enum.

#### Frame Offset

Shift generated lipsync cues by this many frames New-data default: 1. Allowed range: 0 to no explicit upper limit.

**Field:** `frame_offset`. **Owner:** Lipsync layer links. **Data type:** Int.

#### Anticipation

Move mouth-shape cues earlier by this many frames New-data default: 2. Allowed range: 0 to 12.

**Field:** `anticipation_frames`. **Owner:** Lipsync layer links. **Data type:** Int.

#### Bake Range Start

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: .

**Field:** `last_baked_start`. **Owner:** Lipsync layer links. **Data type:** Int.

#### Bake Range End

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: .

**Field:** `last_baked_end`. **Owner:** Lipsync layer links. **Data type:** Int.

#### Audio Changed

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: Off.

**Field:** `is_stale`. **Owner:** Lipsync layer links. **Data type:** Bool.

#### Mode

PREVIEW = live drivers; SHIPPED = baked fcurves New-data default: Preview (Live). Choices: Preview (Live): Drivers respond to scrubbing/playback - fast iteration (`PREVIEW`); Shipped (Baked): Shape key/bone fcurves written - render-ready, NLA-safe (`SHIPPED`).

**Field:** `mode`. **Owner:** Lipsync layer links. **Data type:** Enum.

#### Target

What surface the lipsync drives New-data default: Shape Keys. Choices: Shape Keys: Drive mouth shape keys (cartoon/blendshape rigs) (`SHAPE_KEYS`); Bones: Drive face bones (Rigify-style face rigs) (`BONES`); Both: Drive shape keys AND bones (combined rigs) (`BOTH`).

**Field:** `target_kind`. **Owner:** Lipsync layer links. **Data type:** Enum.

#### Mesh

Object whose shape keys are driven (usually the head mesh) New-data default: empty.

**Field:** `mesh_name`. **Owner:** Lipsync layer links. **Data type:** String.

#### Cue Table

Phoneme/viseme schedule shared by PREVIEW drivers and SHIPPED bake

**Field:** `cue_table`. **Owner:** Lipsync layer links. **Data type:** Collection.

#### Active Cue

Active row in the associated list; the interface updates this as you select a row. New-data default: . Allowed range: 0 to no explicit upper limit.

**Field:** `active_cue_index`. **Owner:** Lipsync layer links. **Data type:** Int.

### Lipsync settings

#### Enable Lipsync

Enable Anim Assist lipsync evaluation for this scene New-data default: On.

**Field:** `enabled`. **Owner:** Lipsync settings. **Data type:** Bool.

#### Viseme Poses

Collection of records managed by the corresponding list and its add/remove commands.

**Field:** `viseme_poses`. **Owner:** Lipsync settings. **Data type:** Collection.

#### Active Viseme

Active row in the associated list; the interface updates this as you select a row. New-data default: . Allowed range: 0 to no explicit upper limit.

**Field:** `active_viseme_index`. **Owner:** Lipsync settings. **Data type:** Int.

#### Rig Wiring

Collection of records managed by the corresponding list and its add/remove commands.

**Field:** `rig_wiring`. **Owner:** Lipsync settings. **Data type:** Collection.

#### Lipsync Layer Links

Collection of records managed by the corresponding list and its add/remove commands.

**Field:** `layer_links`. **Owner:** Lipsync settings. **Data type:** Collection.

#### Active Link

Active row in the associated list; the interface updates this as you select a row. New-data default: . Allowed range: 0 to no explicit upper limit.

**Field:** `active_link_index`. **Owner:** Lipsync settings. **Data type:** Int.

#### Highlight Manual Overrides

Highlight keys protected from automatic lipsync rebaking New-data default: On.

**Field:** `show_manual_overrides`. **Owner:** Lipsync settings. **Data type:** Bool.

#### Rhubarb Path

Path to the optional Rhubarb Lip Sync executable New-data default: empty.

**Field:** `rhubarb_path`. **Owner:** Lipsync settings. **Data type:** String.

#### Jaw Amplitude Scale

Multiplier applied to generated jaw movement New-data default: 1.0. Allowed range: 0.0 to 10.0.

**Field:** `amplitude_jaw_scale`. **Owner:** Lipsync settings. **Data type:** Float.

#### Shape Key Wiring

Logical viseme -> shape_key mapping for the active mesh

**Field:** `shape_key_wiring`. **Owner:** Lipsync settings. **Data type:** Collection.

#### Active Shape Key Wiring Row

Active row in the associated list; the interface updates this as you select a row. New-data default: . Allowed range: 0 to no explicit upper limit.

**Field:** `active_shape_key_index`. **Owner:** Lipsync settings. **Data type:** Int.

#### Warn If Rendering in PREVIEW

Print a console warning if a render starts while a lipsync layer is still in PREVIEW (driver) mode - drivers may not evaluate the way you expect across all render engines New-data default: On.

**Field:** `warn_on_render_in_preview`. **Owner:** Lipsync settings. **Data type:** Bool.

### User breakdown presets

#### Preset Name

Name shown in the breakdown preset picker. New-data default: Custom Preset.

**Field:** `name`. **Owner:** User breakdown presets. **Data type:** String.

#### Factor

Breakdown blend factor, where 0 is the previous pose and 1 is the next pose. New-data default: 0.5. Allowed range: -1.0 to 2.0.

**Field:** `factor`. **Owner:** User breakdown presets. **Data type:** Float.

#### Mode

Blend mode identifier used by the breakdown engine. New-data default: REPLACE.

**Field:** `mode`. **Owner:** User breakdown presets. **Data type:** String.

#### Mask

Channel mask kind applied when this preset runs (ALL, LOCATION, ROTATION, SCALE, or TRANSFORM). New-data default: ALL.

**Field:** `mask_kind`. **Owner:** User breakdown presets. **Data type:** String.

### Breakdown exclusion patterns

#### Pattern

Substring matched against fcurve data_paths to exclude channels from breakdown breakdown operations. New-data default: empty.

**Field:** `pattern`. **Owner:** Breakdown exclusion patterns. **Data type:** String.

### Breakdowns, in-betweens and pose comparison settings

#### Factor

Breakdown blend factor. 0.0 produces the previous pose, 0.5 a clean midpoint, and 1.0 the next pose. Modal drag and numeric breakdown seed from this value. New-data default: 0.5. Allowed range: -1.0 to 2.0.

**Field:** `factor`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Float.

#### Mode

Blend mode applied by the breakdown engine. New-data default: Replace. Choices: Replace: Write a fresh blended value at the target frame, replacing any existing key. (`REPLACE`); Offset: Add a relative offset to the currently evaluated value at the target frame. (`OFFSET`); Push From Previous: Extrapolate past the previous pose for a snappier out-curve. (`PUSH_PREV`); Push Into Next: Extrapolate past the next pose for a heavier anticipation. (`PUSH_NEXT`); Pull To Previous: Pull the new key back toward the previous pose, softening the move. (`PULL_PREV`); Pull To Next: Pull the new key forward toward the next pose, softening the in. (`PULL_NEXT`).

**Field:** `mode`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Enum.

#### Push Strength

Multiplier applied when extrapolating past a neighbour pose (Push modes). New-data default: 1.25. Allowed range: 1.0 to 3.0.

**Field:** `push_strength`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Float.

#### Pull Strength

Blend factor used by the Pull modes, clamped between 0 and 1. New-data default: 0.75. Allowed range: 0.0 to 1.0.

**Field:** `pull_strength`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Float.

#### Offset Amount

Relative offset added to the current evaluated value when using Offset mode. New-data default: .

**Field:** `offset_amount`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Float.

#### Location

When enabled, breakdown operators may write location channels. New-data default: On.

**Field:** `mask_location`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Bool.

#### Rotation

When enabled, breakdown operators may write rotation channels (Euler and quaternion). New-data default: On.

**Field:** `mask_rotation`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Bool.

#### Scale

When enabled, breakdown operators may write scale channels. New-data default: On.

**Field:** `mask_scale`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Bool.

#### Custom

When enabled, breakdown operators may write custom (non-transform) channels. New-data default: Off.

**Field:** `mask_custom`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Bool.

#### X

Allow breakdown writes to array index 0 (X axis, or W component for quaternions). New-data default: On.

**Field:** `mask_axis_x`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Bool.

#### Y

Allow breakdown writes to array index 1 (Y axis, or X component for quaternions). New-data default: On.

**Field:** `mask_axis_y`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Bool.

#### Z

Allow breakdown writes to array index 2 (Z axis, or Y component for quaternions). New-data default: On.

**Field:** `mask_axis_z`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Bool.

#### W

Allow breakdown writes to array index 3 (Z component for quaternions). New-data default: On.

**Field:** `mask_axis_w`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Bool.

#### Ignore Locked Axes

Skip fcurves whose lock flag is set so locked transforms stay untouched. New-data default: On.

**Field:** `skip_locked`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Bool.

#### Respect Exclusion Set

When enabled, fcurves matching the active exclusion set are ignored by all breakdown operators. New-data default: On.

**Field:** `respect_exclusions`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Bool.

#### Quaternion-Aware

Blend quaternion rotation channels with a true slerp across all four components so the resulting rotation never flips mid-arc. New-data default: On.

**Field:** `quaternion_aware`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Bool.

#### Euler Continuity

Pick the shortest arc when blending Euler rotations that cross a ±π boundary. New-data default: On.

**Field:** `euler_wrap_aware`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Bool.

#### Visual Transform

Sample the final evaluated curve value (respecting modifiers) instead of a pure neighbour blend. Useful for constrained rigs. New-data default: Off.

**Field:** `visual_transform`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Bool.

#### Preserve World Contact

Best-effort attempt to keep world-space contact channels (feet, hands) stable during the breakdown. Depends on rig setup. New-data default: Off.

**Field:** `preserve_world_contact`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Bool.

#### Preserve Child Contact

Best-effort attempt to keep child-object contacts stable during the breakdown. New-data default: Off.

**Field:** `preserve_child_contact`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Bool.

#### Match Tangents

Copy handle types from the closer neighbour key so the new breakdown flows cleanly. New-data default: On.

**Field:** `match_tangents`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Bool.

#### Auto-Key Missing Channels

When a channel has no neighbouring keys, insert a key with its currently evaluated value so the breakdown still has something to blend next time. New-data default: Off.

**Field:** `auto_key_missing`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Bool.

#### Space

Transform space used for visual-transform sampling. New-data default: Local. Choices: Local: Sample and write values in the channel's own local transform space. (`LOCAL`); World: Sample values in world space and convert back to the channel space where practical. (`WORLD`).

**Field:** `space`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Enum.

#### Inbetween Count

Number of inbetween keys to distribute inside the current selection gap. New-data default: 1. Allowed range: 1 to 32.

**Field:** `inbetween_count`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Int.

#### Use Selected Keys

When batching, run the breakdown at every selected keyframe instead of a single target frame. New-data default: On.

**Field:** `batch_use_selection`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Bool.

#### Active Preset

Built-in breakdown preset selected for the Apply Preset operator. Choices are provided dynamically by the current scene, rig, registered tools or the owning workflow.

**Field:** `active_preset`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Enum.

#### User Presets

Collection of records managed by the corresponding list and its add/remove commands.

**Field:** `user_presets`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Collection.

#### User Preset Index

Active row in the user preset list. New-data default: .

**Field:** `user_preset_index`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Int.

#### Exclusion Patterns

Collection of records managed by the corresponding list and its add/remove commands.

**Field:** `exclusion_patterns`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Collection.

#### Exclusion Index

Active row in the exclusion-pattern list. New-data default: .

**Field:** `exclusion_index`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Int.

#### Modal Sensitivity

Horizontal pixels required to cover the full 0  ->  1 factor range during modal drag breakdown. New-data default: 220. Allowed range: 40 to 2000.

**Field:** `modal_sensitivity`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Int.

#### Preview Active

Internal flag set while a preview-before-commit breakdown is pending. New-data default: Off.

**Field:** `preview_active`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Bool.

#### Preview Frame

Frame at which the current preview breakdown was staged. New-data default: .

**Field:** `preview_frame`. **Owner:** Breakdowns, in-betweens and pose comparison settings. **Data type:** Float.

### Offsets and transforms settings

#### Translate Δ

Translation delta applied by offset operators before space conversion. New-data default: 0.0, 0.0, 0.0. Components: 3.

**Field:** `translate_amount`. **Owner:** Offsets and transforms settings. **Data type:** FloatVector.

#### Rotate Δ

Rotation delta in radians applied by offset operators before space conversion. New-data default: 0.0, 0.0, 0.0. Components: 3.

**Field:** `rotate_amount`. **Owner:** Offsets and transforms settings. **Data type:** FloatVector.

#### Scale Δ

Scale delta applied additively on top of the current scale channels. New-data default: 0.0, 0.0, 0.0. Components: 3.

**Field:** `scale_amount`. **Owner:** Offsets and transforms settings. **Data type:** FloatVector.

#### Push/Pull Amount

Magnitude used by the Push X/Y/Z and Pull X/Y/Z one-click buttons. New-data default: 0.1. Allowed range: 0.0 to no explicit upper limit.

**Field:** `push_amount`. **Owner:** Offsets and transforms settings. **Data type:** Float.

#### Channels

Which transform channels receive the offset. Choices: Translation: Offset only translation channels (location). (`T`); Rotation: Offset only rotation channels (euler or quaternion). (`R`); Scale: Offset only scale channels. (`S`); Translation + Rotation + Scale: Offset every transform channel. (`TRS`).

**Field:** `channel_mask`. **Owner:** Offsets and transforms settings. **Data type:** Enum.

#### Scope

Whether the offset writes at the current frame, across selected keys, or over an explicit frame range. Choices: Current Frame: Apply the offset at the scene's current frame only. (`CURRENT_FRAME`); Selected Keys: Apply the offset to every selected keyframe on the target channels. (`SELECTED_KEYS`); Frame Range: Apply the offset to every key inside an explicit frame range. (`FRAME_RANGE`).

**Field:** `scope`. **Owner:** Offsets and transforms settings. **Data type:** Enum.

#### Selected Channels Only

Restrict offsets to fcurves whose keyframe points are selected in the Dope Sheet or Graph Editor. New-data default: Off.

**Field:** `selected_channels_only`. **Owner:** Offsets and transforms settings. **Data type:** Bool.

#### Keyed Channels Only

Restrict offsets to fcurves that already have keyframes. Prevents creating keys on untouched channels. New-data default: On.

**Field:** `keyed_channels_only`. **Owner:** Offsets and transforms settings. **Data type:** Bool.

#### Skip Locked

Do not modify fcurves marked as locked in the Dope Sheet or Graph Editor. New-data default: On.

**Field:** `skip_locked`. **Owner:** Offsets and transforms settings. **Data type:** Bool.

#### Skip Muted

Do not modify fcurves marked as muted. New-data default: On.

**Field:** `skip_muted`. **Owner:** Offsets and transforms settings. **Data type:** Bool.

#### Auto-Key Missing

Insert new keys on targeted channels that do not have a key at the current frame. Off by default to respect the user's existing pose. New-data default: Off.

**Field:** `auto_key_missing`. **Owner:** Offsets and transforms settings. **Data type:** Bool.

#### Range Start

First frame of the explicit frame-range scope. New-data default: 1.0.

**Field:** `range_start`. **Owner:** Offsets and transforms settings. **Data type:** Float.

#### Range End

Last frame of the explicit frame-range scope. New-data default: 24.0.

**Field:** `range_end`. **Owner:** Offsets and transforms settings. **Data type:** Float.

#### Falloff

How the offset amount is distributed across the affected frame window. Does not modify fcurve tangents. Choices: None: Every affected frame receives the full offset  -  no falloff. (`NONE`); Linear: Triangular weight peaking at the window midpoint, fading to zero at the edges. (`LINEAR`); Ease In (Distribution): Distributes the offset amount as an ease-in curve: small at the start, full at the end. Does not touch fcurve tangents. (`EASE_IN`); Ease Out (Distribution): Distributes the offset amount as an ease-out curve: full at the start, small at the end. Does not touch fcurve tangents. (`EASE_OUT`); Bell: Smooth cosine bell: zero at the edges, full at the midpoint. (`BELL`).

**Field:** `falloff_shape`. **Owner:** Offsets and transforms settings. **Data type:** Enum.

#### Space

Reference space in which the offset amounts are interpreted before being converted to the target's basis. Choices: Local: Interpret the offset amounts directly in the target's own basis. (`LOCAL`); Parent: Interpret the offset amounts in the target's parent space. (`PARENT`); World: Interpret the offset amounts in world coordinates. (`WORLD`); Visual: Interpret the offset amounts in world coordinates using the depsgraph-evaluated pose, respecting constraints. (`VISUAL`); Gimbal: Rotation-only mode that applies axis-aligned rotation in the target's current rotation order. (`GIMBAL`).

**Field:** `space`. **Owner:** Offsets and transforms settings. **Data type:** Enum.

#### Pivot

Pivot point used for rotation and scale offsets. Choices: Individual Origins: Each target rotates and scales around its own origin  -  the default for pose workflows. (`INDIVIDUAL`).

**Field:** `pivot_mode`. **Owner:** Offsets and transforms settings. **Data type:** Enum.

#### Custom Pivot

World-space custom pivot point. Only used when pivot mode is Custom Point. New-data default: 0.0, 0.0, 0.0. Components: 3.

**Field:** `custom_pivot`. **Owner:** Offsets and transforms settings. **Data type:** FloatVector.

#### Preserve Contact

Zero the translation delta on one axis before applying. Keeps foot contacts planted when nudging elsewhere. Choices: None: No axis is locked. All three translation axes are offset. (`NONE`); Preserve X: Force the X translation component of every offset to zero. Useful for keeping foot contacts glued sideways. (`X`); Preserve Y: Force the Y translation component of every offset to zero. (`Y`); Preserve Z: Force the Z translation component of every offset to zero. The most common setting for keeping feet planted. (`Z`).

**Field:** `preserve_contact_axis`. **Owner:** Offsets and transforms settings. **Data type:** Enum.

#### Mirror Sign

Negate the offset on the configured axis for targets whose name indicates the mirrored side (.L / .R / Left / Right). New-data default: Off.

**Field:** `mirror_sign_enabled`. **Owner:** Offsets and transforms settings. **Data type:** Bool.

#### Mirror Axis

Which axis of the delta is negated on mirrored targets. Choices: X: Flip the X component of the delta on mirrored targets. (`X`); Y: Flip the Y component of the delta on mirrored targets. (`Y`); Z: Flip the Z component of the delta on mirrored targets. (`Z`).

**Field:** `mirror_axis`. **Owner:** Offsets and transforms settings. **Data type:** Enum.

#### Fine Step

Multiply every offset amount by 0.1 for fine nudging. Modal drag also uses this when Shift is held. New-data default: Off.

**Field:** `fine_step`. **Owner:** Offsets and transforms settings. **Data type:** Bool.

#### Preset

Transform multiplier preset applied on top of the entered offset amounts. Choices: Tiny: 0.1 times the entered offset (`TINY`); Small: 0.25 times the entered offset (`SMALL`); Normal: 1 times the entered offset (`NORMAL`); Big: 2 times the entered offset (`BIG`); Huge: 4 times the entered offset (`HUGE`).

**Field:** `active_preset`. **Owner:** Offsets and transforms settings. **Data type:** Enum.

#### Modal Preview Active

Internal: true while a modal offset drag is in progress. New-data default: Off.

**Field:** `modal_preview_active`. **Owner:** Offsets and transforms settings. **Data type:** Bool.

### Trajectory and spacing settings

#### Enable Overlay

Master toggle for the trajectory overlay.  When disabled, no draw handlers are active and no sampling occurs. New-data default: Off.

**Field:** `overlay_enabled`. **Owner:** Trajectory and spacing settings. **Data type:** Bool.

#### Display Mode

Which targets have visible trajectories. Choices: Active Control: Show the trajectory for the active bone or object only. (`ACTIVE`); Multi Control: Show trajectories for every selected bone or object. (`MULTI`); Isolate: Show only the explicitly isolated target. (`ISOLATE`).

**Field:** `display_mode`. **Owner:** Trajectory and spacing settings. **Data type:** Enum.

#### Scope

How the sample window is determined. Choices: Around Current Frame: Sample a window centred on the scene's current frame. (`AROUND_CURRENT`); Full Playback Range: Sample across the scene's full playback range. (`FULL_RANGE`); Custom Range: Sample between explicit start and end frames. (`CUSTOM`).

**Field:** `scope_mode`. **Owner:** Trajectory and spacing settings. **Data type:** Enum.

#### Frames Before

Number of frames before the current frame to sample when using Around Current Frame. New-data default: 25. Allowed range: 1 to no explicit upper limit.

**Field:** `window_before`. **Owner:** Trajectory and spacing settings. **Data type:** Int.

#### Frames After

Number of frames after the current frame to sample when using Around Current Frame. New-data default: 25. Allowed range: 1 to no explicit upper limit.

**Field:** `window_after`. **Owner:** Trajectory and spacing settings. **Data type:** Int.

#### Start Frame

First frame for Custom Range scope. New-data default: 1.0.

**Field:** `custom_start`. **Owner:** Trajectory and spacing settings. **Data type:** Float.

#### End Frame

Last frame for Custom Range scope. New-data default: 250.0.

**Field:** `custom_end`. **Owner:** Trajectory and spacing settings. **Data type:** Float.

#### Step

Frame step between samples.  1.0 = one sample per frame.  Values below 1.0 enable subframe sampling (more precise but more expensive). New-data default: 1.0. Allowed range: 0.1 to no explicit upper limit.

**Field:** `sample_step`. **Owner:** Trajectory and spacing settings. **Data type:** Float.

#### Max Samples

Cap on the total number of samples per target to prevent viewport stalls. New-data default: 160. Allowed range: 10 to no explicit upper limit.

**Field:** `max_samples`. **Owner:** Trajectory and spacing settings. **Data type:** Int.

#### Subframe Sampling

Sample at sub-frame intervals (step < 1.0) for smoother trajectories.  Increases computation cost proportionally. New-data default: Off.

**Field:** `use_subframe`. **Owner:** Trajectory and spacing settings. **Data type:** Bool.

#### Constraint Evaluation (Slow)

Evaluate the depsgraph at each sample frame for constraint-accurate positions.  Much slower than fcurve-only mode  -  ignored during playback to keep animation interaction smooth. New-data default: Off.

**Field:** `use_constraints`. **Owner:** Trajectory and spacing settings. **Data type:** Bool.

#### Space

Coordinate space for trajectory drawing. Choices: World: Draw the trajectory in world space. (`WORLD`).

**Field:** `space_mode`. **Owner:** Trajectory and spacing settings. **Data type:** Enum.

#### Frame Ticks

Draw small dots at every sampled frame position. New-data default: Off.

**Field:** `show_frame_ticks`. **Owner:** Trajectory and spacing settings. **Data type:** Bool.

#### Keyframe Ticks

Draw highlighted dots at keyframe positions on the path. New-data default: On.

**Field:** `show_keyframe_ticks`. **Owner:** Trajectory and spacing settings. **Data type:** Bool.

#### Frame Numbers

Draw frame-number labels next to keyframe ticks. New-data default: Off.

**Field:** `show_frame_numbers`. **Owner:** Trajectory and spacing settings. **Data type:** Bool.

#### Velocity Vectors

Draw velocity direction arrows at each sample point. New-data default: Off.

**Field:** `show_velocity`. **Owner:** Trajectory and spacing settings. **Data type:** Bool.

#### Tangent Lines

Draw path tangent lines at keyframe positions. New-data default: Off.

**Field:** `show_tangent`. **Owner:** Trajectory and spacing settings. **Data type:** Bool.

#### Ghost Points

Draw faded points for the 2 frames before and after the current frame. New-data default: On.

**Field:** `show_ghost_points`. **Owner:** Trajectory and spacing settings. **Data type:** Bool.

#### Spacing Colorization

Colour path segments by their spacing relative to the median. New-data default: Off.

**Field:** `show_spacing_color`. **Owner:** Trajectory and spacing settings. **Data type:** Bool.

#### Arc Deviation Heatmap

Colour the path by deviation from a locally-fit arc (blue=good, red=bad). New-data default: Off.

**Field:** `show_deviation_heatmap`. **Owner:** Trajectory and spacing settings. **Data type:** Bool.

#### Color Preset

Colour palette for the trajectory overlay. Choices: Default: Default trajectory colors (`DEFAULT`); High Contrast: High-contrast trajectory colors (`CONTRAST`); Pastel: Pastel trajectory colors (`PASTEL`).

**Field:** `color_preset`. **Owner:** Trajectory and spacing settings. **Data type:** Enum.

#### Path Width

Line width for the trajectory path in pixels. New-data default: 2.0. Allowed range: 0.5 to no explicit upper limit.

**Field:** `path_width`. **Owner:** Trajectory and spacing settings. **Data type:** Float.

#### Max Display Targets

Maximum number of simultaneous trajectory targets to avoid viewport stalls. New-data default: 3. Allowed range: 1 to no explicit upper limit.

**Field:** `max_display_targets`. **Owner:** Trajectory and spacing settings. **Data type:** Int.

#### Arc Drift

Detect points that deviate from a locally-fit arc. New-data default: On.

**Field:** `enable_drift_detect`. **Owner:** Trajectory and spacing settings. **Data type:** Bool.

#### Flat Arc

Detect stretches where the path has near-zero curvature. New-data default: On.

**Field:** `enable_flat_detect`. **Owner:** Trajectory and spacing settings. **Data type:** Bool.

#### Zig-Zag

Detect rapid direction reversals in a short window. New-data default: On.

**Field:** `enable_zigzag_detect`. **Owner:** Trajectory and spacing settings. **Data type:** Bool.

#### Pop

Detect sudden speed jumps between consecutive samples. New-data default: On.

**Field:** `enable_pop_detect`. **Owner:** Trajectory and spacing settings. **Data type:** Bool.

#### Spacing

Detect over-spaced and under-spaced segments. New-data default: On.

**Field:** `enable_spacing_detect`. **Owner:** Trajectory and spacing settings. **Data type:** Bool.

#### Reversal

Detect velocity direction reversals. New-data default: Off.

**Field:** `enable_reversal_detect`. **Owner:** Trajectory and spacing settings. **Data type:** Bool.

#### Stops

Detect near-zero-speed holds. New-data default: Off.

**Field:** `enable_stop_detect`. **Owner:** Trajectory and spacing settings. **Data type:** Bool.

#### Apex/Contact

Detect local maxima (apex) and minima (contact) on the gravity axis. New-data default: Off.

**Field:** `enable_apex_contact_detect`. **Owner:** Trajectory and spacing settings. **Data type:** Bool.

#### Drift Tolerance

Normalised arc deviation above which a point is flagged as drift. New-data default: 0.05. Allowed range: 0.001 to no explicit upper limit.

**Field:** `drift_tolerance`. **Owner:** Trajectory and spacing settings. **Data type:** Float.

#### Pop Ratio

Speed must exceed this multiple of median speed to be flagged as a pop. New-data default: 4.0. Allowed range: 1.5 to no explicit upper limit.

**Field:** `pop_ratio`. **Owner:** Trajectory and spacing settings. **Data type:** Float.

#### Overspaced Ratio

Segments longer than this multiple of median spacing are flagged. New-data default: 1.8. Allowed range: 1.1 to no explicit upper limit.

**Field:** `spacing_hi`. **Owner:** Trajectory and spacing settings. **Data type:** Float.

#### Underspaced Ratio

Segments shorter than this multiple of median spacing are flagged. New-data default: 0.4. Allowed range: 0.01 to no explicit upper limit.

**Field:** `spacing_lo`. **Owner:** Trajectory and spacing settings. **Data type:** Float.

#### Comparison Mode

Show trajectories for two targets side-by-side with delta overlay. New-data default: Off.

**Field:** `comparison_enabled`. **Owner:** Trajectory and spacing settings. **Data type:** Bool.

#### Compare Target

Name of the second bone or object to compare against the active target. New-data default: empty.

**Field:** `comparison_target`. **Owner:** Trajectory and spacing settings. **Data type:** String.

#### Isolate Target

Name of the bone or object whose trajectory is exclusively shown in Isolate mode. New-data default: empty.

**Field:** `isolate_target`. **Owner:** Trajectory and spacing settings. **Data type:** String.

### Retiming and timing diagnostics settings

#### Anchor

Pivot point for scale operations New-data default: First Key. Choices: First Key: Scale around the earliest keyframe in the selection/action. (`FIRST`); Last Key: Scale around the latest keyframe in the selection/action. (`LAST`); Current Frame: Scale around the scene's current frame (playhead position). (`CURRENT_FRAME`); Active Key: Scale around the active/highlighted keyframe (falls back to playhead). (`ACTIVE`); Custom Frame: Scale around a manually specified pivot frame. (`CUSTOM`).

**Field:** `anchor_mode`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Enum.

#### Scale Factor

Timing scale factor (1.0 = unchanged, 2.0 = double duration, 0.5 = half duration) New-data default: 1.0. Allowed range: 0.01 to 100.0.

**Field:** `scale_factor`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Float.

#### Pivot Frame

Custom pivot frame for scale operations. Only active when Anchor = Custom Frame. New-data default: .

**Field:** `pivot_frame`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Float.

#### Offset

Number of frames to shift keys by (positive = later) New-data default: 1.0.

**Field:** `offset_frames`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Float.

#### Ripple Amount

How many frames to shift the rippled keys New-data default: 1.0.

**Field:** `ripple_delta`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Float.

#### Frame Count

Number of frames to insert or remove at the playhead New-data default: 1. Allowed range: 1 to no explicit upper limit.

**Field:** `insert_frames`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Int.

#### Range Mode

How to determine the active timing range New-data default: From Selection. Choices: From Selection: Derive the active range from the frame span of selected keys. (`SELECTION`); Scene Range: Use the scene's playback range (frame_start to frame_end). (`SCENE`); Custom: Specify range start and end frames manually. (`CUSTOM`).

**Field:** `range_mode`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Enum.

#### Start

Custom timing range start frame New-data default: 1.0.

**Field:** `range_start`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Float.

#### End

Custom timing range end frame New-data default: 100.0.

**Field:** `range_end`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Float.

#### Stored Start

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: 1.0. Hidden command/state field; set through the normal workflow rather than as a general preference.

**Field:** `stored_range_start`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Float.

#### Stored End

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: 100.0. Hidden command/state field; set through the normal workflow rather than as a general preference.

**Field:** `stored_range_end`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Float.

#### Has Stored Range

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: Off. Hidden command/state field; set through the normal workflow rather than as a general preference.

**Field:** `has_stored_range`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Bool.

#### Gap Threshold

Minimum frame gap to count as a timing gap New-data default: 4.0. Allowed range: 1.0 to no explicit upper limit.

**Field:** `gap_threshold`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Float.

#### Fill Mode

How to fill detected timing gaps New-data default: Constant Hold. Choices: Constant Hold: Fill the gap by inserting a key that holds the last known value. (`CONSTANT`); Linear Bridge: Insert a key at the gap midpoint and set interpolation to LINEAR. (`LINEAR`); Mark Only: Report the gap without inserting any keys. (`NONE`).

**Field:** `gap_fill_mode`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Enum.

#### Cluster Radius

Keys within this many frames of each other are considered a cluster New-data default: 2.0. Allowed range: 0.5 to no explicit upper limit.

**Field:** `cluster_radius`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Float.

#### Result

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: Not Run. Choices: Not Run: Diagnostics have not been run yet. (`NONE`); Clean: No timing issues detected. (`CLEAN`); Gaps Found: One or more timing gaps were detected. (`GAPS`); Clusters Found: One or more key clusters were detected. (`CLUSTERS`); Gaps & Clusters: Both timing gaps and key clusters detected. (`BOTH`). Hidden command/state field; set through the normal workflow rather than as a general preference.

**Field:** `last_diag_result`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Enum.

#### Gap Count

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: . Hidden command/state field; set through the normal workflow rather than as a general preference.

**Field:** `last_diag_gap_count`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Int.

#### Cluster Count

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: . Hidden command/state field; set through the normal workflow rather than as a general preference.

**Field:** `last_diag_cluster_count`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Int.

#### Timing Score

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: -1.0. Hidden command/state field; set through the normal workflow rather than as a general preference.

**Field:** `last_diag_score`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Float.

#### Show Details

Expand the detailed diagnostic breakdown in the panel New-data default: Off.

**Field:** `show_diag_details`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Bool.

#### Snap to Frames

Snap keyframe positions to integer frames during modal operations New-data default: On.

**Field:** `modal_snap`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Bool.

#### Show Header Delta

Display the current offset/scale delta in the viewport header New-data default: On.

**Field:** `modal_show_header`. **Owner:** Retiming and timing diagnostics settings. **Data type:** Bool.

### Temporary controls, proxies and baking settings

#### Proxy Type

Type of temporary proxy helper to create (orientation, translation, aim, pole, etc.) New-data default: Orientation. Choices: Orientation: Temporary rotation proxy  -  mirrors target orientation via Copy Rotation. (`ORIENTATION`); Translation: Temporary translation proxy  -  mirrors target position via Copy Location. (`TRANSLATION`); Aim: Temporary aim proxy  -  drives target aim via Track To constraint. (`AIM`); Pole: Temporary pole helper  -  IK pole target reference with no auto-constraint. (`POLE`); Up-Vector: Temporary up-vector helper  -  reference for aim/track-to up axis. (`UP_VECTOR`); Multi-Target Avg: Average-position proxy driven by multiple targets. (`MULTI_TARGET`); Parent-Space: Parent-space proxy  -  temporary re-parenting via Child Of constraint. (`PARENT_SPACE`); World-Space: World-space proxy  -  mirrors full transform via Copy Transforms. (`WORLD_SPACE`); Camera-Space: Camera-space proxy  -  constraint influence keyed for camera-relative motion. (`CAMERA_SPACE`).

**Field:** `proxy_type`. **Owner:** Temporary controls, proxies and baking settings. **Data type:** Enum.

#### Proxy Size

Display size of newly created proxy empties in viewport units New-data default: 0.5. Allowed range: 0.01 to 10.0.

**Field:** `proxy_size`. **Owner:** Temporary controls, proxies and baking settings. **Data type:** Float.

#### Proxy Color

Wireframe colour assigned to new proxy objects for visual identification New-data default: 0.2, 0.8, 1.0. Allowed range: 0.0 to 1.0. Components: 3. Color components use the declared numeric range; a fourth component, where present, is opacity.

**Field:** `proxy_color`. **Owner:** Temporary controls, proxies and baking settings. **Data type:** FloatVector.

#### Auto-Constrain

Automatically add the appropriate constraint between proxy and target on creation. Disable for manual constraint setup. New-data default: On.

**Field:** `auto_constrain`. **Owner:** Temporary controls, proxies and baking settings. **Data type:** Bool.

#### Proxy Mode

How the proxy drives the target: Constrain replaces, Offset adds on top New-data default: Constrain. Choices: Constrain: Proxy drives the target via constraint. (`CONSTRAIN`); Offset: Proxy provides an additive offset layered on top of existing animation. (`OFFSET`).

**Field:** `proxy_mode`. **Owner:** Temporary controls, proxies and baking settings. **Data type:** Enum.

#### Snap to Bone

When creating a locator from a bone, snap the empty to the bone's head position New-data default: On.

**Field:** `locator_snap_to_bone`. **Owner:** Temporary controls, proxies and baking settings. **Data type:** Bool.

#### Bake Range

How to determine the frame range for baking operations New-data default: Scene Range. Choices: Scene Range: Bake across the full scene playback range. (`SCENE`); Action Range: Bake across the frame range of the active action. (`ACTION`); Custom Range: Bake between manually specified start and end frames. (`CUSTOM`); Selection: Derive bake range from selected keyframes. (`SELECTION`); Preview Range: Bake across the scene's preview/playback range markers. (`PREVIEW`).

**Field:** `bake_range_mode`. **Owner:** Temporary controls, proxies and baking settings. **Data type:** Enum.

#### Start

Custom bake range start frame New-data default: 1.0.

**Field:** `bake_range_start`. **Owner:** Temporary controls, proxies and baking settings. **Data type:** Float.

#### End

Custom bake range end frame New-data default: 250.0.

**Field:** `bake_range_end`. **Owner:** Temporary controls, proxies and baking settings. **Data type:** Float.

#### Frame Step

Bake every Nth frame. 1 = every frame, 2 = every other frame New-data default: 1. Allowed range: 1 to 24.

**Field:** `bake_step`. **Owner:** Temporary controls, proxies and baking settings. **Data type:** Int.

#### Channels

Which transform channels to bake: all, location-only, rotation-only, or selected New-data default: All Channels. Choices: All Channels: Bake location, rotation, and scale. (`ALL`); Location Only: Bake only location channels. (`LOC`); Rotation Only: Bake only rotation channels. (`ROT`); Loc + Rot: Bake location and rotation, skip scale. (`LOCROT`); Selected Only: Bake only channels that are currently selected in the channel list. (`SELECTED`).

**Field:** `bake_channels`. **Owner:** Temporary controls, proxies and baking settings. **Data type:** Enum.

#### Key Reduction Tolerance

Maximum deviation allowed when removing redundant keys. Lower = more keys retained, higher = fewer keys. New-data default: 0.01. Allowed range: 0.0001 to 1.0.

**Field:** `smart_bake_tolerance`. **Owner:** Temporary controls, proxies and baking settings. **Data type:** Float.

#### Preserve Existing Timing

When baking, preserve existing keyframe positions and only update values at those frames instead of inserting a key on every frame New-data default: Off.

**Field:** `preserve_timing`. **Owner:** Temporary controls, proxies and baking settings. **Data type:** Bool.

#### Display Mode

How proxy objects are displayed in the viewport: full, dimmed, or hidden New-data default: Full Display. Choices: Full Display: Show proxies at normal size with full wireframe colour. (`FULL`); Dimmed: Reduce proxy size and mute colour for less viewport clutter. (`DIM`); Hidden: Hide proxy empties from the viewport entirely. (`HIDDEN`).

**Field:** `display_mode`. **Owner:** Temporary controls, proxies and baking settings. **Data type:** Enum.

#### Show Names

Display proxy object names in the viewport for quick identification New-data default: On.

**Field:** `show_proxy_names`. **Owner:** Temporary controls, proxies and baking settings. **Data type:** Bool.

#### Active Session

UUID of the currently active P7 session New-data default: empty. Hidden command/state field; set through the normal workflow rather than as a general preference.

**Field:** `active_session_id`. **Owner:** Temporary controls, proxies and baking settings. **Data type:** String.

#### Lock Original Target

Freeze the original target's transform channels while a proxy is actively driving it, preventing accidental edits New-data default: Off.

**Field:** `lock_original_target`. **Owner:** Temporary controls, proxies and baking settings. **Data type:** Bool.

### Matching and space switching settings

#### Match Space

Reference space for matching: world, parent, target, visual, or local New-data default: World. Choices: World: Match the control to world-space identity or a world-space reference. (`WORLD`); Parent: Match the control to its parent's transform. (`PARENT`); Target: Match the control to another selected object or bone. (`TARGET`); Visual Matrix: Match using the fully evaluated visual (depsgraph) matrix. (`VISUAL`); Local Matrix: Match using the unevaluated local matrix of the source. (`LOCAL`).

**Field:** `match_space`. **Owner:** Matching and space switching settings. **Data type:** Enum.

#### Match Channels

Which transform channels to include in the match operation New-data default: All (TRS). Choices: All (TRS): Match location, rotation, and scale. (`ALL`); Location: Match location channels only. (`LOCATION`); Rotation: Match rotation channels only. (`ROTATION`); Scale: Match scale channels only. (`SCALE`); Loc + Rot: Match location and rotation, skip scale. (`LOC_ROT`).

**Field:** `match_channels`. **Owner:** Matching and space switching settings. **Data type:** Enum.

#### Axis Filter

Per-axis toggle for the match operation (X, Y, Z) New-data default: True, True, True. Components: 3.

**Field:** `match_axis`. **Owner:** Matching and space switching settings. **Data type:** BoolVector.

#### Maintain Offset

Preserve the existing spatial offset between source and target rather than snapping exactly to the source position New-data default: Off.

**Field:** `maintain_offset`. **Owner:** Matching and space switching settings. **Data type:** Bool.

#### Compensation Range

Frame range over which to apply space-switch compensation New-data default: Current Frame. Choices: Current Frame: Compensate only the current frame. (`SINGLE`); Selected Keys: Compensate across selected keyframes. (`SELECTION`); Custom Range: Compensate within a manually specified frame range. (`CUSTOM`); Preview Range: Compensate across the scene preview/playback range. (`PREVIEW`).

**Field:** `comp_range`. **Owner:** Matching and space switching settings. **Data type:** Enum.

#### Start

Custom compensation range start frame New-data default: 1.0.

**Field:** `comp_range_start`. **Owner:** Matching and space switching settings. **Data type:** Float.

#### End

Custom compensation range end frame New-data default: 250.0.

**Field:** `comp_range_end`. **Owner:** Matching and space switching settings. **Data type:** Float.

#### Switch Type

What kind of property is being switched (enum, boolean, influence, custom) New-data default: Enum / Integer. Choices: Enum / Integer: Switch an integer or enum custom property. (`ENUM`); Boolean: Toggle a boolean (0/1) custom property. (`BOOL`); Constraint Influence: Blend a constraint's influence between 0 and 1. (`INFLUENCE`); Custom Property: Switch a generic numeric custom property. (`CUSTOM`).

**Field:** `switch_kind`. **Owner:** Matching and space switching settings. **Data type:** Enum.

#### Property Path

RNA or custom-property data path of the switch control (e.g. '["space_switch"]' or 'constraints["Child Of"].influence') New-data default: empty.

**Field:** `switch_prop_path`. **Owner:** Matching and space switching settings. **Data type:** String.

#### Switch Bone

Name of the pose bone owning the switch property (empty for object-level) New-data default: empty.

**Field:** `switch_bone_name`. **Owner:** Matching and space switching settings. **Data type:** String.

#### New Value

The value to set the switch property to New-data default: .

**Field:** `switch_new_value`. **Owner:** Matching and space switching settings. **Data type:** Float.

#### Auto Compensate

Automatically compensate the visual transform when a space-switch property is changed so the control does not visually jump New-data default: On.

**Field:** `auto_compensate`. **Owner:** Matching and space switching settings. **Data type:** Bool.

#### Auto-Key Switch

Automatically insert keyframes on compensated transform channels after a space-switch operation New-data default: On.

**Field:** `auto_key_switch`. **Owner:** Matching and space switching settings. **Data type:** Bool.

#### Switch Preview

Enable preview mode: show the compensation result before committing. Cancel to revert. New-data default: Off.

**Field:** `switch_preview`. **Owner:** Matching and space switching settings. **Data type:** Bool.

#### Respect Locked Transforms

Skip transform channels that are locked on the target object or bone New-data default: On.

**Field:** `respect_locks`. **Owner:** Matching and space switching settings. **Data type:** Bool.

#### Respect Driven Channels

Skip transform channels that are controlled by drivers or constraints, where overriding them would be unsafe New-data default: On.

**Field:** `respect_drivers`. **Owner:** Matching and space switching settings. **Data type:** Bool.

#### Contact Preservation

During multi-frame compensation, try to keep contact points (hands, feet) planted by blending compensation near contact frames New-data default: Off.

**Field:** `contact_preserve`. **Owner:** Matching and space switching settings. **Data type:** Bool.

#### Contact Mask

Comma-separated list of bone names to treat as contact points (e.g. "foot_ik_L, foot_ik_R, hand_ik_L, hand_ik_R") New-data default: empty.

**Field:** `contact_mask`. **Owner:** Matching and space switching settings. **Data type:** String.

#### Show Chain Resolver

Expand the IK Chain Resolver section in the panel New-data default: Off.

**Field:** `show_chain_resolver`. **Owner:** Matching and space switching settings. **Data type:** Bool.

#### Include Muted

Include IK constraints that are currently muted in chain detection results (useful for inspecting disabled setups) New-data default: Off.

**Field:** `chain_include_muted`. **Owner:** Matching and space switching settings. **Data type:** Bool.

#### Highlight Chain Members

Highlight all bones belonging to the selected IK chain in the viewport for visual feedback New-data default: On.

**Field:** `chain_highlight_members`. **Owner:** Matching and space switching settings. **Data type:** Bool.

#### Auto-Detect on Selection

Automatically detect IK chains when the active bone changes, keeping the chain info panel up to date New-data default: On.

**Field:** `chain_auto_detect`. **Owner:** Matching and space switching settings. **Data type:** Bool.

#### Selected Chain

Index of the currently inspected IK chain in the results list New-data default: . Allowed range: 0 to no explicit upper limit.

**Field:** `chain_selected_index`. **Owner:** Matching and space switching settings. **Data type:** Int.

#### Last Armature

Name of the armature used in the most recent chain detection New-data default: empty.

**Field:** `chain_last_armature`. **Owner:** Matching and space switching settings. **Data type:** String.

#### Detected Count

Number of IK chains found in the most recent detection run New-data default: . Allowed range: 0 to no explicit upper limit.

**Field:** `chain_last_count`. **Owner:** Matching and space switching settings. **Data type:** Int.

#### Detected Pattern

Index of the currently selected detected switch pattern New-data default: . Allowed range: 0 to no explicit upper limit.

**Field:** `detected_pattern_index`. **Owner:** Matching and space switching settings. **Data type:** Int.

#### Preset Name

Name for saving or loading a switch preset configuration New-data default: empty.

**Field:** `switch_preset_name`. **Owner:** Matching and space switching settings. **Data type:** String.

### Mirror pair overrides

#### Bone A

First bone in the manual pair New-data default: empty.

**Field:** `bone_a`. **Owner:** Mirror pair overrides. **Data type:** String.

#### Bone B

Second bone in the manual pair (opposite side) New-data default: empty.

**Field:** `bone_b`. **Owner:** Mirror pair overrides. **Data type:** String.

### Mirror naming exceptions

#### Original

Original bone name New-data default: empty.

**Field:** `original`. **Owner:** Mirror naming exceptions. **Data type:** String.

#### Opposite

Opposite bone name override New-data default: empty.

**Field:** `opposite`. **Owner:** Mirror naming exceptions. **Data type:** String.

### Mirroring and pair management settings

#### Mirror Axis

Axis to mirror transforms across New-data default: X Axis. Choices: X Axis: Mirror across X axis (left/right) (`X`); Y Axis: Mirror across Y axis (front/back) (`Y`); Z Axis: Mirror across Z axis (up/down) (`Z`).

**Field:** `mirror_axis`. **Owner:** Mirroring and pair management settings. **Data type:** Enum.

#### Mirror Space

Coordinate space for mirror operations New-data default: Local. Choices: Local: Mirror using local space (standard for most rigs) (`LOCAL`); World: Mirror using world space (`WORLD`); Visual: Mirror using evaluated visual matrices (for constrained rigs) (`VISUAL`).

**Field:** `mirror_space`. **Owner:** Mirroring and pair management settings. **Data type:** Enum.

#### Naming Pattern

Bone naming convention for pair detection New-data default: Auto Detect. Choices: Auto Detect: Automatically detect naming convention (`AUTO`); .L/.R: Detect bones ending in .L and .R (`DOT_LR`); _L/_R: Detect bones ending in _L and _R (`UNDER_LR`); Left/Right: Detect bones containing Left or Right in the name (`WORD_LR`); Custom: Use custom regex patterns (`CUSTOM`).

**Field:** `naming_pattern`. **Owner:** Mirroring and pair management settings. **Data type:** Enum.

#### Left Pattern

Regex pattern matching left-side bones New-data default: empty.

**Field:** `custom_left_pattern`. **Owner:** Mirroring and pair management settings. **Data type:** String.

#### Right Pattern

Regex pattern matching right-side bones New-data default: empty.

**Field:** `custom_right_pattern`. **Owner:** Mirroring and pair management settings. **Data type:** String.

#### Location

Include location channels in mirror New-data default: On.

**Field:** `mirror_location`. **Owner:** Mirroring and pair management settings. **Data type:** Bool.

#### Rotation

Include rotation channels in mirror New-data default: On.

**Field:** `mirror_rotation`. **Owner:** Mirroring and pair management settings. **Data type:** Bool.

#### Scale

Include scale channels in mirror New-data default: On.

**Field:** `mirror_scale`. **Owner:** Mirroring and pair management settings. **Data type:** Bool.

#### Axis Mask

Per-axis enable mask for mirroring New-data default: True, True, True. Components: 3.

**Field:** `axis_mask`. **Owner:** Mirroring and pair management settings. **Data type:** BoolVector.

#### Respect Locks

Skip locked transform channels during mirror New-data default: On.

**Field:** `respect_locks`. **Owner:** Mirroring and pair management settings. **Data type:** Bool.

#### Respect Drivers

Skip driven channels during mirror New-data default: On.

**Field:** `respect_drivers`. **Owner:** Mirroring and pair management settings. **Data type:** Bool.

#### Auto Key

Automatically insert keyframes after mirror operations New-data default: On.

**Field:** `auto_key_mirror`. **Owner:** Mirroring and pair management settings. **Data type:** Bool.

#### Maintain Offset

Preserve existing offset between source and target during mirror New-data default: Off.

**Field:** `maintain_offset`. **Owner:** Mirroring and pair management settings. **Data type:** Bool.

#### Keyed Only

Only mirror channels that have keyframes New-data default: Off.

**Field:** `mirror_keyed_only`. **Owner:** Mirroring and pair management settings. **Data type:** Bool.

#### Visible Only

Only mirror channels visible in the editor New-data default: Off.

**Field:** `mirror_visible_only`. **Owner:** Mirroring and pair management settings. **Data type:** Bool.

#### Pair Overrides

Manual bone pair definitions that override auto-detection

**Field:** `pair_overrides`. **Owner:** Mirroring and pair management settings. **Data type:** Collection.

#### Active Override

Active row in the associated list; the interface updates this as you select a row. New-data default: . Allowed range: 0 to no explicit upper limit.

**Field:** `pair_overrides_index`. **Owner:** Mirroring and pair management settings. **Data type:** Int.

#### Naming Exceptions

Bone naming overrides for non-standard names

**Field:** `naming_exceptions`. **Owner:** Mirroring and pair management settings. **Data type:** Collection.

#### Active Exception

Active row in the associated list; the interface updates this as you select a row. New-data default: . Allowed range: 0 to no explicit upper limit.

**Field:** `naming_exceptions_index`. **Owner:** Mirroring and pair management settings. **Data type:** Int.

### Bone metadata records

#### Object

Object associated with this metadata record New-data default: empty.

**Field:** `object_name`. **Owner:** Bone metadata records. **Data type:** String.

#### Bone

Bone associated with this metadata record New-data default: empty.

**Field:** `bone_name`. **Owner:** Bone metadata records. **Data type:** String.

#### Data

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: {}.

**Field:** `metadata_json`. **Owner:** Bone metadata records. **Data type:** String.

### Object metadata

#### Tool State

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: {}.

**Field:** `tool_state_json`. **Owner:** Object metadata. **Data type:** String.

#### Last Tool

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: empty.

**Field:** `last_tool`. **Owner:** Object metadata. **Data type:** String.

#### Flags

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: .

**Field:** `flags`. **Owner:** Object metadata. **Data type:** Int.

### Frame bookmarks

#### Name

Display name of the frame bookmark New-data default: Bookmark.

**Field:** `name`. **Owner:** Frame bookmarks. **Data type:** String.

#### Frame

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: 1.

**Field:** `frame`. **Owner:** Frame bookmarks. **Data type:** Int.

### Key metadata records

#### Object

Object whose animation this record belongs to New-data default: empty.

**Field:** `object_name`. **Owner:** Key metadata records. **Data type:** String.

#### Data Path

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: empty.

**Field:** `data_path`. **Owner:** Key metadata records. **Data type:** String.

#### Array Index

Active row in the associated list; the interface updates this as you select a row. New-data default: .

**Field:** `array_index`. **Owner:** Key metadata records. **Data type:** Int.

#### Frame

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: .

**Field:** `frame`. **Owner:** Key metadata records. **Data type:** Float.

#### Tag

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: empty.

**Field:** `tag`. **Owner:** Key metadata records. **Data type:** String.

#### Note

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: empty.

**Field:** `note`. **Owner:** Key metadata records. **Data type:** String.

#### Protected

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: Off.

**Field:** `protected`. **Owner:** Key metadata records. **Data type:** Bool.

#### Flavor

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: empty.

**Field:** `flavor`. **Owner:** Key metadata records. **Data type:** String.

### Channel masks

#### Use Mask

Limit Anim Offset propagation to the masked frame range New-data default: On.

**Field:** `enabled`. **Owner:** Channel masks. **Data type:** Bool.

#### Start

First frame of the Anim Offset mask New-data default: 1.

**Field:** `start_frame`. **Owner:** Channel masks. **Data type:** Int.

#### End

Last frame of the Anim Offset mask New-data default: 250.

**Field:** `end_frame`. **Owner:** Channel masks. **Data type:** Int.

#### Blend In

Blend-in frames on the left edge of the mask New-data default: 5. Allowed range: 0 to no explicit upper limit.

**Field:** `blend_left`. **Owner:** Channel masks. **Data type:** Int.

#### Blend Out

Blend-out frames on the right edge of the mask New-data default: 5. Allowed range: 0 to no explicit upper limit.

**Field:** `blend_right`. **Owner:** Channel masks. **Data type:** Int.

### General scene settings

#### Migration Version

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: .

**Field:** `migration_version`. **Owner:** General scene settings. **Data type:** Int.

#### Bone Metadata

Collection of records managed by the corresponding list and its add/remove commands.

**Field:** `bone_metadata`. **Owner:** General scene settings. **Data type:** Collection.

#### Anim Offset Active

Whether the Anim Offset modal operator is currently running New-data default: Off.

**Field:** `anim_offset_active`. **Owner:** General scene settings. **Data type:** Bool.

#### Mask

Assigned data owner or settings record. Choose or initialise it through the matching workflow.

**Field:** `mask`. **Owner:** General scene settings. **Data type:** Pointer.

#### Reference Frame

Frame used as blend target by Blend Frame and Push/Pull operators New-data default: .

**Field:** `reference_frame`. **Owner:** General scene settings. **Data type:** Int.

#### Bookmarks

Collection of records managed by the corresponding list and its add/remove commands.

**Field:** `bookmarks`. **Owner:** General scene settings. **Data type:** Collection.

#### Active Bookmark

Active row in the associated list; the interface updates this as you select a row. New-data default: . Allowed range: 0 to no explicit upper limit.

**Field:** `active_bookmark_index`. **Owner:** General scene settings. **Data type:** Int.

#### Key Metadata

Collection of records managed by the corresponding list and its add/remove commands.

**Field:** `key_metadata`. **Owner:** General scene settings. **Data type:** Collection.

#### Compact Panel

Show Curve Tools as a single compact column instead of sub-panels New-data default: Off.

**Field:** `panel_compact`. **Owner:** General scene settings. **Data type:** Bool.

#### Breakdown

Show breakdown percentage and drag buttons in the header toolbar New-data default: On.

**Field:** `header_show_breakdown`. **Owner:** General scene settings. **Data type:** Bool.

#### Push/Pull

Show push/pull directional buttons in the header toolbar New-data default: On.

**Field:** `header_show_pushpull`. **Owner:** General scene settings. **Data type:** Bool.

#### Retime

Show retime speed-scaling presets in the header toolbar New-data default: On.

**Field:** `header_show_retime`. **Owner:** General scene settings. **Data type:** Bool.

#### Selection

Show key selection shortcuts in the Dope Sheet header toolbar New-data default: On.

**Field:** `header_show_selection`. **Owner:** General scene settings. **Data type:** Bool.

#### Trajectory

Show trajectory overlay toggles in the 3D Viewport header toolbar New-data default: On.

**Field:** `header_show_trajectory`. **Owner:** General scene settings. **Data type:** Bool.

#### Matching

Show quick-match buttons (W/P/V) in the 3D Viewport header toolbar New-data default: On.

**Field:** `header_show_matching`. **Owner:** General scene settings. **Data type:** Bool.

### Session control state

#### Tool Active

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: Off.

**Field:** `is_tool_active`. **Owner:** Session control state. **Data type:** Bool.

#### Active Tool

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: empty.

**Field:** `active_tool_name`. **Owner:** Session control state. **Data type:** String.

#### Op Time

Field used by the named workflow or command. The owning record and identifier below distinguish it from similarly named controls. New-data default: .

**Field:** `last_operator_time`. **Owner:** Session control state. **Data type:** Float.

### Foldout section state

#### Panel

bl_idname of the owning panel New-data default: empty.

**Field:** `panel_id`. **Owner:** Foldout section state. **Data type:** String.

#### Section

Stable identifier for the subsection within its panel New-data default: empty.

**Field:** `section_key`. **Owner:** Foldout section state. **Data type:** String.

#### Expanded

Whether this subsection is currently expanded New-data default: On.

**Field:** `expanded`. **Owner:** Foldout section state. **Data type:** Bool.

### Interface state

#### Prefer Compact

Default to a compact layout for foundation-aware panels. Independent of the addon-pref Compact UI Mode toggle so it can be flipped per-session without touching preferences New-data default: Off.

**Field:** `prefer_compact`. **Owner:** Interface state. **Data type:** Bool.

#### Show Analysis Details

Show the details list under analysis/report boxes. When disabled only the summary line and counts are drawn New-data default: On.

**Field:** `show_analysis_details`. **Owner:** Interface state. **Data type:** Bool.

#### Show Advanced By Default

Open Advanced subsections automatically the first time a panel is drawn in a session New-data default: Off.

**Field:** `show_advanced_default`. **Owner:** Interface state. **Data type:** Bool.

#### Sections

Collection of records managed by the corresponding list and its add/remove commands.

**Field:** `sections`. **Owner:** Interface state. **Data type:** Collection.

### Addon preferences and module switches

#### Debug Mode

Enable verbose logging to the console New-data default: Off.

**Field:** `debug_mode`. **Owner:** Addon preferences and module switches. **Data type:** Bool.

#### Performance Mode

Reduce UI updates and diagnostics for better performance New-data default: Off.

**Field:** `performance_mode`. **Owner:** Addon preferences and module switches. **Data type:** Bool.

#### Show Diagnostics Panel

Show the diagnostics panel in Properties > Scene > Anim Assist > Help & Diagnostics New-data default: Off.

**Field:** `diagnostics_visible`. **Owner:** Addon preferences and module switches. **Data type:** Bool.

#### Show Extended Help Popups

Show Anim Assist question-mark buttons that open detailed help popups; native Bforartists hover tooltips are unaffected New-data default: On.

**Field:** `show_explainer_help`. **Owner:** Addon preferences and module switches. **Data type:** Bool.

#### Compact UI Mode

Draw explainer icons without their neighbouring text labels to keep sidebar panels dense on small screens New-data default: Off.

**Field:** `compact_ui_mode`. **Owner:** Addon preferences and module switches. **Data type:** Bool.

#### Fast Offset Mode

Only propagate Anim Offset on mouse release (faster for complex rigs) New-data default: Off.

**Field:** `animassist_fast_offset`. **Owner:** Addon preferences and module switches. **Data type:** Bool.

#### Auto-key Outside Margins

Auto-insert keys for frames outside the mask blend region during Anim Offset New-data default: Off.

**Field:** `animassist_autokey_outside_margins`. **Owner:** Addon preferences and module switches. **Data type:** Bool.

#### Drag Sensitivity

Mouse pixels needed to reach factor 1.0 in modal drag operators New-data default: 200. Allowed range: 10 to 2000.

**Field:** `animassist_drag_sensitivity`. **Owner:** Addon preferences and module switches. **Data type:** Int.

#### Dense Key Min Gap

Frames below this count as 'too dense' in the diagnostics scan New-data default: 1.0. Allowed range: 0.0 to no explicit upper limit.

**Field:** `p2_dense_min_gap`. **Owner:** Addon preferences and module switches. **Data type:** Float.

#### Redundant Key Tolerance

Value tolerance for flagging a key as redundant (lies on a line) New-data default: 0.0001. Allowed range: 0.0 to no explicit upper limit.

**Field:** `p2_redundant_tolerance`. **Owner:** Addon preferences and module switches. **Data type:** Float.

#### Spike Ratio

Neighbour deviation ratio at which a key is flagged as a spike New-data default: 4.0. Allowed range: 1.0 to no explicit upper limit.

**Field:** `p2_spike_ratio`. **Owner:** Addon preferences and module switches. **Data type:** Float.

#### Anim Assist Pie Menu Hotkey

Open the Anim Assist pie with a shortcut in the 3D Viewport, Graph Editor and Dope Sheet (Shift Alt D unless you change it) New-data default: Off.

**Field:** `pie_hotkey_enabled`. **Owner:** Addon preferences and module switches. **Data type:** Bool.

#### 3D Viewport

Show the Anim Assist menu in the 3D Viewport header New-data default: On.

**Field:** `header_menu_view3d`. **Owner:** Addon preferences and module switches. **Data type:** Bool.

#### Graph Editor

Show the Anim Assist menu in the Graph Editor header New-data default: On.

**Field:** `header_menu_graph`. **Owner:** Addon preferences and module switches. **Data type:** Bool.

#### Dope Sheet

Show the Anim Assist menu in the Dope Sheet header New-data default: On.

**Field:** `header_menu_dopesheet`. **Owner:** Addon preferences and module switches. **Data type:** Bool.

#### Selection Tools

Enable keyframe and channel selection tools New-data default: On.

**Field:** `enable_selection`. **Owner:** Addon preferences and module switches. **Data type:** Bool.

#### Key Utilities

Enable key editing and metadata utilities New-data default: On.

**Field:** `enable_keys`. **Owner:** Addon preferences and module switches. **Data type:** Bool.

#### Transform Workflows

Enable transform and animation offset workflows New-data default: On.

**Field:** `enable_transform`. **Owner:** Addon preferences and module switches. **Data type:** Bool.

#### Breakdown Tools

Enable breakdown, inbetween, and pose comparison tools New-data default: On.

**Field:** `enable_breakdown`. **Owner:** Addon preferences and module switches. **Data type:** Bool.

#### Trajectory Tools

Enable trajectory overlays and arc diagnostics New-data default: On.

**Field:** `enable_trajectory`. **Owner:** Addon preferences and module switches. **Data type:** Bool.

#### Retime Tools

Enable keyframe timing, ripple, and time-warp tools New-data default: On.

**Field:** `enable_retime`. **Owner:** Addon preferences and module switches. **Data type:** Bool.

#### Temp Controls

Enable temporary proxy and rig control tools New-data default: On.

**Field:** `enable_controls`. **Owner:** Addon preferences and module switches. **Data type:** Bool.

#### Matching Workflows

Enable transform matching and IK/FK switching tools New-data default: On.

**Field:** `enable_matching`. **Owner:** Addon preferences and module switches. **Data type:** Bool.

#### Animation Layers

Enable the animation-layer workflow New-data default: On.

**Field:** `enable_layers`. **Owner:** Addon preferences and module switches. **Data type:** Bool.

## Reference D. Command lookup index

The identifiers below link labels to the exact source-defined commands. Search the PDF for an identifier or label to locate its detailed reference. Internal and automatic helpers are identified in their entries.

- `anim_assist.copy_diagnostics` - Copy Diagnostics

- `anim_assist.export_settings` - Export AnimAssist Settings

- `anim_assist.import_settings` - Import AnimAssist Settings

- `anim_assist.refresh_diagnostics` - Refresh Diagnostics

- `anim_assist.show_help_popup` - Anim Assist Help

- `animassist.add_bookmark` - Add Frame Bookmark

- `animassist.add_workspace` - Add Anim Assist Workspace

- `animassist.anim_offset` - Anim Offset

- `animassist.anim_offset_range_from_scene` - Range from Scene

- `animassist.anim_offset_set_range` - Set Offset Range

- `animassist.anim_offset_toggle_mask` - Toggle Mask

- `animassist.apply_preset` - Apply Preset

- `animassist.batch_interpolation` - Batch Set Interpolation

- `animassist.blend_frame` - Blend Frame

- `animassist.blend_neighbor` - Blend to Neighbor

- `animassist.blend_offset` - Blend Offset

- `animassist.blend_toward_reference` - Blend Toward Reference

- `animassist.breakdown_batch_frames` - Batch Over Selected Frames

- `animassist.breakdown_channel_subset` - Custom Channel Subset

- `animassist.breakdown_current_frame` - Breakdown at Current Frame

- `animassist.breakdown_favor_next` - Favor Next Pose

- `animassist.breakdown_favor_prev` - Favor Previous Pose

- `animassist.breakdown_from_clipboard` - Breakdown From Clipboard

- `animassist.breakdown_location_only` - Location Only

- `animassist.breakdown_midpoint` - Midpoint Breakdown

- `animassist.breakdown_numeric` - Numeric Breakdown

- `animassist.breakdown_offset` - Relative Offset

- `animassist.breakdown_percentage` - Quick Percentage Breakdown

- `animassist.breakdown_pull_next` - Pull To Next

- `animassist.breakdown_pull_prev` - Pull To Previous

- `animassist.breakdown_push_next` - Push Into Next

- `animassist.breakdown_push_prev` - Push From Previous

- `animassist.breakdown_repeat_last` - Repeat Last Breakdown

- `animassist.breakdown_rotation_only` - Rotation Only

- `animassist.breakdown_scale_only` - Scale Only

- `animassist.breakdown_selected_controls` - Selected Controls Only

- `animassist.breakdown_transform_only` - Transform Only

- `animassist.breakdown_weighted` - Weighted Previous/Next

- `animassist.clear_all_key_metadata` - Clear All Key Metadata

- `animassist.clear_tag_selected_keys` - Clear Tags on Selected Keys

- `animassist.commit_preview` - Commit Preview

- `animassist.copy_selected_keys` - Copy Selected Keys

- `animassist.deep_uninstall` - Anim Assist: Deep Uninstall (Purge All Data)

- `animassist.delete_by_key_type` - Delete by Key Type

- `animassist.delete_preset` - Delete Preset

- `animassist.deselect_all_visible` - Deselect All Visible Keys

- `animassist.ease_to_ease` - Ease To Ease

- `animassist.inbetween_distribute` - Evenly Distribute Inbetweens

- `animassist.inbetween_on_clusters` - Inbetween on Clusters

- `animassist.inbetween_selected_gap` - Inbetween in Selected Gap

- `animassist.insert_frames` - Insert Frames

- `animassist.invert_channel_visibility` - Invert Channel Visibility

- `animassist.invert_selection` - Invert Key Selection

- `animassist.isolate_by_regex` - Isolate Channels by Regex

- `animassist.isolate_custom_props` - Isolate Custom Properties

- `animassist.isolate_selected_bones` - Isolate Selected Bones

- `animassist.isolate_selected_channels` - Isolate Selected Channels

- `animassist.isolate_transform` - Isolate Transform Channels

- `animassist.manage_exclusion_set` - Manage Exclusion Set

- `animassist.mirror_selected_keys` - Mirror Selected Keys at Current Frame

- `animassist.modal_drag_breakdown` - Modal Drag Breakdown

- `animassist.move_keys` - Move Keys

- `animassist.mute_unselected_channels` - Mute Unselected Channels

- `animassist.offset_selected_frames` - Offset Selected Keys (Frame)

- `animassist.offset_selected_values` - Offset Selected Keys (Value)

- `animassist.open_home` - Open Anim Assist Panel

- `animassist.open_home_window` - Open in Separate Window

- `animassist.p10_add_favorite` - Add to Favorites

- `animassist.p10_add_macro` - Add Macro

- `animassist.p10_add_macro_step` - Add Macro Step

- `animassist.p10_batch_bookmarked` - Batch: Bookmarked Frames

- `animassist.p10_batch_frame_steps` - Batch: Frame Steps

- `animassist.p10_batch_selected` - Batch: Selected Targets

- `animassist.p10_check_hotkey_conflicts` - Check Hotkey Conflicts

- `animassist.p10_clear_errors` - Clear Errors

- `animassist.p10_clear_history` - Clear History

- `animassist.p10_clear_recents` - Clear Recents

- `animassist.p10_clear_snapshots` - Clear Snapshots

- `animassist.p10_export_workspace` - Export Workspace Profile

- `animassist.p10_final_validation` - Final Validation

- `animassist.p10_first_run_setup` - First Run Setup

- `animassist.p10_import_workspace` - Import Workspace Profile

- `animassist.p10_leak_check` - Leak Check

- `animassist.p10_list_snapshots` - List Snapshots

- `animassist.p10_load_demo_config` - Load Demo Config

- `animassist.p10_load_profile` - Load Profile

- `animassist.p10_macro_breakdown_offset` - Breakdown + Offset

- `animassist.p10_macro_diagnose_jump` - Diagnose + Jump

- `animassist.p10_macro_mirror_match` - Mirror + Match

- `animassist.p10_macro_proxy_workflow` - Proxy Workflow

- `animassist.p10_macro_switch_compensate` - Switch + Compensate

- `animassist.p10_metadata_cleanup` - Metadata Cleanup

- `animassist.p10_pie_breakdown` - Breakdown Pie

- `animassist.p10_pie_key_tools` - Key Tools Pie

- `animassist.p10_pie_proxy` - Proxy Controls Pie

- `animassist.p10_pie_switch` - Space Switch Pie

- `animassist.p10_pie_symmetry` - Symmetry Pie

- `animassist.p10_pie_transform` - Transform Pie

- `animassist.p10_rebuild_caches` - Rebuild Caches

- `animassist.p10_record_recent` - Record Recent Tool

- `animassist.p10_remove_favorite` - Remove Favorite

- `animassist.p10_remove_macro` - Remove Macro

- `animassist.p10_remove_macro_step` - Remove Macro Step

- `animassist.p10_remove_profile` - Remove Profile

- `animassist.p10_repeat_last` - Repeat Last Tool

- `animassist.p10_reset_ui` - Reset UI State

- `animassist.p10_restore_snapshot` - Restore Snapshot

- `animassist.p10_run_custom_macro` - Run Custom Macro

- `animassist.p10_safe_disable` - Safe Disable

- `animassist.p10_save_profile` - Save Profile

- `animassist.p10_search_tools` - Search Tools

- `animassist.p10_show_errors` - Show Error Log

- `animassist.p10_show_history` - Show Operation History

- `animassist.p10_show_stats` - Session Statistics

- `animassist.p10_stale_cleanup` - Stale Cleanup

- `animassist.p10_system_diagnostics` - System Diagnostics

- `animassist.p10_tag_preset` - Tag Preset

- `animassist.p10_take_snapshot` - Take Snapshot

- `animassist.p10_toggle_debug` - Toggle Debug Panel

- `animassist.p10_toggle_shelf_mode` - Toggle Shelf Mode

- `animassist.p10_validate_macro` - Validate Macro

- `animassist.p10_validate_registration` - Validate Registration

- `animassist.p11_add_channel_override` - Add Channel Override

- `animassist.p11_add_layer` - Add Layer

- `animassist.p11_assign_by_pattern` - Assign by Pattern

- `animassist.p11_assign_selected` - Assign Selected

- `animassist.p11_auto_partition` - Auto-Partition Layers

- `animassist.p11_blend_layers` - Blend Between Layers

- `animassist.p11_clear_assignments` - Clear Assignments

- `animassist.p11_duplicate_layer` - Duplicate Layer

- `animassist.p11_evaluate_stack` - Evaluate Layer Stack

- `animassist.p11_flatten_all` - Flatten All Layers

- `animassist.p11_init_layers` - Initialize Layers

- `animassist.p11_load_preset` - Load Layer Preset

- `animassist.p11_merge_down` - Merge Down

- `animassist.p11_move_layer_down` - Move Layer Down

- `animassist.p11_move_layer_up` - Move Layer Up

- `animassist.p11_remove_bone` - Remove Bone

- `animassist.p11_remove_channel_override` - Remove Channel Override

- `animassist.p11_remove_layer` - Remove Layer

- `animassist.p11_remove_preset` - Remove Preset

- `animassist.p11_remove_selected` - Remove Selected

- `animassist.p11_rename_layer` - Rename Layer

- `animassist.p11_save_preset` - Save Layer Preset

- `animassist.p11_select_assigned` - Select Assigned Bones

- `animassist.p11_select_layer` - Select Layer

- `animassist.p11_set_active` - Set Active Layer

- `animassist.p11_set_blend_factor` - Set Blend Factor

- `animassist.p11_set_blend_mode` - Set Blend Mode

- `animassist.p11_set_weight` - Set Layer Weight

- `animassist.p11_toggle_lock` - Toggle Lock

- `animassist.p11_toggle_mute` - Toggle Mute

- `animassist.p11_toggle_solo` - Toggle Solo

- `animassist.p12_autofill_shape_key_wiring` - Autofill Shape Key Wiring

- `animassist.p12_autofill_wiring` - Autofill Rig Wiring

- `animassist.p12_bake_lipsync` - Bake Lipsync

- `animassist.p12_capture_viseme` - Capture Viseme

- `animassist.p12_capture_viseme_shape` - Capture Viseme (Shape Keys)

- `animassist.p12_clear_auto_keys` - Clear Auto Keys

- `animassist.p12_install_drivers` - Install Lipsync Drivers

- `animassist.p12_mark_manual` - Mark as Manual Override

- `animassist.p12_pick_mesh` - Use Active Mesh

- `animassist.p12_rebake` - Rebake Lipsync

- `animassist.p12_refresh_audio_hash` - Refresh Audio Hash

- `animassist.p12_remove_drivers` - Remove Lipsync Drivers

- `animassist.p12_reset_viseme` - Reset to Built-in

- `animassist.p12_setup_lipsync` - Setup Lipsync

- `animassist.p12_toggle_mode` - Toggle Live Preview <-> Shipped Bake

- `animassist.p4_apply_preset` - Apply Preset

- `animassist.p4_invert_last` - Invert Last Offset

- `animassist.p4_modal_offset` - Modal Drag Offset

- `animassist.p4_nudge_current` - Nudge Current Frame

- `animassist.p4_offset_rotate_only` - Rotation Only

- `animassist.p4_offset_scale_only` - Scale Only

- `animassist.p4_offset_selected` - Offset Selected Keys

- `animassist.p4_offset_translate_only` - Translation Only

- `animassist.p4_offset_trs_combined` - Combined TRS Offset

- `animassist.p4_pull_x` - Pull X

- `animassist.p4_pull_y` - Pull Y

- `animassist.p4_pull_z` - Pull Z

- `animassist.p4_push_x` - Push X

- `animassist.p4_push_y` - Push Y

- `animassist.p4_push_z` - Push Z

- `animassist.p4_reapply_last` - Reapply Last Offset

- `animassist.p4_set_pivot_cursor` - Pivot from 3D Cursor

- `animassist.p4_set_pivot_head` - Pivot from Bone Head

- `animassist.p4_set_pivot_tail` - Pivot from Bone Tail

- `animassist.p5_disable_overlay` - Disable Trajectory Overlay

- `animassist.p5_enable_overlay` - Enable Trajectory Overlay

- `animassist.p5_isolate_target` - Isolate Target

- `animassist.p5_jump_next_issue` - Next Issue

- `animassist.p5_jump_prev_issue` - Previous Issue

- `animassist.p5_mute_unselected` - Mute Unselected

- `animassist.p5_refresh_overlay` - Refresh Trajectory Overlay

- `animassist.p5_run_diagnostics` - Run Arc Diagnostics

- `animassist.p5_select_bad_arc_keys` - Select Bad-Arc Keys

- `animassist.p5_suggest_candidates` - Suggest Candidate Keys

- `animassist.p6_bake_timing` - Bake to Integer Frames

- `animassist.p6_clear_diagnostics` - Clear Diagnostics

- `animassist.p6_clear_doubles` - Remove Duplicates

- `animassist.p6_clear_range` - Clear Range

- `animassist.p6_collapse_gap` - Collapse Gap at Playhead

- `animassist.p6_compress_timing` - Compress Timing

- `animassist.p6_copy_diag_report` - Copy Report

- `animassist.p6_detect_and_fill` - Detect & Fill Gaps

- `animassist.p6_detect_gaps` - Detect Gaps

- `animassist.p6_distribute_keys` - Distribute Keys

- `animassist.p6_fill_gaps` - Fill Gaps

- `animassist.p6_insert_time` - Insert Time

- `animassist.p6_jump_next_cluster` - Next Cluster

- `animassist.p6_jump_next_gap` - Next Gap

- `animassist.p6_jump_prev_gap` - Previous Gap

- `animassist.p6_match_timing` - Match Timing

- `animassist.p6_modal_offset` - Interactive Offset

- `animassist.p6_modal_scale` - Interactive Scale

- `animassist.p6_normalize_spacing` - Normalize Spacing

- `animassist.p6_offset_keys` - Offset Keys

- `animassist.p6_offset_range` - Offset Range

- `animassist.p6_remove_time` - Remove Time

- `animassist.p6_reset_timing` - Reset Timing

- `animassist.p6_restore_range` - Restore Range

- `animassist.p6_reverse_keys` - Reverse Keys

- `animassist.p6_ripple_backward` - Ripple Backward

- `animassist.p6_ripple_forward` - Ripple Forward

- `animassist.p6_ripple_to_end` - Ripple to End

- `animassist.p6_run_diagnostics` - Run Diagnostics

- `animassist.p6_scale_keys` - Scale Keys

- `animassist.p6_scale_range` - Scale Range

- `animassist.p6_select_keys_in_range` - Select Keys in Range

- `animassist.p6_set_pivot` - Set Pivot from Playhead

- `animassist.p6_set_range_end` - Set Range End

- `animassist.p6_set_range_start` - Set Range Start

- `animassist.p6_snap_to_frames` - Snap to Frames

- `animassist.p6_store_range` - Store Range

- `animassist.p6_time_warp` - Time Warp %

- `animassist.p7_apply_offset` - Apply Offset

- `animassist.p7_auto_cleanup` - Auto Cleanup

- `animassist.p7_bake_locator_from_target` - Bake Locator from Target

- `animassist.p7_bake_preserve_timing` - Bake Preserve Timing

- `animassist.p7_bake_preview` - Bake Preview Range

- `animassist.p7_bake_range` - Bake Range

- `animassist.p7_bake_selected` - Bake Selected

- `animassist.p7_bake_selected_channels` - Bake Selected Channels

- `animassist.p7_bake_step` - Bake with Step

- `animassist.p7_bake_target_from_locator` - Bake Target from Locator

- `animassist.p7_batch_create_proxies` - Batch Create Proxies

- `animassist.p7_check_setup` - Check Setup

- `animassist.p7_cleanup_all` - Cleanup All Sessions

- `animassist.p7_cleanup_session` - Cleanup Session

- `animassist.p7_constrain_locator_to_target` - Constrain Locator  ->  Target

- `animassist.p7_constrain_target_to_locator` - Constrain Target  ->  Locator

- `animassist.p7_create_locator` - Create Locator at Target

- `animassist.p7_create_locator_average` - Locator at Average

- `animassist.p7_create_locator_cursor` - Locator at Cursor

- `animassist.p7_create_proxy` - Create Proxy

- `animassist.p7_export_session` - Export Session

- `animassist.p7_list_sessions` - List Sessions

- `animassist.p7_lock_target` - Lock Target

- `animassist.p7_match_locator_to_target` - Match Locator  ->  Target

- `animassist.p7_match_target_to_locator` - Match Target  ->  Locator

- `animassist.p7_mirror_proxy` - Mirror Proxy

- `animassist.p7_mute_constraints` - Mute Constraints

- `animassist.p7_one_click_cleanup` - One-Click Cleanup

- `animassist.p7_one_click_proxy_bake` - One-Click Proxy & Bake

- `animassist.p7_parent_locator` - Parent Locator to Target

- `animassist.p7_purge_artifacts` - Purge Proxy Artifacts

- `animassist.p7_quick_proxy` - Quick Proxy

- `animassist.p7_recenter_proxy` - Recenter Proxy

- `animassist.p7_reconnect_session` - Reconnect Session

- `animassist.p7_recover_session` - Recover Proxy Session

- `animassist.p7_reduce_keys` - Reduce Keys

- `animassist.p7_remove_constraints` - Remove Session Constraints

- `animassist.p7_remove_proxy` - Remove Proxy

- `animassist.p7_rename_proxy` - Rename Proxy

- `animassist.p7_set_proxy_color` - Set Proxy Color

- `animassist.p7_show_session_info` - Session Info

- `animassist.p7_smart_bake` - Smart Bake

- `animassist.p7_switch_proxy_mode` - Switch Proxy Mode

- `animassist.p7_temp_pivot` - Temp Pivot

- `animassist.p7_toggle_collection` - Toggle Collection

- `animassist.p7_toggle_display` - Toggle Proxy Display

- `animassist.p7_validate_session` - Validate Session

- `animassist.p7_zero_proxy` - Zero Proxy

- `animassist.p8_apply_detected_pattern` - Apply Detected Pattern

- `animassist.p8_bake_switch_preview` - Bake Switch Preview

- `animassist.p8_bake_switch_range` - Bake Switch Range

- `animassist.p8_batch_switch` - Batch Switch

- `animassist.p8_chain_nav` - Navigate Chains

- `animassist.p8_chain_summary` - Chain Summary

- `animassist.p8_chain_to_match` - Chain  ->  Match

- `animassist.p8_clear_history` - Clear Switch History

- `animassist.p8_compensate_multi` - Compensate Multi

- `animassist.p8_compensate_single` - Compensate Single

- `animassist.p8_compensation_report` - Compensation Report

- `animassist.p8_contact_mask_from_selection` - Contact Mask from Selection

- `animassist.p8_contact_preserve_match` - Contact Preserve Match

- `animassist.p8_debug_diagnostics` - Debug Diagnostics

- `animassist.p8_delete_switch_preset` - Delete Switch Preset

- `animassist.p8_detect_all` - Detect All Patterns

- `animassist.p8_detect_chain_for_bone` - Detect Chain for Bone

- `animassist.p8_detect_chains` - Detect IK Chains

- `animassist.p8_detect_custom_props` - Detect Custom Properties

- `animassist.p8_detect_influence_patterns` - Detect Influence Patterns

- `animassist.p8_detect_parent_patterns` - Detect Parent Patterns

- `animassist.p8_detect_space_enums` - Detect Space Enums

- `animassist.p8_find_bone_chains` - Find Chains for Bone

- `animassist.p8_invalidate_chain_cache` - Clear Chain Cache

- `animassist.p8_load_switch_preset` - Load Switch Preset

- `animassist.p8_match_axis_filtered` - Match Axis Filtered

- `animassist.p8_match_local_matrix` - Match Local Matrix

- `animassist.p8_match_location` - Match Location

- `animassist.p8_match_opposite` - Match Opposite

- `animassist.p8_match_rotation` - Match Rotation

- `animassist.p8_match_scale` - Match Scale

- `animassist.p8_match_selected_to_active` - Match Selected to Active

- `animassist.p8_match_to_parent` - Match to Parent

- `animassist.p8_match_to_target` - Match to Target

- `animassist.p8_match_to_world` - Match to World

- `animassist.p8_match_trs` - Match TRS

- `animassist.p8_match_visual_matrix` - Match Visual Matrix

- `animassist.p8_match_with_offset` - Match with Offset

- `animassist.p8_match_without_offset` - Match without Offset

- `animassist.p8_nav_next_switch` - Next Switch

- `animassist.p8_nav_prev_switch` - Prev Switch

- `animassist.p8_quick_match` - Quick Match

- `animassist.p8_repeat_last_switch` - Repeat Last Switch

- `animassist.p8_restore_switch` - Restore Switch

- `animassist.p8_save_switch_preset` - Save Switch Preset

- `animassist.p8_select_chain_bones` - Select Chain Bones

- `animassist.p8_switch_bool` - Switch Bool

- `animassist.p8_switch_enum` - Switch Enum

- `animassist.p8_switch_influence` - Switch Influence

- `animassist.p8_switch_marker` - Switch Marker

- `animassist.p8_toggle_preview` - Toggle Preview

- `animassist.p8_unsupported_warning` - Unsupported Setup Warning

- `animassist.p8_visual_match` - Visual Match

- `animassist.p9_add_naming_exception` - Add Naming Exception

- `animassist.p9_add_opposite` - Add Opposite to Selection

- `animassist.p9_add_pair_override` - Add Pair Override

- `animassist.p9_ambiguous_warning` - Ambiguous Pair Warning

- `animassist.p9_batch_mirror` - Batch Mirror Selected

- `animassist.p9_batch_mirror_active_side` - Mirror Active Side

- `animassist.p9_build_cache` - Build Pair Cache

- `animassist.p9_channel_resolver` - Channel Resolver

- `animassist.p9_custom_pattern` - Apply Custom Pattern

- `animassist.p9_load_pair_preset` - Load Pair Preset

- `animassist.p9_match_opposite_to_active` - Match Opposite to Active

- `animassist.p9_match_to_opposite` - Match to Opposite

- `animassist.p9_mirror_frame` - Mirror Frame

- `animassist.p9_mirror_keyed_only` - Mirror Keyed Only

- `animassist.p9_mirror_local` - Mirror Local

- `animassist.p9_mirror_location` - Mirror Location

- `animassist.p9_mirror_metadata` - Mirror Metadata

- `animassist.p9_mirror_pose` - Mirror Pose

- `animassist.p9_mirror_preset_values` - Mirror Preset Values

- `animassist.p9_mirror_preview` - Mirror Preview

- `animassist.p9_mirror_proxy_helpers` - Mirror Proxy Helpers

- `animassist.p9_mirror_range` - Mirror Range

- `animassist.p9_mirror_report` - Mirror Report

- `animassist.p9_mirror_rotation` - Mirror Rotation

- `animassist.p9_mirror_scale` - Mirror Scale

- `animassist.p9_mirror_selected` - Mirror Selected

- `animassist.p9_mirror_selection_sets` - Mirror Selection Sets

- `animassist.p9_mirror_switch_targets` - Mirror Switch Targets

- `animassist.p9_mirror_visible_only` - Mirror Visible Only

- `animassist.p9_mirror_with_offset` - Mirror with Offset

- `animassist.p9_mirror_without_offset` - Mirror without Offset

- `animassist.p9_mirror_world` - Mirror World

- `animassist.p9_missing_warning` - Missing Opposite Warning

- `animassist.p9_nav_next_unpaired` - Next Unpaired

- `animassist.p9_remove_naming_exception` - Remove Naming Exception

- `animassist.p9_remove_pair_override` - Remove Pair Override

- `animassist.p9_repeat_mirror` - Repeat Last Mirror

- `animassist.p9_save_pair_preset` - Save Pair Preset

- `animassist.p9_select_opposite` - Select Opposite

- `animassist.p9_swap_poses` - Swap Poses

- `animassist.p9_swap_selection` - Swap Selection

- `animassist.p9_validate_pairs` - Validate Pairs

- `animassist.p9_visual_mirror` - Visual Mirror

- `animassist.paste_keys_at_frame` - Paste Keys at Frame

- `animassist.pop_channel_isolation` - Restore Channel Isolation State

- `animassist.pose_compare_report` - Pose Compare Report

- `animassist.pose_snapshot_next` - Set Next Pose

- `animassist.pose_snapshot_prev` - Set Previous Pose

- `animassist.pose_snapshot_reference` - Set Reference Pose

- `animassist.preview_breakdown` - Preview Breakdown

- `animassist.protect_selected_keys` - Protect Selected Keys

- `animassist.prune_orphan_key_metadata` - Prune Orphan Key Metadata

- `animassist.purge_zombie_classes` - Anim Assist: Repair Registration

- `animassist.push_channel_isolation` - Save Channel Isolation State

- `animassist.push_pull` - Push / Pull

- `animassist.recall_bookmark` - Recall Bookmark

- `animassist.remove_bookmark` - Remove Frame Bookmark

- `animassist.report_saved_versions` - Anim Assist: Check Saved Settings Version

- `animassist.safe_delete_selected_keys` - Safe Delete Selected Keys

- `animassist.save_preset` - Save Preset

- `animassist.scan_dense_keys` - Scan Dense Keys

- `animassist.scan_redundant_keys` - Scan Redundant Keys

- `animassist.scan_spike_keys` - Scan Spike Keys

- `animassist.select_all_visible` - Select All Visible Keys

- `animassist.select_between_selected` - Select Between First/Last Selected

- `animassist.select_by_handle_type_adv` - Select Keys by Handle Type

- `animassist.select_by_interpolation` - Select Keys by Interpolation

- `animassist.select_by_key_type` - Select by Key Type

- `animassist.select_by_key_type_adv` - Select Keys by Type

- `animassist.select_by_tag` - Select Keys by Tag

- `animassist.select_by_value_range` - Select Keys by Value Range

- `animassist.select_every_nth` - Select Every Nth Key

- `animassist.select_first_last` - Select First/Last Keys

- `animassist.select_flat_segments` - Select Keys in Flat Segments

- `animassist.select_frame_range` - Select Keys in Frame Range

- `animassist.select_handles` - Select Handles

- `animassist.select_local_extremes` - Select Local Extremes

- `animassist.select_neighbors` - Extend Selection to Neighbours

- `animassist.select_playback_range` - Select Keys in Playback Range

- `animassist.select_preview_range` - Select Keys in Preview Range

- `animassist.select_protected` - Select Protected Keys

- `animassist.set_handle_type` - Set Handle Type

- `animassist.set_key_flavor` - Set Key Flavor

- `animassist.set_key_note` - Set Note on Selected Keys

- `animassist.set_key_type` - Set Key Type

- `animassist.set_reference_frame` - Set Reference Frame

- `animassist.show_all_channels` - Show All Channels

- `animassist.smooth_keys` - Smooth Keys

- `animassist.snap_keys_to_integer_frames` - Snap Selected Keys to Integer Frames

- `animassist.tag_selected_keys` - Tag Selected Keys
