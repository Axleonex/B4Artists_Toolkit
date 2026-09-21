"""Real-window coupled rotation-chain operator and lifecycle journey."""

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
TAG = os.environ.get("B4ML_SECONDARY_UI_TAG", "secondary-chain-source-v1")


def run():
    import bpy
    import numpy as np

    sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]
    import b4artists_ml
    from b4artists_ml import secondary_motion as secondary, workflow as w
    from test_b4artists_ml_secondary_motion import (
        animate_rotation_group,
        fixture,
        rotation_chain,
    )

    b4artists_ml.register()
    obj, source, _, _, _, _ = fixture("rigify_default")
    scene = bpy.context.scene
    original = obj.b4ml.candidate_action
    chain = rotation_chain(obj)
    for index, definition in enumerate(chain):
        animate_rotation_group(original, obj, definition, .45 / (index + 1))
    for bone in obj.pose.bones:
        if hasattr(bone, "select"):
            bone.select = False
        else:
            bone.bone.select = False
    for bone, _, _ in chain:
        if hasattr(bone, "select"):
            bone.select = True
        else:
            bone.bone.select = True
    priority = obj.b4ml.anchors.add()
    priority.frame = 6.0
    priority.payload = obj.b4ml.anchors[0].payload
    obj.b4ml.secondary_space = "LOCAL"
    obj.b4ml.secondary_rotation = True
    obj.b4ml.secondary_location = False
    obj.b4ml.secondary_chain = True
    obj.b4ml.secondary_chain_propagation = .75
    scene.frame_set(6)
    source_lengths = []
    for frame in range(1, 12):
        scene.frame_set(frame)
        source_lengths.append((chain[1][0].head - chain[0][0].head).length)
    scene.frame_set(6)
    state = dict(
        name=obj.name,
        source=source.name,
        input=original.name,
        controls=[item[0].name for item in chain],
        phase="dismiss",
        started=time.monotonic(),
        events=[],
    )
    steps = []
    native_step = secondary.step

    def timed(value):
        began = time.perf_counter()
        before = value.b4ml.secondary_progress
        try:
            return native_step(value)
        finally:
            steps.append(dict(
                ms=(time.perf_counter() - began) * 1000,
                before=before,
                after=value.b4ml.secondary_progress,
            ))

    secondary.step = timed

    def tick():
        try:
            if time.monotonic() - state["started"] > 180:
                raise AssertionError("Coupled secondary-motion UI workflow timeout")
            win = bpy.context.window_manager.windows[0]
            area = next(area for area in win.screen.areas if area.type == "VIEW_3D")
            region = next(region for region in area.regions if region.type == "WINDOW")
            area.spaces.active.show_region_ui = True
            for ui_region in area.regions:
                if ui_region.type == "UI" and hasattr(ui_region, "active_panel_category"):
                    ui_region.active_panel_category = "B4Artists ML"
            obj = bpy.data.objects[state["name"]]
            win.view_layer.objects.active = obj
            obj.select_set(True)
            with bpy.context.temp_override(window=win, area=area, region=region):
                phase = state["phase"]
                if phase == "dismiss":
                    win.event_simulate(type="ESC", value="PRESS")
                    bpy.ops.view3d.view_axis(type="FRONT")
                    bpy.ops.view3d.view_selected(use_all_regions=False)
                    obj.b4ml.show_secondary = True
                    state["phase"] = "start_cancel"
                elif phase == "start_cancel":
                    bpy.ops.ed.undo_push(message="Coupled secondary input ready")
                    assert bpy.ops.b4ml.secondary_solve("INVOKE_DEFAULT") == {"RUNNING_MODAL"}
                    state["phase"] = "escape"
                elif phase == "escape":
                    if not steps:
                        return .02
                    win.event_simulate(type="ESC", value="PRESS")
                    state["phase"] = "cancelled"
                elif phase == "cancelled":
                    if obj.b4ml.secondary_running:
                        return .02
                    assert obj.b4ml.candidate_action == original
                    assert obj.animation_data.action == original
                    state["events"].append("Escape cancelled chain generation and retained input")
                    state["phase"] = "cancel_cleanup"
                    return .12
                elif phase == "cancel_cleanup":
                    state["phase"] = "restart"
                    return .12
                elif phase == "restart":
                    bpy.ops.ed.undo_push(message="Coupled secondary retained input")
                    assert bpy.ops.b4ml.secondary_solve("INVOKE_DEFAULT") == {"RUNNING_MODAL"}
                    state["phase"] = "completed"
                elif phase == "completed":
                    if obj.b4ml.secondary_running:
                        return .02
                    output = obj.b4ml.candidate_action
                    if output == original or obj.b4ml.secondary_input != original:
                        raise AssertionError("Chain modal ended without an output")
                    metrics = json.loads(obj.b4ml.secondary_metrics)
                    assert metrics["backend"] == "implicit_selected_control_chain_v1"
                    assert metrics["chain"] and metrics["chain_links"] == 1
                    assert metrics["chain_controls"] == state["controls"]
                    assert metrics["priority_poses_preserved"] and metrics["editable_linear_keys"]
                    assert metrics["max_rotation_correction_radians"] > .01
                    maximum_length_error = 0.0
                    for frame, expected in zip(range(1, 12), source_lengths):
                        scene.frame_set(frame)
                        actual = (chain[1][0].head - chain[0][0].head).length
                        maximum_length_error = max(maximum_length_error, abs(actual - expected))
                    assert maximum_length_error <= 1e-6
                    scene.frame_set(6)
                    state["metrics"] = metrics
                    state["maximum_link_length_error"] = maximum_length_error
                    state["output"] = output.name
                    state["events"].append("Coupled local rotations completed as editable candidate curves")
                    screenshot = ROOT / f"training/b4artists_ml/cache/secondary-ui-{TAG}.png"
                    bpy.ops.screen.screenshot(filepath=str(screenshot))
                    state["screenshot"] = str(screenshot.relative_to(ROOT))
                    win.event_simulate(type="MOUSEMOVE", value="NOTHING",
                                       x=region.x + 24, y=region.y + 24)
                    state["phase"] = "completion_cleanup"
                    return .12
                elif phase == "completion_cleanup":
                    assert bpy.ops.ed.undo() == {"FINISHED"}
                    state["phase"] = "undo"
                elif phase == "undo":
                    assert obj.b4ml.candidate_action.name == state["input"]
                    assert bpy.ops.ed.redo() == {"FINISHED"}
                    state["phase"] = "redo"
                elif phase == "redo":
                    assert obj.b4ml.candidate_action.name == state["output"]
                    state["events"].append("Undo and Redo restored the chain candidate")
                    assert bpy.ops.b4ml.secondary(operation="RESET") == {"FINISHED"}
                    assert obj.b4ml.candidate_action.name == state["input"]
                    state["events"].append("Restore Input returned to the retained candidate")
                    assert bpy.ops.b4ml.secondary_solve() == {"FINISHED"}
                    assert bpy.ops.b4ml.action(operation="KEEP") == {"FINISHED"}
                    assert bpy.ops.b4ml.action(operation="RESTORE_SOURCE") == {"FINISHED"}
                    assert obj.animation_data.action.name == state["source"]
                    state["events"].append("Keep and Restore Source preserved output and restored source")
                    runtime = {
                        "b4artists_ml/" + path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                        for path in Path(b4artists_ml.__file__).parent.glob("*.py")
                    }
                    durations = [row["ms"] for row in steps]
                    report = dict(
                        runtime_sha256=runtime,
                        passed=True,
                        events=state["events"],
                        module_root=str(Path(b4artists_ml.__file__).resolve().parent),
                        metrics=state["metrics"],
                        maximum_link_length_error=state["maximum_link_length_error"],
                        screenshot=state["screenshot"],
                        step_count=len(steps),
                        step_p95_ms=float(np.percentile(durations, 95)),
                        step_max_ms=max(durations),
                        slowest_steps=sorted(steps, key=lambda row: row["ms"], reverse=True)[:5],
                        elapsed_seconds=time.monotonic() - state["started"],
                        scope="Automated real-window chain operators and events; independent animator usability and visual quality remain unverified.",
                    )
                    (ROOT / f"docs/b4artists_ml/secondary-ui-{TAG}.json").write_text(
                        json.dumps(report, indent=2) + "\n", encoding="utf-8")
                    print(json.dumps(report), flush=True)
                    bpy.ops.wm.quit_blender()
                    return None
        except Exception:
            report = dict(passed=False, phase=state["phase"], events=state["events"],
                          error=traceback.format_exc())
            (ROOT / f"docs/b4artists_ml/secondary-ui-{TAG}.json").write_text(
                json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(report), flush=True)
            bpy.ops.wm.quit_blender()
            return None
        return .03

    bpy.app.timers.register(tick, first_interval=.5)


if __name__ == "__main__":
    if "--host" in sys.argv:
        run()
    else:
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0
        began = time.perf_counter()
        log_path = ROOT / f"training/b4artists_ml/cache/secondary-ui-{TAG}.log"
        with log_path.open("w", encoding="utf-8") as log:
            process = subprocess.run(
                ["X:/5.1.0/bforartists.exe", "--factory-startup", "--no-window-focus",
                 "--enable-event-simulate", "--python", str(HERE), "--", "--host"],
                stdout=log, stderr=subprocess.STDOUT, startupinfo=startup,
                env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="4",
                         B4ML_PACKAGE=os.environ.get("B4ML_PACKAGE", str(ROOT))),
                timeout=240,
            )
        report = dict(exit_code=process.returncode,
                      seconds=time.perf_counter() - began,
                      log=str(log_path.relative_to(ROOT)))
        (ROOT / f"training/b4artists_ml/results/secondary-ui-process-{TAG}.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report), flush=True)
