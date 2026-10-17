# Ghost Tool 4.3.1 toolbar reference

The main Ghost toolbar occupies the native 3D Viewport Tool Settings row. With headers at the top, it is the row beneath the main header. Choose Top Toolbar in Ghost preferences. Right Sidebar (N) and Left Tool Shelf (T) remain alternative locations.

## Top row: direct actions

Read left to right: **Ghost Tool on/off; Ghosts; Before/Ahead ghost counts; Wire; Solid; Paths; Before/Ahead path counts; Add Selected Path; Follow Selection; Drag; Pin; Markers Display; Arc Style; Spacing Ticks; Settings.**

The first ghost icon controls the whole tool. Ghosts separately shows/hides mesh ghosts. Before and Ahead are independent counts relative to the playhead; each top-toolbar number has minus and plus actions. Paths has a separate pair of sample counts. Wire and Solid explicitly select mesh style and do not replace mesh visibility.

Add Selected Path retains a target in the path list. Follow Selection displays the current selection without removing explicitly added targets. Pin instead fixes an editable marker while reshaping. Click Pin and pick a marker; invoke it again for another marker. Hold Pin for Unpin All Markers.

Drag Markers stays active after a confirmed move. Pick another marker in the 3D Viewport, select Drag again to stop, or press Escape. Escape during a move restores that move's starting data, not earlier confirmed edits. Path-handle drag mode also supports repeated picks.

Markers Display is the diamond immediately right of Pin. It shows/hides editable path points and has its own tool-name hover label. Arc Style is a single-click dropdown containing Solid, Speed Colored and Fade directly. It is separate from mesh Wire/Solid and Paths Line Style.

## Hold menus

Click for the main action; press and hold a supported action for parameters. Arc Style and Settings open on an ordinary click.

**Ghost Tool:** mesh/marker updates while scrubbing and Freeze Updates. **Ghosts:** frame-step or keyframe sampling, interval, Opacity, In Front and Fade. **Paths:** sampling, interval, Line Style, Frame Numbers and Bezier Handles.

**Drag:** When Released, Curve Shape or Smooth Neighbours, Nearby Frame Reach and Falloff. **Pin:** pin instructions and Unpin All Markers. **Markers Display:** shared Paths sampling, Keyframe Dots and Marker Frame Numbers. **Follow Selection:** Highlight Active Path. **Spacing Ticks:** Acceleration Indicators.

Settings retains marker generation, range, targets, onion skins, Edit Motion, Compare, Physics, Look and other advanced options. The redundant top-row Generate/Clear icons are removed. Clear All Ghosts remains in advanced controls for deliberate removal of markers and onion skins.

## Bottom Timeline strip

The compact strip sits inline beside native Timeline controls. Its order remains overall on/off, mesh display, earlier/later mesh counts, Wire/Solid, Drag Markers, marker diamond, Paths display and earlier/later path counts. This update does not redesign it or add a second row.

Hold the bottom Ghosts or Paths button for Frame by Frame / By Keyframe, intervals and display settings. More Ghost Settings opens the full options. The bottom marker diamond is a direct toggle; its separate hold menu is on the top toolbar. Snapshot controls live in advanced Compare rather than the bottom strip.

## Visibility, space and recovery

Narrow and split viewports retain the full native row and tool order. Middle-mouse drag horizontally to reach offscreen controls. View > Show Ghost Toolbar or Show Ghost Toolbar in preferences recovers hidden Ghost controls and explicitly reveals the native row when needed. Leaving Top Toolbar preserves native region visibility.

The left shelf width preference is retained. The 4.2.11 width/scale assessment was incomplete; this update makes no new width-fix claim. The duplicate Ghost button in the main viewport header remains removed.

## Version status

This reference describes **4.3.1**, distributed as [b4_ghost_tool_v4.3.1.zip](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.3.1/b4_ghost_tool_v4.3.1.zip). Historical releases retain their original numbers and archives. See the [user guide](../GhostTool_User_Manual.md) and [4.3.1 release notes](../releases/4.3.1/RELEASE-NOTES.md) for workflows and publication status.
