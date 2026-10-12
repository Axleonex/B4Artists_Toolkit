# UI and Behavior Contract

## Design plan

**Subject:** An animator repeatedly adjusting animation from the Timeline.

**Treatment:** Native UI/tool; the mockups communicate design intent only.

**Palette:** Inherit the host theme. Preview references: ground `#242424`, surface `#303030`, buttons `#484848`, ink `#eeeeee`, secondary ink `#bbbbbb`, active state `#4778ad`. No hardcoded product palette.

**Type:** Inherit native UI font and sizes. Short text labels with full action names in tooltips.

**Layout:** One thin owned Text Editor header above the Timeline. Gear first, then seven menu/action clusters separated by native separators. Normal native control heights and widths; no automatic overflow and no third row.

## Known, inferred, and open

- Known: the owner rejected menu navigation for routine commands and approved inline clusters with configurable quick selection.
- Known: 12.4.0 has 70 presets, seven menu families, a shared Timeline dispatcher, and fixed width thresholds that hide quick groups.
- Inferred: family adjacency reduces the search between category and quick action.
- Planning choice: seven fixed menus, global saved selections, and the 13-action default below.
- Open: native panning in the owned header at all widths/scales, precise default-row fit, actual Bforartists behavior and owner usability. These are implementation qualification tasks.

## Defaults and truthful names

| Family | Action IDs | Inline text |
| --- | --- | --- |
| Tween | B25, B50, B75, DRAG | 25%, 50%, 75%, Drag |
| Curves | SMOOTH | Smooth |
| Timing | NUDGE_LEFT, NUDGE_RIGHT, RIPPLE | -1f, +1f, Ripple |
| Keys | RANGE, ENDS | Range, Ends |
| Pose | MIRROR_SELECTED | Mirror Sel |
| Bake | BAKE_STEP | Bake Object |
| Motion | TRAIL_SHOW | Show Trails |

Push/Pull presets belong to Tween according to `GROUPS` and `FAMILY`, despite the historical quick group being named Curves. Keep the operator and its menu family unchanged; place a newly pinned Push/Pull action beside Tween. Bake Object retains active-object scope. Show Trails is an action, not a fabricated on/off toggle. Other pinned actions use an explicit compact label when provided, otherwise their full menu label. Do not invent shorter labels that change meaning.

## Configuration model

Use one BoolProperty per action on `AA_AddonPreferences`, named `timeline_quick_<lowercase action ID>`, for example `timeline_quick_b50`. Stable action IDs are the source of identity. Seventy options must not be packed into an ENUM_FLAG integer.

Keep pure data and helpers in `ui/timeline_catalog.py`: `DEFAULT_QUICK_ACTIONS`, `QUICK_LABELS`, `quick_property_name(action)`, and `quick_clusters(selected_actions)`. The cluster helper filters against known IDs, removes duplicates, walks existing `GROUPS` order, and returns every family with its selected actions in catalog order. No scene state or width enters this helper.

`prefs.py` supplies `prepare_timeline_quick_preferences()` and installs the BoolProperty declarations immediately before `_build_registry()` registers the preferences class. Import catalog data inside that preparation function, after normal package imports have completed. Importing the UI package from the preferences module's top level would risk the existing UI/header/preferences import cycle. Repeat registration must neither duplicate declarations nor overwrite saved user values.

Each field uses its catalog menu label and a description that says it places a quick copy next to the relevant family. New installs and upgrades lacking these fields receive the 13 defaults. All fields set false is a valid custom configuration; never treat it as missing initialization. When preferences are unavailable, render the documented default set without attempting to write preferences from a draw callback.

Preference changes tag owned strips for redraw in every open window. They do not split/join areas, call `_sync` directly, save preferences automatically, or invoke animation operators. Persistence follows Blender/Bforartists' native preference-saving behavior. If automatic saving is disabled, the configuration view explains that Save Preferences is needed.

## Settings home

The owned Timeline strip gear opens `ANIMASSIST_PT_timeline_quick_settings`, labeled **Timeline Quick Tools**. Show:

1. The existing Toolbar Above Timeline preference.
2. **Quick buttons / Saved in add-on preferences**.
3. A family selector `timeline_quick_family` (an ordinary EnumProperty for viewing one of seven families).
4. Native checkboxes for every non-separator action in that family, using full catalog labels.
5. **Reset All Quick Buttons to Defaults**, with a tooltip explaining that it resets all seven families.
6. Native preference-save guidance and horizontal-pan guidance.

Viewing a family is configuration, not action dispatch. The checkbox list must include unchecked and temporarily unavailable tools. Its size must fit the native popup at the tested scale. Use the same settings view when opened from add-on preferences; do not maintain a second independent checkbox layout. The reset operator edits preferences only, is INTERNAL, and creates no animation Undo step.

The existing non-strip `ANIMASSIST_PT_header_toolbar_options` retains its scene-wide category checkboxes and their current semantics. The new strip no longer reads `header_show_*` to hide its clusters. This explicitly separates Timeline quick customization from legacy Graph/Dope Sheet header visibility.

## Drawing and width

Replace `_draw_toolbar()`'s `toolbar_plan(width)` branches with a deterministic sequence: Gear, separator, then each family menu immediately followed by its selected quick buttons. Always use `_button()` for actions. An empty family still has its menu.

Remove More from the owned strip; every former More command remains in its single family menu and can be selected as a quick button. Do not retain the existing width-triggered Tools consolidation. The native Timeline fallback and other editor toolbars keep their existing behavior when the owned strip is disabled/unavailable.

Use native horizontal header panning on overflow. Do not create a custom scrolling animation, narrow the hit targets, rescale labels, truncate with ellipses or automatically unpin tools. The gear is first so configuration is reachable at the initial pan position. Describe panning with the gesture observed in the actual host, not a guessed shortcut. Native panning is a go/no-go check before claiming the layout works; if the host cannot reach the rightmost control, report that failure and revise the layout proposal explicitly.

## Interaction and recovery

Scrub the native Timeline, then click a visible quick action. The shared dispatcher supplies the paired Timeline context and existing fixed arguments. Nudge uses EXEC_DEFAULT; existing modal tools retain INVOKE_DEFAULT. Some existing tools request range/input after invocation; pinning their launcher does not eliminate required tool input.

After a checkbox change, its quick copy appears/disappears in catalog order while menu access remains. Object or scene selection changes only disabled/highlight state. No automatic usage ranking, mode-based reordering or global scope selector is introduced.

Preserve target-owned Undo with `operator(mode, True, **arguments)`, wrapper without a second UNDO step, 12.4.0 Drag snapshots, Offset semantics, and Breakdown anchor help. An unavailable action stays visible and uses the existing reason. A running Offset action highlights the specific pinned Offset button; do not suggest unrelated actions affect that session.

## Qualification

Record default/custom/empty selections; save/restart; two scenes and two Timelines; 100% and 150% scaling; narrow and wide panning; Pose/Object availability; popup clipping; and native apply/cancel/Undo/Redo. The owner task is to insert a Breakdown, nudge selected keys, pin Smooth and Mirror Selected, find those buttons without opening a tool menu, and unpin one while retaining menu access. Report native and owner evidence separately.

Deviations from the earlier previews: Gear moves to the start for overflow access; Push/Pull follows its verified Tween family. These are explicit implementation choices. No user-performance improvement has yet been measured.
