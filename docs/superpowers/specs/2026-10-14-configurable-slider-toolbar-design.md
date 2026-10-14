# Configurable Anim Assist slider toolbar

Date: 2026-10-14. Status: design agreed in conversation; implementation not started.
Baseline: local Anim Assist 12.6.1, commit `b05f243`. Published 12.6.0 is a
different artifact. User selected A, configurable popout sliders, tool settings,
two recommended visible sliders and user-named saved layouts, then requested a
GSD plan with existing-tool verification.

## User experience

Keep the add-on-only second row beside the Timeline header. Order families
Tween, Timing, Curves, Keys, Pose, Bake, Motion. Search, More and Settings are
at the right. Never lengthen the native playback header, create a helper editor,
ship an application patch, or repeatedly resize the workspace.

Fresh installs start with Breakdown and Smooth as visible inline sliders.
Breakdown has 25/50/75 presets. Timing shows -1f/+1f and a Timing Scale popout
control. Keys shows Copy/Paste, Pose Mirror Selected, Bake Bake Object, and
Motion Show Trails. Other tools are available in More/Search and configurable.
Labels accompany the icons by default. Family menus remain available.

Toolbar Settings is a native settings dialog, not a second editor. It lists all
89 catalogue entries by family, with per-tool display mode, order, label/icon
choice, slider width and an Open Tool Settings action. Modes are Hidden,
Button, Popout Slider and Inline Slider. Non-scalar tools offer only Hidden
and Button. Buttons for scalar tools retain their existing invocation behavior;
the two slider modes use the new hold/drag/release behavior.

An inline slider starts a preview when pressed. A popout slider starts from a
direct press and drag on its tool control; its track appears near the control,
without choosing from a menu or moving the row. Release commits one undoable
operation; Esc/right-click cancels. A small movement threshold distinguishes
a drag from a click. A click without movement makes no animation change and
explains the drag affordance. Shift provides precision. Supported numeric entry
uses Enter to commit. A settings edit or layout load never edits animation.

Tool Settings exposes range, default, sensitivity, precision, snap and editable
presets only where the tool supports them. Show whether other options are
scene-specific. Reuse existing masks, anchors and target settings instead of
creating independent copies with conflicting values. Right-click opens tool
settings while idle; during a drag it cancels. Settings has another explicit
entry so it is discoverable. Breakdown keeps the existing anchor explanation.

Named layouts save toolbar presentation, tool order, display modes, slider
configuration and launch defaults. Save As, Load, Update Saved Layout, Rename
and Delete are available. Names are user-entered Unicode, trimmed, nonempty,
at most 64 characters and unique case-insensitively; duplicates report an
actionable error rather than overwrite. The built-in Recommended layout cannot
be deleted or overwritten. Restore Recommended Layout changes the active
layout without deleting saved layouts. Edited layouts show an unsaved marker.
No scene, animation, clipboard, reference-frame or rig-target state is stored
in a toolbar layout. All choices persist in add-on preferences across restart.

## Scalar capability boundary

| Action | Meaning / units | Starting range | Safety boundary |
| --- | --- | --- | --- |
| DRAG | Breakdown blend, percent | 0–100, default 50 | Existing factor -1 to 2; optional overshoot -100–200 |
| SMOOTH | Smooth/rough amount, percent | 0–100, default 0 | Negative roughening and overshoot require explicit settings and effect tests |
| NEIGHBORS | Blend to neighbors, percent | 0–100, default 0 | Finite values; extended range only after effect/cancel tests |
| FRAME | Blend to reference frame, percent | 0–100, default 0 | Uses existing reference settings; extended range must be verified |
| EASE | Ease blend, percent | 0–100, default 0 | Existing math remains authoritative; extended range must be verified |
| AMPLIFY | Signed push/pull amount, percent | -100–200, default 0 | Label signed amount, not absolute scale; finite verified limits |
| SCALE_DRAG | Key timing scale, percent | 50–200, default 100 | Existing minimum factor 0.01 = 1%; no artificial 120% maximum |
| OFFSET_DRAG | Active Action timing offset, frames | -10–10, default 0 | Adjustable finite view range; preserve existing frame snapping |

Ranges in this table are viewport/interaction defaults, not new mathematical
restrictions. Per-tool settings can extend the display range within verified
backend limits. Do not infer that RNA soft bounds prove arbitrary values safe.
The ninth interactive entry, OFFSET (Anim Offset), edits live transforms in a
session rather than one scalar; retain its existing session button/settings.
Ordinary actions such as Copy, Paste and Show Trails do not acquire fake sliders.

## Architecture and recovery

Reuse the public pixel draw handler and native keymaps in timeline_overlay.py.
There is no add-on API for a second true native HEADER region. The row remains
a canvas band. Separate pure layout/model code, a small scalar capability
registry and an undoable slider operator. Reuse the existing core math and
snapshot conventions; never repeatedly invoke undoable operators for previews.
Capture targets/settings once per gesture, restore the starting snapshot before
each preview, then apply an absolute value. Modal state is transient and tied
to the originating window/area; no active gesture is saved in preferences.
Invalid targets, disappearing areas, disable/reload and exceptions must restore
the snapshot and remove temporary UI. Other editors and Timeline canvas outside
the row/active gesture keep their normal input.

On narrow timelines shorten labels and widths to their minimums first, then
turn inline controls into temporary popout presentation, then move lower-priority
buttons to More. Never alter saved modes/order merely because width changes.
No scrolling is needed to reach essentials at supported desktop widths. At a
fully collapsed canvas the band cannot be drawn; report the existing limitation.

Fresh defaults have exactly two inline sliders. Migration preserves explicitly
selected/hidden old quick actions and a hidden row; selected scalar controls can
be migrated to popout mode, selected ordinary controls to Button. Do not replace
an existing personalized selection with the recommended layout. Existing legacy
checkbox fields remain readable during migration and settings import.

## Evidence and endpoint

Run a fresh real-host verification of current tools before code changes, then
the same fixtures through the new controls. A registered operator or FINISHED
return alone is not a pass. Require numeric key/handle/pose/time/clipboard and
motion-trail effects, exact cancellation and undo recovery, correct scope and
disabled-state explanations. Compare direct dispatch, existing bar and new bar.
Capture still images for default, drag, settings and saved-layout states; no
screen/audio recording is part of this plan.

Endpoint: a local add-on ZIP whose exact installed bytes pass the baseline,
new slider, persistence, layout, lifecycle and native-input gates; named layouts
survive a normal restart; human usability is reviewed separately. No push,
merge or publication without the owner's exact Confirm merge update approval.
Full AnimBot algorithm parity and unrelated add-on redesigns are outside scope.

Executable plans: [GSD packet](../../anim_assist/plans/2026-10-14-configurable-slider-toolbar/README.md).
