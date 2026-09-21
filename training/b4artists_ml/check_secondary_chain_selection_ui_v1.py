"""Foreground Bforartists direct-chain selection, reversible swap, and solver handoff."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
REPORT = ROOT / "docs/b4artists_ml/secondary-chain-selection-ui-v1.json"
SCREENSHOT = ROOT / "training/b4artists_ml/cache/secondary-chain-selection-ui-v1.png"
LOG = ROOT / "training/b4artists_ml/cache/secondary-chain-selection-ui-v1.log"
BLEND = ROOT / "training/b4artists_ml/cache/secondary-chain-selection-ui-v1.blend"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_paths():
    paths = list(sorted((ROOT / "b4artists_ml").glob("*.py")))
    paths.extend((
        HERE,
        ROOT / "tests/test_b4artists_ml_secondary_chain_selection_v1.py",
        ROOT / "tests/test_b4artists_ml_secondary_motion.py",
        ROOT / "tests/test_b4artists_ml_contacts.py",
        ROOT / "tests/test_b4artists_ml_posing.py",
    ))
    return tuple(dict.fromkeys(paths))


def input_hashes():
    return {
        str(path.relative_to(ROOT)).replace("\\", "/"): sha(path)
        for path in input_paths()
    }


def run_host():
    import bpy
    sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
    import b4artists_ml
    from b4artists_ml import flight, secondary_motion as secondary, workflow as workflow
    from test_b4artists_ml_secondary_motion import (
        animate_rotation_group,
        fixture,
        rotation_chain,
    )

    frozen_inputs = json.loads(os.environ["B4ML_FROZEN_INPUTS"])
    if input_hashes() != frozen_inputs:
        raise RuntimeError("Foreground inputs changed before host initialization")

    def action_digest(action):
        rows = []
        slots = tuple(action.slots) if hasattr(action, "slots") and action.slots else (None,)
        for slot in slots:
            for curve in workflow.action_curves(action, slot):
                rows.append({
                    "slot": getattr(slot, "identifier", None),
                    "path": curve.data_path,
                    "index": curve.array_index,
                    "lock": bool(curve.lock),
                    "mute": bool(curve.mute),
                    "extrapolation": curve.extrapolation,
                    "auto_smoothing": curve.auto_smoothing,
                    "modifiers": [flight._modifier_signature(item)
                                  for item in curve.modifiers],
                    "keys": [
                        [list(key.co), list(key.handle_left), list(key.handle_right),
                         key.handle_left_type, key.handle_right_type,
                         key.interpolation, key.easing, key.amplitude,
                         key.back, key.period, key.type]
                        for key in curve.keyframe_points
                    ],
                    "samples": [list(point.co) for point in curve.sampled_points],
                })
        payload = json.dumps(rows, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    b4artists_ml.register()
    bpy.context.preferences.edit.use_global_undo = True
    obj, source, _, _, _, _ = fixture("rigify_default")
    chain = rotation_chain(obj)
    for index, definition in enumerate(chain):
        animate_rotation_group(obj.b4ml.candidate_action, obj, definition,
                               .45 / (index + 1))
    parent, child = chain[0][0], chain[1][0]
    for bone in obj.pose.bones:
        secondary._set_selected(bone, bone.name == parent.name)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if obj.mode != "POSE":
        bpy.ops.object.mode_set(mode="POSE")
    obj.data.bones.active = child.bone
    obj.b4ml.show_secondary = True
    obj.b4ml.secondary_chain = True
    obj.b4ml.secondary_space = "LOCAL"
    obj.b4ml.secondary_rotation = True
    obj.b4ml.secondary_location = False
    obj.b4ml.secondary_chain_direction = "PARENTS"
    obj.b4ml.secondary_chain_length = 2
    object_name = obj.name
    source_name = source.name
    source_digest = action_digest(source)
    input_name = obj.b4ml.candidate_action.name
    parent_name, child_name = parent.name, child.name
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    bpy.ops.wm.open_mainfile(filepath=str(BLEND), use_scripts=False)
    obj = bpy.data.objects[object_name]
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if obj.mode != "POSE":
        bpy.ops.object.mode_set(mode="POSE")
    parent, child = obj.pose.bones[parent_name], obj.pose.bones[child_name]
    obj.data.bones.active = child.bone
    before_selection = secondary.selected_controls(obj)
    before_token = flight._curve_token(obj, obj.b4ml.candidate_action)
    before_pose = workflow.raw_pose(obj)
    before_anchors = tuple((float(item.frame), item.payload) for item in obj.b4ml.anchors)
    assert action_digest(bpy.data.actions[source_name]) == source_digest
    names = [parent.name, child.name]
    state = {"phase": "dismiss", "started": time.monotonic(), "events": []}

    def finish(value):
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        print("B4ML_SECONDARY_CHAIN_SELECTION_UI: " + json.dumps(value), flush=True)
        bpy.ops.wm.quit_blender()
        return None

    def current():
        rig = bpy.data.objects[object_name]
        bpy.context.view_layer.objects.active = rig
        rig.select_set(True)
        if rig.mode != "POSE":
            bpy.ops.object.mode_set(mode="POSE")
        return rig

    def verify_input(rig):
        assert rig.b4ml.candidate_action.name == input_name
        assert rig.animation_data.action.name == input_name
        assert flight._curve_token(rig, rig.b4ml.candidate_action) == before_token
        assert workflow.raw_pose(rig) == before_pose
        assert tuple((float(item.frame), item.payload)
                     for item in rig.b4ml.anchors) == before_anchors
        assert action_digest(bpy.data.actions[source_name]) == source_digest

    def tick():
        try:
            if time.monotonic() - state["started"] > 150:
                raise AssertionError("Direct-chain selection UI journey timed out")
            window = bpy.context.window_manager.windows[0]
            area = next(value for value in window.screen.areas if value.type == "VIEW_3D")
            region = next(value for value in area.regions if value.type == "WINDOW")
            ui_region = next(value for value in area.regions if value.type == "UI")
            area.spaces.active.show_region_ui = True
            if hasattr(ui_region, "active_panel_category"):
                ui_region.active_panel_category = "B4Artists ML"
            rig = current()
            rig.data.bones.active = rig.data.bones[child_name]
            with bpy.context.temp_override(window=window, area=area, region=region):
                if state["phase"] == "dismiss":
                    window.event_simulate(type="ESC", value="PRESS")
                    state["phase"] = "select"
                elif state["phase"] == "select":
                    assert bpy.ops.ed.undo_push(
                        message="B4ML direct-chain foreground baseline") == {"FINISHED"}
                    assert bpy.ops.b4ml.secondary_select_chain(
                        direction="PARENTS", max_controls=2) == {"FINISHED"}
                    rig = current()
                    verify_input(rig)
                    assert set(secondary.selected_controls(rig)) == set(names)
                    assert rig.data.bones.active.name == child.name
                    assert rig.b4ml.secondary_chain
                    state["events"].append(
                        "Select Direct Chain chose the eligible parent-child controls")
                    SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
                    for _ in range(12):
                        window.event_simulate(type="WHEELDOWNMOUSE", value="PRESS",
                                              x=ui_region.x + ui_region.width // 2,
                                              y=ui_region.y + ui_region.height // 2)
                    bpy.ops.screen.screenshot(filepath=str(SCREENSHOT))
                    state["phase"] = "undo"
                elif state["phase"] == "undo":
                    window.event_simulate(type="Z", value="PRESS", ctrl=True)
                    state["phase"] = "undo_check"
                elif state["phase"] == "undo_check":
                    rig = current()
                    verify_input(rig)
                    assert not rig.b4ml.secondary_selection_swap
                    state["events"].append(
                        "Native Undo cleared the volatile pointer-bound swap record")
                    state["phase"] = "redo"
                elif state["phase"] == "redo":
                    window.event_simulate(type="Z", value="PRESS", ctrl=True, shift=True)
                    state["phase"] = "redo_check"
                elif state["phase"] == "redo_check":
                    rig = current()
                    verify_input(rig)
                    assert not rig.b4ml.secondary_selection_swap
                    state["events"].append(
                        "Native Redo cleared the volatile pointer-bound swap record")
                    for bone in rig.pose.bones:
                        secondary._set_selected(bone, bone.name == parent_name)
                    rig.data.bones.active = rig.data.bones[child_name]
                    rig.b4ml.secondary_chain = True
                    assert bpy.ops.b4ml.secondary_select_chain(
                        direction="PARENTS", max_controls=2) == {"FINISHED"}
                    rig = current()
                    assert set(secondary.selected_controls(rig)) == set(names)
                    state["events"].append(
                        "Select Direct Chain re-established a session-local swap")
                    state["phase"] = "restore"
                elif state["phase"] == "restore":
                    assert bpy.ops.b4ml.secondary_selection_swap() == {"FINISHED"}
                    rig = current()
                    verify_input(rig)
                    assert secondary.selected_controls(rig) == before_selection
                    state["events"].append(
                        "Swap Previous Selection restored the exact prior selection")
                    state["phase"] = "reapply"
                elif state["phase"] == "reapply":
                    assert bpy.ops.b4ml.secondary_selection_swap() == {"FINISHED"}
                    rig = current()
                    verify_input(rig)
                    assert set(secondary.selected_controls(rig)) == set(names)
                    state["events"].append(
                        "A second swap reapplied the direct chain selection")
                    assert bpy.ops.b4ml.secondary_solve() == {"FINISHED"}
                    rig = current()
                    metrics = json.loads(rig.b4ml.secondary_metrics)
                    assert metrics["backend"] == "implicit_selected_control_chain_v1"
                    assert metrics["chain_controls"] == names
                    assert metrics["editable_linear_keys"]
                    state["events"].append(
                        "The selected chain entered the existing editable secondary solver")
                    assert bpy.ops.b4ml.secondary(operation="RESET") == {"FINISHED"}
                    rig = current()
                    assert rig.b4ml.candidate_action.name == input_name
                    assert rig.animation_data.action.name == input_name
                    source_digest_after = action_digest(bpy.data.actions[source_name])
                    assert source_digest_after == source_digest
                    assert input_hashes() == frozen_inputs
                    return finish({
                        "schema": 2,
                        "passed": True,
                        "host": bpy.app.version_string,
                        "events": state["events"],
                        "direction": "PARENTS",
                        "maximum_controls": 2,
                        "selected_controls": names,
                        "source_action": source_name,
                        "source_action_sha256_before": source_digest,
                        "source_action_sha256_after": source_digest_after,
                        "source_action_unchanged": source_digest_after == source_digest,
                        "input_candidate_unchanged_by_selection": True,
                        "pose_unchanged_by_selection": True,
                        "anchors_unchanged_by_selection": True,
                        "explicit_selection_restore_verified": True,
                        "native_pose_selection_redo_claimed": False,
                        "solver_handoff_verified": True,
                        "semantic_inference": False,
                        "learned_motion": False,
                        "cascadeur_parity": False,
                        "independent_animator_review": False,
                        "screenshot": str(SCREENSHOT.relative_to(ROOT)).replace("/", "\\"),
                        "screenshot_sha256": sha(SCREENSHOT),
                        "input_sha256": frozen_inputs,
                        "runtime_sha256": {key: value for key, value in frozen_inputs.items()
                                           if key.startswith("b4artists_ml/")},
                        "test_sha256": sha(
                            ROOT / "tests/test_b4artists_ml_secondary_chain_selection_v1.py"),
                        "scope": ("Automated foreground panel/operator, explicit reversible selection "
                                  "swap, and existing solver handoff. Visual quality and independent "
                                  "animator usability remain unverified."),
                    })
        except Exception:
            return finish({"schema": 1, "passed": False, "phase": state["phase"],
                           "events": state["events"], "error": traceback.format_exc()})
        return 0.12

    bpy.app.timers.register(tick, first_interval=0.5)


def launch():
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    frozen_inputs = input_hashes()
    REPORT.unlink(missing_ok=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    with LOG.open("w", encoding="utf-8") as stream:
        process = subprocess.Popen(
            [os.environ.get("B4ML_BFORARTISTS", "X:/5.1.0/bforartists.exe"),
             "--factory-startup", "--no-window-focus", "--enable-event-simulate",
             "--python", str(HERE), "--", "--host"],
            cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, startupinfo=startup,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                     OPENBLAS_NUM_THREADS="4",
                     B4ML_FROZEN_INPUTS=json.dumps(frozen_inputs,
                                                   sort_keys=True,
                                                   separators=(",", ":"))))
        deadline = time.monotonic() + 180
        while not REPORT.is_file() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.2)
        if not REPORT.is_file():
            if process.poll() is None:
                process.terminate()
            raise RuntimeError("Foreground direct-chain selection produced no report")
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=10)
    value = json.loads(REPORT.read_text(encoding="utf-8"))
    if not value.get("passed"):
        raise RuntimeError(value)
    if input_hashes() != frozen_inputs:
        raise RuntimeError("Foreground inputs changed during host execution")
    if value.get("input_sha256") != frozen_inputs:
        raise RuntimeError("Foreground report is not bound to frozen launcher inputs")
    print(json.dumps({
        "passed": True,
        "process_exit_code": process.returncode,
        "assertions_completed_before_shutdown": True,
        "seconds": time.perf_counter() - started,
        "report": str(REPORT),
        "report_sha256": sha(REPORT),
    }, indent=2))


if __name__ == "__main__":
    if "--host" in sys.argv:
        run_host()
    else:
        launch()
