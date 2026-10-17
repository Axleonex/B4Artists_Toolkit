# Anim Assist 12.9.0 user guide

Reviewed against 12.9.0 on October 17, 2026. Use Dope Sheet for poses/timing, Graph Editor for curves, and NLA Editor for clips/corrections. Help controls explain individual tools.

## Install and find the tools

Download the [12.9.0 add-on ZIP](https://raw.githubusercontent.com/Axleonex/B4Artists_Toolkit/main/releases/b4_anim_assist_v12.9.0.zip). In Bforartists, open Edit > Preferences > Add-ons > Install from Disk. Select the ZIP and enable Anim Assist. Its package is `B4_anim_assist`. Restart after updating.

Validated host: stock Bforartists 5.2.0, Blender 5.3.0 Alpha base, build `0a1ca45552db`, OpenGL. Standard Blender is unsupported; other builds were not validated.

- **Timeline:** Anim Assist's tool row sits at the bottom of the canvas. Playback and keyframing controls remain in the existing native header.
- **Dope Sheet, Graph Editor and NLA Editor:** point into the editor, press N, then choose the Anim Assist tab. The header's Anim Assist menu provides additional access.
- **Scene Properties > Anim Assist:** character setup, broader animation tools, macros, settings and help. There is no Anim Assist tab in the 3D Viewport sidebar.

Scene Properties > Anim Assist > Setup (once per rig) > First Run Setup creates the general Quick Shelf. Setup also offers a workspace. The optional Shift Alt D pie starts off; enable/rebind it in Settings.

## Timeline: buttons and sliders

The row groups tools into **Tween, Timing, Curves, Keys, Pose, Bake and Motion**. Click an action to run it; use family menus or Find for others. Tooltips explain prerequisites and scope. Action-wide offset affects more than selected-key nudging.

**Recommended** starts with two inline sliders: **Breakdown** and **Smooth**. **Timing Scale** uses a temporary popout slider. Quick buttons include 25%, 50% and 75% breakdowns, -1f/+1f nudges, Copy/Paste Keys, Mirror Selected, Bake Object Transforms and Show World Motion Trails.

Press and drag. Release applies; Esc/right-click restores the captured animation. Shift gives finer movement; Ctrl uses the snap step. Type a value and press Enter for numeric input. Clicking without dragging applies nothing. Watch the status bar.

Eight tools support numeric display: Breakdown, Smooth, Neighbors, Reference, Ease, Push/Pull, Timing Scale and Timing Offset. Reference blends toward the configured reference frame; Push/Pull changes amplitude around that reference. Timing Scale changes key spacing: below 100% keys sit closer (faster), above 100% they spread apart (slower); Timing Offset shifts the active object's Action timing. Check tooltips and scene options before editing a whole Action.

### Customize and save layouts

Open row **Settings**, choose a family/tool, then **Hidden, Button, Popout slider or Inline slider**. Ordinary actions offer Hidden/Button only. Hidden tools remain in Search/More. Move Up/Down orders tools within their family; Slider Width controls inline width.

Use **Tool Settings**, or right-click an idle numeric tool, to set label/icon, range, default, width, precision, drag sensitivity, snapping and presets. **Custom Range / Overshoot** permits supported amounts outside the standard range. Masks, targets and breakdown anchors remain scene settings; **Scene Tool Options** opens those separately.

**Save As** names an arrangement. **Load** restores one; **Update Saved** replaces its saved settings. Rename/Delete manage saved layouts. Recommended is protected. **Restore Recommended Layout** resets the working arrangement while retaining saved layouts. Confirm the main Settings dialog to apply staged changes. Save Preferences after applying if automatic preference saving is off.

On a narrow Timeline, tools that do not fit remain available in More and Search. Shorten the row by reducing inline widths or changing occasional sliders to popout/button mode. If hidden, use **Timeline > View > Show Anim Assist Tool Row**. Give the Timeline enough height for its keys and tool row.

The **bottom-only canvas overlay** retains 12.7.1 placement, away from the top keyframe diamonds. It adds no native header/editor region or workspace split. There is no top/bottom placement setting.

### Stage tabs

Tabs at the left of the row choose a stage: **All**, **Block** (Tween, Keys), **Spline** (Curves), **Polish** (Timing, Pose) and **Deliver** (Bake, Motion). A stage shows only those families from your active layout. It never edits saved layouts, tool modes or slider settings. **All** shows every family.

Click a tab, hold Ctrl and scroll over the tabs, or use **Timeline > View > Anim Assist Stage**. Each workspace keeps its own stage, saved with the file. When the row is tight, the tabs collapse into one button that cycles stages before any slider is shortened. Tools outside the stage remain in More and Search.

**Toolbar Settings** (the row's **Settings** button) also shows **Row Stage**. If you configure a family the current stage hides, a note names the stage that shows it; choose that stage or **All** to see your change on the row. Add-on Preferences have no stage control; there, Anim Assist notes that each workspace picks its stage with the row's tabs.

## Dope Sheet: poses and key timing

The summary counts visible owners, editable curves and selected keys, with All/None selection. **Block & Tween** starts open. The remaining groups are **Timing, Keys & Channels, Pose & Match, Bake & Finish and Quick Shelf**.

1. Select an animated object or pose bones; show the Action channels and select the keys to edit.
2. Use Block & Tween for direct breakdown percentages and drag tools. Expand its options for masks, presets and sampling choices.
3. Use Timing for spacing, offset and ripple work; Keys & Channels for selection, key management and metadata.
4. Use Pose & Match for matching/mirroring, then Bake & Finish for existing bake and diagnostic tools.

Select handle sides in Graph Editor. Dope Sheet retains advanced handle types. Macro authoring/setup live in Scene Properties.

### Breakdown anchors

At an empty frame, surrounding keys anchor the blend: 0 and 10 produce 5 at 50%. An existing playhead key becomes the previous anchor: current 5 and next 10 produce 7.5 at 50%. Repeating can change an existing key again. Check the playhead, keys and masks first.

## Graph Editor: curve shaping

**Shape Curves** starts open with direct shaping, interpolation and handle actions. The complete order is **Select & Channels, Shape Curves, Retime, Clean Up, Pose & Bake and Quick Shelf**. Select & Channels includes handle selection; Clean Up holds key management and diagnostics. Pose & Bake includes matching, mirroring, breakdowns and baking. Its folded **Breakdown Options** configure breakdown sampling, not general curve interpolation.

Select visible editable Action keys, apply the shaping/interpolation action, then inspect the curve and viewport. Selected-key interpolation affects selected editable visible keys only. Key Manager timing commands honor editor visibility and channel locks. Move Keys and Insert Frames run first; tune values in native **Adjust Last Operation**.

Selection helpers support **object Actions**. Empty scope never falls back to the entire active Action. Detached pinned Actions, non-object sources and Graph Drivers mode are unsupported; the sidebar explains exclusions. Check descriptions for Action-wide tools.

## NLA: arrange clips and blend corrections

**Arrange & Time** and **Blend & Corrections** start open together. **Actions & Tracks, Bake & Finish and Quick Shelf** start closed. The summary names the owner, active clip, source Action, selected clip count, scene range and source range. Scene frames locate the clip; source frames describe the Action interval used inside it.

### Arrange clips

1. Select the Action clips to change; make the reference clip active and selected.
2. Click -1f/+1f to nudge, or **Move Selected Clips** for a native move. **Align Starts/Ends** uses the active selected clip as reference.
3. **Sequence Clips** places selected clips consecutively from that reference clip's start. Change the step or sequence gap in Adjust Last Operation.
4. Expand **Timing Options** for active-clip scale, repeat, reverse and scene start/end.

Timing uses scene frames. Locked/overlapping batches reject without partial changes. Arrangement pauses during source editing. Transition, meta and sound strip editing is unavailable here.

### Edit sources and manage sharing

**Edit Action** enters native NLA Tweak Mode. **Open Dope Sheet/Open Graph Editor** reuses a suitable unpinned editor or switches the current area. Use the editor selector to return to NLA, then **Finish Editing** to return to arrangement. Native Tweak Mode maps source time for moved, scaled, repeated and reversed clips.

Shared Action edits can affect other clips. The summary warns about sharing; **Make Selected Clips Unique** separates their sources. **Duplicate Independent** copies the Action; **Duplicate Linked** shares it. **Move Selected Tracks Up/Down** reorders tracks, not clips between tracks. Mute and Solo affect evaluation; the summary reports excluded sources.

**Push Down Active Action/Stash Active Action** operate on the active owner's assigned Action. Push Down requires NLA evaluation enabled. With no selected clip, the summary offers **Add Existing Action Clip** for an editable active object.

### Add a transform correction

1. Select one supported source Action clip. Click **New Transform Correction**.
2. Select its new correction clip, then **Edit Correction**. Edit its transform keys through native Tweak Mode; use Finish Editing when done.
3. Keep unmodified channels neutral: location zero, rotation zero/identity, scale one. Native **Combine** blending applies this transform adjustment over the source motion.
4. At the playhead, click **0%, 50% or 100%** to key the active clip's influence. Adjust Last Operation accepts another value. Zero influence removes the correction's contribution.

Creation makes an independent correction Action and track above the source. It supports object and pose-bone transforms. Constrained/driven rigs, unresolved bones and non-transform source channels are blocked with an explanation. This is separate from the general Animation Layers tools in Scene Properties.

Blend and Animated Influence are native strip settings. With Animated Influence off, the sidebar identifies the automatic blend envelope. **Blend Options** exposes Automatic Blend, blend-in/out and extrapolation. Influence buttons create native influence keys, not pose keys in the source Action.

### Bake while retaining the source stack

1. Select a clip for the owner to bake. Open **Bake & Finish**; check the displayed owner and scene range.
2. Click **Bake to New Action**. Adjust Last Operation changes the scene-derived range and step.
3. Evaluated object/pose transforms go into a retained new Action. It remains **unassigned**; original Actions, clips, parents and constraints remain.
4. Check the output name/range. Separately choose **Use Latest Bake (NLA Off)** to assign it to its owner and disable NLA evaluation, preventing the source stack contributing again.

Before activation, mute/remove active constraints to avoid applying them again. Save the source scene for comparison. Output ownership survives renaming; another object taking the old name cannot receive it. **Remove Empty Tracks** separately cleans up.

NLA Quick Shelf shortcuts: make sources unique, edit the active source and bake the owner. It does not run general key-editing macros against strips.

## Scene Properties and broader tools

Scene Properties > Anim Assist: **Quick Shelf, This Pose, Whole Animation, Rig, Face, Setup (once per rig), Settings, Help & Diagnostics**. This Pose holds offsets/matching/mirroring; Whole Animation holds Action offsets/trails/layers; Rig holds proxies/baking; Face holds lipsync. Configure pair/switch mappings before use.

Search finds existing tools. Recents lists completed tools newest first; Repeat Last uses that entry. Canceled/unfinished commands are excluded. Older files sort Recents by timestamp. Toggle Shelf Mode cycles shelf modes. Configure macros in Scene Properties > Anim Assist > Settings.

For lipsync, configure the target, audio and viseme wiring before Bake Lipsync. Amplitude analysis needs no external phoneme tool; optional Rhubarb needs its executable configured. Live Preview/Baked identify the state. Bake/Rebake writes automatic keys. Mark Manual preserves selected manual work during rebake; Clear Auto Keys removes automatic output while retaining manual keys. Resolve missing-layer/WAV guidance before baking.

## Troubleshooting and verification limits

If a key operation does nothing, check active editor, selected editable keys, visible channels, locks, owner and Action. Native Insert Keyframe remains your normal mesh/object keying workflow. Toolbar visibility alone does not prove keys were inserted: inspect Action data and editor filters too. Report the add-on version, Bforartists build, exact command and a small reproducible scene.

For unavailable NLA actions, check track locks, mute/Solo exclusion, missing Action, disabled NLA evaluation or active Tweak Mode. Finish Editing before arranging clips. Read the unsupported-rig/channel explanation for correction creation. Inspect motion after timing/bake changes; use native Undo if needed, then save/reopen before relying on the result.

The [12.9.0 qualification](releases/12.9.0/qualification.md) covers the stage tabs added in this release. The [12.8.0 qualification](releases/12.8.0/qualification.md) records 16 native behavioral/interaction groups, Undo/Redo, workspace reload, 98 panel registration checks and five Timeline layout regression checks. Native mesh key insertion was visible in Graph/Dope Sheet. All three sidebars were captured at 220, 280 and 360 px. These synthetic fixtures do not certify every existing tool, production rig or host build. Earlier slider/lipsync evidence is historical, not a fresh full-suite pass for 12.8.0.

## Actual interface screenshots

Actual qualification captures: Timeline stage tabs and settings from 12.9.0, editor sidebars from 12.8.0. Open full size; selection determines enabled controls.

- [Timeline stage tabs: Block stage (12.9.0)](releases/12.9.0/evidence/images/stage-block.png)
- [Toolbar Settings with Row Stage (12.9.0)](releases/12.9.0/evidence/images/settings-dialog.png)
- [NLA sidebar: arrangement and corrections, 280 px](releases/12.8.0/evidence/images/nla_editor-280.png)
- [Graph sidebar: curve shaping, 280 px](releases/12.8.0/evidence/images/graph_editor-280.png)
- [Dope Sheet sidebar: poses and timing, 280 px](releases/12.8.0/evidence/images/dopesheet_editor-280.png)

See [release notes](releases/12.9.0/RELEASE-NOTES.md) and the [documentation index](README.md). The 12.5.0 separate-strip screenshots and checkbox-only quick-tool instructions are historical; use this guide for current settings.
