"""Existing actions exposed in the Timeline strip, grouped by animation task.

Concept mapping: docs/anim_assist/releases/12.3.0/animbot-matches.md.
Names describe our actual scope; they do not promise animBot feature parity.
All entries are day-to-day actions (top tier). Bake/proxy settings remain in
their existing sidebar home (mid tier); setup and file procedures are excluded.
"""

from ..constants import BREAKDOWN_ANCHOR_HINT

# (existing operator suffix, fixed arguments, menu label). No scene overrides.
ACTIONS = {
    "B25": ("breakdown_percentage", {"percent": 25}, "25% Breakdown"),
    "B50": ("breakdown_percentage", {"percent": 50}, "50% Breakdown"),
    "B75": ("breakdown_percentage", {"percent": 75}, "75% Breakdown"),
    "DRAG": ("modal_drag_breakdown", {}, "Drag Breakdown"),
    "PUSH_PREV": ("breakdown_push_prev", {}, "Push Previous"),
    "PULL_PREV": ("breakdown_pull_prev", {}, "Pull Previous"),
    "PULL_NEXT": ("breakdown_pull_next", {}, "Pull Next"),
    "PUSH_NEXT": ("breakdown_push_next", {}, "Push Next"),
    "T80": ("p6_scale_keys", {"scale_factor": 0.8}, "Scale Key Spacing to 80%"),
    "T90": ("p6_scale_keys", {"scale_factor": 0.9}, "Scale Key Spacing to 90%"),
    "T110": ("p6_scale_keys", {"scale_factor": 1.1}, "Scale Key Spacing to 110%"),
    "T120": ("p6_scale_keys", {"scale_factor": 1.2}, "Scale Key Spacing to 120%"),
    "RIPPLE": ("p6_ripple_forward", {}, "Ripple Forward"),
    "RANGE": ("select_frame_range", {}, "Select Frame Range"),
    "ALL": ("select_all_visible", {}, "Select All Visible Keys"),
    "ENDS": ("select_first_last", {}, "Select First and Last Keys"),
    "OFFSET": ("anim_offset", {}, "Offset Active Action"),
    "INBETWEEN": ("inbetween_selected_gap", {}, "Add Inbetween in Selected Gap"),
    "INBETWEENS": ("inbetween_distribute", {}, "Distribute Inbetweens in Selected Gap"),
    "NEIGHBORS": ("blend_neighbor", {}, "Blend to Neighbors (Drag)"),
    "FRAME": ("blend_frame", {}, "Blend to Frame (Drag)"),
    "EASE": ("ease_to_ease", {}, "Blend to Ease (Drag)"),
    "AMPLIFY": ("push_pull", {}, "Scale Values from Reference (Drag)"),
    "SMOOTH": ("smooth_keys", {}, "Smooth Keys (Drag)"),
    "REFERENCE": ("set_reference_frame", {}, "Set Reference Frame from Playhead"),
    "HANDLE_AUTO": ("set_handle_type", {"handle_type": "AUTO"}, "Auto Handles"),
    "HANDLE_CLAMPED": ("set_handle_type", {"handle_type": "AUTO_CLAMPED"}, "Auto Clamped Handles"),
    "HANDLE_VECTOR": ("set_handle_type", {"handle_type": "VECTOR"}, "Vector Handles"),
    "HANDLE_ALIGNED": ("set_handle_type", {"handle_type": "ALIGNED"}, "Aligned Handles"),
    "HANDLE_FREE": ("set_handle_type", {"handle_type": "FREE"}, "Free Handles"),
    "NUDGE_LEFT": ("move_keys", {"offset": -1}, "Nudge Selected Keys -1 Frame"),
    "NUDGE_RIGHT": ("move_keys", {"offset": 1}, "Nudge Selected Keys +1 Frame"),
    "SCALE_DRAG": ("p6_modal_scale", {}, "Scale Key Timing (Drag)"),
    "OFFSET_DRAG": ("p6_modal_offset", {}, "Offset Action Timing (Drag)"),
    "OFFSET_ACTION": ("p6_offset_keys", {}, "Offset Action Timing"),
    "INSERT_TIME": ("p6_insert_time", {}, "Insert Time at Playhead"),
    "REMOVE_TIME": ("p6_remove_time", {}, "Remove Time and Keys at Playhead"),
    "DISTRIBUTE_TIME": ("p6_distribute_keys", {}, "Distribute Key Timing in Range"),
    "REVERSE": ("p6_reverse_keys", {}, "Reverse Key Timing in Range"),
    "SNAP": ("p6_snap_to_frames", {}, "Round Key Times"),
    "GROW_LEFT": ("select_neighbors", {"direction": "LEFT"}, "Grow Key Selection Left"),
    "GROW_RIGHT": ("select_neighbors", {"direction": "RIGHT"}, "Grow Key Selection Right"),
    "GROW_BOTH": ("select_neighbors", {"direction": "BOTH"}, "Grow Key Selection Both Sides"),
    "TYPE_KEYFRAME": ("set_key_type", {"key_type": "KEYFRAME"}, "Mark as Keyframe"),
    "TYPE_BREAKDOWN": ("set_key_type", {"key_type": "BREAKDOWN"}, "Mark as Breakdown"),
    "TYPE_HOLD": ("set_key_type", {"key_type": "MOVING_HOLD"}, "Mark as Moving Hold"),
    "TYPE_EXTREME": ("set_key_type", {"key_type": "EXTREME"}, "Mark as Extreme"),
    "TYPE_JITTER": ("set_key_type", {"key_type": "JITTER"}, "Mark as Jitter"),
    "SELECT_BREAKDOWNS": ("select_by_key_type", {"key_type": "BREAKDOWN"}, "Select Breakdown Keys"),
    "MIRROR_ACTIVE": ("p9_mirror_pose", {}, "Mirror Active Bone to Opposite"),
    "MIRROR_SELECTED": ("p9_mirror_selected", {}, "Mirror Selected Bones"),
    "MIRROR_FRAME": ("p9_mirror_frame", {}, "Mirror and Key Current Frame"),
    "MIRROR_RANGE": ("p9_mirror_range", {}, "Mirror and Key Frame Range..."),
    "OPPOSITE": ("p9_select_opposite", {}, "Select Opposite of Active Bone"),
    "SWAP": ("p9_swap_poses", {}, "Swap Left/Right Poses"),
    "ALIGN": ("p8_match_selected_to_active", {}, "Align Selected Objects to Active"),
    "BAKE_STEP": ("p7_bake_step", {}, "Bake Object Transforms"),
    "SMART_BAKE": ("p7_smart_bake", {}, "Bake Object Transforms and Reduce"),
    "REDUCE": ("p7_reduce_keys", {}, "Reduce Keys"),
    "PROXY_TRANSLATION": ("p7_create_proxy", {"proxy_type": "TRANSLATION"}, "Create Object Translation Proxy"),
    "PROXY_ORIENTATION": ("p7_create_proxy", {"proxy_type": "ORIENTATION"}, "Create Object Orientation Proxy"),
    "PROXY_WORLD": ("p7_create_proxy", {"proxy_type": "WORLD_SPACE"}, "Create Object World-Space Proxy"),
    "PROXY_PARENT": ("p7_create_proxy", {"proxy_type": "PARENT_SPACE"}, "Create Object Parent-Space Proxy"),
    "BAKE_CLEANUP": ("p7_one_click_cleanup", {}, "Bake Session and Remove Proxies"),
    "TRAIL_SHOW": ("p5_enable_overlay", {}, "Show World Motion Trails"),
    "TRAIL_HIDE": ("p5_disable_overlay", {}, "Hide World Motion Trails"),
    "TRAIL_REFRESH": ("p5_refresh_overlay", {}, "Refresh World Motion Trails"),
    "TRAIL_DIAGNOSE": ("p5_run_diagnostics", {}, "Diagnose Motion Arcs"),
    "OFFSET_MASK": ("anim_offset_toggle_mask", {}, "Toggle Anim Offset Mask"),
    "OFFSET_SCENE_RANGE": ("anim_offset_range_from_scene", {}, "Set Offset Mask from Scene Range"),
}

# Fixed nudge presets run immediately through the existing undoable execute path.
EXECUTE_ACTIONS = {"NUDGE_LEFT", "NUDGE_RIGHT"}

TIPS = {
    "NEIGHBORS": "Drag to blend selected keys toward the line between bounding neighbors. Esc restores the keys",
    "FRAME": "Drag selected keys toward their reference-frame value. Set the reference from the playhead first; Esc cancels",
    "EASE": "Drag selected keys from linear spacing toward eased spacing. Esc restores the keys",
    "AMPLIFY": "Drag to scale selected key values around the reference-frame value. This changes curve amplitude, not timing",
    "SMOOTH": "Drag selected keys toward neighboring averages; negative factors roughen the curve",
    "NUDGE_LEFT": "Move selected keys one frame earlier, carrying their handles",
    "NUDGE_RIGHT": "Move selected keys one frame later, carrying their handles",
    "OFFSET_ACTION": "Move key times in the active object's Action using its timing offset and range settings. This is not limited to selected keys",
    "OFFSET_DRAG": "Drag to move all key times in the active object's Action. Esc restores them; this does not keep key positions fixed",
    "REMOVE_TIME": "Remove the configured playhead time window, delete keys inside it, and shift later keys backward",
    "SNAP": "Round key times in the active Action to whole frames. This does not resample values to preserve poses",
    "ALIGN": "Match other selected objects to the active object's evaluated transform using your matching channel, offset and lock settings",
    "BAKE_STEP": "Bake the active object's evaluated transform using the existing bake range and Frame Step settings",
    "SMART_BAKE": "Bake the active object's evaluated transform, then reduce keys using the existing reduction tolerance",
    "REDUCE": "Reduce the active object's animation using the existing key-reduction tolerance",
    "PROXY_WORLD": "Create a temporary helper using the existing Copy Transforms proxy setup. It is not an editable temporary pivot",
    "BAKE_CLEANUP": "Bake the active proxy session's constrained objects and remove that session's helpers. Uses existing bake settings",
}

GROUPS = (
    ("tween", "Tween", (
        "B25", "B50", "B75", "DRAG", None, "INBETWEEN", "INBETWEENS", None,
        "PUSH_PREV", "PULL_PREV", "PULL_NEXT", "PUSH_NEXT")),
    ("curves", "Curves", (
        "NEIGHBORS", "FRAME", "EASE", "AMPLIFY", "SMOOTH", "REFERENCE", None,
        "HANDLE_AUTO", "HANDLE_CLAMPED", "HANDLE_VECTOR", "HANDLE_ALIGNED", "HANDLE_FREE")),
    ("timing", "Timing", (
        "NUDGE_LEFT", "NUDGE_RIGHT", None, "T80", "T90", "T110", "T120", "SCALE_DRAG",
        "OFFSET_DRAG", "OFFSET_ACTION", None, "RIPPLE", "INSERT_TIME", "REMOVE_TIME",
        "DISTRIBUTE_TIME", "REVERSE", "SNAP")),
    ("keys", "Keys", (
        "ALL", "RANGE", "ENDS", None, "GROW_LEFT", "GROW_RIGHT", "GROW_BOTH", None,
        "TYPE_KEYFRAME", "TYPE_BREAKDOWN", "TYPE_HOLD", "TYPE_EXTREME", "TYPE_JITTER",
        "SELECT_BREAKDOWNS")),
    ("pose", "Pose", (
        "MIRROR_ACTIVE", "MIRROR_SELECTED", "MIRROR_FRAME", "MIRROR_RANGE", None,
        "OPPOSITE", "SWAP", "ALIGN")),
    ("bake", "Bake", (
        "BAKE_STEP", "SMART_BAKE", "REDUCE", None, "PROXY_TRANSLATION",
        "PROXY_ORIENTATION", "PROXY_WORLD", "PROXY_PARENT", "BAKE_CLEANUP")),
    ("motion", "Motion", (
        "TRAIL_SHOW", "TRAIL_HIDE", "TRAIL_REFRESH", "TRAIL_DIAGNOSE", None,
        "OFFSET", "OFFSET_MASK", "OFFSET_SCENE_RANGE")),
)

# Shared by inline buttons, family menus and More. Scene state never chooses
# positions. More deliberately contains all shortcuts, including inline ones.
QUICK_GROUPS = (
    ("tween", "Tween", ("B25", "B50", "B75", "DRAG")),
    ("curves", "Curves", ("PUSH_PREV", "PULL_PREV", "PULL_NEXT", "PUSH_NEXT")),
    ("timing", "Timing", ("T80", "T90", "T110", "T120", "RIPPLE")),
    ("keys", "Keys", ("RANGE", "ALL", "ENDS")),
    ("motion", "Motion", ("OFFSET",)),
)
FAMILY = {action: (key, label) for key, label, actions in GROUPS
          for action in actions if action is not None}

# Saved quick selection belongs to the add-on, not to a scene or screen width.
DEFAULT_QUICK_ACTIONS = (
    "B25", "B50", "B75", "DRAG", "SMOOTH", "NUDGE_LEFT", "NUDGE_RIGHT",
    "RIPPLE", "RANGE", "ENDS", "MIRROR_SELECTED", "BAKE_STEP", "TRAIL_SHOW",
)
QUICK_LABELS = {
    "B25": "25%", "B50": "50%", "B75": "75%", "DRAG": "Drag",
    "SMOOTH": "Smooth", "NUDGE_LEFT": "-1f", "NUDGE_RIGHT": "+1f",
    "RIPPLE": "Ripple", "RANGE": "Range", "ENDS": "Ends",
    "MIRROR_SELECTED": "Mirror Sel", "BAKE_STEP": "Bake Object",
    "TRAIL_SHOW": "Show Trails",
}


def quick_property_name(action):
    """Stable RNA name; never derive preference identity from a display label."""
    if action not in ACTIONS:
        raise KeyError(action)
    return "timeline_quick_" + action.lower()


def selected_quick_actions(prefs):
    """Missing preferences use defaults; an explicitly empty set stays empty."""
    defaults = frozenset(DEFAULT_QUICK_ACTIONS)
    if prefs is None:
        return defaults
    return frozenset(action for action in ACTIONS
                     if getattr(prefs, quick_property_name(action), action in defaults))


def quick_clusters(selected_actions):
    """Every family, with selected known actions in permanent catalog order."""
    selected = set(selected_actions).intersection(ACTIONS)
    return tuple((key, label, tuple(action for action in actions
                                   if action is not None and action in selected))
                 for key, label, actions in GROUPS)

_SCOPES = {
    "tween": ("Active object's Action; selected/active pose bones when in Pose mode, using Breakdown mask/exclusions",
              "Select an object with an Action"),
    "curves": ("Selected keys on editable selected curves, or the active object's Action when no editor curves are supplied",
               "Select editable keys on an animated object"),
    "timing": ("Active object's Action using Timing range/anchor settings",
               "Select an object with an Action"),
    "keys": ("Editable, unhidden and unmuted curves across view-layer Actions",
             "Have editable animation curves in the view layer"),
    "pose": ("Active armature in Pose mode using bone-pair settings",
             "Select an armature and an active bone in Pose mode"),
    "bake": ("Active object using Object Bake range, step and reduction settings",
             "Select an object; session cleanup requires an existing proxy session"),
    "motion": ("World trajectories of configured object/bone targets using Motion Trail settings",
               "Use the Motion Trail target settings"),
}
_SELECTED_KEY_SCOPE = (
    "Selected keys on editor-selected curves, or the active object's Action",
    "Select keys on an animated object",
)


def command_metadata(action):
    """Return scope, prerequisite and gesture, independent of UI location."""
    family = FAMILY[action][0]
    scope, prerequisite = _SCOPES[family]
    gesture = ""
    if action.startswith("HANDLE_") or action.startswith("TYPE_") or action.startswith("NUDGE_"):
        scope, prerequisite = _SELECTED_KEY_SCOPE
    if action == "SELECT_BREAKDOWNS":
        scope = "Editor-selected curves, or the active object's Action; selects keys by type"
        prerequisite = "Have curves on the active object's Action"
    if action in {"INBETWEEN", "INBETWEENS"}:
        scope = "Selected key gap in the active object's Action using Breakdown settings"
        prerequisite = "Select two bounding keys with a gap"
    if action in {"OFFSET_DRAG"}:
        scope = "All key times in the active object's Action"
    if action == "ALIGN":
        scope = "Other selected objects matched to the active object's evaluated transform"
        prerequisite = "Select a target object and make the reference object active"
    if action.startswith("PROXY_"):
        scope = "Active object; temporary constrained object helper"
        prerequisite = "Select the object to drive through a proxy"
    if action == "BAKE_CLEANUP":
        scope = "Constrained objects and helpers in the existing proxy session"
    if action == "REDUCE":
        prerequisite = "Select an object with an Action to reduce"
    if action == "OFFSET":
        scope = "Captured active object's editable Action curves; live frame mask with blend margins"
        prerequisite = "Select an object with editable Action curves to start Offset"
    if action in {"OFFSET_MASK", "OFFSET_SCENE_RANGE"}:
        scope = "Scene's live Action Offset frame mask; affects an active session immediately"
        prerequisite = "Choose the frame range and blend margins in Offset settings"
    if action == "REFERENCE":
        scope, prerequisite = "Scene playhead; stores the reference frame", "Choose the desired reference frame"
    if action == "DRAG":
        gesture = "Release left mouse to apply; Esc/right mouse restores the pre-drag keys"
    elif action in {"NEIGHBORS", "FRAME", "EASE", "AMPLIFY", "SMOOTH", "SCALE_DRAG", "OFFSET_DRAG"}:
        gesture = "Left click or Enter applies; Esc/right click cancels"
    elif action == "OFFSET":
        gesture = "Click again to finish; Esc uses the existing Offset snapshot restore"
    return scope, prerequisite, gesture


def command_description(action, operation):
    scope, prerequisite, gesture = command_metadata(action)
    parts = [f"Scope: {scope}.", f"{ACTIONS[action][2]}: {TIPS.get(action) or operation}.",
             f"Requires: {prerequisite}."]
    if action in {"B25", "B50", "B75", "DRAG"}:
        parts.append(BREAKDOWN_ANCHOR_HINT)
    if gesture:
        parts.append(gesture + ".")
    parts.append(f"Also in {FAMILY[action][1]} > {ACTIONS[action][2]}. Uses the Timeline below.")
    return " ".join(parts)


def toolbar_plan(logical_width):
    """Conservative native-size budgets; no selection or session dependency."""
    return {
        "compact": logical_width < 900,
        "tween": logical_width >= 360,
        "timing": logical_width >= 1120,
        "keys": logical_width >= 1260,
    }
