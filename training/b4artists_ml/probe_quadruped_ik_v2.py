"""Measure Rigify quadruped IK continuity and target response in Bforartists."""

from pathlib import Path
import importlib
import json
import os
import subprocess
import sys
import time
import traceback


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
OUT = ROOT / "training/b4artists_ml/results/rigify-quadruped-ik-probe-v4"
HOST = Path("X:/5.1.0/bforartists.exe")
PROFILES = ("cat", "horse", "wolf")

SCHEMAS = {
    "cat": {
        "fore": ("upper_arm_parent", "hand_ik", "ORG-f_toe"),
        "hind": ("thigh_parent", "foot_ik", "ORG-r_toe"),
    },
    "horse": {
        "fore": ("upper_arm_parent", "forefoot_ik", "ORG-f_toe"),
        "hind": ("thigh_parent", "hind_foot_ik", "ORG-r_toe"),
    },
    "wolf": {
        "fore": ("front_thigh_parent", "front_foot_ik", "ORG-front_toe"),
        "hind": ("thigh_parent", "foot_ik", "ORG-toe"),
    },
}


def _world(obj, point):
    return obj.matrix_world @ point


def _host(profile):
    import addon_utils
    import bpy
    from mathutils import Vector

    report = {"profile": profile, "complete": False, "limbs": []}
    try:
        addon_utils.enable("rigify", default_set=True, persistent=False)
        module = importlib.import_module("rigify.metarigs.Animals." + profile)
        data = bpy.data.armatures.new(profile + " metarig")
        meta = bpy.data.objects.new(profile + " metarig", data)
        bpy.context.scene.collection.objects.link(meta)
        bpy.context.view_layer.objects.active = meta
        meta.select_set(True)
        module.create(meta)
        if meta.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.pose.rigify_generate()
        obj = bpy.context.object
        obj.matrix_world.translation = Vector((0.31, -0.22, 0.47))
        bpy.context.view_layer.update()
        delta = Vector((0.037, -0.021, 0.028))
        paw_joints = [obj.pose.bones[SCHEMAS[profile][kind][2] + "." + side]
                      for kind in ("fore", "hind") for side in ("L", "R")]
        paws_before = [_world(obj, joint.tail.copy()) for joint in paw_joints]
        torso = obj.pose.bones["torso"]
        torso_before = _world(obj, torso.matrix.translation.copy())
        torso_matrix = torso.matrix.copy()
        torso_matrix.translation += obj.matrix_world.inverted().to_3x3() @ delta
        torso.matrix = torso_matrix
        bpy.context.view_layer.update()
        torso_after = _world(obj, torso.matrix.translation.copy())
        paws_after = [_world(obj, joint.tail.copy()) for joint in paw_joints]
        report["body_translation"] = {
            "requested_delta": list(delta),
            "observed_delta": list(torso_after - torso_before),
            "delta_error": ((torso_after - torso_before) - delta).length,
            "maximum_paw_drift": max((after - before).length for before, after in zip(paws_before, paws_after)),
        }
        for kind, (parent_stem, ik_stem, joint_stem) in SCHEMAS[profile].items():
            for side in ("L", "R"):
                parent = obj.pose.bones[parent_stem + "." + side]
                ik = obj.pose.bones[ik_stem + "." + side]
                joint = obj.pose.bones[joint_stem + "." + side]
                before = _world(obj, joint.tail.copy())
                mode_before = float(parent["IK_FK"])
                parent["IK_FK"] = 0.0
                bpy.context.view_layer.update()
                after_switch = _world(obj, joint.tail.copy())
                switch_error = (after_switch - before).length
                matrix = ik.matrix.copy()
                matrix.translation += obj.matrix_world.inverted().to_3x3() @ delta
                ik.matrix = matrix
                bpy.context.view_layer.update()
                after_move = _world(obj, joint.tail.copy())
                response = after_move - after_switch
                report["limbs"].append({
                    "id": kind + "-" + side,
                    "property_bone": parent.name,
                    "ik_control": ik.name,
                    "joint": joint.name,
                    "mode_before": mode_before,
                    "switch_error": switch_error,
                    "requested_delta": list(delta),
                    "observed_delta": list(response),
                    "delta_error": (response - delta).length,
                })
        report["complete"] = True
    except BaseException:
        report["error"] = traceback.format_exc()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / (profile + ".json")).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"profile": profile, "complete": report["complete"], "error": report.get("error")}), flush=True)


def _main():
    if OUT.exists():
        raise RuntimeError("Evidence exists: " + str(OUT))
    OUT.mkdir(parents=True)
    rows = []
    for profile in PROFILES:
        log = OUT / (profile + ".log")
        started = time.perf_counter()
        with log.open("w", encoding="utf-8") as stream:
            process = subprocess.run(
                [str(HOST), "--background", "--factory-startup", "--disable-autoexec",
                 "--python", str(HERE), "--", profile],
                cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, timeout=900,
                env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="4"),
            )
        result_path = OUT / (profile + ".json")
        result = json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else {"complete": False}
        rows.append({"profile": profile, "complete": result.get("complete", False),
                     "host_exit": process.returncode, "seconds": time.perf_counter() - started})
    (OUT / "summary.json").write_text(json.dumps({"complete": all(row["complete"] for row in rows), "profiles": rows}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    if "--" in sys.argv:
        _host(sys.argv[sys.argv.index("--") + 1])
    else:
        _main()
