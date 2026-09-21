"""Read-only discovery of the Rigify animal templates bundled with Bforartists."""

from pathlib import Path
import importlib
import json
import pkgutil
import sys
import traceback


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "training/b4artists_ml/results/rigify-quadruped-probe-v1.json"


def run():
    import addon_utils
    import bpy

    addon_utils.enable("rigify", default_set=True, persistent=False)
    import rigify.metarigs as metarigs

    modules = []
    for descriptor in pkgutil.walk_packages(metarigs.__path__, metarigs.__name__ + "."):
        name = descriptor.name
        if any(token in name.lower() for token in ("quadruped", "wolf", "cat", "horse", ".animals.")):
            modules.append(name)
    rows = []
    for name in sorted(set(modules)):
        row = {"module": name, "created": False}
        try:
            module = importlib.import_module(name)
            create = getattr(module, "create", None)
            if not callable(create):
                row["reason"] = "no create function"
                rows.append(row)
                continue
            data = bpy.data.armatures.new("Quadruped probe")
            obj = bpy.data.objects.new("Quadruped probe", data)
            bpy.context.scene.collection.objects.link(obj)
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            create(obj)
            if obj.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
            row.update(created=True, bones=[
                {"name": bone.name, "parent": bone.parent.name if bone.parent else None,
                 "head": list(bone.head_local), "tail": list(bone.tail_local),
                 "use_deform": bool(bone.use_deform)}
                for bone in obj.data.bones
            ])
            bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.armatures.remove(data)
        except BaseException:
            row["error"] = traceback.format_exc()
            try:
                if bpy.context.object and bpy.context.object.mode != "OBJECT":
                    bpy.ops.object.mode_set(mode="OBJECT")
            except BaseException:
                pass
        rows.append(row)
    report = {
        "complete": True,
        "rigify_file": str(Path(importlib.import_module("rigify").__file__).resolve()),
        "modules": rows,
        "created_templates": sum(row["created"] for row in rows),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"complete": True, "modules": len(rows),
                      "created_templates": report["created_templates"]}), flush=True)


if __name__ == "__main__":
    if "--host" in sys.argv:
        run()
    else:
        raise SystemExit("Run this script through Bforartists with --host")
