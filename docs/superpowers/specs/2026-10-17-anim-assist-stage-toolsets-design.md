# Anim Assist stage toolsets

Date: 2026-10-17. Status: design agreed in conversation; implementation not started.
Target release: Anim Assist **12.10.0** (owner decision).
Baseline: work branch `work/anim-assist-stage-tabs` at `2205b59` (Anim Assist 12.9.0
candidate, not yet pushed; GitHub `main` is at `6dd7da9`). Previews:
`G:\LapArt\output\anim-assist-stage-extras-preview\stage-*.png` (script mockups,
not Bforartists renders).

## Intent

12.9.0 stage tabs only filter the bottom Timeline row: Block, Spline, Polish and
Deliver show a subset of the families in **All**. The owner wants each stage to be
a deeper toolkit for its phase of work instead: when a stage is selected, it keeps
what **All** shows for that stage's families and adds more tools specific to that
phase. **All** stays the condensed overview, exactly as it is today.

## Owner decisions

1. The per-stage tool sets below are **defaults only**. Toolbar Settings must let
   the user customise each of the four stages separately.
2. Every tool can be hidden or unhidden per stage in Toolbar Settings.
3. Each tool uses the presentation appropriate to it: inline slider, popout slider
   or button. Workflow order must stay sensible left to right.
4. **Option A:** each saved layout stores all five setups (All plus the four
   stages), so Save As, Load, Update Saved, Rename, Delete and the unsaved marker
   cover the per-stage setups together.
5. **Fixed table:** every layout's stages start from the default table below,
   not from what that layout shows in All. Tools a user added to All stay in All;
   they appear in a stage only after the user adds them there. Reset Stage to
   Defaults restores the table. The 12.10.0 release notes must say this, because
   a 12.9.0 user's extra All tools will no longer appear in its stages.
6. **Release:** ship as 12.10.0.

## User experience

- **All** is unchanged: the active layout's existing `order` and `tools`, all seven
  families, current overflow behaviour.
- A stage shows only its families (unchanged mapping: Block = Tween, Keys;
  Spline = Curves; Polish = Timing, Pose; Deliver = Bake, Motion), in permanent
  family order (Tween, Timing, Curves, Keys, Pose, Bake, Motion) so tools do not
  jump between stages. Within each family, tools follow the stage's own order.
- Stage tabs, cycle button, Ctrl+Wheel, View menu and per-workspace stage storage
  behave as in 12.9.1. Tabs show when All fits beside them in full (the 12.9.1
  result); a wider stage toolset compacts or overflows into More rather than
  taking the tabs away from All (review finding).
- Search and the family menus still list every tool. **More** lists the tools the
  current stage shows (or would show without overflow) followed by All Tools.

### Default stage sets

Left to right within each family. "From All" tools come from the Recommended
layout; the rest are added by the stage. Modes: B = button, I = inline slider,
P = popout slider.

| Stage | Family | Default tools in order |
|---|---|---|
| Block | Tween | 25% B, 50% B, 75% B, Breakdown I, Inbetween B, Distribute Inbetweens B, Push Previous B, Pull Previous B, Pull Next B, Push Next B |
| Block | Keys | Select Frame Range B, Select All Visible B, Select First/Last B, Grow Left B, Grow Right B, Mark Keyframe B, Mark Breakdown B, Mark Extreme B, Mark Moving Hold B, Copy B, Paste B |
| Spline | Curves | Set Reference Frame B, Reference P, Neighbors I, Ease I, Smooth I, Push/Pull (Amplify) P, Auto Clamped Handles B, Vector Handles B, Free Handles B |
| Polish | Timing | -1f B, +1f B, Timing Scale P, 80% B, 90% B, 110% B, 120% B, Timing Offset I, Ripple Forward B, Round Key Times (Snap) B |
| Polish | Pose | Select Opposite B, Mirror Selected B, Mirror Active B, Swap Left/Right B |
| Deliver | Bake | Bake Object B, Smart Bake B, Reduce Keys B, Bake Session and Remove Proxies B |
| Deliver | Motion | Show Trails B, Refresh Trails B, Diagnose Motion Arcs B, Hide Trails B |

All other tools in a stage's families start Hidden in that stage. Action IDs come
from `anim_assist/ui/timeline_catalog.py`; no new operators or animation code.

### Toolbar Settings

- A **Stage** dropdown (All, Block, Spline, Polish, Deliver) selects which setup
  the dialog edits. *My call:* it is the same property as the row's stage (the
  12.9.0 "Row Stage" dropdown), so the row behind the dialog shows the setup being
  edited. It opens on the current workspace's stage.
- In a stage, the Family dropdown offers only that stage's families. Per tool:
  display mode (Hidden / Button / Popout / Inline, with sliders only for scalar
  tools, as today), label/icon and Move Up/Down. The 12.9.0 hidden-family note
  stays for All-only cases; it cannot occur inside a stage.
- **Reset Stage to Defaults** restores the current stage's default set.
  **Restore Recommended Layout** restores all five setups.
- *My call:* numeric tool settings (range, default, sensitivity, precision, snap,
  presets, overshoot, slider width) stay **per tool, shared by All and every
  stage**. Only mode, label/icon and order are per stage. Right-click Tool Settings
  is unchanged.

### Single-tool entry points

*My call:* entry points act on the setup the row is showing.
- Right-click a tool on the row, or Tool Settings from inside Toolbar Settings:
  display mode and label/icon change in the current stage (All when the stage is
  All); numeric settings stay shared.
- Search pin/unpin pins into the current stage. A tool from a family the current
  stage does not show pins into All, and the Search popup says so. The pinned icon
  and the empty-query list reflect the current stage.

## Data model

- *My call:* schema version 2. Each layout keeps `order` and `tools` (the All
  setup) and gains `stages`: `{BLOCK|SPLINE|POLISH|DELIVER: {order: [...],
  tools: {action: {mode, label_mode}}}}`, covering only that stage's families.
- Decoding a version 1 record migrates it in memory: every layout (active, every
  saved layout, Recommended) gets the fixed default stage sets. The stored preference is
  rewritten only on the next normal write (settings apply, layout action), never
  on read.
- *My call:* stage entries are stored sparsely: a stage stores its visible tools'
  `order`, `mode` and `label_mode` only; absent tools are Hidden in that stage.
  Even so a layout grows about a third, so the record limit rises from 1,000,000
  to 1,400,000 bytes to keep the 100-layout cap usable (review finding).
- Validation mirrors version 1: known actions only within the stage's families,
  valid modes per tool, unique order, unknown stage keys and unknown tools
  preserved for forward compatibility, at most 100 saved layouts, 1,000,000-byte
  limit.
- `modified()` compares All and all four stages.
- Downgrade: 12.9.0 rejects a version 2 record as unsupported; the band falls back
  to Recommended and the settings dialog shows its existing "keep the original
  settings file" error. Accepted; record it in the release notes.

## Goals, non-goals, anti-goals

- Goals: deeper per-stage toolkits by default; full per-stage customisation saved
  with named layouts; All unchanged; no animation behaviour change.
- Non-goals: new animation operators; changing which families belong to a stage;
  tools from other families inside a stage; per-stage numeric slider settings.
- Anti-goals: any change to All for existing users; moving or rewriting saved
  layouts on read; tools jumping between family positions across stages; settings
  that silently discard user setups.

## Constraints

- Add-on only, Bforartists 5.2.0; bottom-only pixel band as in 12.9.0.
- Pure presentation model stays free of `bpy` (`timeline_config.py`), testable
  without Bforartists, like `tests/test_timeline_config.py` and
  `tests/test_timeline_overlay_layout.py`.
- Existing 89 dispatch mappings and Ghost Tool/BoneCraft untouched.

## Verification expected

- Unit: v1→v2 migration (active, saved, Recommended), round trip, validation
  errors, per-stage defaults match the table, stage layout bounds at 3 scales ×
  5 widths × 5 stages, All output identical to 12.9.0 for the same record.
- Background Bforartists: settings edit per stage, reset stage, Save As/Load/
  Update Saved carry stages, unsaved marker, save/reopen, register cycles.
- Real-GUI Bforartists from the packaged ZIP: each stage's default row and the
  settings dialog editing a stage.
- Owner walkthrough before release.

## Left to the builder

Exact Toolbar Settings layout and wording within the rules above; internal helper
names; how stage defaults are expressed in code (single table, as in 12.9.0);
overflow ordering beyond "tabs give way first".

## Revision 2026-10-18 (owner-approved, after a B4Artists UI/UX review)

- Stage families: Spline = Curves, Motion; Deliver = Bake. Motion trails check arcs during the Spline pass, and the Motion family also holds Anim Offset; neither is delivery work.
- Spline default: To Spline, Neighbors, Ease, Smooth, Set Reference, To Reference (popout), Amplify (popout), Auto Clamped/Vector/Free handles, Show Trails, Hide Trails. To Spline and To Stepped are new catalogue entries for the existing `animassist.batch_interpolation` operator; To Stepped stays in More.
- Deliver default (12 tools, workflow order): Bake Object, Bake Preview, Smart Bake, Reduce, Whole Frames, Proxy & Bake, Location/Rotation/World/Parent proxies, Bake Proxies, Clean All Proxies. Refresh and Diagnose Trails are low-frequency troubleshooting: More and Search only.
- Labels without abbreviations or clashes: Set Reference, To Reference, Amplify (was Push/Pull, which clashed with Block's Push/Pull buttons), Show Trails, Location Proxy, Rotation Proxy.
- Loading: a stage setup that holds a known tool whose family no longer belongs to that stage drops the tool instead of rejecting the whole record.
- Deviation kept: the stage dropdown and family menus are menus inside a toolbar (Bforartists DD1 advises against it). The owner asked for the dropdown and the row already used family menus.
- Key-type icons (owner-approved 2026-10-18): Block's Mark Key/Breakdown/Extreme/Hold default to Icon, drawn as diamonds in `themes[0].common.anim` key colours (selected variants) with Blender's relative sizes and the Dope Sheet key border. Icon is offered only for tools with a distinct icon (`ICON_ACTIONS`: key types, nudges, Copy, Paste); an Icon choice on any other tool is shown, saved and loaded as Label.
- Version B (owner-approved 2026-10-18): stage tool entries may carry their own `presets` (validated against the tool's hard limits via `preset_bounds`; a preset click passes `preset=True` to `animassist.timeline_slider`). Block: Breakdown inline with presets -25/25/50/75/125 replaces B25/B50/B75 and Push/Pull Prev/Next (measured identical keys at default strengths). Polish: Timing Scale inline with presets 80/90/110/120 replaces T80-T120. Icons: grow (key + arrow), Copy/Paste, To Spline/To Stepped, handle types in `themes[0].common.curves` selected colours, nudges; `TRAIL_TOGGLE` (`animassist.timeline_trails_toggle`) replaces Show/Hide Trails on Spline. All keeps tool-level presets (none), so its row is unchanged.
- Reduce and Ripple sliders (owner-approved 2026-10-18): `SLIDERS['REDUCE']` (tolerance 0-0.1, hard 0-1, precision 3) and `SLIDERS['RIPPLE']` (frames -10 to 10, hard -500 to 500); live preview through `timeline_slider_session.capture`. Deliver Reduce inline with presets 0.001/0.01/0.05, Polish Ripple inline with -1/1. Ripple earlier clamps one frame after the playhead. `restore_snapshot` rebuilds a curve's keys when the count changed (the old one-by-one insert crashed on cancel).
- Compact rows (owner pick "B · Compact" for all four stages, 2026-10-18): stage tool entries may set `ticks` (bool); `track_range` stretches the track to include tick presets and `snap_to_tick` snaps a drag within 3% of the span. A ticked inline slider draws no preset buttons and uses at least a 140 px track (98 px compact); demoted to a popout it shows preset buttons again. New icons via `_shape_icon`. Spline FRAME and AMPLIFY inline. All rows fit 1,397 px (layout model and real-window captures).
- Compact All row (owner pick "A · Compact match", 2026-10-18, superseding "All stays as is"): Recommended All keeps the 12.9 tools; 25/50/75 become Breakdown ticks (tool-level `presets` + `ticks`), and nudges, Copy, Paste, Mirror, Bake Object and the Trails toggle show as icons. Tool records gain `ticks` (bool, default False); Tool Settings has Presets as Ticks for All and stages. Stage tabs return from about 1,450 px. The 12.9.1 All-row comparison is now expected to differ; saved records keep their own All row.
- Persistent popups (owner request 2026-10-18): family and More lists replace Blender's popup menus on the row (`_row_menu`, `_list_layout`; columns kept below the scrub strip, whose clicks Blender takes). A plain click on a popout slider makes it sticky (`_stick`, `_sticky_event`): drag on the track, double-click or click away applies, Esc cancels.
- Row edges (owner report 2026-10-18): the band lifts `SCROLLBAR_LIFT` (14 px) above the region bottom when markers do not already lift it, so the View2D horizontal scrollbar sits underneath; when the region reaches the area's left/right edge the layout is inset `CORNER_INSET` (16 px) so the end buttons avoid the area corner action zones.
- Per-row Toolbar Settings with live apply (owner request 2026-10-18): the Family dropdown is replaced by a **Row** dropdown (All, Block, Spline, Polish, Deliver) bound to the workspace stage, so the Timeline switches with it. All lists every tool; a stage lists only its families' tools, each tagged with its family. Every edit (mode, label, width, reorder, row switch) writes the record at once (`live_write`) and redraws the Timelines. The dialog is a plain `invoke_popup` (640 px): it stays open while the pointer moves, a click outside or Esc closes it and keeps the changes, and **Revert Changes** (`animassist.toolbar_revert`) restores the record captured when it opened.
- Any tool on any row, grouped by family (owner request 2026-10-18; supersedes "a stage lists only its families" and "a tool from another family pins into All"): a stage's families become its *home* families (defaults, always-shown menus). `validate_stage` keeps tools of any family; `row_families` = home families plus families with a visible tool on that row, in `FAMILY_ORDER`, and drives the row, its overflow list and More. `pin_target` returns the shown stage. Toolbar Settings lists all 96 tools for every row under collapsible family sections (`AA_ToolbarSection`, open state remembered per row for the session; a stage opens on its home families, All opens closed), with a name filter, per-tool display/label (or width for an inline slider), up/down within the family and a Tool Settings gear.
- Hover Explainers and existing shortcuts (owner request 2026-10-18): preference `explainer_mode` (FULL/SHORT/OFF, default FULL) in the add-on's General box. `core/explainers.register_class` registers each operator with an empty static description and a `description` callback (its own callback kept as `_aa_raw`; an optional `_aa_short` gives Short text); `bl_description` is restored on the Python class after registration. Full returns the full text, Short the first sentence (at most 120 characters, cut at a clause), Off the `bl_label` because Bforartists prints "(undocumented operator)" for an empty description. Row hover (`_shape_tooltip`) applies the same mode and returns nothing for Off. Shortcut lines come from the live user and add-on keyconfigs: active keyboard/mouse items whose idname and properties match the tool's operator, `animassist.timeline_tool` or `animassist.timeline_slider` for that action; none are invented. Property fields keep Bforartists' static tooltip (not configurable by an add-on).
- Native hints (owner pick "Add native hints", 2026-10-18): `timeline_catalog.NATIVE_EQUIVALENTS` maps row tools to Bforartists commands that do the same job (operator, settings). Hover text adds "Bforartists key: <keys> (<editors>: <command>)" only for active keyboard presses bound to them in the live keyconfig (no drags, double-clicks or mouse buttons), after the Anim Assist "Shortcut:" line; kept in Short, dropped in Off. Bforartists 5.2 binds Copy, Paste, Select All, Select More and the Dope Sheet time Scale (R) and Move (W); key types, handles, interpolation, snap, smooth, ease, blend to neighbour, breakdown, decimate, NLA bake and select mirror have no default key and show only when one is bound.
- Find and More, one job each (owner pick "C", 2026-10-18): utilities are [MORE "+N" if any] + SEARCH (24 px icon) + SETTINGS. `toolbar_layout` places the row against the budget without More; if tools are left over it reserves More's width (sized for "+99") and places again, so N is the count of visible tools not placed (equal to `_row_hidden_tools`). On a very narrow row Settings drops its name before the stage control is squeezed out, and More is dropped before Settings. The More list holds only "Did Not Fit"; family lists stay on the family buttons. `animassist.timeline_search` with an empty query shows a `family` tab row (opening on the shown row's first family) and every tool of that family with run and pin buttons; typing searches the whole catalogue.
- Stage dropdown at every width (owner request 2026-10-18: "these 5 to be dropdown options, not always next to one another"): `toolbar_layout` always leads with `STAGE_CYCLE` (named for the shown stage, shortened to its initial only when very tight); the `STAGE` tab kind is no longer laid out. The stage list, Ctrl+Wheel and View > Anim Assist Stage are unchanged.
