"""Foreground Bforartists journey for procedural quadruped gait-phase review."""
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
REPORT = ROOT / "docs/b4artists_ml/quadruped-gait-phase-ui-v1.json"
SCREENSHOT = ROOT / "training/b4artists_ml/cache/quadruped-gait-phase-ui-v1.png"
LOG = ROOT / "training/b4artists_ml/cache/quadruped-gait-phase-ui-v1.log"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_host():
    import addon_utils
    import bpy
    sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
    import b4artists_ml
    from b4artists_ml import contact_math as cm
    from b4artists_ml import quadruped_contacts as qc
    from b4artists_ml import quadruped_gait as gait
    from test_b4artists_ml_quadruped_contacts import _candidate
    from test_b4artists_ml_quadruped_gait_phase_v1 import _install_pattern

    addon_utils.enable("rigify", default_set=True, persistent=False)
    b4artists_ml.register()
    scene, obj, _, _, candidate, _, _ = _candidate("cat")
    _install_pattern(obj)
    scene.frame_set(1)
    state = {"phase": "dismiss", "started": time.monotonic(), "events": []}

    def finish(report):
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("B4ML_GAIT_UI: " + json.dumps(report), flush=True)
        bpy.ops.wm.quit_blender()
        return None

    def tick():
        try:
            if time.monotonic() - state["started"] > 120:
                raise AssertionError("Gait-phase UI journey timed out")
            window = bpy.context.window_manager.windows[0]
            area = next(item for item in window.screen.areas if item.type == "VIEW_3D")
            region = next(item for item in area.regions if item.type == "WINDOW")
            ui_region = next(item for item in area.regions if item.type == "UI")
            area.spaces.active.show_region_ui = True
            if hasattr(ui_region, "active_panel_category"):
                ui_region.active_panel_category = "B4Artists ML"
            window.view_layer.objects.active = obj
            obj.select_set(True)
            with bpy.context.temp_override(window=window, area=area, region=region):
                if state["phase"] == "dismiss":
                    window.event_simulate(type="ESC", value="PRESS")
                    obj.b4ml.show_quadruped_contacts = True
                    state["phase"] = "analyze"
                elif state["phase"] == "analyze":
                    before_action = gait._action_digest(obj, candidate)
                    before_contacts = qc._signature(obj)
                    assert bpy.ops.b4ml.quadruped_gait(operation="ANALYZE") == {"FINISHED"}
                    report = gait.report(obj)
                    assert report["phase_count"] == 4
                    assert report["phases"][0]["phase"] == "DIAGONAL_SUPPORT"
                    assert gait._action_digest(obj, candidate) == before_action
                    assert qc._signature(obj) == before_contacts
                    state.update(phase="navigate", before_action=before_action,
                                 before_contacts=before_contacts)
                    state["events"].append("Analyze Gait Phases produced four read-only support phases")
                elif state["phase"] == "navigate":
                    assert bpy.ops.b4ml.quadruped_gait(operation="NEXT") == {"FINISHED"}
                    phase = gait.current(obj)
                    frame = scene.frame_current + scene.frame_subframe
                    active = [limb for limb in qc.LIMBS
                              if any(row["limb"] == limb and cm.weight(row, frame) > 0
                                     for row in qc.rows(obj))]
                    assert phase["phase"] == "FLIGHT" and active == phase["support_limbs"] == []
                    assert abs(frame - 5.625) < 1e-8
                    assert gait._action_digest(obj, candidate) == state["before_action"]
                    assert qc._signature(obj) == state["before_contacts"]
                    state["events"].append("Next Phase moved to the fractional interior sample with matching contact weights")
                    obj.b4ml.contact_index = 99
                    for _ in range(16):
                        window.event_simulate(type="WHEELDOWNMOUSE", value="PRESS",
                                              x=ui_region.x + ui_region.width // 2,
                                              y=ui_region.y + ui_region.height // 2)
                    state["phase"] = "capture"
                elif state["phase"] == "capture":
                    SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
                    bpy.ops.screen.screenshot(filepath=str(SCREENSHOT))
                    report = {
                        "schema": 1,
                        "passed": True,
                        "host": bpy.app.version_string,
                        "events": state["events"],
                        "displayed_phase": "FLIGHT",
                        "displayed_frame": 5.625,
                        "source_animation_unchanged": True,
                        "accepted_contacts_unchanged": True,
                        "screenshot": str(SCREENSHOT.relative_to(ROOT)).replace("/", "\\"),
                        "screenshot_sha256": sha(SCREENSHOT),
                        "scope": ("Automated foreground panel and operator journey. "
                                  "Independent animator visual assessment remains unverified."),
                    }
                    return finish(report)
        except Exception:
            return finish({"schema": 1, "passed": False, "phase": state["phase"],
                           "events": state["events"], "error": traceback.format_exc()})
        return 0.15

    bpy.app.timers.register(tick, first_interval=0.5)


def launch():
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    started = time.perf_counter()
    with LOG.open("w", encoding="utf-8") as stream:
        process = subprocess.run(
            [os.environ.get("B4ML_BFORARTISTS", "X:/5.1.0/bforartists.exe"),
             "--factory-startup", "--no-window-focus", "--enable-event-simulate",
             "--python", str(HERE), "--", "--host"],
            cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, startupinfo=startup,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="4"),
            timeout=180)
    value = json.loads(REPORT.read_text(encoding="utf-8"))
    if not value.get("passed"):
        raise RuntimeError(value)
    print(json.dumps({"passed": True, "process_exit_code": process.returncode,
                      "assertions_completed_before_shutdown": True,
                      "seconds": time.perf_counter() - started,
                      "report": str(REPORT), "report_sha256": sha(REPORT)}, indent=2))


if __name__ == "__main__":
    if "--host" in sys.argv:
        run_host()
    else:
        launch()
