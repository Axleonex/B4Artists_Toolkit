"""Reproduce the Rigify-default procedural contact proxy decision."""

from pathlib import Path
import json
import sys
import time
import traceback

import bpy


ROOT = Path(__file__).resolve().parents[2]
BLEND = ROOT / "training" / "b4artists_ml" / "results" / "procedural-vertical-slice-v11" / "rigify_default" / "run" / "rigify_default-run.blend"


def main():
    sys.path.insert(0, str(ROOT))
    import b4artists_ml

    b4artists_ml.register()
    bpy.ops.wm.open_mainfile(filepath=str(BLEND), use_scripts=False)
    from b4artists_ml import contacts

    obj = next(obj for obj in bpy.data.objects if obj.type == "ARMATURE" and getattr(obj, "b4ml", None) and obj.b4ml.candidate_action)
    scene = next(scene for scene in bpy.data.scenes if obj.name in scene.objects)
    started = time.perf_counter()
    result = {
        "schema": 1,
        "blend": BLEND.relative_to(ROOT).as_posix(),
        "bones": len(obj.pose.bones),
        "candidate": obj.b4ml.candidate_action.name,
        "contact_input": obj.b4ml.contact_input.name if obj.b4ml.contact_input else None,
        "contact_output": obj.b4ml.contact_output.name if obj.b4ml.contact_output else None,
    }
    iterator = contacts._proxy_correction_steps(obj, scene)
    phases = []
    try:
        while True:
            try:
                info = next(iterator)
                phases.append(info["phase"])
            except StopIteration as stop:
                result.update(outcome="success", report=stop.value)
                break
    except BaseException as exc:
        result.update(outcome="error", error_type=type(exc).__name__, error=str(exc), traceback=traceback.format_exc())
    result["phases"] = phases
    result["seconds"] = time.perf_counter() - started
    print("B4ML_PROXY_DIAGNOSTIC=" + json.dumps(result, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
