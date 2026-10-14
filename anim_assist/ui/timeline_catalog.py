"""Existing actions exposed in the add-on Timeline toolbar, grouped by task.

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
    "MIRROR_RANGE": ("p9_mirror_range", {}, "Mirror and Key Preview or Playback Range"),
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
    "COPY_KEYS": ("copy_selected_keys", {}, "Copy Selected Keys with Handles"),
    "PASTE_KEYS": ("paste_keys_at_frame", {}, "Paste Keys at Copied Times"),
    "BOOKMARK_ADD": ("add_bookmark", {}, "Save Reference Bookmark"),
    "BOOKMARK_REMOVE": ("remove_bookmark", {}, "Remove Active Reference Bookmark"),
    "BOOKMARK_RECALL": ("recall_bookmark", {}, "Set Reference from Active Bookmark"),
    "MATCH_WORLD": ("p8_match_to_world", {}, "Match Object to World Origin"),
    "MATCH_PARENT": ("p8_match_to_parent", {}, "Match Object to Parent"),
    "MATCH_TARGET": ("p8_match_to_target", {}, "Match Active Object to Selected Target"),
    "MATCH_LOCATION": ("p8_match_location", {}, "Match Object Location to Selected Target"),
    "MATCH_ROTATION": ("p8_match_rotation", {}, "Match Object Rotation to Selected Target"),
    "MATCH_SCALE": ("p8_match_scale", {}, "Match Object Scale to Selected Target"),
    "MATCH_TRS": ("p8_match_trs", {}, "Match Object Transforms to Selected Target"),
    "MATCH_VISUAL": ("p8_match_visual_matrix", {}, "Match Object Evaluated Matrix"),
    "MATCH_LOCAL": ("p8_match_local_matrix", {}, "Match Object Local Matrix"),
    "SWITCH_SINGLE": ("p8_compensate_single", {}, "Switch Configured Rig Property and Compensate"),
    "SWITCH_RANGE": ("p8_compensate_multi", {}, "Switch and Key Configured Rig Property in Range"),
    "SWITCH_BOOL": ("p8_switch_bool", {}, "Toggle Configured Rig Boolean and Compensate"),
    "SWITCH_ENUM": ("p8_switch_enum", {}, "Set Configured Rig Integer and Compensate"),
    "SWITCH_INFLUENCE": ("p8_switch_influence", {}, "Set Configured Rig Influence and Compensate"),
}

# Fixed nudge presets run immediately through the existing undoable execute path.
EXECUTE_ACTIONS = {"NUDGE_LEFT", "NUDGE_RIGHT", "MIRROR_RANGE", "BOOKMARK_ADD"}

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
    "PROXY_WORLD": "Create a temporary helper using the existing Copy Transforms proxy setup",
    "BAKE_CLEANUP": "Bake the active proxy session's constrained objects and remove that session's helpers. Uses existing bake settings",
    "PASTE_KEYS": "Paste copied absolute key times plus the paste offset onto matching Action names and curve paths; the playhead does not set the paste time",
}

GROUPS = (
    ("tween", "Tween", (
        "B25", "B50", "B75", "DRAG", None, "INBETWEEN", "INBETWEENS", None,
        "PUSH_PREV", "PULL_PREV", "PULL_NEXT", "PUSH_NEXT")),
    ("curves", "Curves", (
        "NEIGHBORS", "FRAME", "EASE", "AMPLIFY", "SMOOTH", "REFERENCE", None,
        "HANDLE_AUTO", "HANDLE_CLAMPED", "HANDLE_VECTOR", "HANDLE_ALIGNED", "HANDLE_FREE", None,
        "BOOKMARK_ADD", "BOOKMARK_RECALL", "BOOKMARK_REMOVE")),
    ("timing", "Timing", (
        "NUDGE_LEFT", "NUDGE_RIGHT", None, "T80", "T90", "T110", "T120", "SCALE_DRAG",
        "OFFSET_DRAG", "OFFSET_ACTION", None, "RIPPLE", "INSERT_TIME", "REMOVE_TIME",
        "DISTRIBUTE_TIME", "REVERSE", "SNAP")),
    ("keys", "Keys", (
        "ALL", "RANGE", "ENDS", None, "GROW_LEFT", "GROW_RIGHT", "GROW_BOTH", None,
        "TYPE_KEYFRAME", "TYPE_BREAKDOWN", "TYPE_HOLD", "TYPE_EXTREME", "TYPE_JITTER",
        "SELECT_BREAKDOWNS", None, "COPY_KEYS", "PASTE_KEYS")),
    ("pose", "Pose", (
        "MIRROR_ACTIVE", "MIRROR_SELECTED", "MIRROR_FRAME", "MIRROR_RANGE", None,
        "OPPOSITE", "SWAP", "ALIGN", None,
        "MATCH_WORLD", "MATCH_PARENT", "MATCH_TARGET", "MATCH_LOCATION", "MATCH_ROTATION",
        "MATCH_SCALE", "MATCH_TRS", "MATCH_VISUAL", "MATCH_LOCAL", None,
        "SWITCH_SINGLE", "SWITCH_RANGE", "SWITCH_BOOL", "SWITCH_ENUM", "SWITCH_INFLUENCE")),
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
    if getattr(prefs,'timeline_layouts_json',''):
        from .timeline_config import decode
        try:
            tools=decode(prefs.timeline_layouts_json,ACTIONS)['active']['tools']
            return frozenset(action for action in ACTIONS if tools[action]['mode']!='HIDDEN')
        except ValueError:
            pass
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
    if action == "EASE":
        prerequisite = "Select at least two keys on the same editable curve; include an interior key to reshape it"
    if action.startswith("HANDLE_") or action.startswith("TYPE_") or action.startswith("NUDGE_"):
        scope, prerequisite = _SELECTED_KEY_SCOPE
    if action.startswith(("TYPE_", "NUDGE_")):
        scope = "Selected keys in the active object's Action"
        prerequisite = "Select keys in the active object's Action"
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
    if action in {"COPY_KEYS", "PASTE_KEYS"}:
        scope = "Editable, unhidden, unmuted view-layer Action curves matched by Action name, path and array index"
        prerequisite = "Select editable keys to copy" if action == "COPY_KEYS" else "Copy keys into the Anim Assist clipboard first"
    if action.startswith("BOOKMARK_"):
        scope = "Scene reference-frame bookmarks; recall sets the reference without moving the playhead"
        prerequisite = "Set a reference frame" if action == "BOOKMARK_ADD" else "Choose an existing reference bookmark"
    if action.startswith("MATCH_"):
        scope = "Active object's transforms using matching filters, locks, offset and keying settings"
        prerequisite = "Select an active object in Object or Pose mode"
        if action == "MATCH_PARENT":
            prerequisite = "Select an object with a parent"
        elif action not in {"MATCH_WORLD"}:
            prerequisite = "Select a reference object and make the object to match active"
    if action.startswith("SWITCH_"):
        scope = "Configured object or pose-bone property; compensate its evaluated transform using rig switch settings"
        prerequisite = "Configure a writable numeric rig property and target value in Pose options"
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
    parts.append(f"Also in {FAMILY[action][1]} > {ACTIONS[action][2]}.")
    return " ".join(parts)


# Original search terms describe concepts, not another application's guarantees.
SEARCH_TERMS = {
    "B25": "tween breakdown quarter", "B50": "tween breakdown halfway", "B75": "tween breakdown three quarters",
    "DRAG": "tween slider blend", "NEIGHBORS": "tween neighbors slider", "FRAME": "tween reference slider",
    "AMPLIFY": "scale amplitude push pull slider", "SMOOTH": "smooth roughen slider",
    "OFFSET_DRAG": "time offset offsetter timing slider", "OFFSET_ACTION": "time offset offsetter timing",
    "SCALE_DRAG": "retime scale timing slider",
    "COPY_KEYS": "clipboard copy animation", "PASTE_KEYS": "clipboard paste animation",
    "BOOKMARK_ADD": "reference bookmark save", "BOOKMARK_RECALL": "reference bookmark load",
    "BOOKMARK_REMOVE": "reference bookmark delete",
    "SWITCH_SINGLE": "space switch rig compensate", "SWITCH_RANGE": "space switch rig bake compensate",
    "SWITCH_BOOL": "space switch rig boolean", "SWITCH_ENUM": "space switch rig integer enum",
    "SWITCH_INFLUENCE": "space switch rig constraint influence",
}


def search_actions(query):
    """Stable token matching across the complete catalogue, including aliases."""
    terms = query.casefold().split()
    return tuple(action for action, (suffix, _arguments, label) in ACTIONS.items()
                 if all(term in f"{action} {label} {FAMILY[action][1]} {suffix} {SEARCH_TERMS.get(action, '')}".casefold()
                        for term in terms))


def toolbar_plan(logical_width):
    """Conservative native-size budgets; no selection or session dependency."""
    return {
        "compact": logical_width < 900,
        "tween": logical_width >= 360,
        "timing": logical_width >= 1120,
        "keys": logical_width >= 1260,
    }
