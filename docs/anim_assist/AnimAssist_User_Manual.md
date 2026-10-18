# Anim Assist 12.10.0 user guide

Reviewed against 12.10.0 on October 18, 2026. Use Dope Sheet for poses/timing, Graph Editor for curves, and NLA Editor for clips/corrections. Help controls explain individual tools.

## Install and find the tools

Download the [12.10.0 add-on ZIP](https://raw.githubusercontent.com/Axleonex/B4Artists_Toolkit/main/releases/b4_anim_assist_v12.10.0.zip). In Bforartists, open Edit > Preferences > Add-ons > Install from Disk. Select the ZIP and enable Anim Assist. Its package is `B4_anim_assist`. Restart after updating.

Validated host: stock Bforartists 5.2.0, Blender 5.3.0 Alpha base, build `0a1ca45552db`, OpenGL. Standard Blender is unsupported; other builds were not validated.

- **Timeline:** Anim Assist's tool row sits at the bottom of the canvas; see **Timeline: the bottom tool row** below. Playback and keyframing controls remain in the existing native header.
- **Dope Sheet, Graph Editor and NLA Editor:** point into the editor, press N, then choose the Anim Assist tab. The header's Anim Assist menu provides additional access.
- **Scene Properties > Anim Assist:** character setup, broader animation tools, macros, settings and help. There is no Anim Assist tab in the 3D Viewport sidebar.

Scene Properties > Anim Assist > Setup (once per rig) > First Run Setup creates the general Quick Shelf. Setup also offers a workspace. The optional Shift Alt D pie starts off; enable/rebind it in Settings.

## Timeline: the bottom tool row

The tool row sits along the bottom of the Timeline, just above its horizontal scrollbar. It adds no header, region or workspace split, and the Timeline's own playback and keying controls stay in the native header. To show or hide the row, use **Timeline > View > Show Anim Assist Tool Row**. Give the Timeline enough height for its keys and the row.

From left to right the row holds:

| Control | What it does |
|---|---|
| **Stage button** (for example **All**, with a small arrow) | Shows the current stage; click it to choose another. |
| **Family buttons** (Tween, Timing, Curves, Keys, Pose, Bake, Motion) | Coloured names that open the full tool list of that family. The row's tools follow each family name. |
| **Tools** | Buttons, icons and sliders. Click to run; hover for an explanation. |
| **+N** | Appears only when N of the row's tools do not fit; click it to use them. |
| **Find** (magnifier) | Search or browse all 96 tools; run one, or pin it to the row. |
| **Settings** | Toolbar Settings: choose what each row shows. |

Every list on the row (the stage list, family lists and **+N**) opens with one click and stays open while you move the pointer, even over another editor. Click an item to use it. Click the same button again, click anywhere else or press Esc to close the list; clicking another family button switches to that family.

### Choose a stage

A stage is a set of tools for one phase of the work:

- **All:** the condensed overview, with tools from every family.
- **Block:** Tween and Keys tools for blocking poses.
- **Spline:** Curves and Motion tools for splining and checking arcs.
- **Polish:** Timing and Pose tools for spacing and symmetry.
- **Deliver:** Bake tools for finishing and export.

To change the stage:

1. Click the stage button at the left of the row. The list of five stages opens above it (on a short Timeline, as one row of buttons).
2. Click a stage. The row switches and the list closes.

You can also hold Ctrl and scroll over the stage button to step through the stages, or use **Timeline > View > Anim Assist Stage**. Each workspace keeps its own stage, saved with the file.

### Use the tools

- **Buttons and icons** run a tool on click. A greyed tool cannot run yet; hover it to see why (for example, no keys are selected).
- **Icons:** key types show as diamonds in your theme's Dope Sheet key colours (Keyframe, Breakdown smaller, Extreme larger, Moving Hold); handle types use your theme's Graph Editor handle colours. Hover any icon for its name.
- **Inline sliders** stay on the row. Press on the track and drag; release to apply. Esc or right-click while dragging restores the keys as they were. Hold Shift for finer movement and Ctrl to snap to the tool's step. While dragging, type a number and press Enter to use an exact amount. A click without a drag changes nothing.
- **Ticks** on a slider track are presets: click a tick to apply exactly that amount. A drag snaps onto ticks when it passes close to them.
- **The number** at the right of an inline slider opens a field for an exact value; **R** applies the tool's default amount.
- **Popout sliders** show only their name on the row. Press and drag to open a temporary slider and release to apply. Or click once: the popout stays open, you drag on its track, and a double-click or a click anywhere else applies it; Esc cancels.
- **Right-click** a tool to open its Tool Settings.

Ten tools are numeric sliders: Breakdown, Smooth, Neighbors, To Reference, Ease, Amplify, Timing Scale, Timing Offset, Ripple and Reduce.

- **Breakdown** blends the selected keys between the previous and next pose. Values below 0% or above 100% push past them.
- **Timing Scale** changes key spacing: below 100% the keys move closer (faster), above 100% they spread apart (slower). **Timing Offset** shifts the active object's Action in time.
- **Ripple** moves every key after the playhead by the dragged number of frames; moving earlier stops one frame after the playhead.
- **Reduce** removes keys whose removal changes a curve by less than the dragged tolerance. You watch keys disappear as you drag; Esc brings them back.
- **To Reference** blends toward the reference frame (set it with **Set Reference**); **Amplify** scales the motion around that reference.

Action-wide tools such as Timing Offset affect more than the selected keys. Check the hover text and the scene options before you change a whole Action.

### Default rows

Each row starts from a fixed set, left to right in workflow order:

- **All:** Breakdown slider with ticks at 25, 50 and 75%; Smooth slider; -1f/+1f nudges (icons); Timing Scale (popout); Mirror Selected, Bake Object, Trails (an eye that shows or hides world motion trails), Copy and Paste (icons).
- **Block:** Breakdown slider from -25% to 125% with ticks at -25, 25, 50, 75 and 125 (-25 and 125 push past the previous or next pose, 25 and 75 pull toward it); Inbetween and Distribute (icons); Select Range, All Keys and Ends; Grow left and right (icons); Mark Keyframe, Breakdown, Extreme and Moving Hold (key diamonds); Copy and Paste (icons).
- **Spline:** To Spline (curve icon); Neighbors, Ease and Smooth sliders; Set Reference (target icon), then To Reference and Amplify sliders; Auto Clamped, Vector and Free handles (icons); Trails.
- **Polish:** -1f/+1f; Timing Scale slider with ticks at 80, 90, 110 and 120%; Timing Offset slider; Ripple slider with ticks at -1 and 1; Snap (round key times); Select Opposite, Mirror Selected, Mirror Active and Swap (icons).
- **Deliver:** Bake Object (icon), Bake Preview Range, Smart Bake; Reduce slider with ticks at 0.001, 0.01 and 0.05; Bake Keys to Integer Frames (restorable with Reset Timing); One-Click Proxy & Bake; Location, Rotation, World and Parent proxies (icons); Bake Session and Remove Proxies; Remove All Proxy Sessions.

Tools that are not on a row, for example To Stepped or the 25/50/75% Breakdown buttons, are always in **Find**.

### Find and More

**Find** (the magnifier) reaches every tool:

1. Click the magnifier.
2. Type part of a name, a family or an idea (for example "spacing" or "arc"), or leave the field empty and click a family tab to browse its tools.
3. Click a tool to run it. Click its pin to add it to the row you are viewing, or to take it off; a lit pin means the tool is on that row.

A pin goes to the row shown, whatever the tool's family. Find and Toolbar Settings share the same layout, so a pin shows in Toolbar Settings and a Toolbar Settings change shows on the pins.

**More** appears as **+N** just before Find only when N of the row's tools do not fit the Timeline's width. Click it to see and run those tools. When everything fits, there is no More button. To make more room, give the Timeline more width, shorten inline sliders, or change occasional sliders to popout or button.

### Change what a row shows

1. Click **Settings** at the right of the row. Toolbar Settings opens on the row the Timeline shows.
2. In **Row**, choose All, Block, Spline, Polish or Deliver. The Timeline switches to that row while you edit.
3. Open a family by clicking its header (Tween, Timing, Curves, Keys, Pose, Bake, Motion). Each header shows how many of its tools are on the row; a stage opens on its own families. To find a tool by name, type in the search field above the families.
4. For each tool choose:
   - **Display:** Hidden (off the row), Button, Popout slider or Inline slider. Ordinary tools offer Hidden or Button; sliders offer all four.
   - **Label or Icon**, for tools that have an icon. For an inline slider, the second field sets its **Width** instead.
   - The **up and down arrows** move the tool within its family.
   - The **gear** opens the tool's Tool Settings.
5. Close the panel by clicking outside it or pressing Esc. Your changes stay.

Every change shows on the row at once; there is no OK button. **Revert Changes** undoes everything since you opened the panel. Any row can hold any tool: a tool from another family brings that family's button onto the row.

Tools that can show as an icon: key types, handle types, grow selection, -1f/+1f, Inbetween and Distribute, To Spline and To Stepped, Set Reference, Copy, Paste, Mirror Selected, Mirror Active, Select Opposite, Swap, Bake Object, the four proxy types and Trails. Any other tool shows its name.

**Tool Settings** (the gear, or right-click a tool on the row) sets a tool's display, slider range, default, width, precision, drag sensitivity, snapping, presets and **Presets as Ticks**. **Custom Range / Overshoot** allows amounts outside the standard range where the tool supports it. In a stage, the display, label, presets and ticks belong to that stage; the other amounts are shared by All and every stage. Masks, targets and breakdown anchors stay in the scene settings; **Scene Tool Options** opens them.

### Save, load and reset layouts

A layout is the whole set of rows: All and the four stages together.

- **Save As** names the current layout. **Load** restores a saved one; **Update Saved** overwrites it with the current rows. **Rename** and **Delete** manage saved layouts. **Recommended** is built in and cannot be changed.
- **Reset Block to Defaults** (named for the row you edit) restores that stage's default set. **Restore Recommended Layout** restores All and every stage, and keeps your saved layouts.
- Layouts live in the add-on preferences and apply to every Timeline. If Preferences are not saved automatically, click **Save Preferences** in Toolbar Settings to keep your changes after a restart.

Stages start from their fixed default set, not from your All row: a tool you add to All appears in a stage only after you add it there. Add-on Preferences have no stage control; each workspace picks its stage with the row's stage button.

### Hover explanations and shortcuts

Rest the pointer on a control for about half a second to see its explanation. **Hover Explainers** (Edit > Preferences > Add-ons > Anim Assist > General) sets how much it says:

- **Full:** what the tool does, what it works on, what it needs and how to use it.
- **Short:** the name and one line, plus why the tool is greyed if it is.
- **Off:** no Anim Assist hover text on the row. On Bforartists' own buttons in Anim Assist panels and menus, only the tool's name remains, because Bforartists always prints a description line. Setting fields keep their own one-line tooltip. To turn off every tooltip, use **Edit > Preferences > Interface > Tooltips**.

Hover text also lists keys, but only keys that exist:

- **Shortcut:** a key bound to that exact Anim Assist tool. No row tool has one by default; bind one in **Edit > Preferences > Keymap** and it appears.
- **Bforartists key:** Bforartists' own command for the same job, when Bforartists binds a key to it. By default: Ctrl C (Copy), Ctrl V (Paste), A (All Keys), Ctrl Numpad + (Grow both sides), R (Scale Keys in Time, for the timing scale tools) and W (Move Keys in Time, for timing offset and the nudges) in the Dope Sheet. These are Bforartists' commands and can differ in detail: its Paste, for example, pastes at the playhead rather than at the copied times.

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
- [Toolbar Settings editing Block, families grouped (12.10.0)](releases/12.10.0/evidence/images/settings-row-block.png)
- [Stage dropdown open (12.10.0)](releases/12.10.0/evidence/images/stage-dropdown-hover.png)
- [Find browsing tools by family (12.10.0)](releases/12.10.0/evidence/images/find-browse.png)
- [+N listing tools that did not fit (12.10.0)](releases/12.10.0/evidence/images/more-list.png)
- [Hover explanation, Full (12.10.0)](releases/12.10.0/evidence/images/explainer-row-full.png)
- [NLA sidebar: arrangement and corrections, 280 px](releases/12.8.0/evidence/images/nla_editor-280.png)
- [Graph sidebar: curve shaping, 280 px](releases/12.8.0/evidence/images/graph_editor-280.png)
- [Dope Sheet sidebar: poses and timing, 280 px](releases/12.8.0/evidence/images/dopesheet_editor-280.png)

See [release notes](releases/12.10.0/RELEASE-NOTES.md) and the [documentation index](README.md). The 12.5.0 separate-strip screenshots and checkbox-only quick-tool instructions are historical; use this guide for current settings.
