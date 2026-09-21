"""Offline, hash-bound hands-on correction trial for the v13 review scenes.

This developer evaluation helper is intentionally separate from the release add-on.
It never uploads data and never treats automated interaction as a human result.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import os
import sys
import time

import bpy


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
_CONFIG = {}
_SESSIONS = {}
_TIMER_RUNNING = False
FAILURE_FIELDS = (
    "foot_slide", "penetration", "popping", "stretch",
    "timing", "balance", "intent_loss", "other",
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_hash(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _curves(obj, action):
    from b4artists_ml import workflow
    identifier = workflow._slot(obj.animation_data)
    slot = None
    if hasattr(action, "slots") and len(action.slots) > 1:
        slot = next((candidate for candidate in action.slots if candidate.identifier == identifier), None)
        if slot is None:
            raise ValueError("Correction trial action slot is missing")
    return workflow.action_curves(action, slot)


def action_snapshot(obj, action):
    rows = []
    for curve in _curves(obj, action):
        points = []
        for point in curve.keyframe_points:
            values = (
                float(point.co.x), float(point.co.y),
                float(point.handle_left.x), float(point.handle_left.y),
                float(point.handle_right.x), float(point.handle_right.y),
                str(point.interpolation), str(point.easing),
            )
            if not all(math.isfinite(value) for value in values[:6]):
                raise ValueError("Correction trial encountered a nonfinite key")
            points.append(values)
        rows.append(dict(data_path=curve.data_path, array_index=int(curve.array_index), points=points))
    rows.sort(key=lambda row: (row["data_path"], row["array_index"]))
    return rows


def _point_map(snapshot):
    result = {}
    for curve in snapshot:
        identity = (curve["data_path"], curve["array_index"])
        result[identity] = {round(point[0], 6): tuple(point[1:]) for point in curve["points"]}
    return result


def snapshot_diff(before, after, priority_frames):
    left, right = _point_map(before), _point_map(after)
    added = removed = changed = priority_changed = 0
    changed_curves = set()
    priorities = {round(float(frame), 6) for frame in priority_frames}
    for curve in set(left) | set(right):
        a, b = left.get(curve, {}), right.get(curve, {})
        add = set(b) - set(a)
        remove = set(a) - set(b)
        common = set(a) & set(b)
        different = {frame for frame in common if a[frame] != b[frame]}
        if add or remove or different:
            changed_curves.add(curve)
        added += len(add)
        removed += len(remove)
        changed += len(different)
        priority_changed += len((add | remove | different) & priorities)
    return dict(
        changed_curves=len(changed_curves),
        added_keys=added,
        removed_keys=removed,
        changed_keys=changed,
        corrective_key_events=added + removed + changed,
        priority_key_events=priority_changed,
        priority_poses_preserved=priority_changed == 0,
    )


def _find_case(data, case_id):
    matches = [case for case in data.get("cases", ()) if case.get("id") == case_id]
    if len(matches) != 1:
        raise ValueError("Correction trial case is missing or duplicated")
    return matches[0]


def _armature():
    matches = [obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE" and hasattr(obj, "b4ml")]
    matches = [obj for obj in matches if getattr(obj.b4ml, "candidate_action", None)]
    if len(matches) != 1:
        raise ValueError(f"Expected one B4ML review armature, found {len(matches)}")
    return matches[0]


def configure(config):
    required = {"review_data", "case_id", "side", "reviewer_id", "output_directory", "mode"}
    if not isinstance(config, dict) or set(config) != required:
        raise ValueError("Correction trial configuration fields changed")
    data_path = Path(config["review_data"]).resolve()
    output = Path(config["output_directory"]).resolve()
    data = json.loads(data_path.read_text(encoding="utf-8-sig"))
    if data.get("schema") != "b4ml-procedural-vertical-slice-review-data-v2":
        raise ValueError("Correction trial requires the v13/v2 review packet")
    side = config["side"]
    if side not in {"A", "B"}:
        raise ValueError("Correction trial side must be A or B")
    reviewer = str(config["reviewer_id"]).strip()
    if not reviewer or len(reviewer) > 200:
        raise ValueError("A bounded reviewer ID or anonymous code is required")
    case = _find_case(data, config["case_id"])
    if config["mode"] not in {"HUMAN", "SYNTHETIC"}:
        raise ValueError("Correction trial mode must be HUMAN or SYNTHETIC")
    scene_path = Path(bpy.data.filepath).resolve()
    if not scene_path.is_file() or sha(scene_path) != case["source_blend_sha256"]:
        raise ValueError("Open review scene does not match the frozen case hash")
    if case["reveal"].get(side, {}).get("kind") not in {"pre_contact", "corrected"}:
        raise ValueError("Blind method assignment is invalid")
    output.mkdir(parents=True, exist_ok=True)
    _CONFIG.clear()
    _CONFIG.update(
        config=dict(config), data_path=data_path, data_sha256=sha(data_path),
        aggregate_sha256=data["aggregate_sha256"], case=case, side=side,
        reviewer_id=reviewer, output=output,
    )
    state = bpy.context.scene.b4ml_correction_trial
    state.case_label = f"{case['profile']} / {case['task']} / Candidate {side}"
    state.status = "READY"
    state.active_seconds = 0.0
    state.observed_edit_bursts = 0
    state.observed_frame_events = 0
    return _CONFIG


def _method_action(obj):
    kind = _CONFIG["case"]["reveal"][_CONFIG["side"]]["kind"]
    action = obj.b4ml.contact_input if kind == "pre_contact" else obj.b4ml.candidate_action
    if action is None:
        raise ValueError("Frozen review action is missing")
    return kind, action


def _accrue(session):
    now = time.monotonic()
    if not session["paused"]:
        session["active_seconds"] += max(0.0, now - session["last_clock"])
    session["last_clock"] = now


def _poll_session(session):
    _accrue(session)
    scene, obj, action = session["scene"], session["obj"], session["working"]
    if obj.name not in scene.objects or obj.animation_data is None or obj.animation_data.action != action:
        raise ValueError("Correction trial working action changed")
    if session["paused"]:
        return
    snapshot = action_snapshot(obj, action)
    digest = _json_hash(snapshot)
    if digest != session["last_snapshot_sha256"]:
        session["edit_bursts"] += 1
        session["events"].append(dict(kind="animation_edit_burst", active_seconds=session["active_seconds"]))
        session["last_snapshot_sha256"] = digest
    frame = (int(scene.frame_current), float(scene.frame_subframe))
    if frame != session["last_frame"]:
        session["frame_events"] += 1
        session["events"].append(dict(kind="frame_change", active_seconds=session["active_seconds"], frame=list(frame)))
        session["last_frame"] = frame
    state = scene.b4ml_correction_trial
    state.active_seconds = session["active_seconds"]
    state.observed_edit_bursts = session["edit_bursts"]
    state.observed_frame_events = session["frame_events"]


def _timer():
    global _TIMER_RUNNING
    live = False
    for key, session in tuple(_SESSIONS.items()):
        try:
            _poll_session(session)
            live = True
        except (ReferenceError, ValueError):
            _SESSIONS.pop(key, None)
    if live:
        return 0.25
    _TIMER_RUNNING = False
    return None


def _ensure_timer():
    global _TIMER_RUNNING
    if not _TIMER_RUNNING:
        bpy.app.timers.register(_timer, first_interval=0.25)
        _TIMER_RUNNING = True


def start_trial(scene=None):
    if not _CONFIG:
        raise ValueError("Load a correction-trial configuration first")
    scene = scene or bpy.context.scene
    key = scene.as_pointer()
    if key in _SESSIONS:
        raise ValueError("A correction trial is already active")
    obj = _armature()
    from b4artists_ml import workflow
    kind, source = _method_action(obj)
    source_snapshot = action_snapshot(obj, source)
    prior_action = obj.animation_data.action
    prior_slot = workflow._slot(obj.animation_data)
    working = source.copy()
    working.name = f"Blind correction {_CONFIG['side']} - {_CONFIG['case']['id']}"
    working.use_fake_user = True
    workflow.assign_action(obj, working, prior_slot)
    now = time.monotonic()
    session = dict(
        scene=scene, obj=obj, method_kind=kind, source=source,
        source_snapshot=source_snapshot, source_snapshot_sha256=_json_hash(source_snapshot),
        prior_action=prior_action, prior_slot=prior_slot, working=working,
        started_utc=datetime.now(timezone.utc).isoformat(), last_clock=now,
        active_seconds=0.0, paused=False, edit_bursts=0, frame_events=0,
        last_frame=(int(scene.frame_current), float(scene.frame_subframe)),
        last_snapshot_sha256=_json_hash(action_snapshot(obj, working)), events=[],
        control_interactions=1,
    )
    _SESSIONS[key] = session
    state = scene.b4ml_correction_trial
    state.status = "RUNNING"
    _ensure_timer()
    return session


def pause_trial(scene=None, paused=True):
    scene = scene or bpy.context.scene
    session = _SESSIONS.get(scene.as_pointer())
    if session is None:
        raise ValueError("No correction trial is active")
    _poll_session(session)
    session["paused"] = bool(paused)
    session["last_clock"] = time.monotonic()
    session["control_interactions"] += 1
    scene.b4ml_correction_trial.status = "PAUSED" if paused else "RUNNING"


def _report(session):
    _poll_session(session)
    final_snapshot = action_snapshot(session["obj"], session["working"])
    difference = snapshot_diff(
        session["source_snapshot"], final_snapshot, _CONFIG["case"]["priority_frames"]
    )
    state = session["scene"].b4ml_correction_trial
    failures = [field for field in FAILURE_FIELDS if getattr(state, "failure_" + field)]
    return dict(
        schema="b4ml-hands-on-correction-trial-v1",
        human_authored=_CONFIG["config"]["mode"] == "HUMAN",
        synthetic_smoke=_CONFIG["config"]["mode"] == "SYNTHETIC",
        reviewer_id=_CONFIG["reviewer_id"],
        case_id=_CONFIG["case"]["id"],
        profile=_CONFIG["case"]["profile"],
        task=_CONFIG["case"]["task"],
        blind_side=_CONFIG["side"],
        method_identity_hidden_during_trial=True,
        source_review_data_sha256=_CONFIG["data_sha256"],
        source_aggregate_sha256=_CONFIG["aggregate_sha256"],
        source_scene=_CONFIG["case"]["source_blend"],
        source_scene_sha256=_CONFIG["case"]["source_blend_sha256"],
        source_action_snapshot_sha256=session["source_snapshot_sha256"],
        corrected_action_snapshot_sha256=_json_hash(final_snapshot),
        started_utc=session["started_utc"],
        completed_utc=datetime.now(timezone.utc).isoformat(),
        active_work_seconds=session["active_seconds"],
        observed_edit_bursts=session["edit_bursts"],
        observed_frame_events=session["frame_events"],
        tracker_control_interactions=session["control_interactions"] + 1,
        observed_interaction_events=(
            session["edit_bursts"] + session["frame_events"] + session["control_interactions"] + 1
        ),
        action_difference=difference,
        production_acceptable=state.production_acceptable,
        visible_failure_tags=failures,
        notes=state.notes,
        event_log=session["events"],
        interaction_scope=(
            "Observed action-change bursts, frame changes and tracker controls. It does not claim to "
            "capture every mouse, keyboard or external application interaction."
        ),
        full_goal_complete=False,
    )


def finish_trial(scene=None):
    scene = scene or bpy.context.scene
    key = scene.as_pointer()
    session = _SESSIONS.get(key)
    if session is None:
        raise ValueError("No correction trial is active")
    report = _report(session)
    safe_case = report["case_id"].replace("/", "-")
    reviewer = hashlib.sha256(report["reviewer_id"].encode("utf-8")).hexdigest()[:12]
    path = _CONFIG["output"] / f"{safe_case}-{report['blind_side']}-{reviewer}.json"
    if path.exists():
        raise ValueError("Correction trial output already exists")
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)
    _SESSIONS.pop(key, None)
    scene.b4ml_correction_trial.status = "COMPLETE"
    return path, report


def cancel_trial(scene=None):
    scene = scene or bpy.context.scene
    session = _SESSIONS.pop(scene.as_pointer(), None)
    if session is None:
        return False
    from b4artists_ml import workflow
    workflow.assign_action(session["obj"], session["prior_action"], session["prior_slot"])
    working = session["working"]
    working.use_fake_user = False
    if working.users == 0:
        bpy.data.actions.remove(working)
    scene.b4ml_correction_trial.status = "CANCELLED"
    return True


class B4ML_PG_correction_trial(bpy.types.PropertyGroup):
    case_label: bpy.props.StringProperty(default="No trial configured")
    status: bpy.props.StringProperty(default="UNCONFIGURED")
    active_seconds: bpy.props.FloatProperty(default=0.0, precision=2)
    observed_edit_bursts: bpy.props.IntProperty(default=0)
    observed_frame_events: bpy.props.IntProperty(default=0)
    production_acceptable: bpy.props.EnumProperty(
        name="Production acceptable",
        items=(("UNRATED", "Unrated", ""), ("YES", "Yes", ""), ("NO", "No", "")),
        default="UNRATED",
    )
    notes: bpy.props.StringProperty(name="Notes", default="")
    failure_foot_slide: bpy.props.BoolProperty(name="Foot Slide", default=False)
    failure_penetration: bpy.props.BoolProperty(name="Penetration", default=False)
    failure_popping: bpy.props.BoolProperty(name="Popping", default=False)
    failure_stretch: bpy.props.BoolProperty(name="Stretch", default=False)
    failure_timing: bpy.props.BoolProperty(name="Timing", default=False)
    failure_balance: bpy.props.BoolProperty(name="Balance", default=False)
    failure_intent_loss: bpy.props.BoolProperty(name="Intent Loss", default=False)
    failure_other: bpy.props.BoolProperty(name="Other", default=False)


class B4ML_OT_correction_trial_start(bpy.types.Operator):
    bl_idname = "b4ml_review.correction_trial_start"
    bl_label = "Start Blind Correction"
    def execute(self, context):
        try:
            start_trial(context.scene)
        except ValueError as exc:
            self.report({"ERROR"}, str(exc)); return {"CANCELLED"}
        return {"FINISHED"}


class B4ML_OT_correction_trial_pause(bpy.types.Operator):
    bl_idname = "b4ml_review.correction_trial_pause"
    bl_label = "Pause or Resume"
    def execute(self, context):
        session = _SESSIONS.get(context.scene.as_pointer())
        if session is None:
            self.report({"ERROR"}, "No correction trial is active"); return {"CANCELLED"}
        pause_trial(context.scene, not session["paused"])
        return {"FINISHED"}


class B4ML_OT_correction_trial_finish(bpy.types.Operator):
    bl_idname = "b4ml_review.correction_trial_finish"
    bl_label = "Finish and Export"
    def execute(self, context):
        try:
            path, _ = finish_trial(context.scene)
        except ValueError as exc:
            self.report({"ERROR"}, str(exc)); return {"CANCELLED"}
        self.report({"INFO"}, "Correction trial exported: " + str(path))
        return {"FINISHED"}


class B4ML_OT_correction_trial_cancel(bpy.types.Operator):
    bl_idname = "b4ml_review.correction_trial_cancel"
    bl_label = "Cancel and Restore"
    def execute(self, context):
        cancel_trial(context.scene)
        return {"FINISHED"}


class B4ML_PT_correction_trial(bpy.types.Panel):
    bl_label = "B4ML Hands-on Trial"
    bl_idname = "B4ML_PT_correction_trial"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "B4ML Study"
    def draw(self, context):
        layout = self.layout
        state = context.scene.b4ml_correction_trial
        layout.label(text=state.case_label)
        layout.label(text="Status: " + state.status)
        layout.label(text=f"Active time: {state.active_seconds:.2f} s")
        row = layout.row(align=True)
        row.operator("b4ml_review.correction_trial_start")
        row.operator("b4ml_review.correction_trial_pause", text="Pause / Resume")
        layout.prop(state, "production_acceptable")
        box = layout.box(); box.label(text="Visible failures")
        for field in FAILURE_FIELDS:
            box.prop(state, "failure_" + field)
        layout.prop(state, "notes")
        layout.label(text=f"Edit bursts: {state.observed_edit_bursts}")
        layout.label(text=f"Frame events: {state.observed_frame_events}")
        row = layout.row(align=True)
        row.operator("b4ml_review.correction_trial_finish")
        row.operator("b4ml_review.correction_trial_cancel")


CLASSES = (
    B4ML_PG_correction_trial,
    B4ML_OT_correction_trial_start,
    B4ML_OT_correction_trial_pause,
    B4ML_OT_correction_trial_finish,
    B4ML_OT_correction_trial_cancel,
    B4ML_PT_correction_trial,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.b4ml_correction_trial = bpy.props.PointerProperty(type=B4ML_PG_correction_trial)


def unregister():
    for scene in tuple(bpy.data.scenes):
        cancel_trial(scene)
    if hasattr(bpy.types.Scene, "b4ml_correction_trial"):
        del bpy.types.Scene.b4ml_correction_trial
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


def main():
    sys.path[:0] = [str(ROOT), str(ROOT / "training/b4artists_ml")]
    import b4artists_ml
    if not hasattr(bpy.types.Object, "b4ml"):
        b4artists_ml.register()
    register()
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        if len(args) != 1:
            raise ValueError("Expected one correction-trial configuration JSON path")
        configure(json.loads(Path(args[0]).read_text(encoding="utf-8-sig")))


if __name__ == "__main__":
    main()
