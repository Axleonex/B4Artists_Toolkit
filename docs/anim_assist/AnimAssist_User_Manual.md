# Anim Assist 12.10.0 user guide

Reviewed against 12.10.0 on October 17, 2026. Use Dope Sheet for poses/timing, Graph Editor for curves, and NLA Editor for clips/corrections. Help controls explain individual tools.

## Install and find the tools

Download the [12.10.0 add-on ZIP](https://raw.githubusercontent.com/Axleonex/B4Artists_Toolkit/main/releases/b4_anim_assist_v12.10.0.zip). In Bforartists, open Edit > Preferences > Add-ons > Install from Disk. Select the ZIP and enable Anim Assist. Its package is `B4_anim_assist`. Restart after updating.

Validated host: stock Bforartists 5.2.0, Blender 5.3.0 Alpha base, build `0a1ca45552db`, OpenGL. Standard Blender is unsupported; other builds were not validated.

- **Timeline:** Anim Assist's tool row sits at the bottom of the canvas. Playback and keyframing controls remain in the existing native header.
- **Dope Sheet, Graph Editor and NLA Editor:** point into the editor, press N, then choose the Anim Assist tab. The header's Anim Assist menu provides additional access.
- **Scene Properties > Anim Assist:** character setup, broader animation tools, macros, settings and help. There is no Anim Assist tab in the 3D Viewport sidebar.

Scene Properties > Anim Assist > Setup (once per rig) > First Run Setup creates the general Quick Shelf. Setup also offers a workspace. The optional Shift Alt D pie starts off; enable/rebind it in Settings.

## Timeline: buttons and sliders

The row groups tools into **Tween, Timing, Curves, Keys, Pose, Bake and Motion**. Click an action to run it; use family menus or **Find** (the magnifier) for others. Find searches all 96 tools as you type; with nothing typed it shows family tabs to browse every tool. Click a tool to run it, or its pin to add it to the row or take it off. Find and Toolbar Settings share the same layout, so a pin shows in Toolbar Settings and a Settings change shows on the pins. Tooltips explain prerequisites and scope. Action-wide offset affects more than selected-key nudging.

**Recommended** starts with two inline sliders: **Breakdown**, whose track has ticks at 25%, 50% and 75% (click a tick to apply it), and **Smooth**. **Timing Scale** uses a temporary popout slider. Quick icons: -1f/+1f nudges, Copy/Paste Keys, Mirror Selected, Bake Object Transforms and Trails (the eye shows or hides world motion trails). Hover an icon for its name. In Tool Settings, **Presets as Ticks** switches any slider between ticks on its track and preset buttons, in All or in a stage.

Press and drag. Release applies; Esc/right-click restores the captured animation. Shift gives finer movement; Ctrl uses the snap step. Type a value and press Enter for numeric input. Clicking without dragging applies nothing. Watch the status bar. A popout slider (such as Timing Scale in All) can also be clicked: it then stays open, you drag on its track to adjust, and a double-click or a click anywhere else applies; Esc cancels.

A stage can show a slider's presets as ticks on its track instead of buttons: click a tick to apply that preset exactly (the drag snaps onto ticks). If the row is too tight and the slider becomes a popout, its presets show as buttons again. Ten tools support numeric display: Breakdown, Smooth, Neighbors, To Reference, Ease, Amplify, Timing Scale, Timing Offset, Ripple and Reduce. Ripple shifts every key after the playhead by the dragged number of frames (earlier stops one frame after the playhead). Reduce removes keys whose deletion changes a curve by less than the dragged tolerance; drag to watch keys disappear, Esc brings them back. To Reference blends toward the configured reference frame; Amplify changes amplitude around that reference. Timing Scale changes key spacing: below 100% keys sit closer (faster), above 100% they spread apart (slower); Timing Offset shifts the active object's Action timing. Check tooltips and scene options before editing a whole Action.

### Customize and save layouts

Open row **Settings**, choose a family/tool, then **Hidden, Button, Popout slider or Inline slider**. Ordinary actions offer Hidden/Button only. Hidden tools remain in Find. Move Up/Down orders tools within their family; Slider Width controls inline width.

Use **Tool Settings**, or right-click an idle numeric tool, to set display, range, default, width, precision, drag sensitivity, snapping and presets. **Custom Range / Overshoot** permits supported amounts outside the standard range. Masks, targets and breakdown anchors remain scene settings; **Scene Tool Options** opens those separately.

**Save As** names an arrangement. **Load** restores one; **Update Saved** replaces its saved settings. Rename/Delete manage saved layouts. Recommended is protected. **Restore Recommended Layout** resets the working arrangement while retaining saved layouts. Confirm the main Settings dialog to apply staged changes. Save Preferences after applying if automatic preference saving is off.

On a narrow Timeline, a **+N** button appears before Find (for example +3): it lists the row's tools that did not fit. When everything fits, there is no More button. Shorten the row by reducing inline widths or changing occasional sliders to popout/button mode. If hidden, use **Timeline > View > Show Anim Assist Tool Row**. Give the Timeline enough height for its keys and tool row.

The **bottom-only canvas overlay** retains 12.7.1 placement, away from the top keyframe diamonds. It adds no native header/editor region or workspace split. There is no top/bottom placement setting.

### Stage tabs

Tabs at the left of the row choose a stage: **All**, **Block** (Tween, Keys), **Spline** (Curves, Motion), **Polish** (Timing, Pose) and **Deliver** (Bake). **All** is the condensed overview of every family. Each other stage has its own toolset for its families.

Click a tab, hold Ctrl and scroll over the tabs, or use **Timeline > View > Anim Assist Stage**. Each workspace keeps its own stage, saved with the file. When All does not fit beside the tabs, they collapse into one stage button. Click it once to open the stage list (it stays open while you hover), then click a stage. Clicking the button again, clicking anywhere else or pressing Esc closes the list. In a short Timeline the five stages appear as a row above the button. Ctrl+Wheel over the button also cycles stages. Tools that do not fit remain in More and Search. The row sits just above the Timeline's horizontal scrollbar and keeps its end buttons clear of the Timeline's corners. The family buttons (Tween, Keys and so on) and More work the same way: one click opens the list, it stays open while you move the pointer, clicking a tool runs it, and clicking the same button, anywhere else or pressing Esc closes it. Clicking another family button switches to that family; in More, a family opens in place with a Back row.

### Stage toolsets

Each stage starts from a fixed default set, the Recommended tools for its families plus tools for that phase, left to right in workflow order:

- **Block:** Breakdown slider whose track runs from -25% to 125% with ticks at -25, 25, 50, 75 and 125 (click a tick to apply it: -25 and 125 push past the previous or next pose, 25 and 75 pull toward it); Inbetween and Distribute (key-plus-key icons); Select Range/All/Ends; Grow left/right (key and arrow icons); mark Keyframe/Breakdown/Extreme/Moving Hold (key-type diamonds in your theme's Dope Sheet key colours); Copy/Paste (icons). Hover any icon for its name. The 25/50/75% and Push/Pull buttons stay in More and Search.
- **Spline:** To Spline (curve icon; To Stepped is in Find); Neighbors, Ease and Smooth sliders; Set Reference (target icon), then To Reference and Amplify sliders; Auto Clamped/Vector/Free handles (icons in your theme's Graph Editor handle colours); Trails (an eye: click to show world motion trails, again to hide them; a slash means they are off).
- **Polish:** -1f/+1f (arrow icons); Timing Scale slider with ticks at 80, 90, 110 and 120; Timing Offset slider; Ripple slider with ticks at -1 and 1 (1 matches the old Ripple button); Snap; Select Opposite, Mirror Selected, Mirror Active and Swap as icons (Mirror Active's right-hand triangle is hollow).
- **Deliver:** Bake Object (key-bars icon), Bake Preview Range, Smart Bake; Reduce slider with ticks at 0.001, 0.01 and 0.05 (0.01 matches the old Reduce Keys button); Bake Keys to Integer Frames (whole frames, restorable with Reset Timing); One-Click Proxy & Bake; Location, Rotation, World and Parent proxies (icons: move cross, turn arrow, globe, parent link), then Bake Session and Remove Proxies; Remove All Proxy Sessions.

To change a row, open **Toolbar Settings** (the row's **Settings** button). The **Row** dropdown (All, Block, Spline, Polish, Deliver) chooses the row you edit, and the Timeline switches to it. Every row lists all 96 tools, grouped under family headers (Tween, Timing, Curves, Keys, Pose, Bake, Motion). Click a header to open or close it; it shows how many of its tools are on the row, and a stage opens on its own families. Type in **Find** to filter by name. To add a tool to the row, set it to Button, Popout or Inline; to take one off, set it to Hidden. The arrows move a tool up or down within its family, and the gear opens Tool Settings. Any row can hold any tool: a tool from another family brings that family's menu onto the row. Every change shows on the row at once; there is no OK button. Click outside the panel or press Esc to close it and keep your changes, or press **Revert Changes** to undo everything since you opened it. When Preferences are not saved automatically, press **Save Preferences** to keep the changes after a restart. Tools that have an icon (key types, -1f/+1f, Copy and Paste) can also show as Label or Icon; every other tool shows its name. **Reset Block to Defaults** (named for the row you edit) restores that stage; **Restore Recommended Layout** restores All and every stage. Saved layouts store All and all four stages together.

**Hover Explainers** (Preferences > Add-ons > Anim Assist > General) sets how much Anim Assist explains when the pointer rests on a control: **Full** (what it does, what it works on, what it needs, how to use it), **Short** (the name and one line, plus why a tool is greyed) or **Off** (no Anim Assist hover text on the Timeline row; Bforartists' own buttons show only the tool's name, because Bforartists always prints a description line). If a key is bound to a tool, its hover text ends with a Shortcut line; no Timeline tool has a key by default, so this appears only for keys you bind in Preferences > Keymap. Where Bforartists has its own command for the same job with a key bound, a **Bforartists key** line names it, for example Ctrl C for Copy, A for All Keys, R (Scale Keys in Time) for the timing scale tools and W (Move Keys in Time) for the nudges. Those are Bforartists' commands and can differ in detail: its Paste, for instance, pastes at the playhead rather than at the copied times.

Amounts (range, default, presets, slider width, snapping) are shared: changing them in any stage changes them everywhere. Right-click Tool Settings changes the display and label in the stage the row shows. A Search pin also goes to that row, whatever the tool's family. More lists the shown stage's tools.

Stages start from this fixed set, not from your All tools: a tool you added to All appears in a stage only after you add it there. Add-on Preferences have no stage control; there, Anim Assist notes that each workspace picks its stage with the row's tabs.

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

The [12.10.0 qualification](releases/12.10.0/qualification.md) covers stage toolsets; the [12.9.1 qualification](releases/12.9.1/qualification.md) covers the stage tab fixes. The [12.8.0 qualification](releases/12.8.0/qualification.md) records 16 native behavioral/interaction groups, Undo/Redo, workspace reload, 98 panel registration checks and five Timeline layout regression checks. Native mesh key insertion was visible in Graph/Dope Sheet. All three sidebars were captured at 220, 280 and 360 px. These synthetic fixtures do not certify every existing tool, production rig or host build. Earlier slider/lipsync evidence is historical, not a fresh full-suite pass for 12.8.0.

## Actual interface screenshots

Actual qualification captures: Timeline stage toolsets and settings from 12.10.0, editor sidebars from 12.8.0. Open full size; selection determines enabled controls.

- [Timeline stage toolset: Block (12.10.0)](releases/12.10.0/evidence/images/stage-block.png)
- [Timeline stage toolset: Spline (12.10.0)](releases/12.10.0/evidence/images/stage-spline.png)
- [Toolbar Settings editing Block (12.10.0)](releases/12.10.0/evidence/images/settings-dialog.png)
- [NLA sidebar: arrangement and corrections, 280 px](releases/12.8.0/evidence/images/nla_editor-280.png)
- [Graph sidebar: curve shaping, 280 px](releases/12.8.0/evidence/images/graph_editor-280.png)
- [Dope Sheet sidebar: poses and timing, 280 px](releases/12.8.0/evidence/images/dopesheet_editor-280.png)

See [release notes](releases/12.10.0/RELEASE-NOTES.md) and the [documentation index](README.md). The 12.5.0 separate-strip screenshots and checkbox-only quick-tool instructions are historical; use this guide for current settings.
