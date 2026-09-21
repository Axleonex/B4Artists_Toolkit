"""Discover generated Rigify horse and wolf control/deform hierarchies."""

from pathlib import Path
import hashlib
import importlib
import json
import os
import subprocess
import sys
import time
import traceback


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
BASE = ROOT / "training/b4artists_ml/results/rigify-quadruped-generated-probe-v1"
HOST = "X:/5.1.0/bforartists.exe"
PROFILES = ("horse", "wolf")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def host(profile):
    import addon_utils
    import bpy

    report = {"profile": profile, "complete": False}
    try:
        addon_utils.enable("rigify", default_set=True, persistent=False)
        module = importlib.import_module("rigify.metarigs.Animals." + profile)
        data = bpy.data.armatures.new("Quadruped metarig")
        meta = bpy.data.objects.new("Quadruped metarig", data)
        bpy.context.scene.collection.objects.link(meta)
        bpy.context.view_layer.objects.active = meta
        meta.select_set(True)
        module.create(meta)
        if meta.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        metarig = [
            {"name": bone.name, "parent": bone.parent.name if bone.parent else None,
             "use_deform": bool(bone.use_deform)}
            for bone in meta.data.bones
        ]
        bpy.context.view_layer.objects.active = meta
        meta.select_set(True)
        bpy.ops.pose.rigify_generate()
        rig = bpy.context.object
        generated = []
        for bone in rig.pose.bones:
            generated.append({
                "name": bone.name,
                "parent": bone.parent.name if bone.parent else None,
                "use_deform": bool(bone.bone.use_deform),
                "constraints": [constraint.type for constraint in bone.constraints],
                "custom_properties": sorted(str(key) for key in bone.keys()),
            })
        report.update(
            complete=True,
            metarig_bones=metarig,
            generated_bones=generated,
            generated_object=rig.name,
        )
    except BaseException:
        report["error"] = traceback.format_exc()
    path = BASE / f"{profile}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"profile": profile, "complete": report["complete"],
                      "bones": len(report.get("generated_bones", [])),
                      "error": report.get("error")}), flush=True)


def main():
    if BASE.exists():
        raise RuntimeError("Evidence exists: " + str(BASE))
    BASE.mkdir(parents=True)
    rows = []
    for profile in PROFILES:
        log = BASE / f"{profile}.log"
        started = time.perf_counter()
        with log.open("w", encoding="utf-8") as stream:
            process = subprocess.run(
                [HOST, "--background", "--factory-startup", "--disable-autoexec",
                 "--python", str(HERE), "--", profile],
                stdout=stream, stderr=subprocess.STDOUT, timeout=900,
                env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="4"),
            )
        path = BASE / f"{profile}.json"
        report = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"complete": False}
        rows.append({"profile": profile, "complete": report.get("complete", False),
                     "host_exit": process.returncode, "seconds": time.perf_counter() - started,
                     "log": log.relative_to(ROOT).as_posix(), "log_sha256": sha(log)})
        print(json.dumps(rows[-1]), flush=True)
    summary = {"complete": all(row["complete"] for row in rows), "profiles": rows}
    (BASE / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if "--" in sys.argv:
        host(sys.argv[sys.argv.index("--") + 1])
    else:
        main()
